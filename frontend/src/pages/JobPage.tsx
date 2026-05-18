import { useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { supabase } from "../lib/supabase";

const API = import.meta.env.VITE_API_URL as string;
const POLL_INTERVAL_MS = 3000;

type Segment = { start: number; end: number; text: string };
type Transcript = { segments: Segment[]; language?: string };

function formatTime(secs: number) {
  const m = Math.floor(secs / 60).toString().padStart(2, "0");
  const s = Math.floor(secs % 60).toString().padStart(2, "0");
  return `${m}:${s}`;
}

export default function JobPage() {
  const { id } = useParams<{ id: string }>();
  const [status, setStatus] = useState<string>("pending");
  const [transcript, setTranscript] = useState<Transcript | null>(null);
  const [error, setError] = useState("");
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const getToken = async () => {
    const { data } = await supabase.auth.getSession();
    return data.session?.access_token ?? "";
  };

  const fetchStatus = async () => {
    try {
      const token = await getToken();
      const res = await fetch(`${API}/jobs/${id}/status`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error("Failed to fetch status");
      const data = await res.json();
      setStatus(data.status);

      if (data.status === "done") {
        clearInterval(timerRef.current!);
        const tRes = await fetch(`${API}/jobs/${id}/transcript`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const tData = await tRes.json();
        setTranscript(tData.transcript);
      } else if (data.status === "failed") {
        clearInterval(timerRef.current!);
        setError("Transcription failed. Please try again.");
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Unknown error");
      clearInterval(timerRef.current!);
    }
  };

  useEffect(() => {
    fetchStatus();
    timerRef.current = setInterval(fetchStatus, POLL_INTERVAL_MS);
    return () => clearInterval(timerRef.current!);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  return (
    <div className="flex flex-col items-center min-h-screen bg-gray-50 py-12 px-4 gap-6">
      <div className="bg-white shadow rounded-2xl p-8 w-full max-w-2xl flex flex-col gap-4">
        <h1 className="text-xl font-semibold text-gray-800">Transcription Job</h1>
        <p className="text-xs text-gray-400 font-mono break-all">{id}</p>

        {/* Status badge */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-600">Status:</span>
          <StatusBadge status={status} />
        </div>

        {/* Loading spinner while processing */}
        {(status === "pending" || status === "processing") && (
          <div className="flex items-center gap-3 text-gray-500 text-sm">
            <svg className="animate-spin h-4 w-4 text-indigo-500" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
            </svg>
            Polling every 3 s…
          </div>
        )}

        {error && <p className="text-red-500 text-sm">{error}</p>}

        {/* Transcript */}
        {transcript && (
          <div className="mt-4 flex flex-col gap-2">
            <h2 className="font-medium text-gray-700">
              Transcript {transcript.language ? `(${transcript.language})` : ""}
            </h2>
            <div className="bg-gray-50 rounded-xl p-4 flex flex-col gap-2 max-h-[60vh] overflow-y-auto">
              {transcript.segments.map((seg, i) => (
                <div key={i} className="flex gap-3 text-sm">
                  <span className="text-gray-400 font-mono shrink-0 w-20">
                    {formatTime(seg.start)} – {formatTime(seg.end)}
                  </span>
                  <span className="text-gray-800">{seg.text}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, string> = {
    pending: "bg-yellow-100 text-yellow-700",
    processing: "bg-blue-100 text-blue-700",
    done: "bg-green-100 text-green-700",
    failed: "bg-red-100 text-red-700",
  };
  return (
    <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${map[status] ?? "bg-gray-100 text-gray-600"}`}>
      {status}
    </span>
  );
}
