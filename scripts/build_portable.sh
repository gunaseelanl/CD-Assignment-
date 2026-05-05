#!/usr/bin/env sh
# MD INDUSTRIES
# Developer: M.DHANESVARAN

set -eu

command -v python >/dev/null 2>&1 || {
    echo "python not found in PATH" >&2
    exit 1
}

mkdir -p bin output
cat > bin/pyportcc <<'EOF'
#!/usr/bin/env sh
python -m pyportcc "$@"
EOF
chmod +x bin/pyportcc
echo "Portable build completed. Use python -m pyportcc or ./bin/pyportcc."
