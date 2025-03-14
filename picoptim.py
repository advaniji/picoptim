import argparse
import ctypes
import logging
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
import string
import psutil

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def format_size(bytes):
    """Convert bytes to human-readable format."""
    if bytes == 0:
        return "0 bytes"
    for unit in ["bytes", "KB", "MB", "GB", "TB"]:
        if bytes < 1024:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024
    return f"{bytes:.2f} TB"

def install_dependencies() -> None:
    """Ensure that jpegoptim is installed."""
    system = platform.system().lower()
    try:
        subprocess.run(['jpegoptim', '--version'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.info("jpegoptim not found. Installing...")
        if system == 'linux':
            subprocess.run(['sudo', 'apt-get', 'install', '-y', 'jpegoptim'], check=True)
        elif system == 'windows':
            logger.info("Please install jpegoptim from https://github.com/tjko/jpegoptim/releases")
            sys.exit(1)
        else:
            logger.error(f"Unsupported OS: {system}")
            sys.exit(1)

def list_drives() -> list[str]:
    """List all available drives on Windows systems."""
    if platform.system().lower() == 'windows':
        drives = []
        bitmask = ctypes.windll.kernel32.GetLogicalDrives()
        for letter in string.ascii_uppercase:
            if bitmask & 1:
                drives.append(f"{letter}:\\")
            bitmask >>= 1
        return drives
    else:
        return []

def get_target_paths(target: str) -> list[Path]:
    """Resolve target paths based on user input."""
    target = target.strip().lower()
    if target == 'computer':
        return [Path(drive) for drive in list_drives()]
    elif len(target) == 1 and target in string.ascii_letters:
        drive = f"{target.upper()}:\\"
        if os.path.exists(drive):
            return [Path(drive)]
        logger.error(f"Drive {drive} does not exist.")
        sys.exit(1)
    else:
        path = Path(target).resolve()
        if path.exists():
            return [path]
        logger.error(f"Path {target} does not exist.")
        sys.exit(1)

def collect_jpeg_files(paths: list[Path]) -> list[Path]:
    """Collect JPEG files from specified paths."""
    jpeg_files = []
    for path in paths:
        if not path.exists():
            logger.warning(f"Path {path} does not exist. Skipping...")
            continue
        for root, _, files in os.walk(path, followlinks=False):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg')):
                    jpeg_files.append(Path(root) / file)
    return jpeg_files

def optimize_worker(args: tuple) -> tuple[bool, int, int]:
    """Worker function for optimizing images."""
    file_path, lossless, quality, strip_metadata, backup = args
    original_size = file_path.stat().st_size
    try:
        if backup:
            backup_path = file_path.with_suffix(file_path.suffix + '.bak')
            shutil.copy2(file_path, backup_path)

        atime, mtime = file_path.stat().st_atime, file_path.stat().st_mtime
        cmd = ['jpegoptim', '--overwrite', '--force', '--preserve']
        
        if lossless:
            cmd.append('--max=100')
        else:
            cmd.extend(['-m', str(quality)])
        
        if strip_metadata:
            cmd.append('--strip-all')

        cmd.append(str(file_path))
        subprocess.run(cmd, check=True, capture_output=True)
        os.utime(file_path, (atime, mtime))
        return (True, original_size, file_path.stat().st_size)
    except Exception as e:
        logger.debug(f"Error processing {file_path}: {str(e)}")
        return (False, original_size, original_size)

def main() -> None:
    print("Welcome to PicOptim - Your JPEG Optimization Tool!")
    print("-----------------------------------------------")

    parser = argparse.ArgumentParser(description="Optimize JPEG images at scale")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--lossless', action='store_true', help="Perform lossless optimization")
    group.add_argument('--lossy', action='store_true', help="Perform lossy optimization")
    parser.add_argument('target', nargs='?', default=None, help="Path, drive letter (e.g., E), or 'computer' to process entire system")
    parser.add_argument('--quality', type=int, default=75, help="Quality for lossy optimization (1-100, higher means better quality)")
    parser.add_argument('--strip-metadata', action='store_true', help="Remove metadata")
    parser.add_argument('--backup', action='store_true', help="Create backup files")
    parser.add_argument('--workers', type=int, default=None, help="Number of parallel workers")
    args = parser.parse_args()

    # Prompt for missing arguments
    if args.target is None:
        args.target = input("Enter the target path, drive letter (e.g., E), or 'computer' to process the entire system: ").strip()
    
    if not args.lossless and not args.lossy:
        print("Select optimization mode:")
        print("1. Lossy optimization (reduce quality)")
        print("2. Lossless optimization (no quality reduction)")
        mode = input("Enter your choice (1 or 2): ").strip()
        if mode == '1':
            args.lossy = True
        elif mode == '2':
            args.lossless = True
        else:
            logger.error("Invalid choice. Exiting.")
            sys.exit(1)
    
    if args.lossy and (args.quality < 1 or args.quality > 100):
        logger.error("Quality must be between 1 and 100. Exiting.")
        sys.exit(1)

    if args.workers is None:
        default_workers = os.cpu_count() * 2
        try:
            args.workers = int(input(f"Enter number of parallel workers (default {default_workers}): ") or default_workers)
        except ValueError:
            args.workers = default_workers

    install_dependencies()
    target_paths = get_target_paths(args.target)
    
    if not target_paths:
        logger.error("No valid targets found. Please provide a valid path, drive letter, or 'computer'.")
        parser.print_help()
        sys.exit(1)

    logger.info("Scanning for JPEG files...")
    jpeg_files = collect_jpeg_files(target_paths)
    
    if not jpeg_files:
        logger.info("No JPEG files found")
        return

    logger.info(f"Found {len(jpeg_files)} images to optimize")
    total_original = 0
    total_optimized = 0

    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        tasks = [(f, args.lossless, args.quality, args.strip_metadata, args.backup) for f in jpeg_files]
        futures = [executor.submit(optimize_worker, task) for task in tasks]
        
        for future in tqdm(as_completed(futures), total=len(futures), desc="Optimizing"):
            success, orig, opt = future.result()
            total_original += orig
            total_optimized += opt

    saved_bytes = total_original - total_optimized
    logger.info(f"Optimization complete!")
    logger.info(f"Total original size: {format_size(total_original)}")
    logger.info(f"Total optimized size: {format_size(total_optimized)}")
    logger.info(f"Approximate space saved: {format_size(saved_bytes)}")

if __name__ == "__main__":
    main()
