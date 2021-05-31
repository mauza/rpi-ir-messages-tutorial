import time

import library


def main():
    # Setup everything
    sensor = library.IR_Sensor(14)
    ir_led = library.IR_LED(15)
    sensor.start()
    ir_led.off()

    # Send message
    msg = "Hello world"
    encoded_msg = library.serialize_message(msg)
    for code in encoded_msg:
        ir_led.blink(n=code)
        time.sleep(0.06)
    time.sleep(15)
    sensor.stop()


if __name__ == "__main__":
    main()
