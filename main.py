import time
import gpio
import messages


def main():
    sensor = gpio.IR_Sensor(14)
    ir_led = gpio.IR_LED(15)
    sensor.start()
    ir_led.blink(n=100)
    t = []
    for _ in range(1000):
        t.append(sensor.get())
    sensor.stop()
    print(t)


if __name__ == "__main__":
    main()
