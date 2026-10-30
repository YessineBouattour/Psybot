"""
Documentation: Configuration Multi-Modèles LangChain
====================================================

POURQUOI MULTI-MODÈLES?
-----------------------
Chaque LLM a ses forces. En les combinant, on optimise:
- 💰 Coûts (modèles moins chers pour tâches simples)
- ⚡ Performance (meilleur modèle pour chaque tâche)
- 🎯 Qualité (spécialisation par étape)

ARCHITECTURE RECOMMANDÉE
------------------------

┌─────────────────────────────────────────────────────────┐
│  ÉTAPE 1: PRE-RETRIEVAL (Reformulation & Analyse)      │
│  Modèle: GPT-4o-mini ou DeepSeek                       │
│  Pourquoi: Excellente compréhension du français         │
│  Coût: ~$0.15/1M tokens (GPT) ou ~$0.14/1M (DeepSeek) │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  ÉTAPE 2: RETRIEVAL (Recherche vectorielle)            │
│  Modèle: Embeddings (paraphrase-multilingual)          │
│  Pourquoi: Déjà optimisé, pas de LLM nécessaire        │
│  Coût: Gratuit (local)                                  │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  ÉTAPE 3: GENERATION (Création de la réponse)          │
│  Modèle: DeepSeek ou Mistral (local)                   │
│  Pourquoi: Moins cher, bonne qualité pour génération   │
│  Coût: ~$0.14/1M tokens (DeepSeek) ou Gratuit (local) │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  ÉTAPE 4: CRITIQUE (Validation sécurité)               │
│  Modèle: Claude Haiku ou GPT-4o-mini                   │
│  Pourquoi: Meilleur pour éthique/sécurité santé        │
│  Coût: ~$0.25/1M tokens (Claude) ou ~$0.15/1M (GPT)   │
└─────────────────────────────────────────────────────────┘

CONFIGURATIONS TYPES
--------------------

### 1. MODE PRODUCTION (Optimal qualité/coût)
```env
PRERETRIVAL_PROVIDER=openai
PRERETRIVAL_MODEL=gpt-4o-mini

GENERATION_PROVIDER=deepseek
GENERATION_MODEL=deepseek-chat

CRITIQUE_PROVIDER=anthropic
CRITIQUE_MODEL=claude-3-haiku-20240307
```

Coût estimé: ~$0.50/1000 conversations


### 2. MODE ÉCONOMIQUE (DeepSeek partout)
```env
PRERETRIVAL_PROVIDER=deepseek
PRERETRIVAL_MODEL=deepseek-chat

GENERATION_PROVIDER=deepseek
GENERATION_MODEL=deepseek-chat

CRITIQUE_PROVIDER=deepseek
CRITIQUE_MODEL=deepseek-chat
```

Coût estimé: ~$0.40/1000 conversations


### 3. MODE LOCAL (100% Gratuit)
```env
PRERETRIVAL_PROVIDER=ollama
PRERETRIVAL_MODEL=mistral

GENERATION_PROVIDER=ollama
GENERATION_MODEL=mistral

CRITIQUE_PROVIDER=ollama
CRITIQUE_MODEL=mistral
```

Coût: $0 (mais nécessite bon GPU/CPU)


### 4. MODE PREMIUM (Qualité maximale)
```env
PRERETRIVAL_PROVIDER=openai
PRERETRIVAL_MODEL=gpt-4o

GENERATION_PROVIDER=anthropic
GENERATION_MODEL=claude-3-5-sonnet-20241022

CRITIQUE_PROVIDER=openai
CRITIQUE_MODEL=gpt-4o
```

Coût estimé: ~$5/1000 conversations


API KEYS NÉCESSAIRES
--------------------

### OpenAI
1. Créer compte: https://platform.openai.com
2. Ajouter crédit (minimum $5)
3. Générer clé: https://platform.openai.com/api-keys
4. Dans .env: OPENAI_API_KEY=sk-proj-...

### Anthropic (Claude)
1. Créer compte: https://console.anthropic.com
2. Ajouter crédit (minimum $5)
3. Générer clé: https://console.anthropic.com/settings/keys
4. Dans .env: ANTHROPIC_API_KEY=sk-ant-...

### DeepSeek (Moins cher!)
1. Créer compte: https://platform.deepseek.com
2. Gratuit jusqu'à 10M tokens/mois!
3. Générer clé: https://platform.deepseek.com/api_keys
4. Dans .env: DEEPSEEK_API_KEY=sk-...

### Ollama (Gratuit local)
1. Télécharger: https://ollama.ai/download
2. Installer
3. Commande: ollama pull mistral
4. Pas de clé API nécessaire


COMPARAISON COÛTS (Par 1M tokens)
----------------------------------
| Modèle              | Input   | Output  | Français | Qualité |
|---------------------|---------|---------|----------|---------|
| DeepSeek Chat       | $0.14   | $0.28   | ⭐⭐⭐⭐    | ⭐⭐⭐⭐   |
| GPT-4o-mini         | $0.15   | $0.60   | ⭐⭐⭐⭐⭐   | ⭐⭐⭐⭐⭐  |
| Claude Haiku        | $0.25   | $1.25   | ⭐⭐⭐⭐⭐   | ⭐⭐⭐⭐   |
| GPT-4o              | $2.50   | $10.00  | ⭐⭐⭐⭐⭐   | ⭐⭐⭐⭐⭐  |
| Claude Sonnet 3.5   | $3.00   | $15.00  | ⭐⭐⭐⭐⭐   | ⭐⭐⭐⭐⭐  |
| Mistral (local)     | $0      | $0      | ⭐⭐⭐⭐    | ⭐⭐⭐    |


INSTALLATION PACKAGES
---------------------
```bash
# DeepSeek (via OpenAI SDK)
pip install langchain-openai

# Claude
pip install langchain-anthropic

# Ollama
pip install langchain-ollama

# Utilitaire
pip install python-dotenv
```


EXEMPLE D'UTILISATION
---------------------
```python
from demo_agentic_rag import get_llm

# Charger LLM spécifique pour chaque étape
llm_preretrival = get_llm('preretrival')  # GPT-4o-mini
llm_generation = get_llm('generation')     # DeepSeek
llm_critique = get_llm('critique')         # Claude Haiku

# Ou mode mono-modèle
llm = get_llm()  # Utilise LLM_PROVIDER par défaut
```


DÉPANNAGE
---------

Erreur: "API key manquante"
→ Vérifiez .env, pas de 'your_key_here'

Erreur: "Connection timeout"
→ Vérifiez connexion Internet, proxy

Erreur: "Rate limit exceeded"
→ Attendez ou augmentez quota

Modèle lent en local
→ Mistral nécessite 8GB RAM minimum


RECOMMANDATION FINALE
----------------------
Pour un chatbot d'anxiété en production:

✅ Pre-retrieval: GPT-4o-mini (meilleure compréhension)
✅ Generation: DeepSeek (rapport qualité/prix)
✅ Critique: Claude Haiku (sécurité santé mentale)

Coût estimé: $0.50 pour 1000 conversations
Qualité: Production-ready ⭐⭐⭐⭐⭐
