# Training Tools

This directory contains all tools and documentation for training custom Manga Colorizer models.

## Files

### Scripts

- **[train.py](train.py)** - Main training script for the colorization model
- **[bundle_model.py](bundle_model.py)** - Package trained models into generator.zip format
- **[validate_dataset.py](validate_dataset.py)** - Validate dataset before training

### Documentation

- **[TRAINING.md](TRAINING.md)** - Comprehensive training guide with all details
- **[TRAINING_QUICKSTART.md](TRAINING_QUICKSTART.md)** - Quick start guide (5 minutes)
- **[TRAINING_CHEATSHEET.md](TRAINING_CHEATSHEET.md)** - Command reference sheet
- **[TRAINING_IMPLEMENTATION.md](TRAINING_IMPLEMENTATION.md)** - Technical implementation details

### Examples

- **[example_training_data/](example_training_data/)** - Example dataset structure template

## Quick Start

```bash
# 1. Navigate to training directory
cd Backend/training

# 2. Validate your dataset
python validate_dataset.py ../../my_training_data

# 3. Train the model
python train.py \
    --data_dir ../../my_training_data \
    --pretrained_path ../networks/generator.zip \
    --epochs 50 \
    --batch_size 4

# 4. Bundle the trained model
python bundle_model.py \
    --input training_output/generator_final.pth \
    --output ../networks/my_model.zip

# 5. Test compatibility (optional)
python bundle_model.py --test-compat ../networks/my_model.zip
```

## Documentation Order

Start here based on your needs:

1. **New to training?** → Read [TRAINING_QUICKSTART.md](TRAINING_QUICKSTART.md)
2. **Need details?** → Read [TRAINING.md](TRAINING.md)
3. **Quick reference?** → Use [TRAINING_CHEATSHEET.md](TRAINING_CHEATSHEET.md)
4. **Technical info?** → See [TRAINING_IMPLEMENTATION.md](TRAINING_IMPLEMENTATION.md)

## Common Commands

```bash
# Validate dataset
python validate_dataset.py ../../data

# Train (fine-tune)
python train.py --data_dir ../../data --pretrained_path ../networks/generator.zip --epochs 50

# Bundle model
python bundle_model.py -i training_output/generator_final.pth -o ../networks/my_model.zip

# Test compatibility
python bundle_model.py --test-compat model.pth

# Inspect model
python bundle_model.py --inspect ../networks/generator.zip
```

## Dataset Structure

Your training data should be organized like this:

```
my_training_data/
├── bw/              # Black and white manga pages
│   ├── page_001.png
│   ├── page_002.png
│   └── ...
└── color/           # Corresponding colored versions
    ├── page_001.png
    ├── page_002.png
    └── ...
```

See [example_training_data/](example_training_data/) for a template.

## Requirements

- Python 3.8+
- PyTorch with CUDA support
- NVIDIA GPU with 8GB+ VRAM (recommended)
- 100+ paired BW/color manga images (1000+ recommended)

## Support

For issues or questions:
- Check [TRAINING.md](TRAINING.md) troubleshooting section
- Run `python validate_dataset.py` to check your data
- Review `training.log` for error details
- Open a GitHub issue

## Quick Links

- [Main Project README](../../README.md)
- [Backend Documentation](../README.md)
- [Docker Guide](../DOCKER.md)
