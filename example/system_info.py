#!/usr/bin/env python3
"""
System Information Display for Cisco 8831 DCU
Real-time system monitoring with CPU, memory, disk, and network info
Press buttons to cycle through different info screens
"""
import time
import threading
import platform
import os
import subprocess
import psutil
from PIL import Image, ImageDraw, ImageFont
from cisco_8831_dcu import CiscoDCU

WIDTH = 396
HEIGHT = 162

def get_monospace_font(size):
    """Load a monospace font"""
    font_names = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        "/usr/share/fonts/truetype/ubuntu-mono/UbuntuMono-R.ttf",
    ]

    for font_path in font_names:
        try:
            return ImageFont.truetype(font_path, size)
        except:
            continue
    return ImageFont.load_default()

def get_distro_name():
    """Get Linux distribution name"""
    try:
        return platform.linux_distribution()[0] or "Linux"
    except:
        try:
            result = subprocess.run(['lsb_release', '-ds'], capture_output=True, text=True)
            return result.stdout.strip().strip('"')
        except:
            return platform.system()

def get_hostname():
    """Get system hostname"""
    return platform.node()

def get_kernel():
    """Get kernel version"""
    return platform.release()

def get_uptime():
    """Get system uptime"""
    uptime_seconds = time.time() - psutil.boot_time()
    days = int(uptime_seconds // 86400)
    hours = int((uptime_seconds % 86400) // 3600)
    minutes = int((uptime_seconds % 3600) // 60)

    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"

def create_info_screen():
    """Main info screen - system overview - larger and more horizontal"""
    img = Image.new('1', (WIDTH, HEIGHT), 0)
    draw = ImageDraw.Draw(img)
    font_small = get_monospace_font(13)
    font_med = get_monospace_font(18)
    font_big = get_monospace_font(22)

    # Hostname - VERY BIG
    hostname = get_hostname()[:20]
    draw.text((10, 5), hostname, font=font_big, fill=1)

    # Divider
    draw.line([(10, 32), (385, 32)], fill=1)

    # Left column
    y = 40
    distro = get_distro_name()[:18]
    draw.text((10, y), f"OS: {distro}", font=font_small, fill=1)
    y += 16

    kernel = get_kernel()[:16]
    draw.text((10, y), f"Kernel: {kernel}", font=font_small, fill=1)
    y += 16

    uptime = get_uptime()
    draw.text((10, y), f"Uptime: {uptime}", font=font_small, fill=1)

    # Right column
    y = 40
    cpu_count = psutil.cpu_count()
    draw.text((210, y), f"CPUs: {cpu_count}", font=font_small, fill=1)
    y += 16

    mem = psutil.virtual_memory()
    mem_gb = mem.total / (1024**3)
    draw.text((210, y), f"RAM: {mem_gb:.1f}GB", font=font_small, fill=1)

    # Bottom bar - live stats
    draw.line([(10, 118), (385, 118)], fill=1)

    cpu_percent = psutil.cpu_percent(interval=0)
    mem_percent = mem.percent
    draw.text((10, 125), f"CPU: {cpu_percent:5.1f}%     MEM: {mem_percent:5.1f}%",
              font=font_med, fill=1)

    return img

def create_cpu_screen():
    """Detailed CPU information - large horizontal layout"""
    img = Image.new('1', (WIDTH, HEIGHT), 0)
    draw = ImageDraw.Draw(img)
    font_title = get_monospace_font(18)
    font_cpu = get_monospace_font(14)

    # Title
    draw.text((10, 5), "CPU LOAD", font=font_title, fill=1)

    # Overall usage - BIG
    cpu_total = psutil.cpu_percent(interval=0)
    draw.text((140, 8), f"{cpu_total:.0f}%", font=font_title, fill=1)

    # Bar graph for total
    bar_y = 35
    bar_width = 360
    bar_height = 12
    bar_fill = int((cpu_total / 100) * bar_width)
    draw.rectangle((10, bar_y, 10+bar_width, bar_y+bar_height), outline=1)
    if bar_fill > 0:
        draw.rectangle((10, bar_y, 10+bar_fill, bar_y+bar_height), fill=1)

    # Per-core usage in columns
    cpu_counts = psutil.cpu_percent(percpu=True, interval=0.1)

    # Display cores in 2 columns to span horizontally
    col_width = WIDTH // 2
    x_positions = [10, 10 + col_width]

    y = 60
    col = 0
    for i, cpu_percent in enumerate(cpu_counts[:12]):  # Show up to 12 cores
        if i > 0 and i % 6 == 0:  # Switch column after 6 cores
            col = 1
            y = 60

        x = x_positions[col]

        # Core label and percentage
        draw.text((x, y), f"C{i}:{cpu_percent:5.1f}%", font=font_cpu, fill=1)
        y += 16

    if len(cpu_counts) > 12:
        draw.text((10, 145), f"+{len(cpu_counts)-12} more cores", font=font_cpu, fill=1)

    return img

def create_memory_screen():
    """Detailed memory information - larger and wider"""
    img = Image.new('1', (WIDTH, HEIGHT), 0)
    draw = ImageDraw.Draw(img)
    font_small = get_monospace_font(13)
    font_title = get_monospace_font(18)

    # Title
    draw.text((10, 5), "SYSTEM MEMORY", font=font_title, fill=1)
    draw.line([(10, 28), (385, 28)], fill=1)

    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()

    y = 35

    # RAM - LARGE
    total_gb = mem.total / (1024**3)
    used_gb = mem.used / (1024**3)
    draw.text((10, y), f"RAM:  {used_gb:.1f}GB / {total_gb:.1f}GB", font=font_small, fill=1)
    y += 16

    # RAM percentage bar - BIG
    bar_width = 360
    bar_height = 14
    bar_fill = int((mem.percent / 100) * bar_width)
    draw.rectangle((10, y, 10+bar_width, y+bar_height), outline=1)
    if bar_fill > 0:
        draw.rectangle((10, y, 10+bar_fill, y+bar_height), fill=1)
    draw.text((330, y+1), f"{mem.percent:.0f}%", font=font_small, fill=1)
    y += 20

    # Swap
    if swap.total > 0:
        swap_gb = swap.total / (1024**3)
        swap_used = swap.used / (1024**3)
        draw.text((10, y), f"SWAP: {swap_used:.1f}GB / {swap_gb:.1f}GB", font=font_small, fill=1)
        y += 16

        # Swap bar
        bar_fill = int((swap.percent / 100) * bar_width) if swap.percent else 0
        draw.rectangle((10, y, 10+bar_width, y+bar_height), outline=1)
        if bar_fill > 0:
            draw.rectangle((10, y, 10+bar_fill, y+bar_height), fill=1)
        draw.text((330, y+1), f"{swap.percent:.0f}%", font=font_small, fill=1)
        y += 20

    # Available
    avail_gb = mem.available / (1024**3)
    draw.text((10, y), f"Available: {avail_gb:.1f}GB", font=font_small, fill=1)

    return img

def create_disk_screen():
    """Disk usage information - larger and wider"""
    img = Image.new('1', (WIDTH, HEIGHT), 0)
    draw = ImageDraw.Draw(img)
    font_small = get_monospace_font(12)
    font_title = get_monospace_font(18)

    # Title
    draw.text((10, 5), "DISK USAGE", font=font_title, fill=1)
    draw.line([(10, 28), (385, 28)], fill=1)

    # Get all mounted filesystems
    partitions = psutil.disk_partitions()

    y = 35
    bar_height = 12

    for partition in partitions[:3]:  # Show first 3 mounts (more vertical space)
        try:
            usage = psutil.disk_usage(partition.mountpoint)

            # Mount point and size
            mount = partition.mountpoint.replace('/mnt/', '').replace('/media/', '')
            if len(mount) > 20:
                mount = mount[:20]
            total_gb = usage.total / (1024**3)
            used_gb = usage.used / (1024**3)

            draw.text((10, y), f"{mount}:", font=font_small, fill=1)
            y += 13

            # Usage info
            percent = usage.percent
            draw.text((10, y), f"{used_gb:.1f}GB / {total_gb:.1f}GB ({percent:.0f}%)",
                     font=font_small, fill=1)
            y += 13

            # Usage bar - LARGE
            bar_width = 360
            bar_fill = int((percent / 100) * bar_width)
            draw.rectangle((10, y, 10+bar_width, y+bar_height), outline=1)
            if bar_fill > 0:
                draw.rectangle((10, y, 10+bar_fill, y+bar_height), fill=1)

            y += 18

        except:
            continue

    return img

def create_network_screen():
    """Network information - wider horizontal layout"""
    img = Image.new('1', (WIDTH, HEIGHT), 0)
    draw = ImageDraw.Draw(img)
    font_small = get_monospace_font(11)
    font_title = get_monospace_font(18)

    # Title
    draw.text((10, 5), "NETWORK", font=font_title, fill=1)
    draw.line([(10, 28), (385, 28)], fill=1)

    # Network interfaces
    interfaces = psutil.net_if_addrs()

    y = 35
    for iface_name in list(interfaces.keys())[:6]:  # Show first 6 interfaces
        addrs = interfaces[iface_name]

        # Interface name - bold/prominent
        draw.text((10, y), f"{iface_name}:", font=font_small, fill=1)
        y += 12

        # Show first IPv4 and IPv6
        ipv4_shown = False
        ipv6_shown = False

        for addr in addrs:
            if addr.family.name == 'AF_INET' and not ipv4_shown:
                draw.text((15, y), f"IPv4: {addr.address}", font=font_small, fill=1)
                y += 11
                ipv4_shown = True
            elif addr.family.name == 'AF_INET6' and not ipv6_shown:
                # Show shortened IPv6
                short_ipv6 = addr.address.split('%')[0][:22]
                draw.text((15, y), f"IPv6: {short_ipv6}", font=font_small, fill=1)
                y += 11
                ipv6_shown = True

            if ipv4_shown and ipv6_shown:
                break

    return img

class NeofetchDisplay:
    """Neofetch-style display controller"""

    def __init__(self, dcu):
        self.dcu = dcu
        self.screens = [
            ('Info', create_info_screen),
            ('CPU', create_cpu_screen),
            ('Memory', create_memory_screen),
            ('Disk', create_disk_screen),
            ('Network', create_network_screen),
        ]
        self.current_screen = 0
        self.running = True
        self.last_update = {}
        self.cache_intervals = {
            0: 2.0,      # Info: update every 2 seconds
            1: 1.0,      # CPU: update every 1 second (fast data)
            2: 3.0,      # Memory: update every 3 seconds
            3: 5.0,      # Disk: update every 5 seconds (slow data)
            4: 5.0,      # Network: update every 5 seconds (slow data)
        }
        # Initialize all screens with last_update timestamp
        for i in range(len(self.screens)):
            self.last_update[i] = 0

    def show_current(self):
        """Display current screen"""
        screen_func = self.screens[self.current_screen][1]
        img = screen_func()
        self.dcu.lcd.screen(img)
        self.last_update[self.current_screen] = time.time()

    def should_refresh(self):
        """Check if current screen should be refreshed"""
        screen_idx = self.current_screen
        cache_interval = self.cache_intervals.get(screen_idx, 3.0)
        time_since_update = time.time() - self.last_update.get(screen_idx, 0)
        return time_since_update > cache_interval

    def next_screen(self):
        """Go to next screen"""
        self.current_screen = (self.current_screen + 1) % len(self.screens)
        self.show_current()

    def prev_screen(self):
        """Go to previous screen"""
        self.current_screen = (self.current_screen - 1) % len(self.screens)
        self.show_current()

    def handle_keypress(self, event):
        """Handle keypress events"""
        key = event['key']

        if key in ['up', 'top1']:
            self.prev_screen()
        elif key in ['down', 'top2']:
            self.next_screen()
        elif key == 'enter':
            self.show_current()  # Refresh immediately
        elif key == 'volume_up':
            new_contrast = min(255, self.dcu.lcd.contrast_level + 10)
            self.dcu.lcd.contrast(new_contrast)
            self.dcu.lcd.contrast_level = new_contrast
        elif key == 'volume_down':
            new_contrast = max(0, self.dcu.lcd.contrast_level - 10)
            self.dcu.lcd.contrast(new_contrast)
            self.dcu.lcd.contrast_level = new_contrast

    def run(self):
        """Main display loop"""
        print("Starting System Information display...")
        print("Screens: Info → CPU → Memory → Disk → Network")
        print("Controls:")
        print("  UP/Top1: Previous screen")
        print("  DOWN/Top2: Next screen")
        print("  ENTER: Refresh current screen")
        print("  Vol +/-: Adjust contrast")
        print("  Ctrl+C: Exit")
        print()

        # Initialize contrast tracking
        self.dcu.lcd.contrast_level = 15

        self.show_current()

        try:
            while self.running and self.dcu.is_connected:
                try:
                    # Use short timeout for responsive Ctrl+C
                    event = self.dcu.get_keypress(timeout=0.2)

                    if event:
                        self.handle_keypress(event)
                    else:
                        # Refresh current screen if cache interval has passed
                        if self.should_refresh():
                            self.show_current()
                        else:
                            time.sleep(0.05)  # Minimal sleep to avoid busy loop

                except KeyboardInterrupt:
                    raise  # Re-raise to outer try/except
                except Exception as e:
                    print(f"Error: {e}")
                    time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nShutting down...")
            self.running = False

def main():
    """Main entry point - System Information Display"""
    try:
        print("Connecting to Cisco 8831 DCU...")
        with CiscoDCU() as dcu:
            # Uncomment for debug output:
            # dcu.debug(True)

            display = NeofetchDisplay(dcu)
            display.run()

    except KeyboardInterrupt:
        print("\nShutdown requested")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Done")

if __name__ == "__main__":
    # Ensure Ctrl+C works properly
    import signal
    signal.signal(signal.SIGINT, signal.default_int_handler)

    main()
