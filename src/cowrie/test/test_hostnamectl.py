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


class HostnamectlCommandTest(unittest.TestCase):
    """Tests for hostnamectl command."""

    def setUp(self) -> None:
        self.proto = HoneyPotInteractiveProtocol(FakeAvatar(FakeServer()))
        self.tr = FakeTransport("", "31337")
        self.proto.makeConnection(self.tr)
        self.tr.clear()

    def tearDown(self) -> None:
        self.proto.connectionLost("test")

    def test_hostnamectl_help(self) -> None:
        """Test hostnamectl --help"""
        self.proto.lineReceived(b"hostnamectl --help\n")
        output = self.tr.value()
        self.assertIn(b"Query or change system hostname", output)
        self.assertIn(b"Commands:", output)

    def test_hostnamectl_version(self) -> None:
        """Test hostnamectl --version"""
        self.proto.lineReceived(b"hostnamectl --version\n")
        output = self.tr.value()
        self.assertIn(b"systemd", output)

    def test_hostnamectl_status(self) -> None:
        """Test hostnamectl status"""
        self.proto.lineReceived(b"hostnamectl status\n")
        output = self.tr.value()
        self.assertIn(b"Static hostname:", output)
        self.assertIn(b"Operating System:", output)
        self.assertIn(b"Kernel:", output)
        self.assertIn(b"Architecture:", output)

    def test_hostnamectl_default(self) -> None:
        """Test hostnamectl with no arguments (shows status)"""
        self.proto.lineReceived(b"hostnamectl\n")
        output = self.tr.value()
        self.assertIn(b"Static hostname:", output)
        self.assertIn(b"Operating System:", output)

    def test_hostnamectl_set_hostname_requires_root(self) -> None:
        """Test hostnamectl set-hostname requires root"""
        # Create non-root user
        avatar = FakeAvatar(FakeServer())
        avatar.username = "user"
        proto = HoneyPotInteractiveProtocol(avatar)
        tr = FakeTransport("", "31337")
        proto.makeConnection(tr)
        tr.clear()

        proto.lineReceived(b"hostnamectl set-hostname newhostname\n")
        output = tr.value()
        self.assertIn(b"Access denied", output)

        proto.connectionLost("test")

    def test_hostnamectl_set_hostname(self) -> None:
        """Test hostnamectl set-hostname (succeeds silently for root)"""
        self.proto.lineReceived(b"hostnamectl set-hostname testhost\n")
        # Should succeed silently
        self.assertEqual(self.tr.value(), PROMPT)
        # Hostname should be changed
        self.assertEqual(self.proto.hostname, "testhost")


if __name__ == "__main__":
    unittest.main()
