from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from google import genai
from pydantic import BaseModel
import json
from typing import List, Optional
import os
from dotenv import load_dotenv

from ..db.database import get_db
from ..db.crud import get_journal_entry, update_journal_entry
from ..models.entry import JournalEntryUpdate

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Initialize Gemini client
client = None
if api_key:
    try:
        client = genai.Client(api_key=api_key)
        print("Gemini Client initialized.")
    except Exception as e:
        print(f"Error initializing Gemini client: {e}")
else:
    print("WARNING: GEMINI_API_KEY environment variable not set. AI processing will be skipped.")

router = APIRouter(prefix="/agent", tags=["agent"])

# Configurable list of allowed keywords
ALLOWED_KEYWORDS = [
    "productivity", "fitness", "mental health", "learning", "relationships",
    "diet", "work", "relaxation", "sleep", "stress"
]

# Pydantic model for the AI response structure
class AIResponseSchema(BaseModel):
    formatted_content: str
    keywords: List[str]

def process_entry_with_ai(db: Session, entry_id: int):
    """Fetches entry, calls AI, updates entry with results."""
    # Check if the client was successfully initialized
    if not client:
        print(f"AI processing skipped for entry {entry_id}: Gemini client not initialized.")
        return None

    db_entry = get_journal_entry(db, entry_id)
    if not db_entry:
        print(f"Error: Entry with ID {entry_id} not found for AI processing.")
        return None

    # Skip processing if content is too short (optional, adjust threshold as needed)
    if len(db_entry.content.strip()) < 10:
        print(f"Entry {entry_id} is too short for meaningful AI processing. Skipping.")
        formatted_content = "## Journal Entry\n\nThis entry is too short and lacks context to be meaningfully formatted."
        keywords = ["unprocessed"]
        
        update_payload = JournalEntryUpdate(
            formatted_content=formatted_content,
            keywords=keywords
        )
        return update_journal_entry(db, entry_id, update_payload)

    # Prompt template
    prompt = (
        "Format the following journal entry in markdown with clear headings, improved clarity, and short paragraphs. "
        f"Then, select 1-3 relevant keywords from this list: {ALLOWED_KEYWORDS}. "
        "Provide the output as a JSON object with 'formatted_content' (string) and 'keywords' (list of strings)."
        "\nJournal Entry:\n" + db_entry.content
    )

    try:
        print(f"Processing entry {entry_id} with AI...")
        
        # Call Gemini model using client.models.generate_content
        response = client.models.generate_content(
            model="gemini-1.5-flash-latest",  # Or "gemini-1.5-pro-latest"
            config={
                'response_mime_type': 'application/json',
                'response_schema': {
                    "type": "object",
                    "properties": {
                        "formatted_content": {"type": "string"},
                        "keywords": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["formatted_content", "keywords"]
                }
            },
            contents=prompt,
        )
        
        # Extract the response data - simplified approach
        formatted_content = ""
        keywords = []
        
        # Use the parsed response directly
        if hasattr(response, "parsed") and response.parsed:
            print(f"Using parsed result: {response.parsed}")
            # Handle both object and dictionary response formats
            if hasattr(response.parsed, "formatted_content") and hasattr(response.parsed, "keywords"):
                formatted_content = response.parsed.formatted_content
                keywords = response.parsed.keywords
            elif isinstance(response.parsed, dict):
                formatted_content = response.parsed.get("formatted_content", "")
                keywords = response.parsed.get("keywords", [])
        
        # Fallback to response.text if parsed is not available
        elif hasattr(response, "text") and response.text:
            try:
                ai_result = json.loads(response.text)
                formatted_content = ai_result.get("formatted_content", "")
                keywords = ai_result.get("keywords", [])
            except (json.JSONDecodeError, AttributeError) as e:
                print(f"Error parsing AI response text: {e}")
        
        # Ensure we have valid data
        if not formatted_content:
            formatted_content = "Unable to format content"
        if not keywords:
            keywords = ["unprocessed"]
            
        # Validate keywords against allowed list
        valid_keywords = [k for k in keywords if k in ALLOWED_KEYWORDS]
        if not valid_keywords and keywords != ["unprocessed"]:
            valid_keywords = ["unprocessed"]
            
        print(f"Final data - formatted_content: {formatted_content[:50]}..., keywords: {valid_keywords}")

        # Update DB with AI-generated fields
        update_payload = JournalEntryUpdate(
            formatted_content=formatted_content,
            keywords=valid_keywords
        )

        updated_entry = update_journal_entry(db, entry_id, update_payload)

        # Inside process_entry_with_ai, before returning
        print(f"Payload sent to update_journal_entry: {update_payload.model_dump()}") # agent.py
        updated_entry = update_journal_entry(db, entry_id, update_payload) # agent.py
        if updated_entry:
            print(f"Content from updated_entry: '{updated_entry.formatted_content}'") # agent.py
            print(f"Keywords from updated_entry: {updated_entry.keywords}") # agent.py
        else:
            print("update_journal_entry returned None") # agent.py

        return updated_entry

    except Exception as e:
        print(f"Error during AI processing for entry {entry_id}: {e}")
        return None

@router.post("/process/{entry_id}", response_model=AIResponseSchema)
def trigger_agent_processing(entry_id: int, db: Session = Depends(get_db)):
    """Endpoint to manually trigger AI processing for an entry."""
    if not client:
        raise HTTPException(status_code=503, detail="AI service not available: Gemini client not initialized.")

    updated_entry = process_entry_with_ai(db, entry_id)
    if updated_entry is None:
        raise HTTPException(status_code=500, detail="Failed to process entry with AI")

    # Prepare response
    formatted_content = updated_entry.formatted_content or "Content processing failed"
    
    # Ensure keywords is a list
    keywords = updated_entry.keywords or ["unprocessed"]
    if isinstance(keywords, str):
        try:
            keywords = json.loads(keywords)
            if not isinstance(keywords, list):
                keywords = [keywords]
        except json.JSONDecodeError:
            keywords = [keywords]

    return AIResponseSchema(
        formatted_content=formatted_content,
        keywords=keywords
    )