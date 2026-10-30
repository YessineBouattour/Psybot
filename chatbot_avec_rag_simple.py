"""
Chatbot AVEC RAG Simple - Interface Web
Utilise les embeddings et vector store existants
"""
import os
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import gradio as gr
import torch
import numpy as np
# NOTE: Évite l'import de sentence_transformers pour compatibilité Python 3.14

# Imports locaux
from src.retrieval.vector_store import FAISSVectorStore
from src.retrieval.retriever import SemanticRetriever

# Charger configuration
load_dotenv()


def get_llm():
    """Configure le LLM selon .env"""
    provider = os.getenv('LLM_PROVIDER', 'ollama').lower()
    model = os.getenv('LLM_MODEL', 'phi3:mini')
    
    print(f"🤖 Initialisation LLM: {provider.upper()} - {model}")
    
    if provider == 'ollama':
        from langchain_ollama import OllamaLLM
        return OllamaLLM(model=model, temperature=0.7)
    
    elif provider == 'groq':
        from langchain_groq import ChatGroq
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key or api_key == 'your_groq_key_here':
            raise ValueError("❌ GROQ_API_KEY manquante")
        return ChatGroq(model=model, temperature=0.7, api_key=api_key)
    
    elif provider == 'openai':
        from langchain_openai import ChatOpenAI
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or api_key == 'your_openai_key_here':
            raise ValueError("❌ OPENAI_API_KEY manquante")
        return ChatOpenAI(model=model, temperature=0.7, api_key=api_key)
    
    elif provider == 'anthropic':
        from langchain_anthropic import ChatAnthropic
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key or api_key == 'your_claude_key_here':
            raise ValueError("❌ ANTHROPIC_API_KEY manquante")
        return ChatAnthropic(model=model, temperature=0.7, api_key=api_key)
    
    else:
        raise ValueError(f"Provider inconnu: {provider}")


# Initialisation du système RAG
print("\n" + "="*60)
print("🚀 Chargement du système RAG Simple...")
print("="*60)

# 1. Charger le LLM
llm = get_llm()

# 2. Charger le vector store
print("\n📚 Chargement des données...")
vector_store = FAISSVectorStore()

# Charger les embeddings et métadonnées avec gestion mémoire
processed_dir = Path("data/processed")

# Charger avec weights_only=False pour éviter l'erreur de mémoire stricte
embeddings = torch.load(
    processed_dir / "corpus_embeddings.pt",
    map_location='cpu',
    weights_only=False
).numpy()

with open(processed_dir / "corpus_metadata.json", 'r', encoding='utf-8') as f:
    metadata = json.load(f)

with open(processed_dir / "processed_chunks.json", 'r', encoding='utf-8') as f:
    chunks_data = json.load(f)
    texts = [chunk['text'] for chunk in chunks_data]

# Créer l'index
vector_store.create_index(embeddings, metadata, texts)

# 3. Initialiser le retriever
retriever = SemanticRetriever(vector_store)

print("✅ Système RAG prêt !")
print("="*60 + "\n")

# Variables globales pour la session
conversation_history = []
session_start = datetime.now()


def rag_chat(query: str, top_k: int = 5) -> dict:
    """
    Pipeline RAG complet : Récupération + Génération
    
    Args:
        query: Question utilisateur
        top_k: Nombre de chunks à récupérer
        
    Returns:
        Dict avec réponse, sources, scores
    """
    # 1. Récupération des documents pertinents
    results = retriever.retrieve(query, top_k=top_k, score_threshold=0.3)
    
    if not results:
        return {
            "response": "❌ Aucun document pertinent trouvé. Essayez de reformuler votre question.",
            "sources": [],
            "context": ""
        }
    
    # 2. Construire le contexte
    context_parts = []
    sources_info = []
    
    for i, result in enumerate(results, 1):
        context_parts.append(f"[Document {i}]\n{result['text']}\n")
        
        # Accéder aux métadonnées de manière sécurisée
        metadata = result.get('metadata', {})
        if isinstance(metadata, dict):
            source = metadata.get('source', 'unknown')
            page = metadata.get('page', 'N/A')
        else:
            source = 'unknown'
            page = 'N/A'
        
        sources_info.append({
            "doc_id": i,
            "score": round(result['score'], 3),
            "source": source,
            "page": page
        })
    
    context = "\n".join(context_parts)
    
    # 3. Générer la réponse avec le contexte
    prompt = f"""Tu es un assistant spécialisé en gestion de l'anxiété et troubles anxieux.

Tu dois répondre à la question en te basant UNIQUEMENT sur le contexte fourni ci-dessous.

CONTEXTE:
{context}

QUESTION: {query}

INSTRUCTIONS:
1. Réponds de manière empathique et claire
2. Base-toi UNIQUEMENT sur les informations du contexte
3. Cite les numéros des documents utilisés [Document X]
4. Si le contexte est insuffisant, dis-le honnêtement
5. Structure ta réponse clairement

RÉPONSE:"""
    
    response = llm.invoke(prompt)
    
    # Extraire le texte de la réponse
    if hasattr(response, 'content'):
        response_text = response.content
    else:
        response_text = str(response)
    
    return {
        "response": response_text,
        "sources": sources_info,
        "context": context
    }


