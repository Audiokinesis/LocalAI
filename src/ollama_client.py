from __future__ import annotations
import ollama

def client_for(host: str) -> ollama.Client:
    clean_host = host.rstrip('/')
    print(f"[DIAGNOSTIC] Initializing Ollama client for host: '{clean_host}'")
    return ollama.Client(host=clean_host)


def list_models(host: str) -> list[str]:
    print(f"[DIAGNOSTIC] Requesting model list from Ollama host: '{host}'")
    response = client_for(host).list()
    
    # Handle dict response or ListResponse object safely
    models = response.get('models', []) if isinstance(response, dict) else getattr(response, 'models', [])
    print(f"[DIAGNOSTIC] Found {len(models)} total model entries in raw response.")
    
    names = []
    for item in models:
        name = None
        # Try retrieving name string as a class attribute first, then dict key
        if hasattr(item, 'name'):
            name = item.name
        elif hasattr(item, 'model'):
            name = item.model
        elif isinstance(item, dict):
            name = item.get('name') or item.get('model')
            
        if name and name not in names:
            names.append(name)
            
    sorted_names = sorted(names)
    print(f"[DIAGNOSTIC] Unique models discovered: {sorted_names}")
    return sorted_names


def check_connection(host: str) -> tuple[bool, str, list[str]]:
    print(f"[DIAGNOSTIC] Testing connection to host: '{host}'...")
    try:
        names = list_models(host)
        print(f"[DIAGNOSTIC] Connection successful. Host response verified.")
        return True, 'Connected to Ollama.', names
    except Exception as exc:
        print(f"[DIAGNOSTIC] Connection failed. Exception caught: {exc}")
        return False, f'Could not connect to Ollama at {host}: {exc}', []


def model_available(host: str, model: str) -> bool:
    wanted = model.strip()
    print(f"[DIAGNOSTIC] Checking availability for model: '{wanted}' on host: '{host}'")
    if not wanted:
        print(f"[DIAGNOSTIC] Check aborted: requested model string is empty.")
        return False
        
    try:
        models = list_models(host)
    except Exception as exc:
        print(f"[DIAGNOSTIC] Failed to fetch models during availability check: {exc}")
        return False
        
    # Standardize casing and strip version tags (e.g. ':latest') for fallback evaluation
    wanted_lower = wanted.lower()
    wanted_base = wanted_lower.split(':')[0]
    
    is_available = any(
        name.lower() == wanted_lower or name.lower().split(':')[0] == wanted_base 
        for name in models
    )
    print(f"[DIAGNOSTIC] Model availability status for '{wanted}': {is_available}")
    return is_available


def pull_model(host: str, model: str):
    model = model.strip()
    print(f"[DIAGNOSTIC] Attempting to pull model: '{model}' from host: '{host}' (stream=False)")
    if not model:
        print(f"[DIAGNOSTIC] Pull failed: model name is empty.")
        raise ValueError('Enter an Ollama model name first.')
        
    res = client_for(host).pull(model, stream=False)
    print(f"[DIAGNOSTIC] Pull command completed for model '{model}'. Raw response: {res}")
    return res


def embed_texts(host: str, model: str, texts: list[str]) -> list[list[float]]:
    num_texts = len(texts)
    print(f"[DIAGNOSTIC] Generating embeddings using model: '{model}' for {num_texts} text strings.")
    if not texts:
        print(f"[DIAGNOSTIC] Embedding aborted: texts list is empty.")
        return []
        
    response = client_for(host).embed(model=model, input=texts)
    vectors = response.get('embeddings', []) if isinstance(response, dict) else getattr(response, 'embeddings', [])
    print(f"[DIAGNOSTIC] Received {len(vectors)} vectors from Ollama.")
    
    if len(vectors) != num_texts:
        print(f"[DIAGNOSTIC] Error: Payload size mismatch! Expected {num_texts}, got {len(vectors)}")
        raise RuntimeError(f'Ollama returned {len(vectors)} embeddings for {len(texts)} texts.')
        
    if vectors:
        print(f"[DIAGNOSTIC] Sample embedding vector dimensions: {len(vectors[0])} dimensions.")
    return vectors


def chat(host: str, model: str, system_prompt: str, question: str) -> str:
    print(f"[DIAGNOSTIC] Sending chat request to model: '{model}'")
    print(f"[DIAGNOSTIC] System Prompt Length: {len(system_prompt)} chars | Question Length: {len(question)} chars")
    
    response = client_for(host).chat(
        model=model,
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': question},
        ],
        options={'temperature': 0},
    )
    
    if isinstance(response, dict):
        content = response['message']['content']
    else:
        message = getattr(response, 'message', None)
        content = getattr(message, 'content', '')
        
    print(f"[DIAGNOSTIC] Chat generation complete. Received answer length: {len(content)} chars.")
    return content
