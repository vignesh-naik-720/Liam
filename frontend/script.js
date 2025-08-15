const speakerIcon = document.getElementById("speakerIcon");
const echoStatus = document.getElementById("echoStatus");
const transcriptionText = document.getElementById("transcriptionText");

let mediaRecorder;
let audioChunks = [];
let mediaStream = null;
let sessionId = null;
let isRecording = false;
let autoLoopEnabled = true;
let audioPlayer = new Audio();
let FALLBACK_TEXT = "I'm having trouble connecting right now. Please try again later.";

function ensureSessionId() {
  const params = new URLSearchParams(window.location.search);
  let sid = params.get("session");
  if (!sid) {
    sid = crypto.randomUUID();
    params.set("session", sid);
    history.replaceState(null, "", `${location.pathname}?${params.toString()}`);
  }
  sessionId = sid;
  return sid;
}
ensureSessionId();

function setSpeakerState(state) {
  speakerIcon.classList.remove("idle", "speaking-bot", "speaking-user");
  speakerIcon.classList.add(state);
}

async function startRecordingAuto() {
  try {
    if (!mediaStream) {
      mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    }
    mediaRecorder = new MediaRecorder(mediaStream);
    audioChunks = [];
    mediaRecorder.start();
    isRecording = true;

    setSpeakerState("speaking-user");
    echoStatus.textContent = "Recording...";

    mediaRecorder.ondataavailable = (e) => {
      audioChunks.push(e.data);
    };

    mediaRecorder.onstop = async () => {
      isRecording = false;
      setSpeakerState("idle");
      echoStatus.textContent = "Uploading & processing...";

      const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
      const formData = new FormData();
      formData.append("audio", audioBlob, "recording.webm");

      const endpoint = `/agent/chat/${sessionId}`;

      try {
        const response = await fetch(endpoint, { method: "POST", body: formData });
        const result = await response.json();

        if (result.error) {
          console.warn("Server reported error:", result.error);
          echoStatus.textContent = `Error: ${result.error}`;
          transcriptionText.textContent = result.transcription
            ? `Prompt: ${result.transcription}`
            : "[No transcription]";
        } else {
          transcriptionText.textContent = `Prompt: ${result.transcription || "[No text]"}`;
          echoStatus.textContent = "Chat response received.";
        }

        let audioFiles = result.audio_urls || [];

        // If no TTS audio, but fallback exists
        if (!audioFiles.length && result.fallback_text) {
          console.log("Using fallback:", result.fallback_text);
          transcriptionText.textContent += `\n(Fallback) ${result.fallback_text}`;
          FALLBACK_TEXT = result.fallback_text;
          if (result.audio_urls?.length) {
            audioFiles = result.audio_urls;
          }
        }

        if (audioFiles.length > 0) {
          let idx = 0;
          const playNext = () => {
            if (idx >= audioFiles.length) {
              setSpeakerState("idle");
              echoStatus.textContent = "Assistant audio finished.";
              if (autoLoopEnabled) {
                setTimeout(() => startRecordingAuto().catch(console.error), 350);
              }
              return;
            }
            audioPlayer.src = audioFiles[idx];
            audioPlayer.play()
              .then(() => {
                setSpeakerState("speaking-bot");
                echoStatus.textContent = `Playing assistant audio (${idx + 1}/${audioFiles.length})`;
              })
              .catch(err => {
                console.warn("Playback failed:", err);
                setSpeakerState("idle");
                if (idx === audioFiles.length - 1 && autoLoopEnabled) {
                  setTimeout(() => startRecordingAuto().catch(console.error), 350);
                }
              });
            audioPlayer.onended = () => { idx++; playNext(); };
            audioPlayer.onerror = () => { idx++; playNext(); };
          };
          playNext();
        } else {
          echoStatus.textContent = "No assistant audio returned.";
          // Directly loop if no audio
          if (autoLoopEnabled) {
            setTimeout(() => startRecordingAuto().catch(console.error), 350);
          }
        }
      } catch (err) {
        console.error("Processing failed:", err);
        echoStatus.textContent = "Processing failed — playing fallback.";
        audioPlayer.src = "/fallback.mp3";
        audioPlayer.play()
          .then(() => setSpeakerState("speaking-bot"))
          .catch(console.error);
        audioPlayer.onended = () => {
          setSpeakerState("idle");
          if (autoLoopEnabled) startRecordingAuto().catch(console.error);
        };
        transcriptionText.textContent = FALLBACK_TEXT;
      }
    };
  } catch (err) {
    console.error("Mic error:", err);
    alert("Microphone access is required.");
    setSpeakerState("idle");
  }
}

speakerIcon.addEventListener("click", () => {
  if (isRecording) {
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
      mediaRecorder.stop();
    }
    return;
  }
  if (!isRecording && !audioPlayer.paused) {
    // Interrupt bot and start recording
    audioPlayer.pause();
    audioPlayer.currentTime = 0;
    setSpeakerState("speaking-user");
    startRecordingAuto();
    return;
  }
  startRecordingAuto();
});
