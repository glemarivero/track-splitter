import os
import streamlit as st
import base64
import os
from controls import display_audio
from utils import install_ffmpeg_from_url, get_file_path, separate_tracks

AUDIO_DIR = "inputs"
OUTPUT_PATH = "separated"
STEMS = ["vocals", "bass", "drums", "other"]

st.title("Audio Track Splitter")

@st.cache_resource
def get_audio_base64(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
        return base64.b64encode(data).decode()

def get_base64_from_file(file):
    data = file.read()
    st.write(data)
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
          ffmpeg_path = os.path.dirname(install_ffmpeg_from_url())
          path = save_uploaded_file(file_upload)
          separate_tracks(path, OUTPUT_PATH, ffmpeg_path=ffmpeg_path)
  else:
      song = track
  exists = True
  stems = dict()
  try:
      for stem in STEMS:
          stems[stem] = get_audio_base64(get_file_path(song, stem))
  except Exception:
      exists = False
  if exists:
    st.header(song)
    display_audio(**stems)
    cols = st.columns(2)  # Create a 2x2 grid using Streamlit columns
    for i, stem in enumerate(STEMS):
      with open(get_file_path(song, stem), "rb") as fid:
        track_bytes = fid.read()

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