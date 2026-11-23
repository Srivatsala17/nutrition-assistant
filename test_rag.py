from core.rag import answer_question

result = answer_question("Suggest a high protein vegetarian dinner", diet="veg")

print(result["answer"])
print("\nSOURCES:")
for i, s in enumerate(result["sources"], start=1):
    print(f"[{i}] {s['name']} - {s['source']}")