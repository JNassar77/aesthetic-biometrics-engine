// App config — both values are public-safe browser values (see .env.example).
export const ENGINE_PROXY_URL = (import.meta.env.VITE_ENGINE_PROXY_URL ?? "").replace(/\/+$/, "");
export const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY ?? "";

/** Returns a human message if required config is missing, else null. */
export function configError(): string | null {
  if (!ENGINE_PROXY_URL) return "VITE_ENGINE_PROXY_URL is not set (see .env.example).";
  if (!SUPABASE_ANON_KEY) return "VITE_SUPABASE_ANON_KEY is not set (see .env.example).";
  return null;
}
