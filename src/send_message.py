import time

import library


def main():
    # Setup everything
    ir_led = library.IR_LED(15)
    ir_led.off()

    # Send message
    msg = "Hello world"
    ir_led.send_msg(msg)


if __name__ == "__main__":
    main()
