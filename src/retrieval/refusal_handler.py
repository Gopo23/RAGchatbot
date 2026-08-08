import re
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Keywords/phrases indicating advisory, comparative, or predictive intents
BANNED_PHRASES = [
    r"should i (invest|buy|sell)",
    r"which (is|fund is) (better|best)",
    r"is it a good time to",
    r"predict",
    r"forecast",
    r"advice",
    r"recommend",
    r"compare",
    r"vs",
    r"versus",
    r"will the market",
    r"future (performance|returns)",
    r"am i (making a mistake|doing the right thing)"
]

BANNED_PATTERN = re.compile("|".join(BANNED_PHRASES), re.IGNORECASE)

def is_advisory_query(query: str) -> bool:
    """
    Checks if a query contains advisory, comparative, or predictive intents.
    Returns True if the query should be blocked, False otherwise.
    """
    if BANNED_PATTERN.search(query):
        logging.info(f"Refusal triggered for query: {query}")
        return True
    return False

def get_refusal_message() -> str:
    """Returns the standard refusal message."""
    return (
        "I am a Facts-Only FAQ Assistant. I can provide facts and figures "
        "from the official Groww mutual fund pages, but I cannot offer investment "
        "advice, comparisons, or performance predictions. Please consult a "
        "registered financial advisor for personalized guidance."
    )
