import time
from multiprocessing import Pool
from typing import Callable, List, Tuple, Any
from pathlib import Path
from logger import logger


# Create a helper function for progress tracking
def _process_task_wrapper(args: Tuple[Any, Callable]) -> Tuple[bool, Path, float]:
    """Top-level wrapper function for processing tasks"""
    task, processing_func = args
    input_path, output_path = task
    success, ptime = processing_func(input_path, output_path)
    return success, input_path, ptime


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
    tasks = []
    for idx, input_path in enumerate(input_paths):
        output_path = output_dir / f"{input_path.stem}_output{input_path.suffix}"
        tasks.append((input_path, output_path))
        logger.log(
            f"Queued: {input_path.name} (task {idx+1}/{len(input_paths)})", "MAIN"
        )

    args_list = [(task, processing_func) for task in tasks]
    total_tasks = len(tasks)

    success_count = 0
    failed_paths = []
    processing_times = []

    with Pool(processes=num_workers) as pool:
        # Use imap_unordered to get results as they complete
        results = pool.imap_unordered(_process_task_wrapper, args_list)

        # Process results as they come in
        for i, result in enumerate(results, 1):
            success, path, ptime = result
            processing_times.append(ptime)

            if success:
                success_count += 1
                status = "Success"
            else:
                failed_paths.append(path)
                status = "Failed"

            # Update progress
            progress = i / total_tasks * 100
            logger.log(
                f"Completed {i}/{total_tasks} ({progress:.1f}%): "
                f"{path.name} - {status} in {ptime:.1f}s",
                "MAIN",
            )

    total_time = time.time() - start_time
    return success_count, failed_paths, processing_times, total_time
