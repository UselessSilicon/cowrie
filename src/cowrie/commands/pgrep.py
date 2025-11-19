# Copyright (c) 2009-2014 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

"""
pgrep command - look up processes based on name and other attributes
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
    "containerd": [1679],
    "java": [2345],
    "python": [2456],
    "node": [2567],
    "php": [2678],
    "perl": [2789],
}


class Command_pgrep(HoneyPotCommand):
    """
    pgrep command - find processes by name
    """

    def call(self) -> None:
        if not self.args:
            self.errorWrite("pgrep: no matching criteria specified\n")
            self.errorWrite("Usage: pgrep [options] <pattern>\n")
            return

        pattern = None
        exact_match = False
        full_match = False
        list_name = False
        list_full = False
        count_matches = False
        newest = False
        oldest = False
        delimiter = "\n"

        i = 0
        while i < len(self.args):
            arg = self.args[i]

            if arg == "--help":
                self.write_help()
                return
            elif arg == "--version" or arg == "-V":
                self.write("pgrep from procps-ng 3.3.12\n")
                return
            elif arg == "-x" or arg == "--exact":
                exact_match = True
            elif arg == "-f" or arg == "--full":
                full_match = True
            elif arg == "-l" or arg == "--list-name":
                list_name = True
            elif arg == "-a" or arg == "--list-full":
                list_full = True
            elif arg == "-c" or arg == "--count":
                count_matches = True
            elif arg == "-n" or arg == "--newest":
                newest = True
            elif arg == "-o" or arg == "--oldest":
                oldest = True
            elif arg == "-d" or arg == "--delimiter":
                if i + 1 < len(self.args):
                    delimiter = self.args[i + 1]
                    i += 1
            elif not arg.startswith("-"):
                pattern = arg
            i += 1

        if not pattern:
            self.errorWrite("pgrep: no matching criteria specified\n")
            return

        # Find matching processes
        matches = []
        for proc_name, pids in PROCESS_PIDS.items():
            match = False
            if exact_match:
                if proc_name == pattern:
                    match = True
            else:
                if pattern.lower() in proc_name.lower():
                    match = True

            if match:
                if pids is None:
                    # Dynamic PID for shell processes
                    pids = [random.randint(1500, 2500)]
                for pid in pids:
                    matches.append((pid, proc_name))

        # Handle special cases
        if not matches and pattern in ["busybox", "telnetd", "dropbear"]:
            # Return fake PIDs for common botnet targets
            matches.append((random.randint(1000, 2000), pattern))

        if not matches:
            # No output if no matches found (standard behavior)
            return

        # Sort matches
        if newest:
            matches = [matches[-1]]
        elif oldest:
            matches = [matches[0]]

        # Output results
        if count_matches:
            self.write(f"{len(matches)}\n")
        else:
            for pid, proc_name in matches:
                if list_full:
                    # Show full command line
                    self.write(f"{pid} /usr/bin/{proc_name}\n")
                elif list_name:
                    # Show PID and process name
                    self.write(f"{pid} {proc_name}{delimiter}")
                else:
                    # Show only PID
                    self.write(f"{pid}{delimiter}")

    def write_help(self) -> None:
        help_text = """Usage:
 pgrep [options] <pattern>

Options:
 -d, --delimiter <string>  specify output delimiter
 -l, --list-name           list PID and process name
 -a, --list-full           list PID and full command line
 -v, --inverse             negates the matching
 -w, --lightweight         list all TID
 -c, --count               count of matching processes
 -f, --full                use full process name to match
 -g, --pgroup <PGID,...>   match listed process group IDs
 -G, --group <GID,...>     match real group IDs
 -n, --newest              select most recently started
 -o, --oldest              select least recently started
 -P, --parent <PPID,...>   match only child processes of the given parent
 -s, --session <SID,...>   match session IDs
 -t, --terminal <tty,...>  match by controlling terminal
 -u, --euid <ID,...>       match by effective IDs
 -U, --uid <ID,...>        match by real IDs
 -x, --exact               match exactly with the command name
 -F, --pidfile <file>      read PIDs from file
 -L, --logpidfile          fail if PID file is not locked
 -r, --runstates <state>   match runstates [D,S,Z,...]
 --ns <PID>                match the processes that belong to the same
                           namespace as <pid>
 --nslist <ns,...>         list which namespaces will be considered for
                           the --ns option.
                           Available namespaces: ipc, mnt, net, pid, user, uts

 -h, --help                display this help and exit
 -V, --version             output version information and exit

For more details see pgrep(1).
"""
        self.write(help_text)


commands["/usr/bin/pgrep"] = Command_pgrep
commands["pgrep"] = Command_pgrep
