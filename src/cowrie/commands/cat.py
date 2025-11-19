# Copyright (c) 2010 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

"""
cat command

"""

from __future__ import annotations


import getopt

from twisted.python import log

from cowrie.shell.command import HoneyPotCommand
from cowrie.shell.fs import FileNotFound

commands = {}


class Command_cat(HoneyPotCommand):
    """
    cat command
    """

    number = False
    number_nonblank = False
    show_ends = False
    show_tabs = False
    show_nonprinting = False
    squeeze_blank = False
    linenumber = 1

    def start(self) -> None:
        try:
            optlist, args = getopt.gnu_getopt(
                self.args, "AbeEnstTuv", ["help", "number", "number-nonblank", "show-ends", "show-tabs", "show-nonprinting", "squeeze-blank", "version"]
            )
        except getopt.GetoptError as err:
            self.errorWrite(
                f"cat: invalid option -- '{err.opt}'\nTry 'cat --help' for more information.\n"
            )
            self.exit()
            return

        for o, _a in optlist:
            if o in ("--help"):
                self.help()
                self.exit()
                return
            elif o in ("-n", "--number"):
                self.number = True
            elif o in ("-b", "--number-nonblank"):
                self.number_nonblank = True
                self.number = False  # -b overrides -n
            elif o in ("-E", "--show-ends"):
                self.show_ends = True
            elif o in ("-T", "--show-tabs"):
                self.show_tabs = True
            elif o in ("-s", "--squeeze-blank"):
                self.squeeze_blank = True
            elif o in ("-v", "--show-nonprinting"):
                self.show_nonprinting = True
            elif o in ("-e"):
                self.show_ends = True
                self.show_nonprinting = True
            elif o in ("-t"):
                self.show_tabs = True
                self.show_nonprinting = True
            elif o in ("-A"):
                self.show_ends = True
                self.show_tabs = True
                self.show_nonprinting = True

        if len(args) > 0:
            for arg in args:
                if arg == "-":
                    self.output(self.input_data)
                    continue

                pname = self.fs.resolve_path(arg, self.protocol.cwd)

                if self.fs.isdir(pname):
                    self.errorWrite(f"cat: {arg}: Is a directory\n")
                    continue

                try:
                    contents = self.fs.file_contents(pname)
                    self.output(contents)
                except FileNotFound:
                    self.errorWrite(f"cat: {arg}: No such file or directory\n")
            self.exit()
        elif self.input_data is not None:
            self.output(self.input_data)
            self.exit()

    def output(self, inb: bytes | None) -> None:
        """
        This is the cat output, with optional line numbering and formatting
        """
        if inb is None:
            return

        lines = inb.split(b"\n")
        if lines[-1] == b"":
            lines.pop()

        prev_blank = False
        for line in lines:
            # Squeeze blank lines if requested
            is_blank = len(line.strip()) == 0
            if self.squeeze_blank and is_blank and prev_blank:
                continue
            prev_blank = is_blank

            # Number lines (skip blank if -b is used)
            if self.number or (self.number_nonblank and not is_blank):
                self.write(f"{self.linenumber:>6}  ")
                self.linenumber = self.linenumber + 1

            # Process the line for special characters
            if self.show_tabs or self.show_nonprinting:
                line = self.process_line(line)

            self.writeBytes(line)

            # Show line endings if requested
            if self.show_ends:
                self.write("$")

            self.write("\n")

    def process_line(self, line: bytes) -> bytes:
        """
        Process line to show tabs and non-printing characters
        """
        if not (self.show_tabs or self.show_nonprinting):
            return line

        result = bytearray()
        for byte in line:
            if self.show_tabs and byte == 9:  # Tab character
                result.extend(b"^I")
            elif self.show_nonprinting and byte < 32 and byte != 9 and byte != 10:
                # Show control characters as ^X
                result.extend(b"^" + bytes([byte + 64]))
            elif self.show_nonprinting and byte == 127:
                # DEL character
                result.extend(b"^?")
            elif self.show_nonprinting and byte >= 128:
                # High-bit characters shown as M-
                result.extend(b"M-")
                if byte >= 128 + 32 and byte < 127 + 128:
                    result.append(byte - 128)
                else:
                    result.extend(b"^" + bytes([(byte - 128 + 64) % 128]))
            else:
                result.append(byte)
        return bytes(result)

    def lineReceived(self, line: str) -> None:
        """
        This function logs standard input from the user send to cat
        """
        log.msg(
            eventid="cowrie.session.input",
            realm="cat",
            input=line,
            format="INPUT (%(realm)s): %(input)s",
        )

        self.output(line.encode("utf-8"))

    def handle_CTRL_D(self) -> None:
        """
        ctrl-d is end-of-file, time to terminate
        """
        self.exit()

    def help(self) -> None:
        self.write(
            """Usage: cat [OPTION]... [FILE]...
Concatenate FILE(s) to standard output.

With no FILE, or when FILE is -, read standard input.

    -A, --show-all           equivalent to -vET
    -b, --number-nonblank    number nonempty output lines, overrides -n
    -e                       equivalent to -vE
    -E, --show-ends          display $ at end of each line
    -n, --number             number all output lines
    -s, --squeeze-blank      suppress repeated empty output lines
    -t                       equivalent to -vT
    -T, --show-tabs          display TAB characters as ^I
    -u                       (ignored)
    -v, --show-nonprinting   use ^ and M- notation, except for LFD and TAB
        --help     display this help and exit
        --version  output version information and exit

Examples:
    cat f - g  Output f's contents, then standard input, then g's contents.
    cat        Copy standard input to standard output.

GNU coreutils online help: <http://www.gnu.org/software/coreutils/>
Full documentation at: <http://www.gnu.org/software/coreutils/cat>
or available locally via: info '(coreutils) cat invocation'
"""
        )


commands["/bin/cat"] = Command_cat
commands["cat"] = Command_cat
