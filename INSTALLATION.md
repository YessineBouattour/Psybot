# 📦 Guide d'Installation - Projet Chatbot RAG

## 🎯 Vue d'ensemble
Ce projet compare deux chatbots :
- **Chatbot SANS RAG** : Utilise uniquement les connaissances du modèle
- **Chatbot AVEC RAG** : Utilise des documents spécialisés sur l'anxiété et les thérapies cognitives

---

## ⚙️ Prérequis Système

### 1. **Système d'exploitation**
- ✅ Windows 10/11 (64-bit)
- ✅ macOS 11+ 
- ✅ Linux (Ubuntu 20.04+)

### 2. **Espace disque**
- Minimum **2 GB** d'espace libre
- Données et embeddings : ~500 MB

### 3. **RAM**
- Minimum **8 GB** recommandé
- 16 GB pour de meilleures performances

---

## 📥 Installation Étape par Étape

### ÉTAPE 1 : Installer Python 3.11

⚠️ **IMPORTANT** : Python 3.14 ne fonctionne PAS. Utilisez Python 3.11.x

#### Windows :
```powershell
# Télécharger Python 3.11.10
Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.11.10/python-3.11.10-amd64.exe" -OutFile "$env:TEMP\python-3.11.10.exe"

# Installer (cochez "Add to PATH")
Start-Process "$env:TEMP\python-3.11.10.exe" -ArgumentList "/quiet", "PrependPath=1" -Wait
```

#### macOS :
```bash
brew install python@3.11
```

#### Linux :
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev
```

**Vérifier l'installation :**
```bash
python --version
# Doit afficher : Python 3.11.x
```

---

### ÉTAPE 2 : Obtenir les Clés API Gratuites

Ce projet utilise des APIs gratuites (**Groq** et **Gemini**) au lieu de modèles locaux.

#### 1. **Groq API** (génération de réponses)
- Aller sur : https://console.groq.com/keys
- Créer un compte gratuit
- Créer une clé API
- ✅ Limite : 14,400 requêtes/jour GRATUIT

#### 2. **Google Gemini API** (analyse et critique)
- Aller sur : https://aistudio.google.com/app/apikey
- Créer un compte Google
- Créer une clé API
- ✅ Limite : 1,500 requêtes/jour GRATUIT

⚠️ **Gardez ces clés en sécurité** - vous allez les mettre dans le fichier `.env`

---

### ÉTAPE 3 : Cloner/Pull le Projet

```bash
# Si première fois (clone)
git clone <URL_DU_REPO>
cd PFA

# Si mise à jour (pull)
cd PFA
git pull origin main
```

---

### ÉTAPE 4 : Créer l'Environnement Virtuel

```bash
# Créer l'environnement avec Python 3.11
python3.11 -m venv .venv

# Activer l'environnement
# Windows PowerShell :
.venv\Scripts\Activate.ps1

# Windows CMD :
.venv\Scripts\activate.bat

# macOS/Linux :
source .venv/bin/activate
```

---

### ÉTAPE 5 : Installer les Dépendances

```bash
# Avec l'environnement virtuel activé
pip install --upgrade pip
pip install -r requirements.txt
```

**Packages principaux installés :**
- `gradio` : Interface web
- `requests` : Appels API Ollama
- `torch` : Embeddings
- `python-dotenv` : Configuration

---

### ÉTAPE 6 : Vérifier les Données

Les fichiers suivants **doivent exister** dans `data/processed/` :
```
data/processed/
├── corpus_embeddings.pt          # Embeddings pré-calculés (2185 chunks)
├── corpus_metadata.json          # Métadonnées des documents
└── processed_chunks.json         # Chunks de texte (2185 chunks)
```

**Si les fichiers sont absents :**
```bash
python run_phase1.py
```
⏳ Cela prendra 30-60 minutes pour générer les embeddings.

---

### ÉTAPE 7 : Configuration (.env)

Le fichier `.env` doit exister à la racine du projet :

```env
# LLM Configuration
LLM_MODEL=phi3:mini
OLLAMA_API_URL=http://localhost:11434

