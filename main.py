import time
import gpio
import messages


def main():
    sensor = gpio.IR_Sensor(14)
    sensor.stream_input()
    time.sleep(10)
    sensor.stop_stream()


if __name__ == "__main__":
    main()
