import os
import streamlit as st
import base64
import os
import urllib.request
import tarfile
from utils import separate_tracks
from controls import display_audio

AUDIO_DIR = "inputs"
OUTPUT_PATH = "separated"

# Set Streamlit layout to wide mode
# st.set_page_config(layout="wide")

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


def footer():
    return st.markdown("""
    <style>
    .footer {
        position: fixed;
        bottom: 10%;
        left: 0;
        width: 100%;
        text-align: center;
        color: gray;
        padding: 1%;
        background-color: rgba(240, 240, 240, 0.9);
        font-size: 1rem;
        border-top: 0.1rem solid #ddd;
    }
    @media (max-width: 768px) {
        .footer {
            font-size: 0.9rem;
            padding: 2%;
        }
    }
    </style>

    <div class="footer">
        Made with ❤️ by Gabriel Lema<br>
        Powered by <a href="https://github.com/facebookresearch/demucs" target="_blank">Demucs</a> for audio track separation.
    </div>
    """, unsafe_allow_html=True)


def main():
  # Get all MP3 files in folder (without extension)
  mp3_files = [f[:-4] for f in os.listdir(AUDIO_DIR) if f.endswith(".mp3")]

  # Streamlit dropdowns
  track = st.selectbox("Choose a preloaded audio track", mp3_files, key="audio1")
  file_upload = st.file_uploader("Or choose your own song!")

  if file_upload is not None:
      song = file_upload.name
      song = song.replace(" ", "_")[:-4]  # Remove .mp3 extension"]
      if st.button("Split tracks"):
          path = save_uploaded_file(file_upload)
          separate_tracks(path, OUTPUT_PATH, ffmpeg_path=ffmpeg_path)
  else:
      song = track

  # Convert both MP3 files to base64
  exists = True
  vocals_b64 = bass_b64 = drums_b64 = other_b64 = None
  try:
      vocals_b64 = get_audio_base64(f"separated/htdemucs/{song}/vocals.mp3")
      bass_b64 = get_audio_base64(f"separated/htdemucs/{song}/bass.mp3")
      drums_b64 = get_audio_base64(f"separated/htdemucs/{song}/drums.mp3")
      other_b64 = get_audio_base64(f"separated/htdemucs/{song}/other.mp3")
  except Exception:
      exists = False
  if exists:
    st.header(song)
    display_audio(vocals_b64=vocals_b64, bass_b64=bass_b64, drums_b64=drums_b64, other_b64=other_b64)
    cols = st.columns(2)  # Create a 2x2 grid using Streamlit columns
    stems = ["vocals", "bass", "drums", "other"]
    for i, stem in enumerate(stems):
      with open(f"separated/htdemucs/{song}/{stem}.mp3", "rb") as f:
        track_bytes = f.read()

      with cols[i % 2]:  # Alternate between the two columns
        st.download_button(
          label=f"Download {stem.capitalize()}",
          data=track_bytes,
          file_name=f"{song} - {stem}.mp3",
          mime="audio/mp3"
        )
  footer()


if __name__ == "__main__":
    main()
