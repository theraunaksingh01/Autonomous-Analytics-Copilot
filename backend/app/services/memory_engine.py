_memory_store = []


def get_memory():
    """
    Returns last 3 Q&A pairs.
    """
    return _memory_store[-3:]


def update_memory(question: str, result):
    """
    Stores recent interaction.
    """
    _memory_store.append({
        "question": question,
        "result": str(result)
    })