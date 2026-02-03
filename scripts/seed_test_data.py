#!/usr/bin/env python3
"""
Test Data Generation Script for Sentimatrix Studio

This script generates mock data for development and testing purposes.
It creates users, projects, targets, results, and jobs with realistic data.

Usage:
    python scripts/seed_test_data.py [--users N] [--projects N] [--results N]

Requirements:
    pip install motor faker

Environment Variables:
    MONGODB_URL: MongoDB connection string (default: mongodb://localhost:27017)
    DATABASE_NAME: Database name (default: sentimatrix_studio)
"""

import argparse
import asyncio
import os
import random
import sys
from datetime import datetime, timedelta, timezone
from typing import Any

try:
    from bson import ObjectId
    from faker import Faker
    from motor.motor_asyncio import AsyncIOMotorClient
except ImportError:
    print("Required packages not installed. Run:")
    print("  pip install motor faker")
    sys.exit(1)


# Initialize Faker
fake = Faker()

# Platforms supported
PLATFORMS = ["amazon", "steam", "youtube", "reddit", "google", "trustpilot", "yelp"]

# Sentiment labels
SENTIMENTS = ["positive", "negative", "neutral", "mixed"]

# Emotions
EMOTIONS = ["joy", "sadness", "anger", "fear", "surprise", "disgust", "trust", "anticipation"]

# Project statuses
PROJECT_STATUSES = ["active", "paused", "completed", "archived"]

# Job statuses
JOB_STATUSES = ["pending", "running", "completed", "failed", "cancelled"]


def generate_user(index: int) -> dict[str, Any]:
    """Generate a mock user."""
    now = datetime.now(timezone.utc)
    created_at = fake.date_time_between(start_date="-1y", end_date="now", tzinfo=timezone.utc)

    return {
        "_id": ObjectId(),
        "email": f"testuser{index}@example.com",
        "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.S/YL0VlCLuFWxe",  # "password123"
        "name": fake.name(),
        "is_active": True,
        "is_verified": random.choice([True, True, True, False]),  # 75% verified
        "role": "admin" if index == 0 else "user",
        "oauth_provider": random.choice([None, None, None, "google", "github"]),  # 40% OAuth
        "last_login": fake.date_time_between(start_date=created_at, end_date="now", tzinfo=timezone.utc),
        "created_at": created_at,
        "updated_at": now,
    }


def generate_project(user_id: ObjectId, index: int) -> dict[str, Any]:
    """Generate a mock project."""
    now = datetime.now(timezone.utc)
    created_at = fake.date_time_between(start_date="-6m", end_date="now", tzinfo=timezone.utc)

    return {
        "_id": ObjectId(),
        "user_id": str(user_id),
        "name": f"{fake.company()} Sentiment Analysis",
        "description": fake.paragraph(nb_sentences=2),
        "status": random.choice(PROJECT_STATUSES),
        "config": {
            "scraper": {
                "provider": random.choice(["scraperapi", "apify", "brightdata", "scrapingbee"]),
                "max_pages": random.randint(1, 10),
                "delay_ms": random.randint(500, 2000),
            },
            "llm": {
                "provider": random.choice(["groq", "openai", "anthropic"]),
                "model": random.choice(["llama-3.1-70b-versatile", "gpt-4o-mini", "claude-3-haiku"]),
                "temperature": round(random.uniform(0.0, 0.7), 1),
            },
            "analysis": {
                "sentiment": True,
                "emotions": random.choice([True, False]),
                "keywords": random.choice([True, False]),
                "summary": random.choice([True, False]),
            },
        },
        "stats": {
            "total_targets": random.randint(1, 20),
            "total_results": random.randint(0, 500),
            "last_scrape_at": fake.date_time_between(start_date=created_at, end_date="now", tzinfo=timezone.utc) if random.random() > 0.3 else None,
        },
        "created_at": created_at,
        "updated_at": now,
    }


