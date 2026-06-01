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


# Example Output
```
=== Docker Resource Monitor - 2026-06-01 17:50:12 ===

System Total     : 7.40 GiB
System Used      : 4.82 GiB
System Available : 2.58 GiB
System Free      : 1.12 GiB

=== Docker Networks ===
Name                          Driver       Scope      Utilized
------------------------------------------------------------
alfred-net                    bridge       local           5
bridge                        bridge       local           -
host                          host         local           -
none                          null         local           -

=== Container / Network Mapping ===
Container                 Networks
------------------------------------------------------------
n8n                       alfred-net
hermes-agent              alfred-net
ngrok                     alfred-net
brain-piper-tts           alfred-net
brain-faster-whisper      alfred-net
llama-server              bridge

=== Docker Containers ===
Container            CPU %      Memory Usage                 Mem %      PIDs
--------------------------------------------------------------------------------
hermes-agent         12.5%      1.24GiB / 7.40GiB            16.8%      12
n8n                  8.3%       892MiB / 7.40GiB             11.8%      18
llama-server         45.2%      2.18GiB / 7.40GiB            29.5%      9
brain-piper-tts      3.1%       124MiB / 7.40GiB             1.6%       4
ngrok                0.8%       38.4MiB / 7.40GiB            0.5%       3
brain-faster-whisper 2.4%       87.2MiB / 7.40GiB            1.2%       5
--------------------------------------------------------------------------------
Total containers : 6
Docker Total     : 4.56 GiB
Non-Docker       : 0.26 GiB
Combined         : 4.82 GiB / 7.40 GiB
```
