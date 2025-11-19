# Copyright (c) 2009-2014 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

"""
journalctl command - Query the systemd journal
"""

from __future__ import annotations

import random
import time

from cowrie.shell.command import HoneyPotCommand

commands = {}

# Realistic journal entries that would appear on a Linux system
JOURNAL_ENTRIES = [
    {
        "timestamp": "Nov 19 12:00:01",
        "hostname": "localhost",
        "process": "systemd[1]",
        "message": "Started Session 1 of user root.",
    },
    {
        "timestamp": "Nov 19 12:00:15",
        "hostname": "localhost",
        "process": "sshd[891]",
        "message": "Server listening on 0.0.0.0 port 22.",
    },
    {
        "timestamp": "Nov 19 12:00:15",
        "hostname": "localhost",
        "process": "sshd[891]",
        "message": "Server listening on :: port 22.",
    },
    {
        "timestamp": "Nov 19 12:01:01",
        "hostname": "localhost",
        "process": "CRON[1523]",
        "message": "pam_unix(cron:session): session opened for user root by (uid=0)",
    },
    {
        "timestamp": "Nov 19 12:01:01",
        "hostname": "localhost",
        "process": "CRON[1524]",
        "message": "(root) CMD (   cd / && run-parts --report /etc/cron.hourly)",
    },
    {
        "timestamp": "Nov 19 12:01:01",
        "hostname": "localhost",
        "process": "CRON[1523]",
        "message": "pam_unix(cron:session): session closed for user root",
    },
    {
        "timestamp": "Nov 19 12:15:22",
        "hostname": "localhost",
        "process": "systemd[1]",
        "message": "Starting Daily apt download activities...",
    },
    {
        "timestamp": "Nov 19 12:15:23",
        "hostname": "localhost",
        "process": "systemd[1]",
        "message": "Started Daily apt download activities.",
    },
    {
        "timestamp": "Nov 19 12:30:01",
        "hostname": "localhost",
        "process": "systemd-logind[456]",
        "message": "New session 2 of user root.",
    },
]


