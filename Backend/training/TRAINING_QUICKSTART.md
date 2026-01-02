# Quick Start: Training Your Own Colorizer Model

This is a condensed guide for quickly getting started with training. For detailed information, see [TRAINING.md](TRAINING.md).

## Prerequisites

```bash
pip install torch torchvision tqdm pillow numpy
```

GPU with 8GB+ VRAM recommended.

## 1. Prepare Your Dataset (5 minutes)

Create this structure:

```
my_training_data/
├── bw/              # Black & white manga pages
│   ├── page001.png
│   ├── page002.png
│   └── ...
└── color/           # Corresponding colored versions
    ├── page001.png
    ├── page002.png
    └── ...
```

**Important:** Filenames must match exactly between `bw/` and `color/` directories.

## 2. Train the Model (2-24 hours depending on dataset)

### Option A: Fine-tune from existing model (Recommended)

```bash
cd Backend
python train.py \
    --data_dir ../my_training_data \
    --pretrained_path networks/generator.zip \
    --epochs 50 \
    --batch_size 4 \
    --learning_rate 0.00005
```

### Option B: Train from scratch

```bash
python train.py \
    --data_dir ../my_training_data \
    --epochs 100 \
    --batch_size 4
```

**If you run out of memory:** Reduce `--batch_size 2` or `--image_size 512`

## 3. Bundle the Model (1 minute)

```bash
python bundle_model.py \
    --input training_output/generator_final.pth \
    --output networks/my_model.zip
```

## 4. Use Your Model (1 minute)

### Test it:

```bash
python inference.py \
    --input test_page.png \
    --output colored_page.png \
    --colorizer_path networks/my_model.zip
```

### Deploy it:

```bash
# Backup original
cp networks/generator.zip networks/generator_backup.zip

# Replace with your model
cp networks/my_model.zip networks/generator.zip

# Start server
python app-stream.py
```

## Common Commands

### Monitor training:

```bash
tail -f training.log
```

### Check GPU usage:

```bash
nvidia-smi -l 1
```

### Inspect model:

```bash
python bundle_model.py --inspect networks/my_model.zip
```

## Troubleshooting

| Problem           | Solution                                 |
| ----------------- | ---------------------------------------- |
| Out of memory     | Use `--batch_size 2` or `--batch_size 1` |
| Training too slow | Increase `--num_workers 8`               |
| Poor results      | Need more data or longer training        |
| File not found    | Check paths and directory structure      |

## Recommended Settings

### For Small Dataset (<500 images):

```bash
python train.py --data_dir ../data --pretrained_path networks/generator.zip \
    --epochs 30 --batch_size 2 --learning_rate 0.00002
```

### For Medium Dataset (500-5000 images):

```bash
python train.py --data_dir ../data --pretrained_path networks/generator.zip \
    --epochs 50 --batch_size 4 --learning_rate 0.00005
```

### For Large Dataset (>5000 images):

```bash
python train.py --data_dir ../data --epochs 100 \
    --batch_size 8 --use_perceptual_loss
```

## Need More Help?

See [TRAINING.md](TRAINING.md) for:

- Detailed explanations
- Advanced configuration
- Troubleshooting guide
- Best practices
- FAQ
