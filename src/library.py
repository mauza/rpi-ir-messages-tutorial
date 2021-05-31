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


class IR_Sensor:
    threshold = 0.1

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
        raw_buffer = Buffer(20)
        value_buffer = Buffer(10)
        previous_value = 0
        tmp_ascii = 0
        while True:
            if stop():
                break
            raw_value = self.raw_q.get()
            raw_buffer.put(raw_value)
            value = raw_buffer.value()
            value_buffer.put(value)
            #print(f"values: {value}")
            print(f"value buffer: {value_buffer.value()}")
            if value < 0:
                continue
            elif value <= self.threshold:
                if previous_value == 1:
                    print(tmp_ascii)
                    tmp_ascii += 1
                    previous_value = 0
                elif previous_value == 0:
                    if value_buffer.value == 0:
                        ascii_list.append(tmp_ascii)
                        tmp_ascii = 0
            elif value > self.threshold:
                previous_value = 1

            current_time = time.time()
            if len(ascii_list) > 2 or current_time - start_time >= 20:
                start_time = current_time
                print(deserialize_message(ascii_list), end='')
                ascii_list = []


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
        on_time = POLL_INTERVAL * 10
        off_time = POLL_INTERVAL * 10
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
            time.sleep(POLL_INTERVAL*100)

