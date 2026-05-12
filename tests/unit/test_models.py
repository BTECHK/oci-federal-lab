"""
Unit tests for FedTracker Pydantic models.
Tests validate federal personnel record creation and input validation.
"""
import pytest


# ── Section 1: Test valid personnel record creation ─────────────────
# WHAT: Create a PersonnelCreate with name, role, clearance_level and assert fields are set correctly
# LEARNING: Pydantic model instantiation, default values, field access
# LOOK UP: PersonnelCreate from models.py, BaseModel field defaults
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 2: Test invalid inputs ──────────────────────────────────
# WHAT: Assert that missing required fields (name, role) and empty strings raise ValidationError
# LEARNING: pytest.raises context manager, Pydantic ValidationError, min_length constraint
# LOOK UP: pytest.raises, pydantic.ValidationError, Field(min_length=1)
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 3: Test model serialization ─────────────────────────────
# WHAT: Create a PersonnelCreate, call .model_dump() and verify the dict has expected keys/values
# LEARNING: Pydantic model_dump() (v2) — how models serialize for JSON API responses
# LOOK UP: BaseModel.model_dump(), BaseModel.model_json_schema()
#
# Write your implementation below. Check answers/ only after attempting.
