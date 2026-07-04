# cisco-cp-8831-dcu-controller
Using a Cisco conference phone interface as a keypad and lcd screen over usb

## Hardware Revisions
Currently this applies to the V01 model (`CP-8831-DCU-S-V01`). It contains a Texas Instruments `LM3S5R31 ARM Cortex-M3` microcontroller.

There is a second version which I belive switches to a ST (STMicroelectronics) microcontroller, but without having a V02 I am only guessing.

As far as I can tell the communication protocol is identical. The USB device/vendor ID may be different.

## USB Cable
I believe this is the biggest hurdle that has stopped anyone casually poking this device:
- The stock USB connection is a male MicroUSB. The sort I would most commonly associate with a 2010 era phone charger.
- Within the unit it connects with a JST connector (The cable end says HR 12). It is 1cm wide with 5 pins (5v, data+ and data-,ground, shield).
- A molded grommet is attached to the cable and screwed down at the entry-point into the case.
- Within my sheath the cable is colour-coded well. Red/Black/Green/White + outer shield

The best (cheapest) method I have used is to take a regular USB-A cable and splice it onto the end that would plug into the 8831 base unit.
- An adapter for plugging this isn't a regular PC is not common (i.e a reverse USB OTG) cable. 
- There appears to be a "USB 2.0 Male to Micro USB Female Connector Adapter" which would most likely work.
- The "USB-A male to USB-A male" does have some uses, but feels like a power extension cord with 2 male sockets (most use cases it is a bad idea).

### USB Device Permission
As root add a udev rule and then `udevadm control --reload && udevadm trigger` to reload the rules. When the specific device is added it will have the more open permissions added.  
A more rigid group-based access makes more sense (like the dialout group) and a non-privileged user/service running the python code for screen management.  

```
#/etc/udev/rules.d/99-lcd-keypad.rules
#Product: Composite HID Mouse and CDC Serial Example (everyone has read/write)
SUBSYSTEM=="usb", ATTRS{idVendor}=="1cbe", ATTRS{idProduct}=="0009", MODE="0666"

#Product: Device Firmware Upgrade (root only)
SUBSYSTEM=="usb", ATTRS{idVendor}=="1cbe", ATTRS{idProduct}=="0009", MODE="0660"
```

## Terminology
| Term | Description |
| :--- | :--- |
| CP-8831-DCU-S= | Spare Cisco Unified IP Conference Phone 8831 Display Control Unit (DCU) |
| Wired control panel | The panel allows easy control of the unit and viewing of the display without having to move the entire unit. |
| Display | The conference station has a large high-resolution, graphical 3.5-inch backlit display (396 x 162 pixels). |

## Specifications
| Type | Measurement |
| :--- | :--- |
| Dimensions | Control panel: 5.75 x 5.0 x 1.0 in. (14.61 x 12.7 x 2.54 cm) |
| Weight | DCU 0.56 lbs. (253.0 grams) |
| Display | 3.25 x 1.5 in. (8.26 x 3.81 cm); 396 x 162 pixels. |
