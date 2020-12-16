### Inspired from https://github.com/Lehkeda/SP108E_controller/blob/v1/controller.php
### Inspired from https://github.com/hamishcoleman/led_sp108e/
### Inspired from https://github.com/Spled/spled.github.io/issues/1


import select
import socket
import time

CMD_CUSTOM_EFFECT = 0x02
CMD_SPEED = 0x03
CMD_MODE_AUTO = 0x06
CMD_CUSTOM_DELETE = 0x07
CMD_WHITE_BRIGHTNESS = 0x08
CMD_SYNC = 0x10
CMD_SET_DEVICE_NAME = 0x14
CMD_SET_DEVICE_PASSWORD = 0x16
CMD_SET_IC_MODEL = 0x1c
CMD_GET_RECORD_NUM = 0x20
CMD_COLOR = 0x22
CMD_CUSTOM_PREVIEW = 0x24
CMD_CHANGE_PAGE = 0x25
CMD_BRIGHTNESS = 0x2a
CMD_MODE_CHANGE = 0x2c
CMD_DOT_COUNT = 0x2d
CMD_SEC_COUNT = 0x2e
CMD_CHECK_DEVICE_IS_COOL = 0x2f
CMD_SET_RGB_SEQ = 0x3c
CMD_CUSTOM_RECODE = 0x4c
CMD_GET_DEVICE_NAME = 0x77
CMD_SET_DEVICE_TO_AP_MODE = 0x88
CMD_TOGGLE_LAMP = 0xaa
CMD_CHECK_DEVICE = 0xd5

CMD_FRAME_START = 0x38
CMD_FRAME_END = 0x83

# These modes all have a single color, set by CMD_COLOR
MODES = {
    'METEOR': 205,
    'BREATHING': 206,
    'STACK': 207,
    'FLOW': 208,
    'WAVE': 209,
    'FLASH': 210,
    'STATIC': 211,
    'CATCHUP': 212,
    'CUSTOM_EFFECT': 219,
    'AUTO': 0xFC
}
def get_mode(x):
    for k,v in MODES.items():
        if v == x:
            return k
    return 'UNKNOWN'

CHIP_TYPES = {
    "SM16703": 0x00,
    "TM1804": 0x01,
    "UCS1903": 0x02,
    "WS2811": 0x03,
    "WS2801": 0x04,
    "SK6812": 0x05,
    "LPD6803": 0x06,
    "LPD8806": 0x07,
    "APA102": 0x08,
    "APA105": 0x09,
    "DMX512": 0x0a,
    "TM1914": 0x0b,
    "TM1913": 0x0c,
    "P9813": 0x0d,
    "INK1003": 0x0e,
    "P943S": 0x0f,
    "P9411": 0x10,
    "P9413": 0x11,
    "TX1812": 0x12,
    "TX1813": 0x13,
    "GS8206": 0x14,
    "GS8208": 0x15,
    "SK9822": 0x16,
    "TM1814": 0x17,
    "SK6812_RGBW": 0x18,
    "P9414": 0x19,
    "P9412": 0x1a
}
def get_chip_type(x):
    for k,v in CHIP_TYPES.items():
        if v == x:
            return k
    return 'UNKNOWN'

COLOR_ORDERS = {
    "RGB": 0x00,
    "RBG": 0x01,
    "GRB": 0x02,
    "GBR": 0x03,
    "BRG": 0x04,
    "BGR": 0x05
}
def get_color_order(x):
    for k,v in COLOR_ORDERS.items():
        if v == x:
            return k
    return 'UNKNOWN'

class SP108ECommunication(object):
    def __init__(self, controller_ip: str, controller_port: int = 8189, debug: bool = False):
        self._debug = debug

        # Open connection.
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((controller_ip, controller_port))
        self.s.setblocking(False)

    def _send(self, cmd, data=None, delay: float = 0.5):
        if data is None:
            data = b'\x00\x00\x00'
        elif len(data) < 3:
            data += bytes(3 - len(data))
        elif len(data) > 3:
            raise ValueError("data length max is 3")

        data_to_send = bytes([CMD_FRAME_START]) + data + bytes([cmd, CMD_FRAME_END])
        self.s.send(data_to_send)

        if delay > 0.0:
            time.sleep(delay)

    def _recv(self, timeout: float = 1):
        ready = select.select([self.s], [], [], timeout)

        if ready[0]:
            recv = self.s.recv(4096)
            if self._debug:
                print("Received:", recv)
            return recv

        if self._debug:
            print(f"Timeout of {timeout} expired while receiving")

        return ''

    def _sendrecv(self, cmd, data=None, delay=0.0, timeout=1.0):
        self._send(cmd, data, delay)
        return self._recv(timeout)


