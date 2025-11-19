# Copyright (c) 2009-2014 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

"""
strace command - trace system calls and signals
"""

from __future__ import annotations

import random
from cowrie.shell.command import HoneyPotCommand

commands = {}


class Command_strace(HoneyPotCommand):
    """
    strace command stub - simulates process tracing
    """

    def call(self) -> None:
        if not self.args or "--help" in self.args or "-h" in self.args:
            self.write(
                """usage: strace [-CdffhiqrtttTvVwxxy] [-I n] [-e expr]...
              [-a column] [-o file] [-s strsize] [-P path]...
              -p pid... / [-D] [-E var=val]... [-u username] PROG [ARGS]
   or: strace -c[dfw] [-I n] [-e expr]... [-O overhead] [-S sortby]
              -p pid... / [-D] [-E var=val]... [-u username] PROG [ARGS]

Output format:
  -a column      alignment COLUMN for printing syscall results (default 40)
  -i             print instruction pointer at time of syscall
  -o file        send trace output to FILE instead of stderr
  -q             suppress messages about attaching, detaching, etc.
  -r             print relative timestamp
  -s strsize     limit length of print strings to STRSIZE chars (default 32)
  -t             print absolute timestamp
  -tt            print absolute timestamp with usecs
  -T             print time spent in each syscall
  -x             print non-ascii strings in hex
  -xx            print all strings in hex
  -y             print paths associated with file descriptor arguments
  -yy            print protocol specific information associated with socket file descriptors

Statistics:
  -c             count time, calls, and errors for each syscall and report summary
  -C             like -c but also print regular output
  -O overhead    set overhead for tracing syscalls to OVERHEAD usecs
  -S sortby      sort syscall counts by: time, calls, name, nothing (default time)
  -w             summarise syscall latency (default is system time)

Filtering:
  -e expr        a qualifying expression: option=[!]all or option=[!]val1[,val2]...
     options:    trace, abbrev, verbose, raw, signal, read, write
  -P path        trace accesses to path

Tracing:
  -b execve      detach on execve syscall
  -D             run tracer process as a detached grandchild, not as parent
  -f             follow forks
  -ff            follow forks with output into separate files
  -I interruptible
     1:          no signals are blocked
     2:          fatal signals are blocked while decoding syscall (default)
     3:          fatal signals are always blocked (default if '-o FILE PROG')
     4:          fatal signals and SIGTSTP (^Z) are always blocked
  -p pid         trace process with process id PID, may be repeated
  -u username    run command as username handling setuid and/or setgid

Startup:
  -E var         remove var from the environment for command
  -E var=val     put var=val in the environment for command
  -h             print help message
  -V             print version

Miscellaneous:
  -d             enable debug output to stderr
  -v             verbose mode: print unabbreviated argv, stat, termios, etc. args
  -version       print version
"""
            )
            return

        if "-V" in self.args or "--version" in self.args or "-version" in self.args:
            self.write("strace -- version 4.26\n")
            self.write("Copyright (c) 1991-2018 The strace developers.\n")
            self.write("This is free software; see the source for copying conditions.\n")
            self.write("There is NO warranty; not even for MERCHANTABILITY or FITNESS FOR A\n")
            self.write("PARTICULAR PURPOSE.\n")
            return

        # Check for -p (attach to process)
        if "-p" in self.args:
            try:
                idx = self.args.index("-p")
                if idx + 1 < len(self.args):
                    pid = self.args[idx + 1]
                    self.write(f"strace: attach: ptrace(PTRACE_SEIZE, {pid}): Operation not permitted\n")
                    return
            except (ValueError, IndexError):
                pass

        # If a command is provided, simulate tracing it
        command_args = [arg for arg in self.args if not arg.startswith("-")]

        if command_args:
            cmd = command_args[0]
            # Simulate some syscalls
            self.write(f"execve(\"/bin/{cmd}\", [\"{cmd}\"], 0x7ffd... /* 24 vars */) = 0\n")
            self.write(
                "brk(NULL)                               = 0x55c8f2a1b000\n"
            )
            self.write(
                "access(\"/etc/ld.so.preload\", R_OK)     = -1 ENOENT (No such file or directory)\n"
            )
            self.write(
                "openat(AT_FDCWD, \"/etc/ld.so.cache\", O_RDONLY|O_CLOEXEC) = 3\n"
            )
            self.write(
                "fstat(3, {st_mode=S_IFREG|0644, st_size=27690, ...}) = 0\n"
            )
            self.write(
                "mmap(NULL, 27690, PROT_READ, MAP_PRIVATE, 3, 0) = 0x7f8b9c8a1000\n"
            )
            self.write("close(3)                                = 0\n")
            self.write(
                "openat(AT_FDCWD, \"/lib/x86_64-linux-gnu/libc.so.6\", O_RDONLY|O_CLOEXEC) = 3\n"
            )
            self.write(
                "read(3, \"\\177ELF\\2\\1\\1\\3\\0\\0\\0\\0\\0\\0\\0\\0\"..., 832) = 832\n"
            )
            self.write(
                "fstat(3, {st_mode=S_IFREG|0755, st_size=2030544, ...}) = 0\n"
            )
            self.write("close(3)                                = 0\n")

            # Simulate command execution
            exit_code = random.choice([0, 0, 0, 1])  # Usually succeeds
            self.write(f"exit_group({exit_code})                         = ?\n")
            self.write(
                f"+++ exited with {exit_code} +++\n"
            )
        else:
            self.errorWrite("strace: must have PROG [ARGS] or -p PID\n")
            self.errorWrite("Try 'strace -h' for more information.\n")


commands["/usr/bin/strace"] = Command_strace
commands["strace"] = Command_strace
