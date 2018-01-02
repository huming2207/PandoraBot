import subprocess
import json

from Settings import Settings


class ToolRunner:

    @staticmethod
    def start_flashrom(mode, file="/tmp/pbt/flash.bin", programmer="linux_spi"):
        mode_switch = {
            "read": "-r",
            "write": "-w",
            "erase": "-E"
        }

        flashrom_log_opt = open(Settings.load_settings("flashrom_log_location"), "w+")
        flashrom_args = "Command: flashrom -p {} {} {}".format(programmer, mode_switch[mode], str(file))
        print(flashrom_args)

        # In erase mode, the file must not be specified, otherwise it refuses to work.
        if mode == "erase":
            process = subprocess.Popen(args=['flashrom', "-p", programmer, mode_switch[mode]],
                                       stdout=flashrom_log_opt,
                                       stderr=flashrom_log_opt)

            process.wait()
        else:
            process = subprocess.Popen(args=['flashrom', "-p", programmer, mode_switch[mode], str(file)],
                                       stdout=flashrom_log_opt,
                                       stderr=flashrom_log_opt)

            process.wait()

        flashrom_log_opt.write("\nPBT: Flashrom process finished!\n")
        flashrom_log_opt.flush()
        flashrom_log_opt.close()
