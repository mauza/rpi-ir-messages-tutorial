import time, queue
from threading import Thread

import gpiozero

POLL_INTERVAL = 0.001


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
    threshold = 0.2

    def __init__(self, pin_num):
        self.pin_num = pin_num
        self.sensor = gpiozero.InputDevice(pin_num)
        self.raw_q = queue.SimpleQueue()
        self.msg_q = queue.SimpleQueue()
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
        tmp_ascii = 0
        off_iter = 0
        while True:
            if stop():
                break
            raw_value = self.raw_q.get()
            raw_buffer.put(raw_value)
            value = raw_buffer.value()
            print(value)
            if value < 0:
                continue
            elif value <= self.threshold:
                if previous_value == 1:
                    value_buffer.put(0)
                    tmp_ascii += 1
                else:
                    off_iter += 1
                previous_value = 0
            elif value > self.threshold:
                if previous_value == 0:
                    value_buffer.put(1)
                previous_value = 1

            if tmp_ascii != 0 and off_iter >= 500:
                print(deserialize_message([tmp_ascii]), end='')
                #print(value_buffer.buffer)
                value_buffer.empty()
                tmp_ascii = 0
                off_iter = 0
            time.sleep(POLL_INTERVAL/2)


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

    def blink(self, n):
        on_time = POLL_INTERVAL * 20
        off_time = POLL_INTERVAL * 20
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
            time.sleep(POLL_INTERVAL*200)

