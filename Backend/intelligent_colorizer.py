"""
Intelligent CLIP-Guided Colorization with Semantic Segmentation

This module combines semantic segmentation with CLIP guidance for intelligent,
region-aware colorization based on text prompts.

Usage:
    from intelligent_colorizer import IntelligentColorizator
    
    colorizer = IntelligentColorizator(config)
    result = colorizer.colorize_intelligently(image, "red hair, blue background")
"""

import torch
import numpy as np
from PIL import Image
import logging

from clip_colorizer import CLIPGuidedColorizator
from manga_segmenter import MangaSegmenter, PromptBasedColorAssigner

try:
    from manga_segmenter import SEGMENTATION_AVAILABLE
except ImportError:
    SEGMENTATION_AVAILABLE = False


class IntelligentColorizator:
    """
    Combines semantic segmentation with CLIP-guided colorization
    for intelligent, region-aware manga colorization
    """
    
    def __init__(self, config, clip_model_name="ViT-B/32", use_segmentation=True):
        """
        Initialize intelligent colorizer
        
        Args:
            config: MangaColorizator config
            clip_model_name: CLIP model variant
            use_segmentation: Whether to use semantic segmentation
        """
        # Initialize CLIP-guided colorizer
        self.clip_colorizer = CLIPGuidedColorizator(config, clip_model_name)
        self.device = self.clip_colorizer.device
        
        # Initialize segmenter if available
        self.use_segmentation = use_segmentation and SEGMENTATION_AVAILABLE
        
        if self.use_segmentation:
            try:
                self.segmenter = MangaSegmenter(device=self.device)
                self.color_assigner = PromptBasedColorAssigner()
                logging.info("Semantic segmentation enabled")
            except Exception as e:
                logging.warning(f"Failed to initialize segmenter: {e}")
                logging.warning("Falling back to CLIP-only mode")
                self.use_segmentation = False
        else:
            self.segmenter = None
            self.color_assigner = None
            if not SEGMENTATION_AVAILABLE:
                logging.info("Semantic segmentation not available (install rembg)")
            else:
                logging.info("Semantic segmentation disabled")
    
    def colorize_intelligently(self, image, prompt, size=576, refine=True, 
                              visualize_masks=False, mask_output_path=None,
                              hint_mode='sparse'):
        """
        Intelligently colorize image using segmentation and CLIP guidance
        
        Args:
            image: Input grayscale image (PIL Image or numpy array)
            prompt: Text description (e.g., "red hair, blue background, green dress")
            size: Processing size
            refine: Whether to apply CLIP refinement
            visualize_masks: Whether to visualize segmentation masks
            mask_output_path: Path to save mask visualization
            hint_mode: 'sparse' (subtle edge hints), 'medium', or 'full' (fill regions)
            
        Returns:
            Colorized image as numpy array
        """
        logging.info(f"Intelligent colorization with prompt: '{prompt}'")
        
        # Convert to numpy if PIL
        if hasattr(image, 'mode'):
            img_array = np.array(image)
        else:
            img_array = image.copy()
        
        # Step 1: Semantic Segmentation (if enabled)
        if self.use_segmentation and self.segmenter:
            logging.info("Performing semantic segmentation...")
            
            # Segment image into regions
            masks = self.segmenter.segment_detailed(img_array)
            
            # Visualize if requested
            if visualize_masks:
                self.segmenter.visualize_masks(img_array, masks, mask_output_path)
            
            # Parse prompt to assign colors to regions
            color_assignments = self.color_assigner.parse_prompt(prompt)
            
            if color_assignments:
                logging.info(f"Color assignments: {list(color_assignments.keys())}")
                
                # Create color hints based on segmentation
                hint_image, hint_mask = self.color_assigner.create_colored_hints(
                    masks, color_assignments, hint_mode=hint_mode
                )
                
                # Use hints + CLIP guidance
                result = self.clip_colorizer.colorize_with_hints_and_prompt(
                    img_array,
                    hint_image,
                    hint_mask,
                    prompt,
                    size=size,
                    refine=refine
                )
            else:
                logging.info("No color assignments found, using CLIP-only mode")
                result = self.clip_colorizer.colorize_with_prompt(
                    img_array,
                    prompt,
                    size=size,
                    refine=refine
                )
        else:
            # Fallback to CLIP-only mode
            logging.info("Using CLIP-only colorization (no segmentation)")
            result = self.clip_colorizer.colorize_with_prompt(
                img_array,
                prompt,
                size=size,
                refine=refine
            )
        
        return result
    
    def set_refinement_params(self, steps=3, color_strength=0.3):
        """Configure CLIP refinement parameters"""
        self.clip_colorizer.set_refinement_params(steps=steps, color_strength=color_strength)
    
    def disable_segmentation(self):
        """Disable semantic segmentation"""
        self.use_segmentation = False
        logging.info("Semantic segmentation disabled")
    
    def enable_segmentation(self):
        """Enable semantic segmentation if available"""
        if SEGMENTATION_AVAILABLE and self.segmenter:
            self.use_segmentation = True
            logging.info("Semantic segmentation enabled")
        else:
            logging.warning("Cannot enable segmentation: not available")


# Convenience function
def intelligent_colorize(config, image, prompt, **kwargs):
    """
    Quick function for intelligent colorization
    
    Args:
        config: MangaColorizator config
        image: Input image
        prompt: Text description
        **kwargs: Additional arguments
        
    Returns:
        Colorized image
    """
    colorizer = IntelligentColorizator(config)
    return colorizer.colorize_intelligently(image, prompt, **kwargs)
