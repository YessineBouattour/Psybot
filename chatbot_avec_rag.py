"""
Chatbot AVEC RAG - Version Simple et Stable
Utilise GROQ (API gratuite ultra-rapide) + embeddings pré-calculés
Port: 7866 (différent du sans RAG sur 7862)
"""
import os
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import gradio as gr
import numpy as np
import torch
from langchain_groq import ChatGroq

# Charger configuration
load_dotenv()


def call_groq(prompt: str) -> str:
    """Appel à Groq via LangChain"""
    model = os.getenv('GENERATION_MODEL', 'llama-3.3-70b-versatile')
    api_key = os.getenv('GROQ_API_KEY')
    
    if not api_key or api_key == 'your_groq_key_here':
        return "❌ Erreur: Clé API Groq manquante. Configurez GROQ_API_KEY dans .env"
    
    try:
        llm = ChatGroq(
            model=model,
            temperature=0.3,  # Légèrement augmenté pour réponses plus développées
            max_tokens=3000,  # Augmenté pour réponses complètes
            timeout=60.0,
            max_retries=2
        )
        
        response = llm.invoke(prompt)
        return response.content
        
    except Exception as e:
        return f"❌ Erreur Groq: {type(e).__name__}: {str(e)}"


# Chargement des données
print("\n" + "="*60)
print("🚀 Chargement du système RAG avec embeddings...")
print("="*60)

processed_dir = Path("data/processed")

# Charger les chunks de texte
with open(processed_dir / "processed_chunks.json", 'r', encoding='utf-8') as f:
    chunks_data = json.load(f)
    texts = [chunk['text'] for chunk in chunks_data]

# Charger métadonnées (c'est un dict avec clé 'metadata')
with open(processed_dir / "corpus_metadata.json", 'r', encoding='utf-8') as f:
    metadata_file = json.load(f)
    metadata = metadata_file['metadata']  # Liste des métadonnées

# Charger les embeddings pré-calculés
embeddings = torch.load(processed_dir / "corpus_embeddings.pt")
if embeddings.dim() == 1:
    embeddings = embeddings.unsqueeze(0)

print(f"✅ {len(texts)} chunks chargés")
print(f"✅ Embeddings shape: {embeddings.shape}")
print("="*60 + "\n")

# Fonction pour encoder une requête (embedding simple basé sur mots)
def encode_query_simple(query: str, vocab_size: int = 384) -> torch.Tensor:
    """Encode simple de la requête basé sur hash des mots"""
    words = query.lower().split()
    vector = torch.zeros(vocab_size)
    for word in words:
        idx = hash(word) % vocab_size
        vector[idx] += 1.0
    # Normaliser
    norm = torch.norm(vector)
    if norm > 0:
        vector = vector / norm
    return vector


