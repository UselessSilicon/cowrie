# Copyright (c) 2009-2014 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

"""
lsmod command - show the status of modules in the Linux kernel
Used by attackers to check for monitoring tools and before installing rootkits
"""

from __future__ import annotations

from cowrie.shell.command import HoneyPotCommand

commands = {}


class Command_lsmod(HoneyPotCommand):
    """
    lsmod command - show loaded kernel modules
    Used by attackers to:
    - Detect security monitoring tools
    - Check for existing rootkits
    - Prepare for rootkit installation
    """

    def call(self) -> None:
        """Execute lsmod command"""
        # Simulate realistic kernel module output
        # Based on a typical Linux system with common modules

        output = """Module                  Size  Used by
nf_conntrack_ipv4      16384  1
nf_defrag_ipv4         16384  1 nf_conntrack_ipv4
xt_conntrack           16384  1
nf_conntrack          139264  2 xt_conntrack,nf_conntrack_ipv4
libcrc32c              16384  1 nf_conntrack
ipt_MASQUERADE         16384  1
nf_nat_masquerade_ipv4    16384  1 ipt_MASQUERADE
iptable_nat            16384  1
nf_nat_ipv4            16384  1 iptable_nat
nf_nat                 28672  2 nf_nat_ipv4,nf_nat_masquerade_ipv4
iptable_filter         16384  1
ip_tables              24576  2 iptable_nat,iptable_filter
x_tables               40960  4 xt_conntrack,ipt_MASQUERADE,iptable_filter,ip_tables
veth                   24576  0
xt_CHECKSUM            16384  1
iptable_mangle         16384  1
ipt_REJECT             16384  1
nf_reject_ipv4         16384  1 ipt_REJECT
xt_tcpudp              16384  5
bridge                159744  0
stp                    16384  1 bridge
llc                    16384  2 bridge,stp
ip6table_filter        16384  1
ip6_tables             28672  1 ip6table_filter
aufs                  253952  0
overlay                49152  0
nfsd                  348160  1
auth_rpcgss            61440  1 nfsd
nfs_acl                16384  1 nfsd
lockd                  94208  1 nfsd
grace                  16384  2 nfsd,lockd
sunrpc                364544  6 nfsd,auth_rpcgss,lockd,nfs_acl
fscache                65536  1 nfsd
binfmt_misc            20480  1
crct10dif_pclmul       16384  0
crc32_pclmul           16384  0
ghash_clmulni_intel    16384  0
aesni_intel           200704  0
aes_x86_64             20480  1 aesni_intel
lrw                    16384  1 aesni_intel
gf128mul               16384  1 lrw
glue_helper            16384  1 aesni_intel
ablk_helper            16384  1 aesni_intel
cryptd                 24576  3 ghash_clmulni_intel,aesni_intel,ablk_helper
joydev                 20480  0
input_leds             16384  0
serio_raw              16384  0
virtio_balloon         20480  0
i2c_piix4              24576  0
8250_fintek            16384  0
mac_hid                16384  0
ib_iser                49152  0
rdma_cm                61440  1 ib_iser
iw_cm                  45056  1 rdma_cm
ib_cm                  49152  1 rdma_cm
ib_core               229376  4 rdma_cm,ib_iser,iw_cm,ib_cm
iscsi_tcp              20480  0
libiscsi_tcp           24576  1 iscsi_tcp
libiscsi               53248  3 libiscsi_tcp,iscsi_tcp,ib_iser
scsi_transport_iscsi    98304  4 iscsi_tcp,ib_iser,libiscsi
autofs4                40960  2
btrfs                1130496  0
xor                    24576  1 btrfs
raid6_pq              114688  1 btrfs
hid_generic            16384  0
usbhid                 49152  0
hid                   122880  2 hid_generic,usbhid
psmouse               143360  0
virtio_net             45056  0
virtio_blk             20480  2
virtio_pci             24576  0
virtio_ring            28672  5 virtio_blk,virtio_net,virtio_pci,virtio_balloon
virtio                 16384  5 virtio_blk,virtio_net,virtio_pci,virtio_balloon,virtio_ring
pata_acpi              16384  0
floppy                 69632  0
"""
        self.write(output)


commands["/sbin/lsmod"] = Command_lsmod
commands["lsmod"] = Command_lsmod
