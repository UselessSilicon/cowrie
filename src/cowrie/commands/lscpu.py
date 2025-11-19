# Copyright (c) 2009-2014 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

"""
lscpu command - display CPU architecture information
Commonly used by cryptominers to assess CPU resources
"""

from __future__ import annotations

import getopt

from cowrie.shell.command import HoneyPotCommand

commands = {}


class Command_lscpu(HoneyPotCommand):
    """
    lscpu command - display CPU architecture information
    Critical for cryptominer reconnaissance to assess mining capability
    """

    def call(self) -> None:
        """Execute lscpu command"""
        # Parse options
        extended = False
        parse_mode = False

        try:
            optlist, args = getopt.getopt(self.args, "ep")
        except getopt.GetoptError:
            pass
        else:
            for opt, arg in optlist:
                if opt == "-e":
                    extended = True
                elif opt == "-p":
                    parse_mode = True

        if parse_mode:
            # Machine-parseable format
            self.write("# The following is the parsable format, which can be fed to other\n")
            self.write("# programs. Each different item in every column has an unique ID\n")
            self.write("# starting from zero.\n")
            self.write("# CPU,Core,Socket,Node\n")
            self.write("0,0,0,0\n")
            self.write("1,1,0,0\n")
            return

        if extended:
            # Extended CPU list format
            self.write("CPU NODE SOCKET CORE L1d:L1i:L2:L3 ONLINE\n")
            self.write("0   0    0      0    0:0:0:0       yes\n")
            self.write("1   0    0      1    1:1:1:0       yes\n")
            return

        # Standard output format - realistic values for a typical VPS
        output = """Architecture:          x86_64
CPU op-mode(s):        32-bit, 64-bit
Byte Order:            Little Endian
CPU(s):                2
On-line CPU(s) list:   0,1
Thread(s) per core:    1
Core(s) per socket:    2
Socket(s):             1
NUMA node(s):          1
Vendor ID:             GenuineIntel
CPU family:            6
Model:                 85
Model name:            Intel(R) Xeon(R) CPU @ 2.30GHz
Stepping:              7
CPU MHz:               2300.000
BogoMIPS:              4600.00
Hypervisor vendor:     KVM
Virtualization type:   full
L1d cache:             32K
L1i cache:             32K
L2 cache:              256K
L3 cache:              25344K
NUMA node0 CPU(s):     0,1
Flags:                 fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush mmx fxsr sse sse2 ss ht syscall nx pdpe1gb rdtscp lm constant_tsc rep_good nopl xtopology nonstop_tsc cpuid tsc_known_freq pni pclmulqdq ssse3 fma cx16 pcid sse4_1 sse4_2 x2apic movbe popcnt aes xsave avx f16c rdrand hypervisor lahf_lm abm 3dnowprefetch invpcid_single pti ssbd ibrs ibpb stibp fsgsbase tsc_adjust bmi1 hle avx2 smep bmi2 erms invpcid rtm mpx avx512f avx512dq rdseed adx smap clflushopt clwb avx512cd avx512bw avx512vl xsaveopt xsavec xgetbv1 xsaves arat md_clear arch_capabilities
"""
        self.write(output)


commands["/usr/bin/lscpu"] = Command_lscpu
commands["lscpu"] = Command_lscpu
