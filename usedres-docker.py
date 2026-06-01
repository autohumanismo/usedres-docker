#!/usr/bin/env python3
"""

usedres-docker.py - Used Resources by Docker

Should works on: Linux, WSL, macOS (Docker Desktop)

Author: x.com/autohumanismo
License: MIT

version 0.1

"""

import subprocess
import json
from datetime import datetime
from collections import defaultdict


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


def get_system_memory():
    """Portable memory info (Linux/WSL + macOS fallback)"""
    # Try Linux first (including WSL)
    try:
        result = subprocess.run(['free', '-b'], capture_output=True, text=True, check=True)
        lines = result.stdout.strip().split('\n')
        mem_line = lines[1].split()
        total = int(mem_line[1]) / (1024**3)
        used = int(mem_line[2]) / (1024**3)
        free = int(mem_line[3]) / (1024**3)
        available = int(mem_line[6]) / (1024**3)
        return {
            'total': round(total, 2),
            'used': round(used, 2),
            'free': round(free, 2),
            'available': round(available, 2)
        }
    except:
        pass

    # Fallback for macOS
    try:
        # Get total physical memory
        total_result = subprocess.run(['sysctl', '-n', 'hw.memsize'], capture_output=True, text=True, check=True)
        total_bytes = int(total_result.stdout.strip())
        total = total_bytes / (1024**3)

        # Get memory usage via vm_stat
        vm_result = subprocess.run(['vm_stat'], capture_output=True, text=True, check=True)
        vm_lines = vm_result.stdout.strip().split('\n')

        page_size = 4096  # default, will try to detect
        for line in vm_lines:
            if 'page size of' in line:
                page_size = int(line.split()[-2])
                break

        free_pages = 0
        for line in vm_lines:
            if 'Pages free:' in line:
                free_pages = int(line.split(':')[1].strip().replace('.', ''))
            elif 'Pages speculative:' in line:
                free_pages += int(line.split(':')[1].strip().replace('.', ''))

        used = (total_bytes - (free_pages * page_size)) / (1024**3)
        free = (free_pages * page_size) / (1024**3)
        available = free

        return {
            'total': round(total, 2),
            'used': round(used, 2),
            'free': round(free, 2),
            'available': round(available, 2)
        }
    except:
        return None


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

    # System Memory
    sys_mem = get_system_memory()
    if sys_mem:
        print(f"System Total     : {sys_mem['total']} GiB")
        print(f"System Used      : {sys_mem['used']} GiB")
        print(f"System Available : {sys_mem['available']} GiB")
        print(f"System Free      : {sys_mem['free']} GiB\n")
    else:
        print("System memory: Not available on this platform\n")

    # Docker Networks with Utilized count
    networks = get_docker_networks()
    container_nets = get_container_networks()

    network_count = defaultdict(int)
    for c in container_nets:
        for net in c['networks'].split(','):
            net = net.strip()
            if net:
                network_count[net] += 1

    if networks:
        print("=== Docker Networks ===")
        print(f"{'Name':<28} {'Driver':<12} {'Scope':<10} {'Utilized':>8}")
        print("-" * 60)
        for net in networks:
            util = network_count.get(net['name'], 0)
            util_str = str(util) if util > 0 else "-"
            print(f"{net['name']:<28} {net['driver']:<12} {net['scope']:<10} {util_str:>8}")
        print("-" * 60)
        print(f"Total networks: {len(networks)}\n")

    # Container / Network Mapping
    if container_nets:
        print("=== Container / Network Mapping ===")
        print(f"{'Container':<22} {'Networks'}")
        print("-" * 60)
        for c in container_nets:
            print(f"{c['name']:<22} {c['networks']}")
        print("-" * 60)
        print()

    # Docker Containers (sorted by memory)
    containers = get_docker_stats()
    if not containers:
        print("No running containers found.")
        return

    containers.sort(key=lambda x: mem_to_mb(x['mem_usage']), reverse=True)

    print(f"{'Container':<20} {'CPU %':<10} {'Memory Usage':<28} {'Mem %':<10} {'PIDs'}")
    print("-" * 88)
    docker_total_mb = 0.0
    for c in containers:
        name = c['name'][:19]
        mem_str = c['mem_usage']
        print(f"{name:<20} {c['cpu']:<10} {mem_str:<28} {c['mem_perc']:<10} {c['pids']}")
        docker_total_mb += mem_to_mb(mem_str)

    docker_total_gib = docker_total_mb / 1024
    print("-" * 88)
    print(f"Total containers : {len(containers)}")
    print(f"Docker Total     : {docker_total_gib:.2f} GiB")

    if sys_mem:
        non_docker = sys_mem['used'] - docker_total_gib
        print(f"Non-Docker       : {non_docker:.2f} GiB")
        print(f"Combined         : {sys_mem['used']:.2f} GiB / {sys_mem['total']:.2f} GiB")


if __name__ == "__main__":
    main()
