import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./index.css";

// Optional Sentry setup
const sentryDsn = (import.meta as any).env?.VITE_SENTRY_DSN;
if (sentryDsn && typeof window !== "undefined" && (window as any).Sentry) {
  (window as any).Sentry.init({
    dsn: sentryDsn,
    tracesSampleRate: 0.1,
    environment: (import.meta as any).env?.MODE,
  });
}

// Register Service Worker for PWA
if (typeof window !== "undefined" && "serviceWorker" in navigator && import.meta.env.PROD) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/sw.js").catch(() => {});
  });
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>
);

