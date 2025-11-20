# Copyright (c) 2016 Michel Oosterhof <michel@oosterhof.net>

"""
This module contains code to handling saving of honeypot artifacts
These will typically be files uploaded to the honeypot and files
downloaded inside the honeypot, or input being piped in.

Code behaves like a normal Python file handle.

Example:

    with Artifact(name) as f:
        f.write("abc")

or:

    g = Artifact("testme2")
    g.write("def")
    g.close()

"""

from __future__ import annotations

import hashlib
import os
import tempfile
from typing import Any, TYPE_CHECKING

from twisted.python import log

from cowrie.core.config import CowrieConfig

if TYPE_CHECKING:
    from types import TracebackType


class Artifact:
    artifactDir: str = CowrieConfig.get("honeypot", "download_path", fallback=".")

    @staticmethod
    def _validate_artifact_dir(path: str) -> str:
        """
        Validate the artifact directory to ensure it's safe to use.

        Args:
            path: The artifact directory path

        Returns:
            The validated absolute path

        Raises:
            ValueError: If path validation fails
        """
        # Resolve to absolute path
        abs_path = os.path.abspath(path)

        # Check if directory exists, create if it doesn't
        if not os.path.exists(abs_path):
            try:
                os.makedirs(abs_path, mode=0o755, exist_ok=True)
                log.msg(f"Created artifact directory: {abs_path}")
            except OSError as e:
                log.err(f"Failed to create artifact directory {abs_path}: {e}")
                raise ValueError(f"Cannot create artifact directory: {abs_path}") from e

        # Verify it's a directory
        if not os.path.isdir(abs_path):
            raise ValueError(f"Artifact path is not a directory: {abs_path}")

        # Check permissions - should not be world-writable
        dir_stat = os.stat(abs_path)
        if dir_stat.st_mode & 0o002:  # World-writable
            log.msg(
                f"WARNING: Artifact directory {abs_path} is world-writable! Security risk."
            )

        return abs_path

    def __init__(self, label: str) -> None:
        self.label: str = label

        # Validate artifact directory before use
        validated_dir = self._validate_artifact_dir(self.artifactDir)

        try:
            self.fp = tempfile.NamedTemporaryFile(  # pylint: disable=R1732
                dir=validated_dir, delete=False
            )
        except OSError as e:
            log.err(f"Failed to create temporary file in {validated_dir}: {e}")
            raise

        self.tempFilename = self.fp.name
        self.closed: bool = False

        self.shasum: str = ""
        self.shasumFilename: str = ""

    def __enter__(self) -> Any:
        return self.fp

    def __exit__(
        self,
        etype: type[BaseException] | None,
        einst: BaseException | None,
        etrace: TracebackType | None,
    ) -> bool:
        self.close()
        return False

    def write(self, data: bytes) -> None:
        self.fp.write(data)

    def fileno(self) -> Any:
        return self.fp.fileno()

    def close(self, keepEmpty: bool = False) -> tuple[str, str] | None:
        size: int = self.fp.tell()
        if size == 0 and not keepEmpty:
            try:
                os.remove(self.fp.name)
            except FileNotFoundError:
                pass
            return None

        self.fp.seek(0)
        data = self.fp.read()
        self.fp.close()
        self.closed = True

        self.shasum = hashlib.sha256(data).hexdigest()

        # Validate shasum to ensure it's a valid hex string (prevents path traversal)
        if not all(c in "0123456789abcdef" for c in self.shasum):
            log.err(f"ERROR: Invalid SHA256 hash generated: {self.shasum}")
            os.remove(self.fp.name)
            return None

        # Construct and validate final path
        self.shasumFilename = os.path.join(self.artifactDir, self.shasum)

        # Ensure the final path is still within artifactDir (defense in depth)
        abs_shasum_path = os.path.abspath(self.shasumFilename)
        abs_artifact_dir = os.path.abspath(self.artifactDir)

        if not abs_shasum_path.startswith(abs_artifact_dir + os.sep):
            log.err(
                f"ERROR: Path traversal detected in artifact storage: {self.shasumFilename}"
            )
            os.remove(self.fp.name)
            return None

        if os.path.exists(self.shasumFilename):
            log.msg("Not storing duplicate content " + self.shasum)
            os.remove(self.fp.name)
        else:
            os.rename(self.fp.name, self.shasumFilename)
            umask = os.umask(0)
            os.umask(umask)
            os.chmod(self.shasumFilename, 0o666 & ~umask)

        return self.shasum, self.shasumFilename
