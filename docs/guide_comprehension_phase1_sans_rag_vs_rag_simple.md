# Guide de compréhension — Phase 1
## Sans RAG vs RAG Simple (avec exemples)

Ce document explique **concrètement** ce qui se passe dans votre projet avant la partie Agentic RAG.

---

## 1) Vue d’ensemble rapide

### A. Sans RAG
Flux:
1. Question utilisateur
2. Prompt système
3. Appel LLM direct
4. Réponse

👉 Le modèle répond avec ses connaissances générales.

### B. RAG simple
Flux:
1. Question utilisateur
2. Encodage de la question (embedding)
3. Recherche des chunks les plus proches (FAISS)
4. Construction d’un contexte à partir des chunks trouvés
5. Prompt final = contexte + question
6. Appel LLM
7. Réponse + sources

👉 Le modèle répond à partir de **vos documents**.

---

## 2) Comment le chunking est fait dans votre code

Fichier principal: `src/data_processing/chunker.py`

Paramètres utilisés dans le pipeline:
- `chunk_size = 500` caractères
- `chunk_overlap = 50` caractères
- `strategy = "recursive"`

### Logique recursive (ordre des séparateurs)
Le texte est découpé en essayant successivement:
1. `\n\n` (paragraphes)
2. `\n` (lignes)
3. `. ` (phrases)
4. ` ` (mots)
5. caractère par caractère (fallback)

Si un segment est encore trop grand, on descend au niveau suivant.

### Overlap
Chaque chunk (sauf le premier) reçoit les **50 derniers caractères** du chunk précédent.
But: éviter de perdre du contexte aux frontières.

---

## 3) Exemple simple de chunking

### Texte d’entrée (exemple)
"L’anxiété est une réponse normale au stress. Lorsqu’elle devient excessive, elle perturbe le sommeil et la concentration. La TCC est une approche efficace pour réduire les symptômes."

Supposons `chunk_size=80` et `overlap=15` (petite taille juste pour démonstration):

- **Chunk 1**: "L’anxiété est une réponse normale au stress."
- **Chunk 2**: "normale au stress. Lorsqu’elle devient excessive, elle perturbe le sommeil"
- **Chunk 3**: "perturbe le sommeil et la concentration. La TCC est une approche efficace"
- **Chunk 4**: "une approche efficace pour réduire les symptômes."

On voit que des morceaux se recouvrent pour garder la continuité.

---

## 4) Votre qualité de chunking actuelle (mesurée)

Mesure faite sur `data/processed/processed_chunks.json`:
- Nombre total: **2185 chunks**
- Min: **67** caractères
- Max: **551** caractères
- Moyenne: **462.2**
- Médiane: **496**
- Chunks entre 350 et 650 caractères: **87.28%**
- Chunks très petits (<120): **1.24%**

### Interprétation
✅ Globalement bon pour un RAG simple: la majorité des chunks est proche de la taille cible.  
⚠️ Points perfectibles:
- overlap en caractères (pas en tokens)
- `semantic_chunking` est un fallback vers sentence chunking
- découpage phrase regex basique

Conclusion pratique: **suffisamment optimal pour la phase actuelle**.

---

## 5) Embeddings, FAISS, top_k et métrique — explication détaillée

### A. C'est quoi un embedding ?

Un embedding = transformer un texte en **vecteur de nombres** (tableau de floats).

Exemple avec le modèle `paraphrase-multilingual-MiniLM-L12-v2` (dimension 384):

```
"L'anxiété perturbe le sommeil"  →  [0.12, -0.45, 0.33, 0.08, ...]  (384 nombres)
"La peur influence le comportement"  →  [0.11, -0.41, 0.29, 0.10, ...]
"La pizza est délicieuse"  →  [-0.73, 0.22, -0.15, 0.88, ...]
```

Les deux phrases proches sémantiquement ont des vecteurs proches.
La phrase sans rapport a un vecteur très différent.

Votre modèle produit **384 dimensions** (vérifié dans votre `embedder.py`):
- multilingue → français et anglais fonctionnent bien
- léger (420 MB) → tourne en local sans GPU
- qualité suffisante pour un RAG sur corpus médical/psychologie

---

### ❓ Mais les chunks n'ont pas tous la même taille — comment comparer leurs vecteurs ?

C'est une question fondamentale. La réponse: **la dimension du vecteur ne dépend PAS de la taille du texte**. Elle dépend uniquement du modèle.

Le modèle produit **toujours exactement 384 floats**, que le chunk fasse 67 ou 551 caractères.

