import subprocess
import time

from Settings import Settings


class ToolRunner:

    @staticmethod
    def start_flashrom(mode, file="/tmp/pbt/flash.bin", programmer="linux_spi"):
        mode_switch = {
            "read": "-r",
            "write": "-w",
            "erase": "-E"
        }

        flashrom_log_opt = open(Settings.get("flashrom_log_location"), "w+")

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

        # Add a magic flag line to make it stop sending
        flashrom_log_opt.write("\nPBT: Flashrom process finished!\n")
        flashrom_log_opt.flush()
        flashrom_log_opt.close()

    @staticmethod
    def start_openocd(config_files=None, wait=True):

        if config_files is None:
            config_files = []
        base_args = ["openocd"]

        for file in config_files:
            base_args.append("-f")
            base_args.append(file)

        ocd_log_opt = open(Settings.get("ocd_log_location"), "w+")

        process = subprocess.Popen(base_args, stdout=ocd_log_opt, stderr=ocd_log_opt)

        # As OpenOCD will run for quite a while, we can't use process.wait() here.
        if wait:
            time.sleep(5)

        ocd_log_opt.write("\nPBT: OpenOCD process finished!\n")
        ocd_log_opt.flush()

    @staticmethod
    def kill_process(process_name):
        process = subprocess.Popen(["killall", "-9", str(process_name)])
        process.wait()


    @staticmethod
    def start_ttyd(baud, data, flow, parity):

        ttyd_cmd_list = ["ttyd", "-p", Settings.get("ttyd_port")]

        picocom_cmd_list = ["picocom",
                            "-b", str(baud),
                            "-d", str(data),
                            "-f", str(flow),
                            "-p", str(parity),
                            Settings.get("picocom_tty_device")]

        # Merge picocom command into original list
        ttyd_cmd_list.extend(picocom_cmd_list)

        ttyd_log_opt = open(Settings.get("ttyd_log_location"), "w+")

        process = subprocess.Popen(args=ttyd_cmd_list, stdout=ttyd_log_opt, stderr=ttyd_log_opt)

        process.wait()
