// Single source of truth for English UI error strings.
// Backend HTTPException details remain in Vietnamese; we map by status code
// (plus a few keyword hints) so the UI stays consistently English.

export function mapApiError(status: number, body: unknown): string {
  const detail = readDetail(body);

  if (status === 401) return "Your session has expired. Please sign in again.";
  if (status === 403) return "You don't have permission to perform this action.";
  if (status === 404) return "The requested resource was not found.";
  if (status === 405) {
    return "The server rejected this request. Check that VITE_API_URL points to the backend API, not the web app.";
  }
  if (status === 413 || /too large|quá lớn/i.test(detail)) {
    return "The file is too large.";
  }
  if (status === 422) {
    if (/âm thanh|audio/i.test(detail)) {
      return "Invalid audio file. Only .mp3, .mp4, .m4a, and .wav (up to 60 min) are supported.";
    }
    if (/slide|pdf|trang|page/i.test(detail)) {
      return "Invalid slide file. Only .pdf, .txt, .md, and .json (up to 60 pages) are supported.";
    }
    if (/ít nhất|at least/i.test(detail)) {
      return "Upload at least one file (audio or slide).";
    }
    return "Invalid input. Please check your files and try again.";
  }
  if (status >= 500) return "Server error. Please try again.";
  return detail || `Request failed (HTTP ${status}).`;
}

export function mapNetworkError(err: unknown): string {
  if (err instanceof TypeError && err.message === "Failed to fetch") {
    return "Cannot reach the server. Check your internet connection.";
  }
  return err instanceof Error ? err.message : "Upload failed. Please try again.";
}

function readDetail(body: unknown): string {
  if (!body || typeof body !== "object") return "";
  const b = body as { detail?: unknown; message?: unknown };
  if (typeof b.detail === "string") return b.detail;
  if (Array.isArray(b.detail)) {
    return b.detail
      .map((e: unknown) => (e && typeof e === "object" && "msg" in e ? String((e as { msg: unknown }).msg) : ""))
      .filter(Boolean)
      .join("; ");
  }
  if (typeof b.message === "string") return b.message;
  return "";
}
