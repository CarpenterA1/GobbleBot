from machine import I2C
from vl53l1x import VL53L1X
import sensor
import time
import ml
from ml.utils import NMS
import math
import image

# --- Time-of-Flight Sensor Setup ---
tof_i2c = I2C(2)
tof = VL53L1X(tof_i2c)

# --- Configuration Parameters ---
MIN_CONFIDENCE = 0.4
THRESHOLD_LIST = [(math.ceil(MIN_CONFIDENCE * 255), 255)]
COLORS = [
    (255, 0, 0),    # Class 0 (background, not used)
    (0, 255, 0),    # Class 1
    (255, 255, 0),  # Class 2
    (0, 0, 255),    # Class 3
    (255, 0, 255),  # Class 4
    (0, 255, 255),  # Class 5
    (255, 255, 255) # Class 6
]

FULL_SENSOR_WIDTH  = 640
FULL_SENSOR_HEIGHT = 480
IMAGE_WIDTH  = 320
IMAGE_HEIGHT = 240

CRITICAL_ZONE_X_START = int(IMAGE_WIDTH * 0.3)
CRITICAL_ZONE_X_END   = int(IMAGE_WIDTH * 0.7)
CRITICAL_ZONE_Y_START = int(IMAGE_HEIGHT * 0.6)
CRITICAL_ZONE_Y_END   = IMAGE_HEIGHT

MM_TO_INCH = 1 / 25.4

def setup_sensor():
    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)
    sensor.set_windowing((0, 0, 640, 480))  # Adjust to full sensor if desired

    # Disable auto-exposure and set exposure to ~3ms (3000us)
    # If your sensor/firmware supports it, this helps reduce motion blur
    sensor.set_auto_exposure(False, exposure_us=3000)

    # Attempt to limit the maximum gain via gain ceiling
    sensor.set_gainceiling(16)

    # Skip frames to let the sensor adapt
    sensor.skip_frames(time=2000)



def fomo_post_process(model, inputs, outputs):
    n, oh, ow, oc = model.output_shape[0]
    nms = NMS(ow, oh, inputs[0].roi)
    for i in range(oc):
        out_img = image.Image(outputs[0][0, :, :, i] * 255)
        blobs = out_img.find_blobs(THRESHOLD_LIST, x_stride=1, area_threshold=1, pixels_threshold=1)
        for b in blobs:
            rect = b.rect()  # (x, y, w, h)
            x, y, w, h = rect
            score = out_img.get_statistics(thresholds=THRESHOLD_LIST, roi=rect).l_mean() / 255.0
            nms.add_bounding_box(x, y, x + w, y + h, score, i)
    return nms.get_bounding_boxes()

def analyze_detection(x, y, w, h):
    center_x = x + w // 2
    center_y = y + h // 2
    if (center_x >= CRITICAL_ZONE_X_START and center_x <= CRITICAL_ZONE_X_END and
        center_y >= CRITICAL_ZONE_Y_START):
        zone_midpoint = CRITICAL_ZONE_X_START + (CRITICAL_ZONE_X_END - CRITICAL_ZONE_X_START) // 2
        if center_x < zone_midpoint:
            return "Obstacle left! Steer right."
        else:
            return "Obstacle right! Steer left."
    return ""

def draw_detections(img, detection_list, class_label, color):
    action = ""
    for (x, y, w, h), score in detection_list:
        # Draw thicker bounding box
        img.draw_rectangle((x, y, w, h), color=color, thickness=3)

        # Larger text with background for readability
        img.draw_string(
            x, y - 20,
            "{} {:.2f}".format(class_label, score),
            color=color,
            scale=2,
            mono_space=False,
            bg_color=(0, 0, 0)  # black background
        )

        center_x = x + w // 2
        center_y = y + h // 2
        # Thicker circle
        img.draw_circle((center_x, center_y, 4), color=color, thickness=2)

        potential_action = analyze_detection(x, y, w, h)
        if potential_action:
            action = potential_action
    return action

def main():
    setup_sensor()
    model = ml.Model("trained")
    print("Model loaded:", model)
    clock = time.clock()

    while True:
        clock.tick()
        img = sensor.snapshot()  # 320x240 image

        # --- Read ToF Sensor ---
        distance_mm = tof.read()
        distance_in = distance_mm * MM_TO_INCH

        # Larger text with background for distance
        img.draw_string(
            5, IMAGE_HEIGHT - 25,
            "Dist: {} mm / {:.2f} in".format(distance_mm, distance_in),
            color=(0, 255, 255),
            scale=2,
            bg_color=(0, 0, 0)
        )

        # Object detection inference
        detection_results = model.predict([img], callback=fomo_post_process)
        actions = []
        for class_index, detection_list in enumerate(detection_results):
            if class_index == 0 or not detection_list:
                continue
            if hasattr(model, "labels") and len(model.labels) > class_index:
                class_label = model.labels[class_index]
            else:
                class_label = "Class %d" % class_index

            action = draw_detections(img, detection_list, class_label, COLORS[class_index])
            if action:
                actions.append(action)

            for (x, y, w, h), score in detection_list:
                print("Class {}: Bounding Box: x={}, y={}, w={}, h={}, score={:.2f}".format(
                    class_label, x, y, w, h, score))

        if actions:
            for idx, act in enumerate(actions):
                # Print action in large red text with background
                img.draw_string(
                    5, 5 + idx * 25,  # Move down by 25 for each action
                    act,
                    color=(255, 0, 0),
                    scale=2,
                    bg_color=(0, 0, 0)
                )
                print("Action:", act)
        else:
            # "Path clear" in green text with black background
            img.draw_string(
                5, 5,
                "Path clear",
                color=(0, 255, 0),
                scale=2,
                bg_color=(0, 0, 0)
            )

        print("{:.2f} fps".format(clock.fps()))

if __name__ == "__main__":
    main()
