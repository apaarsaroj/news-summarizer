from langchain_core.prompts import ChatPromptTemplate
from pathlib import Path

def load_prompt(filename):
    path = Path(__file__).parent / "prompts" / filename
    return path.read_text()

summarization_prompt = ChatPromptTemplate.from_template(load_prompt("summarization.txt"))
similaritychecker_prompt = ChatPromptTemplate.from_template(load_prompt("similaritychecker.txt"))
hallucinationchecker_prompt = ChatPromptTemplate.from_template(load_prompt("hallucinationchecker.txt"))
relevance_prompt = ChatPromptTemplate.from_template(load_prompt("relevance.txt"))