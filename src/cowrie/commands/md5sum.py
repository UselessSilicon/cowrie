# Copyright (c) 2009-2014 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

"""
md5sum/sha256sum/sha1sum commands - compute and check message digests
"""

from __future__ import annotations

import hashlib
from cowrie.shell.command import HoneyPotCommand

commands = {}


class Command_md5sum(HoneyPotCommand):
    """
    md5sum command - compute MD5 checksum
    """

    def call(self) -> None:
        if "--help" in self.args:
            self.write(
                """Usage: md5sum [OPTION]... [FILE]...
Print or check MD5 (128-bit) checksums.

With no FILE, or when FILE is -, read standard input.

  -b, --binary         read in binary mode
  -c, --check          read MD5 sums from the FILEs and check them
      --tag            create a BSD-style checksum
  -t, --text           read in text mode (default)

The following five options are useful only when verifying checksums:
      --ignore-missing  don't fail or report status for missing files
      --quiet          don't print OK for each successfully verified file
      --status         don't output anything, status code shows success
      --strict         exit non-zero for improperly formatted checksum lines
  -w, --warn           warn about improperly formatted checksum lines

      --help     display this help and exit
      --version  output version information and exit

The sums are computed as described in RFC 1321.  When checking, the input
should be a former output of this program.  The default mode is to print
a line with checksum, a character indicating input mode ('*' for binary,
space for text), and name for each FILE.
"""
            )
            return

        if "--version" in self.args:
            self.write("md5sum (GNU coreutils) 8.30\n")
            return

        check_mode = "-c" in self.args or "--check" in self.args
        files = [arg for arg in self.args if not arg.startswith("-")]

        if not files:
            self.errorWrite("md5sum: no files specified\n")
            return

        for filename in files:
            try:
                # Try to get file contents from virtual filesystem
                if self.fs.exists(filename):
                    contents = self.fs.getfile(filename)
                    if contents and len(contents) > 7:
                        # File has real contents
                        real_file = contents[7]  # Index 7 is the realfile path
                        if real_file:
                            try:
                                with open(real_file, "rb") as f:
                                    data = f.read()
                                    md5 = hashlib.md5(data).hexdigest()
                                    self.write(f"{md5}  {filename}\n")
                                    continue
                            except Exception:
                                pass

                    # If we couldn't read real file, generate fake hash
                    fake_hash = hashlib.md5(filename.encode()).hexdigest()
                    self.write(f"{fake_hash}  {filename}\n")
                else:
                    self.errorWrite(
                        f"md5sum: {filename}: No such file or directory\n"
                    )
            except Exception:
                self.errorWrite(f"md5sum: {filename}: No such file or directory\n")


class Command_sha256sum(HoneyPotCommand):
    """
    sha256sum command - compute SHA256 checksum
    """

    def call(self) -> None:
        if "--help" in self.args:
            self.write(
                """Usage: sha256sum [OPTION]... [FILE]...
Print or check SHA256 (256-bit) checksums.

With no FILE, or when FILE is -, read standard input.

  -b, --binary         read in binary mode
  -c, --check          read SHA256 sums from the FILEs and check them
      --tag            create a BSD-style checksum
  -t, --text           read in text mode (default)

The following five options are useful only when verifying checksums:
      --ignore-missing  don't fail or report status for missing files
      --quiet          don't print OK for each successfully verified file
      --status         don't output anything, status code shows success
      --strict         exit non-zero for improperly formatted checksum lines
  -w, --warn           warn about improperly formatted checksum lines

      --help     display this help and exit
      --version  output version information and exit

The sums are computed as described in FIPS-180-2.  When checking, the input
should be a former output of this program.  The default mode is to print
a line with checksum, a character indicating input mode ('*' for binary,
space for text), and name for each FILE.
"""
            )
            return

        if "--version" in self.args:
            self.write("sha256sum (GNU coreutils) 8.30\n")
            return

        files = [arg for arg in self.args if not arg.startswith("-")]

        if not files:
            self.errorWrite("sha256sum: no files specified\n")
            return

        for filename in files:
            try:
                # Try to get file contents from virtual filesystem
                if self.fs.exists(filename):
                    contents = self.fs.getfile(filename)
                    if contents and len(contents) > 7:
                        # File has real contents
                        real_file = contents[7]  # Index 7 is the realfile path
                        if real_file:
                            try:
                                with open(real_file, "rb") as f:
                                    data = f.read()
                                    sha256 = hashlib.sha256(data).hexdigest()
                                    self.write(f"{sha256}  {filename}\n")
                                    continue
                            except Exception:
                                pass

                    # If we couldn't read real file, generate fake hash
                    fake_hash = hashlib.sha256(filename.encode()).hexdigest()
                    self.write(f"{fake_hash}  {filename}\n")
                else:
                    self.errorWrite(
                        f"sha256sum: {filename}: No such file or directory\n"
                    )
            except Exception:
                self.errorWrite(
                    f"sha256sum: {filename}: No such file or directory\n"
                )


class Command_sha1sum(HoneyPotCommand):
    """
    sha1sum command - compute SHA1 checksum
    """

    def call(self) -> None:
        if "--help" in self.args:
            self.write(
                """Usage: sha1sum [OPTION]... [FILE]...
Print or check SHA1 (160-bit) checksums.

With no FILE, or when FILE is -, read standard input.

  -b, --binary         read in binary mode
  -c, --check          read SHA1 sums from the FILEs and check them
      --tag            create a BSD-style checksum
  -t, --text           read in text mode (default)

      --help     display this help and exit
      --version  output version information and exit
"""
            )
            return

        if "--version" in self.args:
            self.write("sha1sum (GNU coreutils) 8.30\n")
            return

        files = [arg for arg in self.args if not arg.startswith("-")]

        if not files:
            self.errorWrite("sha1sum: no files specified\n")
            return

        for filename in files:
            try:
                # Try to get file contents from virtual filesystem
                if self.fs.exists(filename):
                    contents = self.fs.getfile(filename)
                    if contents and len(contents) > 7:
                        # File has real contents
                        real_file = contents[7]  # Index 7 is the realfile path
                        if real_file:
                            try:
                                with open(real_file, "rb") as f:
                                    data = f.read()
                                    sha1 = hashlib.sha1(data).hexdigest()
                                    self.write(f"{sha1}  {filename}\n")
                                    continue
                            except Exception:
                                pass

                    # If we couldn't read real file, generate fake hash
                    fake_hash = hashlib.sha1(filename.encode()).hexdigest()
                    self.write(f"{fake_hash}  {filename}\n")
                else:
                    self.errorWrite(
                        f"sha1sum: {filename}: No such file or directory\n"
                    )
            except Exception:
                self.errorWrite(f"sha1sum: {filename}: No such file or directory\n")


commands["/usr/bin/md5sum"] = Command_md5sum
commands["md5sum"] = Command_md5sum
commands["/usr/bin/sha256sum"] = Command_sha256sum
commands["sha256sum"] = Command_sha256sum
commands["/usr/bin/sha1sum"] = Command_sha1sum
commands["sha1sum"] = Command_sha1sum
