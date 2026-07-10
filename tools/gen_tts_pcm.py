#!/usr/bin/env python3
"""Generate raw PCM audio (24000Hz, 16-bit signed mono).
Usage:
  python gen_tts_pcm.py <text> <output.pcm>   # TTS from text
  python gen_tts_pcm.py --alarm <output.pcm>   # alarm beeps
Supports: edge-tts > gtts+ffmpeg > pyttsx3 (Windows), auto-resamples to 24000Hz.
"""
import sys, os, struct, math, wave, tempfile, subprocess, array


def _resample_to_24000(wav_path, dst_rate=24000):
    """Read WAV, return 24000Hz 16-bit mono raw PCM bytes."""
    with wave.open(wav_path, "rb") as w:
        src_rate = w.getframerate()
        sw = w.getsampwidth()
        channels = w.getnchannels()
        src = w.readframes(w.getnframes())

    if sw == 2:
        samples = array.array('h', src)
    elif sw == 1:
        samples = array.array('h', [(b - 128) << 8 for b in src])
    else:
        raise ValueError(f"unsupported sample width {sw}")

    if channels > 1:
        mono = array.array('h', [0]) * (len(samples) // channels)
        for i in range(len(mono)):
            mono[i] = samples[i * channels]
        samples = mono

    GAIN = 4.0

    if src_rate == dst_rate:
        out = array.array('h', [max(-32768, min(32767, int(s * GAIN))) for s in samples])
        return out.tobytes()

    src_len = len(samples)
    dst_len = int(src_len * dst_rate / src_rate)
    ratio = src_len / dst_len
    out = array.array('h', [0]) * dst_len
    for i in range(dst_len):
        p = i * ratio
        idx = int(p)
        frac = p - idx
        if idx + 1 < src_len:
            v = samples[idx] * (1 - frac) + samples[idx + 1] * frac
        else:
            v = samples[idx]
        out[i] = max(-32768, min(32767, int(v * GAIN)))
    return out.tobytes()


def _gen_alarm(output):
    """Generate 3 beeps at 1200Hz, 200ms each, 100ms gap, max volume."""
    sr = 24000
    beep_len = sr * 200 // 1000
    gap_len = sr * 100 // 1000
    total = 3 * (beep_len + gap_len)
    buf = array.array('h', [0]) * total
    pos = 0
    for _ in range(3):
        for i in range(beep_len):
            buf[pos] = int(30000 * math.sin(2 * math.pi * 1200 * (pos % beep_len) / sr))
            pos += 1
        for _ in range(gap_len):
            buf[pos] = 0
            pos += 1
    with open(output, "wb") as f:
        buf.tofile(f)
    return True


def _edge_tts(text, output):
    import asyncio, edge_tts
    asyncio.run(edge_tts.Communicate(text, "zh-CN-XiaoxiaoNeural").save_raw(output))
    return os.path.getsize(output) > 100


def _gtts(text, output):
    from gtts import gTTS
    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    tmp.close()
    try:
        gTTS(text, lang="zh-cn").save(tmp.name)
        subprocess.run([
            "ffmpeg", "-y", "-i", tmp.name,
            "-acodec", "pcm_s16le", "-f", "s16le",
            "-ac", "1", "-ar", "24000", output,
        ], check=True, capture_output=True)
        return os.path.getsize(output) > 100
    finally:
        os.unlink(tmp.name)


def _pyttsx3(text, output):
    import pyttsx3
    wav = output + ".wav"
    engine = pyttsx3.init()
    engine.save_to_file(text, wav)
    engine.runAndWait()
    pcm = _resample_to_24000(wav, dst_rate=24000)
    with open(output, "wb") as f:
        f.write(pcm)
    os.unlink(wav)
    return os.path.getsize(output) > 100


BACKENDS = [
    ("edge-tts", _edge_tts),
    ("gtts+ffmpeg", _gtts),
    ("pyttsx3", _pyttsx3),
]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python gen_tts_pcm.py <text> <output.pcm>   # TTS from text")
        print("  python gen_tts_pcm.py --alarm <output.pcm>  # alarm beeps")
        sys.exit(1)

    if sys.argv[1] == "--alarm":
        output = sys.argv[2]
        _gen_alarm(output)
        sz = os.path.getsize(output)
        dur = sz / 2 / 24000
        print(f"OK: {output} ({sz} bytes, {dur:.2f}s, alarm beeps)")
        sys.exit(0)

    text = sys.argv[1]
    output = sys.argv[2]

    for name, func in BACKENDS:
        try:
            if func(text, output):
                sz = os.path.getsize(output)
                dur = sz / 2 / 24000
                print(f"OK: {output} ({sz} bytes, {dur:.2f}s, via {name})")
                sys.exit(0)
        except ImportError:
            continue
        except Exception as e:
            print(f"  {name} failed: {e}")
            continue

    print(f"WARN: no TTS backend, generating 880Hz beep for '{text}'")
    with open(output, "wb") as f:
        for i in range(int(24000 * 0.3)):
            v = int(16000 * math.sin(2 * math.pi * 880 * i / 24000))
            f.write(struct.pack("<h", v))
