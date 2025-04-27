import streamlit as st

def display_audio(vocals, bass, drums, other, model, piano=None, guitar=None):
    # Consolidated HTML and JavaScript for audio controls and playback
    src_vocals = f"data:audio/mp3;base64,{vocals}"
    src_bass = f"data:audio/mp3;base64,{bass}"
    src_drums = f"data:audio/mp3;base64,{drums}"
    src_other = f"data:audio/mp3;base64,{other}"
    src_piano = f"data:audio/mp3;base64,{piano}" if piano else None
    src_guitar = f"data:audio/mp3;base64,{guitar}" if guitar else None

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
        <div class="audio-column">
            <audio id="vocals" src="{src_vocals}" preload="auto"></audio>
            <div class="audio-control">
                <label>🎤 Vocals</label>
                <input type="range" id="vol_vocals" min="0" max="1" step="0.01" value="1">
            </div>
            <audio id="bass" src="{src_bass}" preload="auto"></audio>
            <div class="audio-control">
                <label>🎸 Bass</label>
                <input type="range" id="vol_bass" min="0" max="1" step="0.01" value="1">
            </div>
        </div>
        <div class="audio-column">
            <audio id="drums" src="{src_drums}" preload="auto"></audio>
            <div class="audio-control">
                <label>🥁 Drums</label>
                <input type="range" id="vol_drums" min="0" max="1" step="0.01" value="1">
            </div>
            <audio id="other" src="{src_other}" preload="auto"></audio>
            <div class="audio-control">
                <label>🎶 Other</label>
                <input type="range" id="vol_other" min="0" max="1" step="0.01" value="1">
            </div>
        </div>
        {"<div class='audio-column'>" if model == "htdemucs_6s" else ""}
        {"<audio id='piano' src='" + src_piano + "' preload='auto'></audio>" if model == "htdemucs_6s" else ""}
        {"<div class='audio-control'><label>🎹 Piano</label><input type='range' id='vol_piano' min='0' max='1' step='0.01' value='1'></div>" if model == "htdemucs_6s" else ""}
        {"<audio id='guitar' src='" + src_guitar + "' preload='auto'></audio>" if model == "htdemucs_6s" else ""}
        {"<div class='audio-control'><label>🎸 Guitar</label><input type='range' id='vol_guitar' min='0' max='1' step='0.01' value='1'></div>" if model == "htdemucs_6s" else ""}
        {"</div>" if model == "htdemucs_6s" else ""}
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
    {"const piano = document.getElementById('piano'); const vol_piano = document.getElementById('vol_piano');" if model == "demucs_6s" else ""}
    {"const guitar = document.getElementById('guitar'); const vol_guitar = document.getElementById('vol_guitar');" if model == "demucs_6s" else ""}

    function playAll() {{
        const t = Math.min(vocals.duration || 0, bass.duration || 0, drums.duration || 0, other.duration || 0{", piano.duration || 0, guitar.duration || 0" if model == "demucs_6s" else ""});
        seekbar.max = t;
        vocals.play();
        bass.play();
        drums.play();
        other.play();
        {"piano.play(); guitar.play();" if model == "demucs_6s" else ""}
    }}

    function pauseAll() {{
        vocals.pause();
        bass.pause();
        drums.pause();
        other.pause();
        {"piano.pause(); guitar.pause();" if model == "demucs_6s" else ""}
    }}

    setInterval(() => {{
        if (!vocals.paused && !bass.paused && !drums.paused && !other.paused{"" if model != "demucs_6s" else " && !piano.paused && !guitar.paused"}) {{
            const pos = Math.min(vocals.currentTime, bass.currentTime, drums.currentTime, other.currentTime{", piano.currentTime, guitar.currentTime" if model == "demucs_6s" else ""});
            seekbar.value = pos;
        }}
    }}, 100);

    seekbar.addEventListener("input", () => {{
        vocals.currentTime = seekbar.value;
        bass.currentTime = seekbar.value;
        drums.currentTime = seekbar.value;
        other.currentTime = seekbar.value;
        {"piano.currentTime = seekbar.value; guitar.currentTime = seekbar.value;" if model == "demucs_6s" else ""}
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

    {"vol_piano.addEventListener('input', () => { piano.volume = vol_piano.value; });" if model == "demucs_6s" else ""}
    {"vol_guitar.addEventListener('input', () => { guitar.volume = vol_guitar.value; });" if model == "demucs_6s" else ""}
    </script>
    """
    st.components.v1.html(html_code, height=600 if model == "demucs_6s" else 400)