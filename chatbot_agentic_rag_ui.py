"""
Chatbot Agentic RAG - Interface Gradio
Pipeline 7 agents: Reformulation → Complexité → Décomposition →
                   Retrieval → Re-ranking → Génération → Critique
Port: 7867
"""
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
import gradio as gr

from src.agents.agentic_pipeline import AgenticRAGPipeline

load_dotenv()

# ─────────────────────────────────────────────
# Initialisation pipeline (une seule fois)
# ─────────────────────────────────────────────
VECTOR_STORE_PATH = Path("data/vector_store")

print("\n" + "=" * 60)
print("[AGENTIC RAG] LANCEMENT CHATBOT")
print("=" * 60)

def _env_any(names: list[str], default: str = "") -> str:
    for name in names:
        value = os.getenv(name, "").strip()
        if value:
            return value
    return default


def _make_llm(provider: str, model: str, temperature: float = 0.2) -> Any:
    provider = provider.lower().strip()

    if provider == "groq":
        from langchain_groq import ChatGroq

        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key or api_key == "your_groq_key_here":
            raise ValueError("GROQ_API_KEY manquante dans .env")

        return ChatGroq(
            model=model,
            temperature=temperature,
            max_tokens=2000,
            timeout=60.0,
            max_retries=2,
        )

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        api_key = os.getenv("GOOGLE_API_KEY", "")
        if not api_key or api_key == "your_gemini_key_here":
            raise ValueError("GOOGLE_API_KEY manquante dans .env")

        return ChatGoogleGenerativeAI(
            model=model,
            temperature=temperature,
            max_output_tokens=2000,
            timeout=60,
        )

    if provider == "deepseek":
        from langchain_openai import ChatOpenAI

        api_key = os.getenv("DEEPSEEK_API_KEY", "")
        if not api_key or api_key == "your_deepseek_key_here":
            raise ValueError("DEEPSEEK_API_KEY manquante dans .env")

        return ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=api_key,
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
            max_retries=2,
            timeout=60,
        )

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key or api_key == "your_openai_key_here":
            raise ValueError("OPENAI_API_KEY manquante dans .env")

        return ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=api_key,
            max_retries=2,
            timeout=60,
        )

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key or api_key == "your_claude_key_here":
            raise ValueError("ANTHROPIC_API_KEY manquante dans .env")

        return ChatAnthropic(
            model=model,
            temperature=temperature,
            api_key=api_key,
            timeout=60,
            max_tokens=2000,
        )

    raise ValueError(
        f"Provider non supporté: {provider}. Utilisez groq|gemini|deepseek|openai|anthropic"
    )


_pre_provider = _env_any(
    ["PRERETRIEVAL_PROVIDER", "PRERETRIVAL_PROVIDER", "GENERATION_PROVIDER"],
    default="groq",
)
_gen_provider = _env_any(["GENERATION_PROVIDER"], default="groq")
_crit_provider = _env_any(["CRITIQUE_PROVIDER", "CRITIC_PROVIDER", "PRERETRIEVAL_PROVIDER", "PRERETRIVAL_PROVIDER"], default=_pre_provider)

_gen_default_model = "llama-3.3-70b-versatile" if _gen_provider == "groq" else "gemini-1.5-flash"
_pre_default_model = _gen_default_model

_pre_model = _env_any(["PRERETRIEVAL_MODEL", "PRERETRIVAL_MODEL", "GENERATION_MODEL"], default=_pre_default_model)
_gen_model = _env_any(["GENERATION_MODEL"], default=_gen_default_model)
_crit_model = _env_any(["CRITIQUE_MODEL", "CRITIC_MODEL"], default=_pre_model)


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)).strip())
    except Exception:
        return default


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)).strip())
    except Exception:
        return default


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name, str(default)).strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    return default


_top_k = _env_int("AGENTIC_TOP_K", 16)
_critique_threshold = _env_float("AGENTIC_CRITIQUE_THRESHOLD", 5.5)
_retrieval_score_threshold = _env_float("AGENTIC_RETRIEVAL_SCORE_THRESHOLD", 0.15)
_final_top_n = _env_int("AGENTIC_FINAL_TOP_N", 10)
_generation_max_context_chars = _env_int("AGENTIC_MAX_CONTEXT_CHARS", 3500)
_max_retries = _env_int("AGENTIC_MAX_RETRIES", 0)
_enable_preretrieval = _env_bool("AGENTIC_ENABLE_PRERETRIEVAL", True)
_enable_critique = _env_bool("AGENTIC_ENABLE_CRITIQUE", True)

