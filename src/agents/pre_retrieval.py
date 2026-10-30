"""
Pre-Retrieval: Query Understanding & Reformulation (SELFRag)
Ajoute contexte médical et termes techniques
"""
import difflib
from typing import Dict, List, Optional
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage


class QueryReformulator:
    """
    Reformule les requêtes utilisateur de manière NEUTRE pour améliorer le retrieval
    sans sur-interprétation clinique.
    """
    
    def __init__(self, llm):
        """
        Args:
            llm: LangChain LLM (OpenAI, Anthropic, local, etc.)
        """
        self.llm = llm
        
        self.reformulation_prompt = PromptTemplate(
            input_variables=["query"],
            template="""Tu es un assistant de reformulation pour la recherche documentaire.

    Ta tâche est de reformuler la requête pour améliorer le retrieval, tout en restant fidèle à l'intention.

    Question originale: {query}

    Contraintes strictes:
    1. N'ajoute PAS de diagnostic, hypothèse clinique ou étiquette de trouble non demandée.
    2. N'invente pas de symptômes ni de contexte supplémentaire.
    3. Garde la reformulation courte (max 20 mots) et précise.
    4. Si la requête est déjà claire, conserve-la presque telle quelle.
    5. Une seule phrase, sans puces.

    Reformulation fidèle:"""
        )
    
    def reformulate(self, query: str) -> Dict[str, str]:
        """
        Reformule la requête en ajoutant contexte
        
        Args:
            query: Question utilisateur originale
            
        Returns:
            Dict avec 'original', 'reformulated', 'keywords'
        """
        print(f"\n🔄 PRE-RETRIEVAL: Reformulation de la requête...")
        print(f"   Original: '{query}'")
        
        # Générer reformulation
        prompt = self.reformulation_prompt.format(query=query)
        
        try:
            if self.llm is None:
                reformulated = query
            else:
                reformulated = self.llm.invoke(prompt).content.strip()
        except Exception as e:
            print(f"⚠️  Erreur reformulation: {e}")
            reformulated = query

        # Si le LLM dérive, applique un garde-fou local neutre.
        reformulated = self._ensure_safe_reformulation(query, reformulated)
        
        # Extraire mots-clés
        keywords = self._extract_keywords(reformulated)
        
        print(f"   Reformulée: '{reformulated}'")
        print(f"   Mots-clés: {', '.join(keywords)}")
        
        return {
            'original': query,
            'reformulated': reformulated,
            'keywords': keywords
        }

    def _ensure_safe_reformulation(self, original: str, reformulated: str) -> str:
        """Garantit une reformulation fidèle, courte et non-diagnostique."""
        reformulated = (reformulated or "").strip()

        # Nettoyage de préfixes fréquents renvoyés par certains modèles.
        prefixes = [
            "reformulation enrichie:",
            "reformulation:",
            "question reformulée:",
            "question reformulee:",
        ]
        low = reformulated.lower()
        for prefix in prefixes:
            if low.startswith(prefix):
                reformulated = reformulated[len(prefix):].strip(" '\":")
                break

        orig_norm = " ".join(original.lower().split())
        ref_norm = " ".join(reformulated.lower().split())
        similarity = difflib.SequenceMatcher(None, orig_norm, ref_norm).ratio()

        # Cas d'échec: vide, identique, ou quasi identique.
        if (
            not ref_norm
            or ref_norm == orig_norm
            or similarity >= 0.92
            or len(ref_norm) < max(20, int(0.7 * len(orig_norm)))
        ):
            return self._heuristic_rewrite(original)

        # Evite les reformulations trop longues qui diluent la requête.
        words = reformulated.split()
        if len(words) > 20:
            reformulated = " ".join(words[:20])

        # Garde-fou anti-surdiagnostic.
        lower_ref = reformulated.lower()
        diagnostic_triggers = [
            "vous souffrez", "vous avez", "diagnostic", "tag", "tsp", "tspt",
            "trouble anxieux généralisé", "trouble de stress post-traumatique",
            "personnalité évitante", "pathologie",
        ]
        if any(t in lower_ref for t in diagnostic_triggers):
            return self._heuristic_rewrite(original)

        return reformulated

    def _is_anxiety_domain(self, query: str) -> bool:
        text = query.lower()
        anxiety_terms = [
            "anxiété", "anxiete", "stress", "angoisse", "panique", "phobie",
            "tag", "trouble anxieux", "rumination", "insomnie", "tcc",
            "thérapie", "therapie", "dépression", "depression",
        ]
        return any(term in text for term in anxiety_terms)

    def _heuristic_rewrite(self, query: str) -> str:
        """Fallback local fidèle à la question, sans ajout clinique spéculatif."""
        q = query.strip()
        text = q.lower()

        # Requêtes courtes émotionnelles: reformulation minimale.
        if len(text.split()) <= 6 and any(k in text for k in ["stress", "anxi", "angoiss", "panique"]):
            return f"Comment gérer {q.lower()} au quotidien ?"

        if any(k in text for k in ["qu'est-ce que", "c'est quoi", "défin", "definition"]):
            return f"Définition claire de {q} et éléments clés à connaître."

        if any(k in text for k in ["pourquoi", "cause", "facteur", "déclenche", "declenche"]):
            return f"Causes et facteurs possibles liés à {q}."

        if any(k in text for k in ["comparer", "vs", "versus", "différence", "difference"]):
            return f"Comparaison structurée concernant {q}."

        if any(k in text for k in ["plan", "étapes", "etapes", "semaine", "programme"]):
            return f"Plan pratique par étapes pour {q}."

        return q
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extrait mots-clés médicaux du texte"""
        # Liste de termes médicaux courants
        medical_terms = [
            'anxiété', 'TAG', 'TCC', 'trouble anxieux', 'panique',
            'stress', 'thérapie cognitive', 'comportementale',
            'mindfulness', 'relaxation', 'respiration', 'exposition',
            'rumination', 'inquiétude', 'somatique', 'hypervigilance'
        ]
        
        text_lower = text.lower()
        found_keywords = [term for term in medical_terms if term in text_lower]
        
        return found_keywords[:5]  # Top 5


class QueryComplexityAnalyzer:
    """
    Analyse la complexité d'une requête
    Détermine si décomposition multi-agent nécessaire
    """
    
    def __init__(self, llm):
        self.llm = llm
        
        self.complexity_prompt = PromptTemplate(
            input_variables=["query"],
            template="""Analyse la COMPLEXITÉ de cette question sur l'anxiété.

