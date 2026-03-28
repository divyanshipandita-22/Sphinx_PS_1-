"""
AI-Powered Buzzword Detection using Sentence Transformers
"""

from sentence_transformers import SentenceTransformer, util
import torch

class AIBuzzwordDetector:
    def __init__(self):
        print("Loading AI models for buzzword detection...")
        # Load embedding model for semantic similarity
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Create embeddings for vague terms
        self.vague_terms = {
            'critical': [
                "eco-friendly", "green", "natural", "sustainable", 
                "environmentally friendly", "planet friendly", "earth friendly"
            ],
            'warning': [
                "biodegradable", "compostable", "recyclable", 
                "carbon neutral", "net zero", "carbon offset"
            ]
        }
        
        # Create embeddings for legitimate terms
        self.legitimate_terms = [
            "GOTS certified", "Fair Trade certified", "B Corp certified",
            "third-party verified", "lifecycle assessment", "carbon footprint measured",
            "organic certified", "FSC certified", "OEKO-TEX certified"
        ]
        
        # Pre-compute embeddings for efficiency
        print("Computing embeddings...")
        self.vague_embeddings = {}
        for category, terms in self.vague_terms.items():
            self.vague_embeddings[category] = {
                'terms': terms,
                'embeddings': self.model.encode(terms, convert_to_tensor=True)
            }
        
        self.legitimate_embeddings = self.model.encode(
            self.legitimate_terms, 
            convert_to_tensor=True
        )
        print("Buzzword detector ready!")
    
    def detect_with_similarity(self, text, threshold=0.6):
        """
        Detect vague terms using semantic similarity
        """
        # Split into sentences
        sentences = text.replace('!', '.').replace('?', '.').split('.')
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        results = {
            'vague_critical': [],
            'vague_warning': [],
            'legitimate': []
        }
        
        for sentence in sentences[:15]:  # Limit to 15 sentences for speed
            # Encode sentence
            sent_embedding = self.model.encode(sentence, convert_to_tensor=True)
            
            # Check against vague terms
            for category, data in self.vague_embeddings.items():
                similarities = util.cos_sim(sent_embedding, data['embeddings'])[0]
                max_sim = torch.max(similarities).item()
                
                if max_sim > threshold:
                    matched_term = data['terms'][torch.argmax(similarities).item()]
                    results[f'vague_{category}'].append({
                        'sentence': sentence[:200],
                        'matched_term': matched_term,
                        'similarity': max_sim
                    })
            
            # Check against legitimate terms
            legit_similarities = util.cos_sim(sent_embedding, self.legitimate_embeddings)[0]
            max_legit_sim = torch.max(legit_similarities).item()
            
            if max_legit_sim > threshold:
                matched_term = self.legitimate_terms[torch.argmax(legit_similarities).item()]
                results['legitimate'].append({
                    'sentence': sentence[:200],
                    'matched_term': matched_term,
                    'similarity': max_legit_sim
                })
        
        return results

# Test the module
if __name__ == "__main__":
    print("Testing AI Buzzword Detector...")
    detector = AIBuzzwordDetector()
    
    test_text = "Our earth-friendly sneakers are made with sustainable materials and are GOTS certified."
    results = detector.detect_with_similarity(test_text)
    
    print(f"\nVague Terms Found: {len(results['vague_critical'])}")
    print(f"Legitimate Claims Found: {len(results['legitimate'])}")