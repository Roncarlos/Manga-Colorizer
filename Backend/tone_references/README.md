# Tone Reference Images

This directory contains reference images used for color transfer-based tone adjustment.

## How It Works

The tone adjustment system uses **color transfer in LAB color space**:

1. Each theme (bright, dark, warm, cool, vibrant, pastel) has a reference image
2. When applying a tone, the system:
   - Converts both the colorized manga and the reference image to LAB color space
   - Calculates mean and standard deviation for each channel (L, A, B)
   - Transfers the color statistics: `new_pixel = ((old_pixel - source_mean) * (target_std / source_std)) + target_mean`
   - Converts back to RGB

## Image Requirements

- **Format**: JPG, PNG, or BMP
- **Size**: Any size (color transfer is size-independent)
- **Naming**: Must match theme names:
  - `bright.jpg` (or .png, .bmp)
  - `dark.jpg`
  - `warm.jpg`
  - `cool.jpg`
  - `vibrant.jpg`
  - `pastel.jpg`
  - `neutral` theme doesn't need a reference (no adjustment applied)

## Creating Reference Images

### Option 1: Use the Placeholder Generator

If you have numpy and opencv installed in your Python environment:

```bash
python create_placeholders.py
```

This creates simple gradient placeholder images with representative colors.

### Option 2: Manual Creation

1. Find or create images that embody the mood you want:
   - **Bright**: Cheerful photos with high brightness and saturation (sunny day, flowers)
   - **Dark**: Moody images with low key lighting (night scenes, film noir)
   - **Warm**: Images with warm tones (sunset, autumn leaves, candlelight)
   - **Cool**: Images with cool tones (winter scenes, underwater, moonlight)
   - **Vibrant**: Bold, saturated images (pop art, tropical scenes)
   - **Pastel**: Soft, muted images (watercolor art, spring flowers)

2. Crop/resize them to any size (512x512 recommended but not required)

3. Save them with the correct names in this directory

### Option 3: Use Sample Images

You can use manga panels or anime screenshots that have the color aesthetic you want to replicate.

## Tips

- The reference image's color distribution will be transferred to your colorized manga
- Use images with good color variety (not monochrome)
- The actual content of the reference image doesn't matter - only its color characteristics
- You can test different references to find what works best for your manga style

## Current Status

⚠️ **Placeholder images need to be created**

Run `create_placeholders.py` (requires numpy and opencv-python) or add your own reference images.

Without reference images, the tone adjustment will be skipped and a warning will be logged.
