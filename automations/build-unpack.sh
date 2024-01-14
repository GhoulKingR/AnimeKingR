#!/usr/bin/env bash

echo "Cleaning dist..."
if find "dist" -name "*" -type f; then
    cd dist
    rm -r *
    cd ..
fi

python3 -m build

if find "dist" -name "*.tar.gz" -type f; then
    cd dist
    tar -xzvf *.tar.gz
fi