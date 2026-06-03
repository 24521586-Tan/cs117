import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import NavBar from "../components/NavBar";
import { supabase } from "../lib/supabase";
import { mapApiError, mapNetworkError } from "../lib/error-messages";
import { transcodeWavToMp3 } from "../lib/transcode-audio";
import { uploadToSignedUrl } from "../lib/direct-upload";

const API = import.meta.env.VITE_API_URL as string;
const ALLOWED_AUDIO_EXTS = [".mp3", ".mp4", ".m4a", ".wav"];
const ALLOWED_AUDIO_TYPES = ["audio/mpeg", "audio/mp4", "audio/x-m4a", "audio/m4a", "audio/wav", "audio/x-wav", "audio/wave", "video/mp4"];
const ALLOWED_SLIDE_EXTS = [".pdf", ".txt", ".md", ".json"];
const ALLOWED_SLIDE_TYPES = ["application/pdf", "text/plain", "text/markdown", "text/x-markdown", "application/json"];
const MAX_AUDIO_MINUTES = 60;
// Audio files above this size get re-encoded to MP3 in the browser before upload.
const TRANSCODE_THRESHOLD_BYTES = 30 * 1024 * 1024;

function extOf(name: string): string {
  const i = name.lastIndexOf(".");
  return i >= 0 ? name.slice(i).toLowerCase() : "";
}

function formatSize(bytes: number) {
  return (bytes / 1024 / 1024).toFixed(1) + " MB";
}

