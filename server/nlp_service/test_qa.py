from model_manager import ModelManager

def main():
    print("Initializing ModelManager...")
    manager = ModelManager()
    
    print("\nTesting QA...")
    
    # Example 1: What-type question
    result = manager.get_answer(
        question="What is the capital city of India?",
        context="New Delhi is the capital city of India. It is a bustling metropolis."
    )
    print("\nExample 1:")
    print(f"Answer: {result['answer']}")
    print(f"Confidence: {result['confidence']}")
    
    # Example 2: Where-type question
    result = manager.get_answer(
        question="Where is the Taj Mahal located?",
        context="The Taj Mahal is located in Agra, India."
    )
    print("\nExample 2:")
    print(f"Answer: {result['answer']}")
    print(f"Confidence: {result['confidence']}")
    
    # Example 3: Question with no answer in context
    result = manager.get_answer(
        question="What is the population of Mumbai?",
        context="New Delhi is the capital city of India."
    )
    print("\nExample 3:")
    print(f"Answer: {result['answer']}")
    print(f"Confidence: {result['confidence']}")

if __name__ == "__main__":
    main()
