import sys
sys.path.append("/home/userroot/GitClone/python-ffmpeg")
sys.path.append("/home/userroot/GitClone/own_function")
from own_function import target_file_path, target_file_path_with_level

from downsampling import downsample_video
from multi_process_videos import multi_process_videos
from multiprocessing import cpu_count
from typing import List, Tuple
from pathlib import Path
import argparse

def find_videos(directory: Path, extensions: List[str] = None) -> List[Path]:
    """Find video files in a directory with given extensions"""
    if extensions is None:
        extensions = ['.mp4', '.mov', '.mkv', '.avi', '.flv', '.m4v']
    
    return [
        path for path in directory.rglob('*') 
        if path.suffix.lower() in extensions and path.is_file()
    ]

def print_summary(success_count: int, total: int, failed_paths: List[Path]):
    """Print processing summary"""
    print(f"\nProcessing complete: {success_count}/{total} videos succeeded")
    if failed_paths:
        print("\nFailed files:")
        for path in failed_paths:
            print(f" - {path}")

# if __name__ == "__main__":
#     print("start to convert...")
#     target_ext = ".mp4"
#     source_ext = ".mp4"
#     level = 1

#     input_directory = "/home/userroot/shizheng/photo"
#     # sub_dir = "output"
#     name_postfix = "_output"

#     target_file_paths = target_file_path_with_level(input_directory, source_ext, level)

#     count = 0

#     for file_path in target_file_paths:
#         file = Path(file_path)
#         count += 1
#         print(count)
#         file_path = str(file.resolve())
#         target_file = file.parent / (file.stem + name_postfix + target_ext)

#         # # create output folder if it does not existed
#         # target_file.parent.mkdir(mode=755, parents=True, exist_ok=True)
        
#         target_file_path = str(target_file.resolve())

#         downsample_video(file_path, target_file_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Video Downsampling Tool')
    parser.add_argument('--input', required=True, nargs='+',
                        help='Input file(s) or directory(ies)')
    parser.add_argument('--output', required=True,
                        help='Output directory')
    parser.add_argument('--workers', type=int, default=cpu_count(),
                        help=f'Number of parallel workers (default: {cpu_count()})')
    
    args = parser.parse_args()
    
    # Collect input files
    input_files = []
    for path_str in args.input:
        path = Path(path_str)
        if path.is_file():
            input_files.append(path)
        elif path.is_dir():
            input_files.extend(find_videos(path))
        else:
            print(f"Warning: Path not found - {path}")
    
    if not input_files:
        print("No valid video files found. Exiting.")
        exit(1)
    
    output_dir = Path(args.output)
    
    print(f"Found {len(input_files)} videos for processing")
    print(f"Using {args.workers} parallel workers")
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process videos with generic function
    success_count, failed_paths = multi_process_videos(
        input_paths=input_files,
        output_dir=output_dir,
        processing_func=downsample_video,
        num_workers=min(args.workers, len(input_files))
    )
    
    # Print summary
    print_summary(success_count, len(input_files), failed_paths)
