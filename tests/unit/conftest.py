"""
Test configuration — conftest.py
Pytest fixtures shared across all unit tests.
"""
import sys
import os
import pytest


# ── Section 1: Path setup + imports ─────────────────────────────────
# WHAT: Add fedtracker-app/ to sys.path so tests can import models, database, main
# LEARNING: sys.path.insert — why tests need path manipulation when the app isn't an installed package
# LOOK UP: sys.path, os.path.abspath, os.path.join
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 2: Test database fixture ────────────────────────────────
# WHAT: @pytest.fixture that creates an in-memory SQLite DB with WAL mode and the personnel + audit_log tables
# LEARNING: pytest fixtures, yield vs return (teardown), in-memory SQLite for fast isolated tests
# LOOK UP: pytest.fixture, sqlite3.connect(":memory:"), PRAGMA journal_mode=WAL
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 3: FastAPI TestClient fixture ───────────────────────────
# WHAT: @pytest.fixture that returns a TestClient wrapping the FastAPI app
# LEARNING: Starlette TestClient — sends real HTTP requests in-process, no server needed
# LOOK UP: fastapi.testclient.TestClient, app import from main
#
# Write your implementation below. Check answers/ only after attempting.