pipeline = AgenticRAGPipeline(
    vector_store_path=VECTOR_STORE_PATH,
    llm_preretrival=_make_llm(_pre_provider, _pre_model, temperature=0.2),
    llm_generation=_make_llm(_gen_provider, _gen_model, temperature=0.3),
    llm_critique=_make_llm(_crit_provider, _crit_model, temperature=0.1),
    top_k=_top_k,
    critique_threshold=_critique_threshold,
    retrieval_score_threshold=_retrieval_score_threshold,
    final_top_n=_final_top_n,
    generation_max_context_length=_generation_max_context_chars,
    enable_pre_retrieval_llm=_enable_preretrieval,
    enable_critique=_enable_critique,
)

# ─────────────────────────────────────────────
# État session
# ─────────────────────────────────────────────
conversation_history: list = []
session_start = datetime.now()


# ─────────────────────────────────────────────
# Helpers d'affichage
# ─────────────────────────────────────────────
def format_trace(result: dict) -> str:
    """Construit le panneau de trace agents à partir du résultat."""
    complexity = result.get("complexity", {})
    metadata   = result.get("metadata", {})
    critique   = result.get("critique", {})
    sources    = result.get("sources", [])

    lines = []

    # 1 – Reformulation
    lines.append("### 🔄 Étape 1 – Reformulation")
    lines.append(f"**Original :** {result.get('query', '')}")
    lines.append(f"**Reformulée :** {result.get('reformulated_query', '')}")

    # 2 – Complexité
    lines.append("\n### 🧠 Étape 2 – Complexité")
    complexity_label = complexity.get("complexity", "?")
    emoji = "⚠️ COMPLEXE" if complexity_label == "COMPLEXE" else "✅ SIMPLE"
    lines.append(f"**Résultat :** {emoji}")
    aspects = complexity.get("aspects", [])
    if aspects:
        lines.append(f"**Aspects :** {', '.join(aspects)}")

    # 3 – Décomposition
    lines.append("\n### ✂️ Étape 3 – Décomposition Multi-Agent")
    if metadata.get("multi_agent"):
        n = metadata.get("n_sub_queries", 0)
        lines.append(f"**Mode MULTI-AGENT** → {n} sous-requêtes générées")
        sub_queries = metadata.get("sub_queries", [])
        if sub_queries:
            lines.append("**Sous-requêtes :**")
            for i, sq in enumerate(sub_queries, 1):
                lines.append(f"{i}. {sq}")
    else:
        lines.append("Mode SIMPLE (pas de décomposition)")

    # 3b – Routage retrieval
    lines.append("\n### 🧭 Routage Retrieval")
    route = metadata.get("retrieval_route", "text_only")
    route_conf = metadata.get("retrieval_route_confidence", 0.0)
    route_reason = metadata.get("retrieval_route_reason", "")
    route_source = metadata.get("retrieval_route_source", "unknown")
    graph_exec = metadata.get("graph_executed", False)

    route_label = "TEXT + GRAPH" if route == "text_graph" else "TEXT ONLY"
    lines.append(f"**Décision :** {route_label} (confiance={route_conf:.2f})")
    lines.append(f"**Source décision :** {route_source}")
    if route_reason:
        lines.append(f"**Raison :** {route_reason}")
    if route == "text_graph" and not graph_exec:
        lines.append("⚠️ Module graphe non branché: fallback temporaire sur retrieval texte")

    # 4+5 – Retrieval & Re-ranking
    lines.append("\n### 🔍 Étapes 4-5 – Retrieval & Re-ranking")
    lines.append(f"**Sources retenues :** {len(sources)}")
    for i, src in enumerate(sources, 1):
        score_r = src.get("rerank_score", src.get("score", 0))
        meta    = src.get("metadata", {})
        source_name = meta.get("source", "inconnu")
        page        = meta.get("page", "?")
        lines.append(f"- **[{i}]** Score={score_r:.3f} | {source_name} p.{page}")

    # 6 – Génération  (résumé seulement)
    lines.append("\n### 💬 Étape 6 – Génération")
    response_len = len(result.get("response", ""))
    lines.append(f"Réponse générée ({response_len} caractères)")

    # 7 – Critique Self-RAG
    lines.append("\n### ✅ Étape 7 – Self-RAG Critique")
    scores = critique.get("scores", {})
    score_global = critique.get("score_global", 0)
    validation   = critique.get("validation", "?")
    validation_icon = "✅" if validation == "ACCEPTÉE" else "⚠️"
    lines.append(f"**Score global :** {score_global:.1f}/10  {validation_icon} {validation}")
    if scores:
        for criterion, val in scores.items():
            bar = "█" * int(val) + "░" * (10 - int(val))
            lines.append(f"- {criterion.capitalize()}: {val}/10 `{bar}`")
    problems = critique.get("problemes", [])
    if problems:
        lines.append("**Problèmes :** " + " | ".join(problems))

    return "\n".join(lines)


