#!/usr/bin/env python3
"""
usedres-docker.py - Used Resources by Docker

Author: x.com/autohumanismo
License: MIT
version 1.6
"""

import subprocess
import json
from datetime import datetime
from collections import defaultdict


def format_ram_gib_or_mib(gib: float) -> str:
    if gib >= 1.0:
        return f"{gib:.2f} GiB"
    else:
        mib = gib * 1024
        return f"{mib:.0f} MiB"


def parse_mem_limit(mem_str: str) -> float:
    try:
        if '/' not in mem_str:
            return 0.0
        limit_part = mem_str.split('/')[1].strip()
        if 'GiB' in limit_part:
            return float(limit_part.replace('GiB', ''))
        elif 'MiB' in limit_part:
            return float(limit_part.replace('MiB', '')) / 1024
        return 0.0
    except:
        return 0.0


def get_block_bar(percent: str) -> str:
    try:
        p = float(percent.strip('%'))
        if p < 1.0:
            return " "
        elif p >= 87.5:
            return "█"
        elif p >= 75.0:
            return "▇"
        elif p >= 62.5:
            return "▆"
        elif p >= 50.0:
            return "▅"
        elif p >= 37.5:
            return "▄"
        elif p >= 25.0:
            return "▃"
        elif p >= 12.5:
            return "▂"
        else:
            return "▁"
    except:
        return " "


def create_memory_bar(total_gib: float, used_gib: float, free_gib: float, available_gib: float, width: int = 50):
    if total_gib <= 0:
        return "[" + "_" * width + "]"
    used_width = max(0, int((used_gib / total_gib) * width))
    avail_width = max(0, int((available_gib / total_gib) * width))
    free_width = width - used_width - avail_width

    if free_gib > 0 and free_width < 1:
        free_width = 1
    if available_gib > 0 and avail_width < 1 and free_width > 1:
        avail_width = 1
        free_width -= 1

    bar = "░" * used_width + "⣿" * avail_width + "_" * free_width
    return f"[{bar}]"


def get_system_memory():
    try:
        result = subprocess.run(['free', '-b'], capture_output=True, text=True, check=True)
        lines = result.stdout.strip().split('\n')
        mem_line = lines[1].split()
        swap_line = lines[2].split() if len(lines) > 2 else None

        total = int(mem_line[1]) / (1024**3)
        used = int(mem_line[2]) / (1024**3)
        free = int(mem_line[3]) / (1024**3)
        available = int(mem_line[6]) / (1024**3) if len(mem_line) > 6 else 0

        swap_total = int(swap_line[1]) / (1024**3) if swap_line else 0
        swap_used = int(swap_line[2]) / (1024**3) if swap_line else 0

        return {
            'total': round(total, 2),
            'used': round(used, 2),
            'free': round(free, 2),
            'available': round(available, 2),
            'swap_total': round(swap_total, 2),
            'swap_used': round(swap_used, 2)
        }
    except:
        return None


def get_docker_stats():
    try:
        result = subprocess.run(
            ['docker', 'stats', '--no-stream', '--format', '{{json .}}'],
            capture_output=True, text=True, check=True
        )
        containers = []
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                data = json.loads(line)
                containers.append({
                    'name': data.get('Name', 'Unknown'),
                    'cpu': data.get('CPUPerc', 'N/A'),
                    'mem_usage': data.get('MemUsage', 'N/A'),
                    'mem_perc': data.get('MemPerc', 'N/A'),
                    'pids': data.get('PIDs', 'N/A')
                })
        return containers
    except Exception as e:
        print(f"Docker stats error: {e}")
        return []


def get_docker_networks():
    try:
        result = subprocess.run(
            ['docker', 'network', 'ls', '--format', '{{json .}}'],
            capture_output=True, text=True, check=True
        )
        networks = []
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                data = json.loads(line)
                networks.append({
                    'name': data.get('Name', 'Unknown'),
                    'driver': data.get('Driver', 'N/A'),
                    'scope': data.get('Scope', 'N/A')
                })
        return networks
    except Exception as e:
        print(f"Docker networks error: {e}")
        return []


