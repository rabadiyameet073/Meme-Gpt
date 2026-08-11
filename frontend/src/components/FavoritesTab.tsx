import { useState, useEffect } from "react";
import { api, getSessionId, type MemeRecord } from "../api";
import { MemeCard } from "./MemeCard";
import { Icon } from "./Icon";

const SESSION_ID = getSessionId();

export function FavoritesTab({ onToast }: { onToast: (m: string) => void }) {
  const [favs, setFavs] = useState<MemeRecord[]>([]);
  const [loading, setLoading] = useState(true);

  const loadFavs = async () => {
    try {
      const data = await api.favorites(SESSION_ID);
      setFavs(data);
    } catch {
      setFavs([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFavs();
  }, []);

  if (loading) {
    return (
      <div className="loading-wrap">
        <div className="spinner" />
        <div className="loading-text">Loading your saved memes…</div>
      </div>
    );
  }

  return (
    <div>
      <div className="section-label">
        <Icon name="heart-filled" size={14} /> Saved Favorite Memes ({favs.length})
      </div>
      {favs.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">
            <Icon name="heart" size={36} />
          </div>
          <p>No favorite memes saved yet. Click 'Favorite' on any meme card to save it here.</p>
        </div>
      ) : (
        favs.map((m) => (
          <MemeCard
            key={m.id}
            meme={m}
            isFav
            onToggleFav={() => loadFavs()}
            onToast={onToast}
          />
        ))
      )}
    </div>
  );
}
