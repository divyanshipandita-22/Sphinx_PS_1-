"""
Greenwashing Classification using Open-Source LLMs
"""

from transformers import pipeline
import torch

class GreenwashingClassifier:
    def __init__(self):
        print("Loading AI classifier...")
        # Use zero-shot classifier (no training needed)
        self.classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            device=-1  # -1 for CPU, 0 for GPU if available
        )
        
        self.candidate_labels = [
            "specific sustainability claim with evidence and certification",
            "vague green marketing claim without evidence",
            "no sustainability information"
        ]
        print("Classifier ready!")
    
    def classify(self, text):
        """
        Classify if text contains greenwashing
        """
        if len(text.strip()) < 20:
            return "No sustainability information", 0.9
        
        # Limit text length for performance
        text = text[:1000]
        
        result = self.classifier(text, self.candidate_labels)
        
        category = result['labels'][0]
        confidence = result['scores'][0]
        
        return category, confidence
    
    def generate_reasoning(self, text, analysis_results):
        """
        Generate simple reasoning based on analysis
        """
        vague_count = len(analysis_results.get('vague_terms', []))
        cert_count = len(analysis_results.get('certifications', []))
        
        if cert_count > 0:
            return f"This product shows legitimate sustainability credentials with {cert_count} verified certification(s). The language is specific and verifiable."
        elif vague_count > 2:
            return f"This product uses {vague_count} vague marketing terms like 'eco-friendly' and 'natural' without providing specific evidence or certifications. This is a common greenwashing pattern."
        elif vague_count > 0:
            return f"This product mentions sustainability but lacks specific certifications or data. Look for third-party verification to validate these claims."
        else:
            return f"No clear sustainability claims detected. If sustainability is important, look for products with specific certifications."

# Test
if __name__ == "__main__":
    print("Testing AI Classifier...")
    classifier = GreenwashingClassifier()
    
    test = "Our eco-friendly natural product uses sustainable practices"
    category, score = classifier.classify(test)
    print(f"Category: {category}")
    print(f"Confidence: {score:.2f}")