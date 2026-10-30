# 🚀 Guide de Démarrage Rapide

## ⚡ Démarrage Ultra-Rapide (2 minutes)

```bash
# 1. Activer l'environnement
.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate    # macOS/Linux

# 2. Lancer les chatbots
python chatbot_sans_rag_ui.py    # Port 7862
python chatbot_avec_rag.py       # Port 7865
```

## 🌐 Accès aux Interfaces

- **Sans RAG** : http://localhost:7862
- **Avec RAG** : http://localhost:7865

## 📝 Checklist Avant de Lancer

- [ ] Python 3.11 activé (`python --version`)
- [ ] Clés API Groq et Gemini dans `.env`
- [ ] Dépendances installées (`pip list | grep langchain-groq`)
- [ ] Fichiers dans `data/processed/` présents
- [ ] Test Groq réussi (`python test_groq.py`)

## 🆘 Problèmes Courants

### ❌ "Erreur API"
```bash
# Vérifier vos clés dans .env
python test_groq.py
```

### ❌ Port déjà utilisé
```bash
# Windows
Get-Process python | Stop-Process -Force

# Linux/macOS
pkill python
```

### ❌ Réponses lentes
Vérifier les limites de quota des APIs gratuites

---

📚 **Documentation complète** : Voir [INSTALLATION.md](INSTALLATION.md)
