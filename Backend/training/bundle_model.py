"""
Model Bundling Script

This script packages a trained PyTorch model (.pth) into the generator.zip format
used by the Manga Colorizer application.

Usage:
    python bundle_model.py --input generator_final.pth --output generator.zip
"""

import argparse
import torch
import zipfile
import os
import shutil
from pathlib import Path
import tempfile
import logging


def check_compatibility(state_dict):
    """
    Check if a state_dict is compatible with the Manga Colorizer Generator architecture
    
    Args:
        state_dict: PyTorch state dict to check
        
    Returns:
        tuple: (is_compatible, message)
    """
    # Expected key patterns for the Generator model
    required_keys = [
        'encoder.conv1.weight',
        'encoder.bn1.weight',
        'to0.0.weight',
        'to1.0.weight',
        'tunnel4.0.weight',
        'exit.0.weight'
    ]
    
    # Check if it's a state_dict or a wrapped model
    if isinstance(state_dict, dict):
        keys = list(state_dict.keys())
    else:
        return False, "Model is not a state_dict. It might be a full model object."
    
    if len(keys) == 0:
        return False, "State dict is empty."
    
    # Check for required keys
    missing_keys = []
    for req_key in required_keys:
        if not any(req_key in key for key in keys):
            missing_keys.append(req_key)
    
    if missing_keys:
        first_keys = ', '.join(keys[:5])
        return False, f"""
Model is NOT compatible with Manga Colorizer Generator!

Missing required keys: {', '.join(missing_keys[:3])}{'...' if len(missing_keys) > 3 else ''}

This model appears to be from a different architecture.
Your model's keys start with: {first_keys}...

The Manga Colorizer expects a Generator model trained with the provided train.py script.
Common issues:
  - This is a Discriminator model (e.g., 'latest_net_D_A.pth')
  - This is from a different GAN architecture (CycleGAN, Pix2Pix, etc.)
  - This model wasn't trained with the Manga Colorizer training script

Please ensure you're using:
  1. A model trained with Backend/train.py
  2. The Generator weights (not Discriminator)
  3. A model based on the Colorizer architecture in networks/colorizer.py
"""
    
    # Additional validation - check parameter count is reasonable
    total_params = sum(p.numel() for p in state_dict.values() if isinstance(p, torch.Tensor))
    expected_params_range = (20_000_000, 35_000_000)  # Generator has ~26M params
    
    if not (expected_params_range[0] <= total_params <= expected_params_range[1]):
        return False, f"""
Model parameter count ({total_params:,}) is outside expected range.
Expected: {expected_params_range[0]:,} to {expected_params_range[1]:,} parameters.

This suggests the model architecture is different from the Manga Colorizer Generator.
"""
    
    return True, f"✓ Model is compatible! ({total_params:,} parameters)"


def bundle_model(input_path, output_path, verify=True, check_compat=True):
    """
    Bundle a PyTorch state dict into a .zip format compatible with torch.load()
    
    Args:
        input_path: Path to the .pth file containing the model state dict
        output_path: Path where the generator.zip will be saved
        verify: Whether to verify the bundled model can be loaded
    """
    
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
    
    # Validate input
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    if not input_path.endswith('.pth'):
        logging.warning(f"Input file doesn't have .pth extension: {input_path}")
    
    # Load the model to verify it's valid
    logging.info(f"Loading model from {input_path}...")
    try:
        state_dict = torch.load(input_path, map_location='cpu')
        logging.info(f"Model loaded successfully. Contains {len(state_dict)} keys.")
    except Exception as e:
        raise ValueError(f"Failed to load model: {e}")
    
    # Check compatibility with Manga Colorizer Generator
    if check_compat:
        logging.info("Checking model compatibility...")
        is_compatible, message = check_compatibility(state_dict)
        
        if not is_compatible:
            logging.error("Model compatibility check FAILED!")
            print("\n" + "="*80)
            print(message)
            print("="*80 + "\n")
            raise ValueError("Model is not compatible with Manga Colorizer Generator architecture.")
        else:
            logging.info(message)
    
    # Create temporary directory for intermediate files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_model_path = os.path.join(temp_dir, 'model.pth')
        
        # Save the state dict as a .pth file
        logging.info("Saving model to temporary location...")
        torch.save(state_dict, temp_model_path)
        
        # Create the zip file
        logging.info(f"Creating zip archive at {output_path}...")
        
        # Remove existing output file if it exists
        if os.path.exists(output_path):
            logging.warning(f"Output file already exists. Overwriting: {output_path}")
            os.remove(output_path)
        
        # Create parent directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Simply rename the .pth to .zip (PyTorch saves in a zip-compatible format)
        shutil.copy(temp_model_path, output_path)
        
        logging.info(f"Model bundled successfully: {output_path}")
        
        # Verify the bundled model
        if verify:
            logging.info("Verifying bundled model...")
            try:
                verification_dict = torch.load(output_path, map_location='cpu')
                
                # Check if the loaded dict matches the original
                if len(verification_dict) != len(state_dict):
                    raise ValueError("Parameter count mismatch after bundling")
                
                # Check a few parameter values
                original_keys = list(state_dict.keys())[:5]
                for key in original_keys:
                    if not torch.allclose(state_dict[key], verification_dict[key]):
                        raise ValueError(f"Parameter mismatch for key: {key}")
                
                logging.info("✓ Verification successful! Bundled model is valid.")
                
                # Print some stats
                total_params = sum(p.numel() for p in state_dict.values())
                file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
                logging.info(f"  Total parameters: {total_params:,}")
                logging.info(f"  File size: {file_size_mb:.2f} MB")
                
            except Exception as e:
                raise ValueError(f"Verification failed: {e}")
    
    return output_path


