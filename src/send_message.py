import sys
import library


def main(msg):
    # Setup everything
    ir_led = library.IR_LED(15)
    ir_led.off()

    # Send message
    ir_led.send_msg(msg)


if __name__ == "__main__":
    main(sys.argv[1])
