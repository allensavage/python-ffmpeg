import time
from multiprocessing import Pool
from typing import Callable, List, Tuple
from pathlib import Path
from .logger import logger


def multi_process_videos(
    input_paths: List[Path],
    output_dir: Path,
    processing_func: Callable[[Path, Path], Tuple[bool, float]],
    num_workers: int,
) -> Tuple[int, List[Path], List[float], float]:
    """
    Process videos in parallel with progress tracking.

    Args:
        input_paths: List of input video paths
        output_dir: Output directory
        processing_func: Function to process individual videos
        num_workers: Number of parallel workers

    Returns:
        Tuple (success_count, failed_paths, processing_times, total_time)
    """
    start_time = time.time()
    tasks = [(ip, output_dir / f"{ip.stem}_output{ip.suffix}") for ip in input_paths]

    success_count = 0
    failed_paths = []
    processing_times = []

    # Create a helper function for progress tracking
    def process_task_wrapper(task: Tuple[Path, Path]) -> Tuple[bool, Path, float]:
        input_path, output_path = task
        prefix = f"{tasks.index(task)+1}/{len(tasks)}"
        logger.log(f"Starting: {input_path.name}", prefix)
        success, ptime = processing_func(input_path, output_path)
        status = "Success" if success else "Failed"
        logger.log(f"Completed: {status} in {ptime:.1f}s", prefix)
        return success, input_path, ptime

    with Pool(processes=num_workers) as pool:
        results = []
        total = len(tasks)

        # Process tasks as they complete
        for i, result in enumerate(pool.imap_unordered(process_task_wrapper, tasks)):
            success, path, ptime = result
            results.append(result)
            processing_times.append(ptime)

            if success:
                success_count += 1
            else:
                failed_paths.append(path)

            # Print progress
            progress = (i + 1) / total * 100
            logger.log(f"Overall progress: {i+1}/{total} ({progress:.1f}%)", "MAIN")

    total_time = time.time() - start_time
    return success_count, failed_paths, processing_times, total_time
