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
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 gap-6">
      <div className="bg-white shadow rounded-2xl p-10 flex flex-col items-center gap-6 w-full max-w-sm">
        <h1 className="text-2xl font-semibold text-gray-800">MeetMind</h1>
        <p className="text-gray-500 text-sm text-center">
          AI-powered meeting transcription. Sign in to get started.
        </p>
        <button
          onClick={handleGoogleLogin}
          className="flex items-center gap-3 bg-white border border-gray-300 text-gray-700 px-5 py-2.5 rounded-lg shadow-sm hover:bg-gray-50 transition w-full justify-center font-medium"
        >
          <img
            src="https://www.svgrepo.com/show/475656/google-color.svg"
            alt="Google"
            className="w-5 h-5"
          />
          Sign in with Google
        </button>
      </div>
    </div>
  );
}
