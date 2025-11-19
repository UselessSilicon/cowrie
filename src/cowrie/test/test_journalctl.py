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


class JournalctlCommandTest(unittest.TestCase):
    """Tests for journalctl command."""

    def setUp(self) -> None:
        self.proto = HoneyPotInteractiveProtocol(FakeAvatar(FakeServer()))
        self.tr = FakeTransport("", "31337")
        self.proto.makeConnection(self.tr)
        self.tr.clear()

    def tearDown(self) -> None:
        self.proto.connectionLost("test")

    def test_journalctl_help(self) -> None:
        """Test journalctl --help"""
        self.proto.lineReceived(b"journalctl --help\n")
        output = self.tr.value()
        self.assertIn(b"Query the journal", output)
        self.assertIn(b"Commands:", output)

    def test_journalctl_version(self) -> None:
        """Test journalctl --version"""
        self.proto.lineReceived(b"journalctl --version\n")
        output = self.tr.value()
        self.assertIn(b"systemd", output)

    def test_journalctl_default(self) -> None:
        """Test journalctl with no arguments"""
        self.proto.lineReceived(b"journalctl\n")
        output = self.tr.value()
        self.assertIn(b"-- Logs begin at", output)
        # Should show some log entries
        self.assertIn(b"localhost", output)

    def test_journalctl_lines(self) -> None:
        """Test journalctl -n (lines limit)"""
        self.proto.lineReceived(b"journalctl -n 5\n")
        output = self.tr.value()
        self.assertIn(b"-- Logs begin at", output)

    def test_journalctl_unit(self) -> None:
        """Test journalctl -u (unit filter)"""
        self.proto.lineReceived(b"journalctl -u sshd\n")
        output = self.tr.value()
        self.assertIn(b"-- Logs begin at", output)
        self.assertIn(b"sshd", output)

    def test_journalctl_kernel(self) -> None:
        """Test journalctl -k (kernel messages)"""
        self.proto.lineReceived(b"journalctl -k\n")
        output = self.tr.value()
        self.assertIn(b"-- Logs begin at", output)
        self.assertIn(b"kernel", output)
        self.assertIn(b"Linux version", output)

    def test_journalctl_reverse(self) -> None:
        """Test journalctl -r (reverse)"""
        self.proto.lineReceived(b"journalctl -r\n")
        output = self.tr.value()
        self.assertIn(b"-- Logs begin at", output)

    def test_journalctl_current_session(self) -> None:
        """Test journalctl shows current SSH session"""
        self.proto.lineReceived(b"journalctl -n 20\n")
        output = self.tr.value()
        # Should show SSH login for current session
        self.assertIn(b"Accepted password", output)
        self.assertIn(b"root", output)


if __name__ == "__main__":
    unittest.main()
