# Copyright (c) 2009-2014 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

"""
ss command - socket statistics (modern netstat replacement)
"""

from __future__ import annotations

import random

from cowrie.shell.command import HoneyPotCommand

commands = {}


class Command_ss(HoneyPotCommand):
    """
    ss command - utility to investigate sockets
    """

    def call(self) -> None:
        show_tcp = False
        show_udp = False
        show_listening = False
        show_all = False
        show_processes = False
        numeric = False
        show_summary = False

        # Parse arguments
        if self.args:
            for arg in self.args:
                if arg in ("-h", "--help"):
                    self.show_help()
                    return
                elif arg in ("-V", "--version"):
                    self.show_version()
                    return
                elif arg in ("-s", "--summary"):
                    show_summary = True
                elif arg in ("-a", "--all"):
                    show_all = True
                elif arg in ("-l", "--listening"):
                    show_listening = True
                elif arg in ("-t", "--tcp"):
                    show_tcp = True
                elif arg in ("-u", "--udp"):
                    show_udp = True
                elif arg in ("-p", "--processes"):
                    show_processes = True
                elif arg in ("-n", "--numeric"):
                    numeric = True
                elif arg.startswith("-") and len(arg) > 1:
                    # Handle combined short options like -tuln
                    for char in arg[1:]:
                        if char == "t":
                            show_tcp = True
                        elif char == "u":
                            show_udp = True
                        elif char == "l":
                            show_listening = True
                        elif char == "n":
                            numeric = True
                        elif char == "p":
                            show_processes = True
                        elif char == "a":
                            show_all = True

        # Show summary if requested
        if show_summary:
            self.show_summary_stats()
            return

        # Default to showing all socket types if none specified
        if not show_tcp and not show_udp:
            show_tcp = True
            show_udp = True

        # Show socket information
        self.show_sockets(
            show_tcp=show_tcp,
            show_udp=show_udp,
            show_listening=show_listening,
            show_all=show_all,
            show_processes=show_processes,
            numeric=numeric,
        )

    def show_help(self) -> None:
        """Show ss help"""
        self.write(
            """Usage: ss [ OPTIONS ]
       ss [ OPTIONS ] [ FILTER ]
   -h, --help          this message
   -V, --version       output version information
   -n, --numeric       don't resolve service names
   -r, --resolve       resolve host names
   -a, --all           display all sockets
   -l, --listening     display listening sockets
   -o, --options       show timer information
   -e, --extended      show detailed socket information
   -m, --memory        show socket memory usage
   -p, --processes     show process using socket
   -i, --info          show internal TCP information
   -s, --summary       show socket usage summary
   -4, --ipv4          display only IP version 4 sockets
   -6, --ipv6          display only IP version 6 sockets
   -0, --packet        display PACKET sockets
   -t, --tcp           display only TCP sockets
   -u, --udp           display only UDP sockets
   -d, --dccp          display only DCCP sockets
   -w, --raw           display only RAW sockets
   -x, --unix          display only Unix domain sockets
   -f, --family=FAMILY display sockets of type FAMILY

   -A, --query=QUERY, --socket=QUERY
       QUERY := {all|inet|tcp|udp|raw|unix|packet|netlink}[,QUERY]

   -D, --diag=FILE     Dump raw information about TCP sockets to FILE
   -F, --filter=FILE   read filter information from FILE
"""
        )

    def show_version(self) -> None:
        """Show ss version"""
        self.write("ss utility, iproute2-ss161212\n")

    def show_summary_stats(self) -> None:
        """Show socket usage summary"""
        self.write("Total: 178 (kernel 0)\n")
        self.write(
            "TCP:   12 (estab 1, closed 2, orphaned 0, synrecv 0, timewait 2/0), ports 0\n"
        )
        self.write("\n")
        self.write("Transport Total     IP        IPv6\n")
        self.write("*         0         -         -\n")
        self.write("RAW       0         0         0\n")
        self.write("UDP       8         6         2\n")
        self.write("TCP       10        8         2\n")
        self.write("INET      18        14        4\n")
        self.write("FRAG      0         0         0\n")

    def show_sockets(
        self,
        show_tcp: bool,
        show_udp: bool,
        show_listening: bool,
        show_all: bool,
        show_processes: bool,
        numeric: bool,
    ) -> None:
        """Show socket information"""
        # Build header
        header_parts = [
            "State",
            "Recv-Q",
            "Send-Q",
            "Local Address:Port",
            "Peer Address:Port",
        ]
        if show_processes:
            header_parts.append("Process")

        self.write(
            " ".join(f"{h:20s}" if i < 4 else h for i, h in enumerate(header_parts))
            + "\n"
        )

        # Get connection info
        local_ip = self.protocol.transport.transport.getHost().host
        client_ip = self.protocol.clientIP
        ssh_port = self.protocol.transport.transport.getHost().port
        client_port = self.protocol.realClientPort

        # Show TCP connections
        if show_tcp:
            # Always show the current SSH connection
            state = "ESTAB"
            local_addr = (
                f"{local_ip}:{ssh_port}" if numeric else f"{self.protocol.hostname}:ssh"
            )
            peer_addr = f"{client_ip}:{client_port}"

            line_parts = [
                f"{state:20s}",
                f"{'0':20s}",
                f"{'0':20s}",
                f"{local_addr:20s}",
                peer_addr,
            ]

            if show_processes:
                sshd_pid = random.randint(1000, 9999)
                line_parts.append(f'users:(("sshd",pid={sshd_pid},fd=3))')

            self.write(" ".join(line_parts) + "\n")

            # Show listening SSH port if requested
            if show_listening or show_all:
                listen_addr = f"0.0.0.0:{ssh_port}" if numeric else "*:ssh"
                line_parts = [
                    f"{'LISTEN':20s}",
                    f"{'0':20s}",
                    f"{'128':20s}",
                    f"{listen_addr:20s}",
                    "*:*",
                ]

                if show_processes:
                    sshd_pid = random.randint(500, 999)
                    line_parts.append(f'users:(("sshd",pid={sshd_pid},fd=3))')

                self.write(" ".join(line_parts) + "\n")

        # Show UDP services if requested
        if show_udp and (show_listening or show_all):
            # Common UDP services
            udp_services = [
                ("68", "bootpc", 3),
                ("123", "ntp", 4),
            ]

            for port_num, port_name, fd in udp_services:
                port_str = port_num if numeric else port_name
                line_parts = [
                    f"{'UNCONN':20s}",
                    f"{'0':20s}",
                    f"{'0':20s}",
                    f"{'*:' + port_str:20s}",
                    "*:*",
                ]

                if show_processes:
                    pid = random.randint(300, 800)
                    process_name = port_name if port_name else "udp"
                    line_parts.append(f'users:(("{process_name}",pid={pid},fd={fd}))')

                self.write(" ".join(line_parts) + "\n")


commands["/bin/ss"] = Command_ss
commands["/usr/bin/ss"] = Command_ss
commands["ss"] = Command_ss
