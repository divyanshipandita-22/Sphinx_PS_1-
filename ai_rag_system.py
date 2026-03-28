"""
RAG System using Open-Source Tools
"""

import chromadb
from sentence_transformers import SentenceTransformer
import pandas as pd
import os

class SustainabilityRAG:
    def __init__(self):
        print("Loading RAG system...")
        # Initialize ChromaDB (open-source vector DB)
        self.client = chromadb.Client()
        
        # Create or get collection
        try:
            self.collection = self.client.get_collection("sustainability_knowledge")
        except:
            self.collection = self.client.create_collection("sustainability_knowledge")
        
        # Load embedding model
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Load knowledge base
        self.load_knowledge_base()
        
        # Load certified brands
        self.load_certified_brands()
        print("RAG system ready!")
    
    def load_knowledge_base(self):
        """
        Load certification and sustainability knowledge
        """
        # Certification knowledge
        certification_knowledge = [
            {
                "id": "cert_1",
                "text": "GOTS (Global Organic Textile Standard) requires 95% organic fibers, prohibits toxic chemicals like formaldehyde and heavy metals, and ensures social compliance with ILO standards.",
                "metadata": {"type": "certification", "name": "GOTS"}
            },
            {
                "id": "cert_2", 
                "text": "B Corp certification verifies high social and environmental performance, accountability, and transparency across five impact areas: governance, workers, community, environment, and customers.",
                "metadata": {"type": "certification", "name": "B Corp"}
            },
            {
                "id": "cert_3",
                "text": "Fair Trade Certified ensures fair wages, safe working conditions, environmental sustainability, and community development funds for farmers and workers.",
                "metadata": {"type": "certification", "name": "Fair Trade"}
            },
            {
                "id": "cert_4",
                "text": "Carbon Neutral Certified requires measuring carbon footprint, reducing emissions by at least 10% annually, and offsetting remaining emissions through verified projects.",
                "metadata": {"type": "certification", "name": "Carbon Neutral"}
            },
            {
                "id": "cert_5",
                "text": "FSC (Forest Stewardship Council) certification ensures wood and paper products come from responsibly managed forests that provide environmental, social, and economic benefits.",
                "metadata": {"type": "certification", "name": "FSC"}
            },
            {
                "id": "cert_6",
                "text": "OEKO-TEX Standard 100 certifies that textiles are tested for harmful substances and are safe for human use.",
                "metadata": {"type": "certification", "name": "OEKO-TEX"}
            },
            {
                "id": "redflag_1",
                "text": "Vague terms like 'eco-friendly', 'natural', 'green', and 'sustainable' without specific data or certifications are common greenwashing tactics. Legitimate claims include specific percentages and third-party verification.",
                "metadata": {"type": "red_flag", "name": "vague_terms"}
            },
            {
                "id": "redflag_2", 
                "text": "Claims about 'recycled' materials should specify the percentage of recycled content to be credible. For example, 'made with 50% recycled polyester' is verifiable while 'made with recycled materials' is vague.",
                "metadata": {"type": "red_flag", "name": "unsubstantiated_claims"}
            }
        ]
        
        # Check if collection is empty
        if self.collection.count() == 0:
            print("Loading knowledge into vector database...")
            # Add knowledge to vector DB
            for item in certification_knowledge:
                self.collection.add(
                    documents=[item["text"]],
                    metadatas=[item["metadata"]],
                    ids=[item["id"]]
                )
    
    def load_certified_brands(self):
        """Load certified brands database"""
        self.certified_brands = [
            "Patagonia", "Allbirds", "Eileen Fisher", "Seventh Generation",
            "Dr. Bronners", "Tentree", "Cotopaxi", "Pact", "United By Blue",
            "Reformation", "Veja", "Outerknown", "Prana", "Nisolo"
        ]
    
    def retrieve_knowledge(self, query, n_results=2):
        """
        Retrieve relevant sustainability knowledge based on query
        """
        if not query or len(query) < 10:
            return {"documents": [[]], "metadatas": [[]]}
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            return results
        except:
            return {"documents": [[]], "metadatas": [[]]}
    
    def check_brand(self, text):
        """Check if text mentions certified brands"""
        text_lower = text.lower()
        found_brands = []
        
        for brand in self.certified_brands:
            if brand.lower() in text_lower:
                found_brands.append(brand)
        
        return found_brands
    
    def verify_claims_with_rag(self, text):
        """
        Use RAG to verify sustainability claims
        """
        # Extract sentences that might contain claims
        sentences = text.split('.')
        claim_sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        verification_results = []
        
        for sentence in claim_sentences[:3]:  # Limit for performance
            # Retrieve relevant knowledge
            knowledge = self.retrieve_knowledge(sentence)
            
            if knowledge['documents'] and knowledge['documents'][0]:
                verification_results.append({
                    'claim': sentence[:150],
                    'relevant_knowledge': knowledge['documents'][0],
                    'metadata': knowledge['metadatas'][0] if knowledge['metadatas'] else []
                })
        
        return verification_results

# Test
if __name__ == "__main__":
    print("Testing RAG System...")
    rag = SustainabilityRAG()
    
    query = "Is GOTS certification legitimate?"
    results = rag.retrieve_knowledge(query)
    if results['documents'][0]:
        print("Retrieved knowledge:", results['documents'][0][0][:100])