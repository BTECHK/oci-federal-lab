#!/usr/bin/env bash
# Generate gRPC stubs for fedagent + fedtracker-app from compliance.proto.
# Run from repo root or fedagent/.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
PROTO_DIR="$REPO_ROOT/fedagent/proto"
GO_OUT_DIR="$REPO_ROOT/fedagent/pb"
PY_OUT_DIR="$REPO_ROOT/fedtracker-app/proto"

mkdir -p "$GO_OUT_DIR" "$PY_OUT_DIR"

# ── Go stubs ────────────────────────────────────────────────────────────
# Requires:
#   protoc (apt: protobuf-compiler / brew: protobuf)
#   protoc-gen-go      (go install google.golang.org/protobuf/cmd/protoc-gen-go@latest)
#   protoc-gen-go-grpc (go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest)
echo "[proto] generating Go stubs → $GO_OUT_DIR"
protoc \
    --proto_path="$PROTO_DIR" \
    --go_out="$GO_OUT_DIR" \
    --go_opt=paths=source_relative \
    --go-grpc_out="$GO_OUT_DIR" \
    --go-grpc_opt=paths=source_relative \
    "$PROTO_DIR/compliance.proto"

# ── Python stubs ────────────────────────────────────────────────────────
# Requires: pip install grpcio-tools (already in fedtracker-app/requirements.txt)
echo "[proto] generating Python stubs → $PY_OUT_DIR"
python -m grpc_tools.protoc \
    --proto_path="$PROTO_DIR" \
    --python_out="$PY_OUT_DIR" \
    --grpc_python_out="$PY_OUT_DIR" \
    "$PROTO_DIR/compliance.proto"

touch "$PY_OUT_DIR/__init__.py"

echo "[proto] done. Go: $GO_OUT_DIR | Python: $PY_OUT_DIR"
