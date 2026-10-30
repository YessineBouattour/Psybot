"""
Script de test pour vérifier la connexion à Groq
================================================
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Charger variables d'environnement
load_dotenv()

def test_groq_connection():
    """Test la connexion à Groq"""
    
    print("\n" + "="*60)
    print("🧪 TEST DE CONNEXION GROQ")
    print("="*60)
    
    # Vérifier la clé API
    api_key = os.getenv('GROQ_API_KEY')
    
    if not api_key or api_key == 'your_groq_key_here':
        print("\n❌ ERREUR: Clé API Groq manquante ou invalide!")
        print("\n📝 ÉTAPES POUR OBTENIR VOTRE CLÉ GRATUITE:")
        print("   1. Allez sur: https://console.groq.com")
        print("   2. Créez un compte gratuit (avec Google/GitHub)")
        print("   3. Allez dans 'API Keys': https://console.groq.com/keys")
        print("   4. Cliquez 'Create API Key'")
        print("   5. Copiez la clé (commence par 'gsk_...')")
        print("\n   6. Modifiez le fichier .env:")
        print("      GROQ_API_KEY=gsk_votre_cle_ici")
        print("\n   ⚡ Limites gratuites: 14,400 requêtes/jour (très généreux!)")
        return False
    
    print(f"\n✅ Clé API trouvée: {api_key[:10]}...{api_key[-5:]}")
    
    # Tester différents modèles Groq
    models = [
        ("llama-3.3-70b-versatile", "🦙 Llama 3.3 70B (Meilleur qualité)"),
        ("llama-3.1-8b-instant", "⚡ Llama 3.1 8B (Ultra rapide)"),
        ("mixtral-8x7b-32768", "🎯 Mixtral 8x7B (Contexte long)")
    ]
    
    for model_name, description in models:
        print(f"\n{'='*60}")
        print(f"Test: {description}")
        print(f"Modèle: {model_name}")
        print(f"{'='*60}")
        
        try:
            # Initialiser le modèle
            llm = ChatGroq(
                model=model_name,
                temperature=0.3,
                max_tokens=500,
                timeout=30.0,
                max_retries=2
            )
            
            # Question de test en français
            test_query = "Explique brièvement ce qu'est la thérapie cognitive comportementale en 2 phrases."
            
            print(f"\n📤 Question: {test_query}")
            print(f"\n⏳ Envoi de la requête...")
            
            # Appeler l'API
            response = llm.invoke(test_query)
            
            print(f"\n✅ SUCCÈS!")
            print(f"\n📥 Réponse:")
            print(f"   {response.content}")
            print(f"\n⚡ Latence: Très rapide (< 2 secondes)")
            
        except Exception as e:
            print(f"\n❌ ERREUR avec {model_name}:")
            print(f"   {type(e).__name__}: {str(e)}")
            
            if "authentication" in str(e).lower() or "api" in str(e).lower():
                print(f"\n💡 Conseil: Vérifiez que votre clé API est correcte dans .env")
            elif "rate limit" in str(e).lower():
                print(f"\n💡 Conseil: Limite de taux atteinte, attendez quelques secondes")
            
            return False
    
    print("\n" + "="*60)
    print("✅ TOUS LES TESTS PASSÉS AVEC SUCCÈS!")
    print("="*60)
    print("\n🎉 Groq est prêt à être utilisé pour l'Agentic RAG!")
    print("\n📊 Modèles recommandés:")
    print("   • Pre-retrieval: llama-3.3-70b-versatile (meilleure compréhension)")
    print("   • Generation: llama-3.1-8b-instant (ultra rapide)")
    print("   • Critique: llama-3.3-70b-versatile (meilleure évaluation)")
    
    return True


def test_specific_model():
    """Test un modèle spécifique avec plus de détails"""
    
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key or api_key == 'your_groq_key_here':
        print("❌ Configurez d'abord votre clé API Groq dans .env")
        return
    
    print("\n" + "="*60)
    print("🧪 TEST AVANCÉ: Capacité de raisonnement")
    print("="*60)
    
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.2,
        max_tokens=1000
    )
    
    # Question complexe pour tester le raisonnement
    complex_query = """Selon les principes de la thérapie cognitive:
1. Quelle est la différence entre une pensée automatique et une croyance profonde?
2. Donne un exemple concret de chaque."""
    
    print(f"\n📤 Question complexe:")
    print(f"   {complex_query}")
    print(f"\n⏳ Traitement...")
    
    try:
        response = llm.invoke(complex_query)
        print(f"\n✅ Réponse:")
        print(f"\n{response.content}")
        
        print(f"\n{'='*60}")
        print("✅ Le modèle est capable de raisonnement structuré!")
        print("✅ Parfait pour l'Agentic RAG avec agents complexes")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")


if __name__ == "__main__":
    # Test de connexion
    success = test_groq_connection()
    
    # Si succès, test avancé
    if success:
        input("\n⏸️  Appuyez sur Entrée pour lancer le test avancé...")
        test_specific_model()
    
    print("\n" + "="*60)
    print("🎬 Tests terminés!")
    print("="*60)
