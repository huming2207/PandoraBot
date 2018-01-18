import os
import re


class LogHelpers:

    def __init__(self):

        # Percentage
        self.flashrom_percentage = ""

        # Address range
        self.flashrom_addr_start = ""
        self.flashrom_addr_end = ""

    def stream_log(self, log_file, delete=False, end_line=""):

        # Stream file to the client
        while True:
            new_line = log_file.readline()

            # Percent string looks like "0.27 %, 0x00b000 to 0x00bfff"
            # ref: https://github.com/huming2207/flashrom_google/blob/master/flashrom.c#L1575
            if new_line[0].isdigit() and ", " in new_line:

                progress_details = re.split(" %, | to ", new_line)

                self.flashrom_percentage = str(progress_details[0])
                self.flashrom_addr_start = str(progress_details[1])
                self.flashrom_addr_end = str(progress_details[2])

            # Stream the file to the client until it ends. When it ends, remove it.
            if end_line in new_line:
                yield new_line  # Flush the last line

                if delete:
                    os.remove(log_file.name)
                    log_file.close()

                break

            # Return the line only if the line is not empty
            if new_line:
                yield new_line + "<br>"


