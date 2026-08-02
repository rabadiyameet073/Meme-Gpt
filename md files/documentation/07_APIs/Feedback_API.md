# MemeGPT — Feedback API

> **Document Version:** 1.0 · **Last Updated:** 2026-08-02

---

## `POST /api/v1/feedback`

Records user interactions with memes for model improvement and analytics.

### Request

```json
{
  "query_id": "q_xyz789",
  "meme_id": "meme_042",
  "action": "download",
  "session_id": "sess_abc123"
}
```

| Field | Type | Required | Validation |
|---|---|---|---|
| `query_id` | string | Yes | Must match an existing query |
| `meme_id` | string | Yes | Must match an existing meme |
| `action` | string | Yes | One of the valid signal types |
| `session_id` | string | No | Anonymous tracking |

### Valid Actions

| Action | Signal Weight | Description | Example |
|---|---|---|---|
| `view` | +0.1 | Meme appeared in results | Implicit — logged automatically |
| `click` | +0.5 | User clicked to preview | Tap/click on meme card |
| `copy` | +1.0 | Copied to clipboard | Click "Copy" button |
| `download` | +2.0 | Downloaded file | Click "Download" button |
| `share` | +3.0 | Shared via link/sheet | Click "Share" button |
| `thumbs_up` | +2.0 | Explicit positive vote | Click 👍 |
| `thumbs_down` | -1.0 | Explicit negative vote | Click 👎 |
| `skip` | -0.3 | Scrolled past without interaction | Detected via viewport tracking |

### Response (200 OK)

```json
{
  "success": true,
  "message": "Feedback recorded"
}
```

### Processing

Feedback is processed as a **FastAPI BackgroundTask** — the response is sent immediately, and the database write happens asynchronously.

```python
@app.post("/feedback")
async def record_feedback(request: FeedbackRequest, bg: BackgroundTasks):
    bg.add_task(process_feedback, request)
    return {"success": True, "message": "Feedback recorded"}
```

### Privacy

- No PII is associated with feedback records
- Session IDs are random, not linked to user identity
- Feedback data is used only for improving search quality

---

> **Related Documents:**
> - [API_Overview.md](./API_Overview.md) · [Search_API.md](./Search_API.md)
