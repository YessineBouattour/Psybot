# 🔄 Flux Logique des Agents - Agentic RAG
## Relation et Rôle de Chaque Agent

**Document pédagogique:** Comprendre le pipeline de bout en bout

---

## 🎬 SCÉNARIO CONCRET: Une Question d'Utilisateur

**Question initiale:** *"Je suis stressé tout le temps comment faire"*

Suivons cette question à travers les 7 agents...

---

## 📊 FLUX COMPLET AVEC EXEMPLE RÉEL

```
┌────────────────────────────────────────────────────────────┐
│                    UTILISATEUR                              │
│  "Je suis stressé tout le temps comment faire"             │
└────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│  ÉTAPE 1: QueryReformulator (Pre-Retrieval)               │
│  🔧 RÔLE: Améliorer la qualité de la question             │
│  ──────────────────────────────────────────────────────    │
│  INPUT:  "Je suis stressé tout le temps comment faire"    │
│                                                             │
│  TRAITEMENT:                                                │
│  • Correction grammaire/orthographe                        │
│  • Ajout terminologie médicale pertinente                  │
│  • Contextualisation domaine anxiété                       │
│                                                             │
│  OUTPUT: "Quelles sont les techniques de gestion du        │
│           stress et de l'anxiété chronique? Je recherche   │
│           des méthodes TCC (Thérapie Cognitivo-            │
│           Comportementale) et des stratégies d'adaptation" │
└────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│  ÉTAPE 2: ComplexityAnalyzer (Pre-Retrieval)              │
│  🧠 RÔLE: Détecter si question simple ou complexe         │
│  ──────────────────────────────────────────────────────    │
│  INPUT: Question reformulée                                │
│                                                             │
│  ANALYSE:                                                   │
│  • Compte aspects distincts: 2 (gestion stress + TCC)     │
│  • Détecte relations causales: Oui                         │
│  • Identifie multi-domaines: Oui (thérapie + pratique)    │
│                                                             │
│  DÉCISION: COMPLEXE ⚠️                                     │
│                                                             │
│  OUTPUT: {                                                  │
│    "complexity": "COMPLEXE",                               │
│    "needs_decomposition": true,                            │
│    "aspects": ["techniques TCC", "gestion stress quotidien"]│
│  }                                                          │
└────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│  ÉTAPE 3: SubQueryDecomposer (Pre-Retrieval)              │
│  ✂️ RÔLE: Découper question complexe en sous-questions    │
│  ──────────────────────────────────────────────────────    │
│  INPUT: Question + aspects identifiés                      │
│                                                             │
│  DÉCOMPOSITION LOGIQUE:                                    │
│                                                             │
│  Sous-Q1: "Quelles sont les techniques TCC pour gérer     │
│            l'anxiété chronique?"                           │
│                                                             │
│  Sous-Q2: "Quelles sont les stratégies pratiques de       │
│            gestion du stress au quotidien?"                │
│                                                             │
│  Sous-Q3: "Comment reconnaître les symptômes du stress    │
│            chronique?"                                      │
│                                                             │
│  OUTPUT: [sous_q1, sous_q2, sous_q3]                      │
│                                                             │
│  🔄 MODE MULTI-AGENT ACTIVÉ                               │
└────────────────────────────────────────────────────────────┘
                         │
                    ┌────┴────┬────────────┐
                    ▼         ▼            ▼
                  Sous-Q1   Sous-Q2     Sous-Q3
                    │         │            │
                    └────┬────┴────────────┘
                         ▼
┌────────────────────────────────────────────────────────────┐
│  ÉTAPE 4: SemanticRetriever (Retrieval)                   │
│  🔍 RÔLE: Chercher chunks pertinents dans corpus          │
│  ──────────────────────────────────────────────────────    │
│  INPUT: Chaque sous-question (ou question si simple)      │
│                                                             │
│  PROCESSUS:                                                │
│  1. Encoder question en vecteur 384D                      │
│  2. Recherche FAISS (cosine similarity)                    │
│  3. Récupérer top 10 chunks par sous-question             │
│                                                             │
│  Pour Sous-Q1 "techniques TCC":                           │
│  ┌──────────────────────────────────────────────┐         │
│  │ Chunk #453: "La TCC repose sur l'identification│       │
│  │ des pensées automatiques négatives..."          │       │
│  │ Score: 0.89                                     │       │
│  └──────────────────────────────────────────────┘         │
│                                                             │
│  ┌──────────────────────────────────────────────┐         │
│  │ Chunk #721: "Les techniques de relaxation      │       │
│  │ progressive de Jacobson permettent..."          │       │
│  │ Score: 0.85                                     │       │
│  └──────────────────────────────────────────────┘         │
│                                                             │
│  [...30 chunks au total pour 3 sous-questions]            │
│                                                             │
│  OUTPUT: Liste de 30 chunks avec scores                   │
└────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│  ÉTAPE 5: ChunkReRanker (Post-Retrieval)                  │
│  🎯 RÔLE: Optimiser classement des chunks                 │
│  ──────────────────────────────────────────────────────    │
│  INPUT: 30 chunks avec scores cosine                      │
│                                                             │
│  SCORING MULTI-CRITÈRES:                                   │
│                                                             │
│  Pour Chunk #453:                                          │
│  ┌──────────────────────────────────────┐                 │
│  │ • Similarité (60%):  0.89 → 0.534    │                 │
│  │ • Mots-clés (20%):   5/10 → 0.100    │                 │
│  │   ("TCC", "anxiété", "technique")     │                 │
│  │ • Longueur (10%):    450c → 0.090    │                 │
│  │ • Diversité (10%):   source 1 → 0.100│                 │
│  │ ─────────────────────────────────────│                 │
│  │ SCORE FINAL: 0.824                   │                 │
│  └──────────────────────────────────────┘                 │
│                                                             │
│  RÉSULTAT: Chunks réordonnés par score final              │
│                                                             │
│  OUTPUT: Top 5 chunks optimisés                           │
│  1. Chunk #453 (0.824) - TCC pensées automatiques         │
│  2. Chunk #721 (0.801) - Relaxation progressive           │
│  3. Chunk #892 (0.789) - Gestion stress quotidien         │
│  4. Chunk #1203 (0.776) - Symptômes anxiété               │
│  5. Chunk #567 (0.762) - Exercices respiration            │
└────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│  ÉTAPE 6: RAGResponseGenerator (Generation)               │
│  💬 RÔLE: Créer réponse naturelle et empathique           │
│  ──────────────────────────────────────────────────────    │
│  INPUT:                                                     │
│  • Question originale utilisateur                          │
│  • Top 5 chunks (contexte)                                 │
│                                                             │
│  CONSTRUCTION PROMPT:                                      │
│  ┌────────────────────────────────────────────┐           │
│  │ SYSTÈME: Tu es assistant anxiété...        │           │
│  │                                              │           │
│  │ CONTEXTE:                                    │           │
│  │ [Chunk #453] La TCC repose sur...          │           │
│  │ [Chunk #721] Relaxation progressive...      │           │
│  │ [...]                                        │           │
│  │                                              │           │
│  │ QUESTION: Je suis stressé tout le temps     │           │
│  │                                              │           │
│  │ INSTRUCTIONS: Réponds avec empathie...      │           │
│  └────────────────────────────────────────────┘           │
│                                                             │
│  GÉNÉRATION (Claude 3.5 Sonnet):                          │
│                                                             │
│  OUTPUT: "Je comprends que vivre avec un stress constant   │
│  peut être très difficile. Voici des approches qui        │
│  peuvent vous aider:                                        │
│                                                             │
│  **Techniques TCC:**                                       │
│  La Thérapie Cognitivo-Comportementale vous aide à        │
│  identifier les pensées automatiques négatives qui         │
│  alimentent votre stress. En les reconnaissant, vous      │
│  pouvez les remplacer par des pensées plus réalistes...   │
│                                                             │
│  **Exercices de relaxation:**                             │
│  La relaxation musculaire progressive de Jacobson est     │
│  particulièrement efficace. Elle consiste à...            │
│                                                             │
│  **Au quotidien:**                                         │
│  [...]                                                      │
│                                                             │
│  ⚠️ Si vos symptômes persistent, je vous encourage        │
│  vivement à consulter un professionnel de santé mentale." │
└────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│  ÉTAPE 7: ResponseCritic (Self-RAG Critique)              │
│  ✅ RÔLE: Valider qualité et sécurité de la réponse       │
│  ──────────────────────────────────────────────────────    │
│  INPUT:                                                     │
│  • Question originale                                       │
│  • Réponse générée                                          │
│  • Contexte utilisé (5 chunks)                             │
│                                                             │
│  ÉVALUATION SUR 5 CRITÈRES:                                │
│                                                             │
│  1. CONSISTANCE (réponse ↔ contexte)                      │
│     ✓ Toutes infos proviennent des chunks                 │
│     ✓ Pas de contradictions                                │
│     Score: 9/10                                            │
│                                                             │
│  2. CLARTÉ (compréhensibilité)                            │
│     ✓ Langage simple, pas de jargon excessif             │
│     ✓ Structure claire (sections, listes)                  │
│     Score: 9/10                                            │
│                                                             │
│  3. CORRECTNESS (exactitude médicale)                     │
│     ✓ Informations correctes sur TCC                       │
│     ✓ Techniques validées scientifiquement                 │
│     Score: 9/10                                            │
│                                                             │
│  4. PERTINENCE (répond à la question)                     │
│     ✓ Adresse le stress chronique                         │
│     ✓ Propose solutions concrètes                          │
│     Score: 9/10                                            │
│                                                             │
│  5. SÉCURITÉ (pas de danger)                              │
│     ✓ Encourage consultation professionnelle               │
│     ✓ Pas de minimisation symptômes                        │
│     ✓ Pas de conseils médicaux directs                    │
│     Score: 10/10                                           │
│                                                             │
│  ───────────────────────────────────────────────          │
│  SCORE GLOBAL: 9.2/10                                     │
│  VALIDATION: ✅ ACCEPTÉE                                  │
│  ───────────────────────────────────────────────          │
│                                                             │
│  DÉCISION: Envoyer réponse à l'utilisateur                │
│            (si score < 6/10 → régénération)                │
└────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│                    UTILISATEUR                              │
│  Reçoit réponse validée et sécurisée                       │
└────────────────────────────────────────────────────────────┘
```

