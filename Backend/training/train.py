"""
Manga Colorizer Training Script

This script trains the manga colorization model on paired black-and-white and colored manga pages.
The model architecture is based on a U-Net style generator with ResNeXt bottlenecks.

Usage:
    python train.py --data_dir <path_to_data> --epochs 100 --batch_size 4
"""

import argparse
import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
import numpy as np
from tqdm import tqdm
import logging
from pathlib import Path

from networks.colorizer import Colorizer


class MangaColorizationDataset(Dataset):
    """Dataset for manga colorization with paired BW and color images"""
    
    def __init__(self, data_dir, image_size=576, transform=None):
        """
        Args:
            data_dir: Directory containing 'bw' and 'color' subdirectories
            image_size: Size to resize images (must be divisible by 32)
            transform: Optional transform to be applied on images
        """
        self.data_dir = Path(data_dir)
        self.bw_dir = self.data_dir / 'bw'
        self.color_dir = self.data_dir / 'color'
        self.image_size = image_size
        
        if image_size % 32 != 0:
            raise ValueError("Image size must be divisible by 32")
        
        # Get list of image files
        self.bw_images = sorted([f for f in os.listdir(self.bw_dir) 
                                 if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
        self.color_images = sorted([f for f in os.listdir(self.color_dir) 
                                    if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
        
        if len(self.bw_images) != len(self.color_images):
            raise ValueError(f"Mismatch in number of BW ({len(self.bw_images)}) and color ({len(self.color_images)}) images")
        
        # Basic transforms
        self.to_tensor = transforms.ToTensor()
        self.normalize = transforms.Normalize(mean=[0.5], std=[0.5])  # Normalize to [-1, 1]
        self.transform = transform
        
        logging.info(f"Loaded {len(self.bw_images)} image pairs from {data_dir}")
    
    def __len__(self):
        return len(self.bw_images)
    
    def _resize_and_pad(self, image, size):
        """Resize image to fit within size x size while maintaining aspect ratio, then pad"""
        w, h = image.size
        scale = min(size / w, size / h)
        new_w, new_h = int(w * scale), int(h * scale)
        
        # Resize
        image = image.resize((new_w, new_h), Image.LANCZOS)
        
        # Calculate padding
        pad_w = size - new_w
        pad_h = size - new_h
        
        # Create new image with padding
        if image.mode == 'L':
            new_image = Image.new('L', (size, size), color=255)
        else:
            new_image = Image.new('RGB', (size, size), color=(255, 255, 255))
        
        new_image.paste(image, (0, 0))
        
        return new_image, (pad_h, pad_w)
    
    def __getitem__(self, idx):
        # Load images
        bw_path = self.bw_dir / self.bw_images[idx]
        color_path = self.color_dir / self.color_images[idx]
        
        bw_img = Image.open(bw_path).convert('L')  # Grayscale
        color_img = Image.open(color_path).convert('RGB')
        
        # Resize and pad
        bw_img, pad_info = self._resize_and_pad(bw_img, self.image_size)
        color_img, _ = self._resize_and_pad(color_img, self.image_size)
        
        # Apply custom transforms if provided
        if self.transform:
            bw_img = self.transform(bw_img)
            color_img = self.transform(color_img)
        
        # Convert to tensor and normalize
        bw_tensor = self.to_tensor(bw_img)  # [1, H, W]
        color_tensor = self.to_tensor(color_img)  # [3, H, W]
        
        # Normalize to [-1, 1]
        bw_tensor = bw_tensor * 2.0 - 1.0
        color_tensor = color_tensor * 2.0 - 1.0
        
        # Create hint channel (empty for training from scratch)
        # Format: [BW_channel, Hint_R, Hint_G, Hint_B, Hint_mask]
        hint = torch.zeros(4, self.image_size, self.image_size)
        input_tensor = torch.cat([bw_tensor, hint], dim=0)  # [5, H, W]
        
        return {
            'input': input_tensor,
            'target': color_tensor,
            'bw': bw_tensor,
            'filename': self.bw_images[idx]
        }


class PerceptualLoss(nn.Module):
    """Perceptual loss using VGG features"""
    
    def __init__(self, device='cuda'):
        super(PerceptualLoss, self).__init__()
        from torchvision.models import vgg16, VGG16_Weights
        
        vgg = vgg16(weights=VGG16_Weights.IMAGENET1K_V1).features
        self.layers = nn.Sequential(*list(vgg.children())[:16]).to(device).eval()
        
        for param in self.layers.parameters():
            param.requires_grad = False
    
    def forward(self, pred, target):
        pred_features = self.layers(pred)
        target_features = self.layers(target)
        return nn.functional.mse_loss(pred_features, target_features)


def train_model(args):
    """Main training function"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(args.log_file),
            logging.StreamHandler()
        ]
    )
    
    # Set device
    device = torch.device('cuda' if torch.cuda.is_available() and args.device == 'cuda' else 'cpu')
    logging.info(f"Using device: {device}")
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Load dataset
    train_dataset = MangaColorizationDataset(
        args.data_dir,
        image_size=args.image_size
    )
    
    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=args.num_workers,
        pin_memory=True if device.type == 'cuda' else False
    )
    
    # Initialize model
    model = Colorizer().to(device)
    
    # Load pretrained weights if specified
    if args.pretrained_path and os.path.exists(args.pretrained_path):
        logging.info(f"Loading pretrained weights from {args.pretrained_path}")
        state_dict = torch.load(args.pretrained_path, map_location=device)
        model.generator.load_state_dict(state_dict)
        logging.info("Pretrained weights loaded successfully")
    
    # Setup loss functions
    l1_loss = nn.L1Loss()
    mse_loss = nn.MSELoss()
    
    if args.use_perceptual_loss:
        perceptual_loss = PerceptualLoss(device)
    
    # Setup optimizer
    optimizer = optim.Adam(
        model.parameters(),
        lr=args.learning_rate,
        betas=(0.5, 0.999)
    )
    
    # Learning rate scheduler
    scheduler = optim.lr_scheduler.StepLR(
        optimizer,
        step_size=args.lr_decay_step,
        gamma=args.lr_decay_gamma
    )
    
    # Training loop
    logging.info("Starting training...")
    global_step = 0
    
    for epoch in range(args.epochs):
        model.train()
        epoch_loss = 0.0
        
        progress_bar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{args.epochs}")
        
        for batch_idx, batch in enumerate(progress_bar):
            inputs = batch['input'].to(device)
            targets = batch['target'].to(device)
            
            # Forward pass
            optimizer.zero_grad()
            predictions, guide = model(inputs)
            
            # Calculate losses
            loss_l1 = l1_loss(predictions, targets)
            loss_mse = mse_loss(predictions, targets)
            
            # Main reconstruction loss
            loss = args.l1_weight * loss_l1 + args.mse_weight * loss_mse
            
            # Add perceptual loss if enabled
            if args.use_perceptual_loss:
                # Denormalize from [-1, 1] to [0, 1] for VGG
                pred_denorm = (predictions + 1.0) / 2.0
                target_denorm = (targets + 1.0) / 2.0
                loss_perceptual = perceptual_loss(pred_denorm, target_denorm)
                loss += args.perceptual_weight * loss_perceptual
            
            # Guide loss (auxiliary decoder output)
            if guide is not None:
                loss_guide = mse_loss(guide, targets)
                loss += args.guide_weight * loss_guide
            
            # Backward pass
            loss.backward()
            
            # Gradient clipping
            if args.grad_clip > 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), args.grad_clip)
            
            optimizer.step()
            
            epoch_loss += loss.item()
            global_step += 1
            
            # Update progress bar
            progress_bar.set_postfix({
                'loss': f'{loss.item():.4f}',
                'l1': f'{loss_l1.item():.4f}',
                'mse': f'{loss_mse.item():.4f}'
            })
            
            # Log to file periodically
            if global_step % args.log_interval == 0:
                logging.info(
                    f"Step {global_step} - "
                    f"Loss: {loss.item():.4f}, "
                    f"L1: {loss_l1.item():.4f}, "
                    f"MSE: {loss_mse.item():.4f}"
                )
        
        # Epoch summary
        avg_epoch_loss = epoch_loss / len(train_loader)
        logging.info(f"Epoch {epoch+1}/{args.epochs} - Average Loss: {avg_epoch_loss:.4f}")
        
        # Update learning rate
        scheduler.step()
        current_lr = optimizer.param_groups[0]['lr']
        logging.info(f"Learning rate: {current_lr:.6f}")
        
        # Save checkpoint
        if (epoch + 1) % args.save_interval == 0:
            checkpoint_path = os.path.join(
                args.output_dir,
                f'generator_epoch_{epoch+1}.pth'
            )
            torch.save(model.generator.state_dict(), checkpoint_path)
            logging.info(f"Checkpoint saved: {checkpoint_path}")
    
    # Save final model
    final_path = os.path.join(args.output_dir, 'generator_final.pth')
    torch.save(model.generator.state_dict(), final_path)
    logging.info(f"Training complete! Final model saved: {final_path}")


def main():
    parser = argparse.ArgumentParser(description='Train Manga Colorizer')
    
    # Data parameters
    parser.add_argument('--data_dir', type=str, required=True,
                        help='Directory containing bw/ and color/ subdirectories')
    parser.add_argument('--image_size', type=int, default=576,
                        help='Image size (must be divisible by 32)')
    
    # Training parameters
    parser.add_argument('--epochs', type=int, default=100,
                        help='Number of training epochs')
    parser.add_argument('--batch_size', type=int, default=4,
                        help='Batch size for training')
    parser.add_argument('--learning_rate', type=float, default=0.0002,
                        help='Initial learning rate')
    parser.add_argument('--lr_decay_step', type=int, default=30,
                        help='Epochs before learning rate decay')
    parser.add_argument('--lr_decay_gamma', type=float, default=0.5,
                        help='Learning rate decay factor')
    
    # Loss weights
    parser.add_argument('--l1_weight', type=float, default=1.0,
                        help='Weight for L1 loss')
    parser.add_argument('--mse_weight', type=float, default=1.0,
                        help='Weight for MSE loss')
    parser.add_argument('--use_perceptual_loss', action='store_true',
                        help='Use perceptual loss (requires more VRAM)')
    parser.add_argument('--perceptual_weight', type=float, default=0.1,
                        help='Weight for perceptual loss')
    parser.add_argument('--guide_weight', type=float, default=0.5,
                        help='Weight for guide/auxiliary decoder loss')
    
    # Optimization
    parser.add_argument('--grad_clip', type=float, default=1.0,
                        help='Gradient clipping threshold (0 to disable)')
    
    # Model parameters
    parser.add_argument('--pretrained_path', type=str, default=None,
                        help='Path to pretrained generator weights (.pth or .zip)')
    
    # System parameters
    parser.add_argument('--device', type=str, default='cuda',
                        choices=['cuda', 'cpu'], help='Device to use')
    parser.add_argument('--num_workers', type=int, default=4,
                        help='Number of data loading workers')
    
    # Output parameters
    parser.add_argument('--output_dir', type=str, default='training_output',
                        help='Directory to save checkpoints')
    parser.add_argument('--save_interval', type=int, default=10,
                        help='Save checkpoint every N epochs')
    parser.add_argument('--log_interval', type=int, default=100,
                        help='Log training stats every N steps')
    parser.add_argument('--log_file', type=str, default='training.log',
                        help='Log file path')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not os.path.exists(args.data_dir):
        raise ValueError(f"Data directory does not exist: {args.data_dir}")
    
    bw_dir = os.path.join(args.data_dir, 'bw')
    color_dir = os.path.join(args.data_dir, 'color')
    
    if not os.path.exists(bw_dir) or not os.path.exists(color_dir):
        raise ValueError(f"Data directory must contain 'bw' and 'color' subdirectories")
    
    # Start training
    train_model(args)


if __name__ == '__main__':
    main()
