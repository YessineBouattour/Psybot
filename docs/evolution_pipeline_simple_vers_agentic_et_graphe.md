# Evolution du Pipeline: du RAG Simple (Text) vers Agentic RAG + Graphe

## Objectif du document
Ce document explique:
1. Comment on passe d'un pipeline RAG simple base uniquement sur le texte vers un pipeline multi-agents plus robuste.
2. Pourquoi et quand ajouter un module graphe.
3. Le compromis qualite/cout/complexite, surtout avec contrainte d'APIs gratuites.

---

## 1) Point de depart: Pipeline RAG simple (Text-only)

## Flux minimal
1. Question utilisateur
2. Embedding de la question
3. Recherche vectorielle dans la base texte (FAISS/Chroma)
4. Selection Top-K chunks
5. Generation de la reponse par LLM

## Avantages
- Facile a implementer et maintenir.
- Rapide a executer.
- Faible cout (surtout si embeddings pre-calcules localement).

## Limites
- Sensible aux questions mal formulees.
- Difficile de gerer les questions complexes multi-aspects.
- Pas de verification explicite de la qualite/surete.
- Raisonnement relationnel limite (qui est lie a quoi).

---

## 2) Evolution vers un pipeline Agentic RAG (toujours text-first)

Le principe de l'evolution n'est pas de remplacer le pipeline simple, mais de lui ajouter des etapes de controle et de specialisation.

## Pipeline evolue (text-first)
1. QueryReformulator
2. ComplexityAnalyzer
3. SubQueryDecomposer (si question complexe)
4. SemanticRetriever (texte)
5. ChunkReRanker
6. ResponseGenerator
7. ResponseCritic (avec boucle de regeneration si score faible)

## Ce que chaque ajout apporte
- Reformulation: augmente la qualite de retrieval.
- Analyse de complexite: evite de decomposer inutilement (economise tokens/cout).
- Decomposition: meilleure couverture pour les questions multi-parties.
- Re-ranking: plus de precision dans les sources finales.
- Critique: meilleure fiabilite et securite avant livraison.

---

## 3) Notion de graphe: explication simple

Un graphe est une representation de connaissances sous forme de reseau:
- Noeuds = entites (ex: anxiete chronique, TCC, symptomes, technique respiratoire).
- Aretes = relations (ex: traite, associe_a, aggrave_par, recommande_par).

Exemple tres simple:
- Noeud A: Anxiete chronique
- Noeud B: TCC
- Relation: TCC --traite--> Anxiete chronique

Avec du texte seul, on recupere des passages pertinents.
Avec le graphe, on suit des relations explicites entre entites.

---

## 4) Quand utiliser Text Retrieval vs Graph Retrieval

## Text Retrieval (par defaut)
A utiliser pour:
- Definitions
- Explications generales
- Conseils pratiques
- Questions simples

Exemple: "Qu'est-ce que l'anxiete generalisee?"

## Graph Retrieval (conditionnel)
A utiliser pour:
- Questions relationnelles
- Questions "qui est lie a quoi"
- Questions cause-effet multi-etapes
- Besoin de chemin de raisonnement explicite

Exemple: "Quels symptomes sont associes au stress chronique et quelles techniques ciblent chaque symptome?"

---

## 5) Pourquoi le mode hybride est le meilleur compromis (APIs gratuites)

Avec la contrainte APIs gratuites, il faut minimiser les appels LLM couteux.

Strategie recommandee:
1. Text-first par defaut (peu couteux, rapide).
2. Activation du graphe seulement si la question l'exige.
3. Critique legere (1 passe, regeneration max 1-2 fois).
4. Embeddings et index en local autant que possible.

Resultat:
- Cout controle
- Latence raisonnable
- Qualite meilleure que RAG simple
- Complexite technique progressive (sans sur-ingenierie)

---

## 6) Comparaison rapide

| Critere | RAG Simple (Text) | Agentic Text-first | Agentic Hybride Text+Graph |
|---|---|---|---|
| Precision | Moyenne | Bonne | Tres bonne |
| Cout API | Faible | Moyen | Moyen a eleve (si graphe frequent) |
| Latence | Faible | Moyenne | Moyenne a elevee |
| Complexite implementation | Faible | Moyenne | Elevee |
| Questions relationnelles | Limite | Limite a moyenne | Excellente |
| Controle qualite/surete | Faible | Bon (critic) | Bon a tres bon |

---

## 7) Plan d'adoption progressif conseille

1. Stabiliser le pipeline RAG simple text-only (baseline metrics).
2. Ajouter reformulation + critic (gains rapides de qualite).
3. Ajouter analyse de complexite + decomposition conditionnelle.
4. Ajouter graphe en mode optionnel (feature flag) pour questions relationnelles.
5. Mesurer precision/cout/latence et ajuster les seuils de routage.

---

## 8) Message a presenter a l'encadrant

"Nous avons commence par un RAG simple textuel pour etablir une baseline robuste. Ensuite, nous avons evolue vers une architecture agentique qui conserve le texte comme voie principale, ajoute des etapes de qualite (reformulation, re-ranking, critique), et active le graphe seulement pour les questions relationnelles complexes. Cette strategie permet d'ameliorer la precision sans exploser les couts, ce qui est coherent avec une contrainte d'APIs gratuites."