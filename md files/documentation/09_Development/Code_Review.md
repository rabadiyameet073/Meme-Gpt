# MemeGPT — Code Review Checklist

> **Document Version:** 1.0 · **Last Updated:** 2026-08-02

---

## Purpose

Standard checklist for all code reviews to ensure quality, security, and consistency.

---

## Review Checklist

### ✅ Functionality
- [ ] Feature works as described in the PR
- [ ] Edge cases handled (empty input, max length, special chars, unicode)
- [ ] Error states display user-friendly messages
- [ ] Loading states implemented
- [ ] No regressions in existing features

### ✅ Code Quality
- [ ] Follows coding standards (PEP 8 / ESLint)
- [ ] Type hints (Python) / TypeScript types used properly
- [ ] No `any` types in TypeScript
- [ ] No hardcoded values — use config/env vars
- [ ] No `console.log` / `print` in production code
- [ ] Functions are small and have single responsibility
- [ ] Meaningful variable and function names
- [ ] Comments explain *why*, not *what*

### ✅ Performance
- [ ] No N+1 database queries
- [ ] Async operations used for I/O (not blocking event loop)
- [ ] No unnecessary re-renders in React (memo, useCallback)
- [ ] Images are lazy-loaded below the fold
- [ ] No large synchronous computations in route handlers

### ✅ Security
- [ ] User input is sanitized/validated
- [ ] No PII in log messages
- [ ] API keys not hardcoded
- [ ] SQL injection prevented (parameterized queries)
- [ ] XSS prevented (no `dangerouslySetInnerHTML` without sanitization)
- [ ] Rate limiting applied to new endpoints

### ✅ Testing
- [ ] Unit tests for new business logic
- [ ] Integration test for new API endpoints
- [ ] Edge case tests included
- [ ] All existing tests still pass

### ✅ Documentation
- [ ] Docstrings on new public functions
- [ ] README updated if setup steps changed
- [ ] API docs updated if endpoints changed
- [ ] Env vars documented if new ones added

---

> **Related Documents:**
> - [Coding_Standards.md](./Coding_Standards.md) · [Git_Workflow.md](./Git_Workflow.md) · [10_Testing/Testing_Strategy.md](../10_Testing/Testing_Strategy.md)
