"""
FedTracker data models.
Pydantic v2 models define the shape of data the API accepts and returns.
"""
from pydantic import BaseModel, Field
from typing import Optional


# ── Section 1: Personnel models ─────────────────────────────────────
# WHAT: Request and response models for the /personnel endpoints
# LEARNING: Pydantic v2 BaseModel — field validation, default values, Optional types
# LOOK UP: pydantic.Field, pydantic.BaseModel, pydantic validators
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 2: Audit log models ──────────────────────────────────────
# WHAT: Response model for audit log entries returned by GET /audit
# LEARNING: How response models shape API output independently of DB schema
# LOOK UP: pydantic.BaseModel, datetime types in Pydantic
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 3: API response envelope ────────────────────────────────
# WHAT: Generic paginated response wrapper used by list endpoints
# LEARNING: Generic types in Pydantic, reusable response shapes
# LOOK UP: pydantic.generics (v1) or model_validator (v2), typing.Generic
#
# Write your implementation below. Check answers/ only after attempting.
