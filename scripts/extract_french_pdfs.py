"""
Script pour extraire le texte des PDFs français sur l'anxiété
"""
import json
import pdfplumber
from pathlib import Path
from tqdm import tqdm


def extract_text_from_pdf(pdf_path):
    """Extrait le texte d'un PDF en préservant la structure"""
    text_content = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if text:
                    text_content.append({
                        'page': page_num,
                        'content': text.strip()
                    })
    except Exception as e:
        print(f"❌ Erreur avec {pdf_path.name}: {str(e)}")
        return []
    
    return text_content


def process_all_pdfs(pdf_dir, output_file):
    """Traite tous les PDFs et génère paragraphs.json"""
    pdf_dir = Path(pdf_dir)
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"❌ Aucun PDF trouvé dans {pdf_dir}")
        return
    
    print(f"📚 {len(pdf_files)} PDFs trouvés:")
    for pdf in pdf_files:
        print(f"   - {pdf.name}")
    print()
    
    all_paragraphs = []
    
    for pdf_path in tqdm(pdf_files, desc="Extraction des PDFs"):
        pages = extract_text_from_pdf(pdf_path)
        
        for page_data in pages:
            # Découper en paragraphes (par lignes vides doubles)
            paragraphs = page_data['content'].split('\n\n')
            
            for para in paragraphs:
                para = para.strip()
                if len(para) > 50:  # Ignorer les fragments trop courts
                    all_paragraphs.append({
                        'source': pdf_path.name,
                        'page': page_data['page'],
                        'content': para
                    })
    
    # Sauvegarder
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_paragraphs, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Extraction terminée!")
    print(f"   📄 {len(all_paragraphs)} paragraphes extraits")
    print(f"   💾 Sauvegardé: {output_file}")
    
    # Stats
    print(f"\n📊 Statistiques par PDF:")
    pdf_stats = {}
    for para in all_paragraphs:
        source = para['source']
        pdf_stats[source] = pdf_stats.get(source, 0) + 1
    
    for pdf_name, count in sorted(pdf_stats.items()):
        print(f"   - {pdf_name}: {count} paragraphes")


if __name__ == "__main__":
    PDF_DIR = Path("data/stress_anxiety_pdfs")
    OUTPUT_FILE = Path("data/paragraphs_french.json")
    
    print("="*60)
    print("EXTRACTION DES PDFs FRANÇAIS SUR L'ANXIÉTÉ")
    print("="*60)
    print()
    
    process_all_pdfs(PDF_DIR, OUTPUT_FILE)
    
    print(f"\n🎯 Prochaine étape:")
    print(f"   Remplacer data/paragraphs.json par data/paragraphs_french.json")
    print(f"   Puis relancer: python run_phase1.py")
