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

        try:
            # Parse options
            optlist, args = getopt.getopt(self.args, "RVfv:+=AacDdeijsSu")
        except getopt.GetoptError as err:
            self.write(f"chattr: {err}\n")
            return

        if not args:
            self.write("Usage: chattr [-RVf] [-+=AacDdeijsSu] [-v version] files...\n")
            return

        # Extract operation and attributes
        operation = None
        attributes = []
        recursive = False
        verbose = False

        for opt, arg in optlist:
            if opt == "-R":
                recursive = True
            elif opt == "-V":
                verbose = True
            elif opt == "-f":
                pass  # Force, suppress most error messages
            elif opt == "-v":
                pass  # Version number, ignored
            else:
                # Attribute operations (+, -, =, followed by attribute letters)
                if opt.startswith(("+", "-", "=")):
                    operation = opt[0]
                    attributes.append(opt[1:])

        # Process each file
        for filename in args:
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