class SP180E(SP108ECommunication):
    def __init__(self, controller_ip, controller_port: int = 8189, debug: bool = False):
        super().__init__(controller_ip, controller_port, debug)

    def set_ic_model(self, ic):
        if not ic in CHIP_TYPES:
            raise ValueError("Specified IC is not in the list of supported ICs")
        return self._send(CMD_SET_IC_MODEL, bytes([CHIP_TYPES[ic]]))

    def set_color_order(self, order):
        if not order in COLOR_ORDERS:
            raise ValueError("Specified color order is not valid")
        return self._send(CMD_SET_RGB_SEQ, bytes([COLOR_ORDERS[order]]))

    def set_number_of_leds(self, segment_count: int, leds_per_segment: int):
        if segment_count * leds_per_segment > 2048:
            raise ValueError("Total pixel count cannot exceed 2048")
        if leds_per_segment > 300:
            raise ValueError("The number of pixels per segment cannot exceed 300")
        # bytes([(leds_per_segment & 0xFF00) >> 8, leds_per_segment & 0xFF])
        self._send(CMD_DOT_COUNT, leds_per_segment.to_bytes(2, 'little'))
        self._send(CMD_SEC_COUNT, segment_count.to_bytes(2, 'little'))

    def get_name(self):
        return self._sendrecv(CMD_GET_DEVICE_NAME)

    def is_device_ready(self):
        data = self._sendrecv(CMD_CHECK_DEVICE_IS_COOL)
        return data == b'1'

    def sync(self):
        data = self._sendrecv(CMD_SYNC)

        is_valid = data[0] == 0x38
        leds_per_segment = data[7] + (data[6] << 8)
        segment_count = data[9] + (data[8] << 8)

        return {
            'valid': is_valid,
            'power': data[1] == 1,
            'pattern': data[2],
            'pattern_name': get_mode(data[2]),
            'speed': data[3],
            'brightness': data[4],
            'output_color_order': get_color_order(data[5]),
            'leds_per_segment': leds_per_segment,
            'segment_count': segment_count,
            'total_leds': leds_per_segment * segment_count,
            'current_color_r': data[10],
            'current_color_g': data[11],
            'current_color_b': data[12],
            'output_ic_model': get_chip_type(data[13]),
            'recorded_patterns': data[14],
            'white_channel_brightness': data[15],
        }

    def change_white_brightness(self, brightness: int):
        if not 1 <= brightness <= 255:
            raise ValueError("brightness must be between 1 and 255")
        self._send(CMD_WHITE_BRIGHTNESS, bytes([brightness]))

    def change_color_brightness(self, brightness: int):
        if not 1 <= brightness <= 255:
            raise ValueError("brightness must be between 1 and 255")
        self._send(CMD_BRIGHTNESS, bytes([brightness]))

    def set_color(self, red: int = 0, green: int = 0, blue: int = 0):
        if not 0 <= red <= 255:
            raise ValueError("red must be between 0 and 255")
        if not 0 <= green <= 255:
            raise ValueError("green must be between 0 and 255")
        if not 0 <= blue <= 255:
            raise ValueError("blue must be between 0 and 255")
        self._send(CMD_COLOR, bytes([red, green, blue]))

    def set_pattern(self, pattern):
        if not pattern in MODES:
            raise ValueError("Pattern in not known")
        if pattern == 'AUTO':
            self._send(CMD_MODE_AUTO)
        else:
            self._send(CMD_MODE_CHANGE, bytes([MODES[pattern]]))

    def set_speed(self, speed):
        if not 0 <= speed <= 255:
            raise ValueError("speed must be between 0 and 255")
        self._send(CMD_SPEED, bytes([speed]))

    def set_preloaded_animation(self, index):
        if not 0 <= index <= 0xB4:
            raise ValueError("Index should be between 0 and 0xB4")
        self._send(CMD_MODE_CHANGE, bytes([index]))

    def toggle_on_off(self):
        self._send(CMD_TOGGLE_LAMP)

    def send_pixel_values(self, values):
        self._sendrecv(CMD_CUSTOM_PREVIEW, bytes([0xE9, 0x39, 0x9A]))
        self.s.send(values)
        self._recv()