def format_sources(sources: list) -> str:
    if not sources:
        return "Aucune source."
    lines = ["**📚 Sources utilisées :**\n"]
    for i, src in enumerate(sources, 1):
        meta  = src.get("metadata", {})
        score = src.get("rerank_score", src.get("score", 0))
        lines.append(
            f"**[{i}]** Score={score:.3f} — {meta.get('source','?')} "
            f"(page {meta.get('page','?')})"
        )
        preview = src.get("text", "")[:120].replace("\n", " ")
        lines.append(f"   *{preview}...*\n")
    return "\n".join(lines)


def get_session_info() -> str:
    duration = datetime.now() - session_start
    return f"""
**Session Info:**
- **Type :** Chatbot Agentic RAG
- **LLM Génération :** {_gen_provider} / {_gen_model}
- **LLM Pre-Retrieval :** {_pre_provider} / {_pre_model}
- **LLM Critique :** {_crit_provider} / {_crit_model}
- **Début :** {session_start.strftime('%H:%M:%S')}
- **Durée :** {duration.seconds // 60} min
- **Échanges :** {len(conversation_history)}
"""


def _is_follow_up(message: str) -> bool:
    """Détecte les relances de type 'plus court', 'résume', 'reformule', etc."""
    text = message.lower().strip()
    if not text:
        return False

    follow_up_keywords = [
        "plus court",
        "version courte",
        "résume",
        "resume",
        "reformule",
        "simplifie",
        "détaille",
        "detaille",
        "explique mieux",
        "en bref",
        "en 3 points",
        "plus clair",
        "traduis",
        "corrige",
        "continue",
        "développe",
        "developpe",
        "pareil",
        "même idée",
        "meme idee",
        "c'est la raison",
        "c est la raison",
        "c'est pourquoi",
        "c est pourquoi",
        "du coup",
        "a cause de",
        "à cause de",
        "c'est pour ça",
        "c est pour ca",
    ]

    return any(keyword in text for keyword in follow_up_keywords)


def _should_contextualize_short_message(message: str, history: list) -> bool:
    """Traite les messages courts/elliptiques comme une continuité de l'échange."""
    if not history:
        return False

    text = (message or "").strip().lower()
    if not text:
        return False

    # Si la question introduit un nouveau sujet explicite, on ne contextualise pas de force.
    new_topic_markers = [
        "qu'est-ce que", "c'est quoi", "dsm", "critères", "criteres", "définition", "definition",
        "trouble", "symptômes", "symptomes", "traitement", "comment",
    ]
    if any(marker in text for marker in new_topic_markers):
        return False

    # Messages courts émotionnels ou justificatifs -> continuité probable.
    continuation_markers = [
        "je", "moi", "ça", "ca", "cela", "du coup", "raison", "parce que",
        "seule", "seul", "peur", "stress", "angoisse",
    ]
    word_count = len(text.split())
    return word_count <= 16 and any(marker in text for marker in continuation_markers)


def _is_shortening_follow_up(message: str) -> bool:
    """Détecte explicitement une demande de condensation/résumé."""
    text = message.lower().strip()
    shortening_keywords = [
        "résume",
        "resume",
        "résumé",
        "plus court",
        "version courte",
        "en bref",
        "tl;dr",
        "synthèse",
        "synthese",
        "résumer",
        "resumer",
    ]
    return any(keyword in text for keyword in shortening_keywords)


def _content_to_text(content) -> str:
    """Normalise différents formats Gradio vers un texte simple."""
    if content is None:
        return ""

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, dict):
        value = content.get("text") or content.get("content") or content.get("value") or ""
        return str(value).strip()

    if isinstance(content, (list, tuple)):
        parts = []
        for item in content:
            txt = _content_to_text(item)
            if txt:
                parts.append(txt)
        return " ".join(parts).strip()

    return str(content).strip()


