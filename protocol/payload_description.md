# Cisco 8831 DCU - USB Protocol Specification
 
> Reverse-engineered USB device protocol for the Cisco 8831 Desk Camera Unit (DCU)
 
## Device Information
 
| Property | Value |
|----------|-------|
| **Vendor ID** | `0x1cbe` |
| **Product ID** | `0x0009` |
| **USB Version** | 2.0 |
| **IN Endpoint** | `0x81` (keypresses) |
| **OUT Endpoint** | `0x01` (commands/display) |
| **Max Packet Size** | 64 bytes |
| **Display Resolution** | 396 × 162 pixels |
| **Display Type** | Monochrome, 1-bit per pixel |
 
---
 
## LCD Display Protocol
 
### Command: 0x42 (Display Row Update)
 
Update individual rows of the LCD display.
 
```
Packet Structure (64 bytes):
┌────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬─────────┐
│ 0  │ 1  │ 2  │ 3  │ 4  │ 5  │ 6  │ 7  │ 8  │ 9  │ 10-59   │
├────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼─────────┤
│0x42│0x00│0x40│0x00│0x00│0x00│ Row│ Row│0x8c│0x01│ Pixels  │
│    │    │    │    │    │    │ Lo │ Hi │    │    │ (50B)   │
└────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴─────────┘
```
 
| Bytes | Field | Description |
|-------|-------|-------------|
| 0-1 | Command ID | `0x42, 0x00` (Display Row Update) |
| 2-3 | Packet Length | `0x40, 0x00` (always 64 bytes) |
| 4-5 | Reserved | `0x00, 0x00` |
| 6-7 | Row Number | Little-endian uint16_t (0-161) |
| 8-9 | Fixed | `0x8c, 0x01` (purpose unknown) |
| 10-59 | Pixel Data | 50 bytes = 400 bits = 396 pixels + 4 padding zeros |
 
#### Display Specifications
 
| Property | Value |
|----------|-------|
| **Resolution** | 396 × 162 pixels |
| **Color Depth** | 1-bit (on/off only) |
| **Row Range** | 0-161 (162 rows total) |
| **Pixel Packing** | 8 pixels per byte, MSB first |
 
#### Pixel Packing Algorithm
 
1. Start with 396 pixel values (0 or 1)
2. Reverse pixel array: `pixel[0] ← pixel[395]`
3. Pad with 4 zeros: (400 bits total = 50 bytes)
4. Pack 8 pixels per byte, MSB first:
```
   byte[i] = pixel[7]<<7 | pixel[6]<<6 | ... | pixel[0]<<0
```
 
---
 
## Control Commands
 
### Backlight (0x4A) - ON/OFF ONLY
 
**Important:** This is purely binary on/off. Use **Contrast (0x4C)** for actual brightness control.
 
| Bytes | Field | Value |
|-------|-------|-------|
| 0-1 | Command | `0x4A, 0x00` |
| 2-3 | Length | `0x40, 0x00` |
| 4-5 | State | `0x0000` = OFF, `0x0001` = ON |
| 6-63 | Unused | `0x00...` |
 
**Example:**
```c
// Turn backlight ON
uint8_t pkt[64] = {0x4A, 0x00, 0x40, 0x00, 0x01, 0x00, ...};
 
// Turn backlight OFF
uint8_t pkt[64] = {0x4A, 0x00, 0x40, 0x00, 0x00, 0x00, ...};
```
 
**Note:** Backlight off is useful for screensaver/power saving modes.
 
---
 
### Contrast (0x4C) - ACTUAL BRIGHTNESS ADJUSTMENT
 
⚠️ **Despite being called "contrast", this controls LCD brightness.** Cisco labeled it this way in firmware.
 
| Bytes | Field | Value |
|-------|-------|-------|
| 0-1 | Command | `0x4C, 0x00` |
| 2-3 | Length | `0x40, 0x00` |
| 4-5 | Level | **1-30** (30 distinct brightness levels) |
| 6-63 | Unused | `0x00...` |
 