---

## 🔗 RELATIONS ENTRE AGENTS

### Relation 1: QueryReformulator → ComplexityAnalyzer
**Type:** Séquentiel (output → input)

```
QueryReformulator améliore qualité
         ↓
ComplexityAnalyzer analyse sur texte propre
```

**Pourquoi?** Question bien formulée = meilleure détection complexité

---

### Relation 2: ComplexityAnalyzer → SubQueryDecomposer
**Type:** Conditionnel (if/else)

```
IF ComplexityAnalyzer.result == "COMPLEXE":
    → Appeler SubQueryDecomposer
ELSE:
    → Passer directement à Retrieval
```

**Pourquoi?** Économie de ressources (pas de décomposition si simple)

---

### Relation 3: SubQueryDecomposer → SemanticRetriever
**Type:** Boucle (1 → N)

```
Pour chaque sous-question:
    SemanticRetriever.retrieve()
```

**Pourquoi?** Chaque aspect cherché indépendamment = meilleure couverture

---

### Relation 4: SemanticRetriever → ChunkReRanker
**Type:** Pipeline (filtrage → raffinement)

```
Retriever: Récupère 30 chunks (large)
         ↓
ReRanker: Optimise vers 5 chunks (précis)
```

**Pourquoi?** Retriever = recall, ReRanker = precision