export default function UploadPage() {
  const [dragging, setDragging] = useState(false);
  const [audio, setAudio] = useState<File | null>(null);
  const [pdf, setPdf] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [stage, setStage] = useState("");
  const [transcodePct, setTranscodePct] = useState(0);
  const [error, setError] = useState("");
  const audioInput = useRef<HTMLInputElement>(null);
  const pdfInput = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const handleAudio = (f: File) => {
    const ext = extOf(f.name);
    const typeOk = ALLOWED_AUDIO_TYPES.includes(f.type);
    const extOk = ALLOWED_AUDIO_EXTS.includes(ext);
    if (!typeOk && !extOk) {
      setError("Audio must be .mp3, .mp4, .m4a, or .wav.");
      return;
    }
    // Check audio duration using HTML5 Audio API
    const url = URL.createObjectURL(f);
    const tempAudio = new Audio(url);
    tempAudio.addEventListener("loadedmetadata", () => {
      URL.revokeObjectURL(url);
      const durationMin = tempAudio.duration / 60;
      if (durationMin > MAX_AUDIO_MINUTES) {
        setError(`Audio is ${Math.round(durationMin)} minutes long, exceeding the ${MAX_AUDIO_MINUTES}-minute limit.`);
        return;
      }
      setError("");
      setAudio(f);
    });
    tempAudio.addEventListener("error", () => {
      URL.revokeObjectURL(url);
      // Cannot read duration — accept file, backend will re-check
      setError("");
      setAudio(f);
    });
  };

  const handlePdf = (f: File) => {
    const ext = extOf(f.name);
    const typeOk = ALLOWED_SLIDE_TYPES.includes(f.type);
    const extOk = ALLOWED_SLIDE_EXTS.includes(ext);
    if (!typeOk && !extOk) {
      setError("Slide must be .pdf, .txt, .md, or .json.");
      return;
    }
    setError("");
    setPdf(f);
  };

  const resetUpload = () => {
    setUploading(false);
    setStage("");
    setTranscodePct(0);
  };

  const handleUpload = async () => {
    if (!audio && !pdf) return;
    setUploading(true);
    setError("");

    try {
      // ── Phase A: shrink oversized WAV/M4A in the browser ──
      let audioToUpload = audio;
      const needsTranscode =
        audio &&
        audio.size > TRANSCODE_THRESHOLD_BYTES &&
        /\.(wav|m4a|mp4)$/i.test(audio.name);

      if (needsTranscode && audio) {
        setStage(`Compressing audio (${formatSize(audio.size)})…`);
        setTranscodePct(0);
        audioToUpload = await transcodeWavToMp3(audio, setTranscodePct);
      }

      // ── Phase B1: init — get signed upload URLs ──
      setStage("Preparing upload…");
      const { data: sessionData } = await supabase.auth.getSession();
      const token = sessionData.session?.access_token;
      if (!token) throw new Error("Your session has expired.");

      const initRes = await fetch(`${API}/upload/init`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          audio_filename: audioToUpload?.name,
          audio_size: audioToUpload?.size,
          slide_filename: pdf?.name,
          slide_size: pdf?.size,
        }),
      });
      if (!initRes.ok) {
        let body: unknown = null;
        try { body = await initRes.json(); } catch { /* ignore */ }
        throw new Error(mapApiError(initRes.status, body));
      }
      const init: {
        job_id: string;
        audio: { path: string; token: string } | null;
        slide: { path: string; token: string } | null;
      } = await initRes.json();

      // ── Phase B2: direct upload to Supabase Storage ──
      setStage("Uploading…");
      const uploads: Promise<void>[] = [];
      if (init.audio && audioToUpload) {
        uploads.push(uploadToSignedUrl(init.audio.path, init.audio.token, audioToUpload));
      }
      if (init.slide && pdf) {
        uploads.push(uploadToSignedUrl(init.slide.path, init.slide.token, pdf));
      }
      await Promise.all(uploads);

      // ── Phase B3: complete — kick off the pipeline ──
      setStage("Starting analysis…");
      const completeRes = await fetch(`${API}/upload/complete`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ job_id: init.job_id }),
      });
      if (!completeRes.ok) {
        let body: unknown = null;
        try { body = await completeRes.json(); } catch { /* ignore */ }
        throw new Error(mapApiError(completeRes.status, body));
      }

      navigate(`/jobs/${init.job_id}`);
    } catch (err: unknown) {
      setError(mapNetworkError(err));
      resetUpload();
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <NavBar />

      <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", padding: "48px 24px", gap: 24 }}>
        {/* Header */}
        <div style={{ textAlign: "center", maxWidth: 560 }}>
          <h2 style={{ fontFamily: "'Google Sans', sans-serif", fontSize: 28, fontWeight: 400, color: "var(--gray-900)", marginBottom: 8 }}>
            Upload a meeting
          </h2>
          <p style={{ fontSize: 14, color: "var(--gray-600)" }}>
            Audio (.mp3 / .mp4 / .m4a / .wav · up to 60 min) and/or slides (.pdf / .txt / .md / .json · up to 60 pages) · English
          </p>
        </div>

        {/* Card */}
        <div style={{ width: "100%", maxWidth: 600, background: "var(--surface)", borderRadius: "var(--radius-lg)", boxShadow: "var(--shadow-1)", padding: 32, display: "flex", flexDirection: "column", gap: 24 }}>

          {/* Audio drop zone */}
          <div
            onClick={() => audioInput.current?.click()}
            onDragOver={e => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={e => { e.preventDefault(); setDragging(false); e.dataTransfer.files[0] && handleAudio(e.dataTransfer.files[0]); }}
            style={{
              border: `2px dashed ${audio ? "var(--green)" : dragging ? "var(--blue)" : "var(--gray-400)"}`,
              borderRadius: "var(--radius)",
              padding: "40px 24px",
              textAlign: "center",
              cursor: "pointer",
              background: audio ? "var(--green-light)" : dragging ? "var(--blue-light)" : "transparent",
              transition: "border-color .2s, background .2s",
              display: "flex", flexDirection: "column", alignItems: "center", gap: 12,
            }}
          >
            <div style={{ width: 56, height: 56, borderRadius: "50%", background: audio ? "var(--green-light)" : "var(--gray-100)", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <svg viewBox="0 0 24 24" width="28" height="28" fill={audio ? "var(--green)" : "var(--gray-600)"}>
                <path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z" />
              </svg>
            </div>
            <div style={{ fontFamily: "'Google Sans', sans-serif", fontSize: 16, fontWeight: 500, color: "var(--gray-900)" }}>
              {audio ? audio.name : "Meeting recording"}
            </div>
            <div style={{ fontSize: 13, color: "var(--gray-600)" }}>
              {audio ? `${formatSize(audio.size)} · Selected` : <span>Drag and drop or <span style={{ color: "var(--blue)" }}>choose an audio file</span></span>}
            </div>
            <input ref={audioInput} type="file" accept=".mp3,.mp4,.m4a,.wav,audio/mpeg,audio/mp4,audio/x-m4a,audio/wav,video/mp4" style={{ display: "none" }} onChange={e => e.target.files?.[0] && handleAudio(e.target.files[0])} />
          </div>

          {/* PDF picker */}
          <div
            onClick={() => pdfInput.current?.click()}
            style={{
              border: `2px dashed ${pdf ? "var(--green)" : "var(--gray-400)"}`,
              borderRadius: "var(--radius)",
              padding: "24px",
              cursor: "pointer",
              background: pdf ? "var(--green-light)" : "transparent",
              display: "flex", alignItems: "center", gap: 16,
            }}
          >
            <div style={{ width: 44, height: 44, borderRadius: 8, background: pdf ? "var(--green-light)" : "var(--gray-100)", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
              <svg viewBox="0 0 24 24" width="22" height="22" fill={pdf ? "var(--green)" : "var(--gray-600)"}>
                <path d="M6 2c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6H6zm7 7V3.5L18.5 9H13z" />
              </svg>
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontFamily: "'Google Sans', sans-serif", fontSize: 15, fontWeight: 500, color: "var(--gray-900)" }}>
                {pdf ? pdf.name : "Slides (.pdf / .txt / .md / .json)"}
              </div>
              <div style={{ fontSize: 13, color: "var(--gray-600)" }}>
                {pdf ? `${formatSize(pdf.size)} · Selected` : "Click to choose a slide file"}
              </div>
            </div>
            <input ref={pdfInput} type="file" accept=".pdf,.txt,.md,.json,application/pdf,text/plain,text/markdown,application/json" style={{ display: "none" }} onChange={e => e.target.files?.[0] && handlePdf(e.target.files[0])} />
          </div>

          {error && (
            <div style={{
              background: "var(--red-light, #fce8e6)",
              border: "1px solid var(--red, #d93025)",
              borderRadius: "var(--radius, 8px)",
              padding: "12px 16px",
              display: "flex",
              alignItems: "flex-start",
              gap: 10,
            }}>
              <svg viewBox="0 0 24 24" width="20" height="20" fill="var(--red, #d93025)" style={{ flexShrink: 0, marginTop: 1 }}>
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
              </svg>
              <div style={{ fontSize: 13, color: "var(--red, #d93025)", lineHeight: 1.5 }}>
                {error.split("\n").map((line, i) => (
                  <div key={i}>{error.includes("\n") ? `• ${line}` : line}</div>
                ))}
              </div>
            </div>
          )}

          {/* Stage indicator (compress/upload progress) */}
          {uploading && stage && (
            <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
              <div style={{ fontSize: 13, color: "var(--gray-700)" }}>
                {stage}{stage.startsWith("Compressing") && transcodePct > 0 ? ` ${transcodePct}%` : ""}
              </div>
              {stage.startsWith("Compressing") && (
                <div style={{ height: 4, width: "100%", background: "var(--gray-200)", borderRadius: 999, overflow: "hidden" }}>
                  <div style={{ height: "100%", width: `${transcodePct}%`, background: "var(--blue)", borderRadius: 999, transition: "width .2s" }} />
                </div>
              )}
            </div>
          )}

          {/* Submit */}
          <button
            disabled={(!audio && !pdf) || uploading}
            onClick={handleUpload}
            style={{
              display: "flex", alignItems: "center", justifyContent: "center", gap: 8,
              padding: "10px 24px", width: "100%",
              background: (!audio && !pdf) || uploading ? "var(--gray-400)" : "var(--blue)",
              color: "white", border: "none", borderRadius: 4,
              fontFamily: "'Google Sans', sans-serif", fontSize: 14, fontWeight: 500,
              cursor: (!audio && !pdf) || uploading ? "not-allowed" : "pointer",
              transition: "background .2s",
            }}
          >
            {uploading ? (stage || "Uploading…") : "Start analysis"}
          </button>
        </div>
      </div>
    </div>
  );
}
