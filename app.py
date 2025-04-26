import os
import streamlit as st
import base64
import os
import urllib.request
import tarfile
from utils import separate_tracks
from demucs import separate

st.title("Audio Track Splitter")

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

ffmpeg_path = os.path.dirname(install_ffmpeg_from_url())

@st.cache_resource
def get_audio_base64(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
        return base64.b64encode(data).decode()

def get_base64_from_file(file):
    data = file.read()
    return base64.b64encode(data).decode()

def save_uploaded_file(uploaded_file, save_dir="inputs"):
    file_name = uploaded_file.name.replace(" ", "_")
    save_path = os.path.join(save_dir, file_name)
    if os.path.exists(save_path):
        return save_path
    os.makedirs(save_dir, exist_ok=True)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.read())
    return save_path

AUDIO_DIR = "inputs"
OUTPUT_PATH = "separated"

# Get all MP3 files in folder (without extension)
mp3_files = [f[:-4] for f in os.listdir(AUDIO_DIR) if f.endswith(".mp3")]

# Streamlit dropdowns
track = st.selectbox("Audio file", mp3_files, key="audio1")
file_upload = st.file_uploader("Choose your own song!")

if file_upload is not None:
    song = file_upload.name
    song = song.replace(" ", "_")[:-4]  # Remove .mp3 extension"]
    if st.button("Split tracks"):
        path = save_uploaded_file(file_upload)
        separate_tracks(path, OUTPUT_PATH, ffmpeg_path=ffmpeg_path)
else:
    song = track
    if st.button("Split tracks"):
        separate(f"{AUDIO_DIR}/{song}.mp3", OUTPUT_PATH, ffmpeg_path=ffmpeg_path)

# Convert both MP3 files to base64
try:
    vocals_b64 = get_audio_base64(f"separated/htdemucs/{song}/vocals.mp3")
    bass_b64 = get_audio_base64(f"separated/htdemucs/{song}/bass.mp3")
    drums_b64 = get_audio_base64(f"separated/htdemucs/{song}/drums.mp3")
    other_b64 = get_audio_base64(f"separated/htdemucs/{song}/other.mp3")
except Exception:
    st.stop()


st.header(song)
# Create base64 sources
src_vocals = f"data:audio/mp3;base64,{vocals_b64}"
src_bass = f"data:audio/mp3;base64,{bass_b64}"
src_drums = f"data:audio/mp3;base64,{drums_b64}"
src_other = f"data:audio/mp3;base64,{other_b64}"

# HTML player
html_code = f"""
<audio id="vocals" src="{src_vocals}" preload="auto"></audio>
<audio id="bass" src="{src_bass}" preload="auto"></audio>
<audio id="drums" src="{src_drums}" preload="auto"></audio>
<audio id="other" src="{src_other}" preload="auto"></audio>

<div>
  <button onclick="playAll()">▶ Play</button>
  <button onclick="pauseAll()">⏸ Pause</button>
</div>

<div style="margin-top: 10px;">
  <label>Progress</label>
  <input type="range" id="seekbar" value="0" min="0" step="0.01" style="width: 100%;">
</div>

<div style="margin-top: 10px;">
  <label>Volume Vocals</label>
  <input type="range" id="vol_vocals" min="0" max="1" step="0.01" value="1">
  <label style="margin-left: 20px;">Volume Bass</label>
  <input type="range" id="vol_bass" min="0" max="1" step="0.01" value="1">
</div>
<div style="margin-top: 10px;">
  <label>Volume Drums</label>
  <input type="range" id="vol_drums" min="0" max="1" step="0.01" value="1">
  <label style="margin-left: 20px;">Volume Other</label>
  <input type="range" id="vol_other" min="0" max="1" step="0.01" value="1">
</div>

<script>
const vocals = document.getElementById("vocals");
const bass = document.getElementById("bass");
const drums = document.getElementById("drums");
const other = document.getElementById("other");
const seekbar = document.getElementById("seekbar");
const vol_vocals = document.getElementById("vol_vocals");
const vol_bass = document.getElementById("vol_bass");
const vol_drums = document.getElementById("vol_drums");
const vol_other = document.getElementById("vol_other");

function playAll() {{
  const t = Math.min(vocals.duration || 0, bass.duration || 0, drums.duration || 0, other.duration || 0);
  seekbar.max = t;
  vocals.play();
  bass.play();
  drums.play();
  other.play();
}}

function pauseAll() {{
  vocals.pause();
  bass.pause();
  drums.pause();
  other.pause();
}}

setInterval(() => {{
  if (!vocals.paused && !bass.paused && !drums.paused && !other.paused) {{
    const pos = Math.min(vocals.currentTime, bass.currentTime, drums.currentTime, other.currentTime);
    seekbar.value = pos;
  }}
}}, 100);

seekbar.addEventListener("input", () => {{
  vocals.currentTime = seekbar.value;
  bass.currentTime = seekbar.value;
  drums.currentTime = seekbar.value;
  other.currentTime = seekbar.value;
}});

vol_vocals.addEventListener("input", () => {{
  vocals.volume = vol_vocals.value;
}});

vol_bass.addEventListener("input", () => {{
  bass.volume = vol_bass.value;
}});

vol_drums.addEventListener("input", () => {{
  drums.volume = vol_drums.value;
}});

vol_other.addEventListener("input", () => {{
  other.volume = vol_other.value;
}});
</script>
"""

st.components.v1.html(html_code, height=350)