"""
Chatbot sans RAG avec Interface Web Gradio
Interface élégante pour captures d'écran et rapport
UTILISE GROQ (API gratuite ultra-rapide)
"""
import os
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import gradio as gr
from langchain_groq import ChatGroq

# Charger configuration
load_dotenv()


def call_groq(prompt: str) -> str:
    """Appel à Groq via LangChain"""
    model = os.getenv('GENERATION_MODEL', 'llama-3.1-8b-instant')
    api_key = os.getenv('GROQ_API_KEY')
    
    if not api_key or api_key == 'your_groq_key_here':
        return "❌ Erreur: Clé API Groq manquante. Configurez GROQ_API_KEY dans .env"
    
    try:
        llm = ChatGroq(
            model=model,
            temperature=0.7,
            max_tokens=2048,
            timeout=60.0,
            max_retries=2
        )
        
        response = llm.invoke(prompt)
        return response.content
        
    except Exception as e:
        return f"❌ Erreur Groq: {type(e).__name__}: {str(e)}"


# Initialisation globale
print(f"🤖 Initialisation: GROQ - {os.getenv('GENERATION_MODEL', 'llama-3.1-8b-instant')}")
conversation_history = []
session_start = datetime.now()

# Prompt système
SYSTEM_PROMPT = """Tu es un assistant qui répond à des questions sur l'anxiété et la santé mentale.

⚠️ IMPORTANT: Tu réponds UNIQUEMENT avec tes connaissances générales, SANS accès à des documents spécialisés.

INSTRUCTIONS:
1. Réponds de manière empathique et professionnelle
2. Sois honnête sur les limites de tes connaissances
3. Recommande de consulter un professionnel pour des cas sérieux
4. Utilise un langage accessible et clair

Réponds à la question suivante:"""


def save_conversation():
    """Sauvegarde la conversation dans un fichier JSON"""
    if not conversation_history:
        return "⚠️ Aucune conversation à sauvegarder"
    
    # Créer le dossier
    save_dir = Path(__file__).resolve().parent / "comparaisons_chatbot"
    save_dir.mkdir(exist_ok=True)
    
    # Nom de fichier avec timestamp
    timestamp = session_start.strftime("%Y%m%d_%H%M%S")
    filename = f"chatbot_sans_rag_{timestamp}.json"
    filepath = save_dir / filename
    
    # Métadonnées
    session_data = {
        "metadata": {
            "session_start": session_start.isoformat(),
            "session_end": datetime.now().isoformat(),
            "type": "chatbot_sans_rag",
            "llm_provider": "groq",
            "llm_model": os.getenv('GENERATION_MODEL', 'llama-3.1-8b-instant'),
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
    provider = "GROQ"
    model = os.getenv('GENERATION_MODEL', 'llama-3.1-8b-instant')
    duration = datetime.now() - session_start
    
    return f"""
**Session Info:**
- **Type:** Chatbot SANS RAG (connaissances générales)
- **LLM:** {provider} - {model}
- **Début:** {session_start.strftime("%H:%M:%S")}
- **Durée:** {duration.seconds // 60} minutes
- **Échanges:** {len(conversation_history)}
    """


# Interface Gradio
with gr.Blocks(title="Chatbot Sans RAG - Comparaison") as demo:
    
    # En-tête
    gr.HTML("""
    <div class="header">
        <h1>🤖 Chatbot Sans RAG</h1>
        <p>Réponses basées uniquement sur les connaissances générales du LLM</p>
        <p style="font-size: 0.9em; opacity: 0.9;">⚠️ Sans accès aux documents spécialisés - Pour comparaison avec RAG</p>
    </div>
    """)
    
    with gr.Row():
        with gr.Column(scale=4):
            # Zone de chat élargie pour captures d'écran
            chatbot = gr.Chatbot(
                label="💬 Conversation",
                height=800,
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
        
        with gr.Column(scale=1):
            # Panneau latéral
            gr.Markdown("### 📊 Informations")
            session_info = gr.Markdown(get_session_info())
            
            gr.Markdown("---")
            
            save_btn = gr.Button("💾 Sauvegarder la conversation", variant="secondary")
            save_status = gr.Textbox(label="Statut", lines=3, interactive=False)
            
            gr.Markdown("---")
            
            gr.Markdown("""
            ### 💡 Conseils
            - Posez des questions spécifiques
            - Prenez des captures d'écran
            - Comparez avec le RAG plus tard
            
            ### 📝 Questions suggérées
            - Qu'est-ce que l'anxiété généralisée ?
            - Comment gérer une crise d'angoisse ?
            - Symptômes physiques de l'anxiété ?
            - Différence anxiété et stress ?
            """)
    
    # Événements
    def respond(message, chat_history):
        if not message.strip():
            return "", chat_history, get_session_info()
        
        # Construire le prompt
        full_prompt = f"{SYSTEM_PROMPT}\n\nQUESTION: {message}\n\nRÉPONSE:"
        
        # Générer la réponse via Groq
        bot_message = call_groq(full_prompt)
        
        # Sauvegarder dans l'historique
        entry = {
            "timestamp": datetime.now().isoformat(),
            "question": message,
            "response": bot_message
        }
        conversation_history.append(entry)
        
        # Format Gradio 6.0: dictionnaire avec role et content
        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": bot_message})
        return "", chat_history, get_session_info()
    
    submit_btn.click(
        respond,
        inputs=[msg, chatbot],
        outputs=[msg, chatbot, session_info]
    )
    
    msg.submit(
        respond,
        inputs=[msg, chatbot],
        outputs=[msg, chatbot, session_info]
    )
    
    clear_btn.click(
        lambda: (None, get_session_info()),
        outputs=[chatbot, session_info]
    )
    
    save_btn.click(
        save_conversation,
        outputs=save_status
    )
    
    # Footer
    gr.HTML("""
    <div style="text-align: center; margin-top: 20px; padding: 10px; opacity: 0.7; font-size: 0.9em;">
        🔬 Projet RAG - Phase Comparaison | Chatbot de référence sans enrichissement documentaire
    </div>
    """)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Lancement de l'interface Gradio...")
    print("="*60 + "\n")
    
    demo.launch(
        server_name="127.0.0.1",
        server_port=7862,
        share=False,
        show_error=True,
        theme=gr.themes.Soft()
    )
