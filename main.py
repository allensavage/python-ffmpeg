import sys

sys.path.append("/home/userroot/GitClone/python-ffmpeg")
sys.path.append("/home/userroot/GitClone/own_function")
from .own_function import filter_files_by_extension, list_files_by_depth

from .downsampling import downsample_video
from .multi_process_videos import multi_process_videos
from multiprocessing import cpu_count
from typing import List, Tuple
from pathlib import Path
import argparse
from .logger import logger


def print_summary(
    success_count: int,
    total: int,
    failed_paths: List[Path],
    processing_times: List[float],
    total_time: float,
):
    """Print processing summary"""
    avg_time = sum(processing_times) / total if total else 0
    min_time = min(processing_times) if processing_times else 0
    max_time = max(processing_times) if processing_times else 0

    logger.log("\n" + "=" * 60, None)
    logger.log("PROCESSING SUMMARY", None)
    logger.log("=" * 60, None)
    logger.log(f"Total Videos:      {total}", None)
    logger.log(
        f"Successful:        {success_count} ({success_count/total*100:.1f}%)", None
    )
    logger.log(f"Failed:            {len(failed_paths)}", None)
    logger.log(f"Total Time:        {total_time:.1f} seconds", None)
    logger.log(f"Avg Time/Video:    {avg_time:.1f} seconds", None)
    logger.log(f"Fastest Video:     {min_time:.1f} seconds", None)
    logger.log(f"Slowest Video:     {max_time:.1f} seconds", None)

    if failed_paths:
        logger.log("\nFAILED FILES:", None)
        for path in failed_paths:
            logger.log(f" - {path}", None)

    logger.log("\nPROCESSING TIMES:", None)
    for i, time_val in enumerate(sorted(processing_times, reverse=True)):
        logger.log(f"{i+1:2d}. {time_val:6.1f}s", None)
    logger.log("=" * 60, None)


def main():
    parser = argparse.ArgumentParser(description="Video Downsampling Tool")
    parser.add_argument(
        "--input", required=True, nargs="+", help="Input file(s) or directory(ies)"
    )
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument(
        "--workers",
        type=int,
        default=2,
        help=f"Number of parallel workers (default: 2)",
    )
    parser.add_argument(
        "--max_depth",
        type=int,
        default=0,
        help="the depth of folder you want to research (default: 0)",
    )

    video_exts = [".mp4", ".mov", ".mkv", ".avi", ".flv", ".m4v"]

    args = parser.parse_args()

    max_depth = args.max_depth

    # Collect input files
    input_files = []

    for path in args.input:
        files = list_files_by_depth(path, max_depth)
        input_files = filter_files_by_extension(files, video_exts)

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    num_workers = min(args.workers, len(input_files), cpu_count())
    logger.log(f"Found {len(input_files)} videos for processing", "MAIN")
    logger.log(f"Using {num_workers} workers", "MAIN")

    # Process videos
    success_count, failed_paths, proc_times, total_time = multi_process_videos(
        input_paths=input_files,
        output_dir=output_dir,
        processing_func=downsample_video,
        num_workers=num_workers,
    )

    # Print summary
    print_summary(success_count, len(input_files), failed_paths, proc_times, total_time)


if __name__ == "__main__":
    main()