#### Brightness Levels
 
| Level | Description |
|-------|-------------|
| 1-5 | Very dim (low power mode) |
| **15** | **Default (recommended)** |
| 20-25 | Normal light |
| 25-30 | Bright light |
| 0, 31 | Invalid/undefined |
 
**Example:**
```c
// Set brightness to default (15)
uint8_t pkt[64] = {0x4C, 0x00, 0x40, 0x00, 0x0F, 0x00, ...};
 
// Brightest
uint8_t pkt[64] = {0x4C, 0x00, 0x40, 0x00, 0x1E, 0x00, ...};
```
 
---
 
### LED Control (0x50) - Button Indicators
 
Control the RGB LEDs on **CALL** and **MUTE** buttons.
 
| Bytes | Field | Value |
|-------|-------|-------|
| 0-1 | Command | `0x50, 0x00` |
| 2-3 | Length | `0x40, 0x00` |
| 4-7 | RGB Color | `[R, G, B, 0x00]` (little-endian) |
| 8-63 | Unused | `0x00...` |
 
#### LED Capabilities
 
| Button | Colors | Notes |
|--------|--------|-------|
| **CALL** | Red, Green, Blue, Any combo | Full RGB capable |
| **MUTE** | Red only | Binary on/off |
 
#### Common Color Values
 
| Color | Hex | Bytes |
|-------|-----|-------|
| Off | `0x000000` | `[0x00, 0x00, 0x00, 0x00]` |
| Red | `0xFF0000` | `[0xFF, 0x00, 0x00, 0x00]` |
| Green | `0x00FF00` | `[0x00, 0xFF, 0x00, 0x00]` |
| Blue | `0x0000FF` | `[0x00, 0x00, 0xFF, 0x00]` |
| Yellow | `0xFFFF00` | `[0xFF, 0xFF, 0x00, 0x00]` |
 
**Example:**
```c
// Mute button RED
uint8_t pkt[64] = {0x50, 0x00, 0x40, 0x00, 0xFF, 0x00, 0x00, 0x00, ...};
 
// Call button GREEN
uint8_t pkt[64] = {0x50, 0x00, 0x40, 0x00, 0x00, 0xFF, 0x00, 0x00, ...};
 
// Call button OFF
uint8_t pkt[64] = {0x50, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, ...};
```
 
#### LED Animation Effects
 
- **Breathing/Blinking:** Send repeated on/off commands with timing delays
- **Pulse effect:** Gradually change brightness via timed updates
- **Effect type:** Slow blink (not smooth PWM) - more like binary pulsing
---
 
### Device Information Queries
 
#### Hardware Version (0x11)
 
Query device hardware revision.
 
```c
uint8_t pkt[64] = {0x11, 0x00, 0x40, 0x00, ...};
```
 
#### Splash Screen (0x4C)
 
Display splash/boot screen.
 
```c
uint8_t pkt[64] = {0x4C, 0x00, 0x40, 0x00, ...};
```
 
#### Heartbeat (0x1234)
 
❌ **FALSE LEAD** - Not actually used.
- Was a red herring from reverse engineering (pointer dereferencing artifact)
- No keep-alive required
- USB connection maintains naturally
---
 
## Keypress Input Protocol
 
### Keypress Events (IN Endpoint 0x81)
 
Device sends 64-byte packets on IN endpoint when buttons are pressed/released.
 
```
Packet Structure:
┌────┬────┬────┬────┬────┬────┬────┬────┬────────────┐
│ 0  │ 1  │ 2  │ 3  │ 4  │ 5  │ 6  │ 7  │ 8-63       │
├────┼────┼────┼────┼────┼────┼────┼────┼────────────┤
│0x30│0x00│0x08│0x00│ Key│ ?? │State│0x00│ Unused    │
└────┴────┴────┴────┴────┴────┴────┴────┴────────────┘
```
 
