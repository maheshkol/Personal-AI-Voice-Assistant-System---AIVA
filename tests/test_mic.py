"""
AIVA — Microphone Test Script
==============================
Tests microphone input in 3 stages:
  1. List all available audio devices
  2. Record 5 seconds of audio
  3. Play it back so you can hear yourself

Run from your project folder:
    python test_mic.py
"""

import sys
import wave
import tempfile
import os

# ── 1. Check PyAudio is installed ────────────────────────────────────────────
try:
    import pyaudio
    print("✅ PyAudio imported successfully")
except ImportError:
    print("❌ PyAudio not found.")
    print("   Run: pip install PyAudio")
    sys.exit(1)

# ── 2. Check numpy is installed ──────────────────────────────────────────────
try:
    import numpy as np
    print("✅ NumPy imported successfully")
except ImportError:
    print("❌ NumPy not found.")
    print("   Run: pip install numpy")
    sys.exit(1)


# ─────────────────────────────────────────────────────────────────────────────
# SETTINGS — change MIC_INDEX if the wrong mic is selected
# ─────────────────────────────────────────────────────────────────────────────
MIC_INDEX      = None   # None = system default mic. Change to 0,1,2... if needed
RECORD_SECONDS = 5
SAMPLE_RATE    = 16000  # 16kHz — same as Whisper expects
CHANNELS       = 1      # Mono
CHUNK          = 1024
FORMAT         = pyaudio.paInt16


def list_devices(p: pyaudio.PyAudio):
    """Print all audio devices and highlight input devices."""
    print("\n" + "="*55)
    print("  🎤  AVAILABLE AUDIO DEVICES")
    print("="*55)

    found_input = False
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        is_input  = info['maxInputChannels'] > 0
        is_output = info['maxOutputChannels'] > 0
        kind = []
        if is_input:  kind.append("INPUT")
        if is_output: kind.append("output")
        tag = " ← MIC" if is_input else ""
        print(f"  [{i}] {info['name'][:40]:<40} {' | '.join(kind)}{tag}")
        if is_input:
            found_input = True

    print("="*55)

    if not found_input:
        print("❌ No input devices found! Check your mic is connected.")
        sys.exit(1)

    default_input = p.get_default_input_device_info()
    print(f"\n  Default mic: [{default_input['index']}] {default_input['name']}")
    print(f"  Using index: {MIC_INDEX if MIC_INDEX is not None else 'default'}\n")


def record_audio(p: pyaudio.PyAudio) -> bytes:
    """Record RECORD_SECONDS of audio from microphone."""
    print(f"🎙️  Recording for {RECORD_SECONDS} seconds...")
    print("   >>> SPEAK NOW <<<\n")

    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        input_device_index=MIC_INDEX,
        frames_per_buffer=CHUNK
    )

    frames = []
    total_chunks = int(SAMPLE_RATE / CHUNK * RECORD_SECONDS)

    for i in range(total_chunks):
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)

        # Show a simple progress bar
        progress = int((i / total_chunks) * 30)
        bar = "█" * progress + "░" * (30 - progress)
        remaining = RECORD_SECONDS - int(i / total_chunks * RECORD_SECONDS)
        print(f"  [{bar}] {remaining}s remaining", end="\r")

    print(f"\n\n✅ Recording complete!")

    stream.stop_stream()
    stream.close()

    return b"".join(frames)


def check_volume(audio_bytes: bytes) -> bool:
    """Check if audio has actual sound (not silence)."""
    audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32)
    rms = np.sqrt(np.mean(audio_np ** 2))
    peak = np.max(np.abs(audio_np))

    print(f"\n  📊 Audio Analysis:")
    print(f"     RMS volume  : {rms:.1f}  (> 100 is good)")
    print(f"     Peak volume : {peak:.1f}  (> 500 is good)")

    if rms < 50:
        print("\n  ⚠️  Audio is very quiet or silent!")
        print("     → Check mic is not muted")
        print("     → Try a different MIC_INDEX at top of this file")
        return False
    else:
        print("\n  ✅ Audio level looks good!")
        return True


def playback_audio(p: pyaudio.PyAudio, audio_bytes: bytes):
    """Play back the recorded audio."""
    print("\n🔊 Playing back your recording...")

    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        output=True
    )

    chunk_size = 1024
    for i in range(0, len(audio_bytes), chunk_size * 2):
        chunk = audio_bytes[i : i + chunk_size * 2]
        if chunk:
            stream.write(chunk)

    stream.stop_stream()
    stream.close()
    print("✅ Playback complete!\n")


def save_wav(audio_bytes: bytes) -> str:
    """Save audio to a temp WAV file (useful for Whisper testing)."""
    tmp = tempfile.NamedTemporaryFile(
        suffix=".wav", delete=False, prefix="aiva_test_"
    )
    with wave.open(tmp.name, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)          # 16-bit = 2 bytes
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio_bytes)
    return tmp.name


def test_whisper(wav_path: str):
    """Optional: test Whisper transcription on your recording."""
    try:
        import whisper
        print("🧠 Testing Whisper transcription on your recording...")
        model = whisper.load_model("base")
        result = model.transcribe(wav_path)
        print(f"\n  📝 Whisper heard: \"{result['text'].strip()}\"")
        print(f"  🌐 Detected language: {result['language']}")
    except ImportError:
        print("  ℹ️  Whisper not tested (not installed in this env)")
    except Exception as e:
        print(f"  ⚠️  Whisper test failed: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("\n" + "="*55)
    print("  🤖  AIVA — Microphone Test")
    print("="*55)

    p = pyaudio.PyAudio()

    try:
        # Stage 1 — List devices
        list_devices(p)

        input("  Press Enter to start recording...")

        # Stage 2 — Record
        audio_bytes = record_audio(p)

        # Stage 3 — Volume check
        has_sound = check_volume(audio_bytes)

        if has_sound:
            # Stage 4 — Playback
            play = input("\n  Play back your recording? (y/n): ").strip().lower()
            if play == "y":
                playback_audio(p, audio_bytes)

            # Stage 5 — Save WAV + optional Whisper test
            wav_path = save_wav(audio_bytes)
            print(f"  💾 Saved to: {wav_path}")

            test_whisper(wav_path)

            print("\n" + "="*55)
            print("  ✅  Mic test PASSED — your mic is working!")
            print("  You can now run AIVA in voice mode.")
            print("="*55 + "\n")

        else:
            print("\n" + "="*55)
            print("  ❌  Mic test FAILED — no audio detected.")
            print("  Fix suggestions:")
            print("  1. Change MIC_INDEX in this file (try 0, 1, 2...)")
            print("  2. Check Windows mic privacy settings")
            print("  3. Check mic is not muted in system tray")
            print("="*55 + "\n")

    except OSError as e:
        print(f"\n❌ Could not open mic: {e}")
        print("   → Change MIC_INDEX at the top of this file")
        print("   → Valid indexes shown in device list above")

    except KeyboardInterrupt:
        print("\n\n⌨️  Test cancelled.")

    finally:
        p.terminate()


if __name__ == "__main__":
    main()