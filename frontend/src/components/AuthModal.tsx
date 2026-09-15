import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Icon } from "./Icon";
import {
  loginWithEmail,
  registerWithEmail,
  logout,
  updateProfile,
  getGoogleOAuthUrl,
  getGithubOAuthUrl,
} from "../lib/auth";
import type { User } from "@/types";
import { soundFx } from "../lib/audio";

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentUser: User | null;
  onAuthSuccess: (user: User) => void;
  onLogout: () => void;
}

export function AuthModal({
  isOpen,
  onClose,
  currentUser,
  onAuthSuccess,
  onLogout,
}: AuthModalProps) {
  const [tab, setTab] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Preference editing for logged in user
  const [preferredFormat, setPreferredFormat] = useState(
    currentUser?.preferred_format || "gif"
  );
  const [nsfwEnabled, setNsfwEnabled] = useState(
    currentUser?.nsfw_enabled || false
  );
  const [isSavingPref, setIsSavingPref] = useState(false);

  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleOAuth = async (provider: "google" | "github") => {
    soundFx.playTap();
    setLoading(true);
    setError(null);
    try {
      const url =
        provider === "google"
          ? await getGoogleOAuthUrl()
          : await getGithubOAuthUrl();
      window.location.href = url;
    } catch (err: any) {
      setError(err?.message || `Failed to initiate ${provider} authentication`);
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    soundFx.playTap();
    setError(null);
    setLoading(true);

    try {
      if (tab === "login") {
        const res = await loginWithEmail(email, password);
        soundFx.playSuccess();
        onAuthSuccess(res.user);
        onClose();
      } else {
        const res = await registerWithEmail(email, password, name);
        soundFx.playSuccess();
        onAuthSuccess(res.user);
        onClose();
      }
    } catch (err: any) {
      soundFx.playError();
      setError(err?.message || "Authentication failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleSavePreferences = async (format: string, nsfw: boolean) => {
    setIsSavingPref(true);
    try {
      const updated = await updateProfile({
        preferred_format: format,
        nsfw_enabled: nsfw,
      });
      onAuthSuccess(updated);
      soundFx.playSuccess();
    } catch (e: any) {
      setError(e?.message || "Failed to update preferences");
    } finally {
      setIsSavingPref(false);
    }
  };

  const handleLogoutClick = async () => {
    soundFx.playTap();
    await logout();
    onLogout();
    onClose();
  };

  return (
    <AnimatePresence>
      <div
        className="modal-overlay"
        onClick={onClose}
        style={{
          position: "fixed",
          inset: 0,
          backgroundColor: "rgba(0, 0, 0, 0.72)",
          backdropFilter: "blur(8px)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 9999,
          padding: "20px",
        }}
      >
        <motion.div
          className="auth-modal-card"
          role="dialog"
          aria-modal="true"
          aria-label="User Authentication and Account Settings"
          initial={{ opacity: 0, scale: 0.95, y: 12 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 12 }}
          transition={{ duration: 0.22, ease: [0.16, 1, 0.3, 1] }}
          onClick={(e) => e.stopPropagation()}
          style={{
            width: "100%",
            maxWidth: "460px",
            backgroundColor: "var(--bg-elevated, #16181d)",
            border: "1px solid var(--border, #2d3139)",
            borderRadius: "var(--radius-lg, 16px)",
            padding: "28px",
            boxShadow: "0 24px 48px -12px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.06)",
            color: "var(--text-primary, #f3f4f6)",
            position: "relative",
          }}
        >
          {/* Close Button */}
          <button
            type="button"
            onClick={onClose}
            aria-label="Close authentication modal"
            style={{
              position: "absolute",
              top: "18px",
              right: "18px",
              background: "transparent",
              border: "none",
              color: "var(--text-muted, #9ca3af)",
              cursor: "pointer",
              padding: "4px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              borderRadius: "6px",
            }}
          >
            <Icon name="x" size={18} />
          </button>

          {currentUser ? (
            /* ── Logged-in Profile View ── */
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "16px", marginBottom: "20px" }}>
                <div
                  style={{
                    width: "56px",
                    height: "56px",
                    borderRadius: "50%",
                    background: "linear-gradient(135deg, var(--brand-primary, #6366f1), #a855f7)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: "1.4rem",
                    fontWeight: 700,
                    color: "#ffffff",
                    overflow: "hidden",
                    border: "2px solid rgba(255, 255, 255, 0.15)",
                  }}
                >
                  {currentUser.avatar_url ? (
                    <img
                      src={currentUser.avatar_url}
                      alt={currentUser.name || "Avatar"}
                      style={{ width: "100%", height: "100%", objectFit: "cover" }}
                    />
                  ) : (
                    (currentUser.name?.[0] || currentUser.email[0]).toUpperCase()
                  )}
                </div>
                <div>
                  <h3 style={{ margin: 0, fontSize: "1.2rem", fontWeight: 700 }}>
                    {currentUser.name || "MemeGPT Member"}
                  </h3>
                  <div style={{ fontSize: "0.85rem", color: "var(--text-muted, #9ca3af)", marginTop: "2px" }}>
                    {currentUser.email}
                  </div>
                  <div style={{ marginTop: "6px" }}>
                    <span
                      style={{
                        fontSize: "0.72rem",
                        padding: "3px 8px",
                        borderRadius: "20px",
                        backgroundColor:
                          currentUser.plan === "pro" ? "rgba(99, 102, 241, 0.2)" : "rgba(16, 185, 129, 0.18)",
                        color: currentUser.plan === "pro" ? "#818cf8" : "#34d399",
                        fontWeight: 600,
                        textTransform: "uppercase",
                        letterSpacing: "0.05em",
                      }}
                    >
                      {currentUser.plan || "Free"} Plan
                    </span>
                  </div>
                </div>
              </div>

              {/* Preferences section */}
              <div
                style={{
                  padding: "16px",
                  borderRadius: "var(--radius-md, 12px)",
                  backgroundColor: "var(--bg-card, #1c1f26)",
                  border: "1px solid var(--border-subtle, #282c37)",
                  marginBottom: "20px",
                }}
              >
                <h4 style={{ margin: "0 0 12px 0", fontSize: "0.9rem", color: "var(--text-secondary, #d1d5db)" }}>
                  Personal Preferences
                </h4>

                {/* Default format */}
                <div style={{ marginBottom: "14px" }}>
                  <label style={{ display: "block", fontSize: "0.78rem", color: "var(--text-muted, #9ca3af)", marginBottom: "6px" }}>
                    Preferred Media Format
                  </label>
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "6px" }}>
                    {["gif", "image", "mp4", "webp"].map((fmt) => (
                      <button
                        key={fmt}
                        type="button"
                        onClick={() => {
                          setPreferredFormat(fmt);
                          handleSavePreferences(fmt, nsfwEnabled);
                        }}
                        style={{
                          padding: "6px",
                          borderRadius: "6px",
                          border:
                            preferredFormat === fmt
                              ? "1px solid var(--brand-primary, #6366f1)"
                              : "1px solid var(--border, #2d3139)",
                          backgroundColor:
                            preferredFormat === fmt ? "rgba(99, 102, 241, 0.15)" : "transparent",
                          color: preferredFormat === fmt ? "var(--brand-primary, #6366f1)" : "var(--text-secondary, #d1d5db)",
                          fontSize: "0.78rem",
                          fontWeight: 600,
                          cursor: "pointer",
                          textTransform: "uppercase",
                        }}
                      >
                        {fmt}
                      </button>
                    ))}
                  </div>
                </div>

                {/* NSFW Toggle */}
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                  <div>
                    <div style={{ fontSize: "0.82rem", fontWeight: 500 }}>Include NSFW Memes</div>
                    <div style={{ fontSize: "0.72rem", color: "var(--text-muted, #9ca3af)" }}>
                      Allows mature humor and edgy punchlines
                    </div>
                  </div>
                  <input
                    type="checkbox"
                    checked={nsfwEnabled}
                    onChange={(e) => {
                      const val = e.target.checked;
                      setNsfwEnabled(val);
                      handleSavePreferences(preferredFormat, val);
                    }}
                    style={{ cursor: "pointer", width: "18px", height: "18px" }}
                  />
                </div>
              </div>

              {/* Action buttons */}
              <div style={{ display: "flex", gap: "10px", justifyContent: "flex-end" }}>
                <button
                  type="button"
                  onClick={handleLogoutClick}
                  style={{
                    padding: "8px 16px",
                    borderRadius: "8px",
                    border: "1px solid rgba(239, 68, 68, 0.4)",
                    backgroundColor: "rgba(239, 68, 68, 0.1)",
                    color: "#f87171",
                    fontSize: "0.85rem",
                    fontWeight: 600,
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    gap: "6px",
                  }}
                >
                  <Icon name="logout" size={14} />
                  Log Out
                </button>
              </div>
            </div>
          ) : (
            /* ── Sign In / Register Flow ── */
            <div>
              <div style={{ textAlign: "center", marginBottom: "20px" }}>
                <div
                  style={{
                    width: "44px",
                    height: "44px",
                    margin: "0 auto 12px",
                    borderRadius: "12px",
                    background: "linear-gradient(135deg, var(--brand-primary, #6366f1), #a855f7)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    boxShadow: "0 8px 16px -4px rgba(99, 102, 241, 0.4)",
                  }}
                >
                  <Icon name="sparkles" size={22} color="#ffffff" />
                </div>
                <h3 style={{ margin: 0, fontSize: "1.28rem", fontWeight: 700 }}>
                  {tab === "login" ? "Welcome back to MemeGPT" : "Create your MemeGPT Account"}
                </h3>
                <p style={{ margin: "4px 0 0 0", fontSize: "0.82rem", color: "var(--text-muted, #9ca3af)" }}>
                  Unlock personalized meme recommendations & synced favorites
                </p>
              </div>

              {/* Social Login Buttons */}
              <div style={{ display: "flex", flexDirection: "column", gap: "10px", marginBottom: "18px" }}>
                {/* Google Button */}
                <button
                  type="button"
                  onClick={() => handleOAuth("google")}
                  disabled={loading}
                  style={{
                    width: "100%",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: "10px",
                    padding: "10px",
                    borderRadius: "8px",
                    border: "1px solid var(--border, #2d3139)",
                    backgroundColor: "var(--bg-card, #1c1f26)",
                    color: "var(--text-primary, #f3f4f6)",
                    fontSize: "0.86rem",
                    fontWeight: 600,
                    cursor: "pointer",
                    transition: "all 0.15s ease",
                  }}
                >
                  <svg width="18" height="18" viewBox="0 0 24 24">
                    <path
                      fill="#EA4335"
                      d="M12 5c1.6 0 3 .6 4.1 1.6l3.1-3.1C17.3 1.7 14.8 1 12 1 7.5 1 3.7 3.6 1.9 7.3l3.7 2.9C6.5 7.4 9 5 12 5z"
                    />
                    <path
                      fill="#4285F4"
                      d="M23.5 12.3c0-.8-.1-1.7-.2-2.3H12v4.6h6.5c-.3 1.5-1.1 2.8-2.4 3.7l3.7 2.9c2.2-2 3.7-5 3.7-8.9z"
                    />
                    <path
                      fill="#FBBC05"
                      d="M5.6 14.8c-.2-.7-.4-1.5-.4-2.8s.2-2.1.4-2.8L1.9 6.3C.7 8.7 0 10.3 0 12s.7 3.3 1.9 5.7l3.7-2.9z"
                    />
                    <path
                      fill="#34A853"
                      d="M12 23c3.2 0 6-1.1 8-3l-3.7-2.9c-1.1.7-2.5 1.2-4.3 1.2-3 0-5.5-2.4-6.4-5.2L1.9 16C3.7 19.7 7.5 23 12 23z"
                    />
                  </svg>
                  Continue with Google
                </button>

                {/* GitHub Button */}
                <button
                  type="button"
                  onClick={() => handleOAuth("github")}
                  disabled={loading}
                  style={{
                    width: "100%",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: "10px",
                    padding: "10px",
                    borderRadius: "8px",
                    border: "1px solid var(--border, #2d3139)",
                    backgroundColor: "var(--bg-card, #1c1f26)",
                    color: "var(--text-primary, #f3f4f6)",
                    fontSize: "0.86rem",
                    fontWeight: 600,
                    cursor: "pointer",
                    transition: "all 0.15s ease",
                  }}
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
                  </svg>
                  Continue with GitHub
                </button>
              </div>

              {/* Divider */}
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "10px",
                  margin: "16px 0",
                  color: "var(--text-muted, #9ca3af)",
                  fontSize: "0.76rem",
                }}
              >
                <div style={{ flex: 1, height: "1px", backgroundColor: "var(--border-subtle, #282c37)" }} />
                <span>or with email</span>
                <div style={{ flex: 1, height: "1px", backgroundColor: "var(--border-subtle, #282c37)" }} />
              </div>

              {/* Error Callout */}
              {error && (
                <div
                  style={{
                    padding: "10px 14px",
                    borderRadius: "8px",
                    backgroundColor: "rgba(239, 68, 68, 0.15)",
                    border: "1px solid rgba(239, 68, 68, 0.3)",
                    color: "#fca5a5",
                    fontSize: "0.82rem",
                    marginBottom: "14px",
                  }}
                >
                  {error}
                </div>
              )}

              {/* Tab Selector */}
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr",
                  backgroundColor: "var(--bg-card, #1c1f26)",
                  borderRadius: "8px",
                  padding: "3px",
                  marginBottom: "16px",
                  border: "1px solid var(--border-subtle, #282c37)",
                }}
              >
                <button
                  type="button"
                  onClick={() => {
                    setTab("login");
                    setError(null);
                  }}
                  style={{
                    padding: "7px",
                    borderRadius: "6px",
                    border: "none",
                    backgroundColor: tab === "login" ? "var(--brand-primary, #6366f1)" : "transparent",
                    color: tab === "login" ? "#ffffff" : "var(--text-muted, #9ca3af)",
                    fontSize: "0.82rem",
                    fontWeight: 600,
                    cursor: "pointer",
                    transition: "all 0.15s ease",
                  }}
                >
                  Sign In
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setTab("register");
                    setError(null);
                  }}
                  style={{
                    padding: "7px",
                    borderRadius: "6px",
                    border: "none",
                    backgroundColor: tab === "register" ? "var(--brand-primary, #6366f1)" : "transparent",
                    color: tab === "register" ? "#ffffff" : "var(--text-muted, #9ca3af)",
                    fontSize: "0.82rem",
                    fontWeight: 600,
                    cursor: "pointer",
                    transition: "all 0.15s ease",
                  }}
                >
                  Create Account
                </button>
              </div>

              {/* Email/Password Form */}
              <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                {tab === "register" && (
                  <div>
                    <label style={{ display: "block", fontSize: "0.78rem", color: "var(--text-muted, #9ca3af)", marginBottom: "4px" }}>
                      Your Name
                    </label>
                    <input
                      type="text"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      placeholder="Alex Meme"
                      style={{
                        width: "100%",
                        padding: "10px 12px",
                        borderRadius: "8px",
                        border: "1px solid var(--border, #2d3139)",
                        backgroundColor: "var(--bg-input, #13151a)",
                        color: "var(--text-primary, #f3f4f6)",
                        fontSize: "0.88rem",
                      }}
                    />
                  </div>
                )}

                <div>
                  <label style={{ display: "block", fontSize: "0.78rem", color: "var(--text-muted, #9ca3af)", marginBottom: "4px" }}>
                    Email Address
                  </label>
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@example.com"
                    style={{
                      width: "100%",
                      padding: "10px 12px",
                      borderRadius: "8px",
                      border: "1px solid var(--border, #2d3139)",
                      backgroundColor: "var(--bg-input, #13151a)",
                      color: "var(--text-primary, #f3f4f6)",
                      fontSize: "0.88rem",
                    }}
                  />
                </div>

                <div>
                  <label style={{ display: "block", fontSize: "0.78rem", color: "var(--text-muted, #9ca3af)", marginBottom: "4px" }}>
                    Password
                  </label>
                  <input
                    type="password"
                    required
                    minLength={6}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    style={{
                      width: "100%",
                      padding: "10px 12px",
                      borderRadius: "8px",
                      border: "1px solid var(--border, #2d3139)",
                      backgroundColor: "var(--bg-input, #13151a)",
                      color: "var(--text-primary, #f3f4f6)",
                      fontSize: "0.88rem",
                    }}
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  style={{
                    marginTop: "6px",
                    width: "100%",
                    padding: "11px",
                    borderRadius: "8px",
                    border: "none",
                    background: "linear-gradient(135deg, var(--brand-primary, #6366f1), #4f46e5)",
                    color: "#ffffff",
                    fontSize: "0.92rem",
                    fontWeight: 600,
                    cursor: loading ? "not-allowed" : "pointer",
                    boxShadow: "0 4px 12px rgba(99, 102, 241, 0.35)",
                    transition: "opacity 0.15s ease",
                    opacity: loading ? 0.7 : 1,
                  }}
                >
                  {loading ? "Please wait..." : tab === "login" ? "Sign In" : "Register"}
                </button>
              </form>
            </div>
          )}
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
