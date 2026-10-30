# 🧠 Chatbot RAG Spécialisé - Gestion de l'Anxiété

Projet de Fin d'Année (PFA) — chatbot d'accompagnement sur le stress et l'anxiété, basé sur la
**Retrieval-Augmented Generation (RAG)**. Le projet compare trois approches :

| Chatbot | Fichier | Port |
|---|---|---|
| Sans RAG (LLM seul) | `chatbot_sans_rag_ui.py` | 7862 |
| RAG simple | `chatbot_avec_rag_simple.py` | 7865 |
| RAG (version intermédiaire) | `chatbot_avec_rag.py` | 7866 |
| **Agentic RAG** (pipeline multi-agents) | `chatbot_agentic_rag_ui.py` | 7867 |

## 📋 Architecture Agentic RAG

```
Question utilisateur
    ↓
[PRE-RETRIEVAL]   Reformulation → Analyse de complexité → Décomposition en sous-questions
    ↓
[RETRIEVAL]       Recherche sémantique dans le vector store FAISS (+ retriever graphe)
    ↓
[POST-RETRIEVAL]  Re-ranking et filtrage par pertinence
    ↓
[GENERATION]      LLM (Groq / Gemini) avec contexte enrichi
    ↓
[CRITIQUE]        Self-RAG : cohérence, clarté, exactitude, sécurité (détection de crise)
    ↓
Réponse
```

Détails : [docs/architecture_agentic_finale.md](docs/architecture_agentic_finale.md).

## 🛠️ Installation

Prérequis : Python 3.11+

```bash
# 1. Environnement virtuel
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux / macOS

# 2. Dépendances
pip install -r requirements.txt
pip install -r requirements_agentic.txt

# 3. Clés API
cp .env.example .env
# puis renseigner GROQ_API_KEY et/ou GOOGLE_API_KEY dans .env
```

Clés gratuites : [Groq](https://console.groq.com/keys) · [Google AI Studio](https://aistudio.google.com/apikey)

Guide détaillé : [INSTALLATION.md](INSTALLATION.md) · Démarrage rapide : [QUICKSTART.md](QUICKSTART.md)

## 🚀 Utilisation

```bash
python test_groq.py                  # vérifier la clé API
python chatbot_agentic_rag_ui.py     # puis ouvrir http://localhost:7867
```

Le vector store pré-calculé est fourni dans `data/vector_store/`. Pour le reconstruire à partir
de `data/paragraphs.json` :

```bash
python run_phase1.py
```

## 📦 Structure du projet

```
├── chatbot_*.py              # Interfaces Gradio (sans RAG, RAG simple, Agentic RAG)
├── run_phase1.py             # Chunking + embeddings + construction du vector store
├── test_groq.py              # Test de connexion à l'API Groq
├── src/
│   ├── data_processing/      # chunker, embedder, pipeline
│   ├── retrieval/            # vector store FAISS, retriever, graph retriever
│   ├── agents/               # pre-retrieval, post-retrieval, pipeline agentique
│   └── generation/           # générateur et critique (Self-RAG)
├── scripts/                  # utilitaires (extraction PDF FR, passage multilingue)
├── data/
│   ├── paragraphs*.json      # corpus extrait des PDFs
│   ├── processed/            # chunks + embeddings
│   └── vector_store/         # index FAISS
├── comparaisons_chatbot/     # sauvegardes des conversations (comparaison des approches)
└── docs/                     # documentation technique et comparaisons
```

Les PDFs sources (`data/stress_anxiety_pdfs/`) ne sont pas versionnés (trop volumineux).

## ⚠️ Avertissement

Ce chatbot est un projet académique. Il ne remplace pas un avis médical ou psychologique
professionnel.

## 📄 Licence

Projet à usage académique (PFA).
