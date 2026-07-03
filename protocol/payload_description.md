# CISCO 8831 DCU - USB PROTOCOL SPECIFICATION
Reverse-engineered USB device protocol for the Cisco 8831 Desk Camera Unit (DCU)
VID: 0x1cbe, PID: 0x0009
 
## DEVICE CONFIGURATION
- USB Version: 2.0
- Endpoint IN:  0x81 (64 bytes, keypress input)
- Endpoint OUT: 0x01 (64 bytes, commands/display output)
- Max Packet Size: 64 bytes

## LCD DISPLAY PROTOCOL
 
Command: 0x42 (Display Row Update)
----------------------------------
Packet Structure (64 bytes):
  Bytes 0-1:   Command ID (0x42, 0x00)
  Bytes 2-3:   Packet Length (0x40, 0x00) - always 64 bytes
  Bytes 4-5:   Reserved (0x00, 0x00)
  Bytes 6-7:   Row Number (little-endian uint16_t)
               Byte 6 = Row & 0xFF
               Byte 7 = Row >> 8
               Valid range: 0-161 (162 rows total)
  Bytes 8-9:   Fixed Values (0x8c, 0x01) - purpose unknown
  Bytes 10-59: Pixel Data (50 bytes = 400 bits)
               - Covers 396 pixels of display width (400 bits padded)
               - Bit format: MSB first (0x80 = leftmost pixel)
               - 8 pixels per byte
 
Display Specifications:
  - Resolution: 396 x 162 pixels
  - Monochrome: 1-bit (on/off only)
  - Color Depth: 1-bit per pixel
  - Refresh: Per-row updates (dirty row tracking possible)
Pixel Packing Algorithm:
  1. Start with 396 pixel values (0 or 1)
  2. Reverse pixel array (pixel[0] ← pixel[395])
  3. Pad with 4 zeros (400 bits total = 50 bytes)
  4. Pack 8 pixels per byte, MSB first
     byte[i] = pixel[7]<<7 | pixel[6]<<6 | ... | pixel[0]<<0
Example for single row update:
  Row 50: pkt[6] = 0x32, pkt[7] = 0x00 (50 in little-endian)
          pkt[10:60] = 50 bytes of packed pixel data
 
 
## CONTROL COMMANDS
 
Backlight Control (0x4A)
------------------------
Purpose: Control display backlight on/off
Packet:
  Bytes 0-1:   0x4A, 0x00
  Bytes 2-3:   0x40, 0x00
  Bytes 4-5:   Value (little-endian):
               - 0x0000 = OFF
               - 0x0001 = ON
               Note: Only accepts 0 or 1, NOT 0-255 PWM
  Bytes 6-63:  Unused (0x00)
 
Example:
  Turn ON:  [0x4A, 0x00, 0x40, 0x00, 0x01, 0x00, ...]
  Turn OFF: [0x4A, 0x00, 0x40, 0x00, 0x00, 0x00, ...]
 
 
Contrast Control (0x4C)
-----------------------
Purpose: Set LCD contrast level
Packet:
  Bytes 0-1:   0x4C, 0x00
  Bytes 2-3:   0x40, 0x00
  Bytes 4-5:   Level (little-endian):
               - Range: 0-255
               - Effective: Only lower 3 bits used (0-31 actual levels)
               - Level >> 3 is stored internally
  Bytes 6-63:  Unused (0x00)
 
Recommended Values:
  - Minimum: 0
  - Default: 15 (good visibility)
  - Maximum: 255 (max is clamped to 31 internally)
LED Mute Indicator (0x50)
-------------------------
Purpose: Control mute indicator LED (red for muted)
Packet:
  Bytes 0-1:   0x50, 0x00
  Bytes 2-3:   0x40, 0x00
  Bytes 4-7:   RGB Color (little-endian):
               - 0x000000 = Off (black)
               - 0xFF0000 = Red (muted)
               - 0x00FF00 = Green
               - 0x0000FF = Blue
               Format: [R, G, B, 0x00] or as 32-bit value
  Bytes 8-63:  Unused (0x00)
 
Example:
  Muted (Red):   [0x50, 0x00, 0x40, 0x00, 0xFF, 0x00, 0x00, 0x00, ...]
  Unmuted (Off): [0x50, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, ...]
 
 
Device Information Queries
--------------------------
Various commands used for device status/info:
 
Heartbeat (0x1234):
  Used to keep connection alive
  Packet: [0x34, 0x12, 0x40, 0x00, ...]
 
Hardware Version (0x11):
  Query device hardware revision
  Packet: [0x11, 0x00, 0x40, 0x00, ...]
 
Splash Screen (0x4C):
  Show splash/boot screen
  Packet: [0x4C, 0x00, 0x40, 0x00, ...]

## KEYPRESS INPUT PROTOCOL
 
Keypress Events (IN Endpoint 0x81)
----------------------------------
The device sends 64-byte packets on the IN endpoint when buttons are pressed/released.
 
Packet Structure:
  Bytes 0-3:   Header (0x30, 0x00, 0x08, 0x00) - always same
  Byte 4:      KEY CODE - identifies which button
  Byte 5:      Unknown (varies)
  Byte 6:      KEY STATE
               - 0x01 = Button PRESSED (down)
               - 0x00 = Button RELEASED (up)
  Byte 7:      Unknown (usually 0x00)
  Bytes 8-63:  Unused
 
Debouncing Behavior:
  - Same key within 50ms of previous: ignored
  - Different key or >50ms elapsed: processed
  - Handles mechanical bouncing

## KEY CODE MAPPING
 
