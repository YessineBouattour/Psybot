"""
Vector Store avec FAISS pour recherche sémantique rapide
"""
import faiss
import numpy as np
import torch
from pathlib import Path
from typing import List, Dict, Tuple
import json


class FAISSVectorStore:
    """Vector Store utilisant FAISS pour recherche par similarité"""
    
    def __init__(self, embedding_dim: int = 384):
        """
        Args:
            embedding_dim: Dimension des embeddings
        """
        self.embedding_dim = embedding_dim
        self.index = None
        self.metadata = []
        self.texts = []
        
    def create_index(self, embeddings: np.ndarray, metadata: List[Dict], texts: List[str]):
        """
        Crée l'index FAISS à partir des embeddings
        
        Args:
            embeddings: Array numpy (n_docs, embedding_dim)
            metadata: Liste des métadonnées pour chaque chunk
            texts: Liste des textes originaux
        """
        print(f"🔧 Création de l'index FAISS...")
        
        # Normaliser les embeddings pour cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Créer index FAISS (Inner Product = cosine similarity avec vecteurs normalisés)
        self.index = faiss.IndexFlatIP(self.embedding_dim)
        self.index.add(embeddings)
        
        self.metadata = metadata
        self.texts = texts
        
        print(f"✓ Index créé: {self.index.ntotal} vecteurs")
        
    def search(
        self, 
        query_embedding: np.ndarray, 
        top_k: int = 5
    ) -> List[Dict]:
        """
        Recherche les top_k chunks les plus similaires
        
        Args:
            query_embedding: Embedding de la requête (1, embedding_dim)
            top_k: Nombre de résultats à retourner
            
        Returns:
            Liste de dicts avec {text, metadata, score}
        """
        if self.index is None:
            raise ValueError("Index non créé. Appelez create_index() d'abord.")
        
        # Normaliser query
        query_embedding = query_embedding.reshape(1, -1)
        faiss.normalize_L2(query_embedding)
        
        # Recherche
        scores, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            idx = int(idx)  # Convertir np.int64 en int Python
            if idx < len(self.texts):  # Vérification sécurité
                results.append({
                    'id': idx,
                    'text': self.texts[int(idx)],
                    'metadata': self.metadata[int(idx)],
                    'score': float(score),
                    'rank': len(results) + 1
                })
        
        return results
    
    def save(self, output_dir: Path):
        """Sauvegarde l'index et métadonnées"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Sauvegarder index FAISS
        index_path = output_dir / "faiss_index.bin"
        faiss.write_index(self.index, str(index_path))
        
        # Sauvegarder métadonnées et textes
        data_path = output_dir / "vector_store_data.json"
        with open(data_path, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': self.metadata,
                'texts': self.texts,
                'embedding_dim': self.embedding_dim
            }, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Vector Store sauvegardé dans {output_dir}")
    
    def load(self, input_dir: Path):
        """Charge l'index et métadonnées"""
        input_dir = Path(input_dir)
        
        # Charger index
        index_path = input_dir / "faiss_index.bin"
        self.index = faiss.read_index(str(index_path))
        
        # Charger métadonnées
        data_path = input_dir / "vector_store_data.json"
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.metadata = data['metadata']
            self.texts = data['texts']
            self.embedding_dim = data['embedding_dim']
        
        print(f"✓ Vector Store chargé: {self.index.ntotal} vecteurs")


def create_vector_store_from_embeddings(
    embeddings_file: Path,
    metadata_file: Path,
    output_dir: Path
) -> FAISSVectorStore:
    """
    Crée un Vector Store à partir des fichiers d'embeddings
    
    Args:
        embeddings_file: Chemin vers corpus_embeddings.pt
        metadata_file: Chemin vers corpus_metadata.json
        output_dir: Dossier de sauvegarde
        
    Returns:
        FAISSVectorStore prêt à l'emploi
    """
    print("="*60)
    print("CRÉATION DU VECTOR STORE")
    print("="*60)
    
    # Charger embeddings
    print(f"📥 Chargement des embeddings...")
    embeddings = torch.load(embeddings_file, weights_only=True).numpy()
    
    # Charger métadonnées
    with open(metadata_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        metadata = data['metadata']
        texts = data['texts']
    
    print(f"✓ {len(embeddings)} embeddings chargés (dim={embeddings.shape[1]})")
    
    # Créer Vector Store
    vector_store = FAISSVectorStore(embedding_dim=embeddings.shape[1])
    vector_store.create_index(embeddings, metadata, texts)
    
    # Sauvegarder
    vector_store.save(output_dir)
    
    print("="*60)
    print("✅ VECTOR STORE PRÊT!")
    print("="*60)
    
    return vector_store


if __name__ == "__main__":
    # Test
    from pathlib import Path
    
    PROCESSED_DIR = Path("data/processed")
    VECTOR_STORE_DIR = Path("data/vector_store")
    
    vector_store = create_vector_store_from_embeddings(
        embeddings_file=PROCESSED_DIR / "corpus_embeddings.pt",
        metadata_file=PROCESSED_DIR / "corpus_metadata.json",
        output_dir=VECTOR_STORE_DIR
    )
    
    print("\n🧪 Test de recherche:")
    # Pour tester, il faudrait un embedding de requête
    print("   (Nécessite un embedder pour tester)")