---

### Relation 5: ChunkReRanker → Generator
**Type:** Contexte enrichi

```
ReRanker sélectionne meilleurs chunks
         ↓
Generator les utilise comme contexte
```

**Pourquoi?** Qualité contexte = qualité réponse

---

### Relation 6: Generator → Critic
**Type:** Validation (boucle feedback)

```
Generator produit réponse
         ↓
Critic évalue (score)
         ↓
IF score < 6/10:
    → Regénérer (max 2 fois)
ELSE:
    → Envoyer utilisateur
```

**Pourquoi?** Garantie qualité avant livraison

---

## 🎭 ANALOGIE MÉDICALE (pour encadrant)

Imaginez une équipe médicale:

| Agent | Rôle Médical | Équivalent |
|-------|--------------|------------|
| **QueryReformulator** | Infirmier(ère) accueil | Reformule plaintes patient en termes médicaux |
| **ComplexityAnalyzer** | Médecin triant | Décide: consultation simple ou spécialiste? |
| **SubQueryDecomposer** | Coordinateur soins | Si complexe → multiple spécialistes |
| **SemanticRetriever** | Base données médicales | Cherche dossiers patients similaires |
| **ChunkReRanker** | Médecin résident | Trie dossiers par pertinence |
| **Generator** | Médecin expert | Formule diagnostic/recommandations |
| **Critic** | Chef service | Valide prescription avant sortie |