# Embedding Configuration  
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
CHUNK_SIZE=500
CHUNK_OVERLAP=50

# Data Paths
DATA_DIR=data
PROCESSED_DIR=data/processed
PDF_DIR=data/stress_anxiety_pdfs
```

⚠️ **Si le fichier n'existe pas**, créez-le avec le contenu ci-dessus.

---

## 🚀 Lancer les Chatbots

### Lancer le Chatbot SANS RAG

```bash
python chatbot_sans_rag_ui.py
```

🌐 Interface disponible sur : **http://localhost:7862**

### Lancer le Chatbot AVEC RAG

```bash
python chatbot_avec_rag.py
```

🌐 Interface disponible sur : **http://localhost:7865**

---

## 🔧 Lancement Automatique (Optionnel)

### Créer un script de lancement (Windows)

Créer `launch.ps1` :
```powershell
# Activer l'environnement
& .\.venv\Scripts\Activate.ps1

# Lancer les deux chatbots en arrière-plan
Start-Process -FilePath ".\.venv\Scripts\python.exe" -ArgumentList "chatbot_sans_rag_ui.py" -WindowStyle Hidden
Start-Sleep -Seconds 3
Start-Process -FilePath ".\.venv\Scripts\python.exe" -ArgumentList "chatbot_avec_rag.py" -WindowStyle Hidden

Write-Host "✅ Chatbots lancés !" -ForegroundColor Green
Write-Host "🔵 Sans RAG : http://localhost:7862" -ForegroundColor Cyan
Write-Host "🟣 Avec RAG : http://localhost:7865" -ForegroundColor Magenta
```

Exécuter :
```powershell
.\launch.ps1
```

### Créer un script de lancement (macOS/Linux)

Créer `launch.sh` :
```bash
#!/bin/bash

# Activer l'environnement
source .venv/bin/activate

# Lancer les deux chatbots en arrière-plan
python chatbot_sans_rag_ui.py &
sleep 3
python chatbot_avec_rag.py &

echo "✅ Chatbots lancés !"
echo "🔵 Sans RAG : http://localhost:7862"
echo "🟣 Avec RAG : http://localhost:7865"
```

Rendre exécutable et lancer :
```bash
chmod +x launch.sh
./launch.sh
```

---

## 🧪 Tester l'Installation

### Test 1 : Vérifier les APIs
```bash
python test_groq.py
```

✅ Doit afficher une réponse de Groq.

### Test 2 : Vérifier les Données
```bash
python -c "import torch; print('Embeddings:', torch.load('data/processed/corpus_embeddings.pt').shape)"
```

✅ Doit afficher : `Embeddings: torch.Size([2185, 384])`

### Test 3 : Accéder aux Interfaces
- Ouvrir http://localhost:7862 (Sans RAG)
- Ouvrir http://localhost:7865 (Avec RAG)
- Poser une question : "Qu'est-ce que l'agoraphobie ?"

---

## 🐛 Troubleshooting

### Problème 1 : "Erreur API Groq/Gemini"

**Cause** : Clés API manquantes ou invalides

**Solution** :
1. Vérifier que `.env` contient vos vraies clés API
2. Tester les clés : `python test_groq.py`
3. Vérifier que vous n'avez pas dépassé les limites gratuites

---

### Problème 2 : "Timeout ou réponses lentes"

**Cause** : Limites de débit des APIs gratuites

**Solutions** :
1. Réduire la longueur des questions
2. Attendre quelques secondes entre les requêtes
3. Vérifier votre quota API

---

### Problème 3 : "ModuleNotFoundError"

**Cause** : Dépendances non installées

**Solution** :
```bash
# Activer l'environnement virtuel
.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate    # macOS/Linux

