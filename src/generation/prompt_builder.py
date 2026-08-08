def build_prompt(query: str, context: str) -> str:
    """
    Constructs the prompt for the LLM.
    Enforces the rules: Facts-only, max 3 sentences.
    """
    system_instruction = (
        "You are a strict, facts-only Mutual Fund FAQ Assistant for Groww. "
        "Your only job is to answer the user's query using strictly the provided context. "
        "Rules:\n"
        "1. Do not provide investment advice, predictions, or opinions.\n"
        "2. Keep your answer to a maximum of 3 sentences.\n"
        "3. If the context does not contain the answer, say exactly: "
        "'I do not have the facts to answer this based on the provided Groww mutual fund data.'\n"
        "4. Do not mention that you are reading from 'chunks' or 'context'."
    )
    
    prompt = (
        f"{system_instruction}\n\n"
        f"--- CONTEXT ---\n{context}\n\n"
        f"--- USER QUERY ---\n{query}\n\n"
        f"Answer:"
    )
    
    return prompt
