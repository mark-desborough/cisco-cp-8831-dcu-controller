"""
Cisco 8831 DCU Library - Display, keypress, and LED control
Manages USB communication and dirty row tracking for efficient updates
Improved with debug mode, sleep messaging, and responsive controls
"""
import usb.core
import usb.util
import threading
import time
import struct
from queue import Queue
from PIL import Image, ImageFont, ImageDraw
 
VID = 0x1cbe
PID = 0x0009
WIDTH = 396
HEIGHT = 162
 
class LCDDisplay:
    """LCD Display control"""
    
    def __init__(self, ep_out, ep_in=None, debug=False):
        self.ep_out = ep_out
        self.ep_in = ep_in
        self.previous_screen = None
        self.lock = threading.Lock()
        self.debug = debug
    
    def screen(self, img):
        """
        Update LCD screen with a PIL Image.
        Only sends rows that have changed (dirty row tracking).
        
        Args:
            img: PIL Image (1-bit, 396x162)
        """
        if img.size != (WIDTH, HEIGHT):
            raise ValueError(f"Image must be {WIDTH}x{HEIGHT}, got {img.size}")
        
        with self.lock:
            # Convert image to framebuffer
            fb = self._image_to_framebuffer(img)
            
            # Send only changed rows
            if self.previous_screen is None:
                # First screen, send all rows
                dirty_rows = list(range(HEIGHT))
                if self.debug:
                    print(f"[DEBUG LCD] Sending all {HEIGHT} rows (first screen)")
            else:
                # Find dirty rows
                dirty_rows = []
                for row in range(HEIGHT):
                    if fb[row] != self.previous_screen[row]:
                        dirty_rows.append(row)
                if self.debug and dirty_rows:
                    print(f"[DEBUG LCD] Updating {len(dirty_rows)} dirty rows")
            
            # Send dirty rows
            if dirty_rows:
                for row in dirty_rows:
                    pkt = self._make_packet(row, fb[row])
                    self.ep_out.write(pkt)
            
            # Store current screen as previous
            self.previous_screen = [row[:] for row in fb]
    
    def contrast(self, level):
        """Set LCD contrast (0-255, effectively 0-31)"""
        level = max(0, min(255, level))
        payload = struct.pack("<H", level)
        self._send_command(0x4C, payload)
        if self.debug:
            print(f"[DEBUG LCD] Contrast set to {level}")
    
    def backlight(self, state):
        """Turn backlight on (1) or off (0)"""
        state = 1 if state else 0
        payload = struct.pack("<H", state)
        self._send_command(0x4A, payload)
        if self.debug:
            print(f"[DEBUG LCD] Backlight {'ON' if state else 'OFF'}")
    
    def clear(self):
        """Clear the display"""
        blank = Image.new('1', (WIDTH, HEIGHT), 0)
        self.screen(blank)
    
    # Private methods
    
    def _image_to_framebuffer(self, img):
        """Convert PIL image to framebuffer with reversal"""
        fb = [[0] * WIDTH for _ in range(HEIGHT)]
        pixels = img.load()
        for y in range(HEIGHT):
            for x in range(WIDTH):
                fb[y][x] = pixels[x, y]
            # Reverse for display orientation
            fb[y] = fb[y][::-1]
        return fb
    
    def _pack_row(self, pixels):
        """Pack 396 pixels into 50 bytes"""
        out = bytearray()
        pixels.reverse()
        pixel_list = list(pixels[:WIDTH])[::-1]
        pixel_list += [0] * (400 - WIDTH)
        pixel_list = pixel_list[:400]
        
        for x in range(0, 400, 8):
            b = 0
            for bit in range(8):
                if pixel_list[x + bit]:
                    b |= (0x80 >> bit)
            out.append(b)
        
        return out
    
    def _make_packet(self, row, pixels):
        """Create USB packet for display row"""
        pkt = bytearray(64)
        pkt[0] = 0x42
        pkt[1] = 0x00
        pkt[2] = 0x40
        pkt[3] = 0x00
        pkt[4] = 0x00
        pkt[5] = 0x00
        pkt[6] = row & 0xff
        pkt[7] = row >> 8
        pkt[8] = 0x8c
        pkt[9] = 0x01
        pkt[10:60] = self._pack_row(pixels)
        return pkt
    
    def _send_command(self, cmd, payload=b""):
        """Send a command packet"""
        pkt = bytearray(64)
        struct.pack_into("<H", pkt, 0, cmd)
        struct.pack_into("<H", pkt, 2, 64)
        pkt[4:4+len(payload)] = payload
        try:
            self.ep_out.write(pkt)
        except Exception as e:
            print(f"Error sending command 0x{cmd:02X}: {e}")
 
 
