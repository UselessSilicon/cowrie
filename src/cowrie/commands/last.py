# Copyright (c) 2009 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

"""
Enhanced last command with historical login data
"""

from __future__ import annotations

import random
import time

from cowrie.shell.command import HoneyPotCommand

commands = {}

# Fake historical logins to make the system look like a production server
FAKE_LOGINS = [
    ("root", "192.168.1.100", -7200, 3600),  # 2 hours ago, lasted 1 hour
    ("admin", "10.0.0.5", -86400, 7200),  # 1 day ago, lasted 2 hours
    ("root", "192.168.1.105", -172800, 1800),  # 2 days ago, lasted 30 min
    ("ubuntu", "203.0.113.42", -259200, 600),  # 3 days ago, lasted 10 min
    ("root", "192.168.1.100", -345600, 5400),  # 4 days ago, lasted 1.5 hours
]


class Command_last(HoneyPotCommand):
    """
    Enhanced last command showing login history
    """

    def call(self) -> None:
        lines = 10  # Default number of lines
        hostname_only = False
        ip_only = False
        fulltime = False
        no_hostname = False

        # Parse arguments
        args = list(self.args)
        while args:
            arg = args.pop(0)
            if arg.startswith("-"):
                if arg == "-n" and args and args[0].isdigit():
                    lines = int(args.pop(0))
                elif arg.startswith("-n") and arg[2:].isdigit():
                    lines = int(arg[2:])
                elif arg in ("-a", "--hostlast"):
                    hostname_only = True
                elif arg in ("-d", "--dns"):
                    # DNS lookup (we ignore this)
                    pass
                elif arg in ("-f", "--file"):
                    # Specify wtmp file
                    if args:
                        args.pop(0)  # Ignore the file argument
                elif arg in ("-F", "--fulltimes"):
                    fulltime = True
                elif arg in ("-i", "--ip"):
                    ip_only = True
                elif arg in ("-R", "--nohostname"):
                    no_hostname = True
                elif arg in ("-w", "--fullnames"):
                    # Full user/domain names
                    pass
                elif arg in ("-x", "--system"):
                    # Show system shutdown/reboot entries
                    pass
                elif arg == "--help":
                    self.show_help()
                    return
                elif arg == "--version":
                    self.show_version()
                    return

        # Show current session first
        self.show_login_entry(
            self.protocol.user.username,
            "pts/0",
            self.protocol.clientIP,
            self.protocol.logintime,
            None,  # Still logged in
            fulltime,
            hostname_only,
            ip_only,
            no_hostname,
        )

        # Show historical logins
        current_time = time.time()
        shown = 1  # Already showed current session

        for username, ip, time_offset, duration in FAKE_LOGINS:
            if shown >= lines:
                break

            login_time = current_time + time_offset
            logout_time = login_time + duration

            self.show_login_entry(
                username,
                f"pts/{random.randint(0, 4)}",
                ip,
                login_time,
                logout_time,
                fulltime,
                hostname_only,
                ip_only,
                no_hostname,
            )
            shown += 1

        # Show wtmp begins line
        wtmp_start = current_time - 604800  # 7 days ago
        self.write("\n")
        if fulltime:
            self.write(
                "wtmp begins {}\n".format(
                    time.strftime("%a %b %d %H:%M:%S %Y", time.localtime(wtmp_start))
                )
            )
        else:
            self.write(
                "wtmp begins {}\n".format(
                    time.strftime("%a %b %d %H:%M:%S %Y", time.localtime(wtmp_start))
                )
            )

    def show_login_entry(
        self,
        username: str,
        tty: str,
        ip: str,
        login_time: float,
        logout_time: float | None,
        fulltime: bool,
        hostname_only: bool,
        ip_only: bool,
        no_hostname: bool,
    ) -> None:
        """Show a single login entry"""
        # Format username and tty
        user_field = f"{username:8s}"
        tty_field = f"{tty:12s}"

        # Format IP/hostname
        if no_hostname:
            ip_field = ""
        elif hostname_only:
            ip_field = f"{ip:16s}"
        elif ip_only:
            ip_field = f"{ip:16s}"
        else:
            ip_field = f"{ip:16s}"

        # Format login time
        if fulltime:
            time_str = time.strftime("%a %b %d %H:%M:%S %Y", time.localtime(login_time))
        else:
            time_str = time.strftime("%a %b %d %H:%M", time.localtime(login_time))

        # Format duration/status
        if logout_time is None:
            status = "still logged in"
        else:
            duration = int(logout_time - login_time)
            hours = duration // 3600
            minutes = (duration % 3600) // 60

            if hours > 0:
                status = f"({hours:02d}:{minutes:02d})"
            else:
                status = f"(00:{minutes:02d})"

        # Write the line
        if no_hostname:
            self.write(f"{user_field} {tty_field} {time_str:24s}   {status}\n")
        else:
            self.write(
                f"{user_field} {tty_field} {ip_field} {time_str:24s}   {status}\n"
            )

    def show_help(self) -> None:
        """Show last command help"""
        self.write(
            """Usage:
 last [options] [<username>...] [<tty>...]

Show a listing of last logged in users.

Options:
 -<number>            how many lines to show
 -a, --hostlast       display hostnames in the last column
 -d, --dns            translate the IP number back into a hostname
 -f, --file <file>    use a specific file instead of /var/log/wtmp
 -F, --fulltimes      print full login and logout times and dates
 -i, --ip             display IP numbers rather than hostnames
 -n, --limit <number> how many lines to show
 -R, --nohostname     don't display the hostname field
 -s, --since <time>   display the lines since the specified time
 -t, --until <time>   display the lines until the specified time
 -p, --present <time> display who were present at the specified time
 -w, --fullnames      display full user and domain names
 -x, --system         display system shutdown entries and run level changes

 -h, --help     display this help and exit
 -V, --version  output version information and exit

For more details see last(1).
"""
        )

    def show_version(self) -> None:
        """Show last command version"""
        self.write("last from util-linux 2.27.1\n")


commands["/usr/bin/last"] = Command_last
commands["last"] = Command_last
