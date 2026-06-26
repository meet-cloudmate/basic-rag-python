from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.core.dependencies import get_rag_service
from app.rag.service import RAGService
from app.schemas.documents import DocumentIngestResponse

router = APIRouter()

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB per file


@router.post("/ingest", response_model=DocumentIngestResponse)
def ingest_local_documents(
    rag_service: RAGService = Depends(get_rag_service),
) -> DocumentIngestResponse:
    """Ingest all supported files from the configured documents directory."""
    return rag_service.ingest_directory()


@router.post("/upload", response_model=DocumentIngestResponse)
async def upload_documents(
    files: list[UploadFile] = File(...),
    rag_service: RAGService = Depends(get_rag_service),
) -> DocumentIngestResponse:
    """Upload and ingest one or more documents (.txt, .md, .pdf)."""
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one file is required",
        )

    filenames: list[str] = []
    contents: list[bytes] = []
    for upload in files:
        if not upload.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Each upload must include a filename",
            )
        data = await upload.read()
        if len(data) > MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File '{upload.filename}' exceeds 10 MB limit",
            )
        filenames.append(upload.filename)
        contents.append(data)

    try:
        return rag_service.ingest_uploads(filenames, contents)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
