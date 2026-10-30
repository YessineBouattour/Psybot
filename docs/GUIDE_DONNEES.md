# 📚 Guide de Gestion des Données

## 🔄 Situation Actuelle vs Cible

### ❌ Données Actuelles (Temporaires)
```
data/paragraphs.json
├─ Contenu: Articles scientifiques biologie cellulaire
├─ Langue: ANGLAIS
└─ Utilité: Tests de développement uniquement
```

### ✅ Données Cibles (Production)
```
data/stress_anxiety_pdfs/
├─ Contenu: Documents sur anxiété, stress, TCC
├─ Langue: FRANÇAIS
└─ Utilité: Chatbot final pour patients
```

## 🎯 Plan de Transition

### Phase 1-4: Développement (MAINTENANT)
**Modèle actuel:** `all-MiniLM-L6-v2` (anglais)

✅ **Avantages:**
- Léger (80 MB) → téléchargement rapide
- Fonctionne avec vos données actuelles (anglais)
- Permet de développer tout le système RAG

⚠️ **Limitations:**
- Ne comprend PAS bien le français
- À remplacer pour production

**Action:** Continuez le développement normalement

---

### Phase Production: Bascule Français

**Modèle cible:** `paraphrase-multilingual-MiniLM-L12-v2`

#### Étape 1: Collecter les Données Françaises
```bash
# Placer vos PDFs français dans:
data/stress_anxiety_pdfs/
├─ tcc_anxiete.pdf
├─ mindfulness_guide.pdf
├─ techniques_respiration.pdf
└─ ...
```

#### Étape 2: Extraire le Contenu
```bash
# TODO: Créer script d'extraction PDF → JSON
# Résultat: data/paragraphs_french.json
```

#### Étape 3: Basculer le Modèle (avec bon WiFi!)
```bash
python scripts/switch_to_multilingual.py
```

⚠️ **Prérequis:**
- ✅ Bonne connexion WiFi (téléchargement 420 MB)
- ✅ PDFs français prêts
- ✅ ~10-15 minutes de traitement

#### Étape 4: Re-tester
```bash
# Tester avec requêtes en français:
# "Comment gérer une crise d'anxiété?"
# "Quelles sont les techniques de respiration efficaces?"
```

---

## 📊 Comparaison des Modèles

| Caractéristique | all-MiniLM-L6-v2 (actuel) | multilingual (cible) |
|-----------------|---------------------------|----------------------|
| **Langue** | Anglais uniquement | Français + 50 langues |
| **Taille** | 80 MB | 420 MB |
| **Dimension** | 384 | 384 |
| **Téléchargement** | 2-5 min | 15-60 min (selon WiFi) |
| **Performance FR** | ⚠️ Moyenne | ✅ Excellente |
| **Usage** | Développement | Production |

---

## 🛠️ Comment Utiliser les Deux Modèles

### Option 1: Fichiers Séparés (Recommandé)
```
data/processed/
├─ dev_english/           # Pour développement
│   ├─ corpus_embeddings.pt
│   └─ corpus_metadata.json
│
└─ prod_french/           # Pour production
    ├─ corpus_embeddings.pt
    └─ corpus_metadata.json
```

### Option 2: Configuration Dynamique
```python
# Dans .env
EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
LANGUAGE=french

# Le code charge automatiquement le bon modèle
```

---

## ⏰ Quand Faire la Transition ?

**Transition vers multilingual QUAND:**
- ✅ Toutes les phases de dev sont terminées
- ✅ Le système RAG fonctionne bien
- ✅ Vous avez vos PDFs français
- ✅ Vous avez une bonne connexion WiFi
- ✅ Vous êtes prêts pour les tests finaux

**Rester en anglais SI:**
- ⏳ Encore en développement (Phase 2-6)
- 📡 WiFi trop lent
- 🧪 Tests de l'architecture système

---

## 🚨 Important

**Ne pas re-générer les embeddings maintenant** car:
1. Vous n'avez pas encore de données françaises
2. Le téléchargement prendrait 5h+
3. Ça ne servirait qu'à traiter les mêmes données anglaises

**Attendez d'avoir:**
- ✅ PDFs français sur l'anxiété
- ✅ Meilleure connexion
- ✅ Système RAG fonctionnel pour tester

---

## 📝 TODO Liste

- [ ] Terminer développement Phase 2-6 (avec modèle anglais)
- [ ] Collecter PDFs français sur anxiété
- [ ] Créer script extraction PDF → JSON
- [ ] Attendre bon WiFi
- [ ] Exécuter `switch_to_multilingual.py`
- [ ] Re-tester tout le système en français
