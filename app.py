import os
import streamlit as st
import base64
import os
from controls_refactored import display_audio
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


def save_uploaded_file(uploaded_file, save_dir="inputs"):
    file_name = uploaded_file.name
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

MODELS = {
    "htdemucs": "HTDemucs - 4 tracks",
    "htdemucs_6s": "HTDemucs - 6 tracks",
}

def main():
  # Get all MP3 files in folder (without extension)
  model = st.selectbox("Choose a Demucs model", options=list(MODELS.keys()), format_func=lambda model: MODELS[model])
  if model == "htdemucs":
     stems = ["vocals", "bass", "drums", "other"]
  else:
      stems = ["vocals", "bass", "drums", "other", "guitar", "piano"]
  songs = [path for path in os.listdir(f"{OUTPUT_PATH}/{model}") if not path.startswith(".")]
  # Streamlit dropdowns
  track = st.selectbox("Choose a preloaded audio track", songs, key="audio1")
  file_upload = st.file_uploader("Or choose your own song!")

  if file_upload is not None:
      song = file_upload.name
      song = song[:-4]  # Remove .mp3 extension"]
      if st.button("Split tracks"):
          ffmpeg_path = os.path.dirname(install_ffmpeg_from_url())
          path = save_uploaded_file(file_upload)
          separate_tracks(path, OUTPUT_PATH, ffmpeg_path=ffmpeg_path, model=model)
  else:
      song = track
  exists = True
  loaded_stems = dict()
  try:
      for stem in stems:
          loaded_stems[stem] = get_audio_base64(get_file_path(song, stem, model=model))
  except Exception:
      exists = False
  if exists:
    st.header(song)
    display_audio(stems=loaded_stems, model=model)
    cols = st.columns(2)  # Create a 2x2 grid using Streamlit columns
    for i, stem in enumerate(STEMS):
      with open(get_file_path(song, stem, model=model), "rb") as fid:
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