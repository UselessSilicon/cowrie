# Copyright (c) 2009-2014 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

"""
top command - display Linux processes
"""

from __future__ import annotations

import random
import time
from cowrie.shell.command import HoneyPotCommand

commands = {}


class Command_top(HoneyPotCommand):
    """
    top command - display system processes and resource usage
    """

    def call(self) -> None:
        # Parse basic options
        batch_mode = False
        iterations = 1

        for i, arg in enumerate(self.args):
            if arg == "-h" or arg == "--help":
                self.write_help()
                return
            elif arg == "-v" or arg == "-V":
                self.write("top version 3.3.12\n")
                self.write("Copyright (C) 2002-2017, procps-ng\n")
                return
            elif arg == "-b":
                batch_mode = True
            elif arg == "-n" and i + 1 < len(self.args):
                try:
                    iterations = int(self.args[i + 1])
                except ValueError:
                    pass

        # In a honeypot, we can't do interactive updates
        # So we just show one snapshot and exit
        self.show_top_snapshot()

    def show_top_snapshot(self) -> None:
        """Show a single snapshot of top output"""
        current_time = time.strftime("%H:%M:%S")
        uptime_days = random.randint(1, 30)
        uptime_hours = random.randint(0, 23)
        uptime_mins = random.randint(0, 59)

        # Generate realistic system stats
        load_1 = random.uniform(0.1, 2.0)
        load_5 = random.uniform(0.1, 2.0)
        load_15 = random.uniform(0.1, 2.0)

        total_tasks = random.randint(80, 150)
        running = random.randint(1, 3)
        sleeping = total_tasks - running - 1
        stopped = 0
        zombie = 0

        cpu_us = random.uniform(0.5, 15.0)
        cpu_sy = random.uniform(0.2, 5.0)
        cpu_ni = 0.0
        cpu_id = 100.0 - cpu_us - cpu_sy
        cpu_wa = random.uniform(0.0, 2.0)
        cpu_hi = 0.0
        cpu_si = 0.0
        cpu_st = 0.0

        mem_total = random.randint(1000000, 4000000)
        mem_free = random.randint(100000, 800000)
        mem_used = mem_total - mem_free
        mem_buff = random.randint(50000, 200000)

        swap_total = random.randint(500000, 2000000)
        swap_free = random.randint(400000, 1800000)
        swap_used = swap_total - swap_free
        swap_avail = mem_free + mem_buff

        # Header
        self.write(
            f"top - {current_time} up {uptime_days} days, {uptime_hours:2d}:{uptime_mins:02d},  1 user,  load average: {load_1:.2f}, {load_5:.2f}, {load_15:.2f}\n"
        )
        self.write(
            f"Tasks: {total_tasks} total,   {running} running, {sleeping} sleeping,   {stopped} stopped,   {zombie} zombie\n"
        )
        self.write(
            f"%Cpu(s): {cpu_us:4.1f} us, {cpu_sy:4.1f} sy, {cpu_ni:4.1f} ni, {cpu_id:5.1f} id, {cpu_wa:4.1f} wa, {cpu_hi:4.1f} hi, {cpu_si:4.1f} si, {cpu_st:4.1f} st\n"
        )
        self.write(
            f"KiB Mem : {mem_total:8d} total, {mem_free:8d} free, {mem_used:8d} used, {mem_buff:8d} buff/cache\n"
        )
        self.write(
            f"KiB Swap: {swap_total:8d} total, {swap_free:8d} free, {swap_used:8d} used. {swap_avail:8d} avail Mem\n"
        )
        self.write("\n")

        # Process list header
        self.write(
            "  PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND\n"
        )

        # Generate fake process list
        processes = [
            (1, "root", 20, 0, 33620, 2896, 1516, "S", 0.0, 0.1, "0:01.23", "init"),
            (
                2,
                "root",
                20,
                0,
                0,
                0,
                0,
                "S",
                0.0,
                0.0,
                "0:00.00",
                "kthreadd",
            ),
            (
                305,
                "root",
                20,
                0,
                42396,
                3456,
                2234,
                "S",
                0.0,
                0.2,
                "0:00.45",
                "systemd-journal",
            ),
            (
                324,
                "root",
                20,
                0,
                44620,
                2876,
                2456,
                "S",
                0.0,
                0.1,
                "0:00.12",
                "systemd-udevd",
            ),
            (528, "root", 20, 0, 21536, 1234, 1024, "S", 0.0, 0.1, "0:00.02", "cron"),
            (
                529,
                "root",
                20,
                0,
                256396,
                3456,
                2876,
                "S",
                0.0,
                0.2,
                "0:00.15",
                "rsyslogd",
            ),
            (532, "root", 20, 0, 65536, 3124, 2456, "S", 0.0, 0.2, "0:00.05", "sshd"),
            (
                1024,
                "www-data",
                20,
                0,
                124856,
                4567,
                2345,
                "S",
                0.0,
                0.3,
                "0:00.23",
                "nginx",
            ),
            (
                1234,
                "mysql",
                20,
                0,
                1456789,
                45678,
                23456,
                "S",
                0.3,
                2.8,
                "1:23.45",
                "mysqld",
            ),
            (
                1337,
                "root",
                20,
                0,
                78456,
                4567,
                3456,
                "S",
                0.0,
                0.3,
                "0:00.12",
                "sshd",
            ),
        ]

        # Add current shell and top
        session_pid = random.randint(1500, 2500)
        processes.append(
            (session_pid, "root", 20, 0, 21324, 3456, 2876, "S", 0.0, 0.2, "0:00.01", "bash")
        )
        processes.append(
            (
                session_pid + 1,
                "root",
                20,
                0,
                40388,
                3456,
                2876,
                "R",
                0.7,
                0.2,
                "0:00.01",
                "top",
            )
        )

        # Sort by CPU usage (top processes first)
        processes.sort(key=lambda x: x[8], reverse=True)

        # Display processes
        for pid, user, pr, ni, virt, res, shr, s, cpu, mem, time_val, cmd in processes[
            :20
        ]:
            self.write(
                f"{pid:5d} {user:<8s} {pr:3d} {ni:3d} {virt:7d} {res:6d} {shr:6d} {s} {cpu:5.1f} {mem:4.1f} {time_val:>9s} {cmd}\n"
            )

    def write_help(self) -> None:
        help_text = """Usage:
  top -hv | -bcHiOSs -d secs -n max -u|U user -p pid(s) -o field -w [cols]

  -b  Batch mode operation
      Starts top in 'Batch' mode, which could be useful for sending output
      from top to other programs or to a file.  In this mode, top will not
      accept input and runs until the iterations limit you've set with the
      '-n' command-line option or until killed.

  -c  Command line/Program name toggle
      Starts top with the last remembered 'c' state reversed.  Thus, if top
      was displaying command lines, now that field will show program names,
      and vice versa.

  -d  Delay-time interval as:  -d ss.tt (seconds.tenths)
      Specifies the delay between screen updates, and overrides the
      corresponding value in one's personal config file or the startup
      default.  Later this can be changed with the 'd' or 's' interactive
      commands.

  -H  Threads mode operation
      Instructs top to display individual threads.  Without this command-
      line option a summation of all threads in each process is shown.

  -i  Idle process toggle
      Starts top with the last remembered 'i' state reversed.  When this
      toggle is Off, tasks that are idled or zombied will not be displayed.

  -n  Number of iterations limit as:  -n number
      Specifies the maximum number of iterations, or frames, top should
      produce before ending.

  -o  Override sort field as:  -o fieldname
      Specifies the name of the field on which tasks will be sorted.

  -p  Monitor PIDs as:  -p pid [,pid ...]
      Monitor only processes with specified process IDs.  This option can
      be given up to 20 times, or you can provide a comma delimited list
      with up to 20 pids.  Co-mingling both approaches is permitted.

  -u  Monitor by user as:  -u username or -u UID
      Display only processes with a user id or user name matching that
      given.

  -U  Monitor by user as:  -U username or -U UID
      Display only processes with a user id or user name matching that
      given.  This matches real UID.

  -s  Secure mode operation
      Starts top with secure mode forced, even for root.  This mode is far
      better controlled through a system config file (see topic 5. FILES).

  -S  Cumulative time toggle
      Starts top with the last remembered 'S' state reversed.  When
      Cumulative time mode is On, each process is listed with the cpu time
      that it and its dead children have used.

  -h, --help     display this help text, then quit
  -v, -V         display version information, then quit
"""
        self.write(help_text)


commands["/usr/bin/top"] = Command_top
commands["top"] = Command_top
