# Contributing to SignalLens

Thank you for your interest in contributing to **SignalLens**—an evidence-backed local disruption intelligence platform prototype.

---

## Project Architecture

SignalLens is built as a full-stack monorepo:

* **Backend (`/backend`)**: Built with **FastAPI** and **SQLite** (`signallens.db`). It handles disruption report submission, seed demo datasets, and AI classification via Hugging Face (`facebook/bart-large-mnli`).
* **Frontend (`/frontend`)**: Built with **Vite**, **React**, and **Tailwind CSS**. It provides an interactive UI for submitting disruption reports, filtering by location, and running model predictions on evidence.

---

## Getting Started

### 1. Fork and Clone
```bash
# Clone your fork
git clone [https://github.com/YOUR-USERNAME/signallens.git](https://github.com/YOUR-USERNAME/signallens.git)
cd signallens