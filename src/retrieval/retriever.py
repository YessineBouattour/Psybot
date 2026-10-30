"""
Retriever complet avec scoring et ranking
Implémente cosine similarity ranking
"""
from typing import List, Dict
import numpy as np
from sentence_transformers import SentenceTransformer
from .vector_store import FAISSVectorStore


class SemanticRetriever:
    """
    Retriever avec scoring par cosine similarity
    """
    
    def __init__(
        self,
        vector_store: FAISSVectorStore,
        embedder_model: str = "paraphrase-multilingual-MiniLM-L12-v2"
    ):
        """
        Args:
            vector_store: Vector Store FAISS
            embedder_model: Modèle pour encoder les requêtes
        """
        self.vector_store = vector_store
        self.embedder = SentenceTransformer(embedder_model)
        
        print(f"✓ Retriever initialisé avec {embedder_model}")
    
    def retrieve(
        self, 
        query: str, 
        top_k: int = 5,
        score_threshold: float = 0.0
    ) -> List[Dict]:
        """
        Recherche sémantique avec scoring
        
        Args:
            query: Question de l'utilisateur
            top_k: Nombre de chunks à récupérer
            score_threshold: Score minimum (cosine similarity)
            
        Returns:
            Liste de chunks triés par score décroissant
        """
        # Étape 1: Encoder la requête
        query_embedding = self.embedder.encode([query], convert_to_numpy=True)
        
        # Étape 2: Recherche avec cosine similarity
        results = self.vector_store.search(query_embedding, top_k=top_k)
        
        # Étape 3: Filtrer par threshold
        filtered_results = [r for r in results if r['score'] >= score_threshold]
        
        print(f"🔍 Retrieval: {len(filtered_results)}/{top_k} chunks (score > {score_threshold})")
        
        return filtered_results
    
    def retrieve_with_scores(
        self,
        query: str,
        top_k: int = 10
    ) -> Dict:
        """
        Retrieval avec statistiques détaillées sur les scores
        
        Returns:
            Dict avec results, avg_score, max_score, min_score
        """
        results = self.retrieve(query, top_k=top_k)
        
        if not results:
            return {
                'results': [],
                'avg_score': 0.0,
                'max_score': 0.0,
                'min_score': 0.0,
                'count': 0
            }
        
        scores = [r['score'] for r in results]
        
        return {
            'results': results,
            'avg_score': np.mean(scores),
            'max_score': np.max(scores),
            'min_score': np.min(scores),
            'count': len(results)
        }


if __name__ == "__main__":
    # Test du retriever
    from pathlib import Path
    
    # Charger vector store
    vector_store = FAISSVectorStore()
    vector_store.load(Path("data/vector_store"))
    
    # Créer retriever
    retriever = SemanticRetriever(vector_store)
    
    # Test
    query = "Comment gérer une crise d'anxiété?"
    results = retriever.retrieve(query, top_k=3)
    
    print(f"\n🔍 Requête: '{query}'")
    print(f"📊 {len(results)} résultats:\n")
    
    for i, result in enumerate(results, 1):
        print(f"{i}. Score: {result['score']:.3f}")
        print(f"   Texte: {result['text'][:100]}...")
        print()
