import argparse
import logging
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def install_dependencies() -> None:
    """Ensure that jpegoptim is installed based on the operating system."""
    system = platform.system().lower()
    if system == 'linux':
        try:
            subprocess.run(['jpegoptim', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.info("jpegoptim not found. Installing...")
            subprocess.run(['sudo', 'apt-get', 'install', 'jpegoptim'], check=True)
            logger.info("jpegoptim installed successfully.")
    elif system == 'windows':
        try:
            subprocess.run(['jpegoptim', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.info("jpegoptim not found. Please install it using winget or download it from https://github.com/tjko/jpegoptim.")
            sys.exit(1)
    else:
        logger.error(f"Unsupported operating system: {system}")
        sys.exit(1)

def get_target_paths(target: str) -> list[Path]:
    """Validate and return a list of target paths."""
    target_path = Path(target).resolve(strict=False)
    if target_path.exists():
        return [target_path]
    else:
        logger.error(f"The path '{target}' does not exist or is not accessible.")
        sys.exit(1)

def optimize_jpeg(file_path: Path, lossless: bool, quality: int, strip_metadata: bool, backup: bool) -> bool:
    """Optimize a JPEG file using jpegoptim."""
    try:
        # Backup original file if needed
        if backup:
            backup_path = file_path.with_suffix('.bak')
            shutil.copy2(file_path, backup_path)
            logger.info(f"Backup created: {backup_path}")

        # Save original timestamps
        atime, mtime = file_path.stat().st_atime, file_path.stat().st_mtime

        # Build jpegoptim command
        cmd = ['jpegoptim', '--overwrite']
        if lossless:
            cmd.append('--max=100')  # Lossless (no quality loss)
        else:
            cmd.extend(['-m', str(quality)])
            if strip_metadata:
                cmd.append('--strip-all')  # Strip all metadata

        cmd.append(str(file_path))

        # Run jpegoptim command
        subprocess.run(cmd, check=True)
        logger.info(f"Optimized: {file_path}")

        # Restore timestamps
        os.utime(file_path, (atime, mtime))
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to optimize {file_path}: {e}")
        return False
    except PermissionError:
        logger.error(f"Permission denied: {file_path}")
        return False
    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
        return False

def process_directory(root_dir: Path, lossless: bool, quality: int, strip_metadata: bool, backup: bool, workers: int) -> None:
    """Process all JPEGs in a directory tree."""
    jpeg_files = list(root_dir.rglob('*.jpg')) + list(root_dir.rglob('*.jpeg'))
    with ProcessPoolExecutor(max_workers=workers) as executor:
        list(tqdm(executor.map(
            lambda file_path: optimize_jpeg(file_path, lossless, quality, strip_metadata, backup),
            jpeg_files
        ), total=len(jpeg_files), desc=f"Processing {root_dir}"))

def main() -> None:
    parser = argparse.ArgumentParser(
        prog='picoptim',
        description='A command-line tool to optimize JPEG images with options for quality, metadata handling, and backups.',
        epilog='For more information, visit https://github.com/yourusername/picoptim'
    )
    parser.add_argument('target', help="Directory path, disk (e.g., 'C:\\'), or 'computer' to process the entire system")
    parser.add_argument('--lossless', action='store_true', help="Perform lossless optimization (no quality loss)")
    parser.add_argument('--quality', type=int, default=90, choices=range(1, 101), help="Quality for lossy optimization (1-100)")
    parser.add_argument('--strip-metadata', action='store_true', help="Strip all metadata during optimization")
    parser.add_argument('--backup', action='store_true', help="Create backups of original images")
    parser.add_argument('--workers', type=int, default=4, help="Number of parallel workers for processing")
    args = parser.parse_args()

    install_dependencies()

    target_paths = [args.target] if args.target.lower() != 'computer' else get_target_paths(args.target)

    for path in target_paths:
        process_directory(
            path,
            lossless=args.lossless,
            quality=args.quality,
            strip_metadata=args.strip_metadata,
            backup=args.backup,
            workers=args.workers
        )

if __name__ == '__main__':
    main()
