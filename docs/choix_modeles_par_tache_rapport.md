# Choix des modèles LLM par tâche dans l’architecture Agentic RAG

## Contexte
Ce document justifie la sélection des modèles de langage pour chaque tâche du pipeline Agentic RAG dédié à l’accompagnement autour de l’anxiété. L’objectif est d’optimiser simultanément la qualité des réponses, la robustesse, le coût d’exploitation et la vitesse d’inférence.

Architecture considérée : 7 agents (3 pré-retrieval, 2 retrieval/post-retrieval, 1 génération, 1 critique).

---

## 1) Répartition recommandée (configuration hybride)

| Étape | Agent | Modèle retenu | Provider | Rôle principal |
|---|---|---|---|---|
| Pré-retrieval 1 | Query Reformulation | `llama-3.1-8b-instant` | Groq | Reformuler la requête avec terminologie claire |
| Pré-retrieval 2 | Complexity Analyzer | `deepseek-chat` (V3) | DeepSeek | Classer simple/complexe, extraire aspects |
| Pré-retrieval 3 | Sub-query Decomposer | `deepseek-chat` (V3) | DeepSeek | Décomposer en sous-questions non redondantes |
| Retrieval | Semantic Retriever | Embeddings `paraphrase-multilingual-MiniLM-L12-v2` + FAISS | Local | Recherche vectorielle top-k |
| Post-retrieval | Chunk Re-ranker | Algorithme local (non-LLM) | Local | Réordonner les chunks selon pertinence |
| Génération | RAG Response Generator | `llama-3.3-70b-versatile` | Groq | Produire la réponse finale contextualisée |
| Critique | Response Critic (Self-RAG) | `gemini-2.0-flash` | Google | Vérifier cohérence, sécurité, hallucinations |

---

## 2) Justification détaillée par tâche

### 2.1 Query Reformulation — Groq `llama-3.1-8b-instant`
**Pourquoi ce choix :**
- Très faible latence, adaptée aux opérations fréquentes de pré-traitement.
- Coût nul en pratique sur le plan gratuit Groq, idéal pour itérations de développement.
- Qualité suffisante pour normaliser des requêtes utilisateur courtes/moyennes.

**Pourquoi pas un modèle plus lourd :**
- Le gain qualitatif d’un grand modèle est marginal pour une tâche de reformulation simple.
- La contrainte principale ici est la vitesse, pas le raisonnement profond.

### 2.2 Complexity Analyzer — DeepSeek `deepseek-chat`
**Pourquoi ce choix :**
- Excellentes performances sur les tâches de raisonnement structuré (classification + extraction d’aspects).
- Bon comportement sur des sorties formatées (JSON), utile pour piloter l’orchestrateur.
- Rapport qualité/coût favorable.

**Point d’attention :**
- Utilisation recommandée sur texte non sensible ou anonymisé (voir section conformité).

### 2.3 Sub-query Decomposer — DeepSeek `deepseek-chat`
**Pourquoi ce choix :**
- Très bon découpage logique des questions complexes en sous-objectifs.
- Réduction de la redondance entre sous-questions.
- Cohérence forte avec l’étape Complexity Analyzer (même “style” de raisonnement).

### 2.4 Semantic Retriever — Embeddings locaux + FAISS
**Pourquoi sans LLM :**
- La récupération de contexte est un problème de similarité vectorielle, pas de génération.
- Solution locale déterministe, stable et économique.
- Faible latence et maîtrise complète des données.

### 2.5 Chunk Re-ranker — algorithme local non-LLM
**Pourquoi sans LLM :**
- Re-ranking multi-critères déterministe (similarité, mots-clés, longueur, diversité).
- Réplicabilité expérimentale élevée (important en contexte académique).
- Évite un coût d’inférence supplémentaire sans perte significative sur ce cas d’usage.

