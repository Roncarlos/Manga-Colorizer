#!/usr/bin/env python3
"""
CLIP-Guided Colorization Inference Script

This script demonstrates how to use CLIP-guided text prompts for manga colorization.

Usage:
    python clip_inference.py --input manga.png --prompt "red hair, blue eyes" --output result.png
    
Requirements:
    pip install git+https://github.com/openai/CLIP.git
"""

import argparse
import sys
from pathlib import Path
from PIL import Image
import numpy as np
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from clip_colorizer import CLIPGuidedColorizator
from types import SimpleNamespace


def main():
    parser = argparse.ArgumentParser(
        description='Colorize manga with text prompts using CLIP guidance',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python clip_inference.py -i manga.png -p "red hair, blue eyes" -o result.png
  
  # Multiple color descriptions
  python clip_inference.py -i page.png -p "blonde hair, green dress, purple background" -o colored.png
  
  # Adjust refinement strength
  python clip_inference.py -i manga.png -p "pink hair" -o result.png --strength 0.5 --steps 5
  
  # Without CLIP refinement (just base colorization)
  python clip_inference.py -i manga.png -p "red hair" -o result.png --no-refine
        """
    )
    
    parser.add_argument('--input', '-i', type=str, required=True,
                        help='Input grayscale manga image')
    parser.add_argument('--prompt', '-p', type=str, required=True,
                        help='Text description for colors (e.g., "red hair, blue eyes")')
    parser.add_argument('--output', '-o', type=str, required=True,
                        help='Output colorized image path')
    
    # Model parameters
    parser.add_argument('--colorizer-path', type=str, default='networks/generator.zip',
                        help='Path to colorizer model')
    parser.add_argument('--clip-model', type=str, default='ViT-B/32',
                        choices=['RN50', 'RN101', 'RN50x4', 'RN50x16', 'RN50x64', 'ViT-B/32', 'ViT-B/16', 'ViT-L/14'],
                        help='CLIP model variant')
    
    # Processing parameters
    parser.add_argument('--size', type=int, default=576,
                        help='Processing size (must be divisible by 32)')
    parser.add_argument('--device', type=str, default='cuda',
                        choices=['cuda', 'cpu'],
                        help='Device to use')
    
    # Refinement parameters
    parser.add_argument('--no-refine', action='store_true',
                        help='Skip CLIP refinement (faster but less accurate)')
    parser.add_argument('--steps', type=int, default=3,
                        help='Number of refinement iterations')
    parser.add_argument('--strength', type=float, default=0.3,
                        help='Color adjustment strength (0.0-1.0)')
    
    # Other
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(levelname)s - %(message)s'
    )
    
    # Validate inputs
    if not Path(args.input).exists():
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)
    
    if not Path(args.colorizer_path).exists():
        print(f"Error: Colorizer model not found: {args.colorizer_path}")
        print("Download it from: https://drive.google.com/file/d/1qmxUEKADkEM4iYLp1fpPLLKnfZ6tcF-t/view")
        sys.exit(1)
    
    if args.size % 32 != 0:
        print(f"Error: Size must be divisible by 32, got {args.size}")
        sys.exit(1)
    
    # Create config
    config = SimpleNamespace(
        device=args.device,
        colorizer_path=args.colorizer_path,
        colorizer_tile_size=0,
        tile_pad=16
    )
    
    print("="*80)
    print("CLIP-GUIDED MANGA COLORIZATION")
    print("="*80)
    print(f"Input:  {args.input}")
    print(f"Prompt: {args.prompt}")
    print(f"Output: {args.output}")
    print(f"Model:  {args.colorizer_path}")
    print(f"CLIP:   {args.clip_model}")
    print(f"Device: {args.device}")
    if not args.no_refine:
        print(f"Refine: {args.steps} steps, strength={args.strength}")
    else:
        print(f"Refine: Disabled")
    print("="*80)
    
    # Load image
    print("\n[1/4] Loading image...")
    input_image = Image.open(args.input).convert('L')  # Convert to grayscale
    print(f"  Image size: {input_image.size}")
    
    # Initialize colorizer
    print("\n[2/4] Initializing CLIP-guided colorizer...")
    try:
        colorizer = CLIPGuidedColorizator(config, clip_model_name=args.clip_model)
        
        # Set refinement parameters
        if not args.no_refine:
            colorizer.set_refinement_params(
                steps=args.steps,
                color_strength=args.strength
            )
    except ImportError as e:
        print(f"\nError: {e}")
        print("\nInstall CLIP with:")
        print("  pip install git+https://github.com/openai/CLIP.git")
        sys.exit(1)
    
    # Colorize
    print(f"\n[3/4] Colorizing with prompt: '{args.prompt}'")
    result = colorizer.colorize_with_prompt(
        input_image,
        args.prompt,
        size=args.size,
        refine=not args.no_refine
    )
    
    # Save result
    print(f"\n[4/4] Saving result to: {args.output}")
    output_image = Image.fromarray(result)
    
    # Create output directory if needed
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    output_image.save(args.output)
    
    print("\n" + "="*80)
    print("✓ COLORIZATION COMPLETE!")
    print("="*80)
    print(f"\nResult saved to: {args.output}")
    print(f"Original size: {input_image.size}")
    print(f"Output size:   {output_image.size}")
    
    # Show detected colors
    color_hints = colorizer._parse_color_hints_from_prompt(args.prompt)
    if color_hints:
        print(f"\nDetected colors: {', '.join([c[0] for c in color_hints])}")


if __name__ == '__main__':
    main()
