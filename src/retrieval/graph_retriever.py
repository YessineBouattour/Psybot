"""
Lightweight Graph Retriever
Construit un graphe lexical simple sur les chunks pour activer text_graph
sans dépendance à une base graphe externe.
"""
from __future__ import annotations

import re
import unicodedata
from collections import defaultdict
from typing import Dict, List, Set

from .vector_store import FAISSVectorStore


class LightweightGraphRetriever:
    """Retriever graphe simple basé sur co-occurrence de termes entre chunks."""

    def __init__(self, vector_store: FAISSVectorStore):
        self.vector_store = vector_store
        self.stop_words = {
            "alors", "ainsi", "avec", "avoir", "bien", "comme", "dans", "des", "donc",
            "elle", "elles", "entre", "etre", "font", "leur", "leurs", "mais", "meme",
            "moins", "nous", "pour", "plus", "quoi", "sans", "sera", "sont", "sous",
            "sur", "tres", "tout", "tous", "une", "vous", "votre", "vos", "que", "qui",
            "quoi", "dont", "cela", "ceci", "chez", "leur", "leurs", "cette", "cet", "ces",
            "the", "and", "with", "from", "that", "this", "those", "about", "into", "over",
        }

        self.chunk_terms: List[Set[str]] = []
        self.term_to_ids: Dict[str, Set[int]] = defaultdict(set)
        self._build_index()

    def _normalize(self, text: str) -> str:
        text = (text or "").lower()
        text = unicodedata.normalize("NFD", text)
        text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
        return text

    def _extract_terms(self, text: str) -> Set[str]:
        norm = self._normalize(text)
        tokens = re.findall(r"[a-z]{4,}", norm)
        return {t for t in tokens if t not in self.stop_words}

    def _build_index(self) -> None:
        print("🧩 Construction index graphe lexical...")
        for idx, text in enumerate(self.vector_store.texts):
            terms = self._extract_terms(text)
            self.chunk_terms.append(terms)
            for term in terms:
                self.term_to_ids[term].add(idx)
        print(f"✓ Index graphe prêt: {len(self.chunk_terms)} noeuds, {len(self.term_to_ids)} termes")

    def retrieve(
        self,
        query: str,
        semantic_retriever,
        top_k: int = 10,
        score_threshold: float = 0.20,
    ) -> List[Dict]:
        """Exécute un retrieval hybride: seeds sémantiques + expansion graphe."""
        query_terms = self._extract_terms(query)

        # 1) Seeds sémantiques
        semantic_k = max(top_k, 8)
        semantic_results = semantic_retriever.retrieve(
            query,
            top_k=semantic_k,
            score_threshold=max(0.0, score_threshold * 0.8),
        )

        semantic_scores: Dict[int, float] = {}
        candidate_ids: Set[int] = set()

        for res in semantic_results:
            idx = int(res.get("id", -1))
            if idx >= 0:
                candidate_ids.add(idx)
                semantic_scores[idx] = max(semantic_scores.get(idx, 0.0), float(res.get("score", 0.0)))

        # 2) Expansion par termes de requête
        for term in query_terms:
            ids = self.term_to_ids.get(term, set())
            if not ids:
                continue
            for idx in list(ids)[:120]:
                candidate_ids.add(idx)

        # 3) Expansion voisinage autour des seeds
        seed_ids = list(candidate_ids)
        for seed_id in seed_ids[:40]:
            seed_terms = self.chunk_terms[seed_id] if seed_id < len(self.chunk_terms) else set()
            if not seed_terms:
                continue
            neighbors = set()
            for term in list(seed_terms)[:12]:
                neighbors.update(self.term_to_ids.get(term, set()))
            for nid in list(neighbors)[:80]:
                candidate_ids.add(nid)

        # 4) Scoring graphe
        scored = []
        for idx in candidate_ids:
            if idx >= len(self.vector_store.texts):
                continue

            terms = self.chunk_terms[idx]
            if not terms:
                continue

            q_overlap = len(query_terms.intersection(terms))
            q_score = q_overlap / max(1, len(query_terms))

            # Support voisinage: combien de termes partagés avec seeds
            support = 0
            for sid in semantic_scores.keys():
                shared = len(terms.intersection(self.chunk_terms[sid]))
                if shared >= 2:
                    support += 1
            neighbor_score = min(1.0, support / 5.0)

            semantic_score = semantic_scores.get(idx, 0.0)
            final_score = 0.45 * semantic_score + 0.35 * q_score + 0.20 * neighbor_score

            # Filtre minimal pour éviter le bruit fort
            if final_score < max(0.12, score_threshold * 0.6):
                continue

            scored.append((idx, final_score, semantic_score, q_score, neighbor_score))

        scored.sort(key=lambda x: x[1], reverse=True)
        top_scored = scored[:top_k]

        results: List[Dict] = []
        for rank, (idx, final_score, semantic_score, q_score, neighbor_score) in enumerate(top_scored, start=1):
            results.append(
                {
                    "id": idx,
                    "text": self.vector_store.texts[idx],
                    "metadata": self.vector_store.metadata[idx],
                    "score": float(final_score),
                    "graph_score": float(final_score),
                    "score_details": {
                        "semantic_seed": float(semantic_score),
                        "query_overlap": float(q_score),
                        "neighbor_support": float(neighbor_score),
                    },
                    "rank": rank,
                }
            )

        print(f"🧭 Graph retrieval: {len(results)} chunks (mode text_graph actif)")
        return results
