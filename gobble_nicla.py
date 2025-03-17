from machine import I2C, UART
from vl53l1x import VL53L1X
import sensor
import time
import ml
from ml.utils import NMS
import math
import image


tof_i2c = I2C(2)
tof = VL53L1X(tof_i2c)

uart = UART(9, 115200)


MIN_CONFIDENCE = 0.3
THRESHOLD_LIST = [(math.ceil(MIN_CONFIDENCE * 255), 255)]
COLORS = [
    (255, 0, 0),
    (0, 255, 0),
    (255, 255, 0),
    (0, 0, 255),
    (255, 0, 255),
    (0, 255, 255),
    (255, 255, 255)
]

IMAGE_WIDTH  = 320
IMAGE_HEIGHT = 240

CRITICAL_ZONE_X_START = int(IMAGE_WIDTH * 0.3)
CRITICAL_ZONE_X_END   = int(IMAGE_WIDTH * 0.7)
CRITICAL_ZONE_Y_START = int(IMAGE_HEIGHT * 0.6)
CRITICAL_ZONE_Y_END   = IMAGE_HEIGHT

MM_TO_INCH = 1 / 25.4
PROXIMITY_THRESHOLD_INCH = 20.0

def setup_sensor():
    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)
    sensor.set_auto_exposure(False, exposure_us=3000)
    sensor.set_gainceiling(16)
    sensor.skip_frames(time=2000)

def fomo_post_process(model, inputs, outputs):
    n, out_h, out_w, out_ch = model.output_shape[0]
    nms = NMS(out_w, out_h, inputs[0].roi)
    for class_idx in range(out_ch):
        out_img = image.Image(outputs[0][0, :, :, class_idx] * 255)
        blobs = out_img.find_blobs(
            THRESHOLD_LIST, x_stride=1, y_stride=1,
            area_threshold=1, pixels_threshold=1,
            merge=True
        )
        for b in blobs:
            x, y, w, h = b.rect()
            score = out_img.get_statistics(thresholds=THRESHOLD_LIST, roi=b.rect()).l_mean() / 255.0
            nms.add_bounding_box(x, y, x + w, y + h, score, class_idx)
    return nms.get_bounding_boxes()

def analyze_detection(x, y, w, h, distance_in):
    center_x = x + w // 2
    center_y = y + h // 2
    in_critical = (CRITICAL_ZONE_X_START <= center_x <= CRITICAL_ZONE_X_END) and (center_y >= CRITICAL_ZONE_Y_START)
    if distance_in < PROXIMITY_THRESHOLD_INCH:
        if in_critical:
            zone_mid = CRITICAL_ZONE_X_START + (CRITICAL_ZONE_X_END - CRITICAL_ZONE_X_START) // 2
            return "Stop/Turn R" if center_x < zone_mid else "Stop/Turn L"
        else:
            return "Veer R" if center_x < IMAGE_WIDTH // 2 else "Veer L"
    else:
        if in_critical:
            zone_mid = CRITICAL_ZONE_X_START + (CRITICAL_ZONE_X_END - CRITICAL_ZONE_X_START) // 2
            return "Obs L" if center_x < zone_mid else "Obs R"
    return ""

def draw_detections(img, det_list, class_label, color, distance_in):
    action = ""
    for (x, y, w, h), score in det_list:
        img.draw_rectangle((x, y, w, h), color=color, thickness=2)
        img.draw_string(x, max(y - 15, 0),
                        "%s %.2f" % (class_label, score),
                        color=color, scale=1, mono_space=False, bg_color=(0, 0, 0))
        center_x, center_y = x + w // 2, y + h // 2
        img.draw_circle((center_x, center_y, 3), color=color, thickness=2)
        maybe_action = analyze_detection(x, y, w, h, distance_in)
        if maybe_action:
            action = maybe_action
    return action

def main():
    setup_sensor()
    model = ml.Model("trained")
    clock = time.clock()

    while True:
        clock.tick()
        img = sensor.snapshot()
        distance_mm = tof.read()
        distance_in = distance_mm * MM_TO_INCH

        # Display distance on image
        img.draw_string(5, IMAGE_HEIGHT - 15,
                        "Dist %.1f in" % distance_in,
                        color=(0, 255, 255), scale=1, bg_color=(0, 0, 0))

        # Run inference
        det_results = model.predict([img], callback=fomo_post_process)
        actions = []

        for class_idx, det_list in enumerate(det_results):
            if class_idx == 0 or not det_list:
                continue
            label = model.labels[class_idx] if (hasattr(model, "labels") and len(model.labels) > class_idx) else "C%d" % class_idx
            action = draw_detections(img, det_list, label, COLORS[class_idx], distance_in)
            if action:
                actions.append(action)

        if actions:
            for idx, act in enumerate(actions):
                img.draw_string(5, 5 + idx * 12,
                                act,
                                color=(255, 0, 0), scale=1, bg_color=(0, 0, 0))
        else:
            img.draw_string(5, 5, "Clear", color=(0, 255, 0), scale=1, bg_color=(0, 0, 0))


        message = "D:{:.2f},A:{}".format(distance_in, ';'.join(actions))
        uart.write(message + "\n")

        print(message)

if __name__ == "__main__":
    main()