def semantic_retrieve(query: str, top_k: int = 3) -> list:
    """Récupération hybride: mots-clés + embeddings"""
    query_lower = query.lower()
    query_words = set(query_lower.split())
    
    # Encoder la requête pour similarity
    query_embedding = encode_query_simple(query, vocab_size=embeddings.shape[1])
    
    # Calculer cosine similarity
    similarities = torch.nn.functional.cosine_similarity(
        query_embedding.unsqueeze(0),
        embeddings,
        dim=1
    )
    
    # Combiner avec score mots-clés pour améliorer pertinence
    scores = []
    for idx, (text, sim_score) in enumerate(zip(texts, similarities.tolist())):
        text_lower = text.lower()
        text_words = set(text_lower.split())
        
        # Score mots-clés
        common_words = query_words.intersection(text_words)
        keyword_score = len(common_words) / max(len(query_words), 1)
        
        # Bonus mots-clés importants (avec variantes OCR communes)
        important_keywords = {
            'agoraphobie', 'agoraphobe', 'panique', 'attaque',
            'anxiété', 'anxiety', 'stress', 'peur', 'trouble',
            'tcc', 'thérapie', 'cognitive', 'traitement', 'comportementale',
            'dépression', 'dsm', 'symptôme', 'diagnostic',
            'séance', 'séances', 'protocole', 'durée', 'nombre',
            'semaine', 'mois', 'minutes', 'vingt', 'trente',
            # Variantes OCR
            'ti:ente', 'ti ente', 'quarante', 'quarante-cinq',
            'ti:ente séances', 'vingt ti:ente'
        }
        
        keyword_bonus = 0
        for kw in important_keywords:
            if kw in query_lower and kw in text_lower:
                keyword_bonus += 0.1  # Réduit de 0.3 à 0.1
        
        # BONUS SPÉCIAL: Si question quantitative ("combien", "quel nombre"), favoriser passages avec chiffres
        is_quantitative = any(word in query_lower for word in ['combien', 'nombre', 'durée', 'taux', 'pourcentage', 'quel chiffre'])
        
        if is_quantitative:
            # Détecter présence de chiffres ou mots numériques dans le texte
            numeric_patterns = ['\\d+', 'vingt', 'trente', 'quarante', 'cinquante', 'ti:ente', 
                              'dizaine', 'centaine', '%', 'pourcent']
            import re
            has_numbers = any(re.search(pattern, text_lower) for pattern in numeric_patterns)
            
            if has_numbers:
                # Boost MASSIF pour questions sur "nombre de séances"
                if 'séance' in query_lower or 'session' in query_lower:
                    # Boost ULTRA-AGRESSIF pour compenser les passages avec OCR corrompu
                    # qui contiennent la bonne réponse mais faible similarité sémantique
                    keyword_bonus += 1.2  
                else:
                    keyword_bonus += 0.4  # Boost pour autres questions quantitatives
        
        # Score combiné: 50% mots-clés + 50% embeddings (normalisé entre 0 et 1)
        combined_score = min(1.0, (0.5 * (keyword_score + keyword_bonus)) + (0.5 * sim_score))
        
        scores.append({
            'idx': idx,
            'score': combined_score,
            'text': text,
            'metadata': metadata[idx] if idx < len(metadata) else {}
        })
    
    # Trier par score
    scores.sort(key=lambda x: x['score'], reverse=True)
    
    # Retourner top_k (le filtrage par seuil sera fait après si nécessaire)
    results = scores[:top_k]
    
    return results


