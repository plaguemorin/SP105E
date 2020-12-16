import math

from controller_api import SP180E
from strip import Strip

controller = SP180E("192.168.10.110", debug=False)
controller.set_ic_model('SK6812_RGBW')
controller.set_color_order('GRB')
#controller.set_number_of_leds(2, 150)
controller.set_number_of_leds(1, 300)

controller.change_white_brightness(63)
controller.change_color_brightness(63)
controller.set_speed(255)
controller.set_color(0, 0, 0)
controller.set_pattern('STATIC')

values = controller.sync()
print(values)

if not values['power']:
    controller.toggle_on_off()

s = Strip(values['leds_per_segment'], scale=1)

print("Demo 1...")
for pixel in range(0, values['leds_per_segment']):
    print(" Pixel %d" % pixel)

    s.reset(0, 0, 0)
    s.set_led_color(pixel - 3, 32, 0, 0)
    s.set_led_color(pixel - 2, 0, 64, 0)
    s.set_led_color(pixel - 1, 0, 0, 128)
    s.set_led_color(pixel + 0, 255, 0, 0)
    s.set_led_color(pixel + 1, 0, 128, 128)
    s.set_led_color(pixel + 2, 0, 64, 64)
    s.set_led_color(pixel + 3, 0, 32, 0)

    # Send it more than once to control speed (yeah bad way)
    # but the controller will reset to a color if you don't send
    # it data periodically
    controller.send_pixel_values(s.frame())

print("Demo 2...")
s.reset()
for pulse in range(0, 512):
    for num in range(0, 300):
        if num % 2 == 0:
            s.set_led_color(num, int(math.sin(pulse/10) * 255), int(math.cos(pulse/10) * 255), 0)
        else:
            s.set_led_color(num, 0, int(math.sin(pulse/10) * 255), int(math.cos(pulse/10) * 255))
    controller.send_pixel_values(s.frame())
    controller.send_pixel_values(s.frame())


print("Demo 3...")
while True:
    controller.change_color_brightness(2)
    controller.change_white_brightness(1)

    print("Changing color bright")
    for bright in range(1, 254):
        s.reset(bright, 255 - bright, bright)
        controller.send_pixel_values(s.frame())

    print("Changing white bright")
    for bright in range(1, 254):
        controller.change_white_brightness(bright)

    print("Changing both bright")
    for bright in range(1, 254):
        s.reset(bright, bright, bright)
        controller.send_pixel_values(s.frame())
