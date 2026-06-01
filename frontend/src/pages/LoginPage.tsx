import { supabase } from "../lib/supabase";

export default function LoginPage() {
  const handleGoogleLogin = async () => {
    await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: `${window.location.origin}/auth/callback`,
        scopes: "openid email profile",
      },
    });
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "var(--surface)" }}>
      <div style={{
        width: 360,
        border: "1px solid var(--gray-200)",
        borderRadius: "var(--radius-lg)",
        padding: "48px 40px 36px",
        textAlign: "center",
      }}>
        {/* Logo */}
        <div style={{ width: 48, height: 48, background: "var(--blue)", borderRadius: 12, display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 24px" }}>
          <svg viewBox="0 0 24 24" width="28" height="28" fill="white">
            <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm-1-9c0-.55.45-1 1-1s1 .45 1 1v6c0 .55-.45 1-1 1s-1-.45-1-1V5zm6 6c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
          </svg>
        </div>

        <h1 style={{ fontFamily: "'Google Sans', sans-serif", fontSize: 24, fontWeight: 400, color: "var(--gray-900)", marginBottom: 8 }}>
          Đăng nhập vào MeetMind
        </h1>
        <p style={{ fontSize: 14, color: "var(--gray-600)", marginBottom: 32, lineHeight: 1.5 }}>
          Transcribe cuộc họp của bạn tự động với AI
        </p>

        <button
          onClick={handleGoogleLogin}
          style={{
            display: "flex", alignItems: "center", justifyContent: "center", gap: 12,
            width: "100%", padding: "10px 24px",
            border: "1px solid var(--gray-200)", borderRadius: 4,
            background: "var(--surface)",
            fontFamily: "'Google Sans', sans-serif", fontSize: 14, fontWeight: 500,
            color: "var(--gray-800)", cursor: "pointer",
            transition: "background .2s, box-shadow .2s",
          }}
          onMouseEnter={e => { e.currentTarget.style.background = "var(--gray-50)"; e.currentTarget.style.boxShadow = "var(--shadow-1)"; }}
          onMouseLeave={e => { e.currentTarget.style.background = "var(--surface)"; e.currentTarget.style.boxShadow = "none"; }}
        >
          <GoogleLogo />
          Tiếp tục với Google
        </button>

        <p style={{ marginTop: 24, fontSize: 12, color: "var(--gray-600)" }}>
          Bằng cách đăng nhập, bạn đồng ý với{" "}
          <a href="#" style={{ color: "var(--blue)", textDecoration: "none" }}>Điều khoản dịch vụ</a>
          {" "}và{" "}
          <a href="#" style={{ color: "var(--blue)", textDecoration: "none" }}>Chính sách bảo mật</a>
        </p>
      </div>
    </div>
  );
}

function GoogleLogo() {
  return (
    <svg viewBox="0 0 24 24" width="18" height="18">
      <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
      <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
      <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" />
      <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
    </svg>
  );
}
