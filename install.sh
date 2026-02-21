#!/bin/bash
set -e

echo "Installing system dependencies..."
sudo apt update
sudo apt install -y \
    libgtk-4-dev \
    libgirepository1.0-dev \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    python3-gi \
    python3-gi-cairo \
    gir1.2-gtk-4.0 \
    python3-venv

echo "Creating virtual environment..."
python3 -m venv --system-site-packages .venv

echo "Installing Python dependencies..."
.venv/bin/pip install python-rtmidi

echo "Done! Run ./run.sh to start Barulho."
