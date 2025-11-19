# Copyright (c) 2009 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

from __future__ import annotations

import random
import time

from cowrie.core import utils
from cowrie.shell.command import HoneyPotCommand

commands = {}


class Command_uptime(HoneyPotCommand):
    def call(self) -> None:
        # Generate realistic load averages based on session time
        # Use session ID as seed for consistency within a session
        session_seed = hash(self.protocol.getProtoTransport().transportId) % 10000
        random.seed(session_seed + int(time.time() / 300))  # Changes every 5 minutes

        # Generate realistic load values (typically between 0.0 and 2.0 for a normal system)
        load1 = random.uniform(0.01, 0.80)
        load5 = random.uniform(0.01, 0.60)
        load15 = random.uniform(0.01, 0.50)

        self.write(
            "{}  up {},  1 user,  load average: {:.2f}, {:.2f}, {:.2f}\n".format(
                time.strftime("%H:%M:%S"),
                utils.uptime(self.protocol.uptime()),
                load1,
                load5,
                load15
            )
        )


commands["/usr/bin/uptime"] = Command_uptime
commands["uptime"] = Command_uptime
