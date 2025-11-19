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


class SsCommandTest(unittest.TestCase):
    """Tests for ss command."""

    def setUp(self) -> None:
        self.proto = HoneyPotInteractiveProtocol(FakeAvatar(FakeServer()))
        self.tr = FakeTransport("", "31337")
        self.proto.makeConnection(self.tr)
        self.tr.clear()

    def tearDown(self) -> None:
        self.proto.connectionLost("test")

    def test_ss_help(self) -> None:
        """Test ss --help"""
        self.proto.lineReceived(b"ss --help\n")
        output = self.tr.value()
        self.assertIn(b"Usage:", output)
        self.assertIn(b"OPTIONS", output)

    def test_ss_version(self) -> None:
        """Test ss --version"""
        self.proto.lineReceived(b"ss --version\n")
        output = self.tr.value()
        self.assertIn(b"ss utility", output)
        self.assertIn(b"iproute2", output)

    def test_ss_summary(self) -> None:
        """Test ss -s (summary)"""
        self.proto.lineReceived(b"ss -s\n")
        output = self.tr.value()
        self.assertIn(b"Total:", output)
        self.assertIn(b"TCP:", output)
        self.assertIn(b"UDP:", output)

    def test_ss_tcp(self) -> None:
        """Test ss -t (TCP only)"""
        self.proto.lineReceived(b"ss -t\n")
        output = self.tr.value()
        self.assertIn(b"State", output)
        self.assertIn(b"Recv-Q", output)
        self.assertIn(b"Send-Q", output)
        self.assertIn(b"ESTAB", output)

    def test_ss_tcp_listen(self) -> None:
        """Test ss -tl (TCP listening)"""
        self.proto.lineReceived(b"ss -tl\n")
        output = self.tr.value()
        self.assertIn(b"LISTEN", output)

    def test_ss_all_numeric(self) -> None:
        """Test ss -tan (TCP all numeric)"""
        self.proto.lineReceived(b"ss -tan\n")
        output = self.tr.value()
        self.assertIn(b"State", output)
        self.assertIn(b"ESTAB", output)
        # Should show numeric ports
        self.assertIn(b":", output)

    def test_ss_tcp_with_processes(self) -> None:
        """Test ss -tap (TCP with process info)"""
        self.proto.lineReceived(b"ss -tap\n")
        output = self.tr.value()
        self.assertIn(b"Process", output)
        self.assertIn(b"users:", output)
        self.assertIn(b"sshd", output)

    def test_ss_combined_options(self) -> None:
        """Test ss -tuln (TCP+UDP, listening, numeric)"""
        self.proto.lineReceived(b"ss -tuln\n")
        output = self.tr.value()
        self.assertIn(b"State", output)
        # Should show both TCP and UDP
        self.assertIn(b"LISTEN", output)

    def test_ss_default(self) -> None:
        """Test ss with no arguments"""
        self.proto.lineReceived(b"ss\n")
        output = self.tr.value()
        # Default shows established connections
        self.assertIn(b"State", output)


if __name__ == "__main__":
    unittest.main()