**Comment c'est possible ? — Mean Pooling**

Internalement, le modèle fait:
1. Découpe le texte en tokens (mots ou sous-mots) → nombre variable
2. Calcule un vecteur 384D pour chaque token (via couches Transformer)
3. **Fait la moyenne de tous ces vecteurs** → un seul vecteur de 384D

```
Chunk court (67 chars):
"Anxiété et stress."
  → 4 tokens
  → moyenne(v_token1, v_token2, v_token3, v_token4)
  → [0.12, -0.45, 0.33, ...]   (384D)

Chunk long (551 chars):
"L'anxiété est une réponse normale au stress. Lorsqu'..."
  → 89 tokens
  → moyenne(v_token1, ..., v_token89)
  → [0.10, -0.43, 0.31, ...]   (384D)

→ Les deux sorties ont EXACTEMENT 384 dimensions
→ La cosine similarity fonctionne sans problème
```

**Conséquence sur la qualité :**

| Taille chunk | Effet sur le vecteur |
|---|---|
| Très court (<120 chars) | Vecteur peu riche, sens insuffisamment capturé |
| Optimal (350-550 chars) | Vecteur dense, représentation sémantique précise |
| Très long (>800 chars) | La moyenne dilue les détails, vecteur trop générique |

C'est exactement pourquoi votre cible de `chunk_size=500` est bien choisie: 87% de vos chunks tombent dans la zone optimale.

---

### B. Ce qui est fait dans votre code

**Offline** (une seule fois, lors de la préparation des données):
```python
# Pour chaque chunk du corpus:
embedding = model.encode(chunk_text)   # → vecteur de 384 floats
# Tous sauvegardés dans corpus_embeddings.pt
```

**Online** (à chaque question posée):
```python
# Dans retriever.py:
query_embedding = embedder.encode([question])   # → vecteur 384 floats
results = faiss_index.search(query_embedding, top_k)
```

---

### C. La métrique: Cosine Similarity (et pourquoi)

**Cosine Similarity** mesure l'angle entre deux vecteurs, pas leur distance.

Formule:
$$\text{cosine\_sim}(A, B) = \frac{A \cdot B}{\|A\| \times \|B\|}$$

Résultat entre **-1** et **+1**:
- `1.0` → même direction → très similaires
- `0.0` → perpendiculaires → sans rapport
- `-1.0` → sens opposé → antinomiques

**Exemple concret dans votre projet:**

| Question | Chunk comparé | Score cosine approx. |
|---|---|---|
| "symptômes de l'anxiété" | "Les symptômes incluent insomnie, palpitations..." | ~0.82 |
| "symptômes de l'anxiété" | "La TCC réduit les rechutes à long terme" | ~0.41 |
| "symptômes de l'anxiété" | "Les techniques culinaires françaises..." | ~0.06 |

**Pourquoi cosine et pas distance euclidienne ?**

- Distance euclidienne dépend de la longueur du vecteur → un long texte serait pénalisé par rapport à un court.
- Cosine normlise → compare la **direction** (sens sémantique), pas l'amplitude.
- Standard dans tous les systèmes RAG modernes.

Dans votre `vector_store.py`, ligne clé:
```python
faiss.normalize_L2(embeddings)    # normalise → longueur = 1
self.index = faiss.IndexFlatIP(self.embedding_dim)  # IP = Inner Product
# Inner Product sur vecteurs normalisés = cosine similarity exacte
```

---

### D. Comment fonctionne FAISS

FAISS (Facebook AI Similarity Search) = bibliothèque de recherche vectorielle ultra-rapide.

**Ce qui se passe à l'indexation:**
```
2185 vecteurs de 384 dim → stockés dans un tableau numpy
FAISS les organise pour rendre la recherche rapide
```

**Ce qui se passe à chaque question:**
```
1. Query → encoder → vecteur de 384 floats
2. FAISS calcule la similarité avec tous les 2185 vecteurs
3. Retourne les indices des top_k meilleurs scores
```

**IndexFlatIP** (votre implémentation) = recherche exacte (brute force).  
Cela est approprié pour 2185 vecteurs.  
Pour des millions de vecteurs, on passerait à `IndexIVFFlat` (approximée mais plus rapide).

---

### E. C'est quoi top_k ?

`top_k` = nombre de chunks à récupérer.

Dans votre code:
- `chatbot_avec_rag.py` → `top_k=15` (beaucoup, pour couverture maximale)
- `chatbot_avec_rag_simple.py` → `top_k=5` + seuil `score_threshold=0.3`

