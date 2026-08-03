from google import genai
from google.genai import types
from io import BytesIO
from app.core.config import settings
from app.domains.exercises.schemas import ExtractionResult

client = genai.Client(api_key=settings.GEMINI_API_KEY)

async def extract_exercises_from_content(
    caption: str, 
    video_bytes: BytesIO | None = None, 
    mime_type: str = "video/mp4"
) -> ExtractionResult:
    """
    Uses Gemini 2.5 Flash to extract structured exercise data from a caption and optional video stream.
    """
    
    prompt = f"""
    You are an expert fitness AI. Your job is to extract a list of exercises from the provided social media caption and video (if available).
    For each exercise, extract the title, description, category, equipment, steps, default sets/reps/weight (in kg), and target muscles.
    Ensure strict adherence to the schema.
    
    Caption context:
    {caption}
    """
    
    contents = []
    
    # If video bytes exist, we upload it using the File API for processing
    uploaded_file = None
    try:
        if video_bytes:
            # The google-genai client supports passing raw bytes as a part. 
            # Or we can upload the file. Since we need to keep it ephemeral, we pass it inline if size permits,
            # or upload via File API and then delete.
            # Using File API since Gemini can handle large videos this way.
            uploaded_file = client.files.upload(file=video_bytes, config={'mime_type': mime_type})
            contents.append(uploaded_file)
            
        contents.append(prompt)
        response = client.models.generate_content(
            model='gemini-flash-latest',
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ExtractionResult,
                temperature=0.2,
            ),
        )
        if not response.text:
            raise ValueError("Gemini returned an empty response")
        return ExtractionResult.model_validate_json(response.text)
    finally:
        # Cleanup ephemeral file from Google's servers
        if uploaded_file and uploaded_file.name:
            client.files.delete(name=uploaded_file.name)
        # Flush the buffer memory
        if video_bytes:
            video_bytes.close()
