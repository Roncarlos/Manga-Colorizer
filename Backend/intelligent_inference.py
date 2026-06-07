"""
Intelligent Manga Colorization CLI

Combines semantic segmentation with CLIP-guided colorization for
intelligent, region-aware manga colorization.

Usage:
    # Basic intelligent colorization
    python intelligent_inference.py -i input.jpg -p "red hair, blue background" -o output.png
    
    # With mask visualization
    python intelligent_inference.py -i input.jpg -p "blonde hair, purple dress" -o output.png --visualize-masks --mask-output masks.png
    
    # Disable segmentation (CLIP-only)
    python intelligent_inference.py -i input.jpg -p "vibrant colors" -o output.png --no-segmentation
"""

import argparse
import logging
from pathlib import Path
import numpy as np
from PIL import Image
from types import SimpleNamespace

from colorizator import MangaColorizator
from intelligent_colorizer import IntelligentColorizator

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def main():
    parser = argparse.ArgumentParser(
        description='Intelligent Manga Colorization with Semantic Segmentation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Colorize with segmentation-based hints
  python intelligent_inference.py -i page.jpg -p "red hair, blue background, green dress" -o colored.png
  
  # Visualize detected regions
  python intelligent_inference.py -i page.jpg -p "yellow hair" -o out.png --visualize-masks --mask-output masks.png
  
  # CLIP-only mode (no segmentation)
  python intelligent_inference.py -i page.jpg -p "sunset colors" -o out.png --no-segmentation
  
Region keywords:
  - hair: "hair", "head"
  - background: "background", "bg", "sky", "wall", "room"
  - body: "shirt", "dress", "clothing", "clothes", "outfit"
  
Supported colors:
  red, blue, green, yellow, orange, purple, pink, brown, black, white,
  gray/grey, cyan, magenta, violet, gold, silver, blonde, brunette
        """
    )
    
    # Required arguments
    parser.add_argument('-i', '--input', required=True, help='Input grayscale image path')
    parser.add_argument('-p', '--prompt', required=True, 
                       help='Text description (e.g., "red hair, blue background, green dress")')
    parser.add_argument('-o', '--output', required=True, help='Output path for colorized image')
    
    # Model arguments
    parser.add_argument('-g', '--generator', default='networks/generator.zip',
                       help='Path to generator model (default: networks/generator.zip)')
    parser.add_argument('-e', '--extractor', default='networks/extractor.pth',
                       help='Path to extractor model (default: networks/extractor.pth)')
    
    # CLIP arguments
    parser.add_argument('--clip-model', default='ViT-B/32',
                       choices=['RN50', 'RN101', 'RN50x4', 'RN50x16', 'ViT-B/32', 'ViT-B/16', 'ViT-L/14'],
                       help='CLIP model variant (default: ViT-B/32)')
    
    # Segmentation arguments
    parser.add_argument('--no-segmentation', action='store_true',
                       help='Disable semantic segmentation (use CLIP-only mode)')
    parser.add_argument('--visualize-masks', action='store_true',
                       help='Visualize detected semantic regions')
    parser.add_argument('--mask-output', default=None,
                       help='Path to save mask visualization')
    parser.add_argument('--hint-mode', choices=['sparse', 'medium', 'full'], default='sparse',
                       help='Hint density: sparse=edges only (default), medium=reduced fill, full=fill regions')
    
    # Processing arguments
    parser.add_argument('-s', '--size', type=int, default=576,
                       help='Processing size (default: 576)')
    parser.add_argument('--no-refine', action='store_true',
                       help='Disable CLIP-based refinement')
    parser.add_argument('--refine-steps', type=int, default=3,
                       help='Number of CLIP refinement steps (default: 3)')
    parser.add_argument('--color-strength', type=float, default=0.3,
                       help='CLIP color blending strength (default: 0.3)')
    
    # Device
    parser.add_argument('--cpu', action='store_true', help='Use CPU instead of GPU')
    
    args = parser.parse_args()
    
    # Validate input
    if not Path(args.input).exists():
        logging.error(f"Input file not found: {args.input}")
        return 1
    
    # Set device
    device = 'cpu' if args.cpu else 'cuda'
    
    # Initialize base colorizer config
    logging.info("Loading models...")
    config = SimpleNamespace(
        colorizer_path=args.generator,
        extractor_path=args.extractor,
        device=device,
        colorizer_tile_size=0,
        tile_pad=8
    )
    
    # Initialize intelligent colorizer
    colorizer = IntelligentColorizator(
        config,
        clip_model_name=args.clip_model,
        use_segmentation=not args.no_segmentation
    )
    
    # Set refinement parameters
    colorizer.set_refinement_params(
        steps=args.refine_steps,
        color_strength=args.color_strength
    )
    
    # Load image
    logging.info(f"Loading image: {args.input}")
    image = Image.open(args.input)
    
    # Convert to grayscale if needed
    if image.mode != 'L':
        logging.info("Converting to grayscale...")
        image = image.convert('L')
    
    # Colorize
    logging.info("Starting intelligent colorization...")
    result = colorizer.colorize_intelligently(
        image,
        args.prompt,
        size=args.size,
        refine=not args.no_refine,
        visualize_masks=args.visualize_masks,
        mask_output_path=args.mask_output,
        hint_mode=args.hint_mode
    )
    
    # Save result
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    result_img = Image.fromarray(result.astype(np.uint8))
    result_img.save(output_path)
    
    logging.info(f"✓ Colorized image saved to: {args.output}")
    
    if args.visualize_masks and args.mask_output:
        logging.info(f"✓ Mask visualization saved to: {args.mask_output}")
    
    return 0


if __name__ == '__main__':
    exit(main())
