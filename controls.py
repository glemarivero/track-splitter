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
    gap: 5%;
    margin-top: 5%;
}}
.audio-column {{
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 5%;
    min-width: 45%;
}}
.audio-control {{
    width: 60%;
    margin: 0 auto;
    text-align: center;
}}
input[type="range"] {{
    width: 100%; /* Ensure sliders take full width */
}}
@media (max-width: 768px) {{
    .audio-controls {{
        flex-direction: column;
        gap: 10%;
    }}
    .audio-column {{
        min-width: 100%;
    }}
    .audio-control {{
        width: 90%; /* Adjust control width for smaller screens */
    }}
    input[type="range"] {{
        width: 100%; /* Ensure sliders remain responsive */
    }}
}}
</style>

<div>
    <p style="text-align: left; font-size: 16px; margin-bottom: 20px;">
        Instructions:
        <ul>
            <li>Adjust the volume of individual stems using the sliders.</li>
            <li>Drag the green markers to loop specific sections of the audio.</li>
        </ul>
    </p>
</div>
<div>
    <button onclick="playAll()">▶️ Play</button>
    <button onclick="pauseAll()">⏸️ Pause</button>
</div>

<div style="margin-top: 5%;">
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
let loopStartTime = 0; // Variable to track the latest position for playback start

function initializeAudio() {{
    if (maxDuration === 0) {{
        maxDuration = Math.min(...Object.values(audioElements).map(audio => audio.duration || 0));
        seekbar.max = maxDuration;
        seekbarWidth = seekbar.offsetWidth;
        updateSelectedArea();
        updateTimeDisplay(0);
        loopStartTime = getTimeFromMarker(startMarker); // Ensure loopStartTime is initialized
    }}
}}

// Add event listeners to update duration when metadata is loaded
Object.values(audioElements).forEach(audio => {{
    audio.addEventListener("loadedmetadata", () => {{
        maxDuration = Math.min(...Object.values(audioElements).map(audio => audio.duration || 0));
        seekbar.max = maxDuration;
        updateTimeDisplay(0); // Update the displayed total duration
    }});
}});

function updateTimeDisplay(pos) {{
    const total = Math.min(...Object.values(audioElements).map(audio => audio.duration || 0));
    const formatTime = (time) => {{
        const minutes = Math.floor(time / 60);
        const seconds = Math.floor(time % 60).toString().padStart(2, '0');
        return `${{minutes}}:${{seconds}}`;
    }};
    document.getElementById("current-time").textContent = formatTime(pos);
    document.getElementById("total-time").textContent = formatTime(total);
}}

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

function setAudioPosition(time) {{
    initializeAudio(); // Ensure audio is initialized before setting position
    Object.values(audioElements).forEach(audio => {{
        audio.currentTime = time;
    }});
    seekbar.value = time;
    updateTimeDisplay(time);
}}

function getTimeFromMarker(marker) {{
    const percentage = parseFloat(marker.style.left) / 100;
    return percentage * maxDuration;
}}

function playAll() {{
    maxDuration = Math.min(...Object.values(audioElements).map(audio => audio.duration || 0));
    seekbar.max = maxDuration;
    seekbarWidth = seekbar.offsetWidth;
    updateSelectedArea();

    // Use the latest loopStartTime for playback
    setAudioPosition(loopStartTime);

    Object.values(audioElements).forEach(audio => {{
        audio.play();
    }});
}}

document.addEventListener("DOMContentLoaded", () => {{
    maxDuration = Math.min(...Object.values(audioElements).map(audio => audio.duration || 0));
    seekbar.max = maxDuration;
    seekbarWidth = seekbar.offsetWidth;
    updateSelectedArea();
    updateTimeDisplay(0);

    // Initialize loopStartTime to the position of the start marker
    loopStartTime = getTimeFromMarker(startMarker);
}});

function pauseAll() {{
    Object.values(audioElements).forEach(audio => audio.pause());
}}

