from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

from app.core.config import Settings
from app.rag.vectorstore import get_retriever

RAG_PROMPT = ChatPromptTemplate.from_template(
    """You are a helpful assistant that answers questions using only the provided context.
If the context does not contain enough information, say you do not know based on the
available documents.

Context:
{context}

Question: {question}

Answer:"""
)


def format_docs(documents: list[Document]) -> str:
    return "\n\n---\n\n".join(doc.page_content for doc in documents)


def build_rag_chain(settings: Settings, *, top_k: int | None = None):
    retriever = get_retriever(settings, top_k=top_k)
    llm = ChatOpenAI(
        model=settings.openai_chat_model,
        api_key=settings.openai_api_key or None,
        temperature=0,
    )

    return (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
        }
        | RAG_PROMPT
        | llm
        | StrOutputParser()
    )
