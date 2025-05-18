from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
import json
from enum import Enum, IntEnum
from datetime import date as date_type # Import date type with an alias

class SentimentLevel(IntEnum):
    VERY_NEGATIVE = 1
    NEGATIVE = 2
    NEUTRAL = 3
    POSITIVE = 4
    VERY_POSITIVE = 5


class SleepQuality(IntEnum):
    VERY_POOR = 1
    POOR = 2
    AVERAGE = 3
    GOOD = 4
    EXCELLENT = 5


class StressLevel(IntEnum):
    VERY_LOW = 1
    LOW = 2
    MODERATE = 3
    HIGH = 4
    VERY_HIGH = 5


class SocialEngagement(IntEnum):
    ALONE = 1
    MINIMAL = 2
    MODERATE = 3
    SOCIAL = 4
    VERY_SOCIAL = 5


class JournalEntryBase(BaseModel):
    # Added title and date to the base model
    title: str = Field(..., description="The title of the journal entry")
    date: date_type = Field(..., description="The date of the journal entry") # Use the alias date_type

    content: str = Field(..., description="The main content of the journal entry")
    sentiment_level: Optional[SentimentLevel] = None
    sleep_quality: Optional[SleepQuality] = None
    stress_level: Optional[StressLevel] = None
    social_engagement: Optional[SocialEngagement] = None


class JournalEntryCreate(JournalEntryBase):
    # JournalEntryCreate inherits title and date from JournalEntryBase
    pass


class JournalEntryUpdate(BaseModel):
    # Allow optional update for all base fields including title and date
    title: Optional[str] = None
    date: Optional[date_type] = None # Use the alias date_type and make it Optional

    content: Optional[str] = None
    sentiment_level: Optional[SentimentLevel] = None
    sleep_quality: Optional[SleepQuality] = None
    stress_level: Optional[StressLevel] = None
    social_engagement: Optional[SocialEngagement] = None
    formatted_content: Optional[str] = None
    keywords: Optional[List[str]] = None # Keywords will be a list of strings


class JournalEntry(JournalEntryBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    formatted_content: Optional[str] = None
    activities: Optional[List[str]] = None # Define as List[str]
    sentiment_analysis: Optional[str] = None
    keywords: Optional[List[str]] = None # Define as List[str]

    class Config:
        from_attributes = True # Pydantic V2 uses from_attributes

    # Add this validator for 'keywords' and 'activities'
    @field_validator('keywords', 'activities', mode='before')
    @classmethod
    def parse_json_fields(cls, value):
        if isinstance(value, str): # If the value from DB is a string
            try:
                return json.loads(value) # Try to parse it as JSON
            except json.JSONDecodeError:
                # Decide how to handle malformed JSON:
                # Option 1: Return empty list
                return []
                # Option 2: Return None (if field is Optional)
                # return None
                # Option 3: Raise a custom validation error or let Pydantic handle it
                # raise ValueError("Invalid JSON string")
        # If the value is already a list (e.g. not from DB or pre-processed) or None, return as is
        return value
