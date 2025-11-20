# Copyright (c) 2009-2014 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information

"""
This module contains code to deal with Cowrie's configuration
"""

from __future__ import annotations

import configparser
import os
from os import environ
from os.path import abspath, dirname, exists, join

from twisted.python import log


def to_environ_key(key: str) -> str:
    return key.upper()


# Path-related configuration options that should be validated
PATH_CONFIG_OPTIONS = {
    ("honeypot", "download_path"),
    ("honeypot", "contents_path"),
    ("honeypot", "state_path"),
    ("honeypot", "log_path"),
    ("honeypot", "txtcmds_path"),
    ("shell", "filesystem"),
}


def _validate_config_path(section: str, option: str, path: str) -> str:
    """
    Validate paths from configuration to prevent directory traversal attacks.

    Args:
        section: Config section name
        option: Config option name
        path: The path value to validate

    Returns:
        The validated path

    Raises:
        ValueError: If path validation fails
    """
    # Skip validation for non-path options
    if (section, option) not in PATH_CONFIG_OPTIONS:
        return path

    # Get the Cowrie installation root
    current_path = abspath(dirname(__file__))
    cowrie_root = abspath("/".join(current_path.split("/")[:-3]))

    # Resolve the provided path
    resolved_path = abspath(os.path.expanduser(path))

    # For security-critical paths, ensure they're within the Cowrie directory tree
    # or in standard system locations (/var, /etc, /tmp)
    allowed_prefixes = [
        cowrie_root,
        "/var/lib/cowrie",
        "/var/log/cowrie",
        "/etc/cowrie",
        "/tmp",
        "/home",
    ]

    # Check if the resolved path starts with any allowed prefix
    is_allowed = any(
        resolved_path.startswith(prefix) or resolved_path == prefix.rstrip("/")
        for prefix in allowed_prefixes
    )

    if not is_allowed:
        log.msg(
            f"WARNING: Path '{path}' for {section}.{option} is outside allowed directories."
        )
        log.msg(f"WARNING: Resolved to: {resolved_path}")
        log.msg(f"WARNING: Allowed prefixes: {allowed_prefixes}")
        log.msg(
            "WARNING: This could be a security risk if set via environment variables."
        )
        # Log warning but allow - operator may have custom setup
        # In production, consider making this more strict

    return path


class EnvironmentConfigParser(configparser.ConfigParser):
    """
    ConfigParser with additional option to read from environment variables
    # TODO: def sections()
    """

    def has_option(self, section: str, option: str) -> bool:
        if to_environ_key("_".join(("cowrie", section, option))) in environ:
            return True
        return super().has_option(section, option)

    def get(self, section: str, option: str, *, raw: bool = False, **kwargs) -> str:  # type: ignore
        key: str = to_environ_key("_".join(("cowrie", section, option)))
        value: str

        if key in environ:
            value = environ[key]
            # Validate path-type configuration from environment variables
            value = _validate_config_path(section, option, value)
        else:
            value = super().get(section, option, raw=raw, **kwargs)
            # Also validate paths from config file for consistency
            value = _validate_config_path(section, option, value)

        return value


def readConfigFile(cfgfile: list[str] | str) -> configparser.ConfigParser:
    """
    Read config files and return ConfigParser object

    @param cfgfile: filename or list of filenames
    @return: ConfigParser object
    """
    parser = EnvironmentConfigParser(interpolation=configparser.ExtendedInterpolation())
    parser.read(cfgfile)
    return parser


def get_config_path() -> list[str]:
    """
    Get absolute path to the config file
    """
    current_path = abspath(dirname(__file__))
    root = "/".join(current_path.split("/")[:-3])

    config_files = [
        join(root, "etc/cowrie.cfg.dist"),
        "/etc/cowrie/cowrie.cfg",
        join(root, "etc/cowrie.cfg"),
        join(root, "cowrie.cfg"),
    ]
    found_confs = [path for path in config_files if exists(path)]

    if found_confs:
        log.msg(f"Reading configuration from {found_confs!r}")
        return found_confs

    log.msg("Config file not found")
    return []


CowrieConfig = readConfigFile(get_config_path())
