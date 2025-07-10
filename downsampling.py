import subprocess
from multiprocessing import Lock
import sys
from typing import Tuple, Optional
from pathlib import Path
import shlex
from datetime import datetime
import time


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
        print_safe(f"Starting processing → {output_path.name}", prefix)

        # Run FFmpeg and capture output in real-time
        with subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            text=True,
            encoding="utf-8",
            errors="replace",
        ) as proc:
            # Capture and print output line by line
            for line in proc.stdout:
                line = line.strip()
                if line:
                    print_safe(line, prefix)

            # Check process completion
            if proc.wait() == 0:
                success = True
                print_safe("Completed successfully", prefix)
            else:
                print_safe(f"Failed with exit code: {proc.returncode}", prefix)

    except Exception as e:
        print_safe(f"Unexpected error: {str(e)}", prefix)

    finally:
        processing_time = time.time() - start_time
        print_safe(f"Processing time: {processing_time:.1f}s", prefix)

    return success, input_path, processing_time