Question: {query}

Détermine:
1. COMPLEXITÉ: SIMPLE (1 aspect) ou COMPLEXE (plusieurs aspects)
2. ASPECTS: Liste les différents aspects/sous-questions
3. NÉCESSITE DÉCOMPOSITION: OUI/NON

Réponds au format JSON:
{{
  "complexity": "SIMPLE" ou "COMPLEXE",
  "aspects": ["aspect1", "aspect2", ...],
  "needs_decomposition": true/false,
  "reasoning": "explication"
}}"""
        )
    
    def analyze(self, query: str) -> Dict:
        """
        Analyse la complexité de la requête
        
        Returns:
            Dict avec complexity, aspects, needs_decomposition
        """
        print(f"\n🧠 ANALYSE COMPLEXITÉ...")
        
        prompt = self.complexity_prompt.format(query=query)
        
        try:
            import json
            response = self.llm.invoke(prompt).content.strip()
            
            # Parser JSON
            # Extraire JSON si enrobé dans ```json
            if '```json' in response:
                response = response.split('```json')[1].split('```')[0].strip()
            elif '```' in response:
                response = response.split('```')[1].split('```')[0].strip()
            
            result = json.loads(response)

            # Renforce la robustesse: certaines requêtes multi-objectifs sont
            # parfois classées SIMPLE par le LLM. On force COMPLEXE dans ce cas.
            result = self._apply_complexity_override(query, result)
            
            print(f"   Complexité: {result['complexity']}")
            print(f"   Aspects: {len(result['aspects'])}")
            print(f"   Décomposition: {'OUI' if result['needs_decomposition'] else 'NON'}")
            
            return result
            
        except Exception as e:
            print(f"⚠️  Erreur analyse: {e}")
            # Fallback heuristique robuste (évite de forcer SIMPLE à tort)
            return self._heuristic_complexity_fallback(query)

    def _heuristic_complexity_fallback(self, query: str) -> Dict:
        text = query.lower()

        multi_intent_terms = [
            "compare", "comparer", "différence", "difference", "versus", "vs",
            "puis", "ensuite", "et", "ou", "plan", "étapes", "etapes",
            "priorités", "priorites", "risques", "indicateurs", "semaine",
            "semaines", "court terme", "long terme", "avantages", "inconvénients",
            "inconvenients",
        ]
        found_terms = [term for term in multi_intent_terms if term in text]

        if len(found_terms) >= 3:
            return {
                'complexity': 'COMPLEXE',
                'aspects': [
                    'comparaison des approches',
                    'plan d\'action',
                    'risques et indicateurs de suivi',
                ],
                'needs_decomposition': True,
                'reasoning': f"Fallback heuristique multi-intention: {', '.join(found_terms[:6])}",
            }

        return {
            'complexity': 'SIMPLE',
            'aspects': [query],
            'needs_decomposition': False,
            'reasoning': 'Fallback heuristique: question simple/mono-intention',
        }

    def _apply_complexity_override(self, query: str, result: Dict) -> Dict:
        text = query.lower()

        # Indices de multi-intention / planification structurée.
        multi_intent_terms = [
            "compare", "comparer", "différence", "difference", "versus", "vs",
            "puis", "ensuite", "et", "ou", "plan", "étapes", "etapes",
            "priorités", "priorites", "risques", "indicateurs", "semaine",
            "semaines", "court terme", "long terme", "avantages", "inconvénients",
            "inconvenients",
        ]

        found_terms = [term for term in multi_intent_terms if term in text]
        aspects = result.get('aspects', []) if isinstance(result.get('aspects', []), list) else []

        # Règle: si >= 3 indices multi-intention, on active la décomposition.
        if len(found_terms) >= 3 or len(aspects) >= 3:
            result['complexity'] = 'COMPLEXE'
            result['needs_decomposition'] = True

            if not aspects:
                # Fallback minimal si le LLM n'a pas fourni d'aspects utilisables.
                result['aspects'] = [
                    'comparaison des approches',
                    'plan d\'action',
                    'risques et indicateurs de suivi',
                ]

            base_reason = result.get('reasoning', '')
            result['reasoning'] = (
                f"{base_reason} | override_heuristique_multi_intention: {', '.join(found_terms[:6])}"
            ).strip(' |')

        return result


class SubQueryDecomposer:
    """
    Décompose requêtes complexes en sous-requêtes
    Pour traitement multi-agent
    """
    
    def __init__(self, llm):
        self.llm = llm
        
        self.decomposition_prompt = PromptTemplate(
            input_variables=["query", "aspects"],
            template="""Décompose cette question complexe en sous-questions indépendantes.

