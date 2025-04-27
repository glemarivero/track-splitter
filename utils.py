import os
from demucs.separate import main as demucs_main
import streamlit as st
import tqdm as tqdm_module  # Not from tqdm import tqdm!
import urllib.request
import tarfile

in_path = f'./inputs'
out_path = f'./separated/'


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
                progress_text.text(f"Progress: {progress}%")
                if self.total == self.n:
                    progress_bar.empty()
                    progress_text.empty()

    try:
        # Monkey-patch
        tqdm_module.tqdm = StreamlitTqdm

        # Call your function
        return func(*args, **kwargs)

    finally:
        # Always restore tqdm
        tqdm_module.tqdm = real_tqdm

def separate_tracks(inp=None, outp=None, ffmpeg_path=None):
    inp = inp or in_path
    inp = inp.replace(" ", "")
    outp = outp or out_path
    opts_str = f"-o {outp} -n htdemucs --device cpu --mp3 --mp3-bitrate=320 {inp}"
    opts = opts_str.split()
    os.environ["PATH"] = f"{ffmpeg_path}:{os.environ['PATH']}" if ffmpeg_path else os.environ["PATH"]
    call_function_with_streamlit_progress(demucs_main, opts)


def install_ffmpeg_from_url(install_dir="ffmpeg_bin"):
    if os.path.exists("ffmpeg_bin/ffmpeg-7.0.2-amd64-static"):
        return "ffmpeg_bin/ffmpeg-7.0.2-amd64-static/ffmpeg"
    url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
    tar_path = "ffmpeg.tar.xz"

    # Create install dir
    os.makedirs(install_dir, exist_ok=True)

    # Download the file
    print("⬇️ Downloading ffmpeg static binary...")
    urllib.request.urlretrieve(url, tar_path)

    # Extract the archive
    print("📦 Extracting...")
    with tarfile.open(tar_path, "r:xz") as tar:
        tar.extractall(path=install_dir)

    # Find the ffmpeg binary inside the extracted folder
    extracted_dir = next(os.path.join(install_dir, d) for d in os.listdir(install_dir) if d.startswith("ffmpeg"))
    ffmpeg_path = os.path.join(extracted_dir, "ffmpeg")

    # Make executable
    os.chmod(ffmpeg_path, 0o755)

    return ffmpeg_path

def get_file_path(song, stem):
    return f"{out_path}/htdemucs/{song}/{stem}.mp3"
