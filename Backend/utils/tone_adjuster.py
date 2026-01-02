import numpy as np
import cv2
import os
from pathlib import Path


class ToneAdjuster:
    """Applies tone adjustments to colorized images using color transfer in LAB color space."""
    
    # Reference image directory
    REFERENCE_DIR = Path(__file__).parent.parent / 'tone_references'
    
    THEMES = ['neutral', 'bright', 'dark', 'warm', 'cool', 'vibrant', 'pastel']
    
    # Cache for loaded reference images
    _reference_cache = {}
    
    @staticmethod
    def get_available_themes():
        """Returns list of available theme names."""
        return ToneAdjuster.THEMES.copy()
    
    @staticmethod
    def _load_reference_image(theme):
        """
        Load and cache reference image for a theme.
        
        Args:
            theme: str, theme name
            
        Returns:
            numpy array in LAB color space or None if not found
        """
        if theme in ToneAdjuster._reference_cache:
            return ToneAdjuster._reference_cache[theme]
        
        # Try multiple image formats
        for ext in ['.jpg', '.png', '.bmp', '.jpeg']:
            ref_path = ToneAdjuster.REFERENCE_DIR / f'{theme}{ext}'
            if ref_path.exists():
                try:
                    ref_img = cv2.imread(str(ref_path))
                    if ref_img is not None:
                        # Convert BGR to LAB
                        ref_img_lab = cv2.cvtColor(ref_img, cv2.COLOR_BGR2LAB)
                        ToneAdjuster._reference_cache[theme] = ref_img_lab
                        return ref_img_lab
                except Exception as e:
                    print(f"[-] Error loading reference image for {theme}: {e}")
        
        return None
    
    @staticmethod
    def _get_mean_and_std(image_lab):
        """
        Calculate mean and standard deviation for each channel in LAB space.
        
        Args:
            image_lab: numpy array in LAB color space
            
        Returns:
            tuple of (mean, std) as numpy arrays
        """
        mean, std = cv2.meanStdDev(image_lab)
        mean = np.hstack(mean).flatten()
        std = np.hstack(std).flatten()
        return mean, std
    
    @staticmethod
    def _color_transfer_lab(source_lab, target_mean, target_std):
        """
        Transfer color statistics from target to source in LAB space.
        
        Args:
            source_lab: source image in LAB color space (numpy array)
            target_mean: mean values of target image [L, A, B]
            target_std: std dev values of target image [L, A, B]
            
        Returns:
            numpy array in LAB color space with transferred colors
        """
        # Calculate source statistics
        source_mean, source_std = ToneAdjuster._get_mean_and_std(source_lab)
        
        # Avoid division by zero
        source_std = np.where(source_std == 0, 1.0, source_std)
        
        # Convert to float for processing
        result = source_lab.astype(np.float32)
        
        # Apply color transfer for each channel
        for channel in range(3):
            result[:, :, channel] = ((result[:, :, channel] - source_mean[channel]) * 
                                      (target_std[channel] / source_std[channel]) + 
                                      target_mean[channel])
        
        # Clip to valid LAB ranges
        # L: 0-255, A: 0-255, B: 0-255 (in OpenCV's LAB space)
        result = np.clip(result, 0, 255)
        
        return result.astype(np.uint8)
    
    @staticmethod
    def adjust_tone(image, theme='neutral'):
        """
        Apply tone adjustment to an image using color transfer from reference images.
        
        Args:
            image: numpy array (H, W, 3) in RGB format with values 0-255
            theme: str, one of 'neutral', 'bright', 'dark', 'warm', 'cool', 'vibrant', 'pastel'
            
        Returns:
            numpy array with adjusted tones in RGB format
        """
        if theme not in ToneAdjuster.THEMES:
            print(f"[-] Unknown theme '{theme}', using 'neutral'")
            theme = 'neutral'
        
        # No adjustment for neutral
        if theme == 'neutral':
            return image
        
        # Load reference image for the theme
        reference_lab = ToneAdjuster._load_reference_image(theme)
        
        if reference_lab is None:
            print(f"[-] No reference image found for theme '{theme}', skipping tone adjustment")
            return image
        
        # Calculate target statistics from reference image
        target_mean, target_std = ToneAdjuster._get_mean_and_std(reference_lab)
        
        # Convert source image from RGB to LAB
        # OpenCV uses BGR, so convert RGB -> BGR -> LAB
        image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        source_lab = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2LAB)
        
        # Apply color transfer
        result_lab = ToneAdjuster._color_transfer_lab(source_lab, target_mean, target_std)
        
        # Convert back to RGB
        result_bgr = cv2.cvtColor(result_lab, cv2.COLOR_LAB2BGR)
        result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
        
        return result_rgb
    
    @staticmethod
    def apply_reference_tone(image, reference_image):
        """
        Apply tone adjustment using a custom reference image.
        
        Args:
            image: numpy array (H, W, 3) in RGB format with values 0-255
            reference_image: numpy array (H, W, 3) in RGB format to extract color tone from
            
        Returns:
            numpy array with adjusted tones in RGB format
        """
        # Convert both images from RGB to LAB via BGR
        image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        source_lab = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2LAB)
        
        reference_bgr = cv2.cvtColor(reference_image, cv2.COLOR_RGB2BGR)
        reference_lab = cv2.cvtColor(reference_bgr, cv2.COLOR_BGR2LAB)
        
        # Calculate target statistics from reference image
        target_mean, target_std = ToneAdjuster._get_mean_and_std(reference_lab)
        
        # Apply color transfer
        result_lab = ToneAdjuster._color_transfer_lab(source_lab, target_mean, target_std)
        
        # Convert back to RGB
        result_bgr = cv2.cvtColor(result_lab, cv2.COLOR_LAB2BGR)
        result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
        
        return result_rgb
