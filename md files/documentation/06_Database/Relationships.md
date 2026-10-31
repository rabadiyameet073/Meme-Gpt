# MemeGPT — Database Relationships

> **Document Version:** 1.0 · **Last Updated:** 2026-08-02

---

## Purpose

Documentation of all entity relationships, foreign keys, cascade behaviors, and referential integrity rules.

---

## Entity Relationship Diagram

```mermaid
erDiagram
    Meme ||--o{ MemeVote : "receives votes"
    Meme ||--o{ MemeUsage : "usage logged"
    Meme ||--o{ SavedMeme : "saved by users"
    Meme ||--o{ Feedback : "receives feedback"
    User ||--o{ SavedMeme : "saves memes"
    User ||--o{ Feedback : "gives feedback"

    Meme {
        string id PK "cuid()"
        string name "NOT NULL"
        string category "NOT NULL"
        string dialogue "NOT NULL"
        string explanation "NOT NULL"
        string keywords "JSON array"
        float viralScore "default 0"
        int usageCount "default 0"
        int upvotes "default 0"
        int downvotes "default 0"
    }

    MemeVote {
        string id PK "cuid()"
        string memeId FK "→ Meme.id"
        int vote "1 or -1"
        string sessionId "anonymous"
    }

    MemeUsage {
        string id PK "cuid()"
        string memeId FK "→ Meme.id"
        string query "search query"
        float score "relevance"
    }

    User {
        uuid id PK "Phase 3"
        string email "UNIQUE"
        string plan "free or pro"
    }

    SavedMeme {
        uuid id PK
        uuid userId FK "→ User.id"
        string memeId "→ Meme external"
        string collectionName "default Favorites"
    }

    Feedback {
        uuid id PK
        string sessionId "anonymous"
        uuid userId FK "→ User.id nullable"
        string memeId "→ Meme external"
        string action "signal type"
    }
```

---

## Foreign Key Relationships

| Relationship | From Table | To Table | Type | On Delete |
|---|---|---|---|---|
| MemeVote → Meme | `meme_votes.memeId` | `memes.id` | Many-to-One | CASCADE |
| MemeUsage → Meme | `meme_usage.memeId` | `memes.id` | Many-to-One | CASCADE |
| SavedMeme → User | `saved_memes.userId` | `users.id` | Many-to-One | CASCADE |
| Feedback → User | `feedback.userId` | `users.id` | Many-to-One | SET NULL |

### Cascade Behaviors

| Event | Behavior | Reason |
|---|---|---|
| Delete a meme | Cascade delete votes + usage logs | Orphan data serves no purpose |
| Delete a user | Cascade delete saved memes | User's data should be fully removable (GDPR) |
| Delete a user | Set NULL on feedback.userId | Anonymous feedback still has analytics value |

---

## Relationship Cardinality

| Entity A | Relationship | Entity B | Cardinality |
|---|---|---|---|
| Meme | has | MemeVotes | 1:N (one meme, many votes) |
| Meme | logged in | MemeUsage | 1:N (one meme, many usage entries) |
| User | saves | Memes | M:N (via SavedMeme join table) |
| User | provides | Feedback | 1:N (one user, many feedback entries) |
| Meme | receives | Feedback | 1:N (one meme, many feedback entries) |

---

## Best Practices

1. **Always use foreign keys** — enforce referential integrity at the DB level
2. **CASCADE delete** children when parent is deleted (votes, usage logs)
3. **SET NULL** when child data has independent value (feedback analytics)
4. **Never delete memes in production** — soft-delete with `is_active` flag
5. **Index all FK columns** — required for efficient JOIN operations

---

> **Related Documents:**
> - [Tables.md](./Tables.md) · [Schema.md](./Schema.md) · [Indexing.md](./Indexing.md)
