/// <reference types="vitest/config" />
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: { port: 5173, host: true },
  preview: { port: 4173, host: true },
  test: {
    environment: "node",
    // Deterministic config for tests (so they don't depend on a local .env).
    env: {
      VITE_ENGINE_PROXY_URL: "https://proxy.test/functions/v1/engine-proxy",
      VITE_SUPABASE_ANON_KEY: "test-anon-key",
    },
  },
});
