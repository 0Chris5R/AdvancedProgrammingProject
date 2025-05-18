from sqlalchemy.orm import Session
from datetime import datetime
import json
from typing import List, Optional
from datetime import date # Import date type

# Import Journal models and model
from ..models.entry import JournalEntryCreate, JournalEntryUpdate
from .database import JournalEntryModel

# Import new Goal models and model, including the GoalPriority Enum
from ..models.goal import GoalCreate, GoalUpdate, GoalPriority
from .database import GoalModel

from sqlalchemy import case # Import case for custom ordering


# --- Journal Entry CRUD (Existing functions) ---

def create_journal_entry(db: Session, entry: JournalEntryCreate) -> JournalEntryModel:
    """Create a new journal entry"""
    # Include title and date when creating the model instance
    db_entry = JournalEntryModel(
        title=entry.title,
        date=entry.date, # Pass the date object
        content=entry.content,
        # Explicitly use .value for IntEnum fields
        sentiment_level=entry.sentiment_level.value if entry.sentiment_level is not None else None,
        sleep_quality=entry.sleep_quality.value if entry.sleep_quality is not None else None,
        stress_level=entry.stress_level.value if entry.stress_level is not None else None,
        social_engagement=entry.social_engagement.value if entry.social_engagement is not None else None
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


def get_journal_entry(db: Session, entry_id: int) -> Optional[JournalEntryModel]:
    """Get a specific journal entry by ID"""
    return db.query(JournalEntryModel).filter(JournalEntryModel.id == entry_id).first()


def get_journal_entries(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[JournalEntryModel]:
    """Get all journal entries with pagination"""
    # Order by date (newest first) and then by created_at for tie-breaking
    return db.query(JournalEntryModel).order_by(
        JournalEntryModel.date.desc(),
        JournalEntryModel.created_at.desc()
    ).offset(skip).limit(limit).all()


def update_journal_entry(
    db: Session,
    entry_id: int,
    entry_update: JournalEntryUpdate
) -> Optional[JournalEntryModel]:
    """Update a journal entry"""
    db_entry = get_journal_entry(db, entry_id)
    if db_entry:
        update_data = entry_update.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            if value is None and key not in ['formatted_content', 'keywords', 'activities', 'sentiment_analysis']: # Allow setting AI fields to None explicitly if desired
                # Or simply 'if value is None:' if you always want to skip setting None for all fields during partial updates
                # unless explicitly passed as None in the payload (exclude_unset handles this generally).
                # This check is mostly if you want to avoid overwriting existing values with None for specific fields.
                # For formatted_content and keywords, we want to allow them to be set from update_data.
                pass

            if key in ['sentiment_level', 'sleep_quality', 'stress_level', 'social_engagement'] and value is not None:
                setattr(db_entry, key, value.value)
            elif key == 'keywords' and value is not None: # Handle keywords list
                setattr(db_entry, key, json.dumps(value))
            # Add similar handling if 'activities' were to be updated via this mechanism
            # elif key == 'activities' and value is not None:
            #     setattr(db_entry, key, json.dumps(value))
            else:
                setattr(db_entry, key, value) # This will handle formatted_content (string) correctly

        db_entry.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_entry)
    return db_entry


def delete_journal_entry(db: Session, entry_id: int) -> bool:
    """Delete a journal entry"""
    db_entry = get_journal_entry(db, entry_id)
    if db_entry:
        db.delete(db_entry)
        db.commit()
        return True
    return False



# --- Goal CRUD (New functions, updated for priority and optional date) ---

def create_goal(db: Session, goal: GoalCreate) -> GoalModel:
    """Create a new goal"""
    db_goal = GoalModel(
        title=goal.title,
        type=goal.type,
        # Pass targetDate, which can now be None
        targetDate=goal.targetDate,
        category=goal.category,
        # Store the string value of the Enum
        priority=goal.priority.value,
        description=goal.description,
        progress=0 # New goals start with 0 progress
    )
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal


def get_goal(db: Session, goal_id: int) -> Optional[GoalModel]:
    """Get a specific goal by ID"""
    return db.query(GoalModel).filter(GoalModel.id == goal_id).first()


def get_goals(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[GoalModel]:
    """Get all goals with pagination, ordered by priority (High -> Medium -> Low)"""
    # Order by priority: 'High' first, then 'Medium', then 'Low'
    # Use a case statement for custom ordering - Pass whens as positional arguments
    return db.query(GoalModel).order_by(
        case(
            (GoalModel.priority == GoalPriority.HIGH.value, 1),
            (GoalModel.priority == GoalPriority.MEDIUM.value, 2),
            (GoalModel.priority == GoalPriority.LOW.value, 3),
            else_=4 # Handle any unexpected values
        )
    ).offset(skip).limit(limit).all()


def update_goal(
    db: Session,
    goal_id: int,
    goal_update: GoalUpdate
) -> Optional[GoalModel]:
    """Update a goal"""
    db_goal = get_goal(db, goal_id)
    if db_goal:
        # Use model_dump(exclude_unset=True) for Pydantic V2+
        update_data = goal_update.model_dump(exclude_unset=True)

        # Update the goal with the new data
        for key, value in update_data.items():
             # If the key is 'priority' and the value is not None, store the string value
            if key == 'priority' and value is not None:
                setattr(db_goal, key, value.value)
            else:
                setattr(db_goal, key, value)

        # Handle the case where targetDate might be None in the update
            if key == 'targetDate':
                 setattr(db_goal, key, value)


        # Update the updated_at timestamp
        db_goal.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(db_goal)
    return db_goal


def delete_goal(db: Session, goal_id: int) -> bool:
    """Delete a goal"""
    db_goal = get_goal(db, goal_id)
    if db_goal:
        db.delete(db_goal)
        db.commit()
        return True
    return False

