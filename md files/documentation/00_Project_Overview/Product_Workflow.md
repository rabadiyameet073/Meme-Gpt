# MemeGPT — Product Workflow

> **Document Version:** 1.0  
> **Last Updated:** 2026-08-01  
> **Owner:** Product Lead  
> **Related Documents:** [User_Personas.md](./User_Personas.md) · [00_Project_Overview.md](./00_Project_Overview.md)

---

## Purpose

This document maps every user journey through MemeGPT with detailed sequence diagrams, flow charts, and step-by-step explanations. It serves as the reference for both product design and engineering implementation.

---

## Core User Flows

### Flow 1: Basic Meme Search (Primary Flow)

This is the most common user journey — the "happy path" that 80% of sessions follow.

```mermaid
sequenceDiagram
    actor U as User
    participant APP as MemeGPT App
    participant API as Backend API
    participant AI as AI Pipeline
    participant DB as Vector DB

    U->>APP: Opens app
    APP->>U: Shows search interface
    U->>APP: Types "when your code works first try"
    U->>APP: Taps "Find Meme" button
    APP->>API: POST /api/v1/search
    API->>AI: Parse intent + detect emotion
    AI-->>API: {emotion: "surprise", situation: "code success"}
    API->>AI: Generate query embedding
    AI-->>API: 384-dim vector
    API->>DB: Vector similarity search
    DB-->>API: Top 10 candidates
    API->>API: Re-rank by score + emotion + popularity
    API-->>APP: Top 5 meme results (JSON)
    APP->>U: Display meme grid (<1.5s total)
    U->>APP: Taps preferred meme
    APP->>U: Full-screen preview with actions
    U->>APP: Taps "Copy"
    APP->>U: Meme copied to clipboard ✓
    U->>U: Pastes meme in chat
```

**Step-by-Step Detail:**

| Step | Action | Duration | Technical Detail |
|---|---|---|---|
| 1 | User opens app | 0ms | App is already loaded (PWA) or cold starts in <2s |
| 2 | User types query | Variable | Search input auto-focuses, max 2000 chars |
| 3 | User taps "Find Meme" | 0ms | Triggers API call, shows loading skeleton |
| 4 | LLM context parsing | ~300ms | Groq API extracts emotion, situation, tone, keywords |
| 5 | Emotion detection | ~100ms | Local DistilRoBERTa model classifies primary/secondary emotion |
| 6 | Query embedding | ~50ms | MiniLM-L6-v2 converts enriched query to 384-dim vector |
| 7 | Vector search | ~50ms | Qdrant cosine similarity search with filters |
| 8 | Re-ranking | ~10ms | Apply emotion boost, popularity score, format preference |
| 9 | Response rendered | ~50ms | Client receives JSON, renders meme cards with thumbnails |
| 10 | User interaction | Variable | Copy (instant), Download (~1s), Share (opens sheet) |

---

### Flow 2: Conversation-Based Search

Users paste an entire WhatsApp/Discord conversation for context-aware meme recommendation.

```mermaid
flowchart TD
    A["User copies conversation<br/>from WhatsApp"] --> B["Pastes into MemeGPT<br/>('Conversation' tab)"]
    B --> C["LLM analyzes full<br/>conversation context"]
    C --> D{"Multiple emotional<br/>contexts detected?"}
    D -->|"Yes (e.g., 3 contexts)"| E["Show labeled meme<br/>sections per context"]
    D -->|"No (single context)"| F["Show standard<br/>5 meme results"]
    E --> G["User picks meme<br/>for specific context"]
    F --> G
    G --> H["Copy / Download / Share"]
    H --> I["Shares back to<br/>original conversation"]
```

**LLM Conversation Analysis Example:**

```
Input (pasted conversation):
─────────────────────────────
Friend 1: "Bro did you study for tomorrow's exam?"
Friend 2: "I haven't even started 💀"
Friend 1: "The exam is in 8 hours"
Friend 2: "I'll just pray at this point"
Friend 1: "LMAO same"

LLM Output:
─────────────────────────────
{
  "contexts": [
    {
      "label": "Exam panic",
      "emotion": "fear",
      "tone": "humorous self-deprecation",
      "search_query": "student hasn't studied for exam panic humor"
    },
    {
      "label": "Accepting defeat",
      "emotion": "resignation",
      "tone": "sarcastic acceptance",
      "search_query": "giving up on studying acceptance meme"
    }
  ]
}
```

---

### Flow 3: Multi-Format Download

Users download the same meme in different formats for different platforms.

```mermaid
flowchart LR
    A["User finds<br/>perfect meme"] --> B["Taps Download"]
    B --> C["Format picker appears"]
    C --> D["GIF<br/>For WhatsApp"]
    C --> E["PNG<br/>For Instagram"]
    C --> F["MP4<br/>For TikTok"]
    C --> G["WebP<br/>For Telegram"]
    D --> H["CDN download<br/>starts"]
    E --> H
    F --> H
    G --> H
    H --> I["Success toast:<br/>'Saved to Downloads'"]
```

---

### Flow 4: Chat Refinement (Multi-Turn)

Users can refine results conversationally, similar to ChatGPT.

```
Turn 1:
  User:   "I just submitted my project at 11:59pm"
  MemeGPT: [Shows 5 memes — stressed + relief themed]

Turn 2:
  User:   "Give me something more triumphant"
  MemeGPT: [Re-searches with triumph + victory filter]
           [Shows 5 new results — celebration memes]

Turn 3:
  User:   "Show me a GIF version of the third one"
  MemeGPT: [Returns GIF format of meme #3]

Turn 4:
  User:   "Perfect, download it"
  MemeGPT: [Triggers GIF download]
           [Shows: ✓ Downloaded to your device]
```

