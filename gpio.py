import time
from threading import Thread

import gpiozero

STOP_THREAD = False

class IR_Sensor:

    def __init__(self, pin_num):
        self.pin_num = pin_num
        self.sensor = gpiozero.DigitalInputDevice(pin_num)

    def value(self):
        return self.sensor.value

    def stream_input(self):
        self._thread = Thread(target=self._stream_input, args=(lambda: STOP_THREAD,))
        self._thread.start()

    def _stream_input(self, stop):
        while True:
            if stop():
                break
            print(self.value())
            time.sleep(0.01)

    def stop_stream(self):
        if self._thread:
            global STOP_THREAD
            STOP_THREAD = True
            self._thread.join()
            STOP_THREAD = False





class IR_LED:
    def __init__(self, pin_num):
        self.pin_num = pin_num
        self.LED = gpiozero.LED(pin_num)

    def blink(self, *args, **kwargs):
        return self.LED.blink(*args, **kwargs)
