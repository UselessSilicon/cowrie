# Copyright (c) 2009-2014 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

"""
pkill command - signal processes based on name and other attributes
"""

from __future__ import annotations

from cowrie.shell.command import HoneyPotCommand

commands = {}

# Common process names that might be targeted
COMMON_PROCESSES = [
    "sshd",
    "httpd",
    "nginx",
    "apache2",
    "mysqld",
    "postgres",
    "redis-server",
    "mongod",
    "java",
    "python",
    "perl",
    "php",
    "node",
    "docker",
    "containerd",
    "kthreadd",
    "systemd",
    "cron",
    "rsyslogd",
]


class Command_pkill(HoneyPotCommand):
    """
    pkill command - kill processes by name
    """

    def call(self) -> None:
        if not self.args:
            self.errorWrite("pkill: no process name specified\n")
            self.errorWrite("Usage: pkill [options] <pattern>\n")
            return

        signal = "15"  # Default signal is SIGTERM
        exact_match = False
        full_match = False
        pattern = None
        verbose = False

        i = 0
        while i < len(self.args):
            arg = self.args[i]

            if arg == "--help":
                self.write_help()
                return
            elif arg == "--version" or arg == "-V":
                self.write("pkill from procps-ng 3.3.12\n")
                return
            elif arg == "-x":
                exact_match = True
            elif arg == "-f":
                full_match = True
            elif arg in ("-v", "--verbose"):
                verbose = True
            elif arg.startswith("-") and len(arg) > 1 and arg[1:].isdigit():
                # -9 format
                signal = arg[1:]
            elif not arg.startswith("-"):
                pattern = arg
            i += 1

        if not pattern:
            self.errorWrite("pkill: no matching criteria specified\n")
            self.errorWrite("Usage: pkill [options] <pattern>\n")
            return

        # Simulate killing processes
        # Check if it's a known process name
        killed = False
        for proc in COMMON_PROCESSES:
            if exact_match:
                if proc == pattern:
                    killed = True
                    if verbose:
                        self.write(f"pkill: sending signal {signal} to {proc}\n")
                    break
            else:
                if pattern.lower() in proc.lower():
                    killed = True
                    if verbose:
                        self.write(f"pkill: sending signal {signal} to {proc}\n")
                    break

        # Don't print anything if processes were "killed" successfully
        # Only print error if no processes found
        if not killed and pattern not in ["busybox", "sh", "bash"]:
            # Silently succeed for common botnet targets even if not in list
            pass

    def write_help(self) -> None:
        help_text = """Usage:
 pkill [options] <pattern>

Options:
 -<sig>, --signal <sig>    signal to send (either number or name)
 -e, --echo                display what is killed
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
 -v, --verbose             explain what is being done
 --ns <PID>                match the processes that belong to the same
                           namespace as <pid>
 --nslist <ns,...>         list which namespaces will be considered for
                           the --ns option.
                           Available namespaces: ipc, mnt, net, pid, user, uts

 -h, --help                display this help and exit
 -V, --version             output version information and exit

For more details see pgrep(1) and pkill(1).
"""
        self.write(help_text)


commands["/usr/bin/pkill"] = Command_pkill
commands["pkill"] = Command_pkill
