
from llm import generate_answer

question = input("Ask a question in English: ")

try:
    answer = generate_answer(question)
    print("\nAI answer:")
    print(answer)
except Exception as exc:
    print(f"\nTest failed: {exc}")
