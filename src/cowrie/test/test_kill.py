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


class KillCommandTest(unittest.TestCase):
    """Tests for kill command."""

    def setUp(self) -> None:
        self.proto = HoneyPotInteractiveProtocol(FakeAvatar(FakeServer()))
        self.tr = FakeTransport("", "31337")
        self.proto.makeConnection(self.tr)
        self.tr.clear()

    def tearDown(self) -> None:
        self.proto.connectionLost("test")

    def test_kill_no_args(self) -> None:
        """Test kill with no arguments shows usage"""
        self.proto.lineReceived(b"kill\n")
        self.assertIn(b"usage:", self.tr.value())

    def test_kill_help(self) -> None:
        """Test kill --help"""
        self.proto.lineReceived(b"kill --help\n")
        self.assertIn(b"Usage:", self.tr.value())
        self.assertIn(b"send signal", self.tr.value())

    def test_kill_version(self) -> None:
        """Test kill --version"""
        self.proto.lineReceived(b"kill --version\n")
        self.assertIn(b"kill from util-linux", self.tr.value())

    def test_kill_list_signals(self) -> None:
        """Test kill -l lists signals"""
        self.proto.lineReceived(b"kill -l\n")
        self.assertIn(b"SIGHUP", self.tr.value())
        self.assertIn(b"SIGKILL", self.tr.value())
        self.assertIn(b"SIGTERM", self.tr.value())

    def test_kill_valid_pid(self) -> None:
        """Test kill with valid high PID succeeds silently"""
        self.proto.lineReceived(b"kill 1234\n")
        # Success means no error output, just prompt
        self.assertEqual(self.tr.value(), PROMPT)

    def test_kill_pid_with_signal(self) -> None:
        """Test kill -9 with PID"""
        self.proto.lineReceived(b"kill -9 5678\n")
        # Success means no error output, just prompt
        self.assertEqual(self.tr.value(), PROMPT)

    def test_kill_signal_format(self) -> None:
        """Test kill -SIGTERM format"""
        self.proto.lineReceived(b"kill -SIGTERM 5678\n")
        # Success means no error output
        self.assertEqual(self.tr.value(), PROMPT)

    def test_kill_init_denied(self) -> None:
        """Test kill PID 1 (init) is denied"""
        self.proto.lineReceived(b"kill 1\n")
        self.assertIn(b"Operation not permitted", self.tr.value())

    def test_kill_system_process_denied(self) -> None:
        """Test killing low PID (system process) is denied"""
        self.proto.lineReceived(b"kill 100\n")
        self.assertIn(b"Operation not permitted", self.tr.value())

    def test_kill_invalid_pid(self) -> None:
        """Test kill with invalid PID format"""
        self.proto.lineReceived(b"kill abc\n")
        self.assertIn(b"invalid process id", self.tr.value())

    def test_kill_negative_pid(self) -> None:
        """Test kill with negative PID"""
        self.proto.lineReceived(b"kill -5\n")
        # -5 could be interpreted as signal 5, needs a PID after
        # OR negative PID which should fail
        self.assertIn(b"No such process", self.tr.value())

    def test_kill_with_signal_option(self) -> None:
        """Test kill -s SIGKILL format"""
        self.proto.lineReceived(b"kill -s SIGKILL 9999\n")
        # Should succeed silently
        self.assertEqual(self.tr.value(), PROMPT)

    def test_kill_multiple_pids(self) -> None:
        """Test killing multiple PIDs"""
        self.proto.lineReceived(b"kill 1000 2000 3000\n")
        # Should succeed silently for all valid PIDs
        self.assertEqual(self.tr.value(), PROMPT)


if __name__ == "__main__":
    unittest.main()
