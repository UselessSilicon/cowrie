# Copyright (c) 2009-2014 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

"""
systemctl command - systemd service manager
"""

from __future__ import annotations

import random

from cowrie.shell.command import HoneyPotCommand

commands = {}

# Realistic systemd units that would exist on a Debian/Ubuntu system
SYSTEMD_UNITS = {
    "sshd.service": {
        "loaded": "loaded",
        "active": "active",
        "sub": "running",
        "description": "OpenSSH server daemon",
    },
    "ssh.service": {
        "loaded": "loaded",
        "active": "active",
        "sub": "running",
        "description": "OpenSSH Daemon",
    },
    "cron.service": {
        "loaded": "loaded",
        "active": "active",
        "sub": "running",
        "description": "Regular background program processing daemon",
    },
    "networking.service": {
        "loaded": "loaded",
        "active": "active",
        "sub": "exited",
        "description": "Raise network interfaces",
    },
    "systemd-journald.service": {
        "loaded": "loaded",
        "active": "active",
        "sub": "running",
        "description": "Journal Service",
    },
    "systemd-logind.service": {
        "loaded": "loaded",
        "active": "active",
        "sub": "running",
        "description": "Login Service",
    },
    "systemd-udevd.service": {
        "loaded": "loaded",
        "active": "active",
        "sub": "running",
        "description": "udev Kernel Device Manager",
    },
    "dbus.service": {
        "loaded": "loaded",
        "active": "active",
        "sub": "running",
        "description": "D-Bus System Message Bus",
    },
    "rsyslog.service": {
        "loaded": "loaded",
        "active": "active",
        "sub": "running",
        "description": "System Logging Service",
    },
    "apache2.service": {
        "loaded": "not-found",
        "active": "inactive",
        "sub": "dead",
        "description": "The Apache HTTP Server",
    },
    "nginx.service": {
        "loaded": "not-found",
        "active": "inactive",
        "sub": "dead",
        "description": "A high performance web server",
    },
    "mysql.service": {
        "loaded": "not-found",
        "active": "inactive",
        "sub": "dead",
        "description": "MySQL Community Server",
    },
}


