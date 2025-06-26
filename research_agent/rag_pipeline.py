from typing import List, Dict
import numpy as np
import faiss
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer, CrossEncoder

from .config import AgentConfig

class RAGPipeline:
    def __init__(self, config: AgentConfig):
        self.config = config
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        print("-> Loading embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
        print("-> Loading re-ranking model...")
        self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', device='cpu')

    def run(self, research_data: List[Dict[str, str]], query: str, top_k: int) -> List[Dict[str, str]]:
        if not research_data: return []
        
        # Indexing
        print(f"--> Indexing {len(research_data)} documents...")
        all_chunks, metadata = [], []
        for item in research_data:
            chunks = self.text_splitter.split_text(item['content'])
            for chunk in chunks:
                all_chunks.append(chunk)
                metadata.append({"source": item['source'], "content": chunk})

        if not all_chunks: return []
        
        embeddings = self.embedding_model.encode(all_chunks, show_progress_bar=False)
        index = faiss.IndexFlatL2(embeddings.shape[1]); index.add(np.array(embeddings, dtype=np.float32))
        
        # Retrieval
        print("--> Retrieving relevant chunks...")
        query_embedding = self.embedding_model.encode([query])
        k_retrieve = min(len(all_chunks), self.config.CHUNKS_TO_RETRIEVE)
        if k_retrieve == 0: return []
        _, indices = index.search(np.array(query_embedding, dtype=np.float32), k=k_retrieve)
        
        # Re-ranking
        print("--> Re-ranking for quality...")
        retrieved_chunks = [all_chunks[i] for i in indices[0]]
        
        pairs = [[query, chunk] for chunk in retrieved_chunks]
        scores = self.reranker.predict(pairs, show_progress_bar=False)
        
        # Combine chunks with their original metadata and scores
        retrieved_metadata = [metadata[i] for i in indices[0]]
        ranked_results = sorted(zip(retrieved_metadata, scores), key=lambda x: x[1], reverse=True)
        
        # Return the top_k results
        return [meta for meta, score in ranked_results[:top_k]]
