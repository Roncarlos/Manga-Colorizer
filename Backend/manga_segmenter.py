"""
Semantic Segmentation for Manga Images

This module provides automatic segmentation of manga/anime images into semantic regions
(character, background, hair, clothing) for intelligent color hint placement.

Models used:
- AnimeSegmentation: Character vs background separation
- Optional: More detailed segmentation for hair, clothing, etc.

Usage:
    from manga_segmenter import MangaSegmenter
    
    segmenter = MangaSegmenter()
    masks = segmenter.segment(image)
    # Returns: {'character': mask, 'background': mask, ...}
"""

import torch
import numpy as np
from PIL import Image
import cv2
import logging
from pathlib import Path
from io import BytesIO

try:
    from rembg import remove, new_session
    SEGMENTATION_AVAILABLE = True
except ImportError:
    SEGMENTATION_AVAILABLE = False
    logging.warning("rembg not installed. Install with: pip install rembg[gpu] onnxruntime-gpu")


class MangaSegmenter:
    """
    Automatic segmentation of manga/anime images into semantic regions
    Uses rembg for character/background separation
    """
    
    def __init__(self, device='cuda', model_name='u2net_human_seg'):
        """
        Initialize manga segmenter
        
        Args:
            device: 'cuda' or 'cpu' (note: rembg uses ONNX, device is informational)
            model_name: Model to use ('u2net_human_seg' or 'u2net' recommended)
        """
        if not SEGMENTATION_AVAILABLE:
            raise ImportError(
                "rembg is required. Install with:\n"
                "pip install rembg[gpu] onnxruntime-gpu"
            )
        
        self.device = device
        self.model_name = model_name
        logging.info(f"Loading rembg model: {model_name}")
        
        # Create rembg session
        try:
            self.session = new_session(model_name)
            logging.info("Manga segmenter initialized with rembg")
        except Exception as e:
            logging.warning(f"Failed to create specific session, using default: {e}")
            self.session = None
    
    def segment_character(self, image):
        """
        Segment character from background
        
        Args:
            image: PIL Image or numpy array
            
        Returns:
            dict with 'character' and 'background' masks (numpy arrays)
        """
        # Convert to PIL if needed
        if isinstance(image, np.ndarray):
            # Handle grayscale
            if len(image.shape) == 2:
                image_pil = Image.fromarray(image).convert('RGB')
            else:
                image_pil = Image.fromarray(image)
        else:
            image_pil = image
            if image_pil.mode == 'L':
                image_pil = image_pil.convert('RGB')
        
        # Remove background using rembg
        try:
            if self.session:
                output = remove(image_pil, session=self.session)
            else:
                output = remove(image_pil)
        except Exception as e:
            logging.error(f"Segmentation failed: {e}")
            # Fallback: return full image as character
            h, w = np.array(image_pil)[:, :, 0].shape
            return {
                'character': np.ones((h, w), dtype=np.float32),
                'background': np.zeros((h, w), dtype=np.float32),
                'full_mask': np.ones((h, w), dtype=np.float32)
            }
        
        # Extract alpha channel as mask
        output_np = np.array(output)
        
        if output_np.shape[2] == 4:  # RGBA
            mask = output_np[:, :, 3] / 255.0
        else:  # Fallback
            mask = np.ones(output_np.shape[:2], dtype=np.float32)
        
        # Character mask (foreground)
        character_mask = (mask > 0.5).astype(np.float32)
        
        # Background mask (inverse)
        background_mask = (mask <= 0.5).astype(np.float32)
        
        return {
            'character': character_mask,
            'background': background_mask,
            'full_mask': mask
        }
    
    def segment_detailed(self, image):
        """
        Perform detailed segmentation (hair, face, body, clothing)
        This is a heuristic-based approach since detailed anime segmentation is complex
        
        Args:
            image: PIL Image or numpy array
            
        Returns:
            dict with detailed masks
        """
        # Get basic segmentation first
        basic_masks = self.segment_character(image)
        character_mask = basic_masks['character']
        
        # Convert image to numpy if needed
        if isinstance(image, Image.Image):
            img_array = np.array(image)
        else:
            img_array = image.copy()
        
        # Convert to grayscale for edge detection
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Heuristic: top portion is likely hair/head
        height, width = character_mask.shape
        
        # Hair region: top 30% of character bounding box
        char_pixels = np.where(character_mask > 0.5)
        if len(char_pixels[0]) > 0:
            min_y, max_y = char_pixels[0].min(), char_pixels[0].max()
            min_x, max_x = char_pixels[1].min(), char_pixels[1].max()
            
            hair_region_height = int((max_y - min_y) * 0.3)
            
            hair_mask = np.zeros_like(character_mask)
            hair_mask[min_y:min_y+hair_region_height, min_x:max_x] = character_mask[min_y:min_y+hair_region_height, min_x:max_x]
            
            # Body/clothing: lower portion
            body_mask = character_mask.copy()
            body_mask[min_y:min_y+hair_region_height, :] = 0
        else:
            hair_mask = np.zeros_like(character_mask)
            body_mask = character_mask.copy()
        
        return {
            'character': character_mask,
            'background': basic_masks['background'],
            'hair': hair_mask,
            'body': body_mask,
            'full_mask': basic_masks['full_mask']
        }
    
    def create_semantic_masks(self, image, regions=['character', 'background']):
        """
        Create semantic masks for specified regions
        
        Args:
            image: Input image
            regions: List of regions to segment. Options:
                     'character', 'background', 'hair', 'body'
        
        Returns:
            dict of masks
        """
        # Check if detailed segmentation is needed
        needs_detailed = any(r in regions for r in ['hair', 'body'])
        
        if needs_detailed:
            return self.segment_detailed(image)
        else:
            return self.segment_character(image)
    
    def visualize_masks(self, image, masks, output_path=None):
        """
        Visualize segmentation masks
        
        Args:
            image: Original image
            masks: Dict of masks from segment_*
            output_path: Optional path to save visualization
        """
        import matplotlib.pyplot as plt
        
        # Convert image if needed
        if isinstance(image, Image.Image):
            img_array = np.array(image)
        else:
            img_array = image
        
        # Create figure
        n_masks = len(masks)
        fig, axes = plt.subplots(1, n_masks + 1, figsize=(4 * (n_masks + 1), 4))
        
        # Show original
        axes[0].imshow(img_array, cmap='gray' if len(img_array.shape) == 2 else None)
        axes[0].set_title('Original')
        axes[0].axis('off')
        
        # Show masks
        for idx, (name, mask) in enumerate(masks.items(), 1):
            if 'full' in name.lower():
                continue  # Skip full_mask
            axes[idx].imshow(mask, cmap='viridis')
            axes[idx].set_title(name.capitalize())
            axes[idx].axis('off')
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            logging.info(f"Visualization saved to {output_path}")
        else:
            plt.show()
        
        plt.close()


class PromptBasedColorAssigner:
    """
    Assigns colors to semantic regions based on text prompts
    """
    
    def __init__(self):
        # Region keywords mapping
        self.region_keywords = {
            'hair': ['hair', 'head'],
            'background': ['background', 'bg', 'backdrop', 'sky', 'wall', 'room'],
            'body': ['shirt', 'dress', 'clothing', 'clothes', 'outfit', 'wear', 'garment'],
            'character': ['skin', 'face', 'character']
        }
        
        # Color mappings
        self.color_map = {
            'red': np.array([220, 20, 60]),
            'blue': np.array([30, 144, 255]),
            'green': np.array([34, 139, 34]),
            'yellow': np.array([255, 215, 0]),
            'orange': np.array([255, 140, 0]),
            'purple': np.array([147, 112, 219]),
            'pink': np.array([255, 192, 203]),
            'brown': np.array([139, 69, 19]),
            'black': np.array([20, 20, 20]),
            'white': np.array([245, 245, 245]),
            'gray': np.array([128, 128, 128]),
            'grey': np.array([128, 128, 128]),
            'cyan': np.array([0, 255, 255]),
            'magenta': np.array([255, 0, 255]),
            'violet': np.array([138, 43, 226]),
            'gold': np.array([255, 215, 0]),
            'silver': np.array([192, 192, 192]),
            'blonde': np.array([255, 230, 140]),
            'brunette': np.array([101, 67, 33]),
        }
    
    def parse_prompt(self, prompt):
        """
        Parse prompt to extract color assignments for regions
        
        Args:
            prompt: Text like "red hair, blue background, green dress"
            
        Returns:
            dict mapping regions to RGB colors
        """
        assignments = {}
        prompt_lower = prompt.lower()
        
        # Split by common delimiters
        parts = [p.strip() for p in prompt_lower.replace(',', ';').split(';')]
        
        for part in parts:
            # Find color in this part
            color_found = None
            for color_name, rgb in self.color_map.items():
                if color_name in part:
                    color_found = rgb
                    break
            
            if color_found is None:
                continue
            
            # Find region this color applies to
            for region, keywords in self.region_keywords.items():
                if any(kw in part for kw in keywords):
                    assignments[region] = color_found
                    logging.info(f"Assigned {color_name} to {region}")
                    break
        
        return assignments
    
    def create_colored_hints(self, masks, color_assignments, hint_mode='sparse'):
        """
        Create color hint and mask based on segmentation and assignments
        
        Args:
            masks: Dict of segmentation masks
            color_assignments: Dict of region -> RGB color
            hint_mode: 'sparse' (edge-based hints), 'medium', or 'full' (fill entire region)
            
        Returns:
            Tuple of (hint_image, combined_mask)
        """
        # Get image shape from first mask
        first_mask = next(iter(masks.values()))
        height, width = first_mask.shape
        
        # Initialize hint image and combined mask
        hint_image = np.zeros((height, width, 3), dtype=np.uint8)
        combined_mask = np.zeros((height, width), dtype=np.float32)
        
        # Apply colors to regions
        for region, color in color_assignments.items():
            if region in masks:
                mask = masks[region]
                
                # Create hint mask based on mode
                if hint_mode == 'sparse':
                    # Only hint at edges/boundaries - much more subtle
                    edges = cv2.Canny((mask * 255).astype(np.uint8), 50, 150)
                    edges = cv2.dilate(edges, np.ones((3, 3), np.uint8), iterations=1)
                    hint_mask = edges / 255.0
                    
                    # Add some sparse points inside the region
                    interior = cv2.erode((mask > 0.5).astype(np.uint8), np.ones((20, 20), np.uint8))
                    hint_mask = np.maximum(hint_mask, interior * 0.3)
                    
                elif hint_mode == 'medium':
                    # Reduced opacity in interior, full at edges
                    edges = cv2.Canny((mask * 255).astype(np.uint8), 50, 150)
                    edges = cv2.dilate(edges, np.ones((5, 5), np.uint8), iterations=2)
                    edge_mask = edges / 255.0
                    interior_mask = (mask > 0.5).astype(np.float32) * 0.3
                    hint_mask = np.maximum(edge_mask, interior_mask)
                    
                else:  # 'full'
                    # Original behavior - fill entire region
                    hint_mask = mask
                
                # Apply color to hint image
                for c in range(3):
                    hint_image[:, :, c] = np.where(
                        hint_mask > 0.1,
                        color[c],
                        hint_image[:, :, c]
                    )
                
                # Update combined mask
                combined_mask = np.maximum(combined_mask, hint_mask)
        
        return hint_image, combined_mask


# Convenience function
def segment_and_color_from_prompt(image, prompt, device='cuda'):
    """
    One-shot function to segment image and assign colors from prompt
    
    Args:
        image: Input image
        prompt: Text prompt with color descriptions
        device: 'cuda' or 'cpu'
        
    Returns:
        Tuple of (hint_image, mask) ready for MangaColorizator.update_hint()
    """
    # Segment image
    segmenter = MangaSegmenter(device=device)
    masks = segmenter.segment_detailed(image)
    
    # Parse prompt and assign colors
    assigner = PromptBasedColorAssigner()
    color_assignments = assigner.parse_prompt(prompt)
    
    # Create hints
    hint_image, mask = assigner.create_colored_hints(masks, color_assignments)
    
    return hint_image, mask, masks
