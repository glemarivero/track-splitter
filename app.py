import os
import streamlit as st
import base64
from utils import separate

st.title("Song tracks splitter")

@st.cache_resource
def get_audio_base64(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
        return base64.b64encode(data).decode()

def get_base64_from_file(file):
    data = file.read()
    return base64.b64encode(data).decode()

def save_uploaded_file(uploaded_file, save_dir="inputs"):
    save_path = os.path.join(save_dir, uploaded_file.name)
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
track = st.sidebar.selectbox("Audio file", mp3_files, key="audio1")
file_upload = st.sidebar.file_uploader("Choose your own song!")

if file_upload is not None:
    song = file_upload.name
    if st.sidebar.button("Split tracks"):
        path = save_uploaded_file(file_upload)
        separate(path, OUTPUT_PATH)
else:
    song = track
    if st.sidebar.button("Split tracks"):
        separate(f"{AUDIO_DIR}/{song}.mp3", OUTPUT_PATH)

# Convert both MP3 files to base64
try:
    vocals_b64 = get_audio_base64(f"separated/htdemucs/{song}/vocals.mp3")
    bass_b64 = get_audio_base64(f"separated/htdemucs/{song}/bass.mp3")
    drums_b64 = get_audio_base64(f"separated/htdemucs/{song}/drums.mp3")
    other_b64 = get_audio_base64(f"separated/htdemucs/{song}/other.mp3")
except Exception:
    st.stop()


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