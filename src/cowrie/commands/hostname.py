# Copyright (c) 2009-2014 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

"""
hostname command - show or set system hostname
Common reconnaissance command
"""

from __future__ import annotations

import getopt

from cowrie.core.config import CowrieConfig
from cowrie.shell.command import HoneyPotCommand

commands = {}


class Command_hostname(HoneyPotCommand):
    """
    hostname command - show or set the system's host name
    Used by attackers during reconnaissance phase
    """

    def call(self) -> None:
        """Execute hostname command"""
        # Parse options
        show_fqdn = False
        show_short = False
        show_ip = False
        show_all_fqdn = False
        show_domain = False

        try:
            optlist, args = getopt.getopt(self.args, "aAdfisyV")
        except getopt.GetoptError as err:
            self.write(f"hostname: {err}\n")
            self.write("Try 'hostname --help' for more information.\n")
            return

        for opt, arg in optlist:
            if opt == "-a" or opt == "-A":
                show_all_fqdn = True
            elif opt == "-d":
                show_domain = True
            elif opt == "-f":
                show_fqdn = True
            elif opt == "-i":
                show_ip = True
            elif opt == "-s":
                show_short = True
            elif opt == "-y":
                self.write("hostname: not supported\n")
                return
            elif opt == "-V":
                self.write("hostname 3.23\n")
                return

        # Get hostname from config
        hostname = CowrieConfig.get("honeypot", "hostname", fallback="server01")

        # If trying to set hostname (args provided)
        if args and not any([show_fqdn, show_short, show_ip, show_all_fqdn, show_domain]):
            username = self.protocol.user.username
            if username != "root":
                # Not root - show realistic error message
                self.write("hostname: you must be root to change the host name\n")
                return
            # Root user - pretend to succeed (but don't actually change anything)
            # Silently return without error to maintain honeypot realism
            return

        # Handle different display options
        if show_domain:
            # Show domain name only
            if "." in hostname:
                domain = ".".join(hostname.split(".")[1:])
                self.write(f"{domain}\n")
            else:
                self.write("hostname: Local domain name not set\n")
            return

        if show_ip:
            # Show IP address
            self.write("127.0.1.1\n")
            return

        if show_fqdn or show_all_fqdn:
            # Show fully qualified domain name
            if "." not in hostname:
                hostname = f"{hostname}.localdomain"
            self.write(f"{hostname}\n")
            return

        if show_short:
            # Show short hostname (before first dot)
            short_name = hostname.split(".")[0]
            self.write(f"{short_name}\n")
            return

        # Default - just show hostname
        self.write(f"{hostname}\n")


commands["/bin/hostname"] = Command_hostname
commands["hostname"] = Command_hostname
