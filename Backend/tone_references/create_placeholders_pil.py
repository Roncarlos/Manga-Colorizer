"""
Simple reference image generator using PIL (doesn't require OpenCV).
Creates placeholder images for tone adjustment themes.
"""

try:
    from PIL import Image, ImageDraw
    import random
    from pathlib import Path
    
    # Create tone reference directory
    ref_dir = Path(__file__).parent
    ref_dir.mkdir(exist_ok=True)
    
    # Image size for references
    width, height = 512, 512
    
    def create_gradient_image(colors, filename):
        """Create a gradient image with given colors."""
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)
        
        num_colors = len(colors)
        section_height = height // num_colors
        
        for i, color in enumerate(colors):
            start_y = i * section_height
            end_y = (i + 1) * section_height if i < num_colors - 1 else height
            
            # Draw rectangle with base color
            draw.rectangle([0, start_y, width, end_y], fill=color)
            
            # Add some random pixels for variation
            for _ in range(1000):
                x = random.randint(0, width - 1)
                y = random.randint(start_y, end_y - 1)
                # Slight color variation
                varied_color = tuple(max(0, min(255, c + random.randint(-20, 20))) for c in color)
                draw.point((x, y), fill=varied_color)
        
        img.save(ref_dir / filename, quality=95)
        print(f"✓ Created {filename}")
    
    # Bright theme - vibrant, saturated colors with high luminance
    bright_colors = [
        (255, 220, 180),  # Warm peachy
        (255, 180, 200),  # Bright pink
        (200, 220, 255),  # Light sky blue
        (220, 255, 200),  # Light green
        (255, 240, 180),  # Warm yellow
    ]
    create_gradient_image(bright_colors, 'bright.jpg')
    
    # Dark theme - deep, muted colors with low luminance
    dark_colors = [
        (40, 35, 50),     # Deep purple-blue
        (50, 40, 40),     # Dark brown
        (30, 40, 50),     # Dark blue-grey
        (45, 30, 35),     # Deep maroon
        (35, 45, 40),     # Dark teal
    ]
    create_gradient_image(dark_colors, 'dark.jpg')
    
    # Warm theme - red, orange, yellow tones
    warm_colors = [
        (180, 100, 70),   # Burnt orange
        (200, 130, 90),   # Warm brown
        (220, 150, 100),  # Peachy
        (190, 140, 110),  # Warm tan
        (210, 120, 80),   # Rust
    ]
    create_gradient_image(warm_colors, 'warm.jpg')
    
    # Cool theme - blue, cyan, purple tones
    cool_colors = [
        (100, 120, 180),  # Cool blue
        (120, 140, 190),  # Sky blue
        (90, 110, 150),   # Steel blue
        (110, 100, 160),  # Purple-blue
        (80, 130, 170),   # Cyan-blue
    ]
    create_gradient_image(cool_colors, 'cool.jpg')
    
    # Vibrant theme - highly saturated, bold colors
    vibrant_colors = [
        (255, 50, 100),   # Hot pink
        (50, 180, 255),   # Bright cyan
        (255, 200, 0),    # Golden yellow
        (150, 50, 255),   # Purple
        (50, 255, 100),   # Bright green
    ]
    create_gradient_image(vibrant_colors, 'vibrant.jpg')
    
    # Pastel theme - soft, desaturated colors with high luminance
    pastel_colors = [
        (230, 210, 220),  # Soft pink
        (210, 220, 240),  # Soft blue
        (220, 235, 210),  # Soft green
        (240, 230, 210),  # Soft cream
        (230, 220, 235),  # Soft lavender
    ]
    create_gradient_image(pastel_colors, 'pastel.jpg')
    
    print("\n" + "="*60)
    print("✓ All placeholder reference images created successfully!")
    print("="*60)
    print(f"\nLocation: {ref_dir.absolute()}")
    print("\nThese are placeholder images with representative colors.")
    print("Replace them with images that match your desired aesthetics.")
    print("The images can be any size - color transfer is size-independent.")
    
except ImportError as e:
    print(f"Error: {e}")
    print("\nPIL/Pillow is not installed. To create placeholder images:")
    print("1. Install Pillow: pip install Pillow")
    print("2. Run this script again")
    print("\nAlternatively, manually create images named:")
    print("  bright.jpg, dark.jpg, warm.jpg, cool.jpg, vibrant.jpg, pastel.jpg")
    print("with appropriate color palettes.")