Question principale: {query}
Aspects identifiés: {aspects}

Génère 2-4 sous-questions SPÉCIFIQUES et INDÉPENDANTES.
Chaque sous-question doit être répondable séparément.

Format JSON:
{{
  "sub_queries": [
    {{"id": 1, "query": "sous-question 1", "aspect": "aspect concerné"}},
    {{"id": 2, "query": "sous-question 2", "aspect": "aspect concerné"}}
  ]
}}"""
        )
    
    def decompose(self, query: str, aspects: List[str]) -> List[Dict]:
        """
        Décompose en sous-requêtes
        
        Returns:
            Liste de dicts {id, query, aspect}
        """
        print(f"\n🔀 DÉCOMPOSITION EN SOUS-REQUÊTES...")
        
        prompt = self.decomposition_prompt.format(
            query=query,
            aspects=', '.join(aspects)
        )
        
        try:
            import json

            if self.llm is None:
                return self._fallback_sub_queries(query, aspects)

            response = self.llm.invoke(prompt).content.strip()
            
            # Parser JSON
            if '```json' in response:
                response = response.split('```json')[1].split('```')[0].strip()
            elif '```' in response:
                response = response.split('```')[1].split('```')[0].strip()
            
            result = json.loads(response)
            sub_queries = result.get('sub_queries', [])

            sub_queries = self._normalize_sub_queries(query, aspects, sub_queries)
            
            print(f"   {len(sub_queries)} sous-requêtes générées:")
            for sq in sub_queries:
                print(f"   {sq['id']}. {sq['query']}")
            
            return sub_queries
            
        except Exception as e:
            print(f"⚠️  Erreur décomposition: {e}")
            return self._fallback_sub_queries(query, aspects)

    def _normalize_sub_queries(self, query: str, aspects: List[str], sub_queries: List[Dict]) -> List[Dict]:
        """Nettoie la sortie LLM et garantit une vraie décomposition (>=2)."""
        cleaned: List[Dict] = []

        for i, sq in enumerate(sub_queries, 1):
            if not isinstance(sq, dict):
                continue
            q = str(sq.get('query', '')).strip()
            if not q:
                continue
            cleaned.append({
                'id': i,
                'query': q,
                'aspect': str(sq.get('aspect', f'aspect_{i}')).strip() or f'aspect_{i}',
            })

        # Si le LLM renvoie 0 ou 1 sous-question, fallback structuré.
        if len(cleaned) < 2:
            return self._fallback_sub_queries(query, aspects)

        # Limite de sécurité: max 4 sous-questions.
        return cleaned[:4]

    def _fallback_sub_queries(self, query: str, aspects: List[str]) -> List[Dict]:
        """Fallback déterministe basé sur les aspects de complexité."""
        aspects = [a for a in aspects if isinstance(a, str) and a.strip()]

        if len(aspects) >= 2:
            fallback = []
            for i, aspect in enumerate(aspects[:4], 1):
                fallback.append({
                    'id': i,
                    'query': f"Concernant '{aspect}', répondre à: {query}",
                    'aspect': aspect,
                })
            return fallback

        return [
            {
                'id': 1,
                'query': f"Comparer les approches principales pour: {query}",
                'aspect': 'comparaison des approches',
            },
            {
                'id': 2,
                'query': f"Proposer un plan d'action avec suivi pour: {query}",
                'aspect': 'plan et indicateurs',
            },
        ]


class RetrievalRouter:
    """
    Décide si la question nécessite uniquement du retrieval textuel
    ou un mode hybride texte + graphe.

    Le mode graphe est optionnel: si le pipeline graphe n'est pas encore branché,
    la décision est quand même exposée en metadata pour instrumentation.
    """

    def __init__(self, llm=None):
        self.llm = llm
        self.routing_prompt = PromptTemplate(
            input_variables=["query", "complexity", "aspects"],
            template="""Tu es un routeur de pipeline RAG.

