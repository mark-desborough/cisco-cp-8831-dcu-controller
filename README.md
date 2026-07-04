# cisco-cp-8831-dcu-controller
Using a Cisco conference phone interface as a keypad and lcd screen over usb

Currently this applies to the V01 model (`CP-8831-DCU-S-V01`). It contains a Texas Instruments LM3S5R31 ARM Cortex-M3 microcontroller.
There is a second version which I belive switches to a ST (STMicroelectronics) microcontroller, but without having a V02 I am only guessing.
As far as I can tell the communication protocol is identical. The USB device/vendor ID may be different.

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
