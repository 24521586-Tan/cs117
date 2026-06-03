// Off-main-thread MP3 encoder. Main thread sends Int16 PCM via transferable
// buffers; this worker streams MP3 chunks back as it encodes so memory stays
// bounded and the UI stays responsive.

import lamejs from "@breezystack/lamejs";

const FRAME_SIZE = 1152;
const BITRATE_KBPS = 96;

type InMessage = {
  channels: 1 | 2;
  sampleRate: number;
  left: Int16Array;
  right: Int16Array | null;
};

self.onmessage = (e: MessageEvent<InMessage>) => {
  const { channels, sampleRate, left, right } = e.data;
  try {
    const encoder = new lamejs.Mp3Encoder(channels, sampleRate, BITRATE_KBPS);
    const total = left.length;
    let lastPct = -1;

    for (let i = 0; i < total; i += FRAME_SIZE) {
      const l = left.subarray(i, i + FRAME_SIZE);
      const r = right ? right.subarray(i, i + FRAME_SIZE) : null;
      const out: Uint8Array = r
        ? encoder.encodeBuffer(l, r)
        : encoder.encodeBuffer(l);
      if (out.length > 0) {
        // Copy because subarrays inside lamejs share buffers we want to transfer.
        const chunk = new Uint8Array(out);
        (self as unknown as Worker).postMessage(
          { type: "chunk", chunk },
          [chunk.buffer],
        );
      }
      const pct = Math.floor((i / total) * 100);
      if (pct !== lastPct) {
        lastPct = pct;
        (self as unknown as Worker).postMessage({ type: "progress", pct });
      }
    }

    const tail = encoder.flush();
    if (tail.length > 0) {
      const chunk = new Uint8Array(tail);
      (self as unknown as Worker).postMessage(
        { type: "chunk", chunk },
        [chunk.buffer],
      );
    }
    (self as unknown as Worker).postMessage({ type: "done" });
  } catch (err) {
    (self as unknown as Worker).postMessage({
      type: "error",
      message: err instanceof Error ? err.message : String(err),
    });
  }
};
