from sentence_transformers import SentenceTransformer

class EmbeddingsManager:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
    
    def __call__(self, input):
        # ChromaDB expects a __call__ method that takes 'input' parameter
        if isinstance(input, str):
            input = [input]
        return self.model.encode(input, convert_to_tensor=True).tolist()
    
    def get_embeddings(self, texts):
        # Keeping the original method for backward compatibility
        return self.__call__(texts)
