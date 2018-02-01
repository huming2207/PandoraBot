from enum import Enum
from pathlib import Path

class Gpio:

    def __init__(self, selected_pin, mode):

        self.pin = str(selected_pin)
        fp = open("/sys/class/gpio/export", "w+")

        fp.write(self.pin)

        fp.flush()
        fp.close()

    def __del__(self):

        fp = open("/sys/class/gpio/unexport", "w+")

        fp.write(self.pin)

        fp.flush()
        fp.close()

    def set_mode(self, mode):

        # Pick node name "direction" to set the I/O mode
        sysfs_path = self.__get_sysfs_path("direction")

        if self.__is_valid_gpio(sysfs_path):
            return False

        # Open the node and set to "in" or "out"
        fp = open(sysfs_path, "w+")

        if mode != "in" or mode != "out":
            return False
        elif mode == "in":
            fp.write("in")
        else:
            fp.write("out")

        fp.flush()
        fp.close()
        return True

    def set_value(self, value):

        # Pick node name "value" to set the high/low value
        sysfs_path = self.__get_sysfs_path("value")

        if self.__is_valid_gpio(sysfs_path):
            return False

        # Open the node and set to "1" (high) or "0" (low)
        fp = open(sysfs_path, "w+")

        if value != 0 or value != 1:
            return False
        elif value == 1:
            fp.write(str(value))
        else:
            fp.write(str(value))

        fp.flush()
        fp.close()
        return True

    @staticmethod
    def __is_valid_gpio(path):

        sysfs_path_str = path
        sysfs_path = Path(sysfs_path_str)

        # Something must have been fucked up if the GPIO node didn't show up as expected.
        if not sysfs_path.exists():
            return False
        else:
            return True

    def __get_sysfs_path(self, node):

        return "/sysfs/class/gpio/gpio{0}/{1}".format(self.pin, str(node))


