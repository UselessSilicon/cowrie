# Copyright (c) 2009-2014 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

"""
watch command - execute a program periodically, showing output fullscreen
"""

from __future__ import annotations

from cowrie.shell.command import HoneyPotCommand

commands = {}


class Command_watch(HoneyPotCommand):
    """
    watch command - execute a program periodically and show output
    """

    def call(self) -> None:
        interval = 2.0
        command_args = []

        # Parse arguments
        i = 0
        while i < len(self.args):
            arg = self.args[i]

            if arg in ("-h", "--help"):
                self.show_help()
                return
            elif arg in ("-v", "--version"):
                self.show_version()
                return
            elif arg in ("-n", "--interval"):
                if i + 1 < len(self.args):
                    try:
                        interval = float(self.args[i + 1])
                        i += 1
                    except ValueError:
                        self.write(
                            f"watch: invalid interval '{self.args[i + 1]}'\n"
                        )
                        return
                else:
                    self.write("watch: option requires an argument -- 'n'\n")
                    return
            elif arg in ("-d", "--differences"):
                # Highlight differences - we'll ignore this in our simple implementation
                pass
            elif arg in ("-p", "--precise"):
                # Precise timing - we'll ignore this in our simple implementation
                pass
            elif arg in ("-t", "--no-title"):
                # We don't show title anyway in this simple implementation
                pass
            elif arg in ("-b", "--beep"):
                # Beep on error - we'll ignore this
                pass
            elif arg in ("-e", "--errexit"):
                # Exit on error - we'll ignore this
                pass
            elif arg in ("-g", "--chgexit"):
                # Exit on change - we'll ignore this
                pass
            elif arg in ("-c", "--color"):
                # Interpret ANSI color - we'll ignore this
                pass
            elif arg in ("-x", "--exec"):
                # Pass command to exec instead of sh -c
                # All remaining args are the command
                command_args = self.args[i + 1 :]
                break
            else:
                # Everything else is the command
                command_args = self.args[i:]
                break

            i += 1

        if not command_args:
            self.write("watch: no command specified\n")
            self.write("Try 'watch --help' for more information.\n")
            return

        # In a real watch command, this would repeatedly execute the command
        # For the honeypot, we'll simulate it by showing a message
        command_str = " ".join(command_args)

        self.write(f"\nEvery {interval}s: {command_str}\n\n")
        self.write("(watch command running - press Ctrl+C to exit)\n")
        self.write(f"Command to monitor: {command_str}\n")
        self.write(
            "\nNote: In this honeypot environment, watch command simulation is limited.\n"
        )
        self.write(
            f"The command would normally refresh every {interval:.1f} seconds.\n"
        )

        # Don't actually execute the command repeatedly - just simulate
        # The attacker would press Ctrl+C to exit

    def show_help(self) -> None:
        """Show watch help"""
        self.write(
            """Usage:
 watch [options] command

Options:
  -b, --beep             beep if command has a non-zero exit
  -c, --color            interpret ANSI color and style sequences
  -d, --differences[=<permanent>]
                         highlight changes between updates
  -e, --errexit          exit if command has a non-zero exit
  -g, --chgexit          exit when output from command changes
  -n, --interval <secs>  seconds to wait between updates
  -p, --precise          attempt run command in precise intervals
  -t, --no-title         turn off header
  -x, --exec             pass command to exec instead of "sh -c"

 -h, --help     display this help and exit
 -v, --version  output version information and exit

For more details see watch(1).
"""
        )

    def show_version(self) -> None:
        """Show watch version"""
        self.write("watch from procps-ng 3.3.10\n")


commands["/usr/bin/watch"] = Command_watch
commands["watch"] = Command_watch
