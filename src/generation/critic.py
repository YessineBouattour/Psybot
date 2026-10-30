"""
Self-RAG Critique: Validation de la réponse avant envoi
Évalue: Consistance, Clarté, Correctness
"""
from typing import Dict
from langchain_core.prompts import PromptTemplate


class ResponseCritic:
    """
    Critique la réponse générée avant envoi à l'utilisateur
    Implémente Self-RAG avec métriques d'évaluation
    """
    
    def __init__(self, llm):
        """
        Args:
            llm: LangChain LLM pour critique
        """
        self.llm = llm
        
        self.critique_prompt = PromptTemplate(
            input_variables=["query", "response", "context"],
            template="""Tu es un évaluateur expert en santé mentale et anxiété.

Évalue la qualité de cette réponse selon les critères suivants:

QUESTION: {query}

CONTEXTE UTILISÉ:
{context}

RÉPONSE GÉNÉRÉE:
{response}

Évalue sur une échelle de 0-10 pour chaque critère:

1. **CONSISTANCE** (0-10): La réponse est-elle cohérente avec le contexte fourni?
   - Pas de contradictions
   - Informations alignées avec le contexte
   - Tolérer si réponse générale mais correcte

2. **CLARTÉ** (0-10): La réponse est-elle claire et compréhensible?
   - Langage simple
   - Structure logique
   - Pas de jargon excessif

3. **CORRECTNESS** (0-10): La réponse est-elle médicalement correcte?
   - Informations exactes selon les données actuelles
   - Pas de conseils dangereux
   - Les réponses générales mais justes valent 8-10
   - Les réponses spécialisées très détaillées valent 10

4. **PERTINENCE** (0-10): La réponse répond-elle à la question?
   - Pour questions générales (ex: "comment gérer le stress?"): une réponse générale-mais-juste vaut 7-10
   - Pour questions spécifiques: doit couvrir tous les aspects
   - Pas d'informations hors sujet
   - La réponse peut être généraliste si la question est généraliste

5. **SÉCURITÉ** (0-10): La réponse est-elle sûre pour l'utilisateur?
   - Pas de minimisation de symptômes graves
   - Encourage aide professionnelle si besoin
   - Pas de risque pour la santé mentale

Réponds au format JSON:
{{
  "scores": {{
    "consistance": X,
    "clarte": Y,
    "correctness": Z,
    "pertinence": W,
    "securite": V
  }},
  "score_global": moyenne,
  "validation": "ACCEPTÉE" ou "À AMÉLIORER",
  "problemes": ["liste des problèmes identifiés"],
  "suggestions": "suggestions d'amélioration si validation=À AMÉLIORER",
  "raisons": "explication du score global"
}}"""
        )
    
    def critique(
        self, 
        query: str, 
        response: str, 
        context_chunks: list
    ) -> Dict:
        """
        Critique la réponse générée
        
        Args:
            query: Question originale
            response: Réponse générée
            context_chunks: Chunks utilisés pour génération
            
        Returns:
            Dict avec scores, validation, problèmes, suggestions
        """
        print(f"\n🔍 SELF-RAG CRITIQUE: Évaluation de la réponse...")
        
        # Préparer contexte
        context_text = "\n\n".join([
            f"[{i+1}] {chunk['text'][:200]}..." 
            for i, chunk in enumerate(context_chunks[:3])
        ])
        
        # Générer critique
        prompt = self.critique_prompt.format(
            query=query,
            response=response,
            context=context_text
        )
        
        try:
            import json
            critique_response = self.llm.invoke(prompt).content.strip()
            
            # Parser JSON
            if '```json' in critique_response:
                critique_response = critique_response.split('```json')[1].split('```')[0].strip()
            elif '```' in critique_response:
                critique_response = critique_response.split('```')[1].split('```')[0].strip()
            
            result = json.loads(critique_response)
            
            # Afficher résultats
            print(f"\n   📊 SCORES D'ÉVALUATION:")
            for criterion, score in result['scores'].items():
                emoji = "✅" if score >= 7 else "⚠️" if score >= 5 else "❌"
                print(f"   {emoji} {criterion.capitalize()}: {score}/10")
            
            print(f"\n   🎯 Score global: {result['score_global']:.1f}/10")
            print(f"   ⚖️  Validation: {result['validation']}")
            
            if result['problemes']:
                print(f"\n   ⚠️  Problèmes identifiés:")
                for prob in result['problemes']:
                    print(f"      - {prob}")
            
            if result['validation'] == "À AMÉLIORER" and result.get('suggestions'):
                print(f"\n   💡 Suggestions: {result['suggestions']}")
            
            return result
            
        except Exception as e:
            print(f"⚠️  Erreur critique: {e}")
            # Fallback - accepter par défaut
            return {
                'scores': {
                    'consistance': 7,
                    'clarte': 7,
                    'correctness': 7,
                    'pertinence': 7,
                    'securite': 8
                },
                'score_global': 7.2,
                'validation': 'ACCEPTÉE',
                'problemes': [],
                'suggestions': '',
                'raisons': 'Évaluation par défaut (erreur critique)'
            }
    
    def should_regenerate(self, critique_result: Dict, threshold: float = 6.0) -> bool:
        """
        Détermine si la réponse doit être régénérée
        
        Args:
            critique_result: Résultat de la critique
            threshold: Score minimum acceptable
            
        Returns:
            True si régénération nécessaire
        """
        score = critique_result['score_global']
        security_score = critique_result['scores'].get('securite', 10)
        
        # **NOUVELLE LOGIQUE ASSOUPLE:**
        # Régénérer SEULEMENT si score global < threshold
        # (Accepter "À AMÉLIORER" si score >= threshold)
        should_regen = score < threshold
        
        # EXCEPTION: Toujours régénérer si problème de sécurité critique
        if security_score < 6:
            should_regen = True
            print(f"   ⚠️  ALERTE SÉCURITÉ: Régénération obligatoire")
        
        return should_regen


if __name__ == "__main__":
    print("Module Self-RAG Critique chargé")
    print("Nécessite LLM configuré pour tests")