def format_sources(sources: list) -> str:
    """Formate les sources pour affichage"""
    if not sources:
        return "Aucune source"
    
    formatted = "**📚 Sources utilisées:**\n\n"
    for src in sources:
        formatted += f"- **Document {src['doc_id']}** (Score: {src['score']}) - {src['source']} (Page {src['page']})\n"
    
    return formatted


def save_conversation():
    """Sauvegarde la conversation dans un fichier JSON"""
    if not conversation_history:
        return "⚠️ Aucune conversation à sauvegarder"
    
    # Créer le dossier
    save_dir = Path(__file__).resolve().parent / "comparaisons_chatbot"
    save_dir.mkdir(exist_ok=True)
    
    # Nom de fichier avec timestamp
    timestamp = session_start.strftime("%Y%m%d_%H%M%S")
    filename = f"chatbot_avec_rag_{timestamp}.json"
    filepath = save_dir / filename
    
    # Métadonnées
    session_data = {
        "metadata": {
            "session_start": session_start.isoformat(),
            "session_end": datetime.now().isoformat(),
            "type": "chatbot_avec_rag_simple",
            "llm_provider": os.getenv('LLM_PROVIDER', 'ollama'),
            "llm_model": os.getenv('LLM_MODEL', 'phi3:mini'),
            "total_questions": len(conversation_history)
        },
        "conversations": conversation_history
    }
    
    # Sauvegarder
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)
    
    return f"✅ Conversation sauvegardée !\n📁 {filepath}\n📊 {len(conversation_history)} échanges enregistrés"


def get_session_info():
    """Retourne les infos de la session"""
    provider = os.getenv('LLM_PROVIDER', 'ollama').upper()
    model = os.getenv('LLM_MODEL', 'phi3:mini')
    duration = datetime.now() - session_start
    
    return f"""
**Session Info:**
- **Type:** Chatbot AVEC RAG Simple
- **LLM:** {provider} - {model}
- **Début:** {session_start.strftime("%H:%M:%S")}
- **Durée:** {duration.seconds // 60} minutes
- **Échanges:** {len(conversation_history)}
- **Documents:** {vector_store.index.ntotal} chunks indexés
    """


# Interface Gradio
with gr.Blocks(title="Chatbot AVEC RAG - Comparaison") as demo:
    
    # En-tête
    gr.HTML("""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; margin-bottom: 20px;">
        <h1>🚀 Chatbot AVEC RAG Simple</h1>
        <p>Réponses enrichies par les documents spécialisés sur l'anxiété</p>
        <p style="font-size: 0.9em; opacity: 0.9;">✅ Accès aux PDFs + Citations des sources</p>
    </div>
    """)
    
    with gr.Row():
        with gr.Column(scale=3):
            # Zone de chat
            chatbot = gr.Chatbot(
                label="💬 Conversation",
                height=400,
                show_label=True
            )
            
            # Zone de saisie
            msg = gr.Textbox(
                label="Votre question sur l'anxiété",
                placeholder="Exemple: Qu'est-ce que l'anxiété généralisée ?",
                lines=2
            )
            
            with gr.Row():
                submit_btn = gr.Button("📤 Envoyer", variant="primary", scale=2)
                clear_btn = gr.Button("🗑️ Effacer", scale=1)
            
            # Sources
            sources_display = gr.Markdown(label="📚 Sources", value="")
        
        with gr.Column(scale=1):
            # Panneau latéral
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
    
    # Événements
    def respond(message, chat_history):
        if not message.strip():
            return "", chat_history, get_session_info(), ""
        
        # Pipeline RAG
        try:
            result = rag_chat(message, top_k=5)
            bot_message = result["response"]
            sources_text = format_sources(result["sources"])
            
            # Sauvegarder dans l'historique
            entry = {
                "timestamp": datetime.now().isoformat(),
                "question": message,
                "response": bot_message,
                "sources": result["sources"]
            }
            conversation_history.append(entry)
            
        except Exception as e:
            bot_message = f"❌ Erreur: {str(e)}\n\nVérifiez qu'Ollama est lancé."
            sources_text = ""
        
        # Format Gradio 6.0
        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": bot_message})
        
        return "", chat_history, get_session_info(), sources_text
    
    submit_btn.click(
        respond,
        inputs=[msg, chatbot],
        outputs=[msg, chatbot, session_info, sources_display]
    )
    
    msg.submit(
        respond,
        inputs=[msg, chatbot],
        outputs=[msg, chatbot, session_info, sources_display]
    )
    
    clear_btn.click(
        lambda: (None, get_session_info(), ""),
        outputs=[chatbot, session_info, sources_display]
    )
    
    save_btn.click(
        save_conversation,
        outputs=save_status
    )
    
    # Footer
    gr.HTML("""
    <div style="text-align: center; margin-top: 20px; padding: 10px; opacity: 0.7; font-size: 0.9em;">
        🔬 Projet RAG - Phase RAG Simple | Réponses enrichies par documents spécialisés
    </div>
    """)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Lancement de l'interface Gradio RAG...")
    print("="*60 + "\n")
    
    demo.launch(
        server_name="127.0.0.1",
        server_port=7865,
        share=False,
        show_error=True,
        theme=gr.themes.Soft()
    )
