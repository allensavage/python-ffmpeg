import sys
sys.path.append("/home/userroot/GitClone/python-ffmpeg")
sys.path.append("/home/userroot/OneDrive/Foam/MyThoughts/PC_Tech/python/own_function")
from own_function import get_target_file_path

from downsampling import downsample_video
from pathlib import Path

if __name__ == "__main__":
    print("start to convert...")
    target_ext = ".mp4"
    source_ext = ".mp4"

    input_directory = "/home/userroot/shizheng/photo"
    sub_dir = "output"

    target_file_paths = get_target_file_path(input_directory, source_ext)

    count = 0

    for file_path in target_file_paths:
        file = Path(file_path)
        count += 1
        print(count)
        file_path = str(file.resolve())
        target_file = file.parent / sub_dir / file.name

        # create output folder if it does not existed
        target_file.parent.mkdir(mode=755, parents=True, exist_ok=True)
        
        target_file_path = str(target_file.with_suffix(target_ext).resolve())

        downsample_video(file_path, target_file_path)