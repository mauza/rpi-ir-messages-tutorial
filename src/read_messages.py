import time
import sys

import library


def main(duration):
    sensor = library.IR_Sensor(18)
    sensor.start()
    time.sleep(duration)
    sensor.stop()


if __name__ == "__main__":
    # The first argument is the duration in seconds
    input_duration = int(sys.argv[1])
    main(input_duration)
