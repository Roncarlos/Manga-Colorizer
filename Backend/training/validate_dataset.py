#!/usr/bin/env python3
"""
Quick test script to validate dataset before training
"""

import os
import sys
from pathlib import Path
from PIL import Image

def validate_dataset(data_dir):
    """Validate dataset structure and files"""
    
    print("=" * 80)
    print("DATASET VALIDATION")
    print("=" * 80)
    
    data_path = Path(data_dir)
    bw_dir = data_path / 'bw'
    color_dir = data_path / 'color'
    
    # Check directories exist
    if not data_path.exists():
        print(f"❌ Error: Data directory does not exist: {data_dir}")
        return False
    
    if not bw_dir.exists():
        print(f"❌ Error: BW directory does not exist: {bw_dir}")
        return False
    
    if not color_dir.exists():
        print(f"❌ Error: Color directory does not exist: {color_dir}")
        return False
    
    print(f"✓ Data directory found: {data_dir}")
    print(f"✓ BW directory found: {bw_dir}")
    print(f"✓ Color directory found: {color_dir}")
    print()
    
    # Get file lists
    bw_files = sorted([f for f in os.listdir(bw_dir) 
                       if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
    color_files = sorted([f for f in os.listdir(color_dir) 
                          if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
    
    print(f"BW images found: {len(bw_files)}")
    print(f"Color images found: {len(color_files)}")
    print()
    
    # Check counts match
    if len(bw_files) != len(color_files):
        print(f"❌ Error: Mismatch in number of images!")
        print(f"   BW: {len(bw_files)}, Color: {len(color_files)}")
        return False
    
    if len(bw_files) == 0:
        print("❌ Error: No images found!")
        return False
    
    print(f"✓ Image count matches: {len(bw_files)} pairs")
    print()
    
    # Check filenames match
    mismatches = []
    for bw, color in zip(bw_files, color_files):
        if bw != color:
            mismatches.append((bw, color))
    
    if mismatches:
        print(f"❌ Error: {len(mismatches)} filename mismatches found:")
        for bw, color in mismatches[:10]:
            print(f"   BW: {bw:40s} | Color: {color}")
        if len(mismatches) > 10:
            print(f"   ... and {len(mismatches) - 10} more")
        return False
    
    print(f"✓ All filenames match")
    print()
    
    # Sample a few images to check they can be loaded
    print("Checking sample images...")
    sample_count = min(5, len(bw_files))
    
    for i in range(sample_count):
        try:
            bw_path = bw_dir / bw_files[i]
            color_path = color_dir / color_files[i]
            
            bw_img = Image.open(bw_path)
            color_img = Image.open(color_path)
            
            print(f"  ✓ {bw_files[i]:40s} - BW: {bw_img.size}, Color: {color_img.size}")
            
        except Exception as e:
            print(f"  ❌ Error loading {bw_files[i]}: {e}")
            return False
    
    print()
    
    # Size recommendations
    if len(bw_files) < 100:
        print("⚠ Warning: Small dataset (<100 images)")
        print("  Recommendation: Fine-tune from pretrained model with low learning rate")
    elif len(bw_files) < 1000:
        print("✓ Good dataset size (100-1000 images)")
        print("  Recommendation: Fine-tune from pretrained model")
    else:
        print("✓ Large dataset (>1000 images)")
        print("  Recommendation: Can train from scratch or fine-tune")
    
    print()
    print("=" * 80)
    print("VALIDATION PASSED ✓")
    print("=" * 80)
    print()
    print("Your dataset is ready for training!")
    print()
    print("Recommended training command:")
    
    if len(bw_files) < 500:
        print(f"""
python train.py \\
    --data_dir {data_dir} \\
    --pretrained_path networks/generator.zip \\
    --epochs 30 \\
    --batch_size 2 \\
    --learning_rate 0.00002
        """)
    else:
        print(f"""
python train.py \\
    --data_dir {data_dir} \\
    --pretrained_path networks/generator.zip \\
    --epochs 50 \\
    --batch_size 4 \\
    --learning_rate 0.00005
        """)
    
    return True


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python validate_dataset.py <data_directory>")
        print()
        print("Example: python validate_dataset.py ../my_training_data")
        sys.exit(1)
    
    data_dir = sys.argv[1]
    success = validate_dataset(data_dir)
    
    sys.exit(0 if success else 1)
