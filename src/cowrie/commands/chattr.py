# Copyright (c) 2009-2014 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

"""
chattr command - change file attributes on a Linux file system
Commonly used by cryptominers to make malware files immutable
"""

from __future__ import annotations

import getopt

from cowrie.shell.command import HoneyPotCommand

commands = {}


class Command_chattr(HoneyPotCommand):
    """
    chattr command - used to change file attributes
    Commonly used by attackers to make files immutable (+i flag)
    """

    def call(self) -> None:
        """Execute chattr command"""
        if not self.args:
            self.write("Usage: chattr [-RVf] [-+=AacDdeijsSu] [-v version] files...\n")
            return

        # Manually parse arguments since chattr uses non-getopt style modes like "+i"
        recursive = False
        verbose = False
        operation = None
        attributes = []
        files = []
        skip_next = False

        for i, arg in enumerate(self.args):
            if skip_next:
                skip_next = False
                continue

            # Handle getopt-style options
            if arg == "-R":
                recursive = True
            elif arg == "-V":
                verbose = True
            elif arg == "-f":
                pass  # Force, suppress most error messages
            elif arg == "-v":
                # Next argument is version number, skip it
                skip_next = True
            # Handle mode specifiers like +i, -a, =aAcCdDeijsStTu
            elif arg.startswith(("+", "=")) and len(arg) > 1:
                # Mode specifications starting with + or =
                operation = arg[0]
                attributes.append(arg[1:])
            elif arg.startswith("-") and len(arg) > 1 and arg[1].isalpha():
                # Mode specification starting with - (but not option like -R)
                # e.g., -i for removing immutable attribute
                operation = arg[0]
                attributes.append(arg[1:])
            else:
                # It's a filename
                files.append(arg)

        if not files:
            self.write("Usage: chattr [-RVf] [-+=AacDdeijsSu] [-v version] files...\n")
            return

        # Process each file
        for filename in files:
            path = self.fs.resolve_path(filename, self.protocol.cwd)

            # Check if file exists
            if not self.fs.exists(path):
                self.write(f"chattr: No such file or directory while trying to stat {filename}\n")
                continue

            # Check if it's a directory and -R is not specified
            is_dir = self.fs.isdir(path)
            if is_dir and not recursive:
                # For directories without -R, just succeed silently
                if verbose:
                    # Get current attributes (simulate)
                    self.write(f"Flags of {filename} set as -------------e--\n")
                continue

            # Simulate success
            if verbose:
                attr_str = "-------------e--"  # Default ext4 attributes
                if "i" in "".join(attributes) and operation == "+":
                    attr_str = "----i--------e--"
                elif "a" in "".join(attributes) and operation == "+":
                    attr_str = "-----a-------e--"
                self.write(f"Flags of {filename} set as {attr_str}\n")

        # Attackers commonly use: chattr +i <file> to make files immutable
        # This prevents deletion or modification, used for persistence


commands["/usr/bin/chattr"] = Command_chattr
commands["chattr"] = Command_chattr