**Exemple avec top_k=3:**

Question: "Comment traiter l'anxiété sociale ?"

```
Rank 1: score=0.79 → "L'anxiété sociale se traite par exposition graduelle..."
Rank 2: score=0.73 → "La TCC inclut des exercices de désensibilisation..."
Rank 3: score=0.61 → "Les groupes thérapeutiques améliorent les habiletés sociales..."
```

Ces 3 chunks forment le **contexte** injecté dans le prompt.

**Quel top_k choisir ?**

| top_k | Avantage | Inconvénient |
|---|---|---|
| 3 | Prompt court, ciblé | Peut manquer des infos |
| 5 | Bon compromis | Standard pour RAG simple |
| 10-15 | Couverture maximale | Prompt très long, dilue le contexte |

Votre `chatbot_avec_rag.py` utilise `top_k=15` avec un prompt spécial qui demande au LLM de fusionner sans répétition — c'est une stratégie valide mais coûteuse en tokens.

---

### F. Le seuil (score_threshold)

Dans `chatbot_avec_rag_simple.py`:
```python
retriever.retrieve(query, top_k=5, score_threshold=0.3)
```

Si un chunk a un score cosine < 0.3, il est ignoré même s'il est dans le top-k.  
But: éviter d'injecter des chunks non pertinents qui pollueraient la réponse.

Valeur typique: `0.3` à `0.5` selon la précision voulue.

---

### G. Résumé visuel du flux embedding→retrieval

```
[Question]
    ↓  encode() → vecteur Q (384 floats)
    
[FAISS Index]  (2185 vecteurs de 384 floats)
    ↓  cosine_similarity(Q, chaque chunk)
    ↓  top_k meilleurs scores
    
[Chunk 1: score=0.81]  ─┐
[Chunk 2: score=0.74]   ├──→  contexte injecté dans prompt
[Chunk 3: score=0.65]  ─┘
    
[LLM]
    ↓  génère réponse ancrée sur le contexte
    
[Réponse + sources affichées]
```

---

## 6) Ce que RAG simple ajoute exactement par rapport au sans RAG

## Sans RAG (`chatbot_sans_rag_ui.py`)
- Appel direct à Groq (`call_groq(prompt)`)
- Pas de retrieval
- Pas de chunks
- Pas de sources

## RAG simple (`chatbot_avec_rag.py` / `chatbot_avec_rag_simple.py`)
- Chargement de:
  - `processed_chunks.json`
  - `corpus_embeddings.pt`
  - `corpus_metadata.json`
- Indexation/recherche via FAISS (`src/retrieval/vector_store.py`)
- Retriever sémantique (`src/retrieval/retriever.py`)
- Injection du contexte dans le prompt
- Affichage des sources utilisées

---

## 6) Exemple comparatif sur la même question

Question: "Quels sont les critères DSM-5 du TAG ?"

### Sans RAG
- Réponse possible: générale, parfois incomplète
- Peut oublier des critères ou les reformuler approximativement
- Aucune traçabilité documentaire

### RAG simple
- Récupère les passages les plus proches dans vos chunks
- Le prompt force la réponse à partir du contexte
- Donne une réponse mieux alignée avec vos documents
- Affiche les sources `[Document X]`

---

## 7) Pseudo-code minimal (pour mémoriser)

### Sans RAG
```python
prompt = system_prompt + question
reponse = llm.invoke(prompt)
return reponse
```

### RAG simple
```python
q_emb = embed(question)
chunks = faiss.search(q_emb, top_k)
context = concat(chunks)
prompt = build_prompt(context, question)
reponse = llm.invoke(prompt)
return reponse, sources
```

---

## 8) Checklist compréhension (avant Agentic RAG)

Si vous maîtrisez ces points, vous êtes prêt:
- [ ] Je sais expliquer la différence sans RAG vs RAG simple en 30 secondes
- [ ] Je sais où se fait le chunking dans le code
- [ ] Je sais pourquoi l’overlap est utile
- [ ] Je sais comment FAISS récupère les chunks pertinents
- [ ] Je sais ce que le prompt RAG ajoute au prompt simple
- [ ] Je sais interpréter les sources affichées dans l’UI

---

## 9) Résumé final

- Le **sans RAG** est un baseline rapide mais non ancré sur votre corpus.
- Le **RAG simple** ajoute récupération documentaire + contexte + traçabilité.
- Votre chunking actuel est **globalement solide** pour cette phase.
- Vous pouvez passer à l’Agentic RAG une fois ces mécanismes bien maîtrisés.
