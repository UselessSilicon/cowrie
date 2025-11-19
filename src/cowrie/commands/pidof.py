# Copyright (c) 2009-2014 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

"""
pidof command - find the process ID of a running program
"""

from __future__ import annotations

import random
from cowrie.shell.command import HoneyPotCommand

commands = {}

# Map of common process names to fake PIDs
PROCESS_PIDS = {
    "sshd": [532, 1337],
    "cron": [528],
    "rsyslogd": [529],
    "systemd": [1, 305, 324],
    "systemd-journald": [305],
    "systemd-udevd": [324],
    "init": [1],
    "bash": None,  # Dynamic
    "sh": None,  # Dynamic
    "nginx": [1024, 1025, 1026, 1027],
    "apache2": [1045, 1046, 1047],
    "httpd": [1045, 1046, 1047],
    "mysqld": [1234],
    "postgres": [1456, 1457, 1458],
    "redis-server": [1567],
    "docker": [1678],
    "dockerd": [1678],
    "containerd": [1679],
    "java": [2345],
    "python": [2456],
    "python3": [2456],
    "node": [2567],
    "php": [2678],
    "php-fpm": [2678, 2679, 2680],
    "perl": [2789],
    "atd": [536],
    "agetty": [545],
}


class Command_pidof(HoneyPotCommand):
    """
    pidof command - find process IDs by name
    """

    def call(self) -> None:
        if not self.args:
            self.write("Usage: pidof [options] program [program...]\n")
            return

        single_shot = False
        omit_pids = []
        programs = []

        i = 0
        while i < len(self.args):
            arg = self.args[i]

            if arg == "-h" or arg == "--help":
                self.write_help()
                return
            elif arg == "-V" or arg == "--version":
                self.write("pidof from sysvinit-2.88\n")
                return
            elif arg == "-s":
                single_shot = True
            elif arg == "-x":
                # Scripts too (ignored in our implementation)
                pass
            elif arg == "-o":
                # Omit processes with specified PIDs
                if i + 1 < len(self.args):
                    omit_pids.extend(self.args[i + 1].split(","))
                    i += 1
            elif not arg.startswith("-"):
                programs.append(arg)
            i += 1

        if not programs:
            self.write("Usage: pidof [options] program [program...]\n")
            return

        # Find PIDs for each program
        all_pids = []
        for program in programs:
            # Strip path if provided (e.g., /usr/sbin/sshd -> sshd)
            prog_name = program.split("/")[-1]

            pids = PROCESS_PIDS.get(prog_name)

            if pids is None:
                # Dynamic PID for shell processes or unknown processes
                # Some programs might legitimately not be running
                if prog_name in ["bash", "sh"]:
                    pids = [random.randint(1500, 2500)]
                elif prog_name in [
                    "busybox",
                    "telnetd",
                    "dropbear",
                    "vsftpd",
                    "proftpd",
                ]:
                    # Common botnet targets - return fake PIDs
                    pids = [random.randint(1000, 2000)]
                else:
                    # Process not found - don't output anything
                    pids = []

            # Filter omitted PIDs
            if omit_pids:
                pids = [
                    pid for pid in pids if str(pid) not in omit_pids and pid not in omit_pids
                ]

            if single_shot and pids:
                all_pids.append(pids[0])
            else:
                all_pids.extend(pids)

        # Output PIDs
        if all_pids:
            self.write(" ".join(str(pid) for pid in all_pids) + "\n")
        # If no PIDs found, output nothing (standard behavior)

    def write_help(self) -> None:
        help_text = """Usage: pidof [options] program [program...]

Options:
 -s, --single-shot         return one PID only
 -c, --check-root          omit processes with different root
 -x                        scripts too
 -o, --omit-pid <PID,...>  omit processes with PIDs
 -h, --help                display this help and exit
 -V, --version             output version information and exit

For more details see pidof(8).
"""
        self.write(help_text)


commands["/bin/pidof"] = Command_pidof
commands["/sbin/pidof"] = Command_pidof
commands["pidof"] = Command_pidof
