// Browser-side WAV → MP3 transcoder.
// Used to shrink large uploads (Supabase free-tier file caps + Railway memory)
// before they leave the browser. faster-whisper downsamples internally, so
// 96 kbps mono MP3 is plenty for transcription quality.

import lamejs from "@breezystack/lamejs";

const BITRATE_KBPS = 96;
const FRAME_SIZE = 1152;

export async function transcodeWavToMp3(
  file: File,
  onProgress?: (pct: number) => void,
): Promise<File> {
  const buffer = await file.arrayBuffer();

  // Web Audio API decodes any container the browser knows (wav, mp3, mp4, m4a)
  // into raw PCM Float32 samples.
  const AudioCtx = (window.AudioContext ||
    (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext);
  const audioCtx = new AudioCtx();
  let audioBuffer: AudioBuffer;
  try {
    audioBuffer = await audioCtx.decodeAudioData(buffer.slice(0));
  } finally {
    audioCtx.close();
  }

  const channels = Math.min(audioBuffer.numberOfChannels, 2);
  const sampleRate = audioBuffer.sampleRate;
  const encoder = new lamejs.Mp3Encoder(channels, sampleRate, BITRATE_KBPS);

  const left = floatTo16(audioBuffer.getChannelData(0));
  const right = channels === 2 ? floatTo16(audioBuffer.getChannelData(1)) : null;
  const totalSamples = left.length;

  const chunks: Uint8Array[] = [];
  let lastReported = -1;

  for (let i = 0; i < totalSamples; i += FRAME_SIZE) {
    const l = left.subarray(i, i + FRAME_SIZE);
    const r = right ? right.subarray(i, i + FRAME_SIZE) : null;
    const out = r ? encoder.encodeBuffer(l, r) : encoder.encodeBuffer(l);
    if (out.length > 0) chunks.push(out);

    if (onProgress) {
      const pct = Math.floor((i / totalSamples) * 100);
      if (pct !== lastReported && pct % 2 === 0) {
        lastReported = pct;
        onProgress(pct);
      }
    }
  }

  const tail = encoder.flush();
  if (tail.length > 0) chunks.push(tail);
  onProgress?.(100);

  const blob = new Blob(chunks as BlobPart[], { type: "audio/mpeg" });
  const newName = file.name.replace(/\.(wav|m4a|mp4)$/i, ".mp3");
  return new File([blob], newName, { type: "audio/mpeg" });
}

function floatTo16(input: Float32Array): Int16Array {
  const out = new Int16Array(input.length);
  for (let i = 0; i < input.length; i++) {
    const s = Math.max(-1, Math.min(1, input[i]));
    out[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
  }
  return out;
}
