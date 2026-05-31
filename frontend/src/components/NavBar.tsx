import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "../lib/supabase";

type NavBarProps = {
  showDownload?: boolean;
  onDownload?: () => void;
};

export default function NavBar({ showDownload, onDownload }: NavBarProps) {
  const [menuOpen, setMenuOpen] = useState(false);
  const navigate = useNavigate();
  const menuRef = useRef<HTMLDivElement>(null);

  const handleSignOut = async () => {
    await supabase.auth.signOut();
    navigate("/login", { replace: true });
  };

  return (
    <nav style={{
      background: "var(--surface)",
      borderBottom: "1px solid var(--gray-200)",
      display: "flex",
      alignItems: "center",
      padding: "0 24px",
      height: 64,
      gap: 16,
      position: "sticky",
      top: 0,
      zIndex: 100,
    }}>
      <a href="/upload" style={{ display: "flex", alignItems: "center", gap: 8, fontFamily: "'Google Sans', sans-serif", fontSize: 20, fontWeight: 500, color: "var(--gray-900)", textDecoration: "none" }}>
        <div style={{ width: 32, height: 32, background: "var(--blue)", borderRadius: 8, display: "flex", alignItems: "center", justifyContent: "center" }}>
          <MicIcon />
        </div>
        MeetMind
      </a>

      <a href="/jobs" style={{ marginLeft: 8, padding: "8px 14px", fontFamily: "'Google Sans', sans-serif", fontSize: 14, fontWeight: 500, color: "var(--gray-700)", textDecoration: "none", borderRadius: 6 }}
        onMouseEnter={e => (e.currentTarget.style.background = "var(--gray-100)")}
        onMouseLeave={e => (e.currentTarget.style.background = "transparent")}
      >
        Lịch sử
      </a>

      <div style={{ flex: 1 }} />

      {showDownload && (
        <button onClick={onDownload} style={{ width: 40, height: 40, borderRadius: "50%", border: "none", background: "transparent", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center" }}
          onMouseEnter={e => (e.currentTarget.style.background = "var(--gray-100)")}
          onMouseLeave={e => (e.currentTarget.style.background = "transparent")}
        >
          <svg viewBox="0 0 24 24" width="20" height="20" fill="var(--gray-600)"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z" /></svg>
        </button>
      )}

      {/* Avatar with dropdown */}
      <div style={{ position: "relative" }} ref={menuRef}>
        <div
          onClick={() => setMenuOpen(o => !o)}
          style={{ width: 36, height: 36, borderRadius: "50%", background: "#fbbc04", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "'Google Sans', sans-serif", fontWeight: 500, fontSize: 14, color: "var(--gray-900)", cursor: "pointer", userSelect: "none" }}
        >
          T
        </div>

        {menuOpen && (
          <>
            {/* Backdrop to close on outside click */}
            <div style={{ position: "fixed", inset: 0, zIndex: 99 }} onClick={() => setMenuOpen(false)} />
            <div style={{
              position: "absolute", right: 0, top: 44, zIndex: 100,
              background: "var(--surface)", border: "1px solid var(--gray-200)",
              borderRadius: "var(--radius)", boxShadow: "var(--shadow-2)",
              minWidth: 180, overflow: "hidden",
            }}>
              <button
                onClick={handleSignOut}
                style={{
                  display: "flex", alignItems: "center", gap: 12,
                  width: "100%", padding: "12px 16px",
                  border: "none", background: "transparent",
                  fontFamily: "'Google Sans', sans-serif", fontSize: 14,
                  color: "var(--gray-800)", cursor: "pointer", textAlign: "left",
                }}
                onMouseEnter={e => (e.currentTarget.style.background = "var(--gray-50)")}
                onMouseLeave={e => (e.currentTarget.style.background = "transparent")}
              >
                <svg viewBox="0 0 24 24" width="18" height="18" fill="var(--gray-600)">
                  <path d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5-5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z" />
                </svg>
                Đăng xuất
              </button>
            </div>
          </>
        )}
      </div>
    </nav>
  );
}

function MicIcon() {
  return (
    <svg viewBox="0 0 24 24" width="18" height="18" fill="white">
      <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm-1-9c0-.55.45-1 1-1s1 .45 1 1v6c0 .55-.45 1-1 1s-1-.45-1-1V5zm6 6c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
    </svg>
  );
}