Numeric/Dial Buttons:
  0x00 = '1'       0x01 = '2'       0x02 = '3'
  0x05 = '4'       0x06 = '5'       0x07 = '6'
  0x0A = '7'       0x0B = '8'       0x0C = '9'
  0x0F = '*'       0x10 = '0'       0x11 = '#'
 
Navigation Buttons:
  0x04 = UP        0x09 = ENTER     0x0E = DOWN
 
Function Buttons (Top row):
  0x03 = TOP1      0x08 = TOP2      0x0D = TOP3      0x12 = TOP4
 
Control Buttons:
  0x14 = VOLUME UP          0x15 = VOLUME DOWN
  0x13 = SPEAKER (SPK)      0x16 = MUTE
 
Complete Key Map Table:
  Code | Button
  -----|-------------------
  0x00 | 1
  0x01 | 2
  0x02 | 3
  0x03 | TOP1
  0x04 | UP
  0x05 | 4
  0x06 | 5
  0x07 | 6
  0x08 | TOP2
  0x09 | ENTER
  0x0A | 7
  0x0B | 8
  0x0C | 9
  0x0D | TOP3
  0x0E | DOWN
  0x0F | STAR (*)
  0x10 | 0
  0x11 | HASH (#)
  0x12 | TOP4
  0x13 | SPEAKER
  0x14 | VOLUME_UP
  0x15 | VOLUME_DOWN
  0x16 | MUTE 
 
### Keypress Event Examples:
 
Press TOP1 button:
  [0x30, 0x00, 0x08, 0x00, 0x03, 0x??, 0x01, 0x00, ...]
 
Release TOP1 button:
  [0x30, 0x00, 0x08, 0x00, 0x03, 0x??, 0x00, 0x00, ...]
 
Press VOLUME_UP:
  [0x30, 0x00, 0x08, 0x00, 0x14, 0x??, 0x01, 0x00, ...]
 
Press '5' button:
  [0x30, 0x00, 0x08, 0x00, 0x06, 0x??, 0x01, 0x00, ...]
 
 
## PROTOCOL IMPLEMENTATION NOTES
 
USB Timing:
  - IN endpoint read timeout: 50-100ms recommended
  - Keypresses are buffered if application doesn't read quickly
  - Flush buffer on startup to clear stale events
Pixel Data Important Details:
  1. Row updates are independent - can update any row in any order
  2. Dirty row tracking: Only send rows that changed
  3. Pixel reversal is REQUIRED - bitmap is horizontally flipped
  4. Padding: 396 pixels + 4 zeros = 400 bits = 50 bytes
  5. Byte-level packing: MSB first ordering
Display Refresh Strategy:
  - Full screen update: ~162 packets (~10KB)
  - Partial update: Send only changed rows
  - Minimum update: 1 row = 1 packet
  - Recommended rate: 2-30 fps (adjust for responsiveness)
Contrast Behavior:
  - Contrast level >> 3 stored internally
  - Only 5 bits used (0-31 effective levels)
  - Setting to 15 provides good default visibility
  - Ranges 0-255 work but only 0, 31, 63, 95, 127, 159, 191, 223, 255 distinct
Backlight Behavior:
  - Only accepts 0 or 1 (on/off)
  - NOT PWM or brightness control
  - Setting to any non-zero value = ON
  - Useful for screensaver/power saving

## EXAMPLE: Complete Display Update Sequence
 
1. Connect to USB device (VID 0x1cbe, PID 0x0009)
2. Claim interface 0
3. Flush any buffered input:
   while read(IN, timeout=50ms): pass
4. Send initial setup:
   - Backlight ON (0x4A command)
   - Set Contrast to 15 (0x4C command)
5. For each row of display data:
   - Create 64-byte packet with command 0x42
   - Set row number in bytes 6-7
   - Pack pixel data in bytes 10-59
   - Write to OUT endpoint
6. Listen on IN endpoint for keypresses:
   - Read 64-byte packets
   - Extract key code from byte 4
   - Extract state from byte 6
   - Debounce (50ms window)

## COMMAND SUMMARY TABLE
 
  Command | Purpose              | Payload Bytes | Value Range
  --------|----------------------|---------------|---------------------
  0x42    | Display Row          | 10-59         | Pixel data (packed)
  0x4A    | Backlight            | 4-5           | 0x0000=OFF, 0x0001=ON
  0x4C    | Contrast             | 4-5           | 0-255 (eff. 0-31)
  0x50    | LED Mute             | 4-7           | 0xBBGGRR00 (RGB+unused)
  0x11    | Hardware Version     | N/A           | Query command
  0x1234  | Heartbeat            | N/A           | Keep-alive
  0x4C    | Splash Screen        | N/A           | Show boot screen
 
## KNOWN BEHAVIORS & QUIRKS
 
1. Pixel Reversal Required:
   - Display expects horizontally flipped bitmap
   - Must reverse each row: row = row[::-1]
2. Contrast Implementation:
   - Only lower 3 bits significant (level >> 3)
   - Values 0-31 are distinct, above that repeats
3. Backlight Binary:
   - Despite protocol suggesting 16-bit value, only 0 or 1 work
   - Any non-zero value treated as ON
4. Key Buffering:
   - When application doesn't read, keys accumulate in USB buffer
   - Flush on startup: read until timeout occurs
   - Recommended: Read keypress queue frequently (20-100ms loop)
5. AT Field Power Management:
   - Screensaver can turn backlight off (0x4A with 0x0000)
   - Display stays powered, just backlight cuts
6. Display Persistence:
   - Image persists on display even without updates
   - Can be used for screensaver "breathing" effects
