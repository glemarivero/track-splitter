import base64
import os

import streamlit as st

from controls import display_audio
from utils import (
    download_from_yt,
    get_file_path,
    install_ffmpeg_from_url,
    lock_exists,
    lock_file,
    lock_remove,
    read_version,
    separate_tracks,
)

AUDIO_DIR = "inputs"
OUTPUT_PATH = "separated"


@st.cache_resource
def get_audio_base64(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
        return base64.b64encode(data).decode()


def save_uploaded_file(uploaded_file, save_dir=AUDIO_DIR):
    file_name = uploaded_file.name
    save_path = os.path.join(save_dir, file_name)
    if os.path.exists(save_path):
        return save_path
    os.makedirs(save_dir, exist_ok=True)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.read())
    return save_path


def footer():
    version = read_version()
    st.markdown(
        f"""
    <style>
    .footer {{
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
    }}
    @media (max-width: 768px) {{
        .footer {{
            font-size: 0.9rem;
            padding: 2%;
        }}
    }}
    .audio-section {{
        margin-bottom: 10px; /* Reduce space below audio controllers */
    }}
    </style>
    <div class="footer">
        Made with ❤️ by Gabriel Lema<br>
        Version: {version} <br>
        Powered by <a href="https://github.com/facebookresearch/demucs" target="_blank">Demucs</a> for audio track separation.
    </div>
    """,
        unsafe_allow_html=True,
    )


MODELS = {
    "htdemucs": {
        "description": "HTDemucs - 4 tracks",
        "stems": ["vocals", "bass", "drums", "other"],
    },
    "htdemucs_6s": {
        "description": "HTDemucs - 6 tracks",
        "stems": ["vocals", "bass", "drums", "guitar", "piano", "other"],
    },
}


def main():
    st.title("Audio Track Splitter")
    ffmpeg_path = os.path.dirname(install_ffmpeg_from_url())
    print(ffmpeg_path)
    st.session_state["ffmpeg_path"] = ffmpeg_path
    model = st.selectbox(
        label="Choose a Demucs model",
        options=list(MODELS.keys()),
        format_func=lambda model: MODELS[model]["description"]
        + f' ({", ".join(MODELS[model]["stems"])})',
    )
    stems = MODELS[model]["stems"]
    if "song" not in st.session_state:
        st.session_state["song"] = ""
    song = st.session_state.get("song", "")

    if not st.session_state["song"]:
        file_upload = st.file_uploader("Choose your own song!")
        yt_song = st.text_input("Enter YouTube link:")
        st.text(
            body="ℹ️ Double tap outside the input box after pasting the link if using your phone."
        )
        if yt_song:
            try:
                downloaded_song = download_from_yt(yt_song, input_dir=AUDIO_DIR)
                if downloaded_song:
                    st.session_state["song"] = (
                        downloaded_song  # Set downloaded song as default
                    )
                    st.success("Download complete!")
            except Exception:
                st.error("Failed to download the song.")

        if file_upload is not None:
            st.session_state["song"] = file_upload.name  # Set uploaded file as default
            save_uploaded_file(file_upload, save_dir=AUDIO_DIR)

        songs = [path for path in os.listdir(AUDIO_DIR) if not path.startswith(".")]
        songs = [""] + songs
        if st.session_state["song"] in songs:
            index = songs.index(st.session_state["song"])
        else:
            index = 0
        st.session_state["song"] = st.selectbox(
            "Or choose a preloaded audio track",
            songs,
            key="audio1",
            index=index,
        )
        if st.session_state["song"]:
            st.rerun()
    else:
        if st.button("Go back"):
            st.session_state["song"] = ""
            st.rerun()
        songs = [path for path in os.listdir(AUDIO_DIR) if not path.startswith(".")]
        st.session_state["song"] = st.selectbox(
            "Choose a preloaded audio track",
            songs,
            key="audio1",
            index=songs.index(st.session_state["song"]),
        )
        st.header(st.session_state["song"])
        loaded_stems = dict()
        try:
            for stem in stems:
                loaded_stems[stem] = get_audio_base64(
                    get_file_path(song=st.session_state["song"], stem=stem, model=model)
                )
            exists = True
        except Exception:
            exists = False
            file_path = os.path.join(AUDIO_DIR, st.session_state["song"])
            audio_placeholder = st.empty()
            audio_placeholder.audio(file_path)
            split_button_placeholder = st.empty()
            if split_button_placeholder.button(
                "Split tracks", key="split_button_placeholder"
            ):
                if not lock_exists():
                    lock_file()
                    separate_tracks(
                        file_path=file_path,
                        output_path=OUTPUT_PATH,
                        ffmpeg_path=st.session_state["ffmpeg_path"],
                        model=model,
                    )
                    lock_remove()
                    exists = True
                    audio_placeholder.empty()
                    split_button_placeholder.empty()
                    st.rerun()
                else:
                    st.warning("Please wait a moment before trying again.")
        if exists:
            display_audio(song=song, stems=loaded_stems, model=model)
            stem_to_download = st.selectbox(
                "Download", options=[""] + stems, key="download"
            )
            if stem_to_download:
                st.download_button(
                    label="Download",
                    data=loaded_stems[stem_to_download],
                    file_name=f"{song} - {stem_to_download}.mp3",
                    mime="audio/mp3",
                )

    footer()


if __name__ == "__main__":
    main()