def generate_target(project_id: ObjectId, user_id: ObjectId, platform: str) -> dict[str, Any]:
    """Generate a mock target."""
    now = datetime.now(timezone.utc)

    # Generate platform-specific URLs
    url_templates = {
        "amazon": f"https://www.amazon.com/dp/{fake.bothify(text='??########')}",
        "steam": f"https://store.steampowered.com/app/{random.randint(100000, 999999)}",
        "youtube": f"https://www.youtube.com/watch?v={fake.bothify(text='???????????')}",
        "reddit": f"https://www.reddit.com/r/{fake.word()}/comments/{fake.bothify(text='??????')}",
        "google": f"https://www.google.com/maps/place/{fake.company().replace(' ', '+')}",
        "trustpilot": f"https://www.trustpilot.com/review/{fake.domain_name()}",
        "yelp": f"https://www.yelp.com/biz/{fake.slug()}",
    }

    return {
        "_id": ObjectId(),
        "project_id": str(project_id),
        "user_id": str(user_id),
        "url": url_templates.get(platform, f"https://example.com/{fake.slug()}"),
        "platform": platform,
        "name": fake.company() if platform in ["amazon", "google", "trustpilot", "yelp"] else fake.sentence(nb_words=4),
        "status": random.choice(["pending", "scraped", "failed"]),
        "last_scraped_at": fake.date_time_between(start_date="-30d", end_date="now", tzinfo=timezone.utc) if random.random() > 0.4 else None,
        "scrape_count": random.randint(0, 10),
        "created_at": fake.date_time_between(start_date="-3m", end_date="now", tzinfo=timezone.utc),
        "updated_at": now,
    }


def generate_result(project_id: ObjectId, target_id: ObjectId, user_id: ObjectId, platform: str) -> dict[str, Any]:
    """Generate a mock result with sentiment analysis."""
    now = datetime.now(timezone.utc)
    created_at = fake.date_time_between(start_date="-30d", end_date="now", tzinfo=timezone.utc)

    sentiment = random.choice(SENTIMENTS)
    sentiment_scores = {
        "positive": {"positive": 0.8, "negative": 0.1, "neutral": 0.1},
        "negative": {"positive": 0.1, "negative": 0.8, "neutral": 0.1},
        "neutral": {"positive": 0.2, "negative": 0.2, "neutral": 0.6},
        "mixed": {"positive": 0.4, "negative": 0.4, "neutral": 0.2},
    }

    # Add some randomness to scores
    scores = sentiment_scores[sentiment].copy()
    for key in scores:
        scores[key] = round(scores[key] + random.uniform(-0.1, 0.1), 2)
        scores[key] = max(0, min(1, scores[key]))

    # Generate emotions
    primary_emotion = random.choice(EMOTIONS)
    emotion_scores = {e: round(random.uniform(0, 0.3), 2) for e in EMOTIONS}
    emotion_scores[primary_emotion] = round(random.uniform(0.5, 0.9), 2)

    return {
        "_id": ObjectId(),
        "project_id": str(project_id),
        "target_id": str(target_id),
        "user_id": str(user_id),
        "scrape_job_id": str(ObjectId()),
        "platform": platform,
        "content": {
            "text": fake.paragraph(nb_sentences=random.randint(2, 6)),
            "title": fake.sentence(nb_words=random.randint(4, 10)) if random.random() > 0.3 else None,
            "author": fake.user_name() if random.random() > 0.2 else None,
            "rating": random.randint(1, 5) if platform in ["amazon", "google", "trustpilot", "yelp"] else None,
            "date": fake.date_time_between(start_date="-1y", end_date="now", tzinfo=timezone.utc),
            "url": f"https://{platform}.com/review/{fake.uuid4()}",
        },
        "analysis": {
            "sentiment": {
                "label": sentiment,
                "confidence": round(random.uniform(0.7, 0.99), 2),
                "scores": scores,
            },
            "emotions": {
                "primary": primary_emotion,
                "scores": emotion_scores,
            },
            "keywords": random.sample(
                ["quality", "price", "service", "delivery", "support", "product", "value", "experience"],
                k=random.randint(2, 5)
            ) if random.random() > 0.5 else [],
        },
        "metadata": {
            "language": "en",
            "word_count": random.randint(20, 200),
            "processed_at": now,
        },
        "created_at": created_at,
        "updated_at": now,
    }


def generate_scrape_job(project_id: ObjectId, user_id: ObjectId, target_count: int) -> dict[str, Any]:
    """Generate a mock scrape job."""
    now = datetime.now(timezone.utc)
    created_at = fake.date_time_between(start_date="-7d", end_date="now", tzinfo=timezone.utc)
    status = random.choice(JOB_STATUSES)

    results_count = random.randint(0, 100) if status == "completed" else 0

    return {
        "_id": ObjectId(),
        "project_id": str(project_id),
        "user_id": str(user_id),
        "status": status,
        "progress": 100 if status == "completed" else random.randint(0, 99) if status == "running" else 0,
        "config": {
            "targets": target_count,
            "max_results_per_target": random.randint(10, 50),
        },
        "stats": {
            "targets_processed": target_count if status == "completed" else random.randint(0, target_count),
            "results_scraped": results_count,
            "errors": random.randint(0, 3) if status in ["completed", "failed"] else 0,
        },
        "started_at": created_at if status != "pending" else None,
        "completed_at": fake.date_time_between(start_date=created_at, end_date="now", tzinfo=timezone.utc) if status in ["completed", "failed", "cancelled"] else None,
        "error": "Connection timeout" if status == "failed" else None,
        "created_at": created_at,
        "updated_at": now,
    }


