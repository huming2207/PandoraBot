from enum import Enum
from pathlib import Path
import sys

class Gpio:

    def __init__(self, selected_pin, app):

        self.pin = str(selected_pin)
        self.app = app
        fp = open("/sys/class/gpio/export", "w")

        fp.write(self.pin)

        fp.flush()
        fp.close()

    # def __del__(self):
    #
    #     fp = open("/sys/class/gpio/unexport", "w")
    #
    #     fp.write(self.pin)
    #
    #     fp.flush()
    #     fp.close()

    def set_mode(self, mode):

        # Pick node name "direction" to set the I/O mode
        sysfs_path = self.__get_sysfs_path("direction")

        if not self.__is_valid_gpio(sysfs_path):
            return False

        # Open the node and set to "in" or "out"
        fp = open(sysfs_path, "w")

        if mode == "in":
            fp.write("in")
        elif mode == "out":
            fp.write("out")
        else:
            self.app.logger.error("[ERR] Unexpected value: {0}".format(mode))
            return False

        fp.flush()
        fp.close()
        return True

    def set_value(self, value):

        # Pick node name "value" to set the high/low value
        sysfs_path = self.__get_sysfs_path("value")

        if not self.__is_valid_gpio(sysfs_path):
            return False

        # Open the node and set to "1" (high) or "0" (low)
        fp = open(sysfs_path, "w")

        if not str(value).isdigit():
            return False
        else:
            fp.write(str(value))

        fp.flush()
        fp.close()
        return True

    def get_value(self):

        # Pick node name "value" to set the high/low value
        sysfs_path = self.__get_sysfs_path("value")

        if not self.__is_valid_gpio(sysfs_path):
            return -1

        # Open the node
        result = Path(self.__get_sysfs_path("value")).read_text()

        # Get the value, if incorrect then return -1
        if str(result).isdigit():
            return -1

        return int(result)

    def __is_valid_gpio(self, path):

        sysfs_path_str = path
        sysfs_path = Path(sysfs_path_str)

        # Something must have been fucked up if the GPIO node didn't show up as expected.
        if not sysfs_path.exists():
            self.app.logger.error("[ERR] Not a valid GPIO path for {0}!".format(sysfs_path))
            return False
        else:
            return True

    def __get_sysfs_path(self, node):

        return "/sys/class/gpio/gpio{0}/{1}".format(self.pin, str(node))


