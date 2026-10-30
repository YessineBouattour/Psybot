"""
Post-Retrieval: Re-ranking des chunks récupérés
"""
from typing import List, Dict
import numpy as np


class ChunkReRanker:
    """
    Re-ranking des chunks après retrieval initial
    Utilise critères multiples pour améliorer pertinence
    """
    
    def __init__(self):
        """Initialise le re-ranker"""
        pass
    
    def rerank(
        self,
        chunks: List[Dict],
        query: str,
        weights: Dict[str, float] = None
    ) -> List[Dict]:
        """
        Re-classe les chunks selon plusieurs critères
        
        Args:
            chunks: Liste de chunks avec scores
            query: Requête originale
            weights: Poids pour chaque critère
            
        Returns:
            Chunks re-classés
        """
        if not chunks:
            return []
        
        if weights is None:
            weights = {
                'similarity_score': 0.6,  # Score cosine similarity original
                'keyword_match': 0.2,     # Correspondance mots-clés
                'length_penalty': 0.1,    # Pénalité chunks trop courts/longs
                'diversity': 0.1          # Diversité des sources
            }
        
        print(f"\n🔄 POST-RETRIEVAL: Re-ranking de {len(chunks)} chunks...")
        
        # Calculer scores pour chaque critère
        for i, chunk in enumerate(chunks):
            scores = {}
            
            # 1. Score similarity (déjà présent)
            scores['similarity'] = chunk.get('score', 0.0)
            
            # 2. Keyword match
            scores['keyword'] = self._calculate_keyword_score(chunk['text'], query)
            
            # 3. Length penalty
            scores['length'] = self._calculate_length_score(chunk['text'])
            
            # 4. Diversity (position dans liste originale)
            scores['diversity'] = 1.0 / (i + 1)  # Favorise diversité
            
            # Score final pondéré
            final_score = (
                weights['similarity_score'] * scores['similarity'] +
                weights['keyword_match'] * scores['keyword'] +
                weights['length_penalty'] * scores['length'] +
                weights['diversity'] * scores['diversity']
            )
            
            chunk['rerank_score'] = final_score
            chunk['score_details'] = scores
        
        # Trier par nouveau score
        reranked = sorted(chunks, key=lambda x: x['rerank_score'], reverse=True)
        
        # Mettre à jour les rangs
        for i, chunk in enumerate(reranked, 1):
            chunk['rerank'] = i
        
        print(f"   ✓ Re-ranking terminé")
        top_scores = [f"{c['rerank_score']:.3f}" for c in reranked[:3]]
        print(f"   Top 3 scores: {top_scores}")
        
        return reranked
    
    def _calculate_keyword_score(self, text: str, query: str) -> float:
        """Score basé sur présence mots-clés de la requête"""
        text_lower = text.lower()
        query_words = set(query.lower().split())
        
        # Retirer mots vides
        stop_words = {'le', 'la', 'les', 'un', 'une', 'des', 'de', 'du', 'et', 'ou', 'à', 'au'}
        query_words = query_words - stop_words
        
        if not query_words:
            return 0.0
        
        matches = sum(1 for word in query_words if word in text_lower)
        return matches / len(query_words)
    
    def _calculate_length_score(self, text: str, optimal_length: int = 500) -> float:
        """Pénalise chunks trop courts ou trop longs"""
        length = len(text)
        
        # Score maximal à optimal_length
        if length < 100:  # Trop court
            return length / 100
        elif length > 1000:  # Trop long
            return max(0.3, 1000 / length)
        else:
            # Gaussienne centrée sur optimal_length
            diff = abs(length - optimal_length)
            return np.exp(-(diff**2) / (2 * (optimal_length * 0.5)**2))


if __name__ == "__main__":
    # Test
    reranker = ChunkReRanker()
    
    test_chunks = [
        {'text': 'L\'anxiété est un trouble...', 'score': 0.85},
        {'text': 'La TCC aide...', 'score': 0.80},
        {'text': 'Les techniques de respiration...', 'score': 0.75}
    ]
    
    reranked = reranker.rerank(test_chunks, "comment gérer anxiété")
    
    for chunk in reranked:
        print(f"Score: {chunk['rerank_score']:.3f} - {chunk['text'][:30]}...")
