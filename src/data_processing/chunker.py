"""
Module de Chunking pour documents PDF
Stratégies: Recursive, Semantic, Sentence-based
"""
import re
from typing import List, Dict
from pathlib import Path
import json


class TextChunker:
    """Classe pour découper les documents en chunks optimisés"""
    
    def __init__(
        self, 
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        strategy: str = "recursive"
    ):
        """
        Args:
            chunk_size: Taille maximum d'un chunk (en caractères)
            chunk_overlap: Chevauchement entre chunks pour contexte
            strategy: 'recursive', 'semantic', 'sentence'
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.strategy = strategy
        
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Découpe un texte en chunks avec métadonnées
        
        Args:
            text: Texte à découper
            metadata: Métadonnées du document source
            
        Returns:
            Liste de dictionnaires {text, metadata, chunk_id}
        """
        if self.strategy == "recursive":
            return self._recursive_chunking(text, metadata)
        elif self.strategy == "semantic":
            return self._semantic_chunking(text, metadata)
        elif self.strategy == "sentence":
            return self._sentence_chunking(text, metadata)
        else:
            raise ValueError(f"Stratégie inconnue: {self.strategy}")
    
    def _recursive_chunking(self, text: str, metadata: Dict) -> List[Dict]:
        """
        Chunking récursif par séparateurs hiérarchiques
        Idéal pour documents structurés (paragraphes, phrases)
        """
        # Séparateurs par ordre de priorité
        separators = ["\n\n", "\n", ". ", " ", ""]
        
        chunks = []
        current_separator_idx = 0
        
        def split_text(text: str, separator_idx: int) -> List[str]:
            if separator_idx >= len(separators):
                return [text]
            
            separator = separators[separator_idx]
            splits = text.split(separator) if separator else list(text)
            
            result = []
            current_chunk = ""
            
            for split in splits:
                if len(current_chunk) + len(split) <= self.chunk_size:
                    current_chunk += split + separator
                else:
                    if current_chunk:
                        result.append(current_chunk.strip())
                    
                    # Si le split est trop grand, on descend d'un niveau
                    if len(split) > self.chunk_size:
                        result.extend(split_text(split, separator_idx + 1))
                        current_chunk = ""
                    else:
                        current_chunk = split + separator
            
            if current_chunk:
                result.append(current_chunk.strip())
                
            return result
        
        text_chunks = split_text(text, 0)
        
        # Ajout de l'overlap et des métadonnées
        for i, chunk_text in enumerate(text_chunks):
            # Ajouter overlap avec chunk précédent
            if i > 0 and self.chunk_overlap > 0:
                overlap_text = text_chunks[i-1][-self.chunk_overlap:]
                chunk_text = overlap_text + " " + chunk_text
            
            chunk_metadata = metadata.copy() if metadata else {}
            chunk_metadata["chunk_id"] = i
            chunk_metadata["total_chunks"] = len(text_chunks)
            
            chunks.append({
                "text": chunk_text,
                "metadata": chunk_metadata
            })
        
        return chunks
    
    def _sentence_chunking(self, text: str, metadata: Dict) -> List[Dict]:
        """
        Chunking basé sur les phrases complètes
        Préserve l'intégrité sémantique
        """
        # Découpage en phrases (simple, peut être amélioré avec spaCy)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = ""
        chunk_count = 0
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= self.chunk_size:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunk_metadata = metadata.copy() if metadata else {}
                    chunk_metadata["chunk_id"] = chunk_count
                    
                    chunks.append({
                        "text": current_chunk.strip(),
                        "metadata": chunk_metadata
                    })
                    chunk_count += 1
                
                current_chunk = sentence + " "
        
        # Dernier chunk
        if current_chunk:
            chunk_metadata = metadata.copy() if metadata else {}
            chunk_metadata["chunk_id"] = chunk_count
            
            chunks.append({
                "text": current_chunk.strip(),
                "metadata": chunk_metadata
            })
        
        # Ajouter total_chunks à tous
        for chunk in chunks:
            chunk["metadata"]["total_chunks"] = len(chunks)
        
        return chunks
    
    def _semantic_chunking(self, text: str, metadata: Dict) -> List[Dict]:
        """
        Chunking sémantique basé sur la cohérence thématique
        TODO: Implémenter avec embeddings pour détecter les ruptures sémantiques
        """
        # Pour l'instant, fallback sur sentence chunking
        # À améliorer avec analyse de similarité entre phrases
        return self._sentence_chunking(text, metadata)
    
    def process_paragraphs_json(self, json_path: Path) -> List[Dict]:
        """
        Traite le fichier paragraphs.json existant
        
        Args:
            json_path: Chemin vers paragraphs.json
            
        Returns:
            Liste de chunks avec métadonnées
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            paragraphs = json.load(f)
        
        all_chunks = []
        
        for para in paragraphs:
            content = para.get('content', '')
            metadata = {
                'source': para.get('source', 'unknown'),
                'type': 'scientific_paper'
            }
            
            chunks = self.chunk_text(content, metadata)
            all_chunks.extend(chunks)
        
        return all_chunks


if __name__ == "__main__":
    # Test du chunker
    chunker = TextChunker(chunk_size=300, chunk_overlap=50, strategy="recursive")
    
    test_text = """
    L'anxiété est une réponse émotionnelle normale face au stress. 
    Cependant, lorsqu'elle devient excessive, elle peut interférer avec la vie quotidienne.
    
    Les symptômes de l'anxiété incluent: nervosité, inquiétude constante, difficulté de concentration.
    La thérapie cognitivo-comportementale (TCC) est efficace pour traiter l'anxiété.
    
    Des techniques de relaxation comme la respiration profonde peuvent aider.
    """
    
    chunks = chunker.chunk_text(test_text, {"source": "test.pdf"})
    
    print(f"✓ {len(chunks)} chunks créés")
    for i, chunk in enumerate(chunks):
        print(f"\n--- Chunk {i} ---")
        print(chunk['text'][:100] + "...")
