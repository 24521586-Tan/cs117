import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import NavBar from "../components/NavBar";
import { supabase } from "../lib/supabase";

const API = import.meta.env.VITE_API_URL as string;
const ALLOWED = ["audio/mpeg", "audio/mp4", "audio/x-m4a", "audio/m4a"];

function formatSize(bytes: number) {
  return (bytes / 1024 / 1024).toFixed(1) + " MB";
}

export default function UploadPage() {
  const [dragging, setDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const handleFile = (f: File) => {
    if (!ALLOWED.includes(f.type)) {
      setError("Chỉ hỗ trợ định dạng .mp3 hoặc .m4a.");
      return;
    }
    setError("");
    setFile(f);
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError("");

    const { data: sessionData } = await supabase.auth.getSession();
    const token = sessionData.session?.access_token;
    if (!token) { setError("Phiên đăng nhập hết hạn."); setUploading(false); return; }

    const form = new FormData();
    form.append("file", file);

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
            Tải lên bản ghi âm cuộc họp
          </h2>
          <p style={{ fontSize: 14, color: "var(--gray-600)" }}>
            Hỗ trợ định dạng .mp3 và .m4a · Tối đa 60 phút · Tiếng Việt &amp; Tiếng Anh
          </p>
        </div>

        {/* Card */}
        <div style={{ width: "100%", maxWidth: 600, background: "var(--surface)", borderRadius: "var(--radius-lg)", boxShadow: "var(--shadow-1)", padding: 32, display: "flex", flexDirection: "column", gap: 24 }}>

          {/* Drop zone */}
          <div
            onClick={() => inputRef.current?.click()}
            onDragOver={e => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={e => { e.preventDefault(); setDragging(false); e.dataTransfer.files[0] && handleFile(e.dataTransfer.files[0]); }}
            style={{
              border: `2px dashed ${file ? "var(--green)" : dragging ? "var(--blue)" : "var(--gray-400)"}`,
              borderRadius: "var(--radius)",
              padding: "48px 24px",
              textAlign: "center",
              cursor: "pointer",
              background: file ? "var(--green-light)" : dragging ? "var(--blue-light)" : "transparent",
              transition: "border-color .2s, background .2s",
              display: "flex", flexDirection: "column", alignItems: "center", gap: 12,
            }}
          >
            <div style={{ width: 56, height: 56, borderRadius: "50%", background: file ? "var(--green-light)" : "var(--gray-100)", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <svg viewBox="0 0 24 24" width="28" height="28" fill={file ? "var(--green)" : "var(--gray-600)"}>
                <path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM14 13v4h-4v-4H7l5-5 5 5h-3z" />
              </svg>
            </div>
            <div style={{ fontFamily: "'Google Sans', sans-serif", fontSize: 16, fontWeight: 500, color: "var(--gray-900)" }}>
              {file ? file.name : "Kéo thả file vào đây"}
            </div>
            <div style={{ fontSize: 13, color: "var(--gray-600)" }}>
              {file ? `${formatSize(file.size)} · Đã chọn` : <span>hoặc <span style={{ color: "var(--blue)" }}>chọn từ máy tính</span></span>}
            </div>
            <input ref={inputRef} type="file" accept=".mp3,.m4a,audio/mpeg,audio/mp4,audio/x-m4a" style={{ display: "none" }} onChange={e => e.target.files?.[0] && handleFile(e.target.files[0])} />
          </div>

          {/* File badge */}
          {file && (
            <div style={{ display: "flex", alignItems: "center", gap: 12, padding: "12px 16px", background: "var(--gray-100)", borderRadius: "var(--radius)" }}>
              <div style={{ width: 36, height: 36, background: "var(--blue-light)", borderRadius: 6, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                <svg viewBox="0 0 24 24" width="20" height="20" fill="var(--blue)"><path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z" /></svg>
              </div>
              <div style={{ flex: 1, fontSize: 14, fontWeight: 500, color: "var(--gray-900)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{file.name}</div>
              <div style={{ fontSize: 12, color: "var(--gray-600)", flexShrink: 0 }}>{formatSize(file.size)}</div>
            </div>
          )}

          {error && <p style={{ fontSize: 13, color: "var(--red)" }}>{error}</p>}

          {/* Submit */}
          <button
            disabled={!file || uploading}
            onClick={handleUpload}
            style={{
              display: "flex", alignItems: "center", justifyContent: "center", gap: 8,
              padding: "10px 24px", width: "100%",
              background: !file || uploading ? "var(--gray-400)" : "var(--blue)",
              color: "white", border: "none", borderRadius: 4,
              fontFamily: "'Google Sans', sans-serif", fontSize: 14, fontWeight: 500,
              cursor: !file || uploading ? "not-allowed" : "pointer",
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
