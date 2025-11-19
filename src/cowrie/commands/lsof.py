# Copyright (c) 2009-2014 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

"""
lsof command - list open files
"""

from __future__ import annotations

import random

from cowrie.shell.command import HoneyPotCommand

commands = {}


class Command_lsof(HoneyPotCommand):
    """
    lsof command - list open files and network connections
    """

    def call(self) -> None:
        show_internet = False
        show_tcp = False
        show_udp = False
        show_listening = False
        numeric = False
        specific_pid = None
        specific_user = None

        # Parse arguments
        if self.args:
            for i, arg in enumerate(self.args):
                if arg in ("-h", "-?", "--help"):
                    self.show_help()
                    return
                elif arg in ("-v", "--version"):
                    self.show_version()
                    return
                elif arg == "-i":
                    # Internet connections
                    show_internet = True
                    # Check for protocol specification after -i
                    if i + 1 < len(self.args) and not self.args[i + 1].startswith("-"):
                        proto = self.args[i + 1].lower()
                        if "tcp" in proto:
                            show_tcp = True
                        if "udp" in proto:
                            show_udp = True
                elif arg.startswith("-iTCP") or arg.startswith("-itcp"):
                    show_internet = True
                    show_tcp = True
                elif arg.startswith("-iUDP") or arg.startswith("-iudp"):
                    show_internet = True
                    show_udp = True
                elif arg == "-n":
                    numeric = True
                elif arg == "-P":
                    numeric = True
                elif arg == "-l":
                    show_listening = True
                elif arg == "-p":
                    # Process ID
                    if i + 1 < len(self.args):
                        specific_pid = self.args[i + 1]
                elif arg == "-u":
                    # User
                    if i + 1 < len(self.args):
                        specific_user = self.args[i + 1]

        # Show output
        self.show_open_files(
            show_internet=show_internet,
            show_tcp=show_tcp,
            show_udp=show_udp,
            show_listening=show_listening,
            numeric=numeric,
            specific_pid=specific_pid,
            specific_user=specific_user,
        )

    def show_help(self) -> None:
        """Show lsof help"""
        self.write(
            """lsof 4.89
 latest revision: ftp://lsof.itap.purdue.edu/pub/tools/unix/lsof/
 latest FAQ     : ftp://lsof.itap.purdue.edu/pub/tools/unix/lsof/FAQ
 latest man page: ftp://lsof.itap.purdue.edu/pub/tools/unix/lsof/lsof_man
 usage: [-?abhlnNoOPRtUvV] [+|-c c] [+|-d s] [+D D] [+|-f[cgG]]
 [-F [f]] [-g [s]] [-i [i]] [+|-L [l]] [+|-M] [-o [o]] [-p s]
 [+|-r [t]] [-s [p:s]] [-S [t]] [-T [t]] [-u s] [+|-w] [-x [fl]] [--] [names]
Use the ``-h'' option to get more help information.
"""
        )

    def show_version(self) -> None:
        """Show lsof version"""
        self.write("lsof version information:\n")
        self.write("    revision: 4.89\n")
        self.write(
            "    latest revision: ftp://lsof.itap.purdue.edu/pub/tools/unix/lsof/\n"
        )
        self.write(
            "    latest FAQ     : ftp://lsof.itap.purdue.edu/pub/tools/unix/lsof/FAQ\n"
        )
        self.write(
            "    latest man page: ftp://lsof.itap.purdue.edu/pub/tools/unix/lsof/lsof_man\n"
        )

    def show_open_files(
        self,
        show_internet: bool,
        show_tcp: bool,
        show_udp: bool,
        show_listening: bool,
        numeric: bool,
        specific_pid: str | None,
        specific_user: str | None,
    ) -> None:
        """Show open files and connections"""
        # Header
        self.write(
            "COMMAND     PID      USER   FD      TYPE             DEVICE SIZE/OFF       NODE NAME\n"
        )

        username = self.protocol.user.username
        local_ip = self.protocol.transport.transport.getHost().host
        client_ip = self.protocol.clientIP
        ssh_port = self.protocol.transport.transport.getHost().port
        client_port = self.protocol.realClientPort

        # Filter by user if specified
        if specific_user and specific_user != username:
            return

        # SSH daemon process
        sshd_pid = random.randint(500, 999)
        if not specific_pid or specific_pid == str(sshd_pid):
            # Show listening socket
            if not show_internet or show_tcp or (not show_tcp and not show_udp):
                port_str = str(ssh_port) if numeric else "ssh"
                self.write(
                    f"{'sshd':11s} {sshd_pid:<8d} {'root':8s} {'3u':7s} {'IPv4':16s} "
                    f"{'12345':12s} {'0t0':12s} {'TCP':>6s} *:{port_str} (LISTEN)\n"
                )

        # Current SSH session process
        session_pid = random.randint(1000, 9999)
        if not specific_pid or specific_pid == str(session_pid):
            if not show_internet or show_tcp or (not show_tcp and not show_udp):
                # SSH connection
                port_str = str(ssh_port) if numeric else "ssh"
                self.write(
                    f"{'sshd':11s} {session_pid:<8d} {username:8s} {'3u':7s} {'IPv4':16s} "
                    f"{'45678':12s} {'0t0':12s} {'TCP':>6s} "
                    f"{local_ip}:{port_str}->{client_ip}:{client_port} (ESTABLISHED)\n"
                )

            # Show some file descriptors for the shell
            if not show_internet:
                # stdin/stdout/stderr
                for fd, name in [
                    (0, "/dev/pts/0"),
                    (1, "/dev/pts/0"),
                    (2, "/dev/pts/0"),
                ]:
                    self.write(
                        f"{'bash':11s} {session_pid:<8d} {username:8s} {f'{fd}u':7s} {'CHR':16s} "
                        f"{'136,0':12s} {'0t0':12s} {'3':>6s} {name}\n"
                    )

                # Some common files
                for fd, name in [(255, "/home/" + username + "/.bashrc")]:
                    self.write(
                        f"{'bash':11s} {session_pid:<8d} {username:8s} {f'{fd}r':7s} {'REG':16s} "
                        f"{'8,1':12s} {random.randint(100, 5000):>12d} {'12345':>6s} {name}\n"
                    )

        # System processes if showing all
        if not show_internet and not specific_pid:
            system_processes = [
                ("systemd", 1, "root", "/sbin/init"),
                (
                    "systemd-jo",
                    random.randint(200, 300),
                    "root",
                    "/lib/systemd/systemd-journald",
                ),
                ("cron", random.randint(400, 500), "root", "/usr/sbin/cron"),
            ]

            for cmd, pid, user, exe in system_processes:
                if specific_user and specific_user != user:
                    continue

                # txt (executable)
                self.write(
                    f"{cmd:11s} {pid:<8d} {user:8s} {'txt':7s} {'REG':16s} "
                    f"{'8,1':12s} {random.randint(50000, 200000):>12d} "
                    f"{random.randint(10000, 99999):>6d} {exe}\n"
                )


commands["/usr/bin/lsof"] = Command_lsof
commands["lsof"] = Command_lsof