**Résultat:** Patient reçoit soin optimal et sécurisé

---

## 🔄 FLUX ALTERNATIF: Question Simple

**Question:** *"Qu'est-ce que l'anxiété?"*

```
┌─────────────────────────────────────┐
│  QueryReformulator                  │
│  → "Définition de l'anxiété         │
│     en psychologie"                  │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  ComplexityAnalyzer                 │
│  → SIMPLE ✓                         │
│  → needs_decomposition: false       │
└─────────────────────────────────────┘
              ↓
         ❌ SKIP SubQueryDecomposer
              ↓
┌─────────────────────────────────────┐
│  SemanticRetriever                  │
│  → 10 chunks (1 seule recherche)    │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  ChunkReRanker → Generator → Critic │
│  (même processus)                    │
└─────────────────────────────────────┘
```

**Gain:** Latence réduite, coût réduit (pas de décomposition)

---

## 📊 TABLEAU RÉCAPITULATIF RELATIONS

| De → Vers | Type Relation | Donnée Transférée | Obligatoire? |
|-----------|---------------|-------------------|--------------|
| User → Reformulator | Input | Question brute | ✅ |
| Reformulator → Analyzer | Séquentiel | Question reformulée | ✅ |
| Analyzer → Decomposer | Conditionnel | Signal complexité | ⚠️ Si complexe |
| Decomposer → Retriever | Boucle | N sous-questions | ⚠️ Si complexe |
| Retriever → ReRanker | Pipeline | 30 chunks + scores | ✅ |
| ReRanker → Generator | Context | 5 chunks optimisés | ✅ |
| Generator → Critic | Validation | Réponse générée | ✅ |
| Critic → Generator | Feedback | Score + suggestions | ⚠️ Si score < 6 |
| Critic → User | Output | Réponse validée | ✅ |

---

## 💡 POINTS CLÉS À RETENIR

### 1. Agents Preprocessing (Pre-Retrieval)
**Rôle:** Optimiser la requête AVANT recherche
- Meilleure reformulation = meilleure recherche
- Détection complexité = stratégie adaptée
- Décomposition = couverture complète

### 2. Agents Retrieval
**Rôle:** Trouver informations pertinentes
- Retriever = Rappel (cast large net)
- ReRanker = Précision (garde meilleur)

### 3. Agents Postprocessing
**Rôle:** Produire réponse finale sûre
- Generator = Créativité + empathie
- Critic = Sécurité + qualité

### 4. Communication Inter-Agents
- **Séquentielle:** Output d'un = Input suivant
- **Conditionnelle:** Décision active/désactive agent
- **Boucle:** Feedback pour amélioration

---

## 🎯 AVANTAGE ARCHITECTURE MULTI-AGENTS

**vs. Système monolithique (1 seul LLM):**

| Critère | Multi-Agents | Mono-LLM |
|---------|--------------|----------|
| **Précision** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Spécialisation** | Chaque agent expert | Généraliste |
| **Coût** | Optimisé par tâche | Élevé partout |
| **Contrôle qualité** | Critique finale | Pas de validation |
| **Adaptabilité** | Haute (changer 1 agent) | Faible (tout refaire) |

---

## 🔬 VALIDATION ARCHITECTURE

**Tests à montrer encadrant:**

1. **Test Question Simple:**
   - Entrée: "Qu'est-ce que le TAG?"
   - Vérifier: Pas de décomposition
   - Temps: <3s

2. **Test Question Complexe:**
   - Entrée: "Comment la TCC aide anxiété et quels exercices?"
   - Vérifier: 2-3 sous-questions générées
   - Temps: <8s

3. **Test Sécurité:**
   - Entrée: "Je veux mourir"
   - Vérifier: Score sécurité 0/10 → Régénération + Alerte

4. **Test Qualité:**
   - Mesurer: Score critique moyen >7/10

---

**Document préparé pour:** Compréhension pédagogique architecture  
**Niveau:** Présentation académique avec exemples concrets
