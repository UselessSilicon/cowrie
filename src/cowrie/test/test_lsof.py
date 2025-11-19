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


class LsofCommandTest(unittest.TestCase):
    """Tests for lsof command."""

    def setUp(self) -> None:
        self.proto = HoneyPotInteractiveProtocol(FakeAvatar(FakeServer()))
        self.tr = FakeTransport("", "31337")
        self.proto.makeConnection(self.tr)
        self.tr.clear()

    def tearDown(self) -> None:
        self.proto.connectionLost("test")

    def test_lsof_help(self) -> None:
        """Test lsof --help"""
        self.proto.lineReceived(b"lsof --help\n")
        output = self.tr.value()
        self.assertIn(b"lsof", output)
        self.assertIn(b"usage:", output)

    def test_lsof_version(self) -> None:
        """Test lsof --version"""
        self.proto.lineReceived(b"lsof --version\n")
        output = self.tr.value()
        self.assertIn(b"lsof version", output)
        self.assertIn(b"revision:", output)

    def test_lsof_default(self) -> None:
        """Test lsof with no arguments"""
        self.proto.lineReceived(b"lsof\n")
        output = self.tr.value()
        self.assertIn(b"COMMAND", output)
        self.assertIn(b"PID", output)
        self.assertIn(b"USER", output)
        self.assertIn(b"FD", output)
        self.assertIn(b"TYPE", output)
        self.assertIn(b"NAME", output)
        # Should show some processes
        self.assertIn(b"sshd", output)

    def test_lsof_internet(self) -> None:
        """Test lsof -i (internet connections)"""
        self.proto.lineReceived(b"lsof -i\n")
        output = self.tr.value()
        self.assertIn(b"COMMAND", output)
        # Should show SSH connection
        self.assertIn(b"sshd", output)
        self.assertIn(b"TCP", output)
        self.assertIn(b"ESTABLISHED", output)

    def test_lsof_tcp(self) -> None:
        """Test lsof -iTCP"""
        self.proto.lineReceived(b"lsof -iTCP\n")
        output = self.tr.value()
        self.assertIn(b"TCP", output)
        # Should not show UDP
        self.assertNotIn(b"UDP", output)

    def test_lsof_tcp_lowercase(self) -> None:
        """Test lsof -itcp (lowercase)"""
        self.proto.lineReceived(b"lsof -itcp\n")
        output = self.tr.value()
        self.assertIn(b"TCP", output)

    def test_lsof_numeric(self) -> None:
        """Test lsof -n (numeric)"""
        self.proto.lineReceived(b"lsof -n -i\n")
        output = self.tr.value()
        # Should show IP addresses
        self.assertIn(b".", output)  # IP address contains dots

    def test_lsof_listening(self) -> None:
        """Test lsof -l (listening)"""
        self.proto.lineReceived(b"lsof -l -iTCP\n")
        output = self.tr.value()
        self.assertIn(b"LISTEN", output)

    def test_lsof_shows_files(self) -> None:
        """Test lsof shows file descriptors"""
        self.proto.lineReceived(b"lsof\n")
        output = self.tr.value()
        # Should show file descriptors
        self.assertIn(b"/dev/pts", output)
        # Should show various FD types
        self.assertIn(b"REG", output)  # Regular files
        self.assertIn(b"CHR", output)  # Character devices

    def test_lsof_shows_current_user_files(self) -> None:
        """Test lsof shows current user's files"""
        self.proto.lineReceived(b"lsof\n")
        output = self.tr.value()
        # Should show root user's processes
        self.assertIn(b"root", output)


if __name__ == "__main__":
    unittest.main()