### 2.6 RAG Response Generator — Groq `llama-3.3-70b-versatile`
**Pourquoi ce choix :**
- Meilleure qualité de génération que les petits modèles sur explications longues.
- Bonne balance qualité/latence en environnement de démonstration.
- Performant pour fusionner plusieurs chunks en réponse unique cohérente.

### 2.7 Response Critic (Self-RAG) — Gemini `gemini-2.0-flash`
**Pourquoi ce choix :**
- Très bon comportement en évaluation multi-critères (cohérence, sécurité, clarté).
- Sorties généralement plus propres pour la critique structurée.
- Bon candidat pour détecter incohérences et hallucinations avant réponse finale.

**Pourquoi placer Gemini ici en priorité :**
- La critique est l’étape de contrôle qualité la plus sensible.
- Le gain de robustesse est plus utile ici que sur reformulation/retrieval.

---

## 3) Pourquoi une architecture multi-fournisseurs

L’approche mono-modèle est simple mais sous-optimale. La répartition par tâche permet :
- **Optimisation performance** : modèle rapide pour pré-traitement, modèle plus fort pour critique.
- **Optimisation coût** : éviter d’utiliser un modèle “premium” sur des tâches triviales.
- **Résilience** : possibilité de bascule (fallback) si un provider est indisponible.
- **Évaluation scientifique** : comparaison plus fine de l’apport de chaque composant.

---

## 4) Conformité et gestion du risque (données santé)

### Principe recommandé
- Éviter d’envoyer des informations personnelles identifiantes (PII) à des APIs externes.
- Mettre en place une anonymisation en amont (nom, téléphone, email, adresse, identifiants).
- Journaliser uniquement des traces techniques minimales.

### Position pratique sur DeepSeek
- **Acceptable** pour tâches de raisonnement (complexité/décomposition) sur texte anonymisé.
- **À éviter par défaut** pour génération clinique finale sur données potentiellement sensibles.
- Activer via un flag explicite (ex. `ALLOW_DEEPSEEK=true`) pour contrôle opérationnel.

---

## 5) Configuration de référence pour l’implémentation

```env
# Pré-retrieval
PRERETRIEVAL_PROVIDER=groq
PRERETRIEVAL_MODEL=llama-3.1-8b-instant

COMPLEXITY_PROVIDER=deepseek
COMPLEXITY_MODEL=deepseek-chat

DECOMPOSITION_PROVIDER=deepseek
DECOMPOSITION_MODEL=deepseek-chat

# Generation
GENERATION_PROVIDER=groq
GENERATION_MODEL=llama-3.3-70b-versatile

# Critique
CRITIQUE_PROVIDER=gemini
CRITIQUE_MODEL=gemini-2.0-flash

# Gouvernance
ALLOW_DEEPSEEK=true
ANONYMIZE_INPUT=true
```

---

## 6) Alternatives (selon contraintes)

### Option A — 100% Groq (simplicité maximale)
- Pré-retrieval : `llama-3.1-8b-instant`
- Génération : `llama-3.3-70b-versatile`
- Critique : `llama-3.3-70b-versatile`

**Avantage :** intégration simple, coût faible, excellente latence.  
**Limite :** critique souvent moins fine qu’avec Gemini.

### Option B — 100% “privacy-first” local
- Retrieval/re-ranking locaux (déjà en place)
- Modèles locaux (Ollama) pour génération/critique

**Avantage :** maîtrise complète des données.  
**Limite :** qualité et latence dépendantes du matériel.

---

## 7) Conclusion

La répartition retenue (Groq + DeepSeek + Gemini) est justifiée par une logique de spécialisation des tâches :
- **Groq** pour la vitesse et la génération robuste.
- **DeepSeek** pour le raisonnement structuré (complexité/décomposition).
- **Gemini** pour la **critique** où le gain qualitatif est le plus important.
- **Local** pour retrieval/re-ranking afin de préserver la stabilité et le coût.

Cette stratégie fournit un compromis solide entre qualité scientifique, efficacité opérationnelle et contrôle du risque pour un chatbot orienté santé mentale.
