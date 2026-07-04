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
| Display Control Unit | Written on the PCB as "Beignet - Display Control Unit (2) 1000705-00 Rev D" |

## Specifications
| Type | Measurement |
| :--- | :--- |
| Features | Adjustable display brightness (this is currently questionable as the contrast seems to be the only thing to adjust) | 
| Dimensions | Control panel: 5.75 x 5.0 x 1.0 in. (14.61 x 12.7 x 2.54 cm) |
| Weight | DCU 0.56 lbs. (253.0 grams) |
| Display | 3.25 x 1.5 in. (8.26 x 3.81 cm); 396 x 162 pixels. |

## Known Firmware Versions: 
| Microcontroller | Phone Firmware package | Filename within rootfs | Firmware Version String |
| --- | --- | --- | --- |
| ST | cmterm-8831-sip.10-3-1SR6-4.cop.sgn | `/sbin/beignet_dcu_st.dfu` | Revolabs dcu dcu7938.9-3-2-1-01 @30333+Tue Jan 7 18:23:40 EST 2020 |
| LM3S5R31 | cmterm-8831-sip.10-3-1SR6-4.cop.sgn | `/sbin/beignet_dcu.dfu` | Revolabs dcu dcu7938.9-3-2-1-01 @30333+Tue Jan 7 18:23:40 EST 2020 |
| LM3S5R31 | sip8831.9-3-3-5 | unknown | Revolabs dcu dcu7938.9-3-2-1-01 @10543+Fri Mar 29 12:48:10 EDT 2013 |

### Firmware hints:
The Cisco 7937G is a variant of the Polycom IP 7000 and has the same programming instructions. The 7937G connects to the "Revolabs Single Channel System" via a 10-pin network cable. [Revolabs Ip Phone Ip7000 User Manual](https://usermanual.wiki/Revolabs/RevolabsIpPhoneIp7000UsersManual523886.1844482001.pdf)
It almost looks from the dcu7938 designation this controller is the next iteration of the Cisco 7937G Unified IP Conference Station (CP-7937G). It does feature a lower resolution screen (255 x 128), but appears very similar in most ways (except for having a cable).
