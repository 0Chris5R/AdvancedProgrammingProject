from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from collections import Counter
from typing import List

from app.db.database import get_db
from app.db.crud.journal import get_journal_entries
from app.models.analytics import TsTrends, Averages
from app.services.gemini_agent import generate_insights

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"]
)


def get_basic_stats(db: Session):
    entries = get_journal_entries(db, limit=10000)
    if not entries:
        return {
            "total_entries": 0,
            "current_streak": 0,
            "longest_streak": 0,
            "average_words": 0,
            "total_words": 0,
        }

    dates = sorted(list(set(entry.date for entry in entries)))
    current_streak = 0
    longest_streak = 0
    if dates:
        longest_streak = 1
        current_streak = 1
        for i in range(1, len(dates)):
            if (dates[i] - dates[i-1]).days == 1:
                current_streak += 1
            else:
                longest_streak = max(longest_streak, current_streak)
                current_streak = 1
        longest_streak = max(longest_streak, current_streak)

        if (datetime.now().date() - dates[-1]).days > 1:
            current_streak = 0

    total_words = sum(len(entry.content.split()) for entry in entries)
    average_words = total_words / len(entries) if entries else 0

    return {
        "totalEntries": len(entries),
        "currentStreak": current_streak,
        "longestStreak": longest_streak,
        "averageWords": round(average_words),
        "totalWords": total_words,
    }


@router.get("/")
def get_analytics_data(db: Session = Depends(get_db), period: str = "7days"):
    period_map = {
        "7days": 7,
        "30days": 30,
        "90days": 90,
        "1year": 365,
    }
    period_days = period_map.get(period, 7)
    from_date = datetime.now() - timedelta(days=period_days)
    entries = get_journal_entries(db, from_date=from_date, limit=10000)

    # Basic Stats
    stats = get_basic_stats(db)

    # Weekly Data
    activity = {}
    if period_days == 7:
        # Day of the week for the last 7 days
        date_format = "%a"
        days_in_period = [(datetime.now() - timedelta(days=i)).strftime(date_format)
                          for i in range(period_days - 1, -1, -1)]
    else:
        # Day of the month for longer periods
        date_format = "%Y-%m-%d"
        days_in_period = [(datetime.now() - timedelta(days=i)).strftime(date_format)
                          for i in range(period_days - 1, -1, -1)]

    for entry in entries:
        day_str = entry.date.strftime(date_format)
        if day_str not in activity:
            activity[day_str] = {"day": day_str, "entries": 0, "words": 0, "mood": [
            ], "sleep": [], "stress": [], "social": []}

        activity[day_str]["entries"] += 1
        activity[day_str]["words"] += len(entry.content.split())
        if entry.sentiment_level:
            activity[day_str]["mood"].append(entry.sentiment_level)
        if entry.sleep_quality:
            activity[day_str]["sleep"].append(entry.sleep_quality)
        if entry.stress_level:
            activity[day_str]["stress"].append(entry.stress_level)
        if entry.social_engagement:
            activity[day_str]["social"].append(entry.social_engagement)

    for day, data in activity.items():
        data["mood"] = round(sum(data["mood"]) /
                             len(data["mood"]), 1) if data["mood"] else 0
        data["sleep"] = round(sum(data["sleep"]) /
                              len(data["sleep"]), 1) if data["sleep"] else 0
        data["stress"] = round(sum(data["stress"]) /
                               len(data["stress"]), 1) if data["stress"] else 0
        data["social"] = round(sum(data["social"]) /
                               len(data["social"]), 1) if data["social"] else 0

    weekly_data = [activity.get(day, {"day": day, "entries": 0, "words": 0,
                                "mood": 0, "sleep": 0, "stress": 0, "social": 0}) for day in days_in_period]

    # Mood Distribution
    mood_levels = [
        entry.sentiment_level for entry in entries if entry.sentiment_level is not None]
    mood_distribution_counts = Counter(mood_levels)
    total_moods = sum(mood_distribution_counts.values())
    mood_distribution = [
        {"name": f"Level {k}", "value": round(
            (v / total_moods) * 100), "color": "#22c55e"}
        for k, v in mood_distribution_counts.items()
    ]

    # Sleep Quality Distribution
    sleep_levels = [
        entry.sleep_quality for entry in entries if entry.sleep_quality is not None]
    sleep_distribution_counts = Counter(sleep_levels)
    total_sleep = sum(sleep_distribution_counts.values())
    sleep_quality_data = [
        {"quality": f"Level {k}", "value": round(
            (v / total_sleep) * 100), "color": "#10b981"}
        for k, v in sleep_distribution_counts.items()
    ]

    # Stress Level Distribution
    stress_levels = [
        entry.stress_level for entry in entries if entry.stress_level is not None]
    stress_distribution_counts = Counter(stress_levels)
    total_stress = sum(stress_distribution_counts.values())
    stress_level_data = [
        {"level": f"Level {k}", "value": round(
            (v / total_stress) * 100), "color": "#f97316"}
        for k, v in stress_distribution_counts.items()
    ]

    # Correlation Data
    correlation_data = [
        {
            "sleep": entry.sleep_quality,
            "happiness": entry.sentiment_level,
            "stress": entry.stress_level,
        }
        for entry in entries
        if entry.sleep_quality is not None and entry.sentiment_level is not None
    ]

    # Topic Data
    all_topics = []
    for entry in entries:
        content_lower = entry.content.lower()
        if "work" in content_lower:
            all_topics.append("Work")
        if "family" in content_lower or "friends" in content_lower:
            all_topics.append("Relationships")
        if "health" in content_lower or "exercise" in content_lower:
            all_topics.append("Health")
        if "travel" in content_lower or "vacation" in content_lower:
            all_topics.append("Travel")
        if "hobby" in content_lower or "passion" in content_lower:
            all_topics.append("Hobbies")
    topic_counts = Counter(all_topics)
    topic_data = [{"topic": topic, "count": count, "color": "#3b82f6"}
                  for topic, count in topic_counts.most_common(5)]

    # Averages
    social_levels = [
        entry.social_engagement for entry in entries if entry.social_engagement is not None]
    stats["averageMood"] = round(
        sum(mood_levels) / len(mood_levels), 1) if mood_levels else 0
    stats["averageSleep"] = round(
        sum(sleep_levels) / len(sleep_levels), 1) if sleep_levels else 0
    stats["averageStress"] = round(
        sum(stress_levels) / len(stress_levels), 1) if stress_levels else 0
    stats["averageSocial"] = round(
        sum(social_levels) / len(social_levels), 1) if social_levels else 0
    stats["weeklyGrowth"] = 0
    stats["sleepTrend"] = 0
    stats["stressTrend"] = 0
    stats["socialTrend"] = 0

    # AI Insights
    insights = generate_insights(stats, weekly_data, correlation_data)

    return {
        "stats": stats,
        "weeklyData": weekly_data,
        "moodDistribution": mood_distribution,
        "sleepQualityData": sleep_quality_data,
        "stressLevelData": stress_level_data,
        "correlationData": correlation_data,
        "topicData": topic_data,
        "insights": insights,
    }