// Dragging start marker — update immediately and play from the new position
startMarker.addEventListener("drag", (event) => {{
    if (event.clientX > 0) {{
        initializeAudio(); // Ensure audio is initialized before interacting with markers
        const position = event.clientX - markersContainer.getBoundingClientRect().left;
        loopStartTime = updateMarkerPosition(startMarker, position); // Store start time
        setAudioPosition(loopStartTime); // Update current time
        Object.values(audioElements).forEach(audio => {{
            audio.play(); // Start playing immediately
        }});
    }}
}});

startMarker.addEventListener("dragend", (event) => {{
    if (event.clientX > 0) {{
        initializeAudio(); // Ensure audio is initialized before interacting with markers
        const position = event.clientX - markersContainer.getBoundingClientRect().left;
        loopStartTime = updateMarkerPosition(startMarker, position); // Store start time
        setAudioPosition(loopStartTime); // Update current time
        Object.values(audioElements).forEach(audio => {{
            audio.play(); // Start playing immediately
        }});
    }}
}});

// Add touch support for start marker
startMarker.addEventListener("touchmove", (event) => {{
    const touch = event.touches[0];
    if (touch) {{
        initializeAudio();
        const position = touch.clientX - markersContainer.getBoundingClientRect().left;
        loopStartTime = updateMarkerPosition(startMarker, position);
        setAudioPosition(loopStartTime);
    }}
}});

startMarker.addEventListener("touchstart", (event) => {{
    const touch = event.touches[0];
    if (touch) {{
        initializeAudio();
        const position = touch.clientX - markersContainer.getBoundingClientRect().left;
        loopStartTime = updateMarkerPosition(startMarker, position);
        setAudioPosition(loopStartTime);
    }}
}});

startMarker.addEventListener("touchend", (event) => {{
    const touch = event.changedTouches[0];
    if (touch) {{
        initializeAudio();
        const position = touch.clientX - markersContainer.getBoundingClientRect().left;
        loopStartTime = updateMarkerPosition(startMarker, position);
        setAudioPosition(loopStartTime);
    }}
}});

// Add touch support for end marker
endMarker.addEventListener("drag", (event) => {{
    if (event.clientX > 0) {{
        const position = event.clientX - markersContainer.getBoundingClientRect().left;
        updateMarkerPosition(endMarker, position);
    }}
}});

endMarker.addEventListener("touchmove", (event) => {{
    const touch = event.touches[0];
    if (touch) {{
        const position = touch.clientX - markersContainer.getBoundingClientRect().left;
        updateMarkerPosition(endMarker, position);
    }}
}});

endMarker.addEventListener("touchstart", (event) => {{
    const touch = event.touches[0];
    if (touch) {{
        const position = touch.clientX - markersContainer.getBoundingClientRect().left;
        updateMarkerPosition(endMarker, position);
    }}
}});

endMarker.addEventListener("touchend", (event) => {{
    const touch = event.changedTouches[0];
    if (touch) {{
        const position = touch.clientX - markersContainer.getBoundingClientRect().left;
        updateMarkerPosition(endMarker, position);
    }}
}});

setInterval(() => {{
    if (Object.values(audioElements).every(audio => !audio.paused)) {{
        const pos = Math.min(...Object.values(audioElements).map(audio => audio.currentTime));
        const total = Math.min(...Object.values(audioElements).map(audio => audio.duration || 0));
        seekbar.value = pos;
        updateTimeDisplay(pos);

        const startTime = getTimeFromMarker(startMarker);
        const endTime = getTimeFromMarker(endMarker);

        if (pos >= endTime) {{
            setAudioPosition(startTime);
            Object.values(audioElements).forEach(audio => {{
                audio.play();
            }});
        }}
    }}
}}, 100);

seekbar.addEventListener("input", () => {{
    initializeAudio(); // Ensure audio is initialized before seeking
    setAudioPosition(seekbar.value);
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
