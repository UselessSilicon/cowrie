# Copyright (c) 2009-2014 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

"""
id command - print user identity
One of the most common first commands run by attackers
"""

from __future__ import annotations

import getopt

from cowrie.shell.command import HoneyPotCommand

commands = {}


class Command_id(HoneyPotCommand):
    """
    id command - print real and effective user and group IDs
    Extremely common reconnaissance command - often the first command attackers run
    """

    def call(self) -> None:
        """Execute id command"""
        # Parse options
        show_user = False
        show_group = False
        show_groups = False
        show_name = False
        show_real = False

        try:
            optlist, args = getopt.getopt(self.args, "ugnGrZ")
        except getopt.GetoptError as err:
            self.write(f"id: {err}\n")
            self.write("Try 'id --help' for more information.\n")
            return

        for opt, arg in optlist:
            if opt == "-u":
                show_user = True
            elif opt == "-g":
                show_group = True
            elif opt == "-G":
                show_groups = True
            elif opt == "-n":
                show_name = True
            elif opt == "-r":
                show_real = True
            elif opt == "-Z":
                # SELinux context
                self.write("unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023\n")
                return

        # Get username from protocol
        username = self.protocol.user.username

        # Determine UID/GID based on username
        if username == "root":
            uid = 0
            gid = 0
            groups_list = [(0, "root")]
        else:
            uid = 1000
            gid = 1000
            groups_list = [(1000, username), (4, "adm"), (24, "cdrom"), (27, "sudo"), (30, "dip"), (46, "plugdev"), (108, "lxd")]

        # Handle specific options
        if show_user:
            if show_name:
                self.write(f"{username}\n")
            else:
                self.write(f"{uid}\n")
            return

        if show_group:
            if show_name:
                self.write(f"{groups_list[0][1]}\n")
            else:
                self.write(f"{gid}\n")
            return

        if show_groups:
            if show_name:
                group_names = " ".join([group[1] for group in groups_list])
                self.write(f"{group_names}\n")
            else:
                group_ids = " ".join([str(group[0]) for group in groups_list])
                self.write(f"{group_ids}\n")
            return

        # Default format - show everything
        groups_str = " ".join([f"{gid}({name})" for gid, name in groups_list])
        self.write(f"uid={uid}({username}) gid={gid}({groups_list[0][1]}) groups={groups_str}\n")


commands["/usr/bin/id"] = Command_id
commands["id"] = Command_id
