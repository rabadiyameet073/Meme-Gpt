# Contributing to MemeGPT

Thank you for your interest in contributing to MemeGPT! This repository welcomes community contributions to help build the ultimate AI meme discovery engine.

---

## 🌟 Ways to Contribute

| Type | Difficulty | Impact | Area |
|---|---|---|---|
| 🐛 **Bug reports** | Easy | High | GitHub Issues |
| 📖 **Documentation** | Easy | Medium | `/docs` and `/md files` |
| 🧪 **Adding tests** | Medium | High | `backend/tests` & `frontend/__tests__` |
| ✨ **New features** | Medium–Hard | High | Backend & Frontend apps |
| 🎨 **UI/UX improvements** | Medium | Medium | Frontend components & CSS |
| 🤖 **AI model improvements** | Hard | Very High | Vector embeddings & LLM prompts |

---

## 🚀 First Contribution Checklist (Step-by-Step)

1. **Fork the repository** on GitHub.
2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USER/memegpt.git
   cd memegpt
   ```
3. **Create a branch**:
   ```bash
   git checkout -b fix/my-fix-name
   # or
   git checkout -b feat/my-new-feature
   ```
4. **Follow Development Setup** (see `01_Getting_Started/Development_Setup.md`):
   - Install backend requirements: `pip install -r backend/requirements.txt`
   - Install frontend dependencies: `npm install`
5. **Make your changes**.
6. **Run tests**:
   - Backend: `python -m pytest`
   - Frontend: `npm test`
7. **Commit using Conventional Commits**:
   ```bash
   git commit -m "fix(component): concise description of changes"
   ```
8. **Push to your fork**:
   ```bash
   git push origin fix/my-fix-name
   ```
9. **Open a Pull Request** targeting the `develop` branch!

---

## 🏷️ Good First Issues

Look for issues labeled **`good-first-issue`**:
- Adding a new meme category or tag catalog
- Fixing typos in documentation
- Adding unit test coverage for untested services
- Improving frontend error toasts and accessibility (ARIA labels)

---

## 📜 Code of Conduct

- **Be respectful and inclusive** in all communications.
- **Provide constructive feedback** during code reviews.
- **Help new contributors feel welcome**.
- **Zero NSFW content** in code, comments, sample memes, or documentation.
