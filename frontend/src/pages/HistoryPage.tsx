import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import NavBar from "../components/NavBar";
import { supabase } from "../lib/supabase";
import { mapApiError, mapNetworkError } from "../lib/error-messages";

const API = import.meta.env.VITE_API_URL as string;

type Job = {
  job_id: string;
  status: string;
  progress: number;
  notion_url: string | null;
  error: string | null;
  created_at: string | null;
  title: string | null;
};

const STATUS_LABEL: Record<string, string> = {
  pending: "Pending",
  transcribing: "Transcribing",
  analyzing: "Analyzing",
  syncing: "Syncing to Notion",
  done: "Done",
  failed: "Failed",
};

const TERMINAL = new Set(["done", "failed"]);
const isActive = (s: string) => !TERMINAL.has(s);

function badgeColors(status: string): { bg: string; fg: string } {
  if (status === "done") return { bg: "var(--green-light)", fg: "var(--green)" };
  if (status === "failed") return { bg: "var(--red-light)", fg: "var(--red)" };
  return { bg: "var(--blue-light)", fg: "var(--blue)" };
}

function formatDate(iso: string | null): string {
  if (!iso) return "";
  const d = new Date(iso);
  if (isNaN(d.getTime())) return "";
  return d.toLocaleString("en-US", { day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit" });
}

export default function HistoryPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const fetchJobs = async () => {
    try {
      const { data } = await supabase.auth.getSession();
      const token = data.session?.access_token ?? "";
      const res = await fetch(`${API}/jobs`, { headers: { Authorization: `Bearer ${token}` } });
      if (!res.ok) {
        let body: unknown = null;
        try { body = await res.json(); } catch { /* ignore */ }
        throw new Error(mapApiError(res.status, body));
      }
      const body = await res.json();
      setJobs(body.jobs ?? []);
      setError("");
    } catch (e: unknown) {
      setError(mapNetworkError(e));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
    // Refresh periodically so in-progress jobs update without a manual reload.
    const t = setInterval(fetchJobs, 5000);
    return () => clearInterval(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <NavBar />

      <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", padding: "40px 24px" }}>
        <div style={{ width: "100%", maxWidth: 720 }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 24 }}>
            <h2 style={{ fontFamily: "'Google Sans', sans-serif", fontSize: 26, fontWeight: 400, color: "var(--gray-900)" }}>
              Meeting history
            </h2>
            <a href="/upload" style={{ display: "inline-flex", alignItems: "center", gap: 8, padding: "10px 20px", background: "var(--blue)", color: "white", borderRadius: 4, fontFamily: "'Google Sans', sans-serif", fontSize: 14, fontWeight: 500, textDecoration: "none" }}>
              + New meeting
            </a>
          </div>

          {loading && <p style={{ color: "var(--gray-600)", fontSize: 14 }}>Loading…</p>}
          {error && <p style={{ color: "var(--red)", fontSize: 14 }}>{error}</p>}

          {!loading && !error && jobs.length === 0 && (
            <div style={{ background: "var(--surface)", borderRadius: "var(--radius-lg)", boxShadow: "var(--shadow-1)", padding: "48px 24px", textAlign: "center" }}>
              <p style={{ fontSize: 15, color: "var(--gray-600)", marginBottom: 16 }}>No meetings yet.</p>
              <a href="/upload" style={{ color: "var(--blue)", fontSize: 14, textDecoration: "none" }}>Upload your first meeting →</a>
            </div>
          )}

          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {jobs.map(job => {
              const c = badgeColors(job.status);
              const active = isActive(job.status);
              const label = STATUS_LABEL[job.status] ?? job.status;
              return (
                <div
                  key={job.job_id}
                  onClick={() => navigate(`/jobs/${job.job_id}`)}
                  style={{ background: "var(--surface)", borderRadius: "var(--radius)", boxShadow: "var(--shadow-1)", padding: "16px 20px", display: "flex", alignItems: "center", gap: 16, cursor: "pointer", border: "1px solid var(--gray-200)" }}
                  onMouseEnter={e => (e.currentTarget.style.background = "var(--gray-50)")}
                  onMouseLeave={e => (e.currentTarget.style.background = "var(--surface)")}
                >
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontFamily: "'Google Sans', sans-serif", fontSize: 15, color: "var(--gray-900)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                      {job.title || `Meeting #${job.job_id.slice(0, 8)}`}
                    </div>
                    <div style={{ fontSize: 12, color: "var(--gray-600)", marginTop: 4 }}>
                      {formatDate(job.created_at)}
                      {active && job.status === "transcribing" && ` · ${job.progress}%`}
                    </div>
                  </div>

                  <span style={{ flexShrink: 0, fontSize: 12, fontWeight: 500, padding: "4px 12px", borderRadius: 999, background: c.bg, color: c.fg }}>
                    {label}
                  </span>

                  {job.status === "done" && job.notion_url ? (
                    <a href={job.notion_url} target="_blank" rel="noopener noreferrer" onClick={e => e.stopPropagation()}
                      style={{ flexShrink: 0, fontSize: 13, color: "var(--blue)", textDecoration: "none", fontWeight: 500 }}>
                      Open Notion ↗
                    </a>
                  ) : (
                    <span style={{ flexShrink: 0, fontSize: 13, color: "var(--gray-400)" }}>
                      {active ? "View progress →" : "Details →"}
                    </span>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
