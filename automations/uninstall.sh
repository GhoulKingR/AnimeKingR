#!/usr/bin/env bash

if command -v "akr-download" &> /dev/null; then
    echo "Uninstalling..."
    pip uninstall "anime_king_r" <<< "y"
fi