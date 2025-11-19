# Copyright (c) 2009-2014 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

"""
dmidecode command - DMI table decoder (SMBIOS/DMI)
"""

from __future__ import annotations

from cowrie.shell.command import HoneyPotCommand

commands = {}


class Command_dmidecode(HoneyPotCommand):
    """
    dmidecode command - Display hardware information from BIOS
    Used by malware to detect virtualization
    """

    def call(self) -> None:
        # Check for help or version
        if "--help" in self.args or "-h" in self.args:
            self.write(
                """Usage: dmidecode [OPTIONS]
Options are:
 -d, --dev-mem FILE     Read memory from device FILE (default: /dev/mem)
 -h, --help             Display this help text and exit
 -q, --quiet            Less verbose output
 -s, --string KEYWORD   Only display the value of the given DMI string
 -t, --type TYPE        Only display the entries of given type
 -u, --dump             Do not decode the entries
     --dump-bin FILE    Dump the DMI data to a binary file
     --from-dump FILE   Read the DMI data from a binary file
 -V, --version          Display the version and exit
"""
            )
            return

        if "--version" in self.args or "-V" in self.args:
            self.write("dmidecode 3.2\n")
            return

        # Check for specific string queries
        if "-s" in self.args or "--string" in self.args:
            try:
                idx = self.args.index("-s") if "-s" in self.args else self.args.index("--string")
                if idx + 1 < len(self.args):
                    keyword = self.args[idx + 1]
                    self.output_string(keyword)
                    return
            except (ValueError, IndexError):
                pass

        # Output realistic DMI information that doesn't look like a VM
        self.write("# dmidecode 3.2\n")
        self.write("Getting SMBIOS data from sysfs.\n")
        self.write("SMBIOS 2.8 present.\n\n")

        # BIOS Information
        self.write("Handle 0x0000, DMI type 0, 24 bytes\n")
        self.write("BIOS Information\n")
        self.write("\tVendor: American Megatrends Inc.\n")
        self.write("\tVersion: 5.6.5\n")
        self.write("\tRelease Date: 07/25/2018\n")
        self.write("\tAddress: 0xF0000\n")
        self.write("\tRuntime Size: 64 kB\n")
        self.write("\tROM Size: 8192 kB\n")
        self.write("\tCharacteristics:\n")
        self.write("\t\tPCI is supported\n")
        self.write("\t\tBIOS is upgradeable\n")
        self.write("\t\tBIOS shadowing is allowed\n")
        self.write("\t\tBoot from CD is supported\n")
        self.write("\t\tSelectable boot is supported\n")
        self.write("\t\tEDD is supported\n")
        self.write("\t\t5.25\"/1.2 MB floppy services are supported (int 13h)\n")
        self.write("\t\t3.5\"/720 kB floppy services are supported (int 13h)\n")
        self.write("\t\t3.5\"/2.88 MB floppy services are supported (int 13h)\n")
        self.write("\t\tPrint screen service is supported (int 5h)\n")
        self.write("\t\t8042 keyboard services are supported (int 9h)\n")
        self.write("\t\tSerial services are supported (int 14h)\n")
        self.write("\t\tPrinter services are supported (int 17h)\n")
        self.write("\t\tACPI is supported\n")
        self.write("\t\tUSB legacy is supported\n")
        self.write("\t\tBIOS boot specification is supported\n")
        self.write("\t\tTargeted content distribution is supported\n")
        self.write("\t\tUEFI is supported\n")
        self.write("\tBIOS Revision: 5.6\n\n")

        # System Information
        self.write("Handle 0x0001, DMI type 1, 27 bytes\n")
        self.write("System Information\n")
        self.write("\tManufacturer: Supermicro\n")
        self.write("\tProduct Name: X10SLL-F\n")
        self.write("\tVersion: 0123456789\n")
        self.write("\tSerial Number: A12345678\n")
        self.write("\tUUID: 00112233-4455-6677-8899-AABBCCDDEEFF\n")
        self.write("\tWake-up Type: Power Switch\n")
        self.write("\tSKU Number: To be filled by O.E.M.\n")
        self.write("\tFamily: To be filled by O.E.M.\n\n")

        # Processor Information
        self.write("Handle 0x0004, DMI type 4, 42 bytes\n")
        self.write("Processor Information\n")
        self.write("\tSocket Designation: CPU1\n")
        self.write("\tType: Central Processor\n")
        self.write("\tFamily: Xeon\n")
        self.write("\tManufacturer: Intel(R) Corporation\n")
        self.write("\tID: F2 06 03 00 FF FB EB BF\n")
        self.write("\tSignature: Type 0, Family 6, Model 63, Stepping 2\n")
        self.write("\tFlags:\n")
        self.write("\t\tFPU (Floating-point unit on-chip)\n")
        self.write("\t\tVME (Virtual mode extension)\n")
        self.write("\t\tDE (Debugging extension)\n")
        self.write("\t\tPSE (Page size extension)\n")
        self.write("\t\tTSC (Time stamp counter)\n")
        self.write("\t\tMSR (Model specific registers)\n")
        self.write("\t\tPAE (Physical address extension)\n")
        self.write("\tVersion: Intel(R) Xeon(R) CPU E5-2620 v3 @ 2.40GHz\n")
        self.write("\tVoltage: 1.8 V\n")
        self.write("\tExternal Clock: 100 MHz\n")
        self.write("\tMax Speed: 4000 MHz\n")
        self.write("\tCurrent Speed: 2400 MHz\n")
        self.write("\tStatus: Populated, Enabled\n")
        self.write("\tUpgrade: Socket LGA2011-3\n")
        self.write("\tCore Count: 6\n")
        self.write("\tCore Enabled: 6\n")
        self.write("\tThread Count: 12\n\n")

    def output_string(self, keyword: str) -> None:
        """Output specific DMI string"""
        strings = {
            "bios-vendor": "American Megatrends Inc.\n",
            "bios-version": "5.6.5\n",
            "bios-release-date": "07/25/2018\n",
            "system-manufacturer": "Supermicro\n",
            "system-product-name": "X10SLL-F\n",
            "system-version": "0123456789\n",
            "system-serial-number": "A12345678\n",
            "system-uuid": "00112233-4455-6677-8899-AABBCCDDEEFF\n",
            "baseboard-manufacturer": "Supermicro\n",
            "baseboard-product-name": "X10SLL-F\n",
            "baseboard-version": "1.01\n",
            "baseboard-serial-number": "VM0123456789\n",
            "chassis-manufacturer": "Supermicro\n",
            "chassis-type": "Rack Mount Chassis\n",
            "chassis-version": "0123456789\n",
            "chassis-serial-number": "C12345678\n",
            "processor-family": "Xeon\n",
            "processor-manufacturer": "Intel(R) Corporation\n",
            "processor-version": "Intel(R) Xeon(R) CPU E5-2620 v3 @ 2.40GHz\n",
        }

        if keyword in strings:
            self.write(strings[keyword])
        else:
            # Return empty for unknown keywords
            pass


commands["/usr/sbin/dmidecode"] = Command_dmidecode
commands["dmidecode"] = Command_dmidecode
