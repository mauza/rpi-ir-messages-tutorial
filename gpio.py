import time, queue
from threading import Thread

import gpiozero

STOP_THREAD = False

class IR_Sensor:

    def __init__(self, pin_num):
        self.pin_num = pin_num
        self.sensor = gpiozero.DigitalInputDevice(pin_num)
        self.q = queue.SimpleQueue()

    def start(self):
        self._thread = Thread(target=self._stream_input, args=(lambda: STOP_THREAD,))
        self._thread.start()

    def _stream_input(self, stop):
        while True:
            if stop():
                break
            self.q.put(self.sensor.value)
            time.sleep(0.001)

    def stop(self):
        if self._thread:
            global STOP_THREAD
            STOP_THREAD = True
            self._thread.join()
            STOP_THREAD = False

    def get(self):
        return self.q.get()



class IR_LED:
    def __init__(self, pin_num):
        self.pin_num = pin_num
        self.LED = gpiozero.LED(pin_num)

    def blink(self, n):
        on_time = 0.01
        off_time = 0.01
        self.LED.blink(on_time, off_time, n=n)
