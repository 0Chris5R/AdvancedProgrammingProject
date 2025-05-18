from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import json # Keep json import for handling activities/keywords on read

from ..db.database import get_db
from ..db.crud import (
    create_journal_entry,
    get_journal_entry,
    get_journal_entries,
    update_journal_entry,
    delete_journal_entry
)
# Import updated models
from ..models.entry import JournalEntryCreate, JournalEntry, JournalEntryUpdate

# Import the AI processing function
from .agent import process_entry_with_ai


router = APIRouter(
    prefix="/journal",
    tags=["journal"],
    responses={404: {"description": "Not found"}},
)

# The endpoint functions should now correctly use the updated Pydantic models
# and pass the data to the updated CRUD functions.

@router.post("/entries/", response_model=JournalEntry)
def create_entry(entry: JournalEntryCreate, db: Session = Depends(get_db)):
    """Create a new journal entry and trigger AI processing."""
    # Create the entry in the database
    db_entry = create_journal_entry(db, entry)

    # Trigger AI processing for the newly created entry
    # This call is asynchronous and doesn't block the response to the user
    # You might want to consider a background task queue for more robust handling
    # For simplicity, we'll call it directly here.
    process_entry_with_ai(db, db_entry.id)

    # Convert the SQLAlchemy model to the Pydantic model for the response
    # Ensure keywords are parsed from JSON string back to list for the response
    result = JournalEntry.from_orm(db_entry)
    # Check if keywords exist and are a string before trying to load JSON
    if db_entry.keywords and isinstance(db_entry.keywords, str):
        try:
            result.keywords = json.loads(db_entry.keywords)
        except json.JSONDecodeError:
            result.keywords = [] # Handle potential JSON decode errors
    else:
        result.keywords = [] # Ensure keywords is a list even if None or not string

    # Handle activities if they exist
    if db_entry.activities and isinstance(db_entry.activities, str):
         try:
             result.activities = json.loads(db_entry.activities)
         except json.JSONDecodeError:
             result.activities = []
    else:
         result.activities = []


    return result


@router.get("/entries/", response_model=List[JournalEntry])
def read_entries(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=100),
    db: Session = Depends(get_db)
) -> List[JournalEntry]:
    """Retrieve all journal entries with pagination."""
    db_entries = get_journal_entries(db, skip=skip, limit=limit)
    # Convert SQLAlchemy models to Pydantic models and parse JSON fields
    results = []
    for db_entry in db_entries:
        result = JournalEntry.from_orm(db_entry)
        # Check if keywords exist and are a string before trying to load JSON
        if db_entry.keywords and isinstance(db_entry.keywords, str):
            try:
                result.keywords = json.loads(db_entry.keywords)
            except json.JSONDecodeError:
                result.keywords = [] # Handle potential JSON decode errors
        else:
            result.keywords = [] # Ensure keywords is a list even if None or not string

        # Handle activities if they exist
        if db_entry.activities and isinstance(db_entry.activities, str):
             try:
                 result.activities = json.loads(db_entry.activities)
             except json.JSONDecodeError:
                 result.activities = []
        else:
             result.activities = []

        results.append(result)

    return results


@router.get("/entries/{entry_id}", response_model=JournalEntry)
def read_entry(entry_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific journal entry by ID."""
    db_entry = get_journal_entry(db, entry_id)
    if db_entry is None:
        raise HTTPException(status_code=404, detail="Journal entry not found")

    # Convert the SQLAlchemy model to the Pydantic model for the response
    # Ensure keywords are parsed from JSON string back to list for the response
    result = JournalEntry.from_orm(db_entry)
    # Check if keywords exist and are a string before trying to load JSON
    if db_entry.keywords and isinstance(db_entry.keywords, str):
        try:
            result.keywords = json.loads(db_entry.keywords)
        except json.JSONDecodeError:
            result.keywords = [] # Handle potential JSON decode errors
    else:
        result.keywords = [] # Ensure keywords is a list even if None or not string

    # Handle activities if they exist
    if db_entry.activities and isinstance(db_entry.activities, str):
         try:
             result.activities = json.loads(db_entry.activities)
         except json.JSONDecodeError:
             result.activities = []
    else:
        result.activities = []

    return result


@router.put("/entries/{entry_id}", response_model=JournalEntry)
def update_entry(
    entry_id: int,
    entry_update: JournalEntryUpdate,
    db: Session = Depends(get_db)
):
    """Update a journal entry and trigger AI processing."""
    # update_journal_entry now expects and handles all fields in JournalEntryUpdate
    db_entry = update_journal_entry(db, entry_id, entry_update)
    if db_entry is None:
        raise HTTPException(status_code=404, detail="Journal entry not found")

    # Trigger AI processing for the updated entry
    process_entry_with_ai(db, db_entry.id)

    # Convert the SQLAlchemy model to the Pydantic model for the response
    # Ensure keywords are parsed from JSON string back to list for the response
    result = JournalEntry.from_orm(db_entry)
    # Check if keywords exist and are a string before trying to load JSON
    if db_entry.keywords and isinstance(db_entry.keywords, str):
        try:
            result.keywords = json.loads(db_entry.keywords)
        except json.JSONDecodeError:
            result.keywords = [] # Handle potential JSON decode errors
    else:
        result.keywords = [] # Ensure keywords is a list even if None or not string

    # Handle activities if they exist
    if db_entry.activities and isinstance(db_entry.activities, str):
         try:
             result.activities = json.loads(db_entry.activities)
         except json.JSONDecodeError:
             result.activities = []
    else:
        result.activities = []

    return result


@router.delete("/entries/{entry_id}", response_model=bool)
def delete_entry(entry_id: int, db: Session = Depends(get_db)):
    """Delete a journal entry."""
    success = delete_journal_entry(db, entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return success
