# Copyright (c) 2009-2014 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

"""
who command - show who is logged on
Common reconnaissance command
"""

from __future__ import annotations

import getopt
import time

from cowrie.shell.command import HoneyPotCommand

commands = {}


class Command_who(HoneyPotCommand):
    """
    who command - show who is logged on
    Used by attackers to detect other logged-in users
    """

    def call(self) -> None:
        """Execute who command"""
        # Parse options
        show_all = False
        show_boot = False
        show_dead = False
        show_heading = False
        show_users = False
        show_message = False
        quick = False

        try:
            optlist, args = getopt.getopt(self.args, "abdHmqsTu")
        except getopt.GetoptError:
            pass
        else:
            for opt, arg in optlist:
                if opt == "-a":
                    show_all = True
                elif opt == "-b":
                    show_boot = True
                elif opt == "-d":
                    show_dead = True
                elif opt == "-H":
                    show_heading = True
                elif opt == "-m":
                    show_users = True
                elif opt == "-q":
                    quick = True
                elif opt == "-s":
                    pass  # Short format (default)
                elif opt == "-T" or opt == "-w":
                    show_message = True
                elif opt == "-u":
                    pass  # Show idle time

        # Quick mode - just show usernames
        if quick:
            username = self.protocol.user.username
            self.write(f"{username}\n")
            self.write("# users=1\n")
            return

        # Show heading if requested
        if show_heading:
            if show_message:
                self.write("NAME     LINE         TIME             COMMENT\n")
            else:
                self.write("NAME     LINE         TIME             IDLE  PID   COMMENT\n")

        # Show boot time if requested
        if show_boot or show_all:
            boot_time = time.strftime("%Y-%m-%d %H:%M", time.localtime(time.time() - 86400))
            self.write(f"         system boot  {boot_time}\n")

        # Show current user
        username = self.protocol.user.username
        src_ip = self.protocol.transport.getPeer().host
        login_time = time.strftime("%Y-%m-%d %H:%M", time.localtime())

        # Determine terminal
        terminal = "pts/0"

        if show_message:
            # With message status
            self.write(f"{username:<8} {terminal:<12} {login_time} ({src_ip})\n")
        else:
            # Standard format with idle time
            self.write(f"{username:<8} {terminal:<12} {login_time}   .     {self.protocol.sessionno:<5} ({src_ip})\n")


commands["/usr/bin/who"] = Command_who
commands["who"] = Command_who