Question: {query}
Complexité: {complexity}
Aspects: {aspects}

Décide le mode de retrieval:
- "text_only": si la question est définitionnelle, explicative, ou conseil général.
- "text_graph": si la question est relationnelle (liens entités-entités, cause-effet, dépendances, chaîne de raisonnement explicite).

Réponds STRICTEMENT en JSON:
{{
  "route": "text_only" ou "text_graph",
  "confidence": 0.0-1.0,
  "reason": "justification courte"
}}"""
        )

    def decide(self, query: str, complexity: Optional[Dict] = None) -> Dict:
        """Décide le mode retrieval avec fallback heuristique robuste."""
        complexity = complexity or {}

        heuristic = self._heuristic_route(query, complexity)

        # Si pas de LLM, on retourne la décision heuristique.
        if not self.llm:
            return heuristic

        try:
            import json

            prompt = self.routing_prompt.format(
                query=query,
                complexity=complexity.get("complexity", "SIMPLE"),
                aspects=", ".join(complexity.get("aspects", [])),
            )
            response = self.llm.invoke(prompt).content.strip()

            if '```json' in response:
                response = response.split('```json')[1].split('```')[0].strip()
            elif '```' in response:
                response = response.split('```')[1].split('```')[0].strip()

            parsed = json.loads(response)

            route = parsed.get("route", heuristic["route"])
            if route not in {"text_only", "text_graph"}:
                route = heuristic["route"]

            # Garde-fou: si l'heuristique détecte une question relationnelle,
            # on force text_graph même si le LLM répond text_only.
            if heuristic.get("route") == "text_graph" and route == "text_only":
                route = "text_graph"
                reason = (
                    f"{parsed.get('reason', '')} | override heuristique relationnelle"
                ).strip(" |")
                confidence = max(0.85, float(parsed.get("confidence", 0.0)))
                return {
                    "route": route,
                    "confidence": confidence,
                    "reason": reason,
                    "source": "llm+heuristic_override",
                }

            return {
                "route": route,
                "confidence": float(parsed.get("confidence", heuristic["confidence"])),
                "reason": parsed.get("reason", heuristic["reason"]),
                "source": "llm",
            }
        except Exception as e:
            print(f"⚠️  Erreur routing LLM: {e}")
            heuristic["source"] = "heuristic_fallback"
            return heuristic

    def _heuristic_route(self, query: str, complexity: Dict) -> Dict:
        text = query.lower()

        relation_terms = [
            "relation", "lié", "associe", "associee", "associer",
            "cause", "effet", "dépend", "depend", "impact",
            "chaîne", "chaine", "graphe", "réseau", "reseau",
            "entre", "corrélation", "correlation",
            "influence", "influe", "influencent", "interaction",
            "interagit", "agit", "agit sur", "aide", "aider",
            "réduit", "reduit", "aggrave", "aggravent", "déclenche",
            "declenche", "contribue", "facteur", "facteurs",
            "mécanisme", "mecanisme", "rôle", "role",
        ]

        is_relation_query = any(term in text for term in relation_terms)
        is_complex = complexity.get("needs_decomposition", False)

        if is_relation_query:
            return {
                "route": "text_graph",
                "confidence": 0.85,
                "reason": "Question relationnelle détectée",
                "source": "heuristic",
            }

        if is_complex:
            return {
                "route": "text_only",
                "confidence": 0.70,
                "reason": "Question complexe mais non explicitement relationnelle",
                "source": "heuristic",
            }

        return {
            "route": "text_only",
            "confidence": 0.90,
            "reason": "Question simple/explicative",
            "source": "heuristic",
        }


if __name__ == "__main__":
    # Test (nécessite LLM configuré)
    print("Module pre-retrieval chargé")
    print("Nécessite configuration LLM pour tests")
