import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "../lib/supabase";

export default function AuthCallbackPage() {
  const navigate = useNavigate();
  const [error, setError] = useState("");

  useEffect(() => {
    // Supabase JS automatically exchanges the PKCE code from the URL
    supabase.auth.getSession().then(({ data, error }) => {
      if (error || !data.session) {
        setError(error?.message ?? "Authentication failed. Please try again.");
        return;
      }
      navigate("/upload", { replace: true });
    });
  }, [navigate]);

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="bg-white shadow rounded-2xl p-8 text-center max-w-sm">
          <p className="text-red-500 mb-4">{error}</p>
          <a href="/login" className="text-indigo-600 underline text-sm">Back to login</a>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <p className="text-gray-500">Signing you in…</p>
    </div>
  );
}
