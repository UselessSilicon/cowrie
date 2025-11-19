# Copyright (c) 2009-2014 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

"""
ps command - report a snapshot of current processes
"""

from __future__ import annotations

import random
from cowrie.shell.command import HoneyPotCommand

commands = {}

# Fake process list that looks realistic
# Format: (PID, TTY, TIME, CMD)
FAKE_PROCESSES = [
    (1, "?", "00:00:01", "/sbin/init"),
    (2, "?", "00:00:00", "[kthreadd]"),
    (3, "?", "00:00:00", "[ksoftirqd/0]"),
    (5, "?", "00:00:00", "[kworker/0:0H]"),
    (7, "?", "00:00:00", "[migration/0]"),
    (8, "?", "00:00:00", "[rcu_bh]"),
    (9, "?", "00:00:00", "[rcu_sched]"),
    (10, "?", "00:00:00", "[watchdog/0]"),
    (11, "?", "00:00:00", "[watchdog/1]"),
    (12, "?", "00:00:00", "[migration/1]"),
    (13, "?", "00:00:00", "[ksoftirqd/1]"),
    (15, "?", "00:00:00", "[kworker/1:0H]"),
    (17, "?", "00:00:00", "[kdevtmpfs]"),
    (18, "?", "00:00:00", "[netns]"),
    (19, "?", "00:00:00", "[khungtaskd]"),
    (20, "?", "00:00:00", "[writeback]"),
    (21, "?", "00:00:00", "[ksmd]"),
    (22, "?", "00:00:00", "[khugepaged]"),
    (23, "?", "00:00:00", "[crypto]"),
    (24, "?", "00:00:00", "[kintegrityd]"),
    (25, "?", "00:00:00", "[bioset]"),
    (26, "?", "00:00:00", "[kblockd]"),
    (27, "?", "00:00:00", "[devfreq_wq]"),
    (28, "?", "00:00:00", "[kswapd0]"),
    (29, "?", "00:00:00", "[vmstat]"),
    (201, "?", "00:00:00", "[scsi_eh_0]"),
    (202, "?", "00:00:00", "[scsi_tmf_0]"),
    (203, "?", "00:00:00", "[scsi_eh_1]"),
    (204, "?", "00:00:00", "[scsi_tmf_1]"),
    (231, "?", "00:00:00", "[kworker/1:1H]"),
    (237, "?", "00:00:00", "[jbd2/sda1-8]"),
    (238, "?", "00:00:00", "[ext4-rsv-conver]"),
    (305, "?", "00:00:00", "/lib/systemd/systemd-journald"),
    (324, "?", "00:00:00", "/lib/systemd/systemd-udevd"),
    (528, "?", "00:00:00", "/usr/sbin/cron -f"),
    (529, "?", "00:00:00", "/usr/sbin/rsyslogd -n"),
    (532, "?", "00:00:00", "/usr/sbin/sshd -D"),
    (536, "?", "00:00:00", "/usr/sbin/atd -f"),
    (545, "tty1", "00:00:00", "/sbin/agetty --noclear tty1 linux"),
    (1337, "?", "00:00:00", "sshd: root@pts/0"),
]


