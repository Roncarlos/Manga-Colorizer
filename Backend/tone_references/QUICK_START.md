# Quick Start: Customizing Tone References

## Your Reference Images Are Ready to Replace!

The tone adjustment system uses placeholder images located in:
```
Backend/tone_references/
```

## Current Placeholder Images

✓ `bright.bmp` - Simple gradient with bright colors  
✓ `dark.bmp` - Simple gradient with dark colors  
✓ `warm.bmp` - Simple gradient with warm tones  
✓ `cool.bmp` - Simple gradient with cool tones  
✓ `vibrant.bmp` - Simple gradient with vibrant colors  
✓ `pastel.bmp` - Simple gradient with pastel colors  

## How to Replace Them

1. **Find or create images** that have the color aesthetic you want for each theme

2. **Rename your images** to match the theme names:
   - `bright.jpg` (or .png, .bmp, .jpeg)
   - `dark.jpg`
   - `warm.jpg`
   - `cool.jpg`
   - `vibrant.jpg`
   - `pastel.jpg`

3. **Copy them** to `Backend/tone_references/` (replacing the .bmp files)

4. **Restart** the backend server

## Image Requirements

- ✓ Any size (256x256, 512x512, 1920x1080, etc. - doesn't matter!)
- ✓ Any format (JPG, PNG, BMP)
- ✓ The color distribution matters, not the content
- ✓ More color variety in the reference = better transfer results

## Ideas for Reference Sources

### Bright Theme
- Sunny day photos
- Colorful flower gardens
- Happy anime scenes
- Bright illustrations

### Dark Theme
- Night photography
- Film noir movie stills
- Moody artwork
- Dark anime backgrounds

### Warm Theme
- Sunset/sunrise photos
- Autumn scenery
- Candlelight photos
- Sepia-toned images

### Cool Theme
- Winter landscapes
- Underwater photography
- Night/moonlight scenes
- Blue-tinted artwork

### Vibrant Theme
- Pop art
- Tropical scenes
- Saturated anime artwork
- Colorful street photography

### Pastel Theme
- Watercolor paintings
- Spring flowers
- Soft illustrations
- Pastel aesthetic photos

## Testing Your References

1. Replace one reference image (e.g., `bright.jpg`)
2. Set tone to "Bright" in the extension
3. Colorize a manga page
4. Check if the colors match your expectations
5. Adjust the reference image if needed

## Pro Tips

- **Use manga/anime as references**: If you want a specific anime's color palette, use a screenshot from that anime!
- **Combine references**: Create a collage of multiple images with the colors you want
- **Test on different manga**: Some references work better with certain art styles
- **Keep backups**: Save your original references before replacing

## Technical Note

The system uses **color transfer in LAB color space**:
- It copies the color statistics (mean, standard deviation) from your reference
- Applies them to the colorized manga
- Preserves the manga's structure while changing its color mood

This is much more sophisticated than simple brightness/saturation adjustments!
