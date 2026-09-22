import os
import shutil
from fastapi import APIRouter, File, UploadFile, HTTPException, status
from fastapi.responses import FileResponse
from config.settings import settings
from main import run_pipeline
from utils.exporter import ReportExporter
from utils.logger import logger
from api.schemas import PipelineResponseSchema, HealthCheckSchema

router = APIRouter()


@router.get("/health", response_model=HealthCheckSchema, tags=["Health"])
async def health_check():
    """Returns application status and key configuration checks."""
    return HealthCheckSchema(
        status="healthy",
        device=settings.DEVICE,
        groq_api_configured=bool(settings.GROQ_API_KEY),
        deepgram_api_configured=bool(settings.DEEPGRAM_API_KEY)
    )


@router.post("/process", response_model=PipelineResponseSchema, tags=["Pipeline"])
async def process_media(file: UploadFile = File(...)):
    """
    Accepts an audio/video upload, runs the Voice MoM pipeline, 
    and returns structured transcript and summary data.
    """
    logger.info(f"API Request received: Upload file '{file.filename}'")

    file_path = settings.UPLOAD_DIR / file.filename
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = run_pipeline(str(file_path))
        return result

    except Exception as e:
        logger.error(f"API processing error on '{file.filename}': {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pipeline processing failed: {str(e)}"
        )
    finally:
        file.file.close()


@router.get("/export/pdf/{filename}", tags=["Export"])
async def export_pdf(filename: str):
    """Generates and serves a PDF document for a previously processed recording."""
    json_path = settings.OUTPUT_DIR / f"{filename}_mom.json"
    pdf_path = settings.OUTPUT_DIR / f"{filename}_mom.pdf"

    if not json_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No processed data found for '{filename}'. Process the file first."
        )

    try:
        import json
        with open(json_path, "r", encoding="utf-8") as f:
            mom_data = json.load(f)

        ReportExporter.to_pdf(mom_data, str(pdf_path))
        return FileResponse(
            path=str(pdf_path),
            filename=f"{filename}_MoM.pdf",
            media_type="application/pdf"
        )
    except Exception as e:
        logger.error(f"Failed to generate PDF for '{filename}': {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF export failed: {str(e)}"
        )


@router.get("/export/docx/{filename}", tags=["Export"])
async def export_docx(filename: str):
    """Generates and serves a Word (.docx) document for a previously processed recording."""
    json_path = settings.OUTPUT_DIR / f"{filename}_mom.json"
    docx_path = settings.OUTPUT_DIR / f"{filename}_mom.docx"

    if not json_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No processed data found for '{filename}'. Process the file first."
        )

    try:
        import json
        with open(json_path, "r", encoding="utf-8") as f:
            mom_data = json.load(f)

        ReportExporter.to_docx(mom_data, str(docx_path))
        return FileResponse(
            path=str(docx_path),
            filename=f"{filename}_MoM.docx",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except Exception as e:
        logger.error(f"Failed to generate DOCX for '{filename}': {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"DOCX export failed: {str(e)}"
        )