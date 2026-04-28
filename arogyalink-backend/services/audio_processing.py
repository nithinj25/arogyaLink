import io
import struct
import numpy as np
from scipy.signal import butter, sosfilt
from utils.logger import get_logger

logger = get_logger(__name__)

# Telephone speech band — 300 Hz to 3400 Hz.
# Below 300 Hz: rumble, wind, handling noise.
# Above 3400 Hz: hiss, high-frequency interference.
# Twilio phone recordings: mono, 8000 Hz, 16-bit PCM.
SPEECH_LOW_HZ = 300
SPEECH_HIGH_HZ = 3400
FILTER_ORDER = 5


def preprocess_audio(audio_bytes: bytes) -> bytes:
    """
    Two-stage audio cleanup:
      1. Spectral noise reduction — removes stationary background noise
         (fans, traffic, ambient hum) using spectral gating.
      2. Bandpass filter (300–3400 Hz) — strips sub-bass and high-frequency
         content outside the telephone speech band.

    Input/output: raw WAV bytes (LINEAR16, mono, 8000 Hz).
    Returns cleaned WAV bytes ready for Google STT.
    """
    try:
        sample_rate, pcm = _parse_wav(audio_bytes)
        data = pcm.astype(np.float32)

        # Stage 1: spectral noise reduction
        data = _reduce_noise(data, sample_rate)

        # Stage 2: bandpass filter
        data = _bandpass_filter(data, sample_rate)

        # Re-encode to 16-bit PCM WAV
        pcm_out = np.clip(data, -32768, 32767).astype(np.int16)
        return _build_wav(pcm_out, sample_rate)

    except Exception as e:
        # Never block transcription on preprocessing failure
        logger.warning(f"Audio preprocessing failed, using raw audio: {e}")
        return audio_bytes


def _reduce_noise(data: np.ndarray, sample_rate: int) -> np.ndarray:
    """
    Spectral gating noise reduction.
    Uses the first 0.5 s of the recording as the noise profile — this works
    well for IVR calls where the caller hasn't started speaking yet.
    Falls back to non-stationary mode if the clip is too short.
    """
    try:
        import noisereduce as nr
        profile_samples = int(sample_rate * 0.5)
        if len(data) > profile_samples * 2:
            noise_clip = data[:profile_samples]
            return nr.reduce_noise(y=data, sr=sample_rate, y_noise=noise_clip, stationary=True)
        else:
            # Short clip — use non-stationary mode (no explicit noise profile)
            return nr.reduce_noise(y=data, sr=sample_rate, stationary=False)
    except Exception as e:
        logger.warning(f"Noise reduction skipped: {e}")
        return data


def _bandpass_filter(data: np.ndarray, sample_rate: int) -> np.ndarray:
    """
    5th-order Butterworth bandpass filter.
    Keeps only SPEECH_LOW_HZ–SPEECH_HIGH_HZ, attenuates everything outside.
    Uses second-order sections (sosfilt) for numerical stability.
    """
    nyquist = sample_rate / 2.0
    low = SPEECH_LOW_HZ / nyquist
    high = SPEECH_HIGH_HZ / nyquist

    # Clamp to valid range — Nyquist constraint
    high = min(high, 0.99)

    sos = butter(FILTER_ORDER, [low, high], btype="bandpass", output="sos")
    return sosfilt(sos, data)


def _parse_wav(wav_bytes: bytes) -> tuple[int, np.ndarray]:
    """
    Parse WAV bytes without soundfile/pydub dependency.
    Returns (sample_rate, int16 PCM array).
    Handles standard PCM WAV only (what Twilio produces).
    """
    buf = io.BytesIO(wav_bytes)

    # RIFF header
    riff, size, wave = struct.unpack("<4sI4s", buf.read(12))
    if riff != b"RIFF" or wave != b"WAVE":
        raise ValueError("Not a valid WAV file")

    sample_rate = 8000
    num_channels = 1

    while True:
        chunk_header = buf.read(8)
        if len(chunk_header) < 8:
            break
        chunk_id, chunk_size = struct.unpack("<4sI", chunk_header)

        if chunk_id == b"fmt ":
            fmt_data = buf.read(chunk_size)
            audio_fmt, channels, sr = struct.unpack_from("<HHI", fmt_data, 0)
            sample_rate = sr
            num_channels = channels

        elif chunk_id == b"data":
            raw = buf.read(chunk_size)
            pcm = np.frombuffer(raw, dtype=np.int16)
            # Mix down to mono if stereo
            if num_channels == 2:
                pcm = pcm.reshape(-1, 2).mean(axis=1).astype(np.int16)
            return sample_rate, pcm

        else:
            buf.seek(chunk_size, io.SEEK_CUR)

    raise ValueError("WAV data chunk not found")


def _build_wav(pcm: np.ndarray, sample_rate: int) -> bytes:
    """Encode int16 PCM array back to WAV bytes."""
    num_channels = 1
    bits_per_sample = 16
    byte_rate = sample_rate * num_channels * bits_per_sample // 8
    block_align = num_channels * bits_per_sample // 8
    data_size = len(pcm) * 2  # 2 bytes per int16 sample

    buf = io.BytesIO()
    buf.write(b"RIFF")
    buf.write(struct.pack("<I", 36 + data_size))
    buf.write(b"WAVE")
    buf.write(b"fmt ")
    buf.write(struct.pack("<IHHIIHH",
        16,              # fmt chunk size
        1,               # PCM format
        num_channels,
        sample_rate,
        byte_rate,
        block_align,
        bits_per_sample,
    ))
    buf.write(b"data")
    buf.write(struct.pack("<I", data_size))
    buf.write(pcm.tobytes())
    return buf.getvalue()
