# Tone Adjustment Feature

## Overview

The Manga Colorizer now includes a tone adjustment feature that allows you to change the visual tone/mood of colorized images using **color transfer in LAB color space**. This advanced technique transfers color characteristics from reference images to your colorized manga, providing more natural and sophisticated tone adjustments compared to simple brightness/saturation modifications.

## Available Themes

The following tone themes are available:

1. **Neutral** (default) - No tone adjustment applied
2. **Bright** - Transfers vibrant, cheerful color characteristics
3. **Dark** - Applies moody, dramatic color tones
4. **Warm** - Shifts toward cozy, warm color palettes
5. **Cool** - Applies calm, cool atmospheric colors
6. **Vibrant** - Bold, vivid color transfer
7. **Pastel** - Soft, gentle color aesthetics

## How It Works

### Color Transfer Algorithm

The tone adjustment uses a sophisticated color transfer technique based on LAB color space:

1. **Load Reference Image**: Each theme has a reference image that embodies the desired color aesthetic
2. **Convert to LAB**: Both the colorized manga and reference image are converted to LAB color space (L=lightness, A=green-red, B=blue-yellow)
3. **Calculate Statistics**: Compute mean and standard deviation for each channel
4. **Transfer Colors**: For each pixel: `new_pixel = ((old_pixel - source_mean) * (target_std / source_std)) + target_mean`
5. **Convert Back**: Return to RGB color space

This method preserves the structure and content of your manga while adopting the color characteristics of the reference image.

### Why LAB Color Space?

LAB color space separates luminance (L) from color information (A, B), making it ideal for color manipulation:
- **L channel**: Lightness (0-100)
- **A channel**: Green to Red
- **B channel**: Blue to Yellow

This separation allows for more perceptually uniform color adjustments.

## Backend Implementation

### File Structure

```
Backend/
├── utils/
│   └── tone_adjuster.py       # Color transfer implementation
└── tone_references/           # Reference images for each theme
    ├── README.md             # Instructions for customizing references
    ├── bright.bmp            # Reference for bright theme
    ├── dark.bmp              # Reference for dark theme
    ├── warm.bmp              # Reference for warm theme
    ├── cool.bmp              # Reference for cool theme
    ├── vibrant.bmp           # Reference for vibrant theme
    └── pastel.bmp            # Reference for pastel theme
```

### ToneAdjuster Class

The `ToneAdjuster` class in `utils/tone_adjuster.py` handles all color transfer operations:

```python
# Usage example
from utils.tone_adjuster import ToneAdjuster

# Apply tone adjustment
adjusted_image = ToneAdjuster.adjust_tone(image, theme='bright')
```

### Reference Images

Reference images define the color characteristics for each theme. These are **placeholder images** included by default, but you should replace them with images that match your desired aesthetics:

- **Format**: JPG, PNG, or BMP
- **Size**: Any size (color transfer is size-independent)
- **Content**: The actual content doesn't matter - only the color distribution

#### Customizing Reference Images

To customize the tone themes:

1. Find or create images with the color mood you want
2. Save them in `Backend/tone_references/` with the theme name
3. Supported names: `bright`, `dark`, `warm`, `cool`, `vibrant`, `pastel`
4. Use any image format (`.jpg`, `.png`, `.bmp`)

**Examples of good reference sources:**
- **Bright**: Sunny day photos, colorful flowers, cheerful scenes
- **Dark**: Night photography, film noir stills, low-key lighting
- **Warm**: Sunset photos, autumn leaves, candlelight scenes
- **Cool**: Winter landscapes, underwater photos, moonlight scenes
- **Vibrant**: Pop art, tropical scenes, saturated artwork
- **Pastel**: Watercolor paintings, spring flowers, soft illustrations

You can even use manga panels or anime screenshots that have the exact color palette you want to replicate!

### Frontend Integration

All three frontends (Chrome, Firefox, Safari) have been updated with a "Tone" dropdown selector in their popup interfaces.

#### Chrome/Firefox Extensions
- Dropdown selector in popup with all 7 tone options
- Selected tone is saved to browser storage
- Tone parameter is sent with each colorization request

