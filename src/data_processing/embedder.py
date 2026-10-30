"""
Module d'Embedding pour transformer texte en vecteurs
Utilise sentence-transformers (multilingual)
"""
import torch
import numpy as np
from typing import List, Dict, Union
from pathlib import Path
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import json


class TextEmbedder:
    """Classe pour générer des embeddings de texte"""
    
    def __init__(
        self, 
        model_name: str = "paraphrase-multilingual-MiniLM-L12-v2",
        device: str = None
    ):
        """
        Args:
            model_name: Nom du modèle sentence-transformers
                - paraphrase-multilingual-MiniLM-L12-v2 (recommandé pour français)
                - distiluse-base-multilingual-cased-v2
                - all-MiniLM-L6-v2 (anglais uniquement)
            device: 'cuda', 'cpu', ou None (auto-detect)
        """
        self.model_name = model_name
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        
        print(f"🔄 Chargement du modèle {model_name}...")
        self.model = SentenceTransformer(model_name, device=self.device)
        print(f"✓ Modèle chargé sur {self.device}")
        
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        print(f"📐 Dimension des embeddings: {self.embedding_dim}")
    
    def embed_texts(
        self, 
        texts: List[str], 
        batch_size: int = 32,
        show_progress: bool = True
    ) -> np.ndarray:
        """
        Génère des embeddings pour une liste de textes
        
        Args:
            texts: Liste de textes à encoder
            batch_size: Taille des batchs pour traitement
            show_progress: Afficher barre de progression
            
        Returns:
            Array numpy de shape (n_texts, embedding_dim)
        """
        if show_progress:
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=True,
                convert_to_numpy=True
            )
        else:
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                convert_to_numpy=True
            )
        
        return embeddings
    
    def embed_chunks(
        self, 
        chunks: List[Dict],
        batch_size: int = 32
    ) -> Dict[str, Union[np.ndarray, List[Dict]]]:
        """
        Génère embeddings pour une liste de chunks avec métadonnées
        
        Args:
            chunks: Liste de dicts avec 'text' et 'metadata'
            batch_size: Taille des batchs
            
        Returns:
            Dict avec:
                - embeddings: array numpy (n_chunks, embedding_dim)
                - metadata: liste des métadonnées
                - texts: liste des textes originaux
        """
        print(f"🔄 Génération de {len(chunks)} embeddings...")
        
        texts = [chunk['text'] for chunk in chunks]
        metadata = [chunk['metadata'] for chunk in chunks]
        
        embeddings = self.embed_texts(texts, batch_size=batch_size)
        
        print(f"✓ {len(embeddings)} embeddings générés")
        
        return {
            'embeddings': embeddings,
            'metadata': metadata,
            'texts': texts
        }
    
    def save_embeddings(
        self, 
        embeddings_data: Dict,
        output_dir: Path,
        prefix: str = "corpus"
    ):
        """
        Sauvegarde embeddings et métadonnées
        
        Args:
            embeddings_data: Dict retourné par embed_chunks()
            output_dir: Dossier de sauvegarde
            prefix: Préfixe des fichiers
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Sauvegarder embeddings (format PyTorch)
        embeddings_path = output_dir / f"{prefix}_embeddings.pt"
        torch.save(
            torch.from_numpy(embeddings_data['embeddings']),
            embeddings_path
        )
        print(f"✓ Embeddings sauvegardés: {embeddings_path}")
        
        # Sauvegarder métadonnées
        metadata_path = output_dir / f"{prefix}_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': embeddings_data['metadata'],
                'texts': embeddings_data['texts'],
                'model_name': self.model_name,
                'embedding_dim': self.embedding_dim,
                'n_chunks': len(embeddings_data['texts'])
            }, f, ensure_ascii=False, indent=2)
        print(f"✓ Métadonnées sauvegardées: {metadata_path}")
        
        # Stats
        print(f"\n📊 Statistiques:")
        print(f"  - Nombre de chunks: {len(embeddings_data['texts'])}")
        print(f"  - Dimension: {self.embedding_dim}")
        print(f"  - Taille totale: {embeddings_data['embeddings'].nbytes / 1024 / 1024:.2f} MB")
    
    def load_embeddings(
        self, 
        embeddings_path: Path,
        metadata_path: Path
    ) -> Dict:
        """
        Charge des embeddings sauvegardés
        
        Returns:
            Dict avec embeddings, metadata, texts
        """
        print(f"🔄 Chargement des embeddings...")
        
        embeddings = torch.load(embeddings_path, weights_only=True).numpy()
        
        with open(metadata_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✓ {len(embeddings)} embeddings chargés")
        
        return {
            'embeddings': embeddings,
            'metadata': data['metadata'],
            'texts': data['texts']
        }


if __name__ == "__main__":
    # Test de l'embedder
    embedder = TextEmbedder()
    
    test_texts = [
        "L'anxiété est une réponse naturelle au stress.",
        "La thérapie cognitivo-comportementale aide à gérer l'anxiété.",
        "Les techniques de relaxation sont efficaces."
    ]
    
    embeddings = embedder.embed_texts(test_texts, show_progress=False)
    
    print(f"\n✓ Test réussi!")
    print(f"  Shape: {embeddings.shape}")
    print(f"  Type: {embeddings.dtype}")
    print(f"  Exemple: {embeddings[0][:5]}...")