def _build_contextual_query(message: str, history: list) -> str:
    """Construit une requête enrichie avec le fil conversationnel récent."""
    if not history:
        return message

    # Conserver les 2 derniers échanges (user/assistant) pour garder le fil.
    recent = history[-4:]
    context_lines = []

    for item in recent:
        # Format messages: {"role": ..., "content": ...}
        if isinstance(item, dict):
            role = item.get("role", "")
            content = _content_to_text(item.get("content", ""))
            if content:
                if len(content) > 700:
                    content = content[:700] + "..."
                speaker = "Utilisateur" if role == "user" else "Assistant"
                context_lines.append(f"{speaker}: {content}")
            continue

        # Format tuples legacy: [user_text, assistant_text]
        if isinstance(item, (list, tuple)) and len(item) == 2:
            user_text = _content_to_text(item[0])
            assistant_text = _content_to_text(item[1])

            if user_text:
                if len(user_text) > 700:
                    user_text = user_text[:700] + "..."
                context_lines.append(f"Utilisateur: {user_text}")
            if assistant_text:
                if len(assistant_text) > 700:
                    assistant_text = assistant_text[:700] + "..."
                context_lines.append(f"Assistant: {assistant_text}")

    if not context_lines:
        return message

    context_block = "\n".join(context_lines)
    return (
        "CONTEXTE CONVERSATIONNEL A CONSERVER. "
        "La nouvelle question est probablement liée aux échanges précédents.\n\n"
        f"Historique récent:\n{context_block}\n\n"
        f"Nouvelle question utilisateur: {message}"
    )


def _rewrite_last_answer_short(message: str, history: list) -> str | None:
    """Produit un résumé court à partir de la dernière réponse assistant."""
    if not history:
        return None

    last_user = ""
    last_assistant = ""
    for item in reversed(history):
        if not last_assistant and item.get("role") == "assistant":
            last_assistant = item.get("content", "")
        if not last_user and item.get("role") == "user":
            last_user = item.get("content", "")
        if last_user and last_assistant:
            break

    if not last_assistant:
        return None

    prompt = f"""Tu dois réécrire la réponse précédente en version plus courte.

Règles:
- Réponds uniquement en français
- Garde le même sujet (ne change pas de thème)
- Supprime les répétitions
- Garde les idées cliniquement importantes
- Taille cible: 4 à 7 phrases maximum
- Si l'utilisateur demande "en points", utilise 3 à 5 puces

Question initiale:
{last_user}

Réponse précédente à condenser:
{last_assistant}

Nouvelle consigne utilisateur:
{message}

Version courte:"""

    try:
        return pipeline.generator.llm.invoke(prompt).content.strip()
    except Exception:
        return None


