import time
import sys

import library


def main(duration):
    sensor = library.IR_Sensor(14)
    sensor.start()
    time.sleep(duration)
    sensor.stop()


if __name__ == "__main__":
    # The first argument is the duration in seconds
    main(sys.argv[1])
