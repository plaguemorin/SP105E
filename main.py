from controller_api import SP180E
import time

controller = SP180E("192.168.10.110")
print(controller.sync())

controller.set_ic_model('SK6812_RGBW')
controller.set_color_order('GRB')
controller.set_number_of_leds(1, 300)
controller.set_pattern('AUTO')
controller.set_speed(255)

# print(controller.is_device_ready(), controller.get_name())
print(controller.sync())

# controller.set_color(255, 0, 0)
# time.sleep(5)
# controller.set_color(0, 255, 0)
# time.sleep(5)
# controller.set_color(0, 0, 255)