def extract_model(zip_path, output_path):
    """
    Extract a generator.zip back to a .pth file
    
    Args:
        zip_path: Path to the generator.zip file
        output_path: Path where the .pth file will be saved
    """
    
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
    
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"Zip file not found: {zip_path}")
    
    logging.info(f"Extracting model from {zip_path}...")
    
    try:
        # Load the model from zip
        state_dict = torch.load(zip_path, map_location='cpu')
        
        # Save as .pth
        torch.save(state_dict, output_path)
        
        logging.info(f"Model extracted successfully: {output_path}")
        logging.info(f"  Parameters: {len(state_dict)}")
        
    except Exception as e:
        raise ValueError(f"Failed to extract model: {e}")


def inspect_model(model_path):
    """
    Inspect a model file and print detailed information
    
    Args:
        model_path: Path to the model file (.pth or .zip)
    """
    
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")
    
    logging.info(f"Inspecting model: {model_path}")
    logging.info(f"File size: {os.path.getsize(model_path) / (1024**2):.2f} MB")
    
    try:
        state_dict = torch.load(model_path, map_location='cpu')
        
        print("\n" + "="*80)
        print("MODEL INFORMATION")
        print("="*80)
        
        print(f"\nTotal parameters: {len(state_dict)}")
        
        # Calculate total parameter count
        total_params = sum(p.numel() for p in state_dict.values() if isinstance(p, torch.Tensor))
        print(f"Total parameter count: {total_params:,}")
        print(f"Total parameter size: {total_params * 4 / (1024**2):.2f} MB (assuming float32)")
        
        # Show parameter shapes
        print("\nParameter shapes (first 20):")
        print("-" * 80)
        for i, (name, param) in enumerate(list(state_dict.items())[:20]):
            if isinstance(param, torch.Tensor):
                print(f"  {name:60s} {str(list(param.shape)):20s} {param.dtype}")
        
        if len(state_dict) > 20:
            print(f"  ... and {len(state_dict) - 20} more parameters")
        
        print("="*80 + "\n")
        
    except Exception as e:
        logging.error(f"Failed to inspect model: {e}")
        raise


def main():
    parser = argparse.ArgumentParser(
        description='Bundle or extract Manga Colorizer models',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Bundle a trained model
  python bundle_model.py --input generator_final.pth --output generator.zip
  
  # Extract a bundled model
  python bundle_model.py --extract generator.zip --output extracted_model.pth
  
  # Inspect a model file
  python bundle_model.py --inspect generator.zip
        """
    )
    
    parser.add_argument('--input', '-i', type=str,
                        help='Input .pth file to bundle')
    parser.add_argument('--output', '-o', type=str,
                        help='Output .zip file path')
    parser.add_argument('--extract', '-e', type=str,
                        help='Extract a .zip file to .pth format')
    parser.add_argument('--inspect', '-s', type=str,
                        help='Inspect a model file and show details')
    parser.add_argument('--no-verify', action='store_true',
                        help='Skip verification after bundling')
    parser.add_argument('--no-compat-check', action='store_true',
                        help='Skip compatibility check (not recommended)')
    parser.add_argument('--test-compat', '-t', type=str,
                        help='Test model compatibility without bundling')
    
    args = parser.parse_args()
    
    # Determine action
    if args.test_compat:
        # Test compatibility mode
        logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
        logging.info(f"Testing compatibility of: {args.test_compat}")
        try:
            state_dict = torch.load(args.test_compat, map_location='cpu')
            is_compatible, message = check_compatibility(state_dict)
            
            print("\n" + "="*80)
            print("COMPATIBILITY TEST RESULT")
            print("="*80)
            print(message)
            print("="*80 + "\n")
            
            if not is_compatible:
                exit(1)
        except Exception as e:
            logging.error(f"Failed to test compatibility: {e}")
            exit(1)
    
    elif args.inspect:
        # Inspect mode
        inspect_model(args.inspect)
    
    elif args.extract:
        # Extract mode
        if not args.output:
            parser.error("--output is required when using --extract")
        extract_model(args.extract, args.output)
    
    elif args.input and args.output:
        # Bundle mode
        bundle_model(args.input, args.output, 
                    verify=not args.no_verify,
                    check_compat=not args.no_compat_check)
    
    else:
        parser.error("Must specify either:\n"
                     "  --input and --output (to bundle)\n"
                     "  --extract and --output (to extract)\n"
                     "  --inspect (to inspect)\n"
                     "  --test-compat (to test compatibility)")


if __name__ == '__main__':
    main()
