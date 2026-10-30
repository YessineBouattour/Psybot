"""
Script pour basculer vers le modèle multilingual français
À exécuter quand vous aurez :
1. Meilleure connexion WiFi
2. Vos PDFs français sur l'anxiété
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_processing.pipeline import DataProcessingPipeline


def switch_to_french_model():
    """
    Re-génère les embeddings avec modèle multilingual français
    """
    print("="*60)
    print("🔄 PASSAGE AU MODÈLE MULTILINGUAL FRANÇAIS")
    print("="*60)
    print()
    print("⚠️  ATTENTION: Ce script va télécharger ~420 MB")
    print("   Assurez-vous d'avoir une bonne connexion WiFi!")
    print()
    
    choice = input("Continuer ? (oui/non): ").lower()
    if choice not in ['oui', 'o', 'yes', 'y']:
        print("Annulé.")
        return
    
    DATA_DIR = Path("data")
    OUTPUT_DIR = DATA_DIR / "processed"
    PARAGRAPHS_FILE = DATA_DIR / "paragraphs.json"
    
    # Configuration avec modèle multilingual
    pipeline = DataProcessingPipeline(
        chunk_size=500,
        chunk_overlap=50,
        chunking_strategy="recursive",
        embedding_model="paraphrase-multilingual-MiniLM-L12-v2"  # ✅ FRANÇAIS
    )
    
    print("\n🚀 Génération des nouveaux embeddings...")
    embeddings_data = pipeline.process_from_paragraphs(
        paragraphs_path=PARAGRAPHS_FILE,
        output_dir=OUTPUT_DIR,
        save_chunks=True
    )
    
    print("\n✅ Embeddings multilingues générés!")
    print("   Vos documents français seront maintenant bien compris.")


if __name__ == "__main__":
    switch_to_french_model()