| Bytes | Field | Description |
|-------|-------|-------------|
| 0-3 | Header | `0x30, 0x00, 0x08, 0x00` (always same) |
| 4 | Key Code | Identifies which button (see Key Map) |
| 5 | Unknown | Varies |
| 6 | State | `0x01` = Press, `0x00` = Release |
| 7 | Unknown | Usually `0x00` |
| 8-63 | Unused | - |
 
### Debouncing Behavior
 
- Same key within 50ms of previous → **ignored**
- Different key or >50ms elapsed → **processed**
- Handles mechanical key bouncing automatically
---
 
## Key Code Mapping
 
### Complete Key Map
 
| Code | Button | Code | Button | Code | Button |
|------|--------|------|--------|------|--------|
| `0x00` | 1 | `0x09` | ENTER | `0x12` | TOP4 |
| `0x01` | 2 | `0x0A` | 7 | `0x13` | SPEAKER |
| `0x02` | 3 | `0x0B` | 8 | `0x14` | VOLUME_UP |
| `0x03` | TOP1 | `0x0C` | 9 | `0x15` | VOLUME_DOWN |
| `0x04` | UP | `0x0D` | TOP3 | `0x16` | MUTE |
| `0x05` | 4 | `0x0E` | DOWN | `0x17+` | Unmapped |
| `0x06` | 5 | `0x0F` | * (STAR) | - | - |
| `0x07` | 6 | `0x10` | 0 | - | - |
| `0x08` | TOP2 | `0x11` | # (HASH) | - | - |
 
### Keypress Event Examples
 
**Press TOP1 button:**
```
[0x30, 0x00, 0x08, 0x00, 0x03, 0x??, 0x01, 0x00, ...]
```
 
**Release TOP1 button:**
```
[0x30, 0x00, 0x08, 0x00, 0x03, 0x??, 0x00, 0x00, ...]
```
 
**Press VOLUME_UP:**
```
[0x30, 0x00, 0x08, 0x00, 0x14, 0x??, 0x01, 0x00, ...]
```
 
**Press '5' button:**
```
[0x30, 0x00, 0x08, 0x00, 0x06, 0x??, 0x01, 0x00, ...]
```
 
---
 
## Command Summary
 
| Command | Purpose | Payload Bytes | Value/Range |
|---------|---------|---------------|-------------|
| `0x42` | Display Row | 10-59 | Pixel data (packed) |
| `0x4A` | Backlight | 4-5 | `0x0000`=OFF, `0x0001`=ON |
| `0x4C` | Brightness | 4-5 | **1-30** (default: 15) |
| `0x50` | LED Control | 4-7 | RGB `[R, G, B, 0x00]` |
| `0x11` | HW Version | N/A | Query command |
| `0x4C` | Splash Screen | N/A | Query command |
 
---
 
## Implementation Notes
 
### USB Timing
 
- **IN endpoint read timeout:** 50-100ms recommended
- **Key buffering:** Device buffers keypresses if application doesn't read quickly
- **Startup:** Flush buffer to clear stale events before main loop
### Display Efficiency
 
| Update Type | Packets | Size | Use Case |
|------------|---------|------|----------|
| Full screen | ~162 | ~10KB | Initial load |
| Partial | Variable | Variable | Dirty row tracking |
| Single row | 1 | 64B | Minimal updates |
| Recommended rate | 2-30 fps | - | Adjust for responsiveness |
 
### Pixel Data Details
 
1. **Row updates:** Independent - update any row in any order
2. **Dirty row tracking:** Only send rows that changed (highly recommended)
3. **Pixel reversal:** REQUIRED - bitmap is horizontally flipped
4. **Padding:** 396 pixels + 4 zeros = 400 bits = 50 bytes
5. **Byte packing:** MSB first ordering

### Brightness Control Strategy
  