def save_conversation() -> str:
    if not conversation_history:
        return "⚠️ Aucune conversation à sauvegarder."
    save_dir = Path("comparaisons_chatbot")
    save_dir.mkdir(exist_ok=True)
    ts       = session_start.strftime("%Y%m%d_%H%M%S")
    filepath = save_dir / f"chatbot_agentic_rag_{ts}.json"
    data = {
        "metadata": {
            "session_start": session_start.isoformat(),
            "session_end":   datetime.now().isoformat(),
            "type":          "chatbot_agentic_rag",
            "provider_generation": _gen_provider,
            "provider_preretrival": _pre_provider,
            "provider_critique": _crit_provider,
            "llm_generation": _gen_model,
            "llm_preretrival": _pre_model,
            "llm_critique":   _crit_model,
            "total_questions": len(conversation_history),
        },
        "conversations": conversation_history,
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return f"✅ Sauvegardé → {filepath}\n📊 {len(conversation_history)} échanges"


# ─────────────────────────────────────────────
# Interface Gradio
# ─────────────────────────────────────────────
with gr.Blocks(title="Chatbot Agentic RAG") as demo:

    gr.HTML("""
    <div style="text-align:center;padding:20px;
                background:linear-gradient(135deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%);
                color:white;border-radius:10px;margin-bottom:20px;">
        <h1>🤖 Chatbot Agentic RAG</h1>
        <p>Pipeline 7 agents · Reformulation · Multi-agent · Self-RAG Critique</p>
        <p style="font-size:.85em;opacity:.8;">
            Pre-Retrieval → FAISS Retrieval → Re-ranking → Génération → Validation
        </p>
    </div>
    """)

    with gr.Row():

        # ── Colonne principale ──
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(label="💬 Conversation", height=650)

            msg = gr.Textbox(
                label="Votre question",
                placeholder="Ex: Comment la TCC aide-t-elle l'anxiété chronique ?",
                lines=2,
            )
            with gr.Row():
                submit_btn = gr.Button("📤 Envoyer", variant="primary", scale=2)
                clear_btn  = gr.Button("🗑️ Effacer", scale=1)

            sources_display = gr.Markdown(value="", label="📚 Sources")

        # ── Panneau droit ──
        with gr.Column(scale=2):
            gr.Markdown("### 🔬 Trace des agents")
            trace_display = gr.Markdown(value="*En attente d'une question...*")

            gr.Markdown("---")
            session_info = gr.Markdown(value=get_session_info())

            gr.Markdown("---")
            save_btn    = gr.Button("💾 Sauvegarder", variant="secondary")
            save_status = gr.Textbox(label="Statut", lines=2, interactive=False)

            gr.Markdown("""
---
### 💡 Avantages vs RAG simple
- ✅ Reformulation automatique
- ✅ Détection multi-aspects
- ✅ Re-ranking multi-critères
- ✅ Validation Self-RAG (score /10)

### 📝 Questions test
- Qu'est-ce que l'anxiété généralisée ?
- Comment la TCC aide l'anxiété et le stress ?
- Critères DSM-5 pour le trouble panique ?
""")

    # ── Callback principal ──
    def respond(message, chat_history):
        if not message.strip():
            return "", chat_history, get_session_info(), "*En attente...*", ""

        if _is_shortening_follow_up(message):
            short_answer = _rewrite_last_answer_short(message, chat_history)
            if short_answer:
                trace_text = (
                    "### ✂️ Relance de résumé\n"
                    "Mode local: condensation de la réponse précédente "
                    "(sans nouveau retrieval)."
                )
                sources_text = "Sources conservées depuis la réponse précédente."

                conversation_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "question": message,
                    "effective_query": "follow_up_shortening",
                    "response": short_answer,
                    "metadata": {
                        "mode": "shortening_follow_up",
                    },
                })

                chat_history.append({"role": "user", "content": message})
                chat_history.append({"role": "assistant", "content": short_answer})

                return "", chat_history, get_session_info(), trace_text, sources_text

        effective_query = _build_contextual_query(message, chat_history)

        try:
            result = pipeline.process_query(
                effective_query,
                max_retries=_max_retries,
                user_query=message,
            )

            bot_message    = result["response"]
            trace_text     = format_trace(result)
            sources_text   = format_sources(result.get("sources", []))

            conversation_history.append({
                "timestamp":          datetime.now().isoformat(),
                "question":           message,
                "effective_query":    effective_query,
                "response":           bot_message,
                "reformulated_query": result.get("reformulated_query", ""),
                "complexity":         result.get("complexity", {}),
                "critique":           result.get("critique", {}),
                "metadata":           result.get("metadata", {}),
                "sources":            [
                    {
                        "score":   s.get("rerank_score", s.get("score", 0)),
                        "source":  s.get("metadata", {}).get("source", "?"),
                        "page":    s.get("metadata", {}).get("page", "?"),
                    }
                    for s in result.get("sources", [])
                ],
            })

        except Exception as exc:
            bot_message  = f"❌ Erreur pipeline: {type(exc).__name__}: {exc}"
            trace_text   = f"Erreur: {exc}"
            sources_text = ""

        chat_history.append({"role": "user",      "content": message})
        chat_history.append({"role": "assistant", "content": bot_message})

        return "", chat_history, get_session_info(), trace_text, sources_text

    submit_btn.click(
        respond,
        inputs=[msg, chatbot],
        outputs=[msg, chatbot, session_info, trace_display, sources_display],
    )
    msg.submit(
        respond,
        inputs=[msg, chatbot],
        outputs=[msg, chatbot, session_info, trace_display, sources_display],
    )
    clear_btn.click(
        lambda: (None, get_session_info(), "*En attente...*", ""),
        outputs=[chatbot, session_info, trace_display, sources_display],
    )
    save_btn.click(save_conversation, outputs=save_status)

    gr.HTML("""
    <div style="text-align:center;margin-top:15px;opacity:.6;font-size:.85em;">
        🤖 Agentic RAG · 7 agents · Groq API
    </div>
    """)


if __name__ == "__main__":
    server_port = _env_int("AGENTIC_UI_PORT", _env_int("GRADIO_SERVER_PORT", 7867))

    print("\n" + "=" * 60)
    print(f"🚀 Lancement interface Gradio Agentic RAG sur port {server_port}...")
    print("=" * 60 + "\n")

    demo.launch(
        server_name="127.0.0.1",
        server_port=server_port,
        share=False,
        show_error=True,
    )
