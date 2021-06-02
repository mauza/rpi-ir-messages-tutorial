import time, queue, sys
from threading import Thread

import gpiozero


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
        if current_len == 0:
            return 0
        return sum(self.buffer)/current_len

    def length(self):
        return len(self.buffer)

    def empty(self):
        self.buffer = []


class IR_Sensor:
    on_threshold = 0.45
    off_threshold = 0.1

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
        raw_buffer = Buffer(100)
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
            if value <= self.off_threshold:
                previous_value = 0
                off_iter += 1
            elif value >= self.on_threshold:
                if previous_value == 0:
                    value_buffer.put(1)
                off_iter = 0
                previous_value = 1

            if off_iter >= 4000:
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
        self.LED.off()
        self.blink_interval = 0.09

    def blink(self, n):
        for i in range(n):
            self.LED.on()
            time.sleep(self.blink_interval)
            self.LED.off()
            time.sleep(self.blink_interval)

    def off(self):
        self.LED.off()

    def on(self):
        self.LED.on()

    def send_msg(self, msg):
        encoded_msg = serialize_message(msg)
        for code in encoded_msg:
            print(f"sending ascii code: {code}")
            self.blink(n=code)
            time.sleep(self.blink_interval*150)