async def seed_database(
    mongodb_url: str,
    database_name: str,
    num_users: int = 5,
    num_projects_per_user: int = 3,
    num_results_per_project: int = 50,
) -> None:
    """Seed the database with test data."""
    print(f"Connecting to MongoDB at {mongodb_url}...")
    client = AsyncIOMotorClient(mongodb_url)
    db = client[database_name]

    print(f"Using database: {database_name}")

    # Clear existing test data (optional)
    print("\nClearing existing test data...")
    await db.users.delete_many({"email": {"$regex": "^testuser"}})

    # Generate and insert users
    print(f"\nGenerating {num_users} users...")
    users = [generate_user(i) for i in range(num_users)]
    await db.users.insert_many(users)
    print(f"  Created {len(users)} users")

    total_projects = 0
    total_targets = 0
    total_results = 0
    total_jobs = 0

    for user in users:
        user_id = user["_id"]

        # Generate projects for each user
        num_projects = random.randint(1, num_projects_per_user)
        projects = [generate_project(user_id, i) for i in range(num_projects)]
        await db.projects.insert_many(projects)
        total_projects += len(projects)

        for project in projects:
            project_id = project["_id"]

            # Generate targets for each project
            num_targets = random.randint(2, 8)
            targets = []
            for _ in range(num_targets):
                platform = random.choice(PLATFORMS)
                targets.append(generate_target(project_id, user_id, platform))
            await db.targets.insert_many(targets)
            total_targets += len(targets)

            # Generate results for each project
            num_results = random.randint(10, num_results_per_project)
            results = []
            for _ in range(num_results):
                target = random.choice(targets)
                results.append(generate_result(project_id, target["_id"], user_id, target["platform"]))
            await db.results.insert_many(results)
            total_results += len(results)

            # Generate scrape jobs
            num_jobs = random.randint(1, 5)
            jobs = [generate_scrape_job(project_id, user_id, len(targets)) for _ in range(num_jobs)]
            await db.scrape_jobs.insert_many(jobs)
            total_jobs += len(jobs)

    # Print summary
    print("\n" + "=" * 50)
    print("Test Data Generation Complete!")
    print("=" * 50)
    print(f"  Users:    {len(users)}")
    print(f"  Projects: {total_projects}")
    print(f"  Targets:  {total_targets}")
    print(f"  Results:  {total_results}")
    print(f"  Jobs:     {total_jobs}")
    print("=" * 50)

    # Print test credentials
    print("\nTest Credentials:")
    print("-" * 30)
    print(f"  Admin:  testuser0@example.com / password123")
    print(f"  User:   testuser1@example.com / password123")
    print("-" * 30)

    client.close()


def main():
    parser = argparse.ArgumentParser(
        description="Generate test data for Sentimatrix Studio",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/seed_test_data.py
    python scripts/seed_test_data.py --users 10 --projects 5
    python scripts/seed_test_data.py --results 100
        """
    )
    parser.add_argument(
        "--users", "-u",
        type=int,
        default=5,
        help="Number of test users to create (default: 5)"
    )
    parser.add_argument(
        "--projects", "-p",
        type=int,
        default=3,
        help="Max projects per user (default: 3)"
    )
    parser.add_argument(
        "--results", "-r",
        type=int,
        default=50,
        help="Max results per project (default: 50)"
    )
    parser.add_argument(
        "--mongodb-url",
        type=str,
        default=os.getenv("MONGODB_URL", "mongodb://localhost:27017"),
        help="MongoDB connection URL"
    )
    parser.add_argument(
        "--database",
        type=str,
        default=os.getenv("DATABASE_NAME", "sentimatrix_studio"),
        help="Database name"
    )

    args = parser.parse_args()

    asyncio.run(seed_database(
        mongodb_url=args.mongodb_url,
        database_name=args.database,
        num_users=args.users,
        num_projects_per_user=args.projects,
        num_results_per_project=args.results,
    ))


if __name__ == "__main__":
    main()
