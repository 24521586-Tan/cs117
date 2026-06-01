import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import NavBar from "../components/NavBar";
import { supabase } from "../lib/supabase";

const API = import.meta.env.VITE_API_URL as string;
const ALLOWED_AUDIO = ["audio/mpeg", "audio/mp4", "audio/x-m4a", "audio/m4a", "audio/wav", "audio/x-wav", "audio/wave"];

function formatSize(bytes: number) {
  return (bytes / 1024 / 1024).toFixed(1) + " MB";
}

export default function UploadPage() {
  const [dragging, setDragging] = useState(false);
  const [audio, setAudio] = useState<File | null>(null);
  const [pdf, setPdf] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const audioInput = useRef<HTMLInputElement>(null);
  const pdfInput = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const handleAudio = (f: File) => {
    if (!ALLOWED_AUDIO.includes(f.type)) {
      setError("Âm thanh chỉ hỗ trợ .mp3, .m4a hoặc .wav.");
      return;
    }
    setError("");
    setAudio(f);
  };

  const handlePdf = (f: File) => {
    if (f.type !== "application/pdf") {
      setError("Slide phải là file .pdf.");
      return;
    }
    setError("");
    setPdf(f);
  };

  const handleUpload = async () => {
    if (!audio && !pdf) return;
    setUploading(true);
    setError("");

    const { data: sessionData } = await supabase.auth.getSession();
    const token = sessionData.session?.access_token;
    if (!token) { setError("Phiên đăng nhập hết hạn."); setUploading(false); return; }

    const form = new FormData();
    if (audio) form.append("file", audio);
    if (pdf) form.append("slides", pdf);

    try {
      const res = await fetch(`${API}/upload`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: form,
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail ?? "Upload thất bại");
      }
      const { job_id } = await res.json();
      navigate(`/jobs/${job_id}`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Upload thất bại");
      setUploading(false);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <NavBar />

      <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", padding: "48px 24px", gap: 24 }}>
        {/* Header */}
        <div style={{ textAlign: "center", maxWidth: 560 }}>
          <h2 style={{ fontFamily: "'Google Sans', sans-serif", fontSize: 28, fontWeight: 400, color: "var(--gray-900)", marginBottom: 8 }}>
            Tải lên cuộc họp
          </h2>
          <p style={{ fontSize: 14, color: "var(--gray-600)" }}>
            Ghi âm (.mp3 / .m4a / .wav · tối đa 60 phút) và/hoặc slide (.pdf · tối đa 50 trang) · Tiếng Anh
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
              {audio ? audio.name : "Ghi âm cuộc họp"}
            </div>
            <div style={{ fontSize: 13, color: "var(--gray-600)" }}>
              {audio ? `${formatSize(audio.size)} · Đã chọn` : <span>Kéo thả hoặc <span style={{ color: "var(--blue)" }}>chọn file âm thanh</span></span>}
            </div>
            <input ref={audioInput} type="file" accept=".mp3,.m4a,.wav,audio/mpeg,audio/mp4,audio/x-m4a,audio/wav" style={{ display: "none" }} onChange={e => e.target.files?.[0] && handleAudio(e.target.files[0])} />
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
                {pdf ? pdf.name : "Slide trình chiếu (.pdf)"}
              </div>
              <div style={{ fontSize: 13, color: "var(--gray-600)" }}>
                {pdf ? `${formatSize(pdf.size)} · Đã chọn` : "Bấm để chọn file PDF"}
              </div>
            </div>
            <input ref={pdfInput} type="file" accept=".pdf,application/pdf" style={{ display: "none" }} onChange={e => e.target.files?.[0] && handlePdf(e.target.files[0])} />
          </div>

          {error && <p style={{ fontSize: 13, color: "var(--red)" }}>{error}</p>}

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
            {uploading ? "Đang tải lên…" : "Bắt đầu phân tích"}
          </button>
        </div>
      </div>
    </div>
  );
}
