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
        <div style="position: relative; width: 80%; margin: 0 auto;">
            <input type="range" id="seekbar" value="0" min="0" step="0.01" style="width: 100%; z-index: 1; position: relative;">
            <div id="markers" style="position: relative; top: -10px; width: 100%; height: 20px; z-index: 2;">
                <div id="selected-area" style="position: absolute; top: 50%; height: 5px; background-color: green; z-index: -1; border-radius: 5px;"></div>
                <div id="start-marker" draggable="true" style="position: absolute; left: 0; width: 3px; height: 20px; background-color: green; cursor: ew-resize; transform: translateY(-50%);"></div>
                <div id="end-marker" draggable="true" style="position: absolute; right: 0; width: 3px; height: 20px; background-color: green; cursor: ew-resize; transform: translateY(-50%);"></div>
            </div>
        </div>
        <span id="current-time">0:00</span> / <span id="total-time">0:00</span>
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

    const startMarker = document.getElementById("start-marker");
    const endMarker = document.getElementById("end-marker");
    const selectedArea = document.getElementById("selected-area");
    const markersContainer = document.getElementById("markers");

    let seekbarWidth = seekbar.offsetWidth;
    let maxDuration = 0;

    function updateMarkerPosition(marker, position) {{
        const percentage = Math.min(Math.max(position / seekbarWidth, 0), 1);
        marker.style.left = `${{percentage * 100}}%`;
        updateSelectedArea();
        return percentage * maxDuration;
    }}

    function updateSelectedArea() {{
        const startPercentage = parseFloat(startMarker.style.left) || 0;
        const endPercentage = parseFloat(endMarker.style.left) || 100;
        selectedArea.style.left = `${{startPercentage}}%`;
        selectedArea.style.width = `${{endPercentage - startPercentage}}%`;
    }}

    function syncSeekbarToMarker(marker) {{
        const percentage = parseFloat(marker.style.left) / 100;
        seekbar.value = percentage * maxDuration;
        Object.values(audioElements).forEach(audio => {{
            audio.currentTime = seekbar.value;
        }});
    }}

    startMarker.addEventListener("drag", (event) => {{
        if (event.clientX > 0) {{
            const position = event.clientX - markersContainer.getBoundingClientRect().left;
            const time = updateMarkerPosition(startMarker, position);

            // Update currentTime immediately to the marker's position
            Object.values(audioElements).forEach(audio => {{
                audio.currentTime = time; // Update current time
                if (!audio.paused) {{
                    audio.play(); // Resume playback if already playing
                }}
            }});

            seekbar.value = time; // Sync the seekbar to the marker's position
        }}
    }});

    startMarker.addEventListener("dragend", (event) => {{
        if (event.clientX > 0) {{
            const position = event.clientX - markersContainer.getBoundingClientRect().left;
            const time = updateMarkerPosition(startMarker, position);

            // Ensure playback starts at the | marker's position
            Object.values(audioElements).forEach(audio => {{
                audio.currentTime = time; // Set the audio's current time to the marker's position
                audio.play(); // Start playback
            }});

            seekbar.value = time; // Sync the seekbar to the marker's position
        }}
    }});

    endMarker.addEventListener("drag", (event) => {{
        if (event.clientX > 0) {{
            const position = event.clientX - markersContainer.getBoundingClientRect().left;
            updateMarkerPosition(endMarker, position);
        }}
    }});

    function playAll() {{
        maxDuration = Math.min(...Object.values(audioElements).map(audio => audio.duration || 0));
        seekbar.max = maxDuration;
        seekbarWidth = seekbar.offsetWidth;
        updateSelectedArea(); // Ensure the green bar is initialized

        // Start playback from the | marker's position
        const startPercentage = parseFloat(startMarker.style.left) / 100;
        const startTime = startPercentage * maxDuration;

        Object.values(audioElements).forEach(audio => {{
            audio.currentTime = startTime; // Set playback to start marker position
            audio.play();
        }});
        seekbar.value = startTime; // Sync the seekbar to the start marker
    }}

    document.addEventListener("DOMContentLoaded", () => {{
        updateSelectedArea(); // Initialize the green bar on page load

        // Trigger the Play event programmatically
        playAll();
    }});

    function pauseAll() {{
        Object.values(audioElements).forEach(audio => audio.pause());
    }}

    setInterval(() => {{
        if (Object.values(audioElements).every(audio => !audio.paused)) {{
            const pos = Math.min(...Object.values(audioElements).map(audio => audio.currentTime));
            const total = Math.min(...Object.values(audioElements).map(audio => audio.duration || 0));
            seekbar.value = pos;

            // Update current time and total time display
            const formatTime = (time) => {{
                const minutes = Math.floor(time / 60);
                const seconds = Math.floor(time % 60).toString().padStart(2, '0');
                return `${{minutes}}:${{seconds}}`;
            }};
            document.getElementById("current-time").textContent = formatTime(pos);
            document.getElementById("total-time").textContent = formatTime(total);

            // Restart to | marker position if | marker is reached
            const startPercentage = parseFloat(startMarker.style.left) / 100;
            const endPercentage = parseFloat(endMarker.style.left) / 100;
            const startTime = startPercentage * maxDuration;
            const endTime = endPercentage * maxDuration;

            if (pos >= endTime) {{
                Object.values(audioElements).forEach(audio => {{
                    audio.currentTime = startTime;
                    audio.play(); // Ensure playback resumes from the start marker
                }});
                seekbar.value = startTime;
            }}
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
    st.components.v1.html(
        html_code, height=400 if len(stems) > 4 else 310, scrolling=True
    )
