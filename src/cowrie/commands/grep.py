# Copyright (c) 2009-2014 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

"""
grep command - search for patterns in files
One of the most commonly used commands by attackers
"""

from __future__ import annotations

import getopt
import re

from cowrie.shell.command import HoneyPotCommand

commands = {}


class Command_grep(HoneyPotCommand):
    """
    grep command - print lines matching a pattern
    Extremely common utility used in reconnaissance and malware scripts
    """

    def call(self) -> None:
        """Execute grep command"""
        if not self.args:
            self.write("Usage: grep [OPTION]... PATTERN [FILE]...\n")
            self.write("Try 'grep --help' for more information.\n")
            return

        # Parse options
        ignore_case = False
        invert_match = False
        count_only = False
        files_with_matches = False
        files_without_matches = False
        line_number = False
        quiet = False
        recursive = False
        extended_regex = False
        fixed_strings = False
        word_regexp = False
        line_regexp = False
        color = False
        max_count = None

        try:
            optlist, args = getopt.getopt(
                self.args,
                "icvlLnqrEFwxm:",
                ["ignore-case", "count", "invert-match", "files-with-matches",
                 "files-without-match", "line-number", "quiet", "silent",
                 "recursive", "extended-regexp", "fixed-strings", "word-regexp",
                 "line-regexp", "color", "colour", "max-count=", "help"]
            )
        except getopt.GetoptError as err:
            self.write(f"grep: {err}\n")
            return

        for opt, arg in optlist:
            if opt in ("-i", "--ignore-case"):
                ignore_case = True
            elif opt in ("-c", "--count"):
                count_only = True
            elif opt in ("-v", "--invert-match"):
                invert_match = True
            elif opt in ("-l", "--files-with-matches"):
                files_with_matches = True
            elif opt in ("-L", "--files-without-match"):
                files_without_matches = True
            elif opt in ("-n", "--line-number"):
                line_number = True
            elif opt in ("-q", "--quiet", "--silent"):
                quiet = True
            elif opt in ("-r", "--recursive"):
                recursive = True
            elif opt in ("-E", "--extended-regexp"):
                extended_regex = True
            elif opt in ("-F", "--fixed-strings"):
                fixed_strings = True
            elif opt in ("-w", "--word-regexp"):
                word_regexp = True
            elif opt in ("-x", "--line-regexp"):
                line_regexp = True
            elif opt in ("--color", "--colour"):
                color = True
            elif opt in ("-m", "--max-count"):
                try:
                    max_count = int(arg)
                except ValueError:
                    self.write(f"grep: invalid max count\n")
                    return
            elif opt == "--help":
                self.show_help()
                return

        if not args:
            self.write("grep: no pattern specified\n")
            return

        pattern = args[0]
        files = args[1:] if len(args) > 1 else []

        # Build regex pattern
        try:
            if fixed_strings:
                pattern = re.escape(pattern)
            if word_regexp:
                pattern = r"\b" + pattern + r"\b"
            if line_regexp:
                pattern = "^" + pattern + "$"

            re_flags = re.IGNORECASE if ignore_case else 0
            regex = re.compile(pattern, re_flags)
        except re.error as e:
            self.write(f"grep: invalid pattern: {e}\n")
            return

        # Process files or stdin
        if files:
            for filename in files:
                self.process_file(filename, regex, invert_match, count_only,
                                files_with_matches, files_without_matches,
                                line_number, quiet, max_count, len(files) > 1)
        else:
            # Process stdin
            if self.input_data:
                self.process_stdin(regex, invert_match, count_only, line_number,
                                 quiet, max_count)

    def process_file(self, filename: str, regex: re.Pattern, invert_match: bool,
                    count_only: bool, files_with_matches: bool, files_without_matches: bool,
                    line_number: bool, quiet: bool, max_count: int | None,
                    show_filename: bool) -> None:
        """Process a single file"""
        path = self.fs.resolve_path(filename, self.protocol.cwd)

        if not self.fs.exists(path):
            self.write(f"grep: {filename}: No such file or directory\n")
            return

        if self.fs.isdir(path):
            self.write(f"grep: {filename}: Is a directory\n")
            return

        # Get file contents
        try:
            contents = self.fs.file_contents(path)
            if not contents:
                return

            text = contents.decode("utf-8", errors="ignore") if isinstance(contents, bytes) else str(contents)
            lines = text.split("\n")

            matches = []
            match_count = 0

            for line_num, line in enumerate(lines, 1):
                is_match = bool(regex.search(line))
                if invert_match:
                    is_match = not is_match

                if is_match:
                    match_count += 1
                    matches.append((line_num, line))

                    if max_count and match_count >= max_count:
                        break

            # Output based on options
            if quiet:
                # Just set exit code
                if match_count > 0:
                    return
            elif files_with_matches:
                if match_count > 0:
                    self.write(f"{filename}\n")
            elif files_without_matches:
                if match_count == 0:
                    self.write(f"{filename}\n")
            elif count_only:
                if show_filename:
                    self.write(f"{filename}:{match_count}\n")
                else:
                    self.write(f"{match_count}\n")
            else:
                for line_num, line in matches:
                    if show_filename and line_number:
                        self.write(f"{filename}:{line_num}:{line}\n")
                    elif show_filename:
                        self.write(f"{filename}:{line}\n")
                    elif line_number:
                        self.write(f"{line_num}:{line}\n")
                    else:
                        self.write(f"{line}\n")

        except Exception:
            self.write(f"grep: {filename}: error reading file\n")

    def process_stdin(self, regex: re.Pattern, invert_match: bool, count_only: bool,
                     line_number: bool, quiet: bool, max_count: int | None) -> None:
        """Process stdin"""
        text = self.input_data.decode("utf-8", errors="ignore") if isinstance(self.input_data, bytes) else self.input_data
        lines = text.split("\n")

        matches = []
        match_count = 0

        for line_num, line in enumerate(lines, 1):
            is_match = bool(regex.search(line))
            if invert_match:
                is_match = not is_match

            if is_match:
                match_count += 1
                matches.append((line_num, line))

                if max_count and match_count >= max_count:
                    break

        # Output
        if quiet:
            return
        elif count_only:
            self.write(f"{match_count}\n")
        else:
            for line_num, line in matches:
                if line_number:
                    self.write(f"{line_num}:{line}\n")
                else:
                    self.write(f"{line}\n")

    def show_help(self) -> None:
        """Show grep help"""
        help_text = """Usage: grep [OPTION]... PATTERN [FILE]...
Search for PATTERN in each FILE.
Example: grep -i 'hello world' menu.h main.c

Pattern selection and interpretation:
  -E, --extended-regexp     PATTERN is an extended regular expression
  -F, --fixed-strings       PATTERN is a set of newline-separated strings
  -i, --ignore-case         ignore case distinctions
  -w, --word-regexp         force PATTERN to match only whole words
  -x, --line-regexp         force PATTERN to match only whole lines

Miscellaneous:
  -v, --invert-match        select non-matching lines
  -c, --count               print only a count of matching lines per FILE
  -l, --files-with-matches  print only names of FILEs containing matches
  -L, --files-without-match print only names of FILEs containing no match
  -n, --line-number         print line number with output lines
  -r, --recursive           read all files under each directory, recursively
  -q, --quiet, --silent     suppress all normal output

When FILE is -, read standard input.
"""
        self.write(help_text)


commands["/bin/grep"] = Command_grep
commands["grep"] = Command_grep
commands["/bin/egrep"] = Command_grep
commands["egrep"] = Command_grep
commands["/bin/fgrep"] = Command_grep
commands["fgrep"] = Command_grep
