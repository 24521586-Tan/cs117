import { useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import NavBar from "../components/NavBar";
import { supabase } from "../lib/supabase";

const API = import.meta.env.VITE_API_URL as string;
const POLL_MS = 3000;

type Segment = { start: number; end: number; text: string };
type Transcript = { segments: Segment[]; language?: string };

function fmt(s: number) {
  const m = Math.floor(s / 60).toString().padStart(2, "0");
  const sec = Math.floor(s % 60).toString().padStart(2, "0");
  return `${m}:${sec}`;
}

const STEPS = [
  "Tải lên Supabase Storage",
  "Tách giọng nói (Diarization)",
  "Chuyển đổi giọng nói → văn bản",
];

export default function JobPage() {
  const { id } = useParams<{ id: string }>();
  const [status, setStatus] = useState<string>("pending");
  const [transcript, setTranscript] = useState<Transcript | null>(null);
  const [elapsed, setElapsed] = useState(0);
  const [error, setError] = useState("");
  const timer = useRef<ReturnType<typeof setInterval> | null>(null);
  const ticker = useRef<ReturnType<typeof setInterval> | null>(null);

  const getToken = async () => {
    const { data } = await supabase.auth.getSession();
    return data.session?.access_token ?? "";
  };

  const fetchStatus = async () => {
    try {
      const token = await getToken();
      const res = await fetch(`${API}/jobs/${id}/status`, { headers: { Authorization: `Bearer ${token}` } });
      if (!res.ok) throw new Error("Lỗi khi kiểm tra trạng thái");
      const data = await res.json();
      setStatus(data.status);

      if (data.status === "done") {
        clearInterval(timer.current!);
        clearInterval(ticker.current!);
        const tRes = await fetch(`${API}/jobs/${id}/transcript`, { headers: { Authorization: `Bearer ${token}` } });
        const tData = await tRes.json();
        setTranscript(tData.transcript);
      } else if (data.status === "failed") {
        clearInterval(timer.current!);
        clearInterval(ticker.current!);
        setError("Phân tích thất bại. Vui lòng thử lại.");
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Lỗi không xác định");
      clearInterval(timer.current!);
      clearInterval(ticker.current!);
    }
  };

  useEffect(() => {
    fetchStatus();
    timer.current = setInterval(fetchStatus, POLL_MS);
    ticker.current = setInterval(() => setElapsed(s => s + 1), 1000);
    return () => { clearInterval(timer.current!); clearInterval(ticker.current!); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const isDone = status === "done";
  const isFailed = status === "failed" || !!error;

  const downloadTranscript = () => {
    if (!transcript) return;
    const text = transcript.segments.map(s => `[${fmt(s.start)} – ${fmt(s.end)}] ${s.text}`).join("\n");
    const blob = new Blob([text], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = `transcript-${id}.txt`; a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <NavBar showDownload={isDone} onDownload={downloadTranscript} />

      {!isDone && !isFailed && <ProcessingView status={status} elapsed={elapsed} />}
      {isFailed && <ErrorView message={error} />}
      {isDone && transcript && <TranscriptView transcript={transcript} jobId={id!} />}
    </div>
  );
}

/* ── Processing view ── */
function ProcessingView({ status, elapsed }: { status: string; elapsed: number }) {
  const stepIndex = status === "processing" ? 2 : 0;
  const m = Math.floor(elapsed / 60);
  const s = elapsed % 60;

  return (
    <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "48px 24px", gap: 32 }}>
      <div style={{ width: "100%", maxWidth: 520, background: "var(--surface)", borderRadius: "var(--radius-lg)", boxShadow: "var(--shadow-1)", padding: "48px 40px", display: "flex", flexDirection: "column", alignItems: "center", gap: 24, textAlign: "center" }}>

        {/* Spinner ring */}
        <svg width="80" height="80" viewBox="0 0 80 80" style={{ transform: "rotate(-90deg)" }}>
          <circle cx="40" cy="40" r="35" fill="none" stroke="var(--gray-200)" strokeWidth="4" />
          <circle cx="40" cy="40" r="35" fill="none" stroke="var(--blue)" strokeWidth="4"
            strokeLinecap="round" strokeDasharray="220"
            style={{ animation: "meetmind-spin 2s linear infinite" }}
          />
        </svg>

        <style>{`
          @keyframes meetmind-spin {
            0%   { stroke-dashoffset: 220; }
            50%  { stroke-dashoffset: 55; }
            100% { stroke-dashoffset: 220; }
          }
          @keyframes meetmind-pulse {
            0%, 100% { box-shadow: 0 0 0 0 rgba(26,115,232,.4); }
            50%       { box-shadow: 0 0 0 6px rgba(26,115,232,0); }
          }
        `}</style>

        <div>
          <div style={{ fontFamily: "'Google Sans', sans-serif", fontSize: 22, fontWeight: 400, color: "var(--gray-900)" }}>Đang phân tích bản ghi âm</div>
          <div style={{ fontSize: 14, color: "var(--gray-600)", marginTop: 8 }}>Thường mất 1–3 phút · Bạn có thể đóng tab, kết quả sẽ gửi qua email</div>
        </div>

        {/* Steps */}
        <div style={{ width: "100%", border: "1px solid var(--gray-200)", borderRadius: "var(--radius)", overflow: "hidden" }}>
          {STEPS.map((label, i) => {
            const done = i < stepIndex;
            const active = i === stepIndex;
            return (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 16, padding: "14px 20px", borderBottom: i < STEPS.length - 1 ? "1px solid var(--gray-200)" : "none", fontSize: 14 }}>
                <div style={{ width: 20, height: 20, borderRadius: "50%", flexShrink: 0, display: "flex", alignItems: "center", justifyContent: "center", background: done ? "var(--green)" : active ? "var(--blue)" : "var(--gray-200)", animation: active ? "meetmind-pulse 1.5s infinite" : "none" }}>
                  {done && <svg viewBox="0 0 24 24" width="12" height="12" fill="white"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" /></svg>}
                  {active && <svg viewBox="0 0 24 24" width="12" height="12" fill="white"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 14.5v-9l6 4.5-6 4.5z" /></svg>}
                </div>
                <span style={{ flex: 1, color: done ? "var(--gray-600)" : active ? "var(--blue)" : "var(--gray-400)", fontWeight: active ? 500 : 400 }}>{label}</span>
                {active && <span style={{ fontSize: 12, color: "var(--gray-600)" }}>{m}:{s.toString().padStart(2, "0")}</span>}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

/* ── Transcript view ── */
function TranscriptView({ transcript, jobId }: { transcript: Transcript; jobId: string }) {
  return (
    <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", padding: "32px 24px", gap: 20, maxWidth: 800, margin: "0 auto", width: "100%" }}>
      {/* Top bar */}
      <div style={{ width: "100%", display: "flex", alignItems: "center", gap: 12 }}>
        <a href="/upload" style={{ width: 40, height: 40, borderRadius: "50%", border: "none", background: "transparent", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", textDecoration: "none" }}
          onMouseEnter={e => (e.currentTarget.style.background = "var(--gray-100)")}
          onMouseLeave={e => (e.currentTarget.style.background = "transparent")}
        >
          <svg viewBox="0 0 24 24" width="20" height="20" fill="var(--gray-600)"><path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z" /></svg>
        </a>
        <div style={{ flex: 1, fontFamily: "'Google Sans', sans-serif", fontSize: 20, fontWeight: 500, color: "var(--gray-900)" }}>
          Job #{jobId.slice(0, 8)}
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 6, padding: "4px 12px", borderRadius: 16, background: "var(--green-light)", color: "var(--green)", fontSize: 12, fontWeight: 500, fontFamily: "'Google Sans', sans-serif" }}>
          <svg viewBox="0 0 24 24" width="14" height="14" fill="var(--green)"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" /></svg>
          Hoàn thành
        </div>
      </div>

      {/* Transcript card */}
      <div style={{ width: "100%", background: "var(--surface)", borderRadius: "var(--radius-lg)", boxShadow: "var(--shadow-1)", overflow: "hidden" }}>
        <div style={{ padding: "16px 24px", borderBottom: "1px solid var(--gray-200)", display: "flex", alignItems: "center", gap: 12 }}>
          <span style={{ fontFamily: "'Google Sans', sans-serif", fontSize: 14, fontWeight: 500, color: "var(--gray-800)", flex: 1 }}>
            Transcript · {transcript.segments.length} đoạn
          </span>
          {transcript.language && (
            <div style={{ padding: "2px 10px", background: "var(--blue-light)", color: "var(--blue)", borderRadius: 12, fontSize: 12, fontWeight: 500 }}>
              {transcript.language}
            </div>
          )}
        </div>

        <div>
          {transcript.segments.map((seg, i) => (
            <div key={i} style={{ display: "flex", gap: 16, padding: "14px 24px", borderBottom: i < transcript.segments.length - 1 ? "1px solid var(--gray-100)" : "none", transition: "background .15s", cursor: "pointer" }}
              onMouseEnter={e => (e.currentTarget.style.background = "var(--gray-50)")}
              onMouseLeave={e => (e.currentTarget.style.background = "transparent")}
            >
              <div style={{ fontFamily: "monospace", fontSize: 12, color: "var(--gray-600)", whiteSpace: "nowrap", paddingTop: 2, minWidth: 110 }}>
                {fmt(seg.start)} – {fmt(seg.end)}
              </div>
              <div style={{ fontSize: 14, color: "var(--gray-900)", lineHeight: 1.6, flex: 1 }}>
                {seg.text}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/* ── Error view ── */
function ErrorView({ message }: { message: string }) {
  return (
    <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", padding: 24 }}>
      <div style={{ background: "var(--surface)", borderRadius: "var(--radius-lg)", boxShadow: "var(--shadow-1)", padding: "40px 48px", textAlign: "center", maxWidth: 400 }}>
        <div style={{ width: 48, height: 48, borderRadius: "50%", background: "var(--red-light)", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 16px" }}>
          <svg viewBox="0 0 24 24" width="24" height="24" fill="var(--red)"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" /></svg>
        </div>
        <p style={{ fontSize: 16, fontFamily: "'Google Sans', sans-serif", color: "var(--gray-900)", marginBottom: 8 }}>Phân tích thất bại</p>
        <p style={{ fontSize: 13, color: "var(--gray-600)", marginBottom: 24 }}>{message}</p>
        <a href="/upload" style={{ display: "inline-flex", padding: "10px 24px", background: "var(--blue)", color: "white", borderRadius: 4, fontFamily: "'Google Sans', sans-serif", fontSize: 14, fontWeight: 500, textDecoration: "none" }}>
          Thử lại
        </a>
      </div>
    </div>
  );
}
