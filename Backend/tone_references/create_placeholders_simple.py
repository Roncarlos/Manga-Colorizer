"""
Create minimal placeholder reference images without external dependencies.
Creates simple solid color images in BMP format.
"""

import struct
from pathlib import Path

def create_bmp(width, height, colors, filename):
    """Create a BMP image with horizontal color bands."""
    ref_dir = Path(__file__).parent
    
    # BMP header
    file_size = 54 + (width * height * 3)
    bmp_header = struct.pack('<2sIHHI', b'BM', file_size, 0, 0, 54)
    
    # DIB header (BITMAPINFOHEADER)
    dib_header = struct.pack('<IiiHHIIiiII', 
        40,  # DIB header size
        width, height,
        1,  # Color planes
        24,  # Bits per pixel
        0,  # No compression
        width * height * 3,  # Image size
        2835, 2835,  # Print resolution
        0, 0  # Color palette
    )
    
    # Create pixel data (BMP is stored bottom-to-top, BGR format)
    pixels = bytearray()
    num_colors = len(colors)
    section_height = height // num_colors
    
    for y in range(height - 1, -1, -1):  # Bottom to top
        # Determine which color section this row belongs to
        section = min((height - 1 - y) // section_height, num_colors - 1)
        r, g, b = colors[section]
        
        # Add some variation (simple pattern)
        variation = ((y + y % 10) % 20 - 10)
        r = max(0, min(255, r + variation))
        g = max(0, min(255, g + variation))
        b = max(0, min(255, b + variation))
        
        for x in range(width):
            # BMP uses BGR
            pixels.extend([b, g, r])
        
        # Row padding (BMP rows must be multiple of 4 bytes)
        padding = (4 - (width * 3) % 4) % 4
        pixels.extend([0] * padding)
    
    # Write file
    filepath = ref_dir / filename
    with open(filepath, 'wb') as f:
        f.write(bmp_header)
        f.write(dib_header)
        f.write(pixels)
    
    print(f"✓ Created {filename}")

# Image size (kept small for fast generation)
width, height = 256, 256

# Bright theme
bright_colors = [
    (255, 220, 180),
    (255, 180, 200),
    (200, 220, 255),
    (220, 255, 200),
]
create_bmp(width, height, bright_colors, 'bright.bmp')

# Dark theme
dark_colors = [
    (40, 35, 50),
    (50, 40, 40),
    (30, 40, 50),
    (45, 30, 35),
]
create_bmp(width, height, dark_colors, 'dark.bmp')

# Warm theme
warm_colors = [
    (180, 100, 70),
    (200, 130, 90),
    (220, 150, 100),
    (190, 140, 110),
]
create_bmp(width, height, warm_colors, 'warm.bmp')

# Cool theme
cool_colors = [
    (100, 120, 180),
    (120, 140, 190),
    (90, 110, 150),
    (110, 100, 160),
]
create_bmp(width, height, cool_colors, 'cool.bmp')

# Vibrant theme
vibrant_colors = [
    (255, 50, 100),
    (50, 180, 255),
    (255, 200, 0),
    (150, 50, 255),
]
create_bmp(width, height, vibrant_colors, 'vibrant.bmp')

# Pastel theme
pastel_colors = [
    (230, 210, 220),
    (210, 220, 240),
    (220, 235, 210),
    (240, 230, 210),
]
create_bmp(width, height, pastel_colors, 'pastel.bmp')

print("\n" + "="*60)
print("✓ All placeholder reference images created!")
print("="*60)
print(f"\nLocation: {Path(__file__).parent.absolute()}")
print("\nThese are simple placeholder images with representative colors.")
print("Replace them with real images that match your desired aesthetics.")
print("You can use any image format (JPG, PNG, BMP) and any size.")
