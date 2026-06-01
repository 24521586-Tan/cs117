import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { supabase } from "../lib/supabase";

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const [loading, setLoading] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      setAuthenticated(!!data.session);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <span className="text-gray-500">Loading…</span>
      </div>
    );
  }

  return authenticated ? <>{children}</> : <Navigate to="/login" replace />;
}
