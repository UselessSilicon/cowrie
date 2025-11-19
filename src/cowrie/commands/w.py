# Copyright (c) 2009-2014 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

"""
w command - show who is logged on and what they are doing
Common reconnaissance command to detect other active users
"""

from __future__ import annotations

import getopt
import time

from cowrie.shell.command import HoneyPotCommand

commands = {}


class Command_w(HoneyPotCommand):
    """
    w command - show who is logged on and what they are doing
    Used by attackers to detect other active sessions
    """

    def call(self) -> None:
        """Execute w command"""
        # Parse options
        no_header = False
        short_format = False
        from_field = True

        try:
            optlist, args = getopt.getopt(self.args, "hsfV")
        except getopt.GetoptError:
            pass
        else:
            for opt, arg in optlist:
                if opt == "-h":
                    no_header = True
                elif opt == "-s":
                    short_format = True
                elif opt == "-f":
                    from_field = False
                elif opt == "-V":
                    self.write("w from procps-ng 3.3.15\n")
                    return

        # Get current time and uptime
        current_time = time.strftime("%H:%M:%S")

        # Calculate uptime (simulate a reasonable uptime)
        uptime_seconds = 345600  # 4 days
        uptime_days = uptime_seconds // 86400
        uptime_hours = (uptime_seconds % 86400) // 3600
        uptime_mins = (uptime_seconds % 3600) // 60

        # Get load averages (simulate)
        load_avg = "0.08, 0.12, 0.15"

        # Get user count
        user_count = 1

        # Show header unless -h is specified
        if not no_header:
            self.write(f" {current_time} up {uptime_days} days, {uptime_hours:2d}:{uptime_mins:02d},  {user_count} user,  load average: {load_avg}\n")
            if short_format:
                self.write("USER     TTY      FROM              IDLE WHAT\n")
            else:
                self.write("USER     TTY      FROM             LOGIN@   IDLE   JCPU   PCPU WHAT\n")

        # Show current user info
        username = self.protocol.user.username
        src_ip = self.protocol.transport.getPeer().host
        login_time = time.strftime("%H:%M", time.localtime())
        terminal = "pts/0"
        idle = "0.00s"
        jcpu = "0.01s"
        pcpu = "0.00s"
        what = "-bash"

        if short_format:
            self.write(f"{username:<8} {terminal:<8} {src_ip:<17} {idle:<4} {what}\n")
        else:
            self.write(f"{username:<8} {terminal:<8} {src_ip:<16} {login_time:<8} {idle:<6} {jcpu:<6} {pcpu:<5} {what}\n")


commands["/usr/bin/w"] = Command_w
commands["w"] = Command_w
