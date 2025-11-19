# Copyright (c) 2009-2014 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

"""
sed command - stream editor for filtering and transforming text
Commonly used in malware installation scripts
"""

from __future__ import annotations

import getopt
import re

from cowrie.shell.command import HoneyPotCommand

commands = {}


class Command_sed(HoneyPotCommand):
    """
    sed command - stream editor
    Frequently used by attackers in automated scripts for text manipulation
    """

    def call(self) -> None:
        """Execute sed command"""
        if not self.args:
            self.write("sed: no input files\n")
            return

        # Parse options
        in_place = False
        quiet = False
        expression = None
        script_file = None

        try:
            optlist, args = getopt.getopt(self.args, "nie:f:")
        except getopt.GetoptError as err:
            self.write(f"sed: {err}\n")
            return

        for opt, arg in optlist:
            if opt == "-n":
                quiet = True
            elif opt == "-i":
                in_place = True
            elif opt == "-e":
                expression = arg
            elif opt == "-f":
                script_file = arg

        # Handle case where expression is the first argument (no -e flag)
        if not expression and not script_file and args:
            expression = args[0]
            args = args[1:]

        if not expression and not script_file:
            self.write("sed: no expression specified\n")
            return

        # Handle script file
        if script_file:
            path = self.fs.resolve_path(script_file, self.protocol.cwd)
            if not self.fs.exists(path):
                self.write(f"sed: can't read {script_file}: No such file or directory\n")
                return
            try:
                contents = self.fs.getfile(path)
                if contents:
                    expression = contents[0].decode("utf-8") if isinstance(contents[0], bytes) else contents[0]
            except Exception:
                self.write(f"sed: error reading {script_file}\n")
                return

        # Get input files or stdin
        if args:
            # Process files
            for filename in args:
                path = self.fs.resolve_path(filename, self.protocol.cwd)

                if not self.fs.exists(path):
                    self.write(f"sed: can't read {filename}: No such file or directory\n")
                    continue

                if self.fs.isdir(path):
                    self.write(f"sed: read error on {filename}: Is a directory\n")
                    continue

                # Get file contents
                try:
                    contents = self.fs.getfile(path)
                    if contents:
                        text = contents[0].decode("utf-8") if isinstance(contents[0], bytes) else contents[0]
                        result = self.process_sed(expression, text, quiet)
                        if result is not None:
                            self.write(result)
                except Exception as e:
                    self.write(f"sed: error processing {filename}\n")
        else:
            # Process stdin
            if self.input_data:
                text = self.input_data.decode("utf-8") if isinstance(self.input_data, bytes) else self.input_data
                result = self.process_sed(expression, text, quiet)
                if result is not None:
                    self.write(result)

    def process_sed(self, expression: str, text: str, quiet: bool = False) -> str | None:
        """
        Process text with sed expression
        Implements basic sed commands commonly used by attackers
        """
        # Parse the expression - basic format: s/pattern/replacement/flags
        if expression.startswith("s/") or expression.startswith("s|") or expression.startswith("s#"):
            # Substitution command
            delimiter = expression[1]
            parts = expression[2:].split(delimiter)

            if len(parts) < 2:
                return text

            pattern = parts[0]
            replacement = parts[1] if len(parts) > 1 else ""
            flags = parts[2] if len(parts) > 2 else ""

            # Handle flags
            global_replace = "g" in flags
            ignore_case = "i" in flags

            # Apply regex substitution
            try:
                re_flags = re.IGNORECASE if ignore_case else 0
                if global_replace:
                    result = re.sub(pattern, replacement, text, flags=re_flags)
                else:
                    result = re.sub(pattern, replacement, text, count=1, flags=re_flags)
                return result + ("\n" if not result.endswith("\n") else "")
            except re.error:
                return text

        elif expression.startswith("d"):
            # Delete command
            return "" if not quiet else None

        elif expression.startswith("p"):
            # Print command
            return text + text if not quiet else text

        elif expression.startswith("/"):
            # Pattern match and print
            delimiter_end = expression.find("/", 1)
            if delimiter_end > 0:
                pattern = expression[1:delimiter_end]
                try:
                    lines = text.split("\n")
                    result_lines = [line for line in lines if re.search(pattern, line)]
                    return "\n".join(result_lines) + ("\n" if result_lines else "")
                except re.error:
                    return text

        # For other commands or unrecognized syntax, just return original text
        return text if not quiet else ""


commands["/bin/sed"] = Command_sed
commands["sed"] = Command_sed