def rag_chat(query: str, top_k: int = 15) -> dict:
    """Pipeline RAG complet avec recherche sémantique (top_k=15 pour couverture maximale)"""
    
    # 1. Récupération sémantique
    results = semantic_retrieve(query, top_k=top_k)
    
    if not results:
        return {
            "response": "❌ Aucun document pertinent trouvé pour cette question. Essayez de reformuler votre question avec des mots-clés différents.",
            "sources": [],
            "context": ""
        }
    
    # 2. Construire contexte
    context_parts = []
    sources_info = []
    
    for i, result in enumerate(results, 1):
        # Chunks à 600 caractères (avec top_k=15, ça fait 9000 chars de contexte)
        chunk_text = result['text'][:600] + "..." if len(result['text']) > 600 else result['text']
        # NE PAS inclure le score dans le contexte donné au LLM
        context_parts.append(f"[Document {i}]\n{chunk_text}\n")
        
        meta = result.get('metadata', {})
        sources_info.append({
            "doc_id": i,
            "score": round(result['score'], 3),
            "source": meta.get('source', 'unknown'),
            "page": meta.get('page', 'N/A')
        })
    
    context = "\n".join(context_parts)
    
    # 3. Prompt hybride: naturel mais précis pour critères diagnostiques
    prompt = f"""Tu es un assistant expert en santé mentale et thérapies cognitives. Tu disposes de documents spécialisés pour répondre avec précision.

DOCUMENTS DISPONIBLES:
{context}

QUESTION POSÉE: {query}

📋 INSTRUCTIONS POUR UNE RÉPONSE DE QUALITÉ:

1. **DÉTECTION DU TYPE DE QUESTION**
   - Si critères DSM-5, protocole, étapes, ou liste spécifique → MODE PRÉCIS
   - Si question générale ou explication → MODE NATUREL

2. **MODE PRÉCIS (critères, protocoles, listes)**
   - Liste TOUS les éléments (critère A, B, C, D, E, F...)
   - Pour chaque critère: donne sa description COMPLÈTE et PRÉCISE
   - Si liste de symptômes: énumère-les TOUS (ne dis pas juste "symptômes physiques")
   - Normalise les nombres: "vingt à ti:ente" → "20 à 30"
   - Structure: Introduction brève → Liste exhaustive → Synthèse

3. **MODE NATUREL (autres questions)**
   - Reformule de manière fluide et professionnelle
   - Intègre les informations dans des phrases complètes
   - Évite les répétitions entre documents

4. **RÈGLES COMMUNES**
   - Cite systématiquement: [Document X]
   - NE RÉPÈTE PAS les mêmes informations de plusieurs documents
   - Si plusieurs sources disent la même chose: cite-les toutes mais ne redis qu'une fois
   - Vérifie que tu n'as rien oublié (surtout pour les listes)

EXEMPLE - CRITÈRES DSM-5 (MODE PRÉCIS):

Question: "Quels sont les critères DSM-5 pour le TAG?"

Réponse CORRECTE:
"Le Trouble d'Anxiété Généralisée (TAG) est défini par des critères diagnostiques précis dans le DSM-5. Selon [Document 3], le diagnostic repose sur les critères suivants:

**Critère A - Anxiété excessive**: Anxiété et soucis excessifs (attente avec appréhension) survenant la plupart du temps durant au moins six mois, concernant un certain nombre d'événements ou d'activités.

**Critère B - Difficultés de contrôle**: La personne éprouve de la difficulté à contrôler ces préoccupations.

**Critère C - Symptômes associés**: L'anxiété et les soucis sont associés à trois (ou plus) des six symptômes suivants:
1. Agitation ou sensation d'être survolté ou à bout
2. Fatigabilité facile
3. Difficulté de concentration ou trous de mémoire
4. Irritabilité
5. Tension musculaire
6. Perturbation du sommeil (difficultés d'endormissement, sommeil interrompu ou agité)

**Critère D - Détresse significative**: L'anxiété, les soucis ou les symptômes physiques causent une détresse cliniquement significative ou une altération du fonctionnement social, professionnel ou dans d'autres domaines importants.

**Critère E - Exclusion substance/médicale**: La perturbation n'est pas attribuable aux effets physiologiques d'une substance ou d'une autre affection médicale.

**Critère F - Exclusion autres troubles**: La perturbation n'est pas mieux expliquée par un autre trouble mental.

Cette définition rigoureuse permet d'établir un diagnostic fiable et d'orienter la prise en charge thérapeutique appropriée [Document 3]."

RÉPONSE COMPLÈTE ET SANS RÉPÉTITIONS:"""
    
    # 4. Génération
    response_text = call_groq(prompt)
    
    return {
        "response": response_text,
        "sources": sources_info,
        "context": context
    }


# Variables globales
conversation_history = []
session_start = datetime.now()


def format_sources(sources: list) -> str:
    """Formate les sources"""
    if not sources:
        return "Aucune source"
    
    formatted = "**📚 Sources utilisées:**\n\n"
    for src in sources:
        formatted += f"- **Document {src['doc_id']}** (Score: {src['score']}) - {src['source']} (Page {src['page']})\n"
    
    return formatted


def save_conversation():
    """Sauvegarde conversation"""
    if not conversation_history:
        return "⚠️ Aucune conversation à sauvegarder"
    
    save_dir = Path("comparaisons_chatbot")
    save_dir.mkdir(exist_ok=True)
    
    timestamp = session_start.strftime("%Y%m%d_%H%M%S")
    filename = f"chatbot_avec_rag_{timestamp}.json"
    filepath = save_dir / filename
    
    session_data = {
        "metadata": {
            "session_start": session_start.isoformat(),
            "session_end": datetime.now().isoformat(),
            "type": "chatbot_avec_rag_simple",
            "llm_provider": "groq",
            "llm_model": os.getenv('GENERATION_MODEL', 'llama-3.3-70b-versatile'),
            "total_questions": len(conversation_history)
        },
        "conversations": conversation_history
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)
    
    return f"✅ Conversation sauvegardée !\n📁 {filepath}\n📊 {len(conversation_history)} échanges"


