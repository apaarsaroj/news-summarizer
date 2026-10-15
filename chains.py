from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from prompts import summarization_prompt, faithfulness_prompt, conciseness_prompt, relevance_prompt
from config import SUMMARIZER_TEMPERATURE, JUDGE_TEMPERATURE

load_dotenv()

llm = ChatAnthropic(
    model="claude-haiku-4-5",
    temperature=SUMMARIZER_TEMPERATURE,
)

llm_judge = ChatAnthropic(
    model="claude-haiku-4-5",
    temperature=JUDGE_TEMPERATURE,
)

summarization_chain = summarization_prompt | llm | StrOutputParser()
faithfulness_chain = faithfulness_prompt | llm_judge | StrOutputParser()
conciseness_chain = conciseness_prompt | llm_judge | StrOutputParser()
relevance_chain = relevance_prompt | llm_judge | StrOutputParser()