def get_container_networks():
    try:
        result = subprocess.run(
            ['docker', 'ps', '--format', '{{json .}}'],
            capture_output=True, text=True, check=True
        )
        mapping = []
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                data = json.loads(line)
                name = data.get('Names', 'Unknown')
                nets = data.get('Networks', 'none')
                mapping.append({
                    'name': name,
                    'networks': nets
                })
        return mapping
    except Exception as e:
        print(f"Container networks error: {e}")
        return []


def mem_to_mb(mem_str):
    try:
        val = mem_str.split('/')[0].strip()
        if 'GiB' in val:
            return float(val.replace('GiB', '')) * 1024
        elif 'MiB' in val:
            return float(val.replace('MiB', ''))
        return 0.0
    except:
        return 0.0


def main():
    print(f"\n=== Docker Resource Monitor - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")

    sys_mem = get_system_memory()
    if sys_mem:
        print(f"System Used (░) / Total ([])    : {format_ram_gib_or_mib(sys_mem['used'])} / {format_ram_gib_or_mib(sys_mem['total'])}")
        print(f"System Available (⣿) / Free (_) : {format_ram_gib_or_mib(sys_mem['available'])} / {format_ram_gib_or_mib(sys_mem['free'])}")

        bar = create_memory_bar(sys_mem['total'], sys_mem['used'], sys_mem['free'], sys_mem['available'])
        print(bar)
        print()

    # === Docker Networks ===
    networks = get_docker_networks()
    container_nets = get_container_networks()

    net_to_containers = defaultdict(list)
    for c in container_nets:
        for net in c['networks'].split(','):
            net = net.strip()
            if net:
                net_to_containers[net].append(c['name'])

    if networks:
        print(f"=== Docker Networks ({len(networks)}) ===")
        print(f"{'Name':<22} {'Driver':<8} {'Scope':<8} Containers")
        print("-" * 80)
        for net in networks:
            name = net['name']
            driver = net['driver']
            scope = net['scope']
            cont_list = " ".join(sorted(net_to_containers.get(name, []))) if net_to_containers.get(name) else ""
            print(f"{name:<22} {driver:<8} {scope:<8} {cont_list}")
        print("-" * 80)
        print()

    # === Docker Containers ===
    containers = get_docker_stats()
    if not containers:
        print("No running containers found.")
        return

    containers.sort(key=lambda x: mem_to_mb(x['mem_usage']), reverse=True)

    print(f"=== Docker containers ({len(containers)}) ===")
    print(f"{'Container':<20} {'CPU %':<10} {'Memory Usage':<28} {'Mem %':<10} {'PIDs'}")
    print("-" * 80)
    docker_total_mb = 0.0
    docker_max_gib = 0.0
    for c in containers:
        name = c['name'][:19]
        mem_str = c['mem_usage']
        cpu_bar = get_block_bar(c['cpu'])
        mem_bar = get_block_bar(c['mem_perc'])

        print(f"{name:<20} {cpu_bar} {c['cpu']:<8} {mem_str:<28} {mem_bar} {c['mem_perc']:<8} {c['pids']}")
        docker_total_mb += mem_to_mb(mem_str)
        docker_max_gib += parse_mem_limit(mem_str)

    docker_total_gib = docker_total_mb / 1024

    print("-" * 80)
    print(f"Docker Total / Max : {docker_total_gib:.2f} GiB / {format_ram_gib_or_mib(docker_max_gib)}")

    if sys_mem:
        non_docker_gib = sys_mem['used'] - docker_total_gib
        print(f"Non-Docker         : {format_ram_gib_or_mib(non_docker_gib)}")
        print(f"Swap Used / Total  : {format_ram_gib_or_mib(sys_mem['swap_used'])} / {format_ram_gib_or_mib(sys_mem['swap_total'])}")


if __name__ == "__main__":
    main()


