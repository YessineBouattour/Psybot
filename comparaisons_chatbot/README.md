# Comparaison Chatbot Sans RAG vs Avec RAG

Ce dossier contient les captures de conversations pour analyse comparative.

## Structure des fichiers

### Chatbot Sans RAG
- Fichiers: `chatbot_sans_rag_*.json`
- Type: Réponses basées uniquement sur les connaissances générales du LLM
- Utilisation: Référence de base pour montrer les limitations

### Chatbot Avec RAG (à venir)
- Fichiers: `chatbot_avec_rag_*.json`
- Type: Réponses enrichies par les documents spécialisés
- Utilisation: Démonstration de l'amélioration apportée par le RAG

## Format des fichiers JSON

```json
{
  "metadata": {
    "session_start": "timestamp",
    "type": "chatbot_sans_rag" ou "chatbot_avec_rag",
    "llm_provider": "ollama/openai/anthropic",
    "llm_model": "nom_du_modèle",
    "total_questions": nombre
  },
  "conversations": [
    {
      "timestamp": "timestamp",
      "question": "Question posée",
      "response": "Réponse générée"
    }
  ]
}
```

## Utilisation pour le rapport

1. **Captures d'écran**: Prenez des captures des réponses affichées
2. **Analyse JSON**: Utilisez les fichiers JSON pour analyses quantitatives
3. **Comparaison côte à côte**: Montrez les différences entre sans/avec RAG
4. **Métriques**: Comparez la précision, la pertinence, les sources citées

## Questions recommandées pour la comparaison

- Questions sur des concepts spécifiques dans vos PDFs
- Questions nécessitant des informations précises
- Questions sur des techniques thérapeutiques
- Questions nécessitant des sources fiables
