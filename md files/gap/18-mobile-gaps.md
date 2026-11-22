# 18 — Mobile App (Expo) Gaps

**Source requirements:** `md files/documentation/15_Mobile/*` (Mobile_Overview), `md files/upgraded_docs/11_Mobile_App_Completion.md`, `md files/completion_fixes/06_Mobile_App_Completion.md`, `md files/implementation_guides/05_Mobile_App_Completion.md`
**Related:** [16-integrations-gaps](16-integrations-gaps.md) · [19-testing-gaps](19-testing-gaps.md) · [20-ci-cd-deployment-gaps](20-ci-cd-deployment-gaps.md)

## Verified as fully implemented (re-verified; corrects the earlier reports)
| Item | Evidence |
|---|---|
| Expo SDK 51 / RN 0.74 / Expo Router 3 | `apps/mobile/package.json` |
| App assets present (prior reports said missing; **now resolved**) | `apps/mobile/assets/`: icon 1024², adaptive-icon, splash 1284×2778, notification-icon, favicon |
| Tabs: search, trending, library; meme detail | `apps/mobile/app/(tabs)/*`, `app/meme/[id].tsx` |
| Native share, save to camera roll, haptics, double-tap, pull-to-refresh | `expo-sharing`, `expo-media-library`; `MemeCard.tsx:16-58`; `trending.tsx:74` |
| Offline cache of the last 50 memes | `hooks/useOfflineCache.ts:5`, used in `useMemeSearch.ts:61,80` |

## Gaps
| Gap ID | Requirement | Status | Evidence | Required change | Priority |
|---|---|---|---|---|---|
| MOB-01 | EAS submit config | Partially implemented | `eas.json` submit has `"your@email.com"`, `"YOUR_APP_ID"`, missing `./google-service-account.json` | User fills these in; keep the key out of git | High |
| MOB-02 | Push notifications (registration + delivery) | Partially implemented | `usePushNotifications.ts:98` needs `projectId`; `app.json` lacks `extra.eas.projectId`; no server sender ([16](16-integrations-gaps.md) INT-09) | `eas init`; sender | High |
| MOB-03 | Deep links / universal links | Not implemented | `app.json` has no `scheme`, associated domains or intent filters | Add `scheme: "memegpt"` + links for `/meme/[slug]` | Medium |
| MOB-04 | Production API URL | Needs improvement | `lib/api.ts:6` defaults `EXPO_PUBLIC_API_URL` to `http://localhost:8000`; not in `.env.example` | Env per EAS profile | High |
| MOB-05 | MMKV storage (`Mobile_Overview.md:116`) | Not implemented | No `react-native-mmkv`; `FormatPicker.tsx:3` comment claims it | Add it or fix the doc | Low |
| MOB-06 | Voice input (P2) | Not implemented | Not present; the doc names `expo-speech`, which is TTS only, so the **doc itself is wrong** | Fix the doc; use a speech-recognition lib | Low |
| MOB-07 | Android permissions modern | Needs improvement | `WRITE/READ_EXTERNAL_STORAGE` declared (deprecated API 33+) | Remove | Low |
| MOB-08 | Feature parity with web (vision P2): chat, collections, auth | Partially implemented | No chat or auth screens in `apps/mobile/app` | Add after the web is consolidated | Medium |
| MOB-09 | Mobile tests + CI | Not implemented | No test files; no workflow job | Jest + `tsc --noEmit` + EAS build check | Medium |
| MOB-10 | App size ≈ 29 MB (`Mobile_Overview.md:97-105`) | ASSUMPTION – needs runtime validation | Needs an EAS build | Measure | Low |
| MOB-11 | Mobile analytics | Not implemented | No analytics calls | Umami/Expo analytics | Low |