def get_session_info():
    """Info session"""
    model = os.getenv('GENERATION_MODEL', 'llama-3.3-70b-versatile')
    duration = datetime.now() - session_start
    
    return f"""
**Session Info:**
- **Type:** Chatbot AVEC RAG
- **LLM:** GROQ - {model}
- **Début:** {session_start.strftime("%H:%M:%S")}
- **Durée:** {duration.seconds // 60} minutes
- **Échanges:** {len(conversation_history)}
- **Documents:** {len(texts)} chunks disponibles
    """


# Interface Gradio
with gr.Blocks(title="Chatbot AVEC RAG - Comparaison") as demo:
    
    gr.HTML("""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; margin-bottom: 20px;">
        <h1>🚀 Chatbot AVEC RAG</h1>
        <p>Réponses enrichies par documents spécialisés sur l'anxiété</p>
        <p style="font-size: 0.9em; opacity: 0.9;">✅ Accès aux PDFs + Citations des sources</p>
    </div>
    """)
    
    with gr.Row():
        with gr.Column(scale=4):
            # Zone de chat élargie pour captures d'écran du rapport
            chatbot = gr.Chatbot(
                label="💬 Conversation",
                height=800
            )
            
            msg = gr.Textbox(
                label="Votre question sur l'anxiété",
                placeholder="Exemple: Qu'est-ce que l'anxiété généralisée ?",
                lines=2
            )
            
            with gr.Row():
                submit_btn = gr.Button("📤 Envoyer", variant="primary", scale=2)
                clear_btn = gr.Button("🗑️ Effacer", scale=1)
            
            sources_display = gr.Markdown(label="📚 Sources", value="")
        
        with gr.Column(scale=1):
            gr.Markdown("### 📊 Informations")
            session_info = gr.Markdown(get_session_info())
            
            gr.Markdown("---")
            
            save_btn = gr.Button("💾 Sauvegarder la conversation", variant="secondary")
            save_status = gr.Textbox(label="Statut", lines=3, interactive=False)
            
            gr.Markdown("---")
            
            gr.Markdown("""
            ### 💡 Différences vs Sans RAG
            - ✅ Réponses basées sur VOS documents
            - ✅ Sources citées et traçables
            - ✅ Informations précises et fiables
            - ✅ Citations des passages pertinents
            
            ### 📝 Questions suggérées
            - Critères DSM-5 pour l'anxiété ?
            - Comment fonctionne la TCC ?
            - Statistiques sur l'anxiété ?
            - Techniques de relaxation efficaces ?
            """)
    
    def respond(message, chat_history):
        if not message.strip():
            return "", chat_history, get_session_info(), ""
        
        try:
            result = rag_chat(message, top_k=15)  # Couverture maximale
            bot_message = result["response"]
            sources_text = format_sources(result["sources"])
            
            entry = {
                "timestamp": datetime.now().isoformat(),
                "question": message,
                "response": bot_message,
                "sources": result["sources"]
            }
            conversation_history.append(entry)
            
        except Exception as e:
            bot_message = f"❌ Erreur dans respond(): {type(e).__name__}: {str(e)}"
            sources_text = f"Erreur: {e}"
        
        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": bot_message})
        
        return "", chat_history, get_session_info(), sources_text
    
    submit_btn.click(respond, inputs=[msg, chatbot], outputs=[msg, chatbot, session_info, sources_display])
    msg.submit(respond, inputs=[msg, chatbot], outputs=[msg, chatbot, session_info, sources_display])
    clear_btn.click(lambda: (None, get_session_info(), ""), outputs=[chatbot, session_info, sources_display])
    save_btn.click(save_conversation, outputs=save_status)
    
    gr.HTML("""
    <div style="text-align: center; margin-top: 20px; padding: 10px; opacity: 0.7; font-size: 0.9em;">
        🔬 Chatbot avec RAG - Réponses enrichies par documents
    </div>
    """)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Lancement interface Gradio RAG sur port 7866...")
    print("="*60 + "\n")
    
    demo.launch(
        server_name="127.0.0.1",
        server_port=7866,
        share=False,
        show_error=True
    )
