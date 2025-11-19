# Copyright (c) 2009-2014 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

"""
nmap command - Network exploration tool and security / port scanner
"""

from __future__ import annotations

import random
import time
from twisted.python import log
from cowrie.shell.command import HoneyPotCommand

commands = {}


class Command_nmap(HoneyPotCommand):
    """
    nmap command stub - logs scanning attempts but doesn't actually scan
    """

    def call(self) -> None:
        if not self.args:
            self.write(
                "Nmap 7.80 ( https://nmap.org )\n"
                "Usage: nmap [Scan Type(s)] [Options] {target specification}\n"
                "TARGET SPECIFICATION:\n"
                "  Can pass hostnames, IP addresses, networks, etc.\n"
                "  Ex: scanme.nmap.org, microsoft.com/24, 192.168.0.1; 10.0.0-255.1-254\n"
                "  -iL <inputfilename>: Input from list of hosts/networks\n"
                "  -iR <num hosts>: Choose random targets\n"
                "  --exclude <host1[,host2][,host3],...>: Exclude hosts/networks\n"
                "  --excludefile <exclude_file>: Exclude list from file\n"
                "HOST DISCOVERY:\n"
                "  -sL: List Scan - simply list targets to scan\n"
                "  -sn: Ping Scan - disable port scan\n"
                "  -Pn: Treat all hosts as online -- skip host discovery\n"
                "SCAN TECHNIQUES:\n"
                "  -sS/sT/sA/sW/sM: TCP SYN/Connect()/ACK/Window/Maimon scans\n"
                "  -sU: UDP Scan\n"
                "  -sN/sF/sX: TCP Null, FIN, and Xmas scans\n"
                "PORT SPECIFICATION:\n"
                "  -p <port ranges>: Only scan specified ports\n"
                "    Ex: -p22; -p1-65535; -p U:53,111,137,T:21-25,80,139,8080,S:9\n"
                "SERVICE/VERSION DETECTION:\n"
                "  -sV: Probe open ports to determine service/version info\n"
                "OS DETECTION:\n"
                "  -O: Enable OS detection\n"
                "OUTPUT:\n"
                "  -oN/-oX/-oG <file>: Output scan in normal, XML, Grepable format\n"
                "  -v: Increase verbosity level (use -vv or more for greater effect)\n"
                "MISC:\n"
                "  -A: Enable OS detection, version detection, script scanning, and traceroute\n"
                "  --script=<Lua scripts>: <Lua scripts> is a comma separated list of\n"
                "           directories, script-files or script-categories\n"
                "  -V: Print version number\n"
                "  -h: Print this help summary page.\n"
                "EXAMPLES:\n"
                "  nmap -v -A scanme.nmap.org\n"
                "  nmap -v -sn 192.168.0.0/16 10.0.0.0/8\n"
                "  nmap -v -iR 10000 -Pn -p 80\n"
                "SEE THE MAN PAGE (https://nmap.org/book/man.html) FOR MORE OPTIONS AND EXAMPLES\n"
            )
            return

        # Parse arguments
        targets = []
        scan_type = "SYN"
        ports = "1-1000"
        version_detect = False
        os_detect = False
        verbose = 0

        i = 0
        while i < len(self.args):
            arg = self.args[i]

            if arg in ("-h", "--help"):
                self.call()  # Show help
                return
            elif arg in ("-V", "--version"):
                self.write("Nmap version 7.80 ( https://nmap.org )\n")
                return
            elif arg == "-sS":
                scan_type = "SYN"
            elif arg == "-sT":
                scan_type = "Connect"
            elif arg == "-sU":
                scan_type = "UDP"
            elif arg == "-sV":
                version_detect = True
            elif arg == "-O":
                os_detect = True
            elif arg == "-A":
                version_detect = True
                os_detect = True
            elif arg == "-v":
                verbose = 1
            elif arg == "-vv":
                verbose = 2
            elif arg == "-Pn":
                pass  # Skip host discovery
            elif arg.startswith("-p"):
                if len(arg) > 2:
                    ports = arg[2:]
                elif i + 1 < len(self.args):
                    ports = self.args[i + 1]
                    i += 1
            elif arg.startswith("-o"):
                # Output file - skip next arg
                if i + 1 < len(self.args):
                    i += 1
            elif not arg.startswith("-"):
                targets.append(arg)
            i += 1

        if not targets:
            self.errorWrite("nmap: No targets specified\n")
            return

        # Log the scan attempt
        log.msg(
            eventid="cowrie.command.nmap",
            format="Nmap scan attempted: targets=%(targets)s, scan_type=%(scan_type)s, ports=%(ports)s",
            targets=",".join(targets),
            scan_type=scan_type,
            ports=ports,
        )

        # Simulate nmap output
        self.write(f"\nStarting Nmap 7.80 ( https://nmap.org ) at {time.strftime('%Y-%m-%d %H:%M %Z')}\n")

        if verbose:
            self.write(f"Initiating {scan_type} Scan at {time.strftime('%H:%M')}\n")
            self.write(f"Scanning {len(targets)} host(s) [ports {ports}]\n")

        # Simulate scanning each target
        for target in targets:
            self.write(f"Nmap scan report for {target}\n")
            self.write(f"Host is up (0.00{random.randint(10, 99)}s latency).\n")

            # Show some open ports
            if verbose:
                self.write("Not shown: 997 closed ports\n")

            self.write("PORT     STATE SERVICE\n")

            # Randomly show some common open ports
            common_ports = [
                ("22/tcp", "ssh"),
                ("80/tcp", "http"),
                ("443/tcp", "https"),
            ]

            for port, service in common_ports[:random.randint(1, 3)]:
                self.write(f"{port:<9} open  {service}\n")

            if version_detect:
                self.write("\nService Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel\n")

            if os_detect:
                self.write("\nOS details: Linux 3.2 - 4.9\n")
                self.write("Network Distance: 1 hop\n")

            self.write("\n")

        self.write(
            f"\nNmap done: {len(targets)} IP address{' ' if len(targets) == 1 else 'es '}({len(targets)} host{'s' if len(targets) > 1 else ''} up) scanned in {random.uniform(0.5, 3.0):.2f} seconds\n"
        )


commands["/usr/bin/nmap"] = Command_nmap
commands["nmap"] = Command_nmap
