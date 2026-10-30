"""
Pipeline complet: PDF → Chunks → Embeddings → Vector Store
"""
from pathlib import Path
import json
from typing import Optional
from .chunker import TextChunker
from .embedder import TextEmbedder


class DataProcessingPipeline:
    """Pipeline end-to-end pour préparer les données RAG"""
    
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        chunking_strategy: str = "recursive",
        embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"
    ):
        """
        Args:
            chunk_size: Taille des chunks
            chunk_overlap: Chevauchement entre chunks
            chunking_strategy: Stratégie de chunking
            embedding_model: Modèle d'embeddings
        """
        print("🚀 Initialisation du pipeline de traitement...")
        
        self.chunker = TextChunker(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            strategy=chunking_strategy
        )
        print(f"✓ Chunker configuré ({chunking_strategy}, size={chunk_size})")
        
        self.embedder = TextEmbedder(model_name=embedding_model)
        print(f"✓ Embedder configuré ({embedding_model})")
    
    def process_from_paragraphs(
        self,
        paragraphs_path: Path,
        output_dir: Path,
        save_chunks: bool = True
    ):
        """
        Traite le fichier paragraphs.json existant
        
        Args:
            paragraphs_path: Chemin vers paragraphs.json
            output_dir: Dossier pour sauvegarder les résultats
            save_chunks: Sauvegarder les chunks en JSON
        """
        print(f"\n{'='*60}")
        print(f"📂 PHASE 1: CHUNKING")
        print(f"{'='*60}")
        
        # Étape 1: Chunking
        chunks = self.chunker.process_paragraphs_json(paragraphs_path)
        print(f"✓ {len(chunks)} chunks créés")
        
        # Sauvegarder chunks si demandé
        if save_chunks:
            chunks_path = output_dir / "processed_chunks.json"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            with open(chunks_path, 'w', encoding='utf-8') as f:
                json.dump(chunks, f, ensure_ascii=False, indent=2)
            print(f"✓ Chunks sauvegardés: {chunks_path}")
        
        print(f"\n{'='*60}")
        print(f"🧮 PHASE 2: EMBEDDING")
        print(f"{'='*60}")
        
        # Étape 2: Embedding
        embeddings_data = self.embedder.embed_chunks(chunks)
        
        # Étape 3: Sauvegarde
        print(f"\n{'='*60}")
        print(f"💾 PHASE 3: SAUVEGARDE")
        print(f"{'='*60}")
        
        self.embedder.save_embeddings(embeddings_data, output_dir)
        
        print(f"\n{'='*60}")
        print(f"✅ PIPELINE TERMINÉ!")
        print(f"{'='*60}")
        print(f"Fichiers générés dans: {output_dir}")
        print(f"  - corpus_embeddings.pt")
        print(f"  - corpus_metadata.json")
        if save_chunks:
            print(f"  - processed_chunks.json")
        
        return embeddings_data


def main():
    """Fonction principale pour exécuter le pipeline"""
    
    # Configuration
    DATA_DIR = Path(__file__).resolve().parents[2] / "data"
    OUTPUT_DIR = DATA_DIR / "processed"
    
    PARAGRAPHS_FILE = DATA_DIR / "paragraphs.json"
    
    # Vérification
    if not PARAGRAPHS_FILE.exists():
        print(f"❌ Fichier non trouvé: {PARAGRAPHS_FILE}")
        return
    
    # Exécution du pipeline
    pipeline = DataProcessingPipeline(
        chunk_size=500,
        chunk_overlap=50,
        chunking_strategy="recursive",
        embedding_model="paraphrase-multilingual-MiniLM-L12-v2"
    )
    
    pipeline.process_from_paragraphs(
        paragraphs_path=PARAGRAPHS_FILE,
        output_dir=OUTPUT_DIR,
        save_chunks=True
    )


if __name__ == "__main__":
    main()