class LEDControl:
    """LED control (mute indicator)"""
    
    def __init__(self, ep_out, debug=False):
        self.ep_out = ep_out
        self.debug = debug
    
    def mute(self, color):
        """
        Control mute LED.
        
        Args:
            color: 'red' for muted, 'off' for unmuted, or color value
        """
        if isinstance(color, str):
            if color.lower() == 'red':
                value = 0xFF0000  # Red
            elif color.lower() == 'off':
                value = 0x000000  # Off
            else:
                raise ValueError(f"Unknown color: {color}")
        else:
            value = color & 0xFFFFFF
        
        payload = struct.pack("<I", value)
        self._send_led_command(0x50, payload)
        if self.debug:
            print(f"[DEBUG LED] Set to {color}")
    
    def _send_led_command(self, cmd, payload):
        """Send LED command"""
        pkt = bytearray(64)
        struct.pack_into("<H", pkt, 0, cmd)
        struct.pack_into("<H", pkt, 2, 64)
        pkt[4:4+len(payload)] = payload
        try:
            self.ep_out.write(pkt)
        except Exception as e:
            print(f"Error sending LED command: {e}")
 
 
class KeypressListener:
    """Keypress listener - yields keypress events"""
    
    # Key mappings - Cisco 8831 DCU buttons
    KEY_MAP = {
        0x00: '1', 0x01: '2', 0x02: '3',
        0x05: '4', 0x06: '5', 0x07: '6',
        0x0a: '7', 0x0b: '8', 0x0c: '9',
        0x0f: 'star', 0x10: '0', 0x11: 'hash',
        0x04: 'up', 0x09: 'enter', 0x0e: 'down',
        0x03: 'top1', 0x08: 'top2', 0x0d: 'top3', 0x12: 'top4',
        0x14: 'volume_up', 0x15: 'volume_down',
        0x13: 'speaker',
        0x16: 'mute',
    }
    
    def __init__(self, ep_in, debug=False):
        self.ep_in = ep_in
        self.queue = Queue()
        self.running = True
        self.shutdown_event = threading.Event()
        self.last_key = None
        self.last_key_time = 0
        self.debug = debug
        self.thread = threading.Thread(target=self._listen, daemon=True)
        self.thread.start()
    
    def get(self, timeout=0.2):
        """
        Get next keypress event (non-blocking with timeout).
        
        Returns:
            dict with keys: {'key': key_name, 'code': 0xNN}
            or None on timeout
        """
        try:
            return self.queue.get(timeout=timeout)
        except:
            return None
    
    def stop(self):
        """Stop listening for keypresses"""
        self.running = False
        self.shutdown_event.set()
        # Wait for thread to exit (it uses 100ms USB timeout)
        self.thread.join(timeout=0.5)
    
    def _listen(self):
        """Background thread for listening to keypresses"""
        while self.running:
            try:
                # Use short timeout so shutdown is responsive
                data = self.ep_in.read(64, timeout=50)
                if len(data) >= 7 and not self.shutdown_event.is_set():
                    key_code = data[4]
                    is_pressed = (data[6] == 0x01)
                    
                    if is_pressed:
                        # Debounce: ignore same key within 50ms
                        current_time = time.time()
                        if (self.last_key != key_code or 
                            current_time - self.last_key_time > 0.05):
                            self.last_key = key_code
                            self.last_key_time = current_time
                            
                            key_name = self.KEY_MAP.get(key_code, f"0x{key_code:02X}")
                            event = {'key': key_name, 'code': key_code}
                            self.queue.put(event)
                            
                            if self.debug:
                                print(f"[DEBUG KEY] Pressed: {key_name} (0x{key_code:02X})")
            
            except usb.core.USBTimeoutError:
                pass
            except Exception as e:
                if self.running and not self.shutdown_event.is_set():
                    print(f"Keypress listener error: {e}")
                break
 
 
