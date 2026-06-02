# usedres-docker.py

**Portable Docker Resource Monitor** — lightweight, zero-dependency monitoring tool for Docker hosts.

<img width="719" height="651" alt="image" src="https://github.com/user-attachments/assets/a59fadfc-eaa9-4eb5-b9b0-f0013396fbc6" />


Works on **Linux**, **WSL**, and **macOS** (Docker Desktop) with a single script.

![Python](https://img.shields.io/badge/python-3.6+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

---

## Features

- System memory usage (total / used / available / free)
- Docker networks overview with **Utilized** column (shows how many containers use each network)
- Container-to-network mapping
- Per-container resource usage (CPU %, Memory, PIDs)
- Sorted by memory usage (highest consumers first)
- Clean, readable terminal output
- **Zero external dependencies** — pure Python + Docker CLI

---

## Supported Platforms

- Linux (Ubuntu, Debian, Fedora, Arch, Jetson, Raspberry Pi OS, etc.)
- WSL (Windows Subsystem for Linux)
- macOS (with Docker Desktop)

---

## Requirements

- Python 3.6+
- Docker installed and running
- User has permission to run `docker` commands (add user to `docker` group recommended)

---
