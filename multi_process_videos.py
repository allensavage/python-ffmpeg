from multiprocessing import Pool, cpu_count
from typing import Callable, List, Tuple
from pathlib import Path

def multi_process_videos(
    input_paths: List[Path], 
    output_dir: Path, 
    processing_func: Callable[[Tuple[Path, Path]], Tuple[bool, Path]],
    num_workers: int = cpu_count()
) -> Tuple[int, List[Path]]:
    """
    Generic function to process multiple videos in parallel using any processing function.
    
    Args:
        input_paths: List of Path objects for input videos
        output_dir: Output directory Path object
        processing_func: Function that takes (input_path, output_path) and returns (success, input_path)
        num_workers: Number of parallel processes
        
    Returns:
        Tuple (success_count, failed_paths)
    """
    # Create task list: (input_path, output_path)
    tasks = []
    for input_path in input_paths:
        output_path = output_dir / f"{input_path.stem}_output{input_path.suffix}"
        tasks.append((input_path, output_path))
    
    # Process videos in parallel
    with Pool(processes=num_workers) as pool:
        results = pool.map(processing_func, tasks)
    
    # Calculate results
    success_count = sum(1 for status, _ in results if status)
    failed_paths = [path for status, path in results if not status]
    
    return success_count, failed_paths