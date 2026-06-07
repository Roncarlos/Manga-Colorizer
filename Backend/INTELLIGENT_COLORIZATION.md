# Intelligent Manga Colorization with Semantic Segmentation

This module provides intelligent, region-aware colorization of manga/anime images using semantic segmentation combined with CLIP-guided refinement.

## Features

- **Automatic Semantic Segmentation**: Detects character, background, hair, body/clothing regions
- **Intelligent Color Mapping**: Automatically assigns colors to regions based on text prompts
- **CLIP Refinement**: Further refines colors using CLIP similarity for natural results
- **Fallback Mode**: Works in CLIP-only mode if segmentation is unavailable

## Installation

Install the anime-segmentation package:

```bash
pip install anime-segmentation
```

Or add to your requirements:

```
anime-segmentation
```

## Quick Start

### Command Line

```bash
# Basic usage
python intelligent_inference.py -i input.jpg -p "red hair, blue background, green dress" -o output.png

# Visualize detected regions
python intelligent_inference.py -i input.jpg -p "blonde hair, purple outfit" -o output.png \
    --visualize-masks --mask-output masks.png

# CLIP-only mode (no segmentation)
python intelligent_inference.py -i input.jpg -p "vibrant sunset colors" -o output.png --no-segmentation
```

### Python API

```python
from colorizator import MangaColorizator
from intelligent_colorizer import IntelligentColorizator
from PIL import Image

# Initialize
config = {
    'g_weight_path': '../networks/generator.zip',
    'extractor_path': '../networks/extractor.pth',
    'device': 'cuda'
}

colorizer = IntelligentColorizator(config)

# Colorize with text prompt
image = Image.open('input.jpg').convert('L')
result = colorizer.colorize_intelligently(
    image,
    prompt="red hair, blue background, green dress",
    size=576,
    refine=True
)

# Save result
Image.fromarray(result).save('output.png')
```

## How It Works

### 1. Semantic Segmentation

The system uses **AnimeSegmentation** (based on U2-Net) to automatically detect:

- **Character** (foreground): Main subject, typically the person/character
- **Background**: Sky, walls, rooms, etc.
- **Hair**: Top ~30% of character bounding box
- **Body/Clothing**: Lower portion of character

### 2. Prompt Parsing

The text prompt is parsed to extract color assignments:

```python
"red hair, blue background, green dress"
↓
{
    'hair': RGB(220, 20, 60),        # red
    'background': RGB(30, 144, 255),  # blue
    'body': RGB(34, 139, 34)          # green
}
```

### 3. Color Hint Generation

Colors are applied to the detected regions to create color hints:

```
Segmentation Mask + Color Assignment = Color Hint Image
     [hair region]        [red]            [red pixels in hair region]
```

### 4. Colorization with Hints

The hint image guides the base colorizer:

```python
# Color hints are fed to the model
result = colorizer.colorize_with_hints(grayscale, hint_image, hint_mask)
```

### 5. CLIP Refinement (Optional)

Final refinement using CLIP similarity to ensure colors match the prompt semantically.

## Region Keywords

The prompt parser recognizes these keywords:

### Hair Region

- `hair`, `head`

### Background Region

- `background`, `bg`, `backdrop`, `sky`, `wall`, `room`

### Body/Clothing Region

- `shirt`, `dress`, `clothing`, `clothes`, `outfit`, `wear`, `garment`

### Character/Skin Region

- `skin`, `face`, `character`

## Supported Colors

Standard colors:

- `red`, `blue`, `green`, `yellow`, `orange`, `purple`, `pink`
- `brown`, `black`, `white`, `gray`/`grey`
- `cyan`, `magenta`, `violet`
- `gold`, `silver`

Anime-specific:

- `blonde` (light yellow for hair)
- `brunette` (brown for hair)

## Advanced Usage

### Custom Refinement Parameters

```python
# Adjust CLIP refinement
colorizer.set_refinement_params(
    steps=5,              # More steps = stronger refinement
    color_strength=0.4    # Higher = more CLIP influence
)
```

### Visualize Segmentation Masks

```python
result = colorizer.colorize_intelligently(
    image,
    prompt="red hair, blue bg",
    visualize_masks=True,
    mask_output_path="masks.png"
)
```

This creates a visualization showing:

- Original image
- Character mask
- Background mask
- Hair mask
- Body mask

### Disable Segmentation

```python
# Use CLIP-only mode
colorizer.disable_segmentation()
result = colorizer.colorize_intelligently(image, "vibrant colors")
```

### Fine-Grained Control

```python
from manga_segmenter import MangaSegmenter, PromptBasedColorAssigner

# Manual segmentation
segmenter = MangaSegmenter(device='cuda')
masks = segmenter.segment_detailed(image)

# Manual color assignment
assigner = PromptBasedColorAssigner()
assignments = assigner.parse_prompt("red hair, blue dress")
hint_image, hint_mask = assigner.create_colored_hints(masks, assignments)

# Use with base colorizer
from clip_colorizer import CLIPGuidedColorizator
clip_colorizer = CLIPGuidedColorizator(config)
result = clip_colorizer.colorize_with_hints_and_prompt(
    image, hint_image, hint_mask, "red hair, blue dress"
)
```

