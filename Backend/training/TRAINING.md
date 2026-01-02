# Manga Colorizer Training Guide

This comprehensive guide explains how to train the Manga Colorizer model on your own dataset of black-and-white and colored manga page pairs, and how to bundle the trained model for deployment.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Dataset Preparation](#dataset-preparation)
4. [Training the Model](#training-the-model)
5. [Bundling the Model](#bundling-the-model)
6. [Using Your Trained Model](#using-your-trained-model)
7. [Advanced Configuration](#advanced-configuration)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The Manga Colorizer uses a deep learning model based on a U-Net architecture with ResNeXt bottlenecks to automatically colorize black-and-white manga images. The model learns to map grayscale images to RGB color images through supervised learning on paired examples.

### Model Architecture

- **Generator**: U-Net style encoder-decoder with skip connections
- **Encoder**: SEResNeXt backbone (pretrained on ImageNet-style features)
- **Decoder**: Progressive upsampling with ResNeXt bottlenecks
- **Input**: 5-channel (BW image + 4-channel hint/mask)
- **Output**: RGB color image

### Training Process

The model is trained using:

- **L1 Loss**: Pixel-wise color accuracy
- **MSE Loss**: Color distribution matching
- **Perceptual Loss** (optional): High-level feature matching using VGG
- **Guide Loss**: Auxiliary decoder for better feature learning

---

## Prerequisites

### Hardware Requirements

**Minimum:**

- GPU: NVIDIA GPU with 8GB VRAM (e.g., RTX 2070, GTX 1080)
- RAM: 16GB system RAM
- Storage: 50GB free space (for dataset and checkpoints)

**Recommended:**

- GPU: NVIDIA GPU with 12GB+ VRAM (e.g., RTX 3080, RTX 4090)
- RAM: 32GB system RAM
- Storage: 100GB+ SSD

### Software Requirements

```bash
# Python 3.8 or higher
python --version

# Required packages
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install -r requirements.txt
pip install tqdm pillow numpy
```

### Verify GPU Setup

```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA device: {torch.cuda.get_device_name(0)}")
```

---

## Dataset Preparation

### 1. Dataset Structure

Organize your dataset with this structure:

```
training_data/
├── bw/              # Black and white manga pages
│   ├── page_001.png
│   ├── page_002.png
│   ├── page_003.png
│   └── ...
└── color/           # Corresponding colored versions
    ├── page_001.png
    ├── page_002.png
    ├── page_003.png
    └── ...
```

**Important:**

- File names in `bw/` and `color/` must match exactly (sorted alphabetically)
- Both directories must have the same number of images
- Images should be in the same order (paired correctly)

### 2. Image Requirements

- **Format**: PNG, JPG, or JPEG
- **Resolution**: Any resolution (will be resized during training)
- **Recommended**: 1000-3000 pixels on the longest side
- **Color mode**:
  - BW images: Grayscale or RGB (will be converted)
  - Color images: RGB

### 3. Data Quality Guidelines

**Good Training Data:**

- Clean, high-quality scans
- Consistent style between BW and color versions
- Properly aligned (same cropping/framing)
- Good variety in:
  - Scene types (indoor, outdoor, action, dialogue)
  - Character counts
  - Lighting conditions
  - Detail levels

**Avoid:**

- Blurry or low-quality images
- Misaligned pairs
- Heavily compressed JPEGs
- Images with watermarks or artifacts

### 4. Dataset Size

- **Minimum**: 100 paired images (for fine-tuning)
- **Recommended**: 1,000+ paired images (for general training)
- **Optimal**: 10,000+ paired images (for best results)

### 5. Data Augmentation

The training script automatically handles:

- Resizing and padding
- Normalization
- Random crops (if implemented)

You can add more augmentation in the dataset class if needed.

### 6. Dataset Validation

Before training, validate your dataset:

```bash
# Check dataset structure
python -c "
import os
from pathlib import Path

data_dir = 'training_data'
bw_dir = Path(data_dir) / 'bw'
color_dir = Path(data_dir) / 'color'

bw_files = sorted(os.listdir(bw_dir))
color_files = sorted(os.listdir(color_dir))

print(f'BW images: {len(bw_files)}')
print(f'Color images: {len(color_files)}')
print(f'Match: {bw_files == color_files}')

if bw_files != color_files:
    print('Mismatched files:')
    for b, c in zip(bw_files[:10], color_files[:10]):
        if b != c:
            print(f'  BW: {b} | Color: {c}')
"
```

---

## Training the Model

### Basic Training Command

```bash
cd Backend
python train.py --data_dir path/to/training_data --epochs 100 --batch_size 4
```

### Training from Scratch

```bash
python train.py \
    --data_dir ../training_data \
    --epochs 100 \
    --batch_size 4 \
    --learning_rate 0.0002 \
    --image_size 576 \
    --output_dir ./training_output \
    --device cuda
```

### Fine-tuning from Pretrained Model

```bash
python train.py \
    --data_dir ../training_data \
    --pretrained_path networks/generator.zip \
    --epochs 50 \
    --batch_size 4 \
    --learning_rate 0.00005 \
    --output_dir ./finetuned_output \
    --device cuda
```

### Training Parameters

#### Data Parameters

| Parameter      | Default  | Description                                   |
| -------------- | -------- | --------------------------------------------- |
| `--data_dir`   | Required | Path to training data directory               |
| `--image_size` | 576      | Training image size (must be divisible by 32) |

#### Training Parameters

| Parameter          | Default | Description                          |
| ------------------ | ------- | ------------------------------------ |
| `--epochs`         | 100     | Number of training epochs            |
| `--batch_size`     | 4       | Batch size (reduce if out of memory) |
| `--learning_rate`  | 0.0002  | Initial learning rate                |
| `--lr_decay_step`  | 30      | Epochs before LR decay               |
| `--lr_decay_gamma` | 0.5     | LR decay factor                      |

#### Loss Weights

| Parameter               | Default | Description                   |
| ----------------------- | ------- | ----------------------------- |
| `--l1_weight`           | 1.0     | L1 loss weight                |
| `--mse_weight`          | 1.0     | MSE loss weight               |
| `--use_perceptual_loss` | False   | Enable perceptual loss        |
| `--perceptual_weight`   | 0.1     | Perceptual loss weight        |
| `--guide_weight`        | 0.5     | Auxiliary decoder loss weight |

#### System Parameters

| Parameter         | Default         | Description             |
| ----------------- | --------------- | ----------------------- |
| `--device`        | cuda            | Device: 'cuda' or 'cpu' |
| `--num_workers`   | 4               | Data loader workers     |
| `--output_dir`    | training_output | Checkpoint directory    |
| `--save_interval` | 10              | Save every N epochs     |

### Training Tips

**For Small Datasets (<500 images):**

```bash
python train.py \
    --data_dir ../training_data \
    --pretrained_path networks/generator.zip \
    --epochs 30 \
    --batch_size 2 \
    --learning_rate 0.00002 \
    --l1_weight 2.0
```

**For Large Datasets (>5000 images):**

```bash
python train.py \
    --data_dir ../training_data \
    --epochs 200 \
    --batch_size 8 \
    --learning_rate 0.0002 \
    --use_perceptual_loss \
    --num_workers 8
```

**For High-Quality Results:**

```bash
python train.py \
    --data_dir ../training_data \
    --pretrained_path networks/generator.zip \
    --epochs 100 \
    --batch_size 4 \
    --image_size 768 \
    --use_perceptual_loss \
    --perceptual_weight 0.2 \
    --l1_weight 1.5
```

### Monitoring Training

The training script outputs:

- Real-time loss values in the progress bar
- Detailed logs to `training.log`
- Checkpoints every N epochs in `output_dir/`

**Monitor training:**

```bash
# Watch log file
tail -f training.log

# Check GPU usage
nvidia-smi -l 1
```

### Training Time Estimates

| Dataset Size  | GPU      | Batch Size | Time per Epoch | Total Time (100 epochs) |
| ------------- | -------- | ---------- | -------------- | ----------------------- |
| 100 images    | RTX 3080 | 4          | ~30 seconds    | ~50 minutes             |
| 1,000 images  | RTX 3080 | 4          | ~5 minutes     | ~8 hours                |
| 5,000 images  | RTX 3080 | 4          | ~25 minutes    | ~42 hours               |
| 10,000 images | RTX 4090 | 8          | ~20 minutes    | ~33 hours               |

---

## Bundling the Model

After training, you need to bundle the model into the `generator.zip` format for use with the application.

### Basic Bundling

```bash
cd Backend
python bundle_model.py \
    --input training_output/generator_final.pth \
    --output networks/generator_custom.zip
```

### Bundle Specific Checkpoint

```bash
python bundle_model.py \
    --input training_output/generator_epoch_50.pth \
    --output networks/generator_epoch50.zip
```

### Inspect a Model

```bash
python bundle_model.py --inspect networks/generator.zip
```

Output example:

```
================================================================================
MODEL INFORMATION
================================================================================

Total parameters: 645
Total parameter count: 26,543,891
Total parameter size: 101.23 MB (assuming float32)

Parameter shapes (first 20):
  encoder.conv1.weight                                          [64, 1, 7, 7]           torch.float32
  encoder.bn1.weight                                            [64]                    torch.float32
  ...
================================================================================
```

### Extract Model from Zip

If you need to convert a `.zip` back to `.pth`:

```bash
python bundle_model.py \
    --extract networks/generator.zip \
    --output extracted_model.pth
```

### Bundling Options

| Option             | Description                      |
| ------------------ | -------------------------------- |
| `--input` / `-i`   | Input .pth file to bundle        |
| `--output` / `-o`  | Output .zip file path            |
| `--extract` / `-e` | Extract .zip to .pth             |
| `--inspect` / `-s` | Inspect model details            |
| `--no-verify`      | Skip verification after bundling |

---

## Using Your Trained Model

### 1. Replace Default Model

```bash
# Backup original model
mv Backend/networks/generator.zip Backend/networks/generator_original.zip

# Use your trained model
cp Backend/networks/generator_custom.zip Backend/networks/generator.zip
```

### 2. Test the Model

```bash
cd Backend
python inference.py \
    --input_image path/to/test_manga.png \
    --output_image path/to/output.png \
    --colorizer_path networks/generator_custom.zip
```

### 3. Use with Server

```bash
cd Backend
python app-stream.py
# Server will automatically use networks/generator.zip
```

### 4. Compare Models

```bash
# Test original model
python inference.py --input test.png --output test_original.png \
    --colorizer_path networks/generator_original.zip

# Test your model
python inference.py --input test.png --output test_custom.png \
    --colorizer_path networks/generator_custom.zip
```

---

## Advanced Configuration

### Custom Loss Functions

Edit `train.py` to add custom losses:

```python
# Add custom loss
class StyleLoss(nn.Module):
    def __init__(self):
        super(StyleLoss, self).__init__()
        # Your implementation

    def forward(self, pred, target):
        # Calculate loss
        return loss

# In train_model():
style_loss = StyleLoss()
loss += args.style_weight * style_loss(predictions, targets)
```

### Data Augmentation

Add augmentation to the dataset:

```python
class MangaColorizationDataset(Dataset):
    def __init__(self, data_dir, image_size=576, augment=True):
        self.augment = augment

        if augment:
            self.augmentation = transforms.Compose([
                transforms.RandomHorizontalFlip(p=0.5),
                transforms.RandomRotation(5),
                transforms.ColorJitter(brightness=0.1, contrast=0.1),
            ])

    def __getitem__(self, idx):
        # ... load images ...

        if self.augment:
            # Apply same augmentation to both images
            seed = torch.random.seed()
            torch.manual_seed(seed)
            bw_img = self.augmentation(bw_img)
            torch.manual_seed(seed)
            color_img = self.augmentation(color_img)
```

### Multi-GPU Training

For multiple GPUs:

```python
# In train.py, after model initialization:
if torch.cuda.device_count() > 1:
    print(f"Using {torch.cuda.device_count()} GPUs")
    model = nn.DataParallel(model)
```

### Resume Training

```python
# Save checkpoint with optimizer state
checkpoint = {
    'epoch': epoch,
    'model_state_dict': model.state_dict(),
    'optimizer_state_dict': optimizer.state_dict(),
    'loss': loss,
}
torch.save(checkpoint, 'checkpoint.pth')

# Resume training
checkpoint = torch.load('checkpoint.pth')
model.load_state_dict(checkpoint['model_state_dict'])
optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
start_epoch = checkpoint['epoch'] + 1
```

---

## Troubleshooting

### Out of Memory (OOM)

**Solutions:**

1. Reduce batch size: `--batch_size 2` or `--batch_size 1`
2. Reduce image size: `--image_size 512` or `--image_size 448`
3. Disable perceptual loss: Remove `--use_perceptual_loss`
4. Use gradient accumulation (modify train.py)

### Poor Colorization Quality

**Possible Causes:**

1. **Insufficient training data**: Need more varied examples
2. **Overfitting**: Reduce epochs or add augmentation
3. **Wrong learning rate**: Try `--learning_rate 0.0001` or `0.00005`
4. **Loss weight imbalance**: Adjust `--l1_weight` and `--mse_weight`

**Solutions:**

- Fine-tune from pretrained model
- Add more training data
- Adjust loss weights
- Train longer with lower learning rate

### Training is Too Slow

**Solutions:**

1. Increase `--num_workers` (e.g., `--num_workers 8`)
2. Use smaller `--image_size`
3. Use SSD for dataset storage
4. Enable mixed precision training (modify train.py)

### Model Not Improving

**Check:**

1. Learning rate not too low/high
2. Loss weights balanced
3. Dataset quality and variety
4. Proper data normalization

**Try:**

```bash
# Reset with different hyperparameters
python train.py \
    --data_dir ../training_data \
    --pretrained_path networks/generator.zip \
    --epochs 50 \
    --learning_rate 0.0001 \
    --l1_weight 2.0 \
    --mse_weight 0.5
```

### File Not Found Errors

**Check:**

- Paths are correct and use forward slashes or escaped backslashes
- You're in the Backend directory when running scripts
- Dataset structure matches exactly: `data_dir/bw/` and `data_dir/color/`

### CUDA Errors

```bash
# Clear CUDA cache
python -c "import torch; torch.cuda.empty_cache()"

# Check CUDA version
python -c "import torch; print(torch.version.cuda)"

# Reinstall PyTorch if needed
pip uninstall torch torchvision
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

---

## Best Practices

### 1. Start with Pretrained Model

Always fine-tune from the existing model rather than training from scratch:

```bash
--pretrained_path networks/generator.zip
```

### 2. Use Validation Set

Split your data 80/20 for training and validation to monitor overfitting.

### 3. Save Regularly

Use `--save_interval 5` to save checkpoints frequently.

### 4. Monitor Loss Curves

Track training loss over time. Should decrease smoothly.

### 5. Test Incrementally

Test the model every 10 epochs on sample images to see improvement.

### 6. Backup Everything

- Keep original model: `generator_original.zip`
- Keep training checkpoints
- Keep training logs

---

## Example Workflow

Complete workflow from data to deployment:

```bash
# 1. Prepare dataset
mkdir -p training_data/bw training_data/color
# Copy your BW images to training_data/bw/
# Copy colored images to training_data/color/

# 2. Validate dataset
ls -1 training_data/bw/ | wc -l
ls -1 training_data/color/ | wc -l
# Should show same count

# 3. Start training
cd Backend
python train.py \
    --data_dir ../training_data \
    --pretrained_path networks/generator.zip \
    --epochs 50 \
    --batch_size 4 \
    --learning_rate 0.00005 \
    --use_perceptual_loss \
    --output_dir ./my_training

# 4. Monitor progress
tail -f training.log

# 5. Bundle best model
python bundle_model.py \
    --input my_training/generator_epoch_40.pth \
    --output networks/generator_custom.zip

# 6. Test model
python inference.py \
    --input ../test_manga.png \
    --output ../test_result.png \
    --colorizer_path networks/generator_custom.zip

# 7. Deploy (replace default model)
cp networks/generator.zip networks/generator_backup.zip
cp networks/generator_custom.zip networks/generator.zip

# 8. Start server
python app-stream.py
```

---

## Additional Resources

- **Original Paper**: [Manga Colorization Research](https://github.com/qweasdd/manga-colorization-v2)
- **Model Architecture**: See `Backend/networks/colorizer.py`
- **PyTorch Documentation**: https://pytorch.org/docs/stable/
- **Issues & Support**: GitHub Issues

---

## FAQ

**Q: How many images do I need?**
A: Minimum 100 for fine-tuning, 1000+ for good results, 10000+ for best quality.

**Q: Can I use CPU for training?**
A: Yes with `--device cpu`, but it will be 10-50x slower. Not recommended.

**Q: How do I know when to stop training?**
A: Monitor the loss. When it plateaus and validation quality stops improving, stop training.

**Q: Can I train on multiple styles?**
A: Yes, but mix them in the training data. Model will learn to handle variety.

**Q: How to reduce model size?**
A: Model architecture is fixed. You can't reduce size without modifying the architecture.

**Q: What if BW and color images don't match perfectly?**
A: Model is robust to minor differences, but major misalignment will hurt quality.

---

## Credits

- Training script based on PyTorch best practices
- Model architecture from [qweasdd/manga-colorization-v2](https://github.com/qweasdd/manga-colorization-v2)
- Created for Manga-Colorizer project

---

**Happy Training! 🎨**
