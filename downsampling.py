import subprocess
from typing import Tuple
from pathlib import Path
import time
from .logger import logger  # Import the global logger


def downsample_video(input_path: Path, output_path: Path) -> Tuple[bool, float]:
    """
    Downsamples a video with timing and real-time output handling.

    Args:
        input_path: Path to input video
        output_path: Path for output video
        lock: Thread lock for safe printing

    Returns:
        Tuple (success status, input_path, processing_time)
    """

    start_time = time.time()
    prefix = input_path.stem[:15] + (input_path.stem[15:] and "..")

    # Construct filter chain
    vf_chain = (
        "bwdif=mode=send_field:deint=interlaced,"  # Deinterlace
        "nlmeans=s=1.0:r=3:p=3,"  # Denoise (Ultralight preset equivalent)
        "unsharp=3:3:0.5,"  # Sharpen (Ultralight preset)
        "scale='if(gt(iw,ih),1920,-2)':'if(gt(ih,iw),1920,-2)',"  # Long edge 1920px
        "setsar=1"  # Ensure square pixels
        # f"subtitles={input_path}:si=0"    # Burn first subtitle track
    )

    # Construct FFmpeg command
    cmd = [
        "ffmpeg",
        "-threads",
        "0",
        "-filter_threads",
        "0",
        "-i",
        input_path,
        "-map",
        "0",  # Include all streams
        "-map",
        "-0:s",  # Exclude subtitle streams (burned in)
        "-map_metadata",
        "0",  # Pass through metadata
        "-map_chapters",
        "0",  # Include chapters
        "-movflags",
        "+faststart",  # Web optimization
        "-async",
        "1",  # Align A/V start
        "-fps_mode",
        "vfr",  # Handle VFR (same as source peak)
        "-c:v",
        "libx265",  # H.265 encoder
        "-pix_fmt",
        "yuv420p10le",  # 10-bit color
        "-crf",
        "19",  # Constant Quality 19
        "-preset",
        "fast",  # Encoder preset
        "-profile:v",
        "main10",  # 10-bit profile
        "-x265-params",
        "level=auto:pools=threads:frame-threads=0",  # Auto level and x265 multi-threading
        "-vf",
        vf_chain,  # Apply filter chain
        "-c:a",
        "copy",  # Audio passthru
        "-disposition:a",
        "default",  # Mark default audio track
        output_path,
    ]

    success = False
    try:
        logger.log(f"Starting processing → {output_path.name}", prefix)
        
        # Run FFmpeg with real-time output capture
        with subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            text=True,
            encoding='utf-8',
            errors='replace'
        ) as proc:
            for line in proc.stdout:
                logger.log(line.strip(), prefix)
            
            if proc.wait() == 0:
                success = True
                logger.log("Completed successfully", prefix)
            else:
                logger.log(f"Failed with code {proc.returncode}", prefix)
                
    except Exception as e:
        logger.log(f"Unexpected error: {str(e)}", prefix)
    
    finally:
        processing_time = time.time() - start_time
        logger.log(f"Processing time: {processing_time:.1f}s", prefix)
        
    return success, processing_time