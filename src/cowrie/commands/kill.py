# Copyright (c) 2009-2014 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

"""
kill command
"""

from __future__ import annotations

from cowrie.shell.command import HoneyPotCommand

commands = {}

KILL_HELP = """Usage:
 kill [options] <pid> [...]

Options:
 <pid> [...]            send signal to every <pid> listed
 -<signal>, -s, --signal <signal>
                        specify the <signal> to be sent
 -l, --list=[<signal>]  list all signal names, or convert one to a name
 -L, --table            list all signal names in a nice table

 -h, --help     display this help and exit
 -V, --version  output version information and exit

For more details see kill(1).
"""

KILL_VERSION = """kill from util-linux 2.27.1"""

# Signal names and numbers
SIGNALS = {
    "1": "HUP",
    "2": "INT",
    "3": "QUIT",
    "6": "ABRT",
    "9": "KILL",
    "14": "ALRM",
    "15": "TERM",
    "HUP": "1",
    "INT": "2",
    "QUIT": "3",
    "ABRT": "6",
    "KILL": "9",
    "ALRM": "14",
    "TERM": "15",
    "SIGHUP": "1",
    "SIGINT": "2",
    "SIGQUIT": "3",
    "SIGABRT": "6",
    "SIGKILL": "9",
    "SIGALRM": "14",
    "SIGTERM": "15",
}

SIGNAL_LIST = """ 1) SIGHUP       2) SIGINT       3) SIGQUIT      4) SIGILL       5) SIGTRAP
 6) SIGABRT      7) SIGBUS       8) SIGFPE       9) SIGKILL     10) SIGUSR1
11) SIGSEGV     12) SIGUSR2     13) SIGPIPE     14) SIGALRM     15) SIGTERM
16) SIGSTKFLT   17) SIGCHLD     18) SIGCONT     19) SIGSTOP     20) SIGTSTP
21) SIGTTIN     22) SIGTTOU     23) SIGURG      24) SIGXCPU     25) SIGXFSZ
26) SIGVTALRM   27) SIGPROF     28) SIGWINCH    29) SIGIO       30) SIGPWR
31) SIGSYS      34) SIGRTMIN    35) SIGRTMIN+1  36) SIGRTMIN+2  37) SIGRTMIN+3
38) SIGRTMIN+4  39) SIGRTMIN+5  40) SIGRTMIN+6  41) SIGRTMIN+7  42) SIGRTMIN+8
43) SIGRTMIN+9  44) SIGRTMIN+10 45) SIGRTMIN+11 46) SIGRTMIN+12 47) SIGRTMIN+13
48) SIGRTMIN+14 49) SIGRTMIN+15 50) SIGRTMAX-14 51) SIGRTMAX-13 52) SIGRTMAX-12
53) SIGRTMAX-11 54) SIGRTMAX-10 55) SIGRTMAX-9  56) SIGRTMAX-8  57) SIGRTMAX-7
58) SIGRTMAX-6  59) SIGRTMAX-5  60) SIGRTMAX-4  61) SIGRTMAX-3  62) SIGRTMAX-2
63) SIGRTMAX-1  64) SIGRTMAX
"""


class Command_kill(HoneyPotCommand):
    """
    kill command - send a signal to a process
    """

    def call(self) -> None:
        if not self.args:
            self.write(
                "kill: usage: kill [-s sigspec | -n signum | -sigspec] pid | jobspec "
                "... or kill -l [sigspec]\n"
            )
            return

        signal = "15"  # Default signal is SIGTERM
        list_signals = False
        pids = []

        try:
            # Custom parsing to handle -9, -KILL, -s 9, etc.
            i = 0
            while i < len(self.args):
                arg = self.args[i]

                if arg == "--help" or arg == "-h":
                    self.write(KILL_HELP)
                    return
                elif arg == "--version" or arg == "-V":
                    self.write(KILL_VERSION + "\n")
                    return
                elif arg in ("-l", "--list"):
                    list_signals = True
                    # Check if next arg is a signal number to convert
                    if i + 1 < len(self.args) and self.args[i + 1].isdigit():
                        sig_num = self.args[i + 1]
                        if sig_num in SIGNALS:
                            self.write(f"{SIGNALS[sig_num]}\n")
                        else:
                            self.write(f"kill: unknown signal: {sig_num}\n")
                        return
                    i += 1
                    continue
                elif arg in ("-L", "--table"):
                    self.write(SIGNAL_LIST)
                    return
                elif arg == "-s" or arg == "--signal":
                    if i + 1 < len(self.args):
                        signal = self.args[i + 1]
                        i += 2
                        continue
                    else:
                        self.write("kill: option requires an argument -- 's'\n")
                        return
                elif arg.startswith("-") and not arg[1:].isdigit():
                    # Handle -SIGNAL format
                    sig_name = arg[1:].upper()
                    if sig_name.startswith("SIG"):
                        sig_name = sig_name[3:]
                    if sig_name in SIGNALS:
                        signal = SIGNALS[sig_name]
                    elif sig_name in ["S", "N"]:
                        # -s or -n followed by signal
                        if i + 1 < len(self.args):
                            signal = self.args[i + 1]
                            i += 2
                            continue
                    else:
                        self.write(f"kill: invalid signal specification: {arg}\n")
                        return
                    i += 1
                elif arg.startswith("-") and arg[1:].isdigit():
                    # Handle -9 format
                    signal = arg[1:]
                    i += 1
                else:
                    # Must be a PID
                    pids.append(arg)
                    i += 1

        except Exception as e:
            self.write(f"kill: {e}\n")
            return

        # If -l was specified without arguments, show full list
        if list_signals and not pids:
            self.write(SIGNAL_LIST)
            return

        # Validate signal
        if signal.isdigit():
            if signal not in SIGNALS:
                self.write(f"kill: invalid signal number: {signal}\n")
                return
        else:
            sig_name = signal.upper()
            if sig_name.startswith("SIG"):
                sig_name = sig_name[3:]
            if sig_name not in SIGNALS:
                self.write(f"kill: invalid signal: {signal}\n")
                return

        # Process PIDs
        if not pids:
            self.write("kill: no process ID specified\n")
            return

        for pid in pids:
            # Validate PID format
            if not pid.lstrip("-").isdigit():
                self.write(f"kill: invalid process id: {pid}\n")
                continue

            pid_num = int(pid)

            # Check for special PIDs
            if pid_num == 1:
                self.errorWrite(f"kill: ({pid_num}) - Operation not permitted\n")
            elif pid_num < 1:
                self.errorWrite(f"kill: ({pid_num}) - No such process\n")
            elif pid_num < 300:
                # System processes - permission denied
                self.errorWrite(f"kill: ({pid_num}) - Operation not permitted\n")
            else:
                # Would kill the process (but we just pretend it worked)
                # No output means success
                pass


commands["/bin/kill"] = Command_kill
commands["kill"] = Command_kill
