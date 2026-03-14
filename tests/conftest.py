"""
Shared pytest fixtures.

ANANAS_DB_PATH is set to a temporary file per test session so all
persistence tests share the same bootstrapped schema while never
touching the real dev database on disk.

:memory: does NOT work across multiple sqlite3.connect() calls because
each call opens a fresh empty database — bootstrap() would create tables
in one connection that are invisible to the next.
"""

from __future__ import annotations

import os
import tempfile


def pytest_configure(config):
    # Create one temp DB file for the whole test session
    fd, tmp_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.environ["ANANAS_DB_PATH"] = tmp_path
    os.environ.setdefault("ANTHROPIC_API_KEY", "sk-ant-test-placeholder")


def pytest_unconfigure(config):
    db_path = os.environ.get("ANANAS_DB_PATH", "")
    if db_path and os.path.exists(db_path):
        os.unlink(db_path)