**Technical Implementation:**

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Searching: User submits query
    Searching --> ResultsShown: Results returned
    ResultsShown --> Refining: User sends follow-up
    Refining --> ResultsShown: Refined results returned
    ResultsShown --> Previewing: User taps meme
    Previewing --> ResultsShown: User closes preview
    Previewing --> ActionComplete: Copy/Download/Share
    ActionComplete --> ResultsShown: Continue browsing
    ActionComplete --> Idle: User done
    ResultsShown --> Idle: User clears search
```

---

### Flow 5: Trending Discovery

Users browse trending memes without searching.

```mermaid
flowchart TD
    A["User opens<br/>Trending tab"] --> B["See category chips:<br/>All | Work | Gaming | ❤️ | Tech"]
    B --> C["Select category"]
    C --> D["Meme grid loads<br/>(hourly updated)"]
    D --> E["Browse / scroll"]
    E --> F{"User interaction"}
    F -->|"Copy"| G["Copy to clipboard"]
    F -->|"Download"| H["Download in preferred format"]
    F -->|"Save"| I["Add to Favorites"]
    F -->|"Search similar"| J["'More like this' search"]
    J --> K["New search with<br/>meme's tags as query"]
```

---

### Flow 6: Favorites & Collections

Users manage their personal meme library.

```mermaid
flowchart TD
    A["Any meme result"] --> B{"User action"}
    B -->|"Star ⭐"| C["Added to Favorites"]
    B -->|"Add to Collection"| D["Collection picker"]
    D --> E["Select existing collection<br/>or create new"]
    E --> F["Meme saved to collection"]
    
    G["Library tab"] --> H["View collections"]
    H --> I["Favorites (default)"]
    H --> J["Custom: 'Work Memes'"]
    H --> K["Custom: 'Reactions'"]
    
    I --> L["Grid of saved memes"]
    L --> M["Search within collection"]
    L --> N["Export as ZIP"]
    L --> O["Copy / Download individual"]
```

---

## Admin Workflows

### Weekly Meme Indexing Pipeline

```mermaid
flowchart TD
    A["Sunday 2am UTC<br/>GitHub Actions cron"] --> B["Collect new memes<br/>from Reddit (500 posts)"]
    B --> C["Download images<br/>to Cloudflare R2"]
    C --> D["Preprocessing:<br/>OCR + BLIP caption + LLM tags"]
    D --> E["Generate embeddings:<br/>MiniLM (text) + CLIP (image)"]
    E --> F["Index to Qdrant<br/>(upsert vectors)"]
    F --> G["Update Supabase<br/>(meme metadata)"]
    G --> H["Verify index:<br/>test search with known queries"]
    H --> I{"Tests pass?"}
    I -->|"Yes"| J["✅ Pipeline complete<br/>Slack notification"]
    I -->|"No"| K["❌ Alert founder<br/>Manual investigation"]
```

---

## Error Flows

### Search Error Handling

```mermaid
flowchart TD
    A["User submits search"] --> B{"API responds?"}
    B -->|"Yes"| C{"Results found?"}
    B -->|"No (timeout/error)"| D["Show error state:<br/>'Something went wrong. Try again.'<br/>+ Retry button"]
    C -->|"Yes"| E["Show results"]
    C -->|"No (score < 0.3)"| F["Show empty state:<br/>'No perfect match found.<br/>Try different words or<br/>check trending memes.'"]
    D --> G["User taps Retry"]
    G --> A
    F --> H["Show trending memes<br/>as fallback suggestions"]
```

---

## Platform-Specific Workflows

### Web App Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `⌘/Ctrl + Enter` | Submit search |
| `Escape` | Close lightbox/preview |
| `←` `→` | Navigate between results in preview |
| `C` | Copy current meme (in preview) |
| `D` | Download current meme (in preview) |
| `S` | Save to favorites (in preview) |
| `F` | Toggle format filter |
| `/` | Focus search input |

### Mobile App Gestures

| Gesture | Action |
|---|---|
| Swipe left/right (preview) | Navigate between results |
| Long press (meme card) | Quick copy to clipboard |
| Pull down (results) | Refresh results |
| Double tap (meme) | Add to favorites |
| Pinch zoom (preview) | Zoom into meme image |

---

## Offline Workflow

```mermaid
flowchart TD
    A{"Internet available?"}
    A -->|"Yes"| B["Normal search flow"]
    A -->|"No"| C["Show offline indicator"]
    C --> D["Search offline cache<br/>(last 50 viewed memes)"]
    D --> E{"Matches found<br/>in cache?"}
    E -->|"Yes"| F["Show cached results"]
    E -->|"No"| G["Show message:<br/>'You're offline. Showing<br/>your recent memes.'"]
    G --> H["Show recent memes grid"]
    F --> I["Copy / Share from cache"]
    H --> I
```

---

> **Related Documents:**
> - [User_Personas.md](./User_Personas.md) — Who uses these workflows
> - [07_APIs/Search_API.md](../07_APIs/Search_API.md) — API contract for search
> - [08_Features/Smart_Meme_Search.md](../08_Features/Smart_Meme_Search.md) — Feature spec
> - [04_Frontend/Components.md](../04_Frontend/Components.md) — UI component specs
