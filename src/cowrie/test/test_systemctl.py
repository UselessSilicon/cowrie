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


class SystemctlCommandTest(unittest.TestCase):
    """Tests for systemctl command."""

    def setUp(self) -> None:
        self.proto = HoneyPotInteractiveProtocol(FakeAvatar(FakeServer()))
        self.tr = FakeTransport("", "31337")
        self.proto.makeConnection(self.tr)
        self.tr.clear()

    def tearDown(self) -> None:
        self.proto.connectionLost("test")

    def test_systemctl_help(self) -> None:
        """Test systemctl --help"""
        self.proto.lineReceived(b"systemctl --help\n")
        output = self.tr.value()
        self.assertIn(b"Unit Commands:", output)
        self.assertIn(b"list-units", output)

    def test_systemctl_version(self) -> None:
        """Test systemctl --version"""
        self.proto.lineReceived(b"systemctl --version\n")
        output = self.tr.value()
        self.assertIn(b"systemd", output)

    def test_systemctl_list_units(self) -> None:
        """Test systemctl list-units"""
        self.proto.lineReceived(b"systemctl list-units\n")
        output = self.tr.value()
        self.assertIn(b"UNIT", output)
        self.assertIn(b"LOAD", output)
        self.assertIn(b"ACTIVE", output)
        self.assertIn(b"sshd.service", output)
        self.assertIn(b"loaded units listed", output)

    def test_systemctl_status_ssh(self) -> None:
        """Test systemctl status sshd"""
        self.proto.lineReceived(b"systemctl status sshd\n")
        output = self.tr.value()
        self.assertIn(b"sshd.service", output)
        self.assertIn(b"OpenSSH", output)
        self.assertIn(b"Active:", output)
        self.assertIn(b"Loaded:", output)

    def test_systemctl_status_nonexistent(self) -> None:
        """Test systemctl status for nonexistent service"""
        self.proto.lineReceived(b"systemctl status fakeservice\n")
        output = self.tr.value()
        self.assertIn(b"could not be found", output)

    def test_systemctl_is_active(self) -> None:
        """Test systemctl is-active"""
        self.proto.lineReceived(b"systemctl is-active sshd\n")
        output = self.tr.value()
        self.assertIn(b"active", output)

    def test_systemctl_is_enabled(self) -> None:
        """Test systemctl is-enabled"""
        self.proto.lineReceived(b"systemctl is-enabled sshd\n")
        output = self.tr.value()
        self.assertIn(b"enabled", output)

    def test_systemctl_start_requires_root(self) -> None:
        """Test systemctl start requires root"""
        # Create non-root user
        avatar = FakeAvatar(FakeServer())
        avatar.username = "user"
        proto = HoneyPotInteractiveProtocol(avatar)
        tr = FakeTransport("", "31337")
        proto.makeConnection(tr)
        tr.clear()

        proto.lineReceived(b"systemctl start apache2\n")
        output = tr.value()
        self.assertIn(b"Access denied", output)

        proto.connectionLost("test")

    def test_systemctl_daemon_reload(self) -> None:
        """Test systemctl daemon-reload (succeeds silently for root)"""
        self.proto.lineReceived(b"systemctl daemon-reload\n")
        # Should succeed silently for root
        self.assertEqual(self.tr.value(), PROMPT)


if __name__ == "__main__":
    unittest.main()
