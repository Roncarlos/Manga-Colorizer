# Tone Reference Images

This directory contains reference images used for color tone adjustments.

## How It Works

The colorizer uses color transfer in LAB color space to adjust the tone of colorized manga images. Each image file in this directory represents a different tone preset that users can select.

## Adding Custom Tones

To add a new tone:

1. **Add an image file** to this directory with your desired color palette/tone

   - Supported formats: `.jpg`, `.jpeg`, `.png`, `.bmp`
   - Recommended size: At least 512x512 pixels
   - The image should represent the overall color mood you want

2. **Name the file** using a descriptive tone name (e.g., `sunset.jpg`, `vintage.png`)

   - The filename (without extension) becomes the tone name
   - Use lowercase letters, numbers, and hyphens/underscores
   - Example: `my-custom-tone.jpg` → appears as "My-custom-tone" in the UI

3. **Restart or wait** for the backend to detect the new tone

   - Tones are cached for 60 seconds and auto-detected
   - No code changes needed!

4. The new tone will automatically appear in the browser extension's tone selector

## Default Tones

The following default tones are included:

- **neutral** - No adjustment (special case, no image needed)
- **bright** - Lighter, more illuminated colors
- **dark** - Darker, more shadowed colors
- **warm** - Warmer tones (oranges, reds, yellows)
- **cool** - Cooler tones (blues, cyans)
- **vibrant** - More saturated, vivid colors
- **pastel** - Softer, desaturated colors

## Docker Volume Mapping

When running via Docker, this directory is mapped as:

```yaml
volumes:
  - ./Backend/tones:/app/tones
```

You can add/remove tone images without rebuilding the container. The changes will be detected automatically.

## Tips for Creating Good Tone References

1. **Use representative images**: Choose images that strongly represent the mood/tone you want
2. **Avoid complex scenes**: Simple gradients or color palettes work best
3. **High quality**: Use high-resolution images for better color statistics
4. **Test and iterate**: Try different reference images to get the desired effect
5. **Color balance**: Ensure your reference image has the color balance you want to transfer

## Environment Variable

You can customize the tones directory location using the `TONES_DIR` environment variable:

```bash
export TONES_DIR=/path/to/custom/tones
```

Or in docker-compose:

```yaml
environment:
  - TONES_DIR=/app/custom-tones
volumes:
  - ./my-tones:/app/custom-tones
```
