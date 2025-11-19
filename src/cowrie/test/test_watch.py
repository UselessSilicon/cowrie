# Copyright (c) 2025 Cowrie Project
# See LICENSE for details.

from __future__ import annotations

import os
import unittest

from cowrie.shell.protocol import HoneyPotInteractiveProtocol
from cowrie.test.fake_server import FakeAvatar, FakeServer
from cowrie.test.fake_transport import FakeTransport

os.environ["COWRIE_HONEYPOT_DATA_PATH"] = "data"
os.environ["COWRIE_SHELL_FILESYSTEM"] = "src/cowrie/data/fs.pickle"

PROMPT = b"root@unitTest:~# "


class WatchCommandTest(unittest.TestCase):
    """Tests for watch command."""

    def setUp(self) -> None:
        self.proto = HoneyPotInteractiveProtocol(FakeAvatar(FakeServer()))
        self.tr = FakeTransport("", "31337")
        self.proto.makeConnection(self.tr)
        self.tr.clear()

    def tearDown(self) -> None:
        self.proto.connectionLost("test")

    def test_watch_help(self) -> None:
        """Test watch --help"""
        self.proto.lineReceived(b"watch --help\n")
        output = self.tr.value()
        self.assertIn(b"Usage:", output)
        self.assertIn(b"Options:", output)

    def test_watch_version(self) -> None:
        """Test watch --version"""
        self.proto.lineReceived(b"watch --version\n")
        output = self.tr.value()
        self.assertIn(b"watch from procps-ng", output)

    def test_watch_no_command(self) -> None:
        """Test watch with no command"""
        self.proto.lineReceived(b"watch\n")
        output = self.tr.value()
        self.assertIn(b"no command specified", output)

    def test_watch_with_command(self) -> None:
        """Test watch with command"""
        self.proto.lineReceived(b"watch date\n")
        output = self.tr.value()
        self.assertIn(b"Every", output)
        self.assertIn(b"date", output)

    def test_watch_interval(self) -> None:
        """Test watch -n interval"""
        self.proto.lineReceived(b"watch -n 5 ps\n")
        output = self.tr.value()
        self.assertIn(b"Every 5", output)
        self.assertIn(b"ps", output)

    def test_watch_differences(self) -> None:
        """Test watch -d (differences)"""
        self.proto.lineReceived(b"watch -d ps\n")
        output = self.tr.value()
        self.assertIn(b"ps", output)


if __name__ == "__main__":
    unittest.main()
