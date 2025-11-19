# CLAUDE.md - Cowrie Honeypot Development Guide for AI Assistants

**Last Updated**: 2025-11-19
**Project**: Cowrie SSH/Telnet Honeypot
**Repository**: https://github.com/cowrie/cowrie
**Documentation**: https://docs.cowrie.org/

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Codebase Structure](#codebase-structure)
3. [Architecture](#architecture)
4. [Development Setup](#development-setup)
5. [Development Workflow](#development-workflow)
6. [Testing](#testing)
7. [Code Conventions](#code-conventions)
8. [Key Patterns](#key-patterns)
9. [Working with Commands](#working-with-commands)
10. [Working with Output Plugins](#working-with-output-plugins)
11. [Important Files](#important-files)
12. [Common Tasks](#common-tasks)
13. [Debugging](#debugging)
14. [Security Considerations](#security-considerations)

---

## Project Overview

### What is Cowrie?

Cowrie is a **medium to high interaction SSH and Telnet honeypot** designed to log brute force attacks and shell interaction performed by attackers. It runs in two modes:

1. **Shell Mode (Default)**: Emulates a full UNIX system in Python
2. **Proxy Mode**: Functions as an SSH/Telnet proxy to observe attacker behavior on real systems or VM pools

### Key Features

- Full SSH and Telnet server implementation
- Emulated UNIX shell with 50+ commands
- Virtual filesystem (Debian 5.0-like)
- File upload/download capture (wget, curl, SFTP, SCP)
- Session recording in UML-compatible format
- 30+ output plugins for logging/integration
- JSON logging for SIEM integration
- Docker deployment support

### Technology Stack

- **Language**: Python 3.10+
- **Framework**: Twisted (event-driven networking)
- **Build System**: setuptools with setuptools-scm
- **Testing**: unittest, tox
- **Type Checking**: mypy, pyright, pyre-check
- **Linting**: ruff, pylint
- **Code Formatting**: black, isort

---

## Codebase Structure

### Root Directory Layout

```
/
├── bin/                    # Utility scripts
├── docker/                 # Docker configuration
├── docs/                   # Documentation (Sphinx)
├── etc/                    # Configuration files
│   ├── cowrie.cfg.dist     # Default config (DO NOT EDIT)
│   └── cowrie.cfg          # User config (overrides)
├── honeyfs/                # Virtual filesystem contents
│   ├── etc/                # System files (/etc/passwd, /etc/motd)
│   └── proc/               # /proc filesystem files
├── src/                    # Main source code
│   ├── cowrie/             # Core package
│   ├── twisted/            # Twisted plugins
│   └── backend_pool/       # VM pool backend
├── var/                    # Runtime data
│   ├── log/cowrie/         # Log files
│   ├── lib/cowrie/         # TTY logs, downloads
│   └── run/                # PID files
├── pyproject.toml          # Project configuration
├── requirements.txt        # Core dependencies
├── requirements-output.txt # Output plugin dependencies
├── Makefile                # Developer tasks
└── tox.ini                 # Test automation (in pyproject.toml)
```

### Source Code Structure (`src/cowrie/`)

```
src/cowrie/
├── commands/          # 50+ emulated shell commands
├── core/              # Core functionality
│   ├── config.py      # Configuration management
│   ├── realm.py       # Twisted realm (authentication)
│   ├── checkers.py    # Password/key authentication
│   ├── output.py      # Output plugin base class
│   ├── auth.py        # Authentication logic
│   ├── credentials.py # Credential handling
│   ├── artifact.py    # File artifact storage
│   ├── ttylog.py      # TTY session recording
│   └── uuid.py        # Sensor UUID generation
├── data/              # Static data files
│   ├── fs.pickle      # Virtual filesystem metadata
│   └── txtcmds/       # Simple text-based commands
├── insults/           # Terminal handling
├── output/            # 30+ output plugins
├── pool_interface/    # VM pool interface
├── python/            # Python utilities
├── scripts/           # CLI utilities
│   ├── cowrie.py      # Main entry point
│   ├── fsctl.py       # Filesystem control
│   ├── playlog.py     # TTY replay utility
│   ├── createfs.py    # Filesystem creation
│   └── asciinema.py   # Asciinema conversion
├── shell/             # Shell emulation
│   ├── honeypot.py    # Main shell logic
│   ├── protocol.py    # Protocol handling
│   ├── command.py     # Command base class
│   ├── fs.py          # Virtual filesystem
│   ├── session.py     # Session management
│   └── filetransfer.py # SFTP/SCP handling
├── ssh/               # SSH protocol implementation
│   ├── factory.py     # SSH factory
│   ├── transport.py   # SSH transport
│   ├── userauth.py    # SSH authentication
│   ├── connection.py  # SSH connection
│   └── session.py     # SSH session
├── ssh_proxy/         # SSH proxy mode
├── telnet/            # Telnet protocol
├── telnet_proxy/      # Telnet proxy mode
├── test/              # Unit tests
└── vendor/            # Third-party code (excluded from linting)
```

---

## Architecture

### High-Level Flow

```
Attacker → SSH/Telnet Server → Authentication → Shell/Proxy → Logging → Output Plugins
```

### Key Components

#### 1. Protocol Layer

**SSH Server** (`cowrie.ssh`)
- Full SSH protocol implementation using Twisted Conch
- Transport, authentication, connection, session handling
- SFTP and SCP support
- SSH exec command support

**Telnet Server** (`cowrie.telnet`)
- Telnet protocol implementation
- Similar structure to SSH

#### 2. Authentication Layer

**Realm** (`core/realm.py`)
- Twisted realm implementation
- Creates avatars for authenticated users

**Checkers** (`core/checkers.py`)
- Password authentication (userdb.txt)
- Public key authentication
- No authentication (optional)

**User Database** (`etc/userdb.txt`)
```
# Format: username:x:password
root:x:toor
admin:x:*           # Any password
user:x:!/badpass    # Deny this password
test:x:/^test.*/i   # Regex matching
```

#### 3. Shell Emulation

**HoneyPot Shell** (`shell/honeypot.py`)
- Command parsing and execution
- Environment variables
- I/O redirection (`>`, `>>`, `|`)
- Job control (basic)
- Tab completion

**Virtual Filesystem** (`shell/fs.py`)
- Pickled metadata in `data/fs.pickle`
- Real file contents in `honeyfs/`
- Path resolution with symlinks
- Wildcard/glob support
- File attributes: name, type, UID, GID, size, mode, timestamps

**Commands** (`commands/`)
- Each command is a separate Python module
- Inherits from `HoneyPotCommand` base class
- Registered in module-level `commands` dictionary

#### 4. Output System

**Event-Based Logging**
- All actions generate events
- Events broadcast to all enabled output plugins
- Plugins can filter events by type

**Output Plugins** (`output/`)
- 30+ plugins for various integrations
- Base class: `cowrie.core.output.Output`
- Common plugins: jsonlog, textlog, mysql, elasticsearch, slack

#### 5. Proxy Mode (Optional)

**SSH/Telnet Proxy** (`ssh_proxy/`, `telnet_proxy/`)
- Transparent proxying to real systems
- VM pool support with libvirt
- Session recording and logging

---

## Development Setup

### Prerequisites

- Python 3.10 or higher
- python-virtualenv
- Git

### Initial Setup

```bash
# Clone repository
git clone https://github.com/cowrie/cowrie
cd cowrie

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e '.[dev]'

# Install pre-commit hooks
pre-commit install

# Generate version file
python -m setuptools_scm --force-write-version-files

# Copy default configuration
cp etc/cowrie.cfg.dist etc/cowrie.cfg

# Edit configuration as needed
vim etc/cowrie.cfg
```

### Running Cowrie

```bash
# Using the cowrie command
bin/cowrie start         # Start in background
bin/cowrie stop          # Stop
bin/cowrie restart       # Restart
bin/cowrie status        # Check status

# Using twistd directly (foreground)
twistd --nodaemon cowrie

# Using Docker
make docker-build
make docker-run
docker exec -it cowrie bash
```

---

## Development Workflow

### Branch Strategy

- **main**: Production-ready code
- **feature/xxx**: New features
- **fix/xxx**: Bug fixes
- Work against latest source on main branch

### Making Changes

1. **Create a branch**
```bash
git checkout -b feature/my-feature
```

2. **Make your changes**
- Focus on specific changes
- Don't reformat unrelated code
- Add tests for new functionality

3. **Run pre-commit checks**
```bash
make pre-commit
# or
pre-commit run --all-files
```

4. **Run tests**
```bash
make test
# or
tox
# or specific environment
tox -e py310
```

5. **Run linting**
```bash
make lint
# or
tox -e lint
```

6. **Commit with clear message**
```bash
git add .
git commit -m "Add feature X"
```

7. **Push and create PR**
```bash
git push origin feature/my-feature
# Create pull request on GitHub
```

### Pre-commit Hooks

The project uses pre-commit hooks to ensure code quality:

- **pyupgrade**: Upgrade syntax to Python 3.8+
- **black**: Code formatting
- **isort**: Import sorting
- **yesqa**: Remove unnecessary noqa comments
- **Standard hooks**: Check YAML, JSON, TOML, trailing whitespace, etc.

Files in `src/cowrie/vendor/` are excluded from all checks.

---

## Testing

### Test Framework

- **Framework**: Python unittest
- **Location**: `src/cowrie/test/`
- **Automation**: tox

### Running Tests

```bash
# Run all tests
tox

# Run specific Python version
tox -e py310
tox -e py311
tox -e py312

# Run linting
tox -e lint

# Run type checking
tox -e typing

# Run tests directly
python -m unittest discover src --verbose

# Run specific test
python -m unittest cowrie.test.test_cat
```

### Writing Tests

**Test Structure:**
```python
import unittest
from cowrie.test.fake_server import FakeServer
from cowrie.test.fake_transport import FakeTransport
from cowrie.shell.protocol import HoneyPotInteractiveProtocol

class MyCommandTest(unittest.TestCase):
    def setUp(self):
        """Set up test fixture"""
        self.proto = HoneyPotInteractiveProtocol(
            FakeAvatar(FakeServer())
        )
        self.tr = FakeTransport("1.2.3.4", "12345")
        self.proto.makeConnection(self.tr)
        self.tr.clear()

    def test_command(self):
        """Test command execution"""
        self.proto.lineReceived(b"whoami\n")
        self.assertEqual(self.tr.value(), b"root\n$ ")

    def tearDown(self):
        """Clean up"""
        self.proto.connectionLost("test")
```

**Test Coverage Areas:**
- Basic commands (ls, cat, cd, etc.)
- File operations
- Pipe operations
- Network commands
- Authentication
- Protocol handling

### CI/CD

**GitHub Actions** (`.github/workflows/tox.yml`):
- Runs on every push and PR
- Tests against Python 3.10, 3.11, 3.12, 3.13, 3.14, PyPy
- Runs lint, docs, typing, and unit tests
- Matrix testing for multiple Python versions

---

## Code Conventions

### Python Style Guide

**PEP 8 Compliance** - enforced by ruff and pylint

### Type Hints

**Required for new code** - enforced by mypy, pyright, pyre-check

```python
from __future__ import annotations

def process_login(username: str, password: str) -> bool:
    """Process login attempt."""
    return check_credentials(username, password)
```

**Type Checking Configuration** (pyproject.toml):
- Strict settings enabled
- `no_implicit_optional = true`
- `strict_optional = true`
- `warn_return_any = true`
- `disallow_incomplete_defs = true`

### Import Organization

**Order** (enforced by isort):
```python
# 1. Future imports
from __future__ import annotations

# 2. Standard library
import os
import sys
from typing import Any

# 3. Third-party
import requests

# 4. Zope (special section)
from zope.interface import implementer

# 5. Twisted (special section)
from twisted.internet import reactor
from twisted.python import log

# 6. First-party (Cowrie)
from cowrie.core.config import CowrieConfig
from cowrie.shell.command import HoneyPotCommand

# 7. Local (relative imports)
from .utils import helper_function
```

### Code Formatting

**Black** - enforced by pre-commit
- Line length: 88 characters
- Automatic formatting

**Ruff** - fast linter
- Checks: A, B, E, F, UP, YTT, T20, Q, RUF, TC, TRY, PYI, FAST
- Target: Python 3.10+
- Ignores: A005, E501, UP007, B019, RUF001

### File Headers

```python
# Copyright (c) 2009-2014 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information
```

### Logging

**Use Twisted logging:**
```python
from twisted.python import log

# Event logging
log.msg(
    eventid='cowrie.session.connect',
    session='abc123',
    src_ip='1.2.3.4',
    format='Connection from %(src_ip)s'
)

# Error logging
log.err(
    eventid='cowrie.error',
    error='Something went wrong',
    format='Error: %(error)s'
)
```

### Configuration

**Reading config:**
```python
from cowrie.core.config import CowrieConfig

# Get string value
version = CowrieConfig.get('ssh', 'version')

# Get boolean
enabled = CowrieConfig.getboolean('output_jsonlog', 'enabled')

# Get integer
port = CowrieConfig.getint('ssh', 'listen_port')

# With default value
timeout = CowrieConfig.getint('honeypot', 'timeout', fallback=30)
```

**Environment variable override:**
```bash
# Format: COWRIE_SECTION_OPTION
export COWRIE_SSH_VERSION="SSH-2.0-OpenSSH_8.0"
export COWRIE_HONEYPOT_HOSTNAME="server01"
```

---

## Key Patterns

### Twisted Patterns

#### Deferreds and Callbacks

```python
from twisted.internet import defer

@defer.inlineCallbacks
def async_operation(self):
    """Async operation using inlineCallbacks"""
    result = yield some_deferred_operation()
    defer.returnValue(result)
```

#### Factories and Protocols

```python
from twisted.internet import protocol

class MyProtocol(protocol.Protocol):
    def connectionMade(self):
        """Called when connection is established"""
        pass

    def dataReceived(self, data):
        """Called when data is received"""
        pass

class MyFactory(protocol.Factory):
    def buildProtocol(self, addr):
        """Create protocol instance"""
        return MyProtocol()
```

### Plugin Pattern

**Dynamic Loading:**
```python
from importlib import import_module

# Load output plugins
for section in CowrieConfig.sections():
    if section.startswith("output_"):
        engine = section.split("_")[1]
        module = import_module(f"cowrie.output.{engine}")
        output = module.Output()
```

### Command Pattern

**Base class pattern:**
```python
from cowrie.shell.command import HoneyPotCommand

commands = {}

class Command_mycommand(HoneyPotCommand):
    def start(self):
        """Initialize (optional)"""
        self.call()

    def call(self):
        """Main logic"""
        self.write("output\n")
        self.exit()

commands['/bin/mycommand'] = Command_mycommand
commands['mycommand'] = Command_mycommand
```

### Observer Pattern

**Event broadcasting:**
```python
from twisted.python import log

# Emit event
log.msg(
    eventid='cowrie.custom.event',
    session=self.session,
    data=payload
)

# Observer (in output plugin)
def write(self, event):
    if event['eventid'] == 'cowrie.custom.event':
        self.process(event)
```

---

## Working with Commands

### Command Implementation Levels

#### 1. Text-Based Commands (Simplest)

**No Python code required!**

Create a text file in `src/cowrie/data/txtcmds/`:

```bash
# src/cowrie/data/txtcmds/bin/df
Filesystem     1K-blocks    Used Available Use% Mounted on
/dev/sda1       19092056 2643784  15479836  15% /
tmpfs             509348       0    509348   0% /dev/shm
```

Then add to virtual filesystem:
```python
fs.mkfile('/bin/df', 0, 0, 1024, 33188)
```

#### 2. Simple Python Commands

**For basic logic:**

```python
# src/cowrie/commands/whoami.py
from cowrie.shell.command import HoneyPotCommand

commands = {}

class Command_whoami(HoneyPotCommand):
    def call(self):
        self.write(f"{self.protocol.user.username}\n")

commands['/usr/bin/whoami'] = Command_whoami
commands['whoami'] = Command_whoami
```

#### 3. Complex Python Commands

**For full implementations:**

```python
# src/cowrie/commands/wget.py
from __future__ import annotations

import getopt
from twisted.internet import defer
import treq

from cowrie.shell.command import HoneyPotCommand
from cowrie.core.artifact import Artifact

commands = {}

class Command_wget(HoneyPotCommand):
    """Wget command implementation"""

    @defer.inlineCallbacks
    def start(self):
        """Download file"""
        try:
            # Parse arguments
            optlist, args = getopt.getopt(self.args, 'qO:')

            url = args[0] if args else None
            if not url:
                self.write("wget: missing URL\n")
                self.exit()
                return

            # Download
            self.write(f"Connecting to {url}...\n")
            response = yield treq.get(url, timeout=10)
            content = yield response.content()

            # Save artifact
            with Artifact(f"wget-{url}") as artf:
                artf.write(content)
                log.msg(
                    eventid='cowrie.session.file_download',
                    format='Downloaded %(url)s',
                    url=url,
                    shasum=artf.shasum
                )

            self.write("File saved.\n")

        except Exception as e:
            self.write(f"wget: error: {e}\n")
        finally:
            self.exit()

commands['/usr/bin/wget'] = Command_wget
commands['wget'] = Command_wget
```

### Command Base Class (`HoneyPotCommand`)

**Available Attributes:**
- `self.protocol` - Protocol instance
- `self.args` - Command arguments (list)
- `self.environ` - Environment variables (dict)
- `self.fs` - Virtual filesystem
- `self.input_data` - STDIN data (from pipes)
- `self.write_callbacks` - STDOUT callbacks
- `self.exit_callbacks` - Exit callbacks

**Available Methods:**
- `self.write(str)` - Write to STDOUT
- `self.writeBytes(bytes)` - Write raw bytes
- `self.errorWrite(str)` - Write to STDERR
- `self.exit()` - Exit command
- `self.check_arguments()` - Parse arguments
- `self.set_default_result()` - Set exit code

**Lifecycle Methods:**
```python
def start(self):
    """Called first (optional)"""
    self.call()

def call(self):
    """Main command logic"""
    pass

def exit(self):
    """Cleanup and exit"""
    pass

def handle_CTRL_C(self):
    """Handle Ctrl+C (optional)"""
    self.write("^C\n")
    self.exit()

def handle_CTRL_D(self):
    """Handle Ctrl+D (optional)"""
    pass

def handle_TAB(self):
    """Tab completion (optional)"""
    pass

def lineReceived(self, line):
    """Interactive input (optional)"""
    pass
```

### I/O Redirection

**Automatically handled by base class:**

```bash
command > file         # STDOUT to file
command >> file        # Append STDOUT
command 2> file        # STDERR to file
command | command2     # Pipe STDOUT
command 2>&1 | cmd2    # Pipe STDOUT and STDERR
```

Implementation checks for `>`, `>>`, `|` in constructor and sets up appropriate file handles.

### Filesystem Operations

```python
# Check if file exists
if self.fs.exists(path):
    pass

# Resolve path
realpath = self.fs.resolve_path(path, self.protocol.cwd)

# Get file contents
contents = self.fs.getfile(path)

# Create file
self.fs.mkfile(path, uid, gid, size, mode)

# List directory
for entry in self.fs.get_path('/home'):
    print(entry)

# Get file attributes
attrs = self.fs.getfile(path)
# attrs = [name, type, uid, gid, size, mode, ctime, contents, target, realfile]
```

### Testing Commands

```python
import unittest
from cowrie.test.fake_server import FakeServer, FakeAvatar
from cowrie.test.fake_transport import FakeTransport
from cowrie.shell.protocol import HoneyPotInteractiveProtocol

class WhoamiTest(unittest.TestCase):
    def setUp(self):
        self.proto = HoneyPotInteractiveProtocol(
            FakeAvatar(FakeServer())
        )
        self.tr = FakeTransport("1.2.3.4", "12345")
        self.proto.makeConnection(self.tr)
        self.tr.clear()

    def test_whoami(self):
        self.proto.lineReceived(b"whoami\n")
        self.assertIn(b"root", self.tr.value())
```

---

## Working with Output Plugins

### Plugin Structure

**Location**: `src/cowrie/output/<plugin_name>.py`

**Base Class**: `cowrie.core.output.Output`

### Creating a Plugin

```python
# src/cowrie/output/example.py
from __future__ import annotations

from twisted.python import log
from cowrie.core.output import Output

class Output(Output):
    """Example output plugin"""

    def start(self):
        """Initialize plugin"""
        # Read configuration
        self.server = CowrieConfig.get('output_example', 'server')
        self.enabled_events = CowrieConfig.get(
            'output_example',
            'events',
            fallback='*'
        ).split(',')

        log.msg(f"Example output plugin started: {self.server}")

    def stop(self):
        """Cleanup"""
        log.msg("Example output plugin stopped")

    def write(self, event):
        """Handle event"""
        # Filter events
        if self.enabled_events != ['*']:
            if event['eventid'] not in self.enabled_events:
                return

        # Process event
        if event['eventid'] == 'cowrie.session.connect':
            self.handle_connect(event)
        elif event['eventid'] == 'cowrie.command.input':
            self.handle_command(event)

    def handle_connect(self, event):
        """Handle connection event"""
        log.msg(f"Connection from {event['src_ip']}")

    def handle_command(self, event):
        """Handle command event"""
        log.msg(f"Command: {event['input']}")
```

### Configuration

**Add to** `etc/cowrie.cfg`:

```ini
[output_example]
enabled = true
server = example.com
events = cowrie.session.connect,cowrie.command.input
```

### Common Event IDs

**Session Events:**
- `cowrie.session.connect` - New connection
- `cowrie.session.closed` - Session ended
- `cowrie.session.params` - Session parameters

**Authentication Events:**
- `cowrie.login.success` - Successful login
- `cowrie.login.failed` - Failed login

**Command Events:**
- `cowrie.command.input` - Command executed
- `cowrie.command.failed` - Command not found
- `cowrie.command.success` - Command succeeded

**File Events:**
- `cowrie.session.file_download` - File downloaded (wget, curl)
- `cowrie.session.file_upload` - File uploaded (SFTP, SCP)

**Client Events:**
- `cowrie.client.version` - SSH client version
- `cowrie.client.kex` - SSH key exchange
- `cowrie.client.fingerprint` - SSH client fingerprint

### Event Structure

```python
{
    'eventid': 'cowrie.command.input',
    'session': 'abc123def456',  # Session UUID
    'src_ip': '1.2.3.4',         # Source IP
    'src_port': 12345,           # Source port
    'dst_ip': '5.6.7.8',         # Destination IP
    'dst_port': 2222,            # Destination port
    'username': 'root',          # Username
    'timestamp': '2025-01-19T12:00:00.000000Z',
    'message': 'Command input',
    'input': 'ls -la',           # The command
    'protocol': 'ssh',           # Protocol (ssh/telnet)
    'sensor': 'myhoneypot',      # Sensor name
}
```

### Plugin Examples

**JSONLog** (`output/jsonlog.py`):
- Writes events to JSON file
- One event per line
- Located in `var/log/cowrie/cowrie.json`

**MySQL** (`output/mysql.py`):
- Writes events to MySQL database
- Requires mysqlclient
- Schema in `docs/sql/mysql.sql`

**Slack** (`output/slack.py`):
- Posts events to Slack webhook
- Configurable message formatting
- Event filtering

**VirusTotal** (`output/virustotal.py`):
- Submits downloaded files to VirusTotal
- API key required
- Rate limiting

---

## Important Files

### Configuration

**`etc/cowrie.cfg.dist`** - Default configuration (DO NOT EDIT)
- Contains all available options with defaults
- Reference for configuration options
- Overridden by `etc/cowrie.cfg`

**`etc/cowrie.cfg`** - User configuration
- Only include options you want to override
- INI format (ConfigParser)
- Can be overridden by environment variables

**`etc/userdb.txt`** - Authentication database
```
# username:x:password
root:x:toor
admin:x:*              # Any password
user:x:!/forbidden     # Deny this password
test:x:/^test\d+$/i    # Regex pattern
```

### Data Files

**`src/cowrie/data/fs.pickle`** - Virtual filesystem metadata
- Pickled Python data structure
- Contains file/directory metadata
- ~1.2MB file
- Edit with `bin/fsctl` or `bin/createfs`

**`src/cowrie/data/txtcmds/`** - Text-based command outputs
- Simple commands without Python code
- Directory structure mirrors filesystem
- Example: `bin/df`, `usr/bin/uptime`

**`honeyfs/`** - Virtual filesystem contents
- Real file contents for virtual filesystem
- Subdirectories: `etc/`, `proc/`, etc.
- Example: `honeyfs/etc/passwd`, `honeyfs/etc/motd`

### Entry Points

**`src/twisted/plugins/cowrie_plugin.py`** - Twisted plugin
- Main entry point for Twisted
- `CowrieServiceMaker` class
- `makeService()` method initializes everything

**`src/cowrie/scripts/cowrie.py`** - CLI entry point
- Wrapper around `twistd` command
- Commands: start, stop, restart, status

### Logging and Data

**`var/log/cowrie/cowrie.json`** - JSON event log
- One event per line
- Enabled by default
- Used by most integrations

**`var/log/cowrie/cowrie.log`** - Debug log
- Text format
- Twisted log output
- Useful for debugging

**`var/lib/cowrie/tty/`** - TTY session recordings
- UML-compatible format
- Replayable with `bin/playlog`
- One file per session

**`var/lib/cowrie/downloads/`** - Downloaded/uploaded files
- Named by SHA256 hash
- Automatic deduplication
- Metadata in JSON log

---

## Common Tasks

### Add a New Command

1. **Create command file**:
```bash
vim src/cowrie/commands/mycommand.py
```

2. **Implement command**:
```python
from cowrie.shell.command import HoneyPotCommand

commands = {}

class Command_mycommand(HoneyPotCommand):
    def call(self):
        self.write("Hello from mycommand!\n")

commands['/bin/mycommand'] = Command_mycommand
commands['mycommand'] = Command_mycommand
```

3. **Add to filesystem** (if needed):
```bash
bin/fsctl cowrie-fs add /bin/mycommand file 0 0 1024 33188
```

4. **Test**:
```bash
bin/cowrie restart
ssh -p 2222 root@localhost
$ mycommand
```

### Add an Output Plugin

1. **Create plugin file**:
```bash
vim src/cowrie/output/myplugin.py
```

2. **Implement plugin** (see "Working with Output Plugins")

3. **Add configuration**:
```bash
vim etc/cowrie.cfg
```
```ini
[output_myplugin]
enabled = true
option = value
```

4. **Test**:
```bash
bin/cowrie restart
# Check logs
tail -f var/log/cowrie/cowrie.log
```

### Modify Virtual Filesystem

**Using fsctl**:
```bash
# List files
bin/fsctl cowrie-fs ls /

# Add file
bin/fsctl cowrie-fs add /bin/test file 0 0 1024 33188

# Add directory
bin/fsctl cowrie-fs mkdir /test 0 0 4096 16877

# Remove file
bin/fsctl cowrie-fs rm /bin/test

# Get file info
bin/fsctl cowrie-fs get /bin/ls
```

**Using createfs** (rebuild from scratch):
```bash
# Create new filesystem from real directory
bin/createfs -l /path/to/real/system -o data/fs.pickle -p honeyfs/
```

### Update Dependencies

```bash
# Update requirements.txt
vim requirements.txt

# Install updated dependencies
pip install -r requirements.txt

# Check for issues
pip check

# Run tests
tox
```

### Build and Release

```bash
# Build package
python -m build

# Check package
twine check dist/*

# Upload to PyPI (maintainers only)
twine upload dist/*
```

### Docker Build

```bash
# Build Docker image
make docker-build

# Load locally
make docker-load

# Run container
make docker-run

# View logs
make docker-logs

# Shell into container
make docker-shell

# Stop container
make docker-stop
```

---

## Debugging

### Enable Debug Logging

**In `etc/cowrie.cfg`**:
```ini
[honeypot]
log_level = DEBUG
```

### View Logs

```bash
# Real-time log monitoring
tail -f var/log/cowrie/cowrie.log

# JSON events
tail -f var/log/cowrie/cowrie.json | jq

# Session logs
ls -la var/lib/cowrie/tty/
```

### Replay TTY Sessions

```bash
# List sessions
ls var/lib/cowrie/tty/

# Replay session
bin/playlog var/lib/cowrie/tty/20250119-120000-abc123.log

# Convert to asciinema
bin/asciinema var/lib/cowrie/tty/20250119-120000-abc123.log
```

### Run in Foreground

```bash
# Run without daemonizing
twistd --nodaemon cowrie

# With debug output
twistd --nodaemon --debug cowrie
```

### Python Debugger

```python
# In code
import pdb; pdb.set_trace()

# Or with ipdb (better)
import ipdb; ipdb.set_trace()
```

### Common Issues

**Port already in use:**
```bash
# Check what's using port 2222
lsof -i :2222

# Kill process
kill <PID>
```

**Permission denied:**
```bash
# Cowrie should NOT run as root
# Run as regular user
sudo su - cowrie
```

**Module not found:**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Check installation
pip list | grep cowrie
```

**Configuration errors:**
```bash
# Validate config
python -c "from cowrie.core.config import CowrieConfig; print('OK')"
```

---

## Security Considerations

### Critical Context

**⚠️ Cowrie is a HONEYPOT - a security research tool**

- **Purpose**: Capture and analyze attacker behavior
- **DO NOT** use honeypot data for production systems
- **DO NOT** connect honeypot to production networks without isolation
- **DO NOT** expose real credentials or sensitive data

### Code Review Guidelines

When working with Cowrie code:

1. **This is defensive security code** - analyzing malware and attacker behavior is the core purpose
2. **Malware analysis is expected** - downloaded files may be malicious
3. **Command emulation** - code that simulates vulnerable behavior is intentional
4. **Do not "fix" security features** - apparent vulnerabilities may be intentional honeypot behavior

### Sandboxing

**Downloaded files**:
- Stored by SHA256 hash in `var/lib/cowrie/downloads/`
- Should be analyzed in isolated environment
- Integration with Cuckoo Sandbox available

**Proxy mode**:
- VM pool provides isolation
- Backend systems should be disposable
- No production systems in pool

### Authentication

**Never use real credentials:**
- `etc/userdb.txt` contains fake credentials
- Purpose is to look realistic to attackers
- Common weak passwords are intentional

### Network Isolation

**Best practices:**
- Run on isolated network segment
- No access to production systems
- Firewall outbound connections (optional)
- Monitor for unexpected activity

### Logging Privacy

**Be aware of data collection:**
- IP addresses are logged
- Commands are recorded
- Files are stored
- Check local regulations (GDPR, etc.)

### Regular Updates

```bash
# Update Cowrie
git pull origin main
pip install -r requirements.txt

# Update dependencies for security patches
pip install --upgrade -r requirements.txt
```

---

## AI Assistant Guidelines

When working with Cowrie as an AI assistant:

### Understanding Context

1. **This is a honeypot** - security research tool, not a vulnerable application
2. **Malware handling is normal** - analyzing malicious files is core functionality
3. **Emulation is intentional** - code that looks vulnerable is designed to attract attackers
4. **Don't over-sanitize** - removing "unsafe" patterns may break honeypot functionality

### Code Changes

**DO:**
- Add new command implementations
- Create output plugins for integrations
- Improve test coverage
- Fix actual bugs in command emulation
- Enhance documentation
- Optimize performance

**DON'T:**
- "Fix" intentionally vulnerable-looking code without understanding context
- Remove or sanitize malware analysis features
- Change authentication to be more secure (defeats purpose)
- Modify logging to hide attacker activity
- Make the honeypot less realistic to attackers

### When in Doubt

- Read the documentation: https://docs.cowrie.org/
- Check existing issues: https://github.com/cowrie/cowrie/issues
- Ask for clarification about security-related changes
- Understand the purpose before "improving" security

### Testing Changes

Always test changes thoroughly:
```bash
# Run full test suite
tox

# Run specific tests
python -m unittest cowrie.test.test_<module>

# Test in live environment
bin/cowrie start
ssh -p 2222 root@localhost
```

### Pull Request Guidelines

1. **Focus on specific change** - don't refactor unrelated code
2. **Include tests** - for new functionality
3. **Update documentation** - if adding features
4. **Follow conventions** - match existing code style
5. **Run pre-commit** - ensure hooks pass
6. **Explain security changes** - if modifying authentication/logging

---

## Quick Reference

### Common Commands

```bash
# Development
make test               # Run all tests
make lint               # Run linting
make pre-commit         # Run pre-commit hooks
make docs               # Build documentation

# Running
bin/cowrie start        # Start honeypot
bin/cowrie stop         # Stop honeypot
bin/cowrie status       # Check status

# Utilities
bin/fsctl               # Filesystem control
bin/playlog             # Replay TTY sessions
bin/createfs            # Create filesystem

# Docker
make docker-build       # Build image
make docker-run         # Run container
make docker-logs        # View logs
make docker-shell       # Shell into container
```

### File Locations

```
etc/cowrie.cfg          # Configuration
etc/userdb.txt          # Authentication
var/log/cowrie/         # Logs
var/lib/cowrie/tty/     # Session recordings
var/lib/cowrie/downloads/ # Downloaded files
src/cowrie/commands/    # Command implementations
src/cowrie/output/      # Output plugins
```

### Configuration Sections

```ini
[honeypot]              # Core settings
[ssh]                   # SSH server
[telnet]                # Telnet server
[output_jsonlog]        # JSON logging
[output_mysql]          # MySQL output
[output_slack]          # Slack notifications
```

### Environment Variables

```bash
COWRIE_HONEYPOT_HOSTNAME="server01"
COWRIE_SSH_VERSION="SSH-2.0-OpenSSH_8.0"
COWRIE_OUTPUT_JSONLOG_ENABLED="true"
```

---

## Additional Resources

- **Documentation**: https://docs.cowrie.org/
- **Repository**: https://github.com/cowrie/cowrie
- **Issues**: https://github.com/cowrie/cowrie/issues
- **Slack**: https://www.cowrie.org/slack/
- **PyPI**: https://pypi.org/project/cowrie
- **Docker Hub**: https://hub.docker.com/r/cowrie/cowrie

---

**Last Updated**: 2025-11-19
**Version**: Based on current main branch
**Maintainer**: Michel Oosterhof (michel@oosterhof.net)
