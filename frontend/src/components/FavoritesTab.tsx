import { useState, useEffect } from "react";
import { api, getSessionId, type MemeRecord } from "../api";
import { MemeCard } from "./MemeCard";
import { Icon } from "./Icon";
import {
  loadUserData,
  createCustomCollection,
  deleteCustomCollection,
  removeSavedMeme,
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
      setApiFavs(serverData);
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
      onToast(`Deleted "${name}", memes moved to Favorites`);
      setSelectedCollection("Favorites");
      refreshData();
    }
  };

  // Determine displayed memes based on active tab
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
    // Custom or Favorites
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

  if (loading) {
    return (
      <div className="loading-wrap">
        <div className="spinner" />
        <div className="loading-text">Loading your collections…</div>
      </div>
    );
  }

  const collectionsList = [
    { name: "Favorites", icon: "heart-filled", count: userData.favorites.filter((f) => f.collection === "Favorites").length || apiFavs.length },
    { name: "Recently Viewed", icon: "clock", count: (userData.recentlyViewed || []).length },
    { name: "Recently Copied", icon: "copy", count: (userData.recentlyCopied || []).length },
    ...userData.collections
      .filter((c) => c.name !== "Favorites")
      .map((c) => ({
        name: c.name,
        icon: "folder",
        count: userData.favorites.filter((f) => f.collection === c.name).length,
      })),
  ];

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
        <div className="section-label" style={{ margin: 0 }}>
          <Icon name="folder" size={16} /> Collections & Favorites
        </div>
        <button
          className="btn-action"
          onClick={() => setShowAddModal(true)}
          style={{ fontSize: "0.8rem", padding: "4px 10px" }}
        >
          <Icon name="plus" size={12} /> New Collection
        </button>
      </div>

      {/* Collection tabs */}
      <div style={{ display: "flex", gap: "8px", overflowX: "auto", paddingBottom: "12px", marginBottom: "16px" }}>
        {collectionsList.map((col) => {
          const isSelected = selectedCollection === col.name;
          return (
            <button
              key={col.name}
              onClick={() => setSelectedCollection(col.name)}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "6px",
                padding: "6px 12px",
                borderRadius: "20px",
                border: isSelected ? "1px solid var(--accent)" : "1px solid var(--border)",
                background: isSelected ? "rgba(168, 85, 247, 0.15)" : "var(--bg-card)",
                color: isSelected ? "var(--accent)" : "var(--text-secondary)",
                fontSize: "0.82rem",
                fontWeight: 600,
                cursor: "pointer",
                whiteSpace: "nowrap",
                transition: "all 0.15s ease",
              }}
            >
              <Icon name={col.icon as any} size={13} />
              <span>{col.name}</span>
              <span style={{ opacity: 0.6, fontSize: "0.75rem" }}>({col.count})</span>
              {isSelected && col.name !== "Favorites" && col.name !== "Recently Viewed" && col.name !== "Recently Copied" && (
                <span
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteCollection(col.name);
                  }}
                  title="Delete collection"
                  style={{ marginLeft: "4px", color: "var(--text-muted)", cursor: "pointer" }}
                >
                  ×
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Create collection modal */}
      {showAddModal && (
        <div style={{ background: "var(--bg-card)", border: "1px solid var(--border)", borderRadius: "8px", padding: "12px", marginBottom: "16px" }}>
          <form onSubmit={handleCreateCollection} style={{ display: "flex", gap: "8px" }}>
            <input
              type="text"
              placeholder="Collection name (e.g. Work, Discord, Friend Group)"
              value={newCollectionName}
              onChange={(e) => setNewCollectionName(e.target.value)}
              autoFocus
              style={{
                flex: 1,
                padding: "6px 10px",
                borderRadius: "6px",
                border: "1px solid var(--border)",
                background: "var(--bg-primary)",
                color: "var(--text-primary)",
                fontSize: "0.85rem",
              }}
            />
            <button type="submit" className="btn-action primary-action" style={{ padding: "6px 12px" }}>
              Create
            </button>
            <button type="button" className="btn-action" onClick={() => setShowAddModal(false)} style={{ padding: "6px 12px" }}>
              Cancel
            </button>
          </form>
        </div>
      )}

      {/* Displayed Memes */}
      {displayedMemes.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">
            <Icon name="heart" size={36} />
          </div>
          <p>No memes in "{selectedCollection}" yet. Click 'Favorite' on any meme card to save it.</p>
        </div>
      ) : (
        displayedMemes.map((m) => (
          <MemeCard
            key={m.id}
            meme={m}
            isFav={true}
            onToggleFav={() => {
              removeSavedMeme(m.id);
              refreshData();
            }}
            onToast={onToast}
          />
        ))
      )}
    </div>
  );
}
