import datetime
import os
import shlex
import tarfile
import urllib.request

import streamlit as st
import tqdm as tqdm_module
from demucs.separate import main as demucs_main

in_path = "./inputs"
out_path = "./separated/"
MAX_TIME_LOCK_IN_SECONDS = 1000


def timeit(func):
    def wrapper(*args, **kwargs):
        import time

        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        st.write(f"Execution time: {end_time - start_time:.2f} seconds")
        return result

    return wrapper


def call_function_with_streamlit_progress(func, *args, **kwargs):
    progress_bar = st.progress(0)
    progress_text = st.empty()

    # Save the real tqdm
    real_tqdm = tqdm_module.tqdm

    # Fake tqdm
    class StreamlitTqdm(real_tqdm):
        def update(self, n=1):
            super().update(n)
            if self.total:
                progress = int((self.n / self.total) * 100)
                progress_bar.progress(min(progress, 100))
                elapsed_time = self.format_dict["elapsed"]
                rate = self.format_dict["rate"]
                remaining_time = (
                    (self.total - self.n) / rate if rate and self.total > self.n else 0
                )
                progress_text.text(
                    f"Progress: {progress}% | Elapsed: {elapsed_time:.2f}s | Remaining: {remaining_time:.2f}s"
                )
                if self.total == self.n:
                    progress_bar.empty()
                    progress_text.empty()

    try:
        # Monkey-patch
        tqdm_module.tqdm = StreamlitTqdm
        return func(*args, **kwargs)

    finally:
        # Restore tqdm
        tqdm_module.tqdm = real_tqdm


@timeit
def separate_tracks(
    file_path: str, output_path: str, ffmpeg_path=None, model="htdemucs"
):
    opts_str = f'-o {output_path} -n {model} --device cpu --mp3 --mp3-bitrate=320 "{file_path}"'

    opts = shlex.split(opts_str)
    os.environ["PATH"] = (
        f"{ffmpeg_path}:{os.environ['PATH']}" if ffmpeg_path else os.environ["PATH"]
    )
    call_function_with_streamlit_progress(demucs_main, opts)


def install_ffmpeg_from_url(install_dir="ffmpeg_bin"):
    if os.path.exists("ffmpeg_bin/ffmpeg-7.0.2-amd64-static"):
        return "ffmpeg_bin/ffmpeg-7.0.2-amd64-static/ffmpeg"
    url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
    tar_path = "ffmpeg.tar.xz"

    # Create install dir
    os.makedirs(install_dir, exist_ok=True)

    # Download the file
    urllib.request.urlretrieve(url, tar_path)

    # Extract the archive
    with tarfile.open(tar_path, "r:xz") as tar:
        tar.extractall(path=install_dir)

    # Find the ffmpeg binary inside the extracted folder
    extracted_dir = next(
        os.path.join(install_dir, d)
        for d in os.listdir(install_dir)
        if d.startswith("ffmpeg")
    )
    ffmpeg_path = os.path.join(extracted_dir, "ffmpeg")

    # Make executable
    os.chmod(ffmpeg_path, 0o755)
    # Move ffmpeg to the PATH
    os.environ["PATH"] = f"{os.path.dirname(ffmpeg_path)}:{os.environ['PATH']}"

    return ffmpeg_path


def get_file_path(song: str, stem: str, model: str) -> str:
    if song.endswith(".mp3"):
        song = song[:-4]
    return f"{out_path}/{model}/{song}/{stem}.mp3"


def download_from_yt(url: str, input_dir: str) -> str:
    import yt_dlp

    # if https://youtu.be/GLvohMXgcBo?si=1RLd6Dc6Yxz-4Yb5
    # then url = https://www.youtube.com/watch?v=GLvohMXgcBo&si=1RLd6Dc6Yxz-4Yb5
    if "youtu.be" in url:
        video = url.split("/")[-1].split("?")[0]
        url = f"https://www.youtube.com/watch?v={video}"

    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "outtmpl": f"{input_dir}/%(title)s.%(ext)s",
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        },
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        original_file = ydl.prepare_filename(info)
        # Replace extension with .mp3
        mp3_file = os.path.basename(os.path.splitext(original_file)[0] + ".mp3")
        return mp3_file


def lock_file():
    # creates a lock file with the current time
    now = datetime.datetime.now()
    with open("/tmp/lock", "w") as f:
        f.write(now.isoformat())


def lock_remove():
    # removes the lock file if it exists
    if os.path.exists("/tmp/lock"):
        os.remove("/tmp/lock")


def lock_exists(max_time_lock_in_seconds=MAX_TIME_LOCK_IN_SECONDS):
    # checks if the lock file exists and when it was created
    now = datetime.datetime.now()
    if os.path.exists("/tmp/lock"):
        with open("/tmp/lock", "r") as f:
            created_time = datetime.datetime.fromisoformat(f.read().strip())
        if (now - created_time).total_seconds() > max_time_lock_in_seconds:
            lock_remove()
            return False
        else:
            return True
    else:
        return False
