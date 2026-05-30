import { useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import NavBar from "../components/NavBar";
import { supabase } from "../lib/supabase";

const API = import.meta.env.VITE_API_URL as string;
const POLL_MS = 3000;

// Pipeline stages, in order. Index is derived from the job status.
const STEPS = [
  "Tạo bản ghi lời nói (WhisperX)",
  "Phân tích nội dung (Gemini)",
  "Đồng bộ sang Notion",
];

const STATUS_STEP: Record<string, number> = {
  pending: 0,
  transcribing: 0,
  analyzing: 1,
  syncing: 2,
};

export default function JobPage() {
  const { id } = useParams<{ id: string }>();
  const [status, setStatus] = useState<string>("pending");
  const [notionUrl, setNotionUrl] = useState<string | null>(null);
  const [elapsed, setElapsed] = useState(0);
  const [error, setError] = useState("");
  const timer = useRef<ReturnType<typeof setInterval> | null>(null);
  const ticker = useRef<ReturnType<typeof setInterval> | null>(null);

  const getToken = async () => {
    const { data } = await supabase.auth.getSession();
    return data.session?.access_token ?? "";
  };

  const stop = () => {
    clearInterval(timer.current!);
    clearInterval(ticker.current!);
  };

  const fetchStatus = async () => {
    try {
      const token = await getToken();
      const res = await fetch(`${API}/jobs/${id}/status`, { headers: { Authorization: `Bearer ${token}` } });
      if (!res.ok) throw new Error("Lỗi khi kiểm tra trạng thái");
      const data = await res.json();
      setStatus(data.status);

      if (data.status === "done") {
        stop();
        setNotionUrl(data.notion_url ?? null);
      } else if (data.status === "failed") {
        stop();
        setError(data.error || "Phân tích thất bại. Vui lòng thử lại.");
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Lỗi không xác định");
      stop();
    }
  };

  useEffect(() => {
    fetchStatus();
    timer.current = setInterval(fetchStatus, POLL_MS);
    ticker.current = setInterval(() => setElapsed(s => s + 1), 1000);
    return () => stop();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const isDone = status === "done";
  const isFailed = status === "failed" || !!error;

  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <NavBar />

      {!isDone && !isFailed && <ProcessingView status={status} elapsed={elapsed} />}
      {isFailed && <ErrorView message={error} />}
      {isDone && <DoneView notionUrl={notionUrl} jobId={id!} />}
    </div>
  );
}

/* ── Processing view ── */
function ProcessingView({ status, elapsed }: { status: string; elapsed: number }) {
  const stepIndex = STATUS_STEP[status] ?? 0;
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
          <div style={{ fontFamily: "'Google Sans', sans-serif", fontSize: 22, fontWeight: 400, color: "var(--gray-900)" }}>Đang xử lý cuộc họp</div>
          <div style={{ fontSize: 14, color: "var(--gray-600)", marginTop: 8 }}>Có thể mất vài phút với bản ghi dài · Bạn có thể đóng tab</div>
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

/* ── Done view ── */
function DoneView({ notionUrl, jobId }: { notionUrl: string | null; jobId: string }) {
  return (
    <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", padding: 24 }}>
      <div style={{ background: "var(--surface)", borderRadius: "var(--radius-lg)", boxShadow: "var(--shadow-1)", padding: "48px 48px", textAlign: "center", maxWidth: 440 }}>
        <div style={{ width: 56, height: 56, borderRadius: "50%", background: "var(--green-light)", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 20px" }}>
          <svg viewBox="0 0 24 24" width="30" height="30" fill="var(--green)"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" /></svg>
        </div>
        <p style={{ fontSize: 20, fontFamily: "'Google Sans', sans-serif", color: "var(--gray-900)", marginBottom: 8 }}>Hoàn thành!</p>
        <p style={{ fontSize: 14, color: "var(--gray-600)", marginBottom: 28 }}>
          Trang ghi chú (Tóm tắt + To-do) đã được tạo trên Notion · Job #{jobId.slice(0, 8)}
        </p>
        {notionUrl ? (
          <a href={notionUrl} target="_blank" rel="noopener noreferrer"
            style={{ display: "inline-flex", alignItems: "center", gap: 8, padding: "12px 28px", background: "var(--blue)", color: "white", borderRadius: 4, fontFamily: "'Google Sans', sans-serif", fontSize: 14, fontWeight: 500, textDecoration: "none" }}>
            Mở trang Notion
            <svg viewBox="0 0 24 24" width="16" height="16" fill="white"><path d="M19 19H5V5h7V3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2v-7h-2v7zM14 3v2h3.59l-9.83 9.83 1.41 1.41L19 6.41V10h2V3h-7z" /></svg>
          </a>
        ) : (
          <p style={{ fontSize: 13, color: "var(--gray-600)" }}>Không tìm thấy link Notion (kiểm tra cấu hình NOTION_*).</p>
        )}
        <div style={{ marginTop: 24 }}>
          <a href="/upload" style={{ fontSize: 13, color: "var(--blue)", textDecoration: "none" }}>← Tải lên cuộc họp khác</a>
        </div>
      </div>
    </div>
  );
}

/* ── Error view ── */
function ErrorView({ message }: { message: string }) {
  return (
    <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", padding: 24 }}>
      <div style={{ background: "var(--surface)", borderRadius: "var(--radius-lg)", boxShadow: "var(--shadow-1)", padding: "40px 48px", textAlign: "center", maxWidth: 440 }}>
        <div style={{ width: 48, height: 48, borderRadius: "50%", background: "var(--red-light)", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 16px" }}>
          <svg viewBox="0 0 24 24" width="24" height="24" fill="var(--red)"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" /></svg>
        </div>
        <p style={{ fontSize: 16, fontFamily: "'Google Sans', sans-serif", color: "var(--gray-900)", marginBottom: 8 }}>Phân tích thất bại</p>
        <p style={{ fontSize: 13, color: "var(--gray-600)", marginBottom: 24, wordBreak: "break-word" }}>{message}</p>
        <a href="/upload" style={{ display: "inline-flex", padding: "10px 24px", background: "var(--blue)", color: "white", borderRadius: 4, fontFamily: "'Google Sans', sans-serif", fontSize: 14, fontWeight: 500, textDecoration: "none" }}>
          Thử lại
        </a>
      </div>
    </div>
  );
}
