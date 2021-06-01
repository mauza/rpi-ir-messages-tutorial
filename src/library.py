import time, queue, sys
from threading import Thread

import gpiozero

POLL_INTERVAL = 0.0001


def serialize_message(message):
    return [ord(character) for character in message]


def deserialize_message(ascii_list):
    return "".join([chr(num) for num in ascii_list])


class Buffer:
    def __init__(self, size):
        self.size = size
        self.buffer = []

    def put(self, item):
        self.buffer.append(item)
        if len(self.buffer) > self.size:
            self.buffer.pop(0)

    def value(self):
        current_len = len(self.buffer)
        if current_len < self.size:
            return -1
        return sum(self.buffer)/current_len

    def length(self):
        return len(self.buffer)

    def empty(self):
        self.buffer = []


class IR_Sensor:
    threshold = 0.4

    def __init__(self, pin_num):
        self.pin_num = pin_num
        self.sensor = gpiozero.InputDevice(pin_num)
        self.raw_q = queue.SimpleQueue()
        self._stop = False

    def start(self):
        stop_fn = lambda: self._stop
        self.io_thread = Thread(target=self._stream_input, args=(stop_fn,))
        self.convert_thread = Thread(target=self._convert_input, args=(stop_fn,))
        self.io_thread.start()
        self.convert_thread.start()

    def _convert_input(self, stop):
        raw_buffer = Buffer(10)
        value_buffer = Buffer(1000)
        previous_value = 0
        off_iter = 0
        while True:
            if stop():
                break
            raw_value = self.raw_q.get()
            raw_buffer.put(raw_value)
            value = raw_buffer.value()
            # if value > 0:
            #     print(value)
            if value < 0:
                continue
            elif value < self.threshold:
                if previous_value == 1:
                    value_buffer.put(0)
                previous_value = 0
                off_iter += 1
            elif value >= self.threshold:
                if previous_value == 0:
                    value_buffer.put(1)
                off_iter = 0
                previous_value = 1

            if off_iter >= 100:
                ascii_code = sum(value_buffer.buffer)
                if ascii_code == 0:
                    continue
                print(ascii_code)
                # print(deserialize_message([ascii_code]), end='')
                sys.stdout.flush()
                value_buffer.empty()
                off_iter = 0


    def _stream_input(self, stop):
        while True:
            if stop():
                break
            raw_value = self.sensor.value
            if raw_value == 0:
                value = 1
            else:
                value = 0
            self.raw_q.put(value)
            time.sleep(POLL_INTERVAL)

    def stop(self):
        self._stop = True
        self.convert_thread.join()
        self.io_thread.join()
        self._stop = False

    def get(self):
        return self.q.get()


class IR_LED:
    def __init__(self, pin_num):
        self.pin_num = pin_num
        self.LED = gpiozero.LED(pin_num)
        self.blink_interval = 0.01

    def blink(self, n):
        on_time = self.blink_interval
        off_time = self.blink_interval
        self.LED.blink(on_time, off_time, n=n, background=False)

    def off(self):
        self.LED.off()

    def on(self):
        self.LED.on()

    def send_msg(self, msg):
        encoded_msg = serialize_message(msg)
        for code in encoded_msg:
            print(f"sending ascii code: {code}")
            self.blink(n=code)
            time.sleep(0.1)

