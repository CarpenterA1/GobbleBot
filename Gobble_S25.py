import pygame
import serial
import time

# ─── Configuration ─────────────────────────────────────────────────────────────
PORT    = 'COM7'      # your HC-06 outgoing port
BAUD    = 19200
TIMEOUT = 0.1         # initial timeout for ON wait

# map pygame button idx → solenoid number
BUTTON_TO_SOL = {
    2: '1',   # button idx 2 → solenoid “1”
    3: '2',   # button idx 3 → solenoid “2”
    1: '3',   # button idx 1 → solenoid “3”
}

# ─── Solenoid helper ────────────────────────────────────────────────────────────
def send_solenoid(ser, sol):
    """Fire solenoid sol ('1'–'3'), printing ON then OFF."""
    ser.reset_input_buffer()
    ser.write(sol.encode('ascii'))
    ser.flush()

    # wait for SOLn_ON
    target_on  = f"SOL{sol}_ON"
    target_off = f"SOL{sol}_OFF"

    while True:
        line = ser.readline().decode('ascii', errors='ignore').strip()
        if line:
            print("Arduino:", line)
            if line == target_on:
                break

    # wait for SOLn_OFF
    while True:
        if ser.in_waiting:
            line = ser.readline().decode('ascii', errors='ignore').strip()
            if line:
                print("Arduino:", line)
                if line == target_off:
                    break
        time.sleep(0.01)

# ─── Main ────────────────────────────────────────────────────────────────────────
def main():
    # Initialize serial link
    ser = serial.Serial(PORT, BAUD, timeout=TIMEOUT)
    time.sleep(2)  # HC-06 wake

    # Initialize pygame & joystick
    pygame.init()
    pygame.joystick.init()
    if pygame.joystick.get_count() == 0:
        print("No joystick detected. Plug in and restart.")
        return
    joy = pygame.joystick.Joystick(0)
    joy.init()
    print(f"Joystick '{joy.get_name()}' initialized, {joy.get_numbuttons()} buttons.")

    print("Press button 2->SOL1, 3->SOL2, 1->SOL3. Press ESC or Ctrl+C to quit.")

    try:
        while True:
            for evt in pygame.event.get():
                # handle button down
                if evt.type == pygame.JOYBUTTONDOWN:
                    btn = evt.button
                    if btn in BUTTON_TO_SOL:
                        sol = BUTTON_TO_SOL[btn]
                        print(f"Button {btn} -> n firing solenoid {sol}…")
                        send_solenoid(ser, sol)
                # optional: quit on controller “back” or ESC
                elif evt.type == pygame.JOYBUTTONDOWN and btn == pygame.K_ESCAPE:
                    raise KeyboardInterrupt

            # small delay to avoid busy-loop
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nExiting…")

    finally:
        joy.quit()
        pygame.quit()
        ser.close()

if __name__ == '__main__':
    main()