## Command Line Options

```bash
python intelligent_inference.py [OPTIONS]

Required:
  -i, --input PATH          Input grayscale image
  -p, --prompt TEXT         Text description with colors
  -o, --output PATH         Output path

Models:
  -g, --generator PATH      Generator model path
  -e, --extractor PATH      Extractor model path
  --clip-model NAME         CLIP variant (default: ViT-B/32)

Segmentation:
  --no-segmentation         Disable segmentation (CLIP-only)
  --visualize-masks         Show detected regions
  --mask-output PATH        Save mask visualization

Processing:
  -s, --size INT           Processing size (default: 576)
  --no-refine              Disable CLIP refinement
  --refine-steps INT       CLIP refinement iterations (default: 3)
  --color-strength FLOAT   CLIP blending strength (default: 0.3)
  --cpu                    Use CPU instead of GPU
```

## Example Prompts

### Character Focus

```bash
# Hair coloring
python intelligent_inference.py -i page.jpg -p "blonde hair" -o out.png
python intelligent_inference.py -i page.jpg -p "red hair, green eyes" -o out.png

# With outfit
python intelligent_inference.py -i page.jpg -p "purple hair, blue dress" -o out.png
```

### Scene Focus

```bash
# Background coloring
python intelligent_inference.py -i page.jpg -p "sunset background" -o out.png
python intelligent_inference.py -i page.jpg -p "blue sky background" -o out.png

# Complete scene
python intelligent_inference.py -i page.jpg -p "orange hair, white shirt, pink background" -o out.png
```

### Complex Descriptions

```bash
# Multi-region
python intelligent_inference.py -i page.jpg \
    -p "blonde hair, green dress, purple background, gold accessories" \
    -o out.png

# Natural language (CLIP will help)
python intelligent_inference.py -i page.jpg \
    -p "vibrant sunset colors with warm tones" \
    -o out.png
```

## Technical Details

### Models Used

1. **AnimeSegmentation** (isnetis variant)

   - Architecture: U2-Net based
   - Purpose: Character/background separation
   - Input: RGB or grayscale manga images
   - Output: Binary segmentation mask

2. **CLIP** (ViT-B/32)

   - Purpose: Text-image similarity for refinement
   - Compares colorized output with text prompt
   - Guides iterative color adjustment

3. **MangaColorizator** (base model)
   - Architecture: SEResNeXt encoder + U-Net decoder
   - Purpose: Actual colorization with hints
   - Input: Grayscale + color hints + mask

### Pipeline Flow

```
Grayscale Image + Text Prompt
         ↓
    Segmentation (AnimeSegmentation)
         ↓
   Region Detection (character, bg, hair, body)
         ↓
    Prompt Parsing (extract colors + regions)
         ↓
  Color Hint Creation (assign colors to masks)
         ↓
  Base Colorization (MangaColorizator with hints)
         ↓
   CLIP Refinement (iterative adjustment)
         ↓
    Final Result
```

### Performance

- **Segmentation**: ~0.5-1s per image (GPU)
- **Base Colorization**: ~2-3s per image (GPU)
- **CLIP Refinement**: ~1-2s per iteration (GPU)
- **Total**: ~5-10s per image with all features

GPU recommended for best performance.

## Troubleshooting

### "AnimeSegmentation not installed"

```bash
pip install anime-segmentation
```

### Segmentation not working

```python
# Check if available
from manga_segmenter import ANIME_SEG_AVAILABLE
print(ANIME_SEG_AVAILABLE)

# Use CLIP-only mode
python intelligent_inference.py -i input.jpg -p "prompt" -o out.png --no-segmentation
```

### Colors not applied correctly

1. **Check region keywords**: Ensure prompt uses recognized keywords

   ```python
   # Good
   "red hair, blue background"

   # Bad (won't be recognized)
   "red bangs, blue scenery"
   ```

2. **Visualize masks** to see detected regions:

   ```bash
   python intelligent_inference.py -i input.jpg -p "red hair" -o out.png \
       --visualize-masks --mask-output masks.png
   ```

3. **Adjust color strength**:
   ```bash
   python intelligent_inference.py -i input.jpg -p "red hair" -o out.png \
       --color-strength 0.5  # Increase CLIP influence
   ```

### Out of memory

```bash
# Reduce processing size
python intelligent_inference.py -i input.jpg -p "prompt" -o out.png --size 384

# Use CPU
python intelligent_inference.py -i input.jpg -p "prompt" -o out.png --cpu
```

## Limitations

1. **Segmentation accuracy**: Hair/body detection is heuristic-based (top 30% = hair)
2. **Complex scenes**: Works best with single character + simple background
3. **Prompt dependency**: Results depend on clear color+region keywords
4. **Processing time**: Slower than base colorization due to segmentation + CLIP

## Future Improvements

- Fine-grained segmentation (face, eyes, accessories)
- Multi-character support with separate regions
- Learned region detection instead of heuristics
- Interactive mask editing
- Region-specific style transfer

## See Also

- [clip_colorizer.py](clip_colorizer.py) - CLIP-guided colorization (no segmentation)
- [manga_segmenter.py](manga_segmenter.py) - Segmentation module
- [colorizator.py](colorizator.py) - Base colorizer
