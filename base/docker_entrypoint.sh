#!/bin/bash
cat >> /etc/apt/preferences.d/99pin-unstable << EOF
Package: *
Pin: release a=stable
Pin-Priority: 900

Package: *
Pin: release a=unstable
Pin-Priority: 10
EOF
apt update 
apt install -t unstable firefox