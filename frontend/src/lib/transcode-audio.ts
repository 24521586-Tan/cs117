// Browser-side WAV/M4A/MP4 → MP3 transcoder.
//
// Decoding (hardware-accelerated) runs on the main thread; the heavy lamejs
// encode loop runs in a worker so the page stays responsive. Audio is downmixed
// to mono to roughly halve in-flight memory (a 60-min stereo WAV at 44.1 kHz
// decodes to ~300 MB of Float32 — mono drops that to ~150 MB).

import TranscodeWorker from "./transcode-audio.worker?worker";

const SAFE_DECODE_BYTES = 200 * 1024 * 1024;  // ~200 MB raw — Web Audio will refuse anything close to the tab heap limit

export async function transcodeWavToMp3(
  file: File,
  onProgress?: (pct: number) => void,
): Promise<File> {
  if (file.size > SAFE_DECODE_BYTES) {
    throw new Error("Audio file is too large to compress in the browser.");
  }

  const arrayBuffer = await file.arrayBuffer();

  // Decode container → raw PCM via Web Audio.
  const AudioCtx =
    window.AudioContext ||
    (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
  const audioCtx = new AudioCtx();
  let audioBuffer: AudioBuffer;
  try {
    audioBuffer = await audioCtx.decodeAudioData(arrayBuffer);
  } finally {
    audioCtx.close();
  }

  // Downmix to mono and convert to Int16.
  const sampleRate = audioBuffer.sampleRate;
  const left = pcmToInt16(downmixToMono(audioBuffer));
  const right: Int16Array | null = null;

  // Encode in a worker so the main thread keeps painting.
  return new Promise<File>((resolve, reject) => {
    const worker = new TranscodeWorker();
    const chunks: Uint8Array[] = [];

    worker.onmessage = (e: MessageEvent<{ type: string; pct?: number; chunk?: Uint8Array; message?: string }>) => {
      const msg = e.data;
      if (msg.type === "chunk" && msg.chunk) {
        chunks.push(msg.chunk);
      } else if (msg.type === "progress" && typeof msg.pct === "number") {
        onProgress?.(msg.pct);
      } else if (msg.type === "done") {
        onProgress?.(100);
        worker.terminate();
        const blob = new Blob(chunks as BlobPart[], { type: "audio/mpeg" });
        const newName = file.name.replace(/\.(wav|m4a|mp4)$/i, ".mp3");
        resolve(new File([blob], newName, { type: "audio/mpeg" }));
      } else if (msg.type === "error") {
        worker.terminate();
        reject(new Error(msg.message || "Audio compression failed."));
      }
    };

    worker.onerror = (e) => {
      worker.terminate();
      reject(new Error(e.message || "Audio compression worker crashed."));
    };

    // Transfer the PCM buffer to the worker (zero-copy).
    worker.postMessage(
      { channels: 1, sampleRate, left, right },
      [left.buffer],
    );
  });
}

function downmixToMono(buffer: AudioBuffer): Float32Array {
  if (buffer.numberOfChannels === 1) return buffer.getChannelData(0);
  const l = buffer.getChannelData(0);
  const r = buffer.getChannelData(1);
  const out = new Float32Array(l.length);
  for (let i = 0; i < l.length; i++) out[i] = (l[i] + r[i]) * 0.5;
  return out;
}

function pcmToInt16(input: Float32Array): Int16Array {
  const out = new Int16Array(input.length);
  for (let i = 0; i < input.length; i++) {
    const s = Math.max(-1, Math.min(1, input[i]));
    out[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
  }
  return out;
}