class Command_journalctl(HoneyPotCommand):
    """
    journalctl command - Query the systemd journal
    """

    def call(self) -> None:
        follow = False
        lines = 10
        unit = None
        show_kernel = False
        reverse = False

        # Parse arguments
        i = 0
        while i < len(self.args):
            arg = self.args[i]

            if arg in ("-h", "--help"):
                self.show_help()
                return
            elif arg == "--version":
                self.show_version()
                return
            elif arg in ("-f", "--follow"):
                follow = True
            elif arg in ("-n", "--lines"):
                if i + 1 < len(self.args):
                    try:
                        lines = int(self.args[i + 1])
                        i += 1
                    except ValueError:
                        self.errorWrite(
                            f"journalctl: invalid line count: {self.args[i + 1]}\n"
                        )
                        return
            elif arg.startswith("-n"):
                # Handle -n10 format
                try:
                    lines = int(arg[2:])
                except ValueError:
                    self.errorWrite(f"journalctl: invalid line count: {arg[2:]}\n")
                    return
            elif arg in ("-u", "--unit"):
                if i + 1 < len(self.args):
                    unit = self.args[i + 1]
                    i += 1
                else:
                    self.errorWrite("journalctl: option requires an argument -- 'u'\n")
                    return
            elif arg == "--since":
                if i + 1 < len(self.args):
                    # Consume the argument but don't use it in this simple implementation
                    i += 1
                else:
                    self.errorWrite(
                        "journalctl: option requires an argument -- 'since'\n"
                    )
                    return
            elif arg in ("-k", "--dmesg"):
                show_kernel = True
            elif arg in ("-b", "--boot"):
                # Show logs from current boot (default behavior)
                pass
            elif arg in ("-r", "--reverse"):
                reverse = True
            elif arg == "--no-pager":
                # Consume but don't use in this implementation
                pass
            elif arg in ("-o", "--output"):
                if i + 1 < len(self.args):
                    # Consume the argument but don't use it in this simple implementation
                    i += 1
            elif arg in ("-x", "--catalog"):
                # Add explanatory help texts (we ignore this)
                pass
            elif arg in ("-e", "--pager-end"):
                # Jump to end (we show recent logs anyway)
                pass
            elif arg == "-xe":
                # Common combination: catalog + pager-end
                pass

            i += 1

        # Show journal entries
        if follow:
            self.write("-- Logs begin at Mon 2025-11-19 12:00:00 UTC. --\n")
            self.write("(Following mode - press Ctrl+C to exit)\n")
            # In a real implementation, this would continuously show new logs
            # For honeypot purposes, we just show a few entries and wait
            self.show_entries(lines, unit, show_kernel, reverse)
            # Don't exit - simulate continuous following
            # (The command will be interrupted by Ctrl+C)
        else:
            self.write("-- Logs begin at Mon 2025-11-19 12:00:00 UTC. --\n")
            self.show_entries(lines, unit, show_kernel, reverse)

    def show_help(self) -> None:
        """Show journalctl help"""
        self.write(
            """journalctl [OPTIONS...] [MATCHES...]

Query the journal.

Flags:
     --system              Show the system journal
     --user                Show the user journal for the current user
  -M --machine=CONTAINER   Operate on local container
  -S --since=DATE          Show entries not older than the specified date
  -U --until=DATE          Show entries not newer than the specified date
  -c --cursor=CURSOR       Show entries starting at the specified cursor
     --after-cursor=CURSOR Show entries after the specified cursor
     --show-cursor         Print the cursor after all the entries
  -b --boot[=ID]           Show current boot or the specified boot
     --list-boots          Show terse information about recorded boots
  -k --dmesg               Show kernel message log from the current boot
  -u --unit=UNIT           Show logs from the specified unit
     --user-unit=UNIT      Show logs from the specified user unit
  -t --identifier=STRING   Show entries with the specified syslog identifier
  -p --priority=RANGE      Show entries with the specified priority
  -e --pager-end           Immediately jump to the end in the pager
  -f --follow              Follow the journal
  -n --lines[=INTEGER]     Number of journal entries to show
     --no-tail             Show all lines, even in follow mode
  -r --reverse             Show the newest entries first
  -o --output=STRING       Change journal output mode (short, json, cat, etc.)
     --utc                 Express time in Coordinated Universal Time (UTC)
  -x --catalog             Add message explanations where available
     --no-full             Ellipsize fields
  -a --all                 Show all fields, including long and unprintable
  -q --quiet               Do not show privilege warning
     --no-pager            Do not pipe output into a pager
  -m --merge               Show entries from all available journals
  -D --directory=PATH      Show journal files from directory
     --file=PATH           Show journal file
     --root=ROOT           Operate on catalog hierarchy under ROOT
     --interval=TIME       Time interval for changing the FSS sealing key
     --verify-key=KEY      Specify FSS verification key

Commands:
  -h --help                Show this help text
     --version             Show package version
  -F --field=FIELD         List all values that a specified field takes
     --new-id128           Generate a new 128-bit ID
     --disk-usage          Show total disk usage of all journal files
     --vacuum-size=BYTES   Reduce disk usage below specified size
     --vacuum-time=TIME    Remove journal files older than specified date
     --flush               Flush all journal data from /run into /var
     --header              Show journal header information
     --list-catalog        Show all message IDs in the catalog
     --dump-catalog        Show entries in the message catalog
     --update-catalog      Update the message catalog database
"""
        )

    def show_version(self) -> None:
        """Show journalctl version"""
        self.write("systemd 229\n")
        self.write("+PAM +AUDIT +SELINUX +IMA +APPARMOR +SMACK +SYSVINIT +UTMP\n")

    def show_entries(
        self, lines: int, unit: str | None, show_kernel: bool, reverse: bool
    ) -> None:
        """Show journal entries"""
        entries = []

        # Generate some dynamic entries with current connection info
        current_time = time.strftime("%b %d %H:%M:%S")
        hostname = self.protocol.hostname
        username = self.protocol.user.username
        client_ip = self.protocol.clientIP

        # Add current session login
        ssh_pid = random.randint(1000, 9999)
        entries.append(
            {
                "timestamp": current_time,
                "hostname": hostname,
                "process": f"sshd[{ssh_pid}]",
                "message": f"Accepted password for {username} from {client_ip} port {self.protocol.realClientPort} ssh2",
            }
        )

        entries.append(
            {
                "timestamp": current_time,
                "hostname": hostname,
                "process": f"sshd[{ssh_pid}]",
                "message": f"pam_unix(sshd:session): session opened for user {username} by (uid=0)",
            }
        )

        # Add static journal entries
        entries.extend(JOURNAL_ENTRIES)

        # Filter by unit if specified
        if unit:
            # Normalize unit name
            if not unit.endswith(".service"):
                unit = f"{unit}.service"

            entries = [
                e
                for e in entries
                if unit.replace(".service", "") in e["process"].lower()
            ]

        # Show kernel logs if requested
        if show_kernel:
            entries = [
                {
                    "timestamp": "Nov 19 12:00:00",
                    "hostname": hostname,
                    "process": "kernel",
                    "message": "[    0.000000] Linux version 4.15.0-20-generic (buildd@lcy01-amd64-029)",
                },
                {
                    "timestamp": "Nov 19 12:00:00",
                    "hostname": hostname,
                    "process": "kernel",
                    "message": "[    0.000000] Command line: BOOT_IMAGE=/boot/vmlinuz-4.15.0-20-generic root=UUID=1234-5678 ro quiet splash",
                },
            ]

        # Reverse if requested
        if reverse:
            entries = list(reversed(entries))

        # Limit number of lines
        entries = entries[:lines]

        # Display entries
        for entry in entries:
            self.write(
                f"{entry['timestamp']} {entry['hostname']} {entry['process']}: {entry['message']}\n"
            )


commands["/bin/journalctl"] = Command_journalctl
commands["/usr/bin/journalctl"] = Command_journalctl
commands["journalctl"] = Command_journalctl
