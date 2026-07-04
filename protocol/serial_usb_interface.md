# The Serial Console

The usb devices being detected by the linux kernel.

```[Sat Jul  4 11:33:21 2026] usb 1-2: new full-speed USB device number 27 using xhci_hcd
[Sat Jul  4 11:33:21 2026] usb 1-2: New USB device found, idVendor=1cbe, idProduct=0009, bcdDevice= 1.00
[Sat Jul  4 11:33:21 2026] usb 1-2: New USB device strings: Mfr=1, Product=2, SerialNumber=3
[Sat Jul  4 11:33:21 2026] usb 1-2: Product: Composite HID Mouse and CDC Serial Example
[Sat Jul  4 11:33:21 2026] usb 1-2: Manufacturer: Texas Instruments
[Sat Jul  4 11:33:21 2026] usb 1-2: SerialNumber: 12345678
[Sat Jul  4 11:33:21 2026] cdc_acm 1-2:1.1: ttyACM0: USB ACM device
```

Connecting to the USB Console device: `minicom -D /dev/ttyACM0`

```
dcu>help

        Commands:

        help    bdfu    diags   env     lcdr
        led     splash  trace   ver

dcu>ver

DCU Firmware:
Version:  dcu8831.9-3-3-5

dcu>env info

Environment:

 id:  44435545
 crc: 00000000
 len: 00000400

 ver: dcu8831.9-3-3-5
 rev: HwRev=1,LcdRev=1

dcu>bdfu

Jumping to DFU Bootloader...
```

After entering the Device Firmware Upgrade (DFU) mode from the console: 

```
[Sat Jul  4 11:39:12 2026] usb 1-2: USB disconnect, device number 27
[Sat Jul  4 11:39:13 2026] usb 1-2: new full-speed USB device number 28 using xhci_hcd
[Sat Jul  4 11:39:13 2026] usb 1-2: New USB device found, idVendor=1cbe, idProduct=00ff, bcdDevice= 0.01
[Sat Jul  4 11:39:13 2026] usb 1-2: New USB device strings: Mfr=1, Product=2, SerialNumber=3
[Sat Jul  4 11:39:13 2026] usb 1-2: Product: Device Firmware Upgrade
[Sat Jul  4 11:39:13 2026] usb 1-2: Manufacturer: Texas Instruments
[Sat Jul  4 11:39:13 2026] usb 1-2: SerialNumber: 0.1
```

The firmware can be dumped with `dfu-util -U /tmp/8831_firmware.bin`
