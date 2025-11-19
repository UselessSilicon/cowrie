# Copyright (c) 2009-2014 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

"""
killall command - kill processes by name
"""

from __future__ import annotations

from cowrie.shell.command import HoneyPotCommand

commands = {}


class Command_killall(HoneyPotCommand):
    """
    killall command - kill all processes by name
    """

    def call(self) -> None:
        if not self.args:
            self.write(
                "Usage: killall [OPTION]... [--] NAME...\n"
                "       killall -l, --list\n"
                "       killall -V, --version\n\n"
                "  -e,--exact          require exact match for very long names\n"
                "  -I,--ignore-case    case insensitive process name match\n"
                "  -g,--process-group  kill process group instead of process\n"
                "  -y,--younger-than   kill processes younger than TIME\n"
                "  -o,--older-than     kill processes older than TIME\n"
                "  -i,--interactive    ask for confirmation before killing\n"
                "  -l,--list           list all known signal names\n"
                "  -q,--quiet          don't print complaints\n"
                "  -r,--regexp         interpret NAME as an extended regular expression\n"
                "  -s,--signal SIGNAL  send this signal instead of SIGTERM\n"
                "  -u,--user USER      kill only process(es) running as USER\n"
                "  -v,--verbose        report if the signal was successfully sent\n"
                "  -V,--version        display version information\n"
                "  -w,--wait           wait for processes to die\n"
                "  -n,--ns PID         match processes that belong to the same namespaces\n"
                "                      as PID\n"
                "  -Z,--context REGEXP kill only process(es) having context\n"
                "                      (must precede other arguments)\n"
            )
            return

        signal = "TERM"  # Default signal
        quiet = False
        verbose = False
        exact = False
        ignore_case = False
        process_names = []

        i = 0
        while i < len(self.args):
            arg = self.args[i]

            if arg == "-l" or arg == "--list":
                self.write(
                    "HUP INT QUIT ILL TRAP ABRT BUS FPE KILL USR1 SEGV USR2 PIPE ALRM TERM\n"
                )
                self.write(
                    "STKFLT CHLD CONT STOP TSTP TTIN TTOU URG XCPU XFSZ VTALRM PROF WINCH POLL\n"
                )
                self.write("PWR SYS\n")
                return
            elif arg == "-V" or arg == "--version":
                self.write("killall (PSmisc) 23.1\n")
                self.write(
                    "Copyright (C) 1993-2017 Werner Almesberger and Craig Small\n\n"
                )
                self.write(
                    "PSmisc comes with ABSOLUTELY NO WARRANTY.\n"
                    "This is free software, and you are welcome to redistribute it under\n"
                    "the terms of the GNU General Public License.\n"
                    "For more information about these matters, see the files named COPYING.\n"
                )
                return
            elif arg == "-q" or arg == "--quiet":
                quiet = True
            elif arg == "-v" or arg == "--verbose":
                verbose = True
            elif arg == "-e" or arg == "--exact":
                exact = True
            elif arg == "-I" or arg == "--ignore-case":
                ignore_case = True
            elif arg == "-s" or arg == "--signal":
                if i + 1 < len(self.args):
                    signal = self.args[i + 1]
                    i += 1
                else:
                    self.write("killall: option requires an argument -- 's'\n")
                    return
            elif arg.startswith("-") and len(arg) > 1 and not arg.startswith("--"):
                # Could be -9 or other signal
                if arg[1:].isdigit() or arg[1:].isalpha():
                    signal = arg[1:]
            elif not arg.startswith("-"):
                process_names.append(arg)

            i += 1

        if not process_names:
            self.write("killall: no process selection criteria\n")
            return

        # Simulate killing processes
        for proc_name in process_names:
            # Botnets often try to kill competing malware or specific processes
            # We silently succeed for most process names
            # Common targets: telnetd, sshd, dropbear, busybox, sh, bash, apache2, nginx, httpd

            # Some processes might not exist
            if proc_name in ["nonexistent", "fakeprocess"]:
                if not quiet:
                    self.write(f"killall: {proc_name}: no process found\n")
            else:
                # Silently succeed - process "killed"
                if verbose:
                    self.write(f"Killed {proc_name} with signal {signal}\n")
                pass


commands["/usr/bin/killall"] = Command_killall
commands["killall"] = Command_killall
