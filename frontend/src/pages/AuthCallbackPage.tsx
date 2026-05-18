import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "../lib/supabase";

export default function AuthCallbackPage() {
  const navigate = useNavigate();
  const [error, setError] = useState("");

  useEffect(() => {
    supabase.auth.getSession().then(({ data, error }) => {
      if (error || !data.session) {
        setError(error?.message ?? "Xác thực thất bại. Vui lòng thử lại.");
        return;
      }
      navigate("/upload", { replace: true });
    });
  }, [navigate]);

  if (error) {
    return (
      <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "var(--surface)" }}>
        <div style={{ background: "var(--surface)", border: "1px solid var(--gray-200)", borderRadius: "var(--radius-lg)", padding: "48px 40px", textAlign: "center", maxWidth: 360 }}>
          <p style={{ color: "var(--red)", marginBottom: 16, fontSize: 14 }}>{error}</p>
          <a href="/login" style={{ color: "var(--blue)", fontSize: 14, textDecoration: "none" }}>Quay lại đăng nhập</a>
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "var(--surface)" }}>
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 16 }}>
        <svg width="40" height="40" viewBox="0 0 80 80" style={{ transform: "rotate(-90deg)" }}>
          <circle cx="40" cy="40" r="35" fill="none" stroke="var(--gray-200)" strokeWidth="4" />
          <circle cx="40" cy="40" r="35" fill="none" stroke="var(--blue)" strokeWidth="4"
            strokeLinecap="round" strokeDasharray="220"
            style={{ animation: "meetmind-spin 2s linear infinite" }}
          />
        </svg>
        <style>{`@keyframes meetmind-spin { 0% { stroke-dashoffset: 220; } 50% { stroke-dashoffset: 55; } 100% { stroke-dashoffset: 220; } }`}</style>
        <p style={{ fontFamily: "'Google Sans', sans-serif", fontSize: 16, color: "var(--gray-600)" }}>Đang đăng nhập…</p>
      </div>
    </div>
  );
}
