from pydantic import BaseModel, Field


class DocumentSource(BaseModel):
    source: str
    chunks_created: int


class DocumentIngestResponse(BaseModel):
    message: str
    total_chunks: int = Field(description="Total chunks added to the vector store")
    sources: list[DocumentSource]
