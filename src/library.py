import time, queue
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
        if current_len < self.size:
            return -1
        return sum(self.buffer)/current_len

    def length(self):
        return len(self.buffer)


class IR_Sensor:

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
        start_time = time.time()
        ascii_list = []
        long_buffer = Buffer(20)
        short_buffer = Buffer(2)
        previous_value = 0
        tmp_ascii = 0
        while True:
            if stop():
                break
            raw_value = self.raw_q.get()
            short_buffer.put(raw_value)
            long_buffer.put(raw_value)
            current_value = short_buffer.value()
            print(long_buffer.buffer)
            if current_value < 0:
                continue
            elif previous_value == 0 and current_value <= 0.1:
                ascii_list.append(tmp_ascii)
                tmp_ascii = 0
                continue
            elif current_value <= 0.5:
                previous_value = 0
            elif current_value > 0.5:
                if previous_value == 0:
                    tmp_ascii += 1
                previous_value = 1

            current_time = time.time()
            if current_time - start_time >= 15:
                start_time = current_time
                print(deserialize_message(ascii_list))
                ascii_list = []


    def _stream_input(self, stop):
        while True:
            if stop():
                break
            self.raw_q.put(self.sensor.value)
            time.sleep(0.001)

    def stop(self):
        self._stop = True
        self.io_thread.join()
        self.convert_thread.join()
        self._stop = False

    def get(self):
        return self.q.get()


class IR_LED:
    def __init__(self, pin_num):
        self.pin_num = pin_num
        self.LED = gpiozero.LED(pin_num)

    def blink(self, n):
        on_time = 0.05
        off_time = 0.05
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
            time.sleep(0.2)

