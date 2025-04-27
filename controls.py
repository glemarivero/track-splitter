import streamlit as st

STEMS_EMOJIS = {
    "vocals": "🎤",
    "bass": "🎸",
    "drums": "🥁",
    "other": "🎶",
    "piano": "🎹",
    "guitar": "🎸",
}

def display_audio(song, stems, model):
    # Consolidated HTML and JavaScript for audio controls and playback
    src_stems = {key: f"data:audio/mp3;base64,{value}" for key, value in stems.items()}

    audio_columns = ""
    for stem, src in src_stems.items():
        audio_columns += f"""
        <div class="audio-column">
            <audio id="{stem}" src="{src}" preload="auto"></audio>
            <div class="audio-control">
                <label>{STEMS_EMOJIS[stem]} {stem.capitalize()}</label>
                <div style="display: flex; align-items: center; justify-content: center; gap: 10px;">
                    <input type="range" id="vol_{stem}" min="0" max="1" step="0.01" value="1">
                </div>
            </div>
        </div>
        """

    html_code = f"""
    <style>
    .audio-controls {{
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        gap: 5%; /* Adjusted to percentage */
        margin-top: 5%; /* Adjusted to percentage */
    }}
    .audio-column {{
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 5%; /* Adjusted to percentage */
        min-width: 45%; /* Ensures two columns */
    }}
    .audio-control {{
        width: 60%;
        margin: 0 auto; /* Centers the control */
        text-align: center;
    }}
    @media (max-width: 768px) {{
        .audio-controls {{
            flex-direction: column; /* Stack columns vertically on smaller screens */
            gap: 10%; /* Increase gap for better spacing on mobile */
        }}
        .audio-column {{
            min-width: 100%; /* Full width for each column on mobile */
        }}
    }}
    </style>

    <div>
        <button onclick="playAll()">▶️ Play</button>
        <button onclick="pauseAll()">⏸ Pause</button>
    </div>

    <div style="margin-top: 5%;"> <!-- Adjusted to percentage -->
        <label>Progress</label>
        <input type="range" id="seekbar" value="0" min="0" step="0.01" style="width: 100%;">
    </div>

    <div class="audio-controls">
        {audio_columns}
    </div>

    <script>
    const stems = {list(src_stems.keys())};
    const seekbar = document.getElementById("seekbar");
    const audioElements = stems.reduce((acc, stem) => {{
        acc[stem] = document.getElementById(stem);
        return acc;
    }}, {{}});
    const volumeControls = stems.reduce((acc, stem) => {{
        acc[stem] = document.getElementById(`vol_${{stem}}`);
        return acc;
    }}, {{}});

    function playAll() {{
        const t = Math.min(...Object.values(audioElements).map(audio => audio.duration || 0));
        seekbar.max = t;
        Object.values(audioElements).forEach(audio => audio.play());
    }}

    function pauseAll() {{
        Object.values(audioElements).forEach(audio => audio.pause());
    }}

    setInterval(() => {{
        if (Object.values(audioElements).every(audio => !audio.paused)) {{
            const pos = Math.min(...Object.values(audioElements).map(audio => audio.currentTime));
            seekbar.value = pos;
        }}
    }}, 100);

    seekbar.addEventListener("input", () => {{
        Object.values(audioElements).forEach(audio => {{
            audio.currentTime = seekbar.value;
        }});
    }});

    Object.entries(volumeControls).forEach(([stem, control]) => {{
        control.addEventListener("input", () => {{
            audioElements[stem].volume = control.value;
        }});
    }});
    </script>
    """
    st.components.v1.html(html_code, height=400 if len(stems) > 4 else 300, scrolling=True)