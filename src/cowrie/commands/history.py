# Copyright (c) 2009-2014 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

"""
history command - display command history
Used by attackers for reconnaissance to see what commands have been run
"""

from __future__ import annotations

import getopt

from cowrie.shell.command import HoneyPotCommand

commands = {}


class Command_history(HoneyPotCommand):
    """
    history command - display the command history list
    Used by attackers to discover what commands have been executed
    """

    def call(self) -> None:
        """Execute history command"""
        # Parse options
        clear_history = False
        delete_offset = None
        num_lines = None

        try:
            optlist, args = getopt.getopt(self.args, "cd:n:")
        except getopt.GetoptError:
            # Bash history doesn't error on invalid options, just ignores them
            pass
        else:
            for opt, arg in optlist:
                if opt == "-c":
                    clear_history = True
                elif opt == "-d":
                    try:
                        delete_offset = int(arg)
                    except ValueError:
                        self.write(f"bash: history: {arg}: numeric argument required\n")
                        return
                elif opt == "-n":
                    try:
                        num_lines = int(arg)
                    except ValueError:
                        self.write(f"bash: history: {arg}: numeric argument required\n")
                        return

        # Handle clear
        if clear_history:
            # In a real honeypot, we don't want to actually clear history
            # Just pretend we did
            return

        # Handle delete
        if delete_offset is not None:
            # Pretend to delete the entry
            return

        # Get history from protocol
        history_lines = []

        # Check if we have access to historyLines (available in interactive protocol)
        if hasattr(self.protocol, "historyLines"):
            history_lines = self.protocol.historyLines
        else:
            # If not available, provide some fake history that looks realistic
            history_lines = [
                b"ls -la",
                b"whoami",
                b"uname -a",
                b"cat /etc/passwd",
                b"ps aux",
                b"netstat -tulpn",
                b"history",
            ]

        # Determine how many lines to show
        if num_lines:
            history_lines = history_lines[-num_lines:]

        # Display history with line numbers
        # Start numbering from 1
        start_num = 1
        if len(history_lines) > 500:
            # If we have lots of history, start numbering from current position
            start_num = len(history_lines) - 500 + 1
            history_lines = history_lines[-500:]

        for i, line in enumerate(history_lines, start=start_num):
            # Format: "  NUM  COMMAND"
            try:
                line_str = line.decode("utf-8") if isinstance(line, bytes) else line
                self.write(f"  {i:4}  {line_str}\n")
            except (UnicodeDecodeError, AttributeError):
                # Skip lines that can't be decoded
                pass


commands["history"] = Command_history
