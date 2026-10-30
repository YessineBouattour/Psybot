"""
Script d'exécution PHASE 1: Chunking + Embedding
"""
from pathlib import Path
from src.data_processing.pipeline import DataProcessingPipeline


def main():
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║         CHATBOT RAG - GESTION DE L'ANXIÉTÉ              ║
    ║                    PHASE 1: FOUNDATION                   ║
    ║         Chunking + Embedding + Vector Store             ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    # Chemins
    DATA_DIR = Path("data")
    OUTPUT_DIR = DATA_DIR / "processed"
    PARAGRAPHS_FILE = DATA_DIR / "paragraphs.json"
    
    # Vérification fichiers
    if not PARAGRAPHS_FILE.exists():
        print(f"❌ ERREUR: Fichier non trouvé: {PARAGRAPHS_FILE}")
        print(f"   Assurez-vous que paragraphs.json existe dans data/")
        return
    
    print(f"✓ Fichier source trouvé: {PARAGRAPHS_FILE}")
    print(f"✓ Sortie: {OUTPUT_DIR}/")
    print()
    
    # Configuration du pipeline
    print("📋 Configuration:")
    print("  - Chunk size: 500 caractères")
    print("  - Chunk overlap: 50 caractères")
    print("  - Stratégie: Recursive chunking")
    print("  - Modèle: paraphrase-multilingual-MiniLM-L12-v2 (FRANÇAIS)")
    print()
    
    input("Appuyez sur ENTRÉE pour démarrer le traitement...")
    print()
    
    # Initialisation du pipeline
    pipeline = DataProcessingPipeline(
        chunk_size=500,
        chunk_overlap=50,
        chunking_strategy="recursive",
        embedding_model="paraphrase-multilingual-MiniLM-L12-v2"
    )
    
    # Exécution
    try:
        embeddings_data = pipeline.process_from_paragraphs(
            paragraphs_path=PARAGRAPHS_FILE,
            output_dir=OUTPUT_DIR,
            save_chunks=True
        )
        
        print(f"\n{'='*60}")
        print("🎉 SUCCÈS! Phase 1 terminée avec succès")
        print(f"{'='*60}")
        print("\n📦 Fichiers générés:")
        print(f"  ✓ {OUTPUT_DIR}/corpus_embeddings.pt")
        print(f"  ✓ {OUTPUT_DIR}/corpus_metadata.json")
        print(f"  ✓ {OUTPUT_DIR}/processed_chunks.json")
        
        print(f"\n📊 Statistiques:")
        print(f"  - Nombre de chunks: {len(embeddings_data['texts'])}")
        print(f"  - Dimension embeddings: {embeddings_data['embeddings'].shape[1]}")
        print(f"  - Taille mémoire: {embeddings_data['embeddings'].nbytes / 1024 / 1024:.2f} MB")
        
        print(f"\n🎯 Prochaine étape:")
        print(f"  → Phase 2: Implémenter le RAG basique (Retrieval + LLM)")
        
    except Exception as e:
        print(f"\n❌ ERREUR lors du traitement:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
