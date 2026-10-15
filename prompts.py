from langchain_core.prompts import ChatPromptTemplate
from pathlib import Path

def load_prompt(filename):
    path = Path(__file__).parent / "prompts" / filename
    return path.read_text()

summarization_prompt = ChatPromptTemplate.from_template(load_prompt("summarization.txt"))
faithfulness_prompt = ChatPromptTemplate.from_template(load_prompt("faithfulness.txt"))
conciseness_prompt = ChatPromptTemplate.from_template(load_prompt("conciseness.txt"))
relevance_prompt = ChatPromptTemplate.from_template(load_prompt("relevance.txt"))