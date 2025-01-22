import argparse
import sys
from PIL import Image
import numpy as np
from colormath.color_objects import sRGBColor
from colormath.color_objects import LabColor
from colormath.color_diff import delta_e_cie2000
from colormath.color_conversions import convert_color

def parse_args():
    parser = argparse.ArgumentParser(description="Convert an image to a given color palette.")
    parser.add_argument("input", help="Path to the input image.")
    parser.add_argument("output", help="Path to save the output image.")
    parser.add_argument("--palette", nargs='+', default=['#d1c4af', '#a39990', '#363132'],
                        help="List of hex colors to use in the output image.")
    return parser.parse_args()

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def color_distance(color1, color2):
    c1_rgb = sRGBColor(color1[0] / 255, color1[1] / 255, color1[2] / 255)
    c2_rgb = sRGBColor(color2[0] / 255, color2[1] / 255, color2[2] / 255)
    
    c1_lab = convert_color(c1_rgb, LabColor)
    c2_lab = convert_color(c2_rgb, LabColor)
    
    return delta_e_cie2000(c1_lab, c2_lab)

def process_image(image_path, output_path, palette):
    image = Image.open(image_path).convert("RGBA")
    pixels = np.array(image)
    new_pixels = pixels.copy()
    palette_rgb = [hex_to_rgb(color.replace('#', '')) for color in palette]
    
    for y in range(pixels.shape[0]):
        for x in range(pixels.shape[1]):
            r, g, b, a = pixels[y, x]
            if a == 0:
                continue
            min_dist = float('inf')
            best_color = (r, g, b)
            for palette_color in palette_rgb:
                dist = color_distance((r, g, b), palette_color)
                if dist < min_dist:
                    min_dist = dist
                    best_color = palette_color
            new_pixels[y, x, :3] = best_color
    
    new_image = Image.fromarray(new_pixels).convert('RGB')
    new_image.save(output_path)

def main():
    args = parse_args()
    process_image(args.input, args.output, args.palette)

if __name__ == "__main__":
    main()