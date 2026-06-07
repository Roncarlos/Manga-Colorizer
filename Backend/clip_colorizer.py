"""
CLIP-Guided Colorization

This module adds text prompt support to the Manga Colorizer using CLIP (Contrastive Language-Image Pre-training).
It works as a post-processing step that refines colorization based on text descriptions.

Usage:
    from clip_colorizer import CLIPGuidedColorizator
    
    clip_colorizer = CLIPGuidedColorizator(config)
    result = clip_colorizer.colorize_with_prompt(image, "red hair, blue eyes, green shirt")
"""

import torch
import torch.nn.functional as F
import numpy as np
from PIL import Image
import logging

try:
    import clip
    CLIP_AVAILABLE = True
except ImportError:
    CLIP_AVAILABLE = False
    logging.warning("CLIP not installed. Install with: pip install git+https://github.com/openai/CLIP.git")

from colorizator import MangaColorizator


class CLIPGuidedColorizator:
    """
    Extends MangaColorizator with CLIP-guided text prompt support.
    
    This class uses CLIP to:
    1. Generate initial colorization with base model
    2. Compare result against text prompt
    3. Iteratively refine colors to match description
    """
    
    def __init__(self, config, clip_model_name="ViT-B/32"):
        """
        Initialize CLIP-guided colorizer
        
        Args:
            config: Configuration object for MangaColorizator
            clip_model_name: CLIP model variant to use
        """
        if not CLIP_AVAILABLE:
            raise ImportError(
                "CLIP is required for text-guided colorization. "
                "Install with: pip install git+https://github.com/openai/CLIP.git"
            )
        
        # Initialize base colorizer
        self.base_colorizer = MangaColorizator(config)
        self.device = self.base_colorizer.device
        
        # Load CLIP model
        logging.info(f"Loading CLIP model: {clip_model_name}")
        self.clip_model, self.clip_preprocess = clip.load(clip_model_name, device=self.device)
        self.clip_model.eval()
        
        # Color adjustment parameters
        self.refinement_steps = 3
        self.learning_rate = 0.1
        self.color_strength = 0.3
        
        logging.info("CLIP-Guided Colorizer initialized")
    
    def _preprocess_for_clip(self, image_np):
        """Convert numpy image to CLIP input format"""
        # Convert to PIL
        pil_image = Image.fromarray(image_np)
        # Apply CLIP preprocessing
        return self.clip_preprocess(pil_image).unsqueeze(0).to(self.device)
    
    def _compute_clip_similarity(self, image_np, text_prompt):
        """
        Compute CLIP similarity between image and text prompt
        
        Args:
            image_np: Image as numpy array (H, W, 3) in range [0, 255]
            text_prompt: Text description
            
        Returns:
            Similarity score (0-1, higher is better)
        """
        with torch.no_grad():
            # Prepare image
            image_input = self._preprocess_for_clip(image_np)
            
            # Prepare text
            text_tokens = clip.tokenize([text_prompt]).to(self.device)
            
            # Get features
            image_features = self.clip_model.encode_image(image_input)
            text_features = self.clip_model.encode_text(text_tokens)
            
            # Normalize features
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)
            
            # Compute similarity
            similarity = (image_features @ text_features.T).item()
            
        return similarity
    
    def _parse_color_hints_from_prompt(self, prompt):
        """
        Extract color keywords from prompt
        
        Args:
            prompt: Text prompt like "red hair, blue eyes"
            
        Returns:
            List of color keywords found
        """
        # Common color mappings
        color_map = {
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
        }
        
        prompt_lower = prompt.lower()
        found_colors = []
        
        for color_name, rgb_value in color_map.items():
            if color_name in prompt_lower:
                found_colors.append((color_name, rgb_value))
        
        return found_colors
    
    def _apply_color_bias(self, image_np, color_hints, strength=0.3):
        """
        Apply subtle color bias based on color hints
        
        Args:
            image_np: Image as numpy array (H, W, 3)
            color_hints: List of (color_name, rgb_value) tuples
            strength: How strongly to apply the bias (0-1)
            
        Returns:
            Adjusted image
        """
        if not color_hints:
            return image_np
        
        adjusted = image_np.copy().astype(np.float32)
        
        for color_name, target_rgb in color_hints:
            # Apply subtle color shift towards target colors
            # This preserves original colorization while nudging towards desired colors
            color_diff = target_rgb.astype(np.float32) - adjusted.mean(axis=(0, 1))
            adjusted += color_diff * strength
        
        # Clip to valid range
        adjusted = np.clip(adjusted, 0, 255).astype(np.uint8)
        
        return adjusted
    
    def _refine_with_clip(self, image_np, text_prompt, max_iterations=3):
        """
        Iteratively refine colorization based on CLIP feedback
        
        Args:
            image_np: Initial colorized image
            text_prompt: Target text description
            max_iterations: Maximum refinement iterations
            
        Returns:
            Refined image
        """
        best_image = image_np.copy()
        best_similarity = self._compute_clip_similarity(image_np, text_prompt)
        
        logging.info(f"Initial CLIP similarity: {best_similarity:.4f}")
        
        # Extract color hints from prompt
        color_hints = self._parse_color_hints_from_prompt(text_prompt)
        
        if color_hints:
            logging.info(f"Detected colors in prompt: {[c[0] for c in color_hints]}")
        
        for iteration in range(max_iterations):
            # Apply color adjustments based on hints
            strength = self.color_strength * (1 + iteration * 0.2)  # Gradually increase
            candidate = self._apply_color_bias(best_image, color_hints, strength)
            
            # Check if this improves CLIP similarity
            candidate_similarity = self._compute_clip_similarity(candidate, text_prompt)
            
            logging.info(f"Iteration {iteration + 1}: similarity = {candidate_similarity:.4f}")
            
            if candidate_similarity > best_similarity:
                best_similarity = candidate_similarity
                best_image = candidate
                logging.info(f"  → Improvement found! (Δ = +{candidate_similarity - best_similarity:.4f})")
            else:
                # No improvement, stop early
                logging.info("  → No improvement, stopping refinement")
                break
        
        logging.info(f"Final CLIP similarity: {best_similarity:.4f}")
        
        return best_image
    
    def colorize_with_prompt(self, image, prompt, size=576, refine=True):
        """
        Colorize image with text prompt guidance
        
        Args:
            image: Input grayscale image (PIL Image or numpy array)
            prompt: Text description (e.g., "red hair, blue eyes, green clothing")
            size: Processing size (must be divisible by 32)
            refine: Whether to apply CLIP-guided refinement
            
        Returns:
            Colorized image as numpy array (H, W, 3)
        """
        logging.info(f"Colorizing with prompt: '{prompt}'")
        
        # Convert PIL Image to numpy array if needed
        if hasattr(image, 'mode'):  # PIL Image
            image = np.array(image)
        
        # Step 1: Generate base colorization
        self.base_colorizer.set_image(image, size=size)
        base_result = self.base_colorizer.colorize()
        
        if not refine:
            return base_result
        
        # Step 2: Refine with CLIP guidance
        refined_result = self._refine_with_clip(
            base_result, 
            prompt, 
            max_iterations=self.refinement_steps
        )
        
        return refined_result
    
    def colorize_with_hints_and_prompt(self, image, hint, mask, prompt, size=576, refine=True):
        """
        Colorize with both manual hints and text prompt
        
        Args:
            image: Input grayscale image (PIL Image or numpy array)
            hint: Manual color hints (RGB)
            mask: Mask for color hints
            prompt: Text description
            size: Processing size
            refine: Whether to apply CLIP refinement
            
        Returns:
            Colorized image as numpy array
        """
        logging.info(f"Colorizing with hints and prompt: '{prompt}'")
        
        # Convert PIL Image to numpy array if needed
        if hasattr(image, 'mode'):  # PIL Image
            image = np.array(image)
        
        # Set image first to get the resized dimensions
        self.base_colorizer.set_image(image, size=size)
        
        # Get the actual dimensions after resize_pad
        target_h = self.base_colorizer.current_image.shape[2]
        target_w = self.base_colorizer.current_image.shape[3]
        
        # Resize hint and mask to match the resized image dimensions
        if hint.shape[0] != target_h or hint.shape[1] != target_w:
            import cv2
            hint_resized = cv2.resize(hint, (target_w, target_h), interpolation=cv2.INTER_LINEAR)
            mask_resized = cv2.resize(mask, (target_w, target_h), interpolation=cv2.INTER_LINEAR)
        else:
            hint_resized = hint
            mask_resized = mask
        
        # Apply resized hints
        self.base_colorizer.update_hint(hint_resized, mask_resized)
        base_result = self.base_colorizer.colorize()
        
        if not refine:
            return base_result
        
        # Refine with CLIP
        refined_result = self._refine_with_clip(
            base_result,
            prompt,
            max_iterations=self.refinement_steps
        )
        
        return refined_result
    
    def set_refinement_params(self, steps=3, learning_rate=0.1, color_strength=0.3):
        """
        Configure refinement parameters
        
        Args:
            steps: Number of refinement iterations
            learning_rate: Learning rate for adjustments
            color_strength: Strength of color bias (0-1)
        """
        self.refinement_steps = steps
        self.learning_rate = learning_rate
        self.color_strength = color_strength
        
        logging.info(f"Refinement params updated: steps={steps}, lr={learning_rate}, strength={color_strength}")


# Convenience function for quick usage
def colorize_with_text(config, image, prompt, **kwargs):
    """
    Quick function to colorize with text prompt
    
    Args:
        config: MangaColorizator config
        image: Input image
        prompt: Text description
        **kwargs: Additional arguments for colorize_with_prompt
        
    Returns:
        Colorized image
    """
    colorizer = CLIPGuidedColorizator(config)
    return colorizer.colorize_with_prompt(image, prompt, **kwargs)
