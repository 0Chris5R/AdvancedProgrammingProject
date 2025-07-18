"""
API routes for retrieving and analyzing journal entry analytics.
"""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.analytics import TsTrends, Averages
from app.services.analytics import AnalyticsService
from app.services.gemini_agent import summarize_journal_entries
from app.utils.analytics import parse_period_to_days


router = APIRouter(
    prefix="/analytics",
    tags=["analytics"]
)


@router.get("/trends/", response_model=TsTrends)
def get_trends(
    db: Session = Depends(get_db),
    period: str = Query(
        "30days",
        description="Period to analyze (e.g., '7days', '30days', '90days')."
    )
) -> TsTrends:
    """
    Retrieves time series data for sentiment, sleep, stress, and social
    engagement from journal entries over a specified period.
    """
    past_days = parse_period_to_days(period)
    analytics_service = AnalyticsService(db)
    return analytics_service.calculate_trends(past_days)


@router.get("/stats/", response_model=Averages)
def get_stats(
    db: Session = Depends(get_db),
    period: str = Query(
        "30days",
        description="Period for calculating stats (e.g., '7days', '30days')."
    )
) -> Averages:
    """
    Calculates and retrieves average values for key metrics over a
    specified period.
    """
    past_days = parse_period_to_days(period)
    analytics_service = AnalyticsService(db)
    return analytics_service.calculate_averages(past_days)


@router.get("/correlations/")
def get_correlations(
    db: Session = Depends(get_db),
    period: str = Query(
        "30days",
        description="Period for correlation analysis (e.g., '30days')."
    )
):
    """
    Calculates and retrieves correlations between state tracking fields.
    """
    past_days = parse_period_to_days(period)
    analytics_service = AnalyticsService(db)
    return analytics_service.calculate_correlations(past_days)


@router.get("/summary/")
def generate_summary(
    db: Session = Depends(get_db),
    period: str = Query(
        "30days",
        description="Period for the summary (e.g., '7days', '30days')."
    )
):
    """
    Generates a summary of journal entries for a specified period.
    """
    past_days = parse_period_to_days(period)
    to_date = datetime.now()
    from_date = to_date - timedelta(days=past_days)

    analytics_service = AnalyticsService(db)
    entry_details = analytics_service.prepare_summary_data(from_date, to_date)

    if not entry_details:
        return {"summary": "No journal entries found for the specified period."}

    summary = summarize_journal_entries("\n".join(entry_details))
    return {"summary": summary}
