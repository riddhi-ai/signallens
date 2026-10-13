/// <reference types="vite/client" />

// Only public, browser-visible configuration belongs here. Never add a secret with a VITE_ prefix.
interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string
}
