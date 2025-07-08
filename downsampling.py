import subprocess
import shlex

def downsample_video(input_path, output_path):
    """
    Downsamples a video with HandBrake-like settings using FFmpeg.
    
    Args:
        input_path (str): Path to input video file.
        output_path (str): Path for output video file.
    """
    # # Escape input path for subtitle filter
    # escaped_input_path = shlex.quote(input_path)
    
    # Construct filter chain
    vf_chain = (
        "bwdif=mode=send_field:deint=interlaced,"  # Deinterlace
        "nlmeans=s=1.0:r=3:p=3,"                 # Denoise (Ultralight preset equivalent)
        "unsharp=3:3:0.5,"                       # Sharpen (Ultralight preset)
        "scale='if(gt(iw,ih),1920,-2)':'if(gt(ih,iw),1920,-2)',"        # Long edge 1920px
        "setsar=1"                          # Ensure square pixels
        # f"subtitles={input_path}:si=0"    # Burn first subtitle track
    )
    
    # Construct FFmpeg command
    cmd = [
        "ffmpeg",
        "-threads", "0",
        "-filter_threads", "0",
        "-i", input_path,
        "-map", "0",                          # Include all streams
        "-map", "-0:s",                       # Exclude subtitle streams (burned in)
        "-map_metadata", "0",                 # Pass through metadata
        "-map_chapters", "0",                 # Include chapters
        "-movflags", "+faststart",            # Web optimization
        "-async", "1",                        # Align A/V start
        "-fps_mode", "vfr",                      # Handle VFR (same as source peak)
        "-c:v", "libx265",                    # H.265 encoder
        "-pix_fmt", "yuv420p10le",            # 10-bit color
        "-crf", "19",                         # Constant Quality 19
        "-preset", "fast",                    # Encoder preset
        "-profile:v", "main10",               # 10-bit profile
        "-x265-params", "level=auto:pools=threads:frame-threads=0",        # Auto level and x265 multi-threading
        "-vf", vf_chain,                      # Apply filter chain
        "-c:a", "copy",                       # Audio passthru
        "-disposition:a", "default",          # Mark default audio track
        output_path
    ]
    
    try:
        print(f"Processing: {input_path} → {output_path}")
        result = subprocess.run(cmd, check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        print(f"Completed: {output_path}")
        return True, input_path
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode() if e.stderr else str(e)
        print(f"Error processing {input_path}: {error_msg}")
        return False, input_path
    except Exception as e:
        print(f"Unexpected error with {input_path}: {str(e)}")
        return False, input_path