class Command_ps(HoneyPotCommand):
    """
    ps command implementation
    """

    def call(self) -> None:
        # Parse arguments
        show_all = False
        show_full = False
        show_user = False
        bsd_style = False
        aux_format = False
        ef_format = False
        show_forest = False

        args = self.args[:]

        # Handle combined options like -aux or aux (BSD style)
        i = 0
        while i < len(args):
            arg = args[i]

            if arg == "--help":
                self.write_help()
                return
            elif arg == "--version":
                self.write("ps from procps-ng 3.3.12\n")
                return
            elif arg in ("-e", "-A"):
                show_all = True
            elif arg == "-f":
                show_full = True
                ef_format = True
            elif arg == "-u":
                show_user = True
            elif arg == "-ef":
                show_all = True
                show_full = True
                ef_format = True
            elif arg == "aux" or arg == "-aux":
                aux_format = True
                show_all = True
            elif arg == "-w":
                # Wide output (ignored, we always use wide)
                pass
            elif arg == "--forest" or arg == "-H":
                show_forest = True
            elif arg.startswith("-") and len(arg) > 1 and not arg.startswith("--"):
                # Parse combined flags like -ef, -aux
                for char in arg[1:]:
                    if char == "e" or char == "A":
                        show_all = True
                    elif char == "f":
                        show_full = True
                        ef_format = True
                    elif char == "u":
                        show_user = True
                    elif char == "a":
                        show_all = True
                        aux_format = True
                    elif char == "x":
                        show_all = True
                        aux_format = True
                    elif char == "w":
                        pass  # Wide output
                    elif char == "H":
                        show_forest = True
            i += 1

        # Get current session PID (simulate it)
        session_pid = random.randint(1500, 2500)

        if aux_format:
            # BSD-style output: USER PID %CPU %MEM VSZ RSS TTY STAT START TIME COMMAND
            self.write(
                "USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND\n"
            )
            for pid, tty, time, cmd in FAKE_PROCESSES:
                user = "root"
                cpu = "0.0"
                mem = "0.0"
                vsz = random.randint(1000, 50000)
                rss = random.randint(100, 5000)
                stat = "S" if pid > 1 else "Ss"
                start = "Nov18"
                self.write(
                    f"{user:<8} {pid:>5} {cpu:>4} {mem:>4} {vsz:>6} {rss:>5} {tty:<8} {stat:<4} {start:<6} {time} {cmd}\n"
                )
            # Add current session
            self.write(
                f"{'root':<8} {session_pid:>5} {'0.0':>4} {'0.1':>4} {21324:>6} {3456:>5} {'pts/0':<8} {'Ss':<4} {'Nov19':<6} 00:00:00 -bash\n"
            )
            self.write(
                f"{'root':<8} {session_pid + 1:>5} {'0.0':>4} {'0.0':>4} {15216:>6} {1124:>5} {'pts/0':<8} {'R+':<4} {'15:30':<6} 00:00:00 ps aux\n"
            )

        elif ef_format:
            # Unix-style -ef output: UID PID PPID C STIME TTY TIME CMD
            self.write("UID        PID  PPID  C STIME TTY          TIME CMD\n")
            for pid, tty, time, cmd in FAKE_PROCESSES:
                uid = "root"
                ppid = 0 if pid <= 2 else (1 if pid < 100 else 2)
                c = "0"
                stime = "Nov18" if pid < 1000 else "15:30"
                self.write(
                    f"{uid:<8} {pid:>5} {ppid:>5} {c:>2} {stime:<6} {tty:<12} {time} {cmd}\n"
                )
            # Add current session
            self.write(
                f"{'root':<8} {session_pid:>5} {532:>5} {'0':>2} {'15:30':<6} {'pts/0':<12} 00:00:00 -bash\n"
            )
            self.write(
                f"{'root':<8} {session_pid + 1:>5} {session_pid:>5} {'0':>2} {'15:30':<6} {'pts/0':<12} 00:00:00 ps -ef\n"
            )

        elif show_all:
            # Simple -e output: PID TTY TIME CMD
            self.write("  PID TTY          TIME CMD\n")
            for pid, tty, time, cmd in FAKE_PROCESSES:
                self.write(f"{pid:>5} {tty:<12} {time} {cmd}\n")
            # Add current session
            self.write(f"{session_pid:>5} {'pts/0':<12} 00:00:00 bash\n")
            self.write(f"{session_pid + 1:>5} {'pts/0':<12} 00:00:00 ps\n")

        else:
            # Default: show only current user's processes
            self.write("  PID TTY          TIME CMD\n")
            self.write(f"{session_pid:>5} {'pts/0':<12} 00:00:00 bash\n")
            self.write(f"{session_pid + 1:>5} {'pts/0':<12} 00:00:00 ps\n")

    def write_help(self) -> None:
        help_text = """Usage:
 ps [options]

Basic options:
 -A, -e               all processes
 -a                   all with tty, except session leaders
  a                   all with tty, including other users
 -d                   all except session leaders
 -N, --deselect       negate selection
  r                   only running processes
  T                   all processes on this terminal
  x                   processes without controlling ttys

Selection by list:
 -C <command>         command name
 -G, --Group <GID>    real group id or name
 -g, --group <group>  session or effective group name
 -p, p, --pid <PID>   process id
     --ppid <PID>     parent process id
 -s, --sid <session>  session id
 -t, t, --tty <tty>   terminal
 -u, U, --user <UID>  effective user id or name
 -U, --User <UID>     real user id or name

Output formats:
 -F                   extra full
 -f                   full-format, including command lines
  f, --forest         ascii art process tree
 -H                   show process hierarchy
 -j                   jobs format
  j                   BSD job control format
 -l                   long format
  l                   BSD long format
 -M, Z                add security data (for SELinux)
 -O <format>          preloaded with default columns
  O <format>          as -O, with BSD personality
 -o, o, --format <format>
                      user-defined format
  s                   signal format
  u                   user-oriented format
  v                   virtual memory format
  X                   register format
 -y                   do not show flags, show rss vs. addr (used with -l)
     --context        display security context (for SELinux)
     --headers        repeat header lines, one per page
     --no-headers     do not print header at all
     --cols, --columns, --width <num>
                      set screen width
     --rows, --lines <num>
                      set screen height

Show threads:
 -L                   possibly with LWP and NLWP columns
 -m, m                after processes
 -T                   possibly with SPID column

Misc options:
 -c                   show scheduling class with -l option
  c                   show true command name
  e                   show the environment after command
  k,    --sort        specify sort order as: [+|-]key[,[+|-]key[,...]]
  L                   show format specifiers
  n                   display numeric uid and wchan
  S,    --cumulative  include some dead child process data
 -y                   do not show flags, show rss (only with -l)
 -V, V, --version     display version information and exit
 -w, w                unlimited output width

 -h, --help           display this help and exit

For more details see ps(1).
"""
        self.write(help_text)


commands["/bin/ps"] = Command_ps
commands["ps"] = Command_ps
