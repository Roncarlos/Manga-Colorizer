# Example Training Data

This directory demonstrates the required structure for training data.

## Directory Structure

```
example_training_data/
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

## Requirements

1. **File Names Must Match**: Files in `bw/` and `color/` must have identical names
2. **Same Count**: Both directories must have the same number of files
3. **Proper Pairing**: Each BW image must correspond to its colored version
4. **Supported Formats**: PNG, JPG, JPEG

## Usage

1. Place your black-and-white manga pages in the `bw/` directory
2. Place the corresponding colored versions in the `color/` directory
3. Ensure filenames match exactly between both directories
4. Run the validation script:
   ```bash
   python validate_dataset.py example_training_data
   ```
5. Start training:
   ```bash
   python train.py --data_dir example_training_data --epochs 50 --batch_size 4
   ```

## Tips

- Use descriptive, sequential filenames (e.g., `page_001.png`, `page_002.png`)
- Keep original high-quality scans
- Ensure both BW and color images are properly aligned
- Aim for at least 100 paired images (1000+ recommended)

## Validation

Before training, validate your dataset:

```bash
python validate_dataset.py example_training_data
```

This will check:

- Directory structure
- File counts
- Filename matching
- Image loading
- Dataset size recommendations

For detailed training instructions, see [TRAINING.md](../TRAINING.md)
