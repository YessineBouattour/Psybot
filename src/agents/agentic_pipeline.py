"""
Pipeline Agentic RAG complet avec LangChain
Orchestre tous les agents pour traitement intelligent des requêtes
"""
from typing import Dict, List
from pathlib import Path

# Agents
from src.agents.pre_retrieval import (
    QueryReformulator,
    QueryComplexityAnalyzer,
    SubQueryDecomposer,
    RetrievalRouter,
)
from src.agents.post_retrieval import ChunkReRanker

# Retrieval
from src.retrieval.vector_store import FAISSVectorStore
from src.retrieval.retriever import SemanticRetriever
from src.retrieval.graph_retriever import LightweightGraphRetriever

# Generation
from src.generation.generator import RAGResponseGenerator
from src.generation.critic import ResponseCritic


class AgenticRAGPipeline:
    """
    Pipeline RAG Agentic complet
    
    Étapes:
    1. Pre-Retrieval (reformulation + analyse complexité)
    2. Retrieval (avec scoring cosine similarity)
    3. Post-Retrieval (re-ranking)
    4. Generation
    5. Self-Critique
    6. Envoi (ou régénération)
    """
    
    def __init__(
        self,
        vector_store_path: Path,
        llm_preretrival=None,
        llm_generation=None,
        llm_critique=None,
        llm=None,  # Fallback si un seul LLM
        embedder_model: str = "paraphrase-multilingual-MiniLM-L12-v2",
        top_k: int = 10,
        critique_threshold: float = 6.0,
        retrieval_score_threshold: float = 0.20,
        final_top_n: int = 7,
        generation_max_context_length: int = 3500,
        enable_pre_retrieval_llm: bool = True,
        enable_critique: bool = True,
    ):
        """
        Args:
            vector_store_path: Chemin vers vector store
            llm_preretrival: LLM pour pre-retrieval (reformulation, analyse)
            llm_generation: LLM pour génération de réponse
            llm_critique: LLM pour critique/validation
            llm: LLM unique si pas de spécialisation
            embedder_model: Modèle d'embeddings
            top_k: Nombre de chunks à récupérer
            critique_threshold: Score minimum pour accepter réponse
            retrieval_score_threshold: Seuil minimum cosine similarity au retrieval
            final_top_n: Nombre de chunks finaux injectés en génération
            generation_max_context_length: Taille max du contexte transmis au LLM
            enable_pre_retrieval_llm: Active reformulation/analyse/routage via LLM
            enable_critique: Active l'étape Self-RAG critique
        """
        print("="*60)
        print("INITIALISATION AGENTIC RAG PIPELINE")
        print("="*60)
        
        # Fallback: si un seul LLM fourni, l'utiliser partout
        if llm and not (llm_preretrival or llm_generation or llm_critique):
            print("\n⚠️  Mode mono-modèle (même LLM pour toutes les étapes)")
            llm_preretrival = llm_generation = llm_critique = llm
        elif not (llm_preretrival and llm_generation and llm_critique):
            raise ValueError("Fournissez soit 'llm' (mono), soit les 3 LLMs spécialisés")
        else:
            print("\n✨ Mode multi-modèles (LLMs spécialisés par étape)")
        
        # Charger Vector Store
        print("\n📦 Chargement Vector Store...")
        self.vector_store = FAISSVectorStore()
        self.vector_store.load(vector_store_path)
        
        # Initialiser composants
        print("\n🤖 Initialisation des agents...")
        
        # Pre-Retrieval (avec LLM spécialisé)
        self.query_reformulator = QueryReformulator(llm_preretrival)
        self.complexity_analyzer = QueryComplexityAnalyzer(llm_preretrival)
        self.sub_query_decomposer = SubQueryDecomposer(llm_preretrival)
        self.retrieval_router = RetrievalRouter(llm_preretrival)
        
        # Retrieval
        self.retriever = SemanticRetriever(self.vector_store, embedder_model)
        self.graph_retriever = LightweightGraphRetriever(self.vector_store)
        
        # Post-Retrieval
        self.reranker = ChunkReRanker()
        
        # Generation (avec LLM spécialisé)
        self.generator = RAGResponseGenerator(llm_generation)
        
        # Critique (avec LLM spécialisé)
        self.critic = ResponseCritic(llm_critique)
        
        self.top_k = top_k
        self.critique_threshold = critique_threshold
        self.retrieval_score_threshold = retrieval_score_threshold
        self.final_top_n = final_top_n
        self.generation_max_context_length = generation_max_context_length
        self.enable_pre_retrieval_llm = enable_pre_retrieval_llm
        self.enable_critique = enable_critique
        
        print("\n✅ Pipeline initialisé!")
        print("="*60)
    
    def process_query(self, query: str, max_retries: int = 2, user_query: str = None) -> Dict:
        """
        Traite une requête utilisateur de bout en bout
        
        Args:
            query: Question de l'utilisateur
            max_retries: Nombre max de régénérations
            user_query: Question brute de l'utilisateur (sans contexte injecté)
            
        Returns:
            Dict avec response, metadata, scores
        """
        print(f"\n{'='*60}")
        print(f"🚀 TRAITEMENT REQUÊTE AGENTIC RAG")
        print(f"{'='*60}")
        print(f"Query: '{query}'")

        display_query = (user_query or query or "").strip()
        
        # === ÉTAPE 1: PRE-RETRIEVAL ===
        print(f"\n{'─'*60}")
        print("ÉTAPE 1: PRE-RETRIEVAL")
        print(f"{'─'*60}")
        
        if self.enable_pre_retrieval_llm:
            # Reformulation
            reformulation_result = self.query_reformulator.reformulate(query)
            query_to_use = reformulation_result['reformulated']

            # Analyse complexité
            complexity_result = self.complexity_analyzer.analyze(query_to_use)

            # Routage retrieval basé sur la question brute pour mieux capter
            # les signaux relationnels parfois lissés par la reformulation.
            route_input = display_query or query_to_use
            route_decision = self.retrieval_router.decide(route_input, complexity_result)
            print(
                "   → Routage retrieval: "
                f"{route_decision['route']} "
                f"(confidence={route_decision['confidence']:.2f})"
            )

            # Décomposition si nécessaire
            sub_queries = []
            if complexity_result['needs_decomposition']:
                sub_queries = self.sub_query_decomposer.decompose(
                    query_to_use,
                    complexity_result['aspects']
                )
                print(f"   → Mode MULTI-AGENT activé ({len(sub_queries)} sous-requêtes)")
            else:
                print(f"   → Mode SIMPLE (pas de décomposition)")
        else:
            query_to_use = query
            complexity_result = {
                'complexity': 'SIMPLE',
                'aspects': [],
                'needs_decomposition': False,
            }
            route_decision = {
                'route': 'text_only',
                'confidence': 1.0,
                'reason': 'Mode rapide: pre-retrieval LLM désactivé',
            }
            sub_queries = []
            print("   ⚡ Mode rapide: reformulation/analyse/routage LLM désactivés")
        
        # === ÉTAPE 2: RETRIEVAL ===
        print(f"\n{'─'*60}")
        print("ÉTAPE 2: RETRIEVAL (Cosine Similarity)")
        print(f"{'─'*60}")

        use_graph = route_decision['route'] == 'text_graph'
        graph_executed = False

        if use_graph:
            print("   🧭 Mode text_graph: activation du retrieval graphe")
        
        if sub_queries:
            # Multi-agent: retrieval pour chaque sous-requête
            all_chunks = []
            for sq in sub_queries:
                if use_graph:
                    chunks = self.graph_retriever.retrieve(
                        sq['query'],
                        semantic_retriever=self.retriever,
                        top_k=max(1, self.top_k // len(sub_queries)),
                        score_threshold=self.retrieval_score_threshold,
                    )
                    graph_executed = True
                else:
                    chunks = self.retriever.retrieve(
                        sq['query'],
                        top_k=max(1, self.top_k // len(sub_queries)),
                        score_threshold=self.retrieval_score_threshold,
                    )
                all_chunks.extend(chunks)
            
            # Dédupliquer par texte
            seen_texts = set()
            unique_chunks = []
            for chunk in all_chunks:
                if chunk['text'] not in seen_texts:
                    seen_texts.add(chunk['text'])
                    unique_chunks.append(chunk)
            
            retrieved_chunks = unique_chunks[:self.top_k]
        else:
            # Simple: retrieval direct
            if use_graph:
                retrieved_chunks = self.graph_retriever.retrieve(
                    query_to_use,
                    semantic_retriever=self.retriever,
                    top_k=self.top_k,
                    score_threshold=self.retrieval_score_threshold,
                )
                graph_executed = True
            else:
                retrieved_chunks = self.retriever.retrieve(
                    query_to_use,
                    top_k=self.top_k,
                    score_threshold=self.retrieval_score_threshold,
                )
        
        print(f"   ✓ {len(retrieved_chunks)} chunks récupérés")
        
        # === ÉTAPE 3: POST-RETRIEVAL (Re-ranking) ===
        print(f"\n{'─'*60}")
        print("ÉTAPE 3: POST-RETRIEVAL (Re-ranking)")
        print(f"{'─'*60}")
        
        reranked_chunks = self.reranker.rerank(retrieved_chunks, query_to_use)
        
        # Garder top N après re-ranking
        final_chunks = reranked_chunks[:self.final_top_n]
        
        # === ÉTAPE 4: GENERATION ===
        print(f"\n{'─'*60}")
        print("ÉTAPE 4: GÉNÉRATION")
        print(f"{'─'*60}")
        
        generation_result = self.generator.generate(
            display_query,
            final_chunks,
            max_context_length=self.generation_max_context_length,
        )
        
        # === ÉTAPE 5: SELF-CRITIQUE ===
        print(f"\n{'─'*60}")
        print("ÉTAPE 5: SELF-RAG CRITIQUE")
        print(f"{'─'*60}")

        if self.enable_critique:
            critique_result = self.critic.critique(
                display_query,
                generation_result['response'],
                final_chunks
            )
        else:
            critique_result = {
                'score_global': 10.0,
                'validation': 'ACCEPTÉE',
                'scores': {},
                'problemes': [],
            }
            print("   ⚡ Mode rapide: critique désactivée")
        
        # === ÉTAPE 6: VALIDATION ===
        print(f"\n{'─'*60}")
        print("ÉTAPE 6: VALIDATION")
        print(f"{'─'*60}")
        
        if self.enable_critique and self.critic.should_regenerate(critique_result, self.critique_threshold):
            print(f"   ⚠️  Score insuffisant ({critique_result['score_global']:.1f}/{self.critique_threshold})")
            
            if max_retries > 0:
                print(f"   🔄 Régénération ({max_retries} tentatives restantes)...")
                # TODO: Améliorer le prompt avec suggestions de critique
                return self.process_query(query, max_retries - 1, user_query=display_query)
            else:
                print(f"   ⚠️  Nombre max de tentatives atteint")
        
        print(f"\n   ✅ VALIDATION: Réponse acceptée!")
        
        # === RÉSULTAT FINAL ===
        print(f"\n{'='*60}")
        print(f"✅ TRAITEMENT TERMINÉ")
        print(f"{'='*60}")

        return {
            'query': display_query,
            'response': generation_result['response'],
            'reformulated_query': query_to_use,
            'complexity': complexity_result,
            'sources': final_chunks,
            'critique': critique_result,
            'metadata': {
                'n_sources': len(final_chunks),
                'multi_agent': len(sub_queries) > 0,
                'n_sub_queries': len(sub_queries),
                'sub_queries': [sq.get('query', '') for sq in sub_queries],
                'score_global': critique_result['score_global'],
                'retrieval_route': route_decision['route'],
                'retrieval_route_confidence': route_decision['confidence'],
                'retrieval_route_reason': route_decision['reason'],
                'retrieval_route_source': route_decision.get('source', 'unknown'),
                'graph_requested': route_decision['route'] == 'text_graph',
                'graph_executed': graph_executed,
            }
        }


if __name__ == "__main__":
    print("Pipeline Agentic RAG chargé")
    print("Nécessite LLM configuré pour exécution")
