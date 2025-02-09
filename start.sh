#!/bin/bash

# Install ffmpeg manually
echo "Installing ffmpeg..."
apk add --no-cache ffmpeg

# Run the bot
echo "Starting bot..."
python bot.py
