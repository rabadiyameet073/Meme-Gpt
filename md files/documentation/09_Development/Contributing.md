# MemeGPT — Contributing Guide

> **Document Version:** 1.0 · **Last Updated:** 2026-08-02

---

## Welcome!

Thank you for your interest in contributing to MemeGPT! This guide will help you get started.

---

## Ways to Contribute

| Type | Difficulty | Impact |
|---|---|---|
| 🐛 Bug reports | Easy | High |
| 📖 Documentation improvements | Easy | Medium |
| 🧪 Adding tests | Medium | High |
| ✨ New features | Medium–Hard | High |
| 🎨 UI/UX improvements | Medium | Medium |
| 🤖 AI model improvements | Hard | Very High |

---

## First Contribution Checklist

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USER/memegpt.git`
3. Create a branch: `git checkout -b fix/my-fix`
4. Follow [Development Setup](../01_Getting_Started/Development_Setup.md)
5. Make your changes
6. Run tests: `npm test` and `cd backend && python -m pytest`
7. Commit: `git commit -m "fix(component): description"`
8. Push: `git push origin fix/my-fix`
9. Open a Pull Request to `develop`

---

## Good First Issues

Look for issues labeled **`good-first-issue`** — these are curated for new contributors:
- Add a new meme category
- Fix a typo in documentation
- Add a unit test for an untested function
- Improve error messages
- Add accessibility attributes to UI components

---

## Code of Conduct

- Be respectful and inclusive
- Give constructive feedback
- Help new contributors feel welcome
- No NSFW content in code, comments, or documentation

---

> **Related Documents:**
> - [01_Getting_Started/First_Contribution.md](../01_Getting_Started/First_Contribution.md) · [Git_Workflow.md](./Git_Workflow.md)
