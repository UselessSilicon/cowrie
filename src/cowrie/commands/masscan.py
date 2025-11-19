# Copyright (c) 2009-2014 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

"""
masscan command - Fast TCP port scanner
"""

from __future__ import annotations

import random
import time
from twisted.python import log
from cowrie.shell.command import HoneyPotCommand

commands = {}


class Command_masscan(HoneyPotCommand):
    """
    masscan command stub - logs scanning attempts but doesn't actually scan
    """

    def call(self) -> None:
        if not self.args or "--help" in self.args or "-h" in self.args:
            self.write(
                """usage:
masscan -p80,8000-8100 10.0.0.0/8 --rate=10000
 scan some web ports on 10.x.x.x at 10kpps
masscan --nmap
 list those options that are compatible with nmap
masscan -p80 10.0.0.0/8 --banners -oB <filename>
 save results of scan in binary format to <filename>
masscan --open --banners --readscan <filename> -oX <savefile>
 read binary scan results in <filename> and save them as xml in <savefile>

TARGET SPECIFICATION:
 Can pass IP addresses, ranges or CIDR networks
 Ex: 10.0.0.1, 10.0.0.0/8, 10.0.0.3-10.0.0.23
 -iL <filename>: Input from list of IPs/ranges
 --exclude <ip/range>: IP addresses to exclude from scan
 --excludefile <file>: File with IPs to exclude

PORT SPECIFICATION:
 -p <ports>: Ports to scan. Use ranges and/or comma separated
             Ex: -p22,80,443,8000-8100

OPTIONS:
 --banners: Capture banner information
 --rate <packets-per-second>: Transmission rate
 --conf <filename>: Read parameters from configuration file
 --echo: Echo the configuration parameters
 --adapter <name>: Use named raw network interface
 --adapter-ip <ip>: Send packets using this IP address
 --adapter-port <port>: Send packets using this port
 --adapter-mac <mac>: Send packets using this MAC address
 --router-mac <mac>: Send packets to this MAC address
 --ping: Include ICMP echo request
 --exclude <ip>: Exclude this IP address from scan
 --excludefile <file>: Exclude IPs in this file
 --append-output: Append to output file, don't overwrite
 --iflist: List available network interfaces
 --retries <count>: Maximum retransmission rate
 --nmap: Print help about nmap-compatibility
 --pcap-payloads <file>: Read packets from libpcap file
 --nmap-payloads <file>: Read packets from nmap file
 --http-user-agent <value>: Set HTTP user-agent field
 --open-only: Report only open ports
 --pcap <filename>: Save packets in libpcap format
 --packet-trace: Print summary of packets sent/received
 --pfring: Force usage of PF_RING driver
 --resume <index>: Resume scan from this index
 --resume-count <count>: Maximum scan count before exiting
 --shards <x>/<y>: Split scan across instances
 --rotate <time>: Rotate output files after this time
 --rotate-offset <time>: Offset time by this
 --rotate-dir <directory>: Store rotated files in this dir
 --seed <int>: Random seed for scan order
 --ttl <num>: Set IP TTL field
 --wait <seconds>: Wait before transmitting
 --offline: Don't transmit packets

OUTPUT:
 -oX <file>: Save output in XML format
 -oJ <file>: Save output in JSON format
 -oG <file>: Save output in Grepable format
 -oB <file>: Save output in Binary format
 -oL <file>: Save output in List format

COMPATIBILITY:
 masscan --nmap: List nmap-compatible options
"""
            )
            return

        # Check for version
        if "--version" in self.args or "-V" in self.args:
            self.write(
                "Masscan version 1.0.5 ( https://github.com/robertdavidgraham/masscan )\n"
            )
            self.write("Compiled on: Jan 15 2025 12:34:56\n")
            self.write("Compiler: gcc 9.3.0\n")
            self.write("OS: Linux\n")
            self.write("CPU: x86 (64 bit)\n")
            return

        # Check for nmap compatibility
        if "--nmap" in self.args:
            self.write(
                """The following nmap options are supported:
 -iL <filename>            Input from list of IPs/ranges
 -p <port-range>           Ports to scan
 -Pn                       Skip host discovery (always on for masscan)
 -n                        No DNS resolution (always on for masscan)
 -sS                       SYN scan (always on for masscan)
 --open                    Report only open ports
 --exclude <ip/range>      Exclude these IPs
 --excludefile <file>      Exclude IPs in this file
 -oX <file>                XML output
 -oG <file>                Grepable output
 -oN <file>                Normal output
 -v                        Verbose output
"""
            )
            return

        # Parse arguments
        targets = []
        ports = []
        rate = 100
        banners = False
        open_only = False

        i = 0
        while i < len(self.args):
            arg = self.args[i]

            if arg == "-p":
                if i + 1 < len(self.args):
                    ports.append(self.args[i + 1])
                    i += 1
            elif arg.startswith("-p"):
                ports.append(arg[2:])
            elif arg == "--rate":
                if i + 1 < len(self.args):
                    try:
                        rate = int(self.args[i + 1])
                    except ValueError:
                        pass
                    i += 1
            elif arg == "--banners":
                banners = True
            elif arg == "--open" or arg == "--open-only":
                open_only = True
            elif arg.startswith("-o"):
                # Output file - skip next arg
                if not arg[2:] and i + 1 < len(self.args):
                    i += 1
            elif not arg.startswith("-"):
                targets.append(arg)
            i += 1

        if not targets:
            self.errorWrite("FAIL: target IP address(es) required\n")
            return

        if not ports:
            self.errorWrite("FAIL: target port(s) required, use '-p <port>'\n")
            return

        # Log the scan attempt
        log.msg(
            eventid="cowrie.command.masscan",
            format="Masscan scan attempted: targets=%(targets)s, ports=%(ports)s, rate=%(rate)d",
            targets=",".join(targets),
            ports=",".join(ports),
            rate=rate,
        )

        # Simulate masscan output
        self.write("\nStarting masscan 1.0.5 (http://bit.ly/14GZzcT) at ")
        self.write(time.strftime("%Y-%m-%d %H:%M:%S GMT\n"))
        self.write(f"Initiating SYN Stealth Scan\n")
        self.write(f"Scanning {len(targets)} hosts [ports: {','.join(ports)}]\n")

        # Simulate finding some open ports
        port_list = []
        for port_spec in ports:
            if "-" in port_spec:
                try:
                    start, end = port_spec.split("-")
                    port_list.extend(range(int(start), min(int(end) + 1, int(start) + 10)))
                except ValueError:
                    pass
            else:
                try:
                    port_list.append(int(port_spec))
                except ValueError:
                    pass

        # Show some discovered ports
        for target in targets[:5]:  # Limit to 5 targets to avoid spam
            for port in port_list[:3]:  # Show a few ports
                if random.random() < 0.3:  # 30% chance port is "open"
                    timestamp = time.strftime("%H:%M:%S")
                    self.write(f"Discovered open port {port}/tcp on {target}\n")

        self.write("\n")


commands["/usr/bin/masscan"] = Command_masscan
commands["masscan"] = Command_masscan
