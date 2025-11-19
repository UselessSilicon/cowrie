# Copyright (c) 2009-2014 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

"""
hostnamectl command - Control the system hostname
"""

from __future__ import annotations

from cowrie.core.config import CowrieConfig
from cowrie.shell.command import HoneyPotCommand

commands = {}


class Command_hostnamectl(HoneyPotCommand):
    """
    hostnamectl command - Control the system hostname and related settings
    """

    def call(self) -> None:
        if not self.args:
            # Default: show status
            self.show_status()
            return

        action = self.args[0]

        if action in ("--help", "-h"):
            self.show_help()
        elif action == "--version":
            self.show_version()
        elif action == "status":
            self.show_status()
        elif action == "set-hostname":
            if len(self.args) < 2:
                self.errorWrite("hostnamectl: set-hostname requires an argument\n")
                return
            self.set_hostname(self.args[1])
        elif action == "set-icon-name":
            if len(self.args) < 2:
                self.errorWrite("hostnamectl: set-icon-name requires an argument\n")
                return
            self.set_icon_name(self.args[1])
        elif action == "set-chassis":
            if len(self.args) < 2:
                self.errorWrite("hostnamectl: set-chassis requires an argument\n")
                return
            self.set_chassis(self.args[1])
        elif action == "set-deployment":
            if len(self.args) < 2:
                self.errorWrite("hostnamectl: set-deployment requires an argument\n")
                return
            # Require root
            if self.protocol.user.username != "root":
                self.errorWrite("Failed to set deployment: Access denied\n")
        elif action == "set-location":
            if len(self.args) < 2:
                self.errorWrite("hostnamectl: set-location requires an argument\n")
                return
            # Require root
            if self.protocol.user.username != "root":
                self.errorWrite("Failed to set location: Access denied\n")
        else:
            self.errorWrite(f"hostnamectl: unknown operation '{action}'\n")

    def show_help(self) -> None:
        """Show hostnamectl help"""
        self.write(
            """hostnamectl [OPTIONS...] COMMAND ...

Query or change system hostname.

  -h --help              Show this help
     --version           Show package version
     --no-ask-password   Do not prompt for password
  -H --host=[USER@]HOST  Operate on remote host
  -M --machine=CONTAINER Operate on local container
     --transient         Only set transient hostname
     --static            Only set static hostname
     --pretty            Only set pretty hostname

Commands:
  status                 Show current hostname settings
  set-hostname NAME      Set system hostname
  set-icon-name NAME     Set icon name for host
  set-chassis NAME       Set chassis type for host
  set-deployment NAME    Set deployment environment for host
  set-location NAME      Set location for host
"""
        )

    def show_version(self) -> None:
        """Show hostnamectl version"""
        self.write("systemd 229\n")

    def show_status(self) -> None:
        """Show hostname status"""
        hostname = self.protocol.hostname
        kernel_version = CowrieConfig.get(
            "shell", "kernel_version", fallback="3.2.0-4-amd64"
        )
        hardware = CowrieConfig.get("shell", "hardware_platform", fallback="x86_64")

        # Determine OS info
        # Most honeypots simulate Debian/Ubuntu
        os_name = "Debian GNU/Linux"
        os_version = "8 (jessie)"

        self.write(f"   Static hostname: {hostname}\n")
        self.write("         Icon name: computer-vm\n")
        self.write("           Chassis: vm\n")
        self.write(f"        Machine ID: {'a' * 32}\n")  # Fake machine ID
        self.write(f"           Boot ID: {'b' * 32}\n")  # Fake boot ID
        self.write("    Virtualization: kvm\n")
        self.write(f"  Operating System: {os_name} {os_version}\n")
        self.write(f"            Kernel: Linux {kernel_version}\n")
        self.write(f"      Architecture: {hardware}\n")

    def set_hostname(self, hostname: str) -> None:
        """Set hostname"""
        # Check root privileges
        if self.protocol.user.username != "root":
            self.errorWrite("Failed to set hostname: Access denied\n")
            return

        # Set the hostname
        self.protocol.hostname = hostname
        # Success - no output

    def set_icon_name(self, icon: str) -> None:
        """Set icon name"""
        # Check root privileges
        if self.protocol.user.username != "root":
            self.errorWrite("Failed to set icon name: Access denied\n")
            return
        # Success - no output

    def set_chassis(self, chassis: str) -> None:
        """Set chassis type"""
        # Check root privileges
        if self.protocol.user.username != "root":
            self.errorWrite("Failed to set chassis: Access denied\n")
            return

        # Validate chassis type
        valid_chassis = [
            "desktop",
            "laptop",
            "server",
            "tablet",
            "handset",
            "watch",
            "embedded",
            "vm",
            "container",
        ]
        if chassis not in valid_chassis:
            self.errorWrite(
                f"Failed to set chassis: Invalid chassis type '{chassis}'\n"
            )
            return
        # Success - no output


commands["/bin/hostnamectl"] = Command_hostnamectl
commands["/usr/bin/hostnamectl"] = Command_hostnamectl
commands["hostnamectl"] = Command_hostnamectl