| Control | Purpose | Range | Notes |
|---------|---------|-------|-------|
| **Backlight (0x4A)** | Power | ON/OFF | Binary only, no PWM |
| **Contrast (0x4C)** | **Brightness** | 1-30 | This adjusts the contrast, but darkens all pixels and reduces the amount of light seen (thus brightness) |
 
**Usage:**
- Use **0x4A** to turn display on/off (screensaver/power saving)
- Use **0x4C** to adjust brightness (what users expect)
- Never combine - use one or the other for each purpose
### LED Control Details
 
| Feature | Details |
|---------|---------|
| **CALL Button LED** | Full RGB - can be any color |
| **MUTE Button LED** | Red only - binary on/off |
| **Animation** | Slow blink effect via timed on/off (not smooth PWM) |
| **Control** | Send repeated 0x50 commands with delays |
 
### Key Buffering
 
- Keys accumulate in USB buffer if application doesn't read
- **Startup sequence:** Read until timeout to flush stale events
- **Loop rate:** Poll keypress queue every 20-100ms
---
 
## Known Behaviors & Quirks
 
### 1. Pixel Reversal Required
- Display expects horizontally flipped bitmap
- Must reverse each row: `row = row[::-1]`
### 2. Backlight vs Brightness (Cisco's Misleading Design)
- Backlight (0x4A) is purely ON/OFF, no PWM
- Brightness adjustment is done via Contrast (0x4C) instead
- Cisco labeled the contrast control as "brightness" in their firmware
- Backlight OFF useful for power saving/screensaver
- Use contrast to adjust actual display brightness (1-30 levels, default 15)
### 3. Contrast Implementation
- 30 distinct brightness levels (1-30)
- Default: 15 (good visibility)
- 0 and 31: Invalid/undefined
- Only values 1-30 produce visible changes
### 4. LED Control
- Two buttons have controllable LEDs (CALL and MUTE)
- CALL button: Can be red, green, or off (full RGB)
- MUTE button: Can only be red or off
- LED effects use on/off timing (slow blink/breathing effect)
- Not smooth PWM, more like timed pulses
### 5. No Heartbeat Required
- 0x1234 was a false discovery from reverse engineering
- No keep-alive or heartbeat is actually needed
- USB connection maintains naturally
### 6. Key Buffering
- When application doesn't read, keys accumulate in USB buffer
- Flush on startup: read until timeout occurs
- Recommended: Read keypress queue frequently (20-100ms loop)
### 7. AT Field Power Management
- Screensaver can turn backlight off (0x4A with 0x0000)
- Display stays powered, just backlight cuts
- Useful for reducing power consumption
### 8. Display Persistence
- Image persists on display even without updates
- Can be used for screensaver "breathing" effects via LED pulsing
---
 
## Complete Display Update Sequence
 
```python
# 1. Connect to device
device = usb.core.find(idVendor=0x1cbe, idProduct=0x0009)
 
# 2. Claim interface
cfg = device.get_active_configuration()
intf = cfg[(0, 0)]
 
# 3. Flush buffered input
while True:
    try:
        ep_in.read(64, timeout=50)
    except usb.core.USBTimeoutError:
        break
 
# 4. Send initial setup
ep_out.write([0x4A, 0x00, 0x40, 0x00, 0x01, 0x00, ...])  # Backlight ON
ep_out.write([0x4C, 0x00, 0x40, 0x00, 0x0F, 0x00, ...])  # Contrast = 15
 
# 5. Update display (per row)
for row in range(162):
    packet = create_packet(row, pixel_data[row])
    ep_out.write(packet)
 
# 6. Listen for keypresses
while True:
    data = ep_in.read(64, timeout=100)
    key_code = data[4]
    state = data[6]  # 0x01 = press, 0x00 = release
```
 
---
 
## References & Credits
 
- Protocol reverse-engineered from USB traffic analysis
- Tested on Cisco 8831 Desk Camera Unit
- See `cisco_8831_dcu.py` library for working implementation