#### Safari Extension
- Simplified dropdown in popup (matching Safari's minimal interface)
- Tone is stored and sent with requests to the backend

## Usage

### For Users

1. Open the extension popup
2. Select your desired tone from the "Tone" dropdown
3. Click "Colorize!" to process images with the selected tone
4. The tone will be remembered for future sessions

### For Developers

#### Backend API

The `/colorize-image-data` endpoint now accepts a `tone` parameter:

```python
{
    "imgName": "image.jpg",
    "imgURL": "https://...",
    "colorize": true,
    "upscale": true,
    "tone": "bright"  # Optional, defaults to 'neutral'
}
```

#### Customizing Themes

**Option 1: Replace Reference Images (Recommended)**

The easiest way to customize themes is to replace the reference images in `Backend/tone_references/`:

1. Find images that embody your desired color aesthetic
2. Rename them to match theme names (e.g., `bright.jpg`, `dark.png`)
3. Place them in the `tone_references` directory
4. Restart the backend server

**Option 2: Add New Themes**

To add entirely new themes:

1. Add the theme name to the `THEMES` list in `tone_adjuster.py`:
   ```python
   THEMES = ['neutral', 'bright', 'dark', 'warm', 'cool', 'vibrant', 'pastel', 'your_theme']
   ```

2. Create a reference image named `your_theme.jpg` (or .png, .bmp) in `tone_references/`

3. Add the theme option to all frontend popup HTML files:
   ```html
   <option value="your_theme">Your Theme</option>
   ```

#### Generating Placeholder References

If you want to regenerate the placeholder images:

```bash
cd Backend/tone_references
python create_placeholders_simple.py  # Pure Python, no dependencies
# or
python create_placeholders_pil.py    # Better quality, requires Pillow
# or  
python create_placeholders.py        # Best quality, requires numpy + opencv
```

## Technical Details

### Processing Order
1. Denoise (if enabled)
2. Colorize (if enabled)
3. Upscale (if enabled)
4. **Tone Adjustment** (if tone != 'neutral')
5. Return result

### Performance
Color transfer adds minimal processing time (~0.01-0.05 seconds per image) since it only involves:
- Two color space conversions (RGB↔LAB)
- Statistical calculations (mean, std dev)
- Simple arithmetic operations

The algorithm is highly efficient and works on images of any size.

### Color Space Operations
1. **RGB → BGR → LAB**: Convert input to LAB color space
2. **Statistics**: Calculate mean and std dev for L, A, B channels
3. **Transfer**: Apply color transfer formula per channel
4. **LAB → BGR → RGB**: Convert back to RGB output

### Size Independence
The color transfer algorithm is completely size-independent:
- Reference images can be any dimension (64x64 to 4K+)
- Works on any manga resolution
- Only color statistics matter, not image dimensions

## Examples

The tone adjustment creates dramatically different moods from the same colorized base:

- **Neutral**: Original AI colorization output
- **Bright**: Adopts vibrant, cheerful color palette from reference
- **Dark**: Transfers moody, dramatic color characteristics
- **Warm**: Takes on cozy, warm tones from reference image
- **Cool**: Applies calm, cool atmospheric colors
- **Vibrant**: Inherits bold, saturated color distribution
- **Pastel**: Adopts soft, gentle color aesthetics

### Real-World Usage Tips

1. **Find the right references**: The quality of tone adjustment depends heavily on your reference images
2. **Test different sources**: Try photos, artwork, or even anime screenshots as references
3. **Match your manga style**: Use references that complement your manga's art style
4. **Experiment**: The same manga can look completely different with different references

## Troubleshooting

### Tone adjustment is being skipped

Check the server logs. If you see:
```
[-] No reference image found for theme 'bright', skipping tone adjustment
```

**Solution**: Create reference images in `Backend/tone_references/` directory

### Colors look wrong

The reference image's color distribution is too different from your manga's style.

**Solution**: Choose a more appropriate reference image or adjust the reference colors

### Processing is slow

Color transfer is very fast. Slowness is likely from colorization/upscaling, not tone adjustment.

**Solution**: Check other processing settings (upscale factor, image size)

## Advanced: Understanding LAB Color Space

LAB color space is designed to approximate human vision:
- **L (Lightness)**: 0 (black) to 100 (white)  
- **A channel**: Green (negative) to Red (positive)
- **B channel**: Blue (negative) to Yellow (positive)

The color transfer formula ensures:
- The relative color distribution is preserved
- The absolute colors match the reference's statistics
- Perceptually smooth transitions

This is why LAB-based color transfer produces more natural results than simple RGB adjustments.
