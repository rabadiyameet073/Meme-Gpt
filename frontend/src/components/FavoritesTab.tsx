import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { api, getSessionId, type MemeRecord } from "../api";
import { MemeCard } from "./MemeCard";
import { Icon, type IconName } from "./Icon";
import {
  loadUserData,
  createCustomCollection,
  deleteCustomCollection,
  type LocalStorageSchema,
} from "../lib/storage";

const SESSION_ID = getSessionId();

export function FavoritesTab({ onToast }: { onToast: (m: string) => void }) {
  const [userData, setUserData] = useState<LocalStorageSchema>(loadUserData());
  const [selectedCollection, setSelectedCollection] = useState<string>("Favorites");
  const [newCollectionName, setNewCollectionName] = useState<string>("");
  const [showAddModal, setShowAddModal] = useState<boolean>(false);
  const [apiFavs, setApiFavs] = useState<MemeRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const refreshData = async () => {
    const local = loadUserData();
    setUserData(local);
    try {
      const serverData = await api.favorites(SESSION_ID);
      setApiFavs(serverData || []);
    } catch {
      /* Fallback to local storage */
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshData();
  }, []);

  const handleCreateCollection = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCollectionName.trim()) return;
    const ok = createCustomCollection(newCollectionName.trim());
    if (ok) {
      onToast(`Created collection "${newCollectionName.trim()}"`);
      setNewCollectionName("");
      setShowAddModal(false);
      refreshData();
    } else {
      onToast("Collection already exists or invalid name");
    }
  };

  const handleDeleteCollection = (name: string) => {
    if (name === "Favorites") return;
    if (window.confirm(`Delete collection "${name}"? Memes will move to Favorites.`)) {
      deleteCustomCollection(name);
      onToast(`Deleted "${name}"`);
      setSelectedCollection("Favorites");
      refreshData();
    }
  };

  let displayedMemes: any[] = [];
  if (selectedCollection === "Recently Viewed") {
    displayedMemes = (userData.recentlyViewed || []).map((m) => ({
      id: m.memeId,
      name: m.name,
      category: "recent",
      dialogue: m.name,
      explanation: "Recently viewed",
      formats: { image: m.thumbnailUrl },
      preview_url: m.thumbnailUrl,
    }));
  } else if (selectedCollection === "Recently Copied") {
    displayedMemes = (userData.recentlyCopied || []).map((m) => ({
      id: m.memeId,
      name: m.name,
      category: "copied",
      dialogue: m.name,
      explanation: "Recently copied",
      formats: { image: m.thumbnailUrl },
      preview_url: m.thumbnailUrl,
    }));
  } else {
    const localMatches = userData.favorites.filter((f) => f.collection === selectedCollection);
    if (localMatches.length > 0) {
      displayedMemes = localMatches.map((m) => ({
        id: m.memeId,
        name: m.name,
        category: m.collection.toLowerCase(),
        dialogue: m.name,
        explanation: `Saved to ${m.collection}`,
        formats: { image: m.thumbnailUrl },
        preview_url: m.thumbnailUrl,
      }));
    } else if (selectedCollection === "Favorites" && apiFavs.length > 0) {
      displayedMemes = apiFavs;
    }
  }

  const collectionsList: { name: string; icon: IconName; count: number }[] = [
    {
      name: "Favorites",
      icon: "heart-filled",
      count: userData.favorites.filter((f) => f.collection === "Favorites").length || apiFavs.length,
    },
    { name: "Recently Viewed", icon: "clock", count: (userData.recentlyViewed || []).length },
    { name: "Recently Copied", icon: "copy", count: (userData.recentlyCopied || []).length },
    ...userData.collections
      .filter((c) => c.name !== "Favorites")
      .map((c) => ({
        name: c.name,
        icon: "tag" as IconName,
        count: userData.favorites.filter((f) => f.collection === c.name).length,
      })),
  ];

  return (
    <div style={{ maxWidth: "1200px", margin: "0 auto" }}>
      {/* Header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "12px",
          marginBottom: "20px",
        }}
      >
        <div>
          <h2 style={{ fontSize: "1.4rem", fontWeight: 700, display: "flex", alignItems: "center", gap: "8px" }}>
            <Icon name="heart" size={22} color="var(--accent-rose)" />
            Saved Memes & Collections
          </h2>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.88rem", marginTop: "4px" }}>
            Your personal library of bookmarked reaction templates and history
          </p>
        </div>

        <button
          type="button"
          className="btn btn-secondary"
          onClick={() => setShowAddModal(true)}
          style={{ fontSize: "0.82rem" }}
        >
          <Icon name="plus" size={14} color="var(--brand-primary)" />
          New Collection
        </button>
      </div>

      {/* Collection Chips Bar */}
      <div className="chips-carousel" style={{ marginBottom: "24px" }}>
        {collectionsList.map((col) => {
          const isSelected = selectedCollection === col.name;
          return (
            <button
              key={col.name}
              type="button"
              onClick={() => setSelectedCollection(col.name)}
              className={`chip-btn ${isSelected ? "active" : ""}`}
            >
              <Icon
                name={col.icon}
                size={14}
                color={isSelected ? "var(--brand-primary)" : col.name === "Favorites" ? "var(--accent-rose)" : "var(--text-muted)"}
              />
              <span>{col.name}</span>
              <span style={{ opacity: 0.7, fontSize: "0.75rem", fontFamily: "var(--font-mono)" }}>({col.count})</span>
              {isSelected && !["Favorites", "Recently Viewed", "Recently Copied"].includes(col.name) && (
                <span
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteCollection(col.name);
                  }}
                  title="Delete collection"
                  style={{ marginLeft: "4px", opacity: 0.7 }}
                >
                  <Icon name="trash" size={12} />
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Loading Skeleton */}
      {loading ? (
        <div className="card-grid">
          {[1, 2, 3].map((n) => (
            <div
              key={n}
              style={{
                height: "300px",
                borderRadius: "var(--radius-md)",
                backgroundColor: "var(--bg-card)",
                border: "1px solid var(--border-subtle)",
              }}
            />
          ))}
        </div>
      ) : displayedMemes.length === 0 ? (
        /* Empty State */
        <div
          style={{
            textAlign: "center",
            padding: "60px 20px",
            backgroundColor: "var(--bg-card)",
            borderRadius: "var(--radius-md)",
            border: "1px solid var(--border)",
          }}
        >
          <div
            style={{
              width: "48px",
              height: "48px",
              borderRadius: "var(--radius-sm)",
              backgroundColor: "rgba(244, 63, 94, 0.1)",
              color: "var(--accent-rose)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              margin: "0 auto 16px",
            }}
          >
            <Icon name="heart" size={24} />
          </div>
          <h3 style={{ fontSize: "1.15rem", marginBottom: "6px" }}>No saved memes in this collection</h3>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.88rem", maxWidth: "380px", margin: "0 auto" }}>
            Click the heart icon on any meme card while searching or browsing to save it here for instant access.
          </p>
        </div>
      ) : (
        /* Saved Memes Grid */
        <div className="card-grid">
          {displayedMemes.map((m) => (
            <MemeCard key={m.id} meme={m} isFav onToast={onToast} onToggleFav={refreshData} />
          ))}
        </div>
      )}

      {/* Add Collection Modal */}
      <AnimatePresence>
        {showAddModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            style={{
              position: "fixed",
              inset: 0,
              backgroundColor: "var(--bg-overlay)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              zIndex: 100,
              padding: "20px",
            }}
            onClick={() => setShowAddModal(false)}
          >
            <motion.div
              initial={{ scale: 0.96, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.96, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              style={{
                backgroundColor: "var(--bg-panel)",
                border: "1px solid var(--border)",
                borderRadius: "var(--radius-md)",
                padding: "24px",
                width: "100%",
                maxWidth: "400px",
                boxShadow: "var(--shadow-lg)",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
                <h3 style={{ fontSize: "1.15rem", fontWeight: 700 }}>Create New Collection</h3>
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  style={{ background: "transparent", border: "none", color: "var(--text-muted)", cursor: "pointer" }}
                >
                  <Icon name="x" size={16} />
                </button>
              </div>

              <form onSubmit={handleCreateCollection}>
                <div style={{ marginBottom: "18px" }}>
                  <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "6px" }}>
                    Collection Name
                  </label>
                  <input
                    type="text"
                    value={newCollectionName}
                    onChange={(e) => setNewCollectionName(e.target.value)}
                    placeholder="e.g. Work Chaos, Meeting Reactions"
                    autoFocus
                    style={{
                      width: "100%",
                      padding: "10px 12px",
                      backgroundColor: "var(--bg-input)",
                      border: "1px solid var(--border)",
                      borderRadius: "var(--radius-sm)",
                      color: "var(--text-primary)",
                      fontFamily: "var(--font-body)",
                      outline: "none",
                    }}
                  />
                </div>

                <div style={{ display: "flex", justifyContent: "flex-end", gap: "8px" }}>
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => setShowAddModal(false)}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={!newCollectionName.trim()}
                  >
                    Create
                  </button>
                </div>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