# Réinstaller les dépendances
pip install -r requirements_free_apis.txt
```

---

### Problème 4 : "KeyError: 'metadata'"

**Cause** : Fichiers de données corrompus

**Solution** :
```bash
# Regénérer les données
python run_phase1.py
```

---

### Problème 5 : Port déjà utilisé

**Cause** : Un processus utilise déjà le port 7862 ou 7865

**Solution Windows** :
```powershell
# Trouver le processus
Get-Process python | Stop-Process -Force
```

**Solution macOS/Linux** :
```bash
# Trouver et tuer le processus
lsof -ti:7862 | xargs kill -9
lsof -ti:7865 | xargs kill -9
```

---

### Problème 6 : Python 3.14 installé

**Symptôme** : Erreurs avec `transformers` ou `langchain`

**Solution** : Désinstaller Python 3.14 et installer Python 3.11
```bash
# Vérifier la version
python --version

# Si 3.14.x, désinstaller et installer 3.11 (voir ÉTAPE 1)
```

---

## 📊 Utilisation des Chatbots

### Questions de Test Suggérées

**Pour tester la différence Sans RAG vs Avec RAG :**

1. **Agoraphobie** : "Comment traiter l'agoraphobie avec la TCC ?"
2. **Anxiété généralisée** : "Quels sont les symptômes de l'anxiété généralisée ?"
3. **Thérapies cognitives** : "Quel est le modèle cognitif de la dépression selon Aaron Beck ?"
4. **Techniques TCC** : "Comment fonctionne la restructuration cognitive ?"

**Le chatbot AVEC RAG devrait donner :**
- Des réponses plus précises et détaillées
- Des citations de documents [Document X]
- Des sources avec scores de pertinence

---

## 📁 Structure du Projet

```
PFA/
├── chatbot_sans_rag_ui.py          # Chatbot baseline (port 7862)
├── chatbot_avec_rag.py             # Chatbot RAG (port 7865)
├── run_phase1.py                   # Script de traitement des données
├── requirements.txt                # Dépendances Python
├── .env                            # Configuration
├── INSTALLATION.md                 # Ce fichier
├── README.md                       # Documentation projet
│
├── data/
│   ├── processed/
│   │   ├── corpus_embeddings.pt    # Embeddings (2185 chunks)
│   │   ├── corpus_metadata.json    # Métadonnées
│   │   └── processed_chunks.json   # Chunks de texte
│   └── stress_anxiety_pdfs/        # PDFs sources (non versionnés)
│
├── src/
│   ├── data_processing/            # Pipeline de traitement
│   ├── retrieval/                  # Système de recherche
│   └── generation/                 # Génération de réponses
│
└── .venv/                          # Environnement virtuel (non versionné)
```

---

## 🔄 Mise à Jour du Projet

```bash
# Pull les dernières modifications
git pull origin main

# Réinstaller les dépendances (si requirements.txt a changé)
pip install -r requirements.txt

# Relancer les chatbots
python chatbot_sans_rag_ui.py
python chatbot_avec_rag.py
```

---

## 📝 Notes Importantes

1. **Python 3.11 obligatoire** : Ne PAS utiliser Python 3.14
2. **Clés API gratuites** : Groq (14,400 req/jour) + Gemini (1,500 req/jour)
3. **Ports utilisés** : 7862 (sans RAG), 7865 (avec RAG)
4. **Embeddings pré-calculés** : Inclus dans le repo (pas besoin de regénérer)
5. **PDFs sources** : Non versionnés (trop volumineux), seulement les embeddings

---

## 🆘 Support

Si vous rencontrez des problèmes :

1. Vérifier les logs dans le terminal
2. Consulter la section Troubleshooting ci-dessus
3. Vérifier que tous les prérequis sont installés
4. S'assurer que Python 3.11 est utilisé
5. Tester les clés API (`python test_groq.py`)

---

## ✅ Checklist d'Installation

- [ ] Python 3.11.x installé et vérifié
- [ ] Clés API Groq et Gemini obtenues
- [ ] Projet cloné/pullé depuis Git
- [ ] Environnement virtuel créé et activé
- [ ] Dépendances installées (`requirements_free_apis.txt`)
- [ ] Fichier `.env` configuré avec les vraies clés API
- [ ] Fichiers de données présents dans `data/processed/`
- [ ] Test Groq réussi (`python test_groq.py`)
- [ ] Les deux chatbots démarrent sans erreur
- [ ] Interfaces web accessibles (ports 7862 et 7865)

---

**Bon courage ! 🚀**
