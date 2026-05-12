"""
Unit tests for the audit-processor OCI Function.
Tests audit event parsing and error handling without OCI dependencies.
"""
import pytest


# ── Section 1: Test valid audit event processing ────────────────────
# WHAT: Build a mock OCI Events body with CSV data, call the processing logic,
#       verify action_summary and top_ips are extracted correctly
# LEARNING: Testing serverless functions locally — mock the event body, test the
#           parsing logic independently of OCI infrastructure
# LOOK UP: json.loads, csv.DictReader, collections.Counter
#
# Write your implementation below. Check answers/ only after attempting.


# ── Section 2: Test malformed event handling ────────────────────────
# WHAT: Pass an event body with missing fields (no resourceName, no additionalDetails),
#       verify the function raises KeyError or returns an error gracefully
# LEARNING: Defensive coding in serverless — events can be malformed, partial, or replayed
# LOOK UP: pytest.raises(KeyError), json.loads edge cases
#
# Write your implementation below. Check answers/ only after attempting.
