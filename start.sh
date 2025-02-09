#!/bin/bash
echo "Installing FFmpeg..."
nix-env -iA nixpkgs.ffmpeg  # Railway supports Nix package manager
echo "Starting bot..."
python bot.py