class Command_systemctl(HoneyPotCommand):
    """
    systemctl command - Control the systemd system and service manager
    """

    def call(self) -> None:
        if not self.args:
            # No args = list-units
            self.list_units()
            return

        action = self.args[0]

        # Handle help and version
        if action in ("--help", "-h"):
            self.show_help()
            return
        elif action == "--version":
            self.show_version()
            return

        # Handle different actions
        if action == "list-units":
            self.list_units()
        elif action == "list-unit-files":
            self.list_unit_files()
        elif action == "status":
            service = self.args[1] if len(self.args) > 1 else None
            self.show_status(service)
        elif action in ("start", "stop", "restart", "reload"):
            if len(self.args) < 2:
                self.write(f"systemctl {action}: missing service name\n")
                return
            self.service_action(action, self.args[1])
        elif action in ("enable", "disable"):
            if len(self.args) < 2:
                self.write(f"systemctl {action}: missing service name\n")
                return
            self.service_enable_disable(action, self.args[1])
        elif action == "is-active":
            if len(self.args) < 2:
                self.write("systemctl is-active: missing service name\n")
                return
            self.is_active(self.args[1])
        elif action == "is-enabled":
            if len(self.args) < 2:
                self.write("systemctl is-enabled: missing service name\n")
                return
            self.is_enabled(self.args[1])
        elif action == "daemon-reload":
            # Daemon reload always requires root
            if self.protocol.user.username != "root":
                self.write("Failed to reload daemon: Access denied\n")
            # Otherwise succeed silently
        else:
            self.write(f"Unknown operation '{action}'.\n")

    def show_help(self) -> None:
        """Show systemctl help"""
        self.write(
            """systemctl [OPTIONS...] COMMAND ...

Query or send control commands to the systemd manager.

Unit Commands:
  list-units [PATTERN...]         List units currently in memory
  list-sockets [PATTERN...]       List socket units currently in memory
  list-timers [PATTERN...]        List timer units currently in memory
  start NAME...                   Start (activate) one or more units
  stop NAME...                    Stop (deactivate) one or more units
  reload NAME...                  Reload one or more units
  restart NAME...                 Start or restart one or more units
  try-restart NAME...             Restart one or more units if active
  reload-or-restart NAME...       Reload one or more units if possible,
                                  otherwise start or restart
  isolate NAME                    Start one unit and stop all others
  kill NAME...                    Send signal to processes of a unit
  is-active PATTERN...            Check whether units are active
  is-failed PATTERN...            Check whether units are failed
  status [PATTERN...|PID...]      Show runtime status of one or more units
  show [PATTERN...|JOB...]        Show properties of one or more units/jobs

Unit File Commands:
  list-unit-files [PATTERN...]    List installed unit files
  enable NAME...                  Enable one or more unit files
  disable NAME...                 Disable one or more unit files
  reenable NAME...                Reenable one or more unit files
  preset NAME...                  Enable/disable one or more unit files
  is-enabled NAME...              Check whether unit files are enabled
  mask NAME...                    Mask one or more units
  unmask NAME...                  Unmask one or more units
  daemon-reload                   Reload systemd manager configuration

Options:
  -h --help           Show this help
     --version        Show package version
  -t --type=TYPE      List units of a particular type
     --state=STATE    List units with particular LOAD or SUB or ACTIVE state
  -p --property=NAME  Show only properties by this name
  -a --all            Show all loaded units/properties
  -l --full           Don't ellipsize unit names on output
     --no-pager       Do not pipe output into a pager
"""
        )

    def show_version(self) -> None:
        """Show systemctl version"""
        self.write("systemd 229\n")
        self.write(
            "+PAM +AUDIT +SELINUX +IMA +APPARMOR +SMACK +SYSVINIT +UTMP +LIBCRYPTSETUP +GCRYPT +GNUTLS +ACL +XZ -LZ4 +SECCOMP +BLKID +ELFUTILS +KMOD -IDN\n"
        )

    def list_units(self) -> None:
        """List active units"""
        self.write(
            "UNIT                           LOAD   ACTIVE SUB       DESCRIPTION\n"
        )

        for unit, info in SYSTEMD_UNITS.items():
            if info["active"] == "active":
                self.write(
                    f"{unit:30s} {info['loaded']:6s} {info['active']:6s} "
                    f"{info['sub']:9s} {info['description']}\n"
                )

        self.write(
            "\nLOAD   = Reflects whether the unit definition was properly loaded.\n"
        )
        self.write(
            "ACTIVE = The high-level unit activation state, i.e. generalization of SUB.\n"
        )
        self.write(
            "SUB    = The low-level unit activation state, values depend on unit type.\n"
        )
        self.write(
            f"\n{sum(1 for u in SYSTEMD_UNITS.values() if u['active'] == 'active')} loaded units listed.\n"
        )

    def list_unit_files(self) -> None:
        """List unit files"""
        self.write("UNIT FILE                              STATE\n")

        for unit in SYSTEMD_UNITS:
            if SYSTEMD_UNITS[unit]["loaded"] == "loaded":
                state = (
                    "enabled"
                    if SYSTEMD_UNITS[unit]["active"] == "active"
                    else "disabled"
                )
                self.write(f"{unit:38s} {state}\n")

        self.write(
            f"\n{len([u for u in SYSTEMD_UNITS if SYSTEMD_UNITS[u]['loaded'] == 'loaded'])} unit files listed.\n"
        )

    def show_status(self, service: str | None) -> None:
        """Show service status"""
        if not service:
            # Show system status
            self.write(f"● {self.protocol.hostname}\n")
            self.write("    State: running\n")
            self.write("     Jobs: 0 queued\n")
            self.write("   Failed: 0 units\n")
            return

        # Normalize service name (add .service if not present)
        if not service.endswith(".service"):
            service = f"{service}.service"

        if service not in SYSTEMD_UNITS:
            self.write(f"Unit {service} could not be found.\n")
            return

        info = SYSTEMD_UNITS[service]

        if info["loaded"] == "not-found":
            self.write(f"Unit {service} could not be found.\n")
            return

        # Show detailed status
        active_str = "active" if info["active"] == "active" else "inactive"
        color_code = "●" if info["active"] == "active" else "○"

        self.write(f"{color_code} {service} - {info['description']}\n")
        self.write(
            f"   Loaded: {info['loaded']} (/lib/systemd/system/{service}; enabled; vendor preset: enabled)\n"
        )
        self.write(
            f"   Active: {active_str} ({info['sub']}) since Mon 2025-11-19 12:00:00 UTC; 1h ago\n"
        )

        if info["active"] == "active":
            pid = random.randint(500, 2000)
            self.write(f" Main PID: {pid} ({service.replace('.service', '')})\n")
            self.write(f"    Tasks: {random.randint(1, 3)}\n")
            self.write(f"   Memory: {random.uniform(1.0, 10.0):.1f}M\n")
            self.write(f"   CGroup: /system.slice/{service}\n")
            self.write(
                f"           └─{pid} /usr/sbin/{service.replace('.service', '')}\n"
            )

    def service_action(self, action: str, service: str) -> None:
        """Handle start/stop/restart/reload"""
        # Check root privileges
        if self.protocol.user.username != "root":
            self.write(f"Failed to {action} {service}: Access denied\n")
            return

        # Normalize service name
        if not service.endswith(".service"):
            service = f"{service}.service"

        if service not in SYSTEMD_UNITS:
            self.write(
                f"Failed to {action} {service}: Unit {service} not found.\n"
            )
            return

        # Pretend to succeed (no output on success)
        pass

    def service_enable_disable(self, action: str, service: str) -> None:
        """Handle enable/disable"""
        # Check root privileges
        if self.protocol.user.username != "root":
            self.write(f"Failed to {action} unit: Access denied\n")
            return

        # Normalize service name
        if not service.endswith(".service"):
            service = f"{service}.service"

        if service not in SYSTEMD_UNITS:
            self.write(
                f"Failed to {action} unit: Unit file {service} does not exist.\n"
            )
            return

        if action == "enable":
            self.write(
                f"Created symlink /etc/systemd/system/multi-user.target.wants/{service} → /lib/systemd/system/{service}.\n"
            )
        else:
            self.write(
                f"Removed /etc/systemd/system/multi-user.target.wants/{service}.\n"
            )

    def is_active(self, service: str) -> None:
        """Check if service is active"""
        # Normalize service name
        if not service.endswith(".service"):
            service = f"{service}.service"

        if service in SYSTEMD_UNITS and SYSTEMD_UNITS[service]["active"] == "active":
            self.write("active\n")
        else:
            self.write("inactive\n")

    def is_enabled(self, service: str) -> None:
        """Check if service is enabled"""
        # Normalize service name
        if not service.endswith(".service"):
            service = f"{service}.service"

        if service in SYSTEMD_UNITS and SYSTEMD_UNITS[service]["loaded"] == "loaded":
            self.write("enabled\n")
        else:
            self.write("disabled\n")


commands["/bin/systemctl"] = Command_systemctl
commands["/usr/bin/systemctl"] = Command_systemctl
commands["systemctl"] = Command_systemctl
