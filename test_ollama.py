import ollama
try:
    models = ollama.list()
    print([m['model'] for m in models.get('models', [])])
except Exception as e:
    print(f"Error: {e}")
