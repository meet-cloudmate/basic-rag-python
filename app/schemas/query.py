from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    top_k: int | None = Field(
        default=None,
        ge=1,
        le=20,
        description="Override default number of chunks to retrieve",
    )


class SourceChunk(BaseModel):
    content: str
    source: str | None = None
    score: float | None = None


class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceChunk]
