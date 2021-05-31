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
    ir_led.send_msg(msg)
    time.sleep(15)
    sensor.stop()


if __name__ == "__main__":
    main()
