# Training Cheat Sheet

Quick reference for training commands and parameters.

## Quick Commands

```bash
# Validate dataset
python validate_dataset.py ../my_data

# Train (basic)
python train.py --data_dir ../my_data --epochs 50 --batch_size 4

# Train (fine-tune)
python train.py --data_dir ../my_data --pretrained_path networks/generator.zip --epochs 50

# Bundle model
python bundle_model.py -i training_output/generator_final.pth -o networks/my_model.zip

# Inspect model
python bundle_model.py --inspect networks/my_model.zip

# Test model
python inference.py --input test.png --output result.png --colorizer_path networks/my_model.zip
```

## Common Parameters

| Parameter           | Default         | Description           |
| ------------------- | --------------- | --------------------- |
| `--data_dir`        | Required        | Path to training data |
| `--epochs`          | 100             | Training epochs       |
| `--batch_size`      | 4               | Batch size            |
| `--learning_rate`   | 0.0002          | Learning rate         |
| `--image_size`      | 576             | Image size (÷32)      |
| `--pretrained_path` | None            | Pretrained model      |
| `--output_dir`      | training_output | Save location         |
| `--device`          | cuda            | cuda or cpu           |

## Preset Configurations

### Small Dataset (<500 images)

```bash
python train.py --data_dir ../data --pretrained_path networks/generator.zip \
    --epochs 30 --batch_size 2 --learning_rate 0.00002
```

### Medium Dataset (500-5000)

```bash
python train.py --data_dir ../data --pretrained_path networks/generator.zip \
    --epochs 50 --batch_size 4 --learning_rate 0.00005
```

### Large Dataset (>5000)

```bash
python train.py --data_dir ../data --epochs 100 --batch_size 8 \
    --use_perceptual_loss --num_workers 8
```

### Low VRAM (4-6GB)

```bash
python train.py --data_dir ../data --epochs 50 --batch_size 1 \
    --image_size 448 --learning_rate 0.00005
```

### High Quality

```bash
python train.py --data_dir ../data --pretrained_path networks/generator.zip \
    --epochs 100 --image_size 768 --use_perceptual_loss \
    --perceptual_weight 0.2 --l1_weight 1.5
```

## Troubleshooting

| Issue          | Fix                                    |
| -------------- | -------------------------------------- |
| Out of memory  | `--batch_size 1` or `--image_size 512` |
| Too slow       | `--num_workers 8`                      |
| Poor results   | More data or `--epochs 100`            |
| File not found | Check `--data_dir` path                |

## File Structure

```
Backend/
├── train.py                 # Training script
├── bundle_model.py          # Model bundler
├── validate_dataset.py      # Dataset validator
├── TRAINING.md             # Full documentation
├── TRAINING_QUICKSTART.md  # Quick start
└── example_training_data/
    ├── bw/                 # BW images here
    └── color/              # Color images here
```

## Workflow

1. **Setup**: Create `data/bw/` and `data/color/` with paired images
2. **Validate**: `python validate_dataset.py ../data`
3. **Train**: `python train.py --data_dir ../data --epochs 50`
4. **Bundle**: `python bundle_model.py -i training_output/generator_final.pth -o my_model.zip`
5. **Deploy**: `cp my_model.zip networks/generator.zip`

## Monitoring

```bash
# Watch training log
tail -f training.log

# GPU usage
nvidia-smi -l 1

# Check checkpoints
ls -lh training_output/
```

## Best Practices

✅ Always validate dataset first  
✅ Start with fine-tuning  
✅ Save checkpoints frequently  
✅ Test on sample images regularly  
✅ Back up original model

❌ Don't train on misaligned pairs  
❌ Don't use batch_size > VRAM allows  
❌ Don't skip validation  
❌ Don't forget to bundle before deploying

## Resources

- 📖 Full Guide: [TRAINING.md](TRAINING.md)
- 🚀 Quick Start: [TRAINING_QUICKSTART.md](TRAINING_QUICKSTART.md)
- 📋 Implementation: [TRAINING_IMPLEMENTATION.md](TRAINING_IMPLEMENTATION.md)

---

**Need help?** Check [TRAINING.md](TRAINING.md) section 8 (Troubleshooting)
