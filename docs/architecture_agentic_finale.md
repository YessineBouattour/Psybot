# Architecture Agentic Finale et Modeles par Tache

## 1. Vue d'ensemble

Le systeme final suit un pipeline Agentic RAG en 7 etapes:

1. Pre-Retrieval: Reformulation de la requete
2. Pre-Retrieval: Analyse de complexite
3. Pre-Retrieval: Decomposition en sous-requetes (si necessaire)
4. Retrieval Routing: Choix text_only vs text_graph
5. Retrieval: Recherche semantique dans le vector store
6. Post-Retrieval: Re-ranking des chunks
7. Generation + Critique: Reponse finale et validation

Ce design conserve la robustesse du RAG texte tout en preparant l'activation progressive du mode graphe.

## 2. Architecture Detaillee

### Etape 1 - Query Reformulator
- Objectif: normaliser et enrichir la requete utilisateur
- Entree: question utilisateur brute
- Sortie: requete reformulee orientee retrieval
- Fichier: src/agents/pre_retrieval.py

### Etape 2 - Query Complexity Analyzer
- Objectif: detecter si la requete est SIMPLE ou COMPLEXE
- Entree: requete reformulee
- Sortie: niveau de complexite + aspects
- Fichier: src/agents/pre_retrieval.py

### Etape 3 - SubQuery Decomposer
- Objectif: decomposer en sous-questions pour le mode multi-agent
- Condition: active si besoin de decomposition
- Sortie: liste de sous-requetes
- Fichier: src/agents/pre_retrieval.py

### Etape 4 - Retrieval Router
- Objectif: choisir entre text_only et text_graph
- Regles:
  - text_graph: question relationnelle (cause-effet, influence, interaction, etc.)
  - text_only: question explicative simple
- Fallback: si graphe non branche, execution en texte avec metadata de routage
- Fichier: src/agents/pre_retrieval.py

### Etape 5 - Semantic Retrieval
- Objectif: recuperer les passages les plus pertinents
- Mecanisme: embeddings + FAISS
- Sortie: top-k chunks
- Fichiers: src/retrieval/retriever.py, src/retrieval/vector_store.py

### Etape 6 - Chunk Re-Ranker
- Objectif: reranker les chunks recuperes
- Sortie: chunks ordonnes par pertinence finale
- Fichier: src/agents/post_retrieval.py

### Etape 7 - Generation + Critique
- Generation:
  - construit la reponse a partir des chunks rerankes
  - fichier: src/generation/generator.py
- Critique:
  - evalue la qualite/surete
  - peut demander regeneration selon threshold
  - fichier: src/generation/critic.py

Orchestrateur principal:
- Fichier: src/agents/agentic_pipeline.py

Interface UI:
- Fichier: chatbot_agentic_rag_ui.py

## 3. Modeles Utilises par Tache

Configuration actuelle cible (variables d'environnement):
- PRERETRIEVAL_PROVIDER=gemini
- PRERETRIEVAL_MODEL=gemini-1.5-flash
- GENERATION_PROVIDER=groq
- GENERATION_MODEL=llama-3.3-70b-versatile
- CRITIQUE_PROVIDER=gemini
- CRITIQUE_MODEL=gemini-1.5-flash

Repartition finale:

1. Reformulation (Pre-Retrieval)
- Modele: Gemini 1.5 Flash
- Raison: rapide, bon en structuration linguistique

2. Analyse de complexite
- Modele: Gemini 1.5 Flash
- Raison: bonne capacite de classification et extraction d'aspects

3. Decomposition en sous-requetes
- Modele: Gemini 1.5 Flash
- Raison: generation de sous-questions coherentes a faible cout

4. Routage retrieval (text_only vs text_graph)
- Modele principal: Gemini 1.5 Flash
- Fallback robuste: heuristique locale (sans appel LLM si erreur)

5. Retrieval semantique
- Modele d'embedding: paraphrase-multilingual-MiniLM-L12-v2
- Infrastructure: FAISS local
- Raison: zero cout API par requete, rapide, stable

6. Re-ranking
- Mecanisme: scoring local (heuristiques + metriques de pertinence)
- Raison: rapide, deterministic, economique

7. Generation reponse finale
- Modele: Groq Llama 3.3 70B Versatile
- Raison: excellente vitesse d'inference + bonne qualite de reponse

8. Critique / Validation
- Modele: Gemini 1.5 Flash
- Raison: bon compromis cout/qualite pour evaluation

## 4. Raccourci Flux Execution

Question utilisateur
-> Reformulation (Gemini)
-> Complexite (Gemini)
-> Decomposition si necessaire (Gemini)
-> Routing text_only/text_graph (Gemini + fallback heuristique)
-> Retrieval FAISS (embeddings locaux)
-> Re-ranking local
-> Generation (Groq)
-> Critique (Gemini)
-> Reponse finale + trace

## 5. Etat Actuel du Mode Graphe

- Le routeur peut choisir text_graph
- La decision apparait dans les metadata et la trace UI
- Execution graphe complete: non activee pour le moment
- Fallback operationnel: text retrieval (aucun blocage runtime)

## 6. Garantie de Compatibilite

Les autres interfaces restent independantes:
- chatbot_sans_rag_ui.py
- chatbot_avec_rag.py

Le pipeline agentic est isole dans:
- chatbot_agentic_rag_ui.py
- src/agents/agentic_pipeline.py

Donc l'activation agentic n'interrompt pas les interfaces classiques si les dependances sont presentes.
