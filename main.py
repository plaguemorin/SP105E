from controller_api import SP180E
from picture import picture

controller = SP180E("192.168.10.110")
#print(controller.sync())

controller.set_ic_model('SK6812_RGBW')
controller.set_color_order('GRB')
#controller.set_number_of_leds(2, 150)
controller.set_number_of_leds(1, 300)
controller.set_color(0, 0, 0)

# controller.change_white_brightness(1)
# controller.change_color_brightness(63)
controller.set_speed(255)
# controller.set_pattern('CUSTOM_EFFECT')

print(controller.sync())

# for pixel in range(0, 150):
#     frame = [0,0,0] * 300
#
#     frame[pixel * 6 + 0] = int(pixel / 300 * 255)
#     frame[pixel * 6 + 1] = 0
#     frame[pixel * 6 + 2] = int((299 - pixel) / 300 * 255)
#
#     controller.send_pixel_values(bytes(frame))

for line_number in range(0, int((len(picture) / 300))):
    frame = [0, 0, 0] * 300

    for pixel in range(0, 300):
        color233 = picture[line_number * 300 + pixel]

        frame[pixel * 3 + 0] = int(((color233 >> 5 & 0x07) / 0x7) * 255)
        frame[pixel * 3 + 1] = int(((color233 >> 2 & 0x07) / 0x07) * 255)
        frame[pixel * 3 + 2] = int(((color233 & 0x03) / 0x03) * 255)

    controller.send_pixel_values(bytes(frame))
