// Direct browser → Supabase Storage upload using a signed upload URL minted
// by the backend. Bypasses the Railway request-body limit and avoids holding
// the audio in backend RAM.

import { supabase } from "./supabase";

const BUCKET = "audio-files";

export async function uploadToSignedUrl(
  path: string,
  token: string,
  file: File,
): Promise<void> {
  const { error } = await supabase.storage
    .from(BUCKET)
    .uploadToSignedUrl(path, token, file, {
      contentType: file.type || "application/octet-stream",
      upsert: true,
    });
  if (error) {
    const message = error.message || "Storage upload failed.";
    if (/payload|too large|413/i.test(message)) {
      throw new Error("Storage rejected the file: it exceeds the bucket size limit.");
    }
    throw new Error(message);
  }
}
