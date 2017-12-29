import subprocess
from FlashromTaskType import FlashromTaskType
from threading import Thread
from queue import Queue, Empty


class ServerController:

    flashrom_stdout_queue = Queue()

    def startFlashrom(self, mode, file = "/tmp/pbt/flash.bin", programmer = "linux_spi"):

        mode_switch = {
            FlashromTaskType.READ: "-r",
            FlashromTaskType.WRITE: "-w",
            FlashromTaskType.ERASE: "-E"
        }

        flashrom_opt = open('/tmp/pbt/pbt_flashrom.log', 'w+')

        process = subprocess.Popen(["flashrom", "-p", programmer, mode_switch[mode], file],
                                   stdout=flashrom_opt,
                                   stderr=flashrom_opt)










