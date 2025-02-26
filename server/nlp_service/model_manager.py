from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
import torch

class ModelManager:
    def __init__(self):
        self.available_models = {
            'text_generation': {
                'default': 'google/flan-t5-base',
                'alternatives': [
                    'google/flan-t5-large',
                    'google/flan-t5-xl'
                ]
            },
            'qa': {
                'default': 'distilbert-base-cased-distilled-squad',
                'alternatives': [
                    'deepset/roberta-base-squad2',
                    'bert-large-uncased-whole-word-masking-finetuned-squad'
                ]
            },
            'summarization': {
                'default': 'facebook/bart-large-cnn',
                'alternatives': [
                    'google/pegasus-xsum',
                    't5-base'
                ]
            }
        }
        
        # Force CPU usage initially
        self.device = -1
        self.generation_pipeline = None
        self.qa_pipeline = None
        self.qa_model = None
        self.qa_tokenizer = None
        self.initialize_generation_model()
        self.initialize_qa_model()
    
    def initialize_generation_model(self, model_name=None):
        """Initialize the text generation model pipeline"""
        try:
            if model_name is None:
                model_name = self.available_models['text_generation']['default']
            
            print(f"Initializing text generation model: {model_name}")
            
            self.generation_pipeline = pipeline(
                task="text2text-generation",
                model=model_name,
                device=self.device
            )
            
            # Verify pipeline works with test input
            test_result = self.generation_pipeline(
                "Answer this question: What is the capital of India? Context: New Delhi is the capital of India.",
                max_length=100,
                do_sample=False
            )
            print("Pipeline test result:", test_result)
            
        except Exception as e:
            print(f"Error initializing generation model: {str(e)}")
            raise
    
    def initialize_qa_model(self, model_name=None):
        """Initialize the QA model pipeline"""
        try:
            if model_name is None:
                model_name = self.available_models['qa']['default']
            
            print(f"Initializing QA model: {model_name}")
            
            # Create pipeline directly without separate model/tokenizer
            self.qa_pipeline = pipeline(
                task="question-answering",
                model=model_name,
                device=self.device
            )
            
            # Verify pipeline works with test input
            test_result = self.qa_pipeline(
                question="What is the capital of India?",
                context="New Delhi is the capital of India.",
            )
            print("Pipeline test result:", test_result)
            
        except Exception as e:
            print(f"Error initializing QA model: {str(e)}")
            raise
    
    def get_answer(self, question, context, **kwargs):
        """Get answer using the text generation pipeline"""
        try:
            if not self.generation_pipeline:
                self.initialize_generation_model()
            
            print("\nProcessing Query:")
            print(f"Question: {question}")
            print(f"Context: {context}")
            
            # Combine question and context into a structured prompt
            prompt = f''' Please have a look at the following question and the context provided.
            Answer the question based on the context provided. Try to form a good response. 
            If you are not sure about the answer, based on the context provided, please say so.

            Question: {question}
            
            Context: {context}
            
            Answer:
            '''
            
            print(f"Prompt: {prompt}")
            # Generate the answer
            result = self.generation_pipeline(
                prompt,
                max_length=150,
                do_sample=False,  # Deterministic generation
                temperature=0.3,  # Lower temperature for more focused answers
                num_return_sequences=1
            )
            
            if not result or not isinstance(result, list):
                raise ValueError("Invalid model output")
            
            answer = result[0]['generated_text'].strip()
            
            print(f"Generated answer: {answer}")
            # Estimate confidence based on answer length and presence of uncertainty markers
            uncertainty_phrases = ['i am not sure', 'i cannot', 'unable to', 'don\'t know']
            confidence = 0.8  # Base confidence
            if any(phrase in answer.lower() for phrase in uncertainty_phrases):
                confidence = 0.2
            elif len(answer) < 10:
                confidence = 0.4
            
            return {
                'answer': answer,
                'confidence': confidence,
                'start': 0,  # These are not applicable for generation models
                'end': 0     # but kept for API compatibility
            }
            
        except Exception as e:
            print(f"Error in get_answer: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'answer': "I apologize, but I encountered an error while processing your question. Please try again.",
                'confidence': 0.0,
                'start': 0,
                'end': 0
            }
    
    def format_response(self, qa_result, confidence_threshold=0.01):
        """Format the response based on confidence score"""
        if qa_result['confidence'] < confidence_threshold:
            return {
                'answer': "I couldn't find a reliable answer to this question in the provided context.",
                'confidence': qa_result['confidence']
            }
        
        # Clean and format the answer
        answer = qa_result['answer'].strip()
        
        # Ensure the answer is a complete sentence
        if not answer.endswith(('.', '?', '!')):
            answer += '.'
        
        return {
            'answer': answer,
            'confidence': qa_result['confidence']
        }
    
    def switch_to_better_qa_model(self):
        """Switch to a more capable generation model"""
        try:
            # Use a more powerful model for better performance
            better_model = "google/flan-t5-large"
            print(f"Switching to better model: {better_model}")
            self.initialize_generation_model(better_model)
            return True
        except Exception as e:
            print(f"Failed to switch to better model: {str(e)}")
            return False

# Example usage
if __name__ == "__main__":

    manager = ModelManager()
    
    # Test with hardcoded example
    result = manager.get_answer(None, None, use_hardcoded=True)
    formatted = manager.format_response(result)
    print("\nTest result with hardcoded values:")
    print(f"Answer: {formatted['answer']}")
    print(f"Confidence: {formatted['confidence']:.4f}")
    
    # Test with custom input
    custom_context = """
    Python is a programming language created by Guido van Rossum and released in 1991. 
    It is known for its readability and simplicity. Python 3.0 was released in 2008 
    and introduced many changes that were not backward compatible with Python 2.
    """
    custom_question = "Who created Python?"
    
    result = manager.get_answer(custom_question, custom_context)
    formatted = manager.format_response(result)
    print("\nTest result with custom input:")
    print(f"Answer: {formatted['answer']}")
    print(f"Confidence: {formatted['confidence']:.4f}")
    
    # Try with better model
    manager.switch_to_better_qa_model()
    result = manager.get_answer(custom_question, custom_context)
    formatted = manager.format_response(result)
    print("\nTest result with better model:")
    print(f"Answer: {formatted['answer']}")
    print(f"Confidence: {formatted['confidence']:.4f}")