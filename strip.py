
class Strip(object):
    def __init__(self, num_leds, scale = 1.0):
        if num_leds > 300:
            raise ValueError('Num Leds cannot be more than 300')
        self._num_leds = num_leds
        self._scale = scale

        # There's always 300 RGB values
        self._frame = [0, 0, 0] * 300

        # If there's 300 leds, then leds are 0,1,2,3,4,5,6,7,8,...
        # If there's 150 leds, then leds are 0,2,4,6,8,10,...
        # If there's 3 leds then leds are 0, 99, 299
        self._pixel_stride = int(300 / self._num_leds * 3)

    def set_led_color(self, led: int, red, green, blue):
        if 0 <= led < self._num_leds:
            p_red = int(red * self._scale)
            p_green = int(green * self._scale)
            p_blue = int(blue * self._scale)

            # Must be less or equal to 255 and more or equal to 0
            p_red = min(255, max(0, p_red))
            p_green = min(255, max(0, p_green))
            p_blue = min(255, max(0, p_blue))

            self._frame[led * self._pixel_stride + 0] = p_red
            self._frame[led * self._pixel_stride + 1] = p_green
            self._frame[led * self._pixel_stride + 2] = p_blue

    def reset(self, red = 0, green = 0, blue = 0):
        self._frame = [red, green, blue] * 300

    def frame(self):
        return bytes(self._frame)
