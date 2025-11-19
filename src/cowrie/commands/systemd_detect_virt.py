# Copyright (c) 2009-2014 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

"""
systemd-detect-virt command - Detect execution in a virtualized environment
"""

from __future__ import annotations

from cowrie.shell.command import HoneyPotCommand

commands = {}


class Command_systemd_detect_virt(HoneyPotCommand):
    """
    systemd-detect-virt command - Detect virtualization
    Returns 'none' to make it appear as bare metal
    """

    def call(self) -> None:
        if "--help" in self.args or "-h" in self.args:
            self.write(
                """systemd-detect-virt [OPTIONS...]

Detect execution in a virtualized environment.

  -h --help             Show this help
     --version          Show package version
  -c --container        Only detect whether we are run in a container
  -v --vm               Only detect whether we are run in a VM
  -r --chroot           Detect whether we are run in a chroot() environment
  -q --quiet            Don't output anything, just set return value
     --list-all         List all known and detectable types
"""
            )
            return

        if "--version" in self.args:
            self.write("systemd 237\n")
            return

        if "--list-all" in self.args:
            self.write(
                """Known virtualization technologies (both VM, i.e. full hardware virtualization,
and container, i.e. shared kernel virtualization):
VM:
        qemu
        kvm
        zvm
        vmware
        microsoft
        oracle
        xen
        bochs
        uml
        parallels
        bhyve
        qnx
        acrn
Container:
        openvz
        lxc
        lxc-libvirt
        systemd-nspawn
        docker
        podman
        rkt
        wsl
"""
            )
            return

        quiet = "-q" in self.args or "--quiet" in self.args
        container_only = "-c" in self.args or "--container" in self.args
        vm_only = "-v" in self.args or "--vm" in self.args

        # Always report as "none" - not running in a virtual environment
        # This makes the honeypot appear as bare metal hardware
        if not quiet:
            self.write("none\n")

        # Exit code 1 means "not detected" which is what we want
        # (malware will think it's running on real hardware)


commands["/usr/bin/systemd-detect-virt"] = Command_systemd_detect_virt
commands["systemd-detect-virt"] = Command_systemd_detect_virt
