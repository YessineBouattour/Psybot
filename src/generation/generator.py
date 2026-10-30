"""
Générateur de réponses avec contexte RAG
"""
from typing import List, Dict
from langchain_core.prompts import PromptTemplate


class RAGResponseGenerator:
    """
    Génère des réponses basées sur le contexte récupéré
    """
    
    def __init__(self, llm):
        """
        Args:
            llm: LangChain LLM
        """
        self.llm = llm
        
        self.generation_prompt = PromptTemplate(
            input_variables=["query", "context"],
            template="""Tu es un assistant spécialisé en gestion de l'anxiété et troubles anxieux.

Tu dois répondre à la question de l'utilisateur en te basant UNIQUEMENT sur le contexte fourni ci-dessous.

CONTEXTE:
{context}

QUESTION: {query}

INSTRUCTIONS:
1. Réponds de manière empathique et claire
2. Base-toi UNIQUEMENT sur les informations du contexte
3. Si le contexte ne contient pas l'information, dis-le honnêtement
4. Utilise un langage accessible (évite jargon médical excessif)
5. Suggère de consulter un professionnel si la question concerne des symptômes graves
6. Choisis la structure la plus adaptée à la question (réponse directe, mini-plan, comparaison, liste d'actions, synthèse).
7. N'utilise PAS systématiquement les mêmes titres ni le même ordre d'idées d'une réponse à l'autre.
8. Si la question est académique (DSM, critères, définition), une structure plus formelle est autorisée.
9. Si la question est pratique, privilégie une forme concise et actionnable.
7. Priorise l'exactitude factuelle: ne déduis pas au-delà du contexte
10. Cite explicitement les sources du contexte quand possible (ex: Source 1, Source 2)
11. Donne une réponse utile et suffisamment détaillée
12. N'ajoute pas de question de relance à la fin

RÉPONSE:"""
        )

        self.conversational_prompt = PromptTemplate(
            input_variables=["query", "context"],
            template="""Tu es un assistant de soutien psychoéducatif, empathique et concret.

Tu dois répondre à l'utilisateur en te basant UNIQUEMENT sur le contexte ci-dessous.

CONTEXTE:
{context}

MESSAGE UTILISATEUR: {query}

INSTRUCTIONS:
1. Réponds de façon naturelle et humaine (pas format rapport académique).
2. N'ajoute PAS de diagnostic médical non demandé.
3. Évite les sections rigides "Définition/Signes/Différenciation" sauf si la question l'exige explicitement.
4. Donne une aide pratique immédiate en 3 à 5 actions concrètes.
5. Sois concis: 6 à 10 phrases maximum.
6. Si nécessaire, termine par une question de clarification utile.
7. Si le contexte ne suffit pas, dis-le brièvement et reste prudent.

RÉPONSE:"""
        )

    def _response_style(self, query: str) -> str:
        """Détermine le style de sortie: académique vs conversationnel."""
        q = (query or "").lower().strip()

        academic_markers = [
            "dsm", "critères", "criteres", "définition", "definition",
            "diagnostic", "étiologie", "etiologie", "prévalence", "prevalence",
            "compare", "comparer", "versus", "vs", "trouble", "classification",
        ]
        conversational_markers = [
            "je suis", "je me sens", "j'ai", "aide-moi", "aide moi",
            "que faire", "comment faire", "j'arrive pas", "je n'arrive pas",
            "stressé", "stresse", "angoissé", "angoisse", "panique",
        ]

        # Questions académiques prioritaires: forcer le mode structuré même si la forme est courte.
        if any(marker in q for marker in ["dsm", "critères", "criteres", "définition", "definition"]):
            return "academic"

        if any(marker in q for marker in conversational_markers):
            return "conversational"
        if any(marker in q for marker in academic_markers):
            return "academic"

        if len(q.split()) <= 8:
            return "conversational"

        return "academic"
    
    def generate(
        self,
        query: str,
        context_chunks: List[Dict],
        max_context_length: int = 2000
    ) -> Dict:
        """
        Génère une réponse basée sur les chunks récupérés
        
        Args:
            query: Question de l'utilisateur
            context_chunks: Chunks récupérés et re-ranked
            max_context_length: Longueur max du contexte
            
        Returns:
            Dict avec response, sources, metadata
        """
        print(f"\n💬 GÉNÉRATION: Création de la réponse...")
        
        # Construire contexte
        context_parts = []
        total_length = 0
        used_chunks = []
        
        for i, chunk in enumerate(context_chunks):
            chunk_text = f"[Source {i+1}] {chunk['text']}"
            chunk_length = len(chunk_text)
            
            if total_length + chunk_length <= max_context_length:
                context_parts.append(chunk_text)
                used_chunks.append(chunk)
                total_length += chunk_length
            else:
                break
        
        context = "\n\n".join(context_parts)
        
        print(f"   Contexte: {len(used_chunks)} chunks, {total_length} caractères")
        
        # Générer réponse
        style = self._response_style(query)
        prompt_template = self.conversational_prompt if style == "conversational" else self.generation_prompt

        prompt = prompt_template.format(query=query, context=context)
        
        try:
            response = self.llm.invoke(prompt).content.strip()
            
            print(f"   ✓ Réponse générée ({len(response)} caractères)")
            
            return {
                'response': response,
                'sources': used_chunks,
                'n_sources': len(used_chunks),
                'query': query
            }
            
        except Exception as e:
            print(f"❌ Erreur génération: {e}")
            return {
                'response': f"Désolé, une erreur s'est produite lors de la génération de la réponse. Erreur: {str(e)}",
                'sources': used_chunks,
                'n_sources': len(used_chunks),
                'query': query,
                'error': str(e)
            }


if __name__ == "__main__":
    print("Module génération chargé")
