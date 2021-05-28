import time
import gpio
import messages


def main():
    sensor = gpio.IR_Sensor(14)
    ir_led = gpio.IR_LED(15)
    sensor.stream_input()
    ir_led.blink(on_time=0.5, off_time=0.5)
    time.sleep(10)
    sensor.stop_stream()


if __name__ == "__main__":
    main()