class CiscoDCU:
    """
    Cisco 8831 DCU - Main control class
    
    Usage (automatic cleanup with context manager):
        with CiscoDCU() as dcu:
            dcu.debug(True)
            screen = build_pil_image()
            dcu.lcd.screen(screen)
            
            while True:
                event = dcu.get_keypress()  # 0.2s timeout (responsive to Ctrl+C)
                if event:
                    print(f"Pressed: {event['key']}")
    
    Usage (manual cleanup):
        dcu = CiscoDCU()
        dcu.debug(True)
        
        # Display
        screen = build_pil_image()
        dcu.lcd.screen(screen)
        dcu.lcd.contrast(15)
        dcu.lcd.backlight(1)
        dcu.lcd.clear()
        
        # Keypresses (0.2s default timeout for responsive Ctrl+C)
        event = dcu.get_keypress()  # Returns {'key': 'top1', 'code': 0x0f}
        event = dcu.get_keypress(timeout=5)  # Custom timeout
        
        # LED
        dcu.led.mute('red')
        dcu.led.mute('off')
        
        # Sleep/wake support
        dcu.set_sleep_screen()  # Show "sleeping" message and turn off
        dcu.wake_from_sleep()   # Wake and restore previous screen
        
        # Cleanup
        dcu.close()
    """
    
    def __init__(self):
        self.dev = None
        self.ep_in = None
        self.ep_out = None
        self.lcd = None
        self.led = None
        self.keypress = None
        self.debug_mode = False
        self.shutdown_event = threading.Event()
        self.previous_screen = None
        self.is_sleeping = False
        
        self._connect()
        self._flush_input_buffer()
        self._startup_sequence()
    
    def debug(self, enable=True):
        """Enable/disable debug logging"""
        self.debug_mode = enable
        if self.keypress:
            self.keypress.debug = enable
        if self.lcd:
            self.lcd.debug = enable
        if self.led:
            self.led.debug = enable
        if enable:
            print("[DEBUG] Debug mode enabled")
    
    def _log(self, msg):
        """Print debug message"""
        if self.debug_mode:
            print(f"[DEBUG] {msg}")
    
    @property
    def is_connected(self):
        """Check if device is connected and not shutting down"""
        return not self.shutdown_event.is_set() and self.dev is not None
    
    def get_keypress(self, timeout=0.2):
        """
        Get next keypress event (with short default timeout for responsiveness).
        
        Args:
            timeout: Wait time in seconds (default 0.2s for instant Ctrl+C response)
        
        Returns:
            dict: {'key': key_name, 'code': 0xNN}
            None: on timeout or shutdown
        """
        if self.shutdown_event.is_set():
            return None
        return self.keypress.get(timeout=timeout)
    
    def set_sleep_screen(self, show_message=True):
        """Put display to sleep with optional message"""
        if not self.is_sleeping:
            self._log("Display sleeping")
            self.is_sleeping = True
            
            # Save current screen before sleeping
            if self.lcd.previous_screen:
                self.previous_screen = self.lcd.previous_screen
            
            if show_message:
                img = Image.new('1', (WIDTH, HEIGHT), 0)
                draw = ImageDraw.Draw(img)
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 16)
                except:
                    font = ImageFont.load_default()
                draw.text((140, 75), "sleeping...", font=font, fill=1)
                self.lcd.screen(img)
            
            self.lcd.backlight(0)
    
    def wake_from_sleep(self, restore_screen=True):
        """Wake display from sleep"""
        if self.is_sleeping:
            self._log("Display waking")
            self.lcd.backlight(1)
            self.is_sleeping = False
            
            if restore_screen and self.previous_screen is not None:
                self._log("Restoring previous screen")
                self.lcd.screen(self.previous_screen)
    
    def close(self):
        """Close connection and clean up - can be called multiple times safely"""
        if self.shutdown_event.is_set():
            return  # Already closed
        
        self._log("Shutting down")
        self.shutdown_event.set()
        
        if self.keypress:
            try:
                self.keypress.stop()
            except:
                pass
        
        if self.dev:
            try:
                self.dev = None
            except:
                pass
        
        print("Disconnected from Cisco 8831 DCU")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures cleanup"""
        self.close()
        return False  # Don't suppress exceptions
    
    def __del__(self):
        """Ensure cleanup on object deletion"""
        try:
            self.close()
        except:
            pass
    
    # Private methods
    
    def _connect(self):
        """Connect to USB device"""
        self._log("Scanning for Cisco 8831 DCU...")
        
        self.dev = usb.core.find(idVendor=VID, idProduct=PID)
        if self.dev is None:
            raise RuntimeError(f"Cisco 8831 DCU not found (VID=0x{VID:04x}, PID=0x{PID:04x})")
        
        cfg = self.dev.get_active_configuration()
        intf = cfg[(0, 0)]
        
        self.ep_in = usb.util.find_descriptor(
            intf,
            custom_match=lambda e:
                usb.util.endpoint_direction(e.bEndpointAddress)
                == usb.util.ENDPOINT_IN)
        
        self.ep_out = usb.util.find_descriptor(
            intf,
            custom_match=lambda e:
                usb.util.endpoint_direction(e.bEndpointAddress)
                == usb.util.ENDPOINT_OUT)
        
        print(f"Connected to Cisco 8831 DCU")
        self._log(f"IN endpoint:  {hex(self.ep_in.bEndpointAddress)}")
        self._log(f"OUT endpoint: {hex(self.ep_out.bEndpointAddress)}")
        
        # Initialize sub-objects with debug mode
        self.lcd = LCDDisplay(self.ep_out, self.ep_in, debug=self.debug_mode)
        self.led = LEDControl(self.ep_out, debug=self.debug_mode)
        self.keypress = KeypressListener(self.ep_in, debug=self.debug_mode)
    
    def _flush_input_buffer(self):
        """Clear any buffered keypresses from before connection"""
        self._log("Flushing input buffer...")
        cleared = 0
        try:
            while True:
                data = self.ep_in.read(64, timeout=50)
                if data:
                    cleared += 1
                else:
                    break
        except usb.core.USBTimeoutError:
            pass
        
        if cleared > 0:
            print(f"Cleared {cleared} buffered packet(s)")
        else:
            self._log("Buffer was empty")
    
    def _startup_sequence(self):
        """Initialize display on startup"""
        self._log("Running startup sequence...")
        self.lcd.backlight(1)
        self.lcd.clear()
        self.lcd.contrast(15)
        print("Startup complete")
 
 
# Convenience function for quick setup
def connect(debug=False):
    """Connect to Cisco 8831 DCU"""
    dcu = CiscoDCU()
    if debug:
        dcu.debug(True)
    return dcu
 
 
if __name__ == "__main__":
    # Example usage
    print("Cisco 8831 DCU Library")
    print("Import this module in your code:")
    print("  from cisco_8831_dcu import CiscoDCU")
    print("  dcu = CiscoDCU()")
    print("  dcu.debug(True)  # Enable debug logging")
