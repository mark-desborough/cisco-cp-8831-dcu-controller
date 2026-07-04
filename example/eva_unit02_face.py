#!/usr/bin/python3
from PIL import Image
from cisco_8831_dcu import CiscoDCU, WIDTH, HEIGHT

def load_png_for_lcd(path):
    """
    Load a PNG and convert it to a 1-bit image sized for the Cisco LCD.
    """
   # img = Image.open(path)

    img = Image.open(path).convert("L")
    img = img.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)

    # threshold to 1-bit
    img = img.convert("1", dither=Image.Dither.NONE)

    img = Image.eval(img, lambda x: 255 - x)

    return img


def main():
    png_path = "eva_unit02_face.png"

    # Convert image
    img = load_png_for_lcd(png_path)

    # Send to device
    with CiscoDCU() as dcu:
        dcu.debug(True)

        # Optional setup tweaks
        dcu.lcd.backlight(1)

        # Push image to screen
        dcu.lcd.screen(img)

        print("Image sent. Exiting.")

        dcu.close()

if __name__ == "__main__":
    main()
