#!/bin/bash
set -e

# Arrancar SSH en background
/usr/sbin/sshd

# Arrancar la app (proceso principal)
exec nix-shell --run "python app.py"
