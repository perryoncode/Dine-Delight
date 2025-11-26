import os
import random
from datetime import datetime
from typing import List, Dict
from pymongo import MongoClient

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://codewithperry:uYIoXdcbIBi3qdBh@cluster0.iub7ykj.mongodb.net/",
)
DB_NAME = os.getenv("DB_NAME", "Restaurant")
ORDERS_COLLECTION = os.getenv("ORDERS_COLLECTION", "orders")
DISHES_COLLECTION = os.getenv("DISHES_COLLECTION", "dishes")

FALLBACK_DISHES = [
    {"name": "Chole Bhature", "price": 70.0},
    {"name": "Masala Dosa", "price": 90.0},
    {"name": "Paneer Tikka", "price": 120.0},
    {"name": "Veg Biryani", "price": 150.0},
    {"name": "Gulab Jamun", "price": 40.0},
]

NAMES = [
    "Aarav Sharma", "Vivaan Gupta", "Aditya Singh", "Vihaan Patel", "Arjun Mehta",
    "Reyansh Kumar", "Krishna Rao", "Ishaan Nair", "Shaurya Jain", "Dhruv Shah",
    "Pranshu Tripathi", "Aanya Kapoor", "Anaya Verma", "Diya Bansal", "Pari Chatterjee",
    "Aadhya Iyer", "Kiara Reddy", "Myra Bose", "Sara Malhotra", "Ira Kulkarni",
]


def get_dishes(collection) -> List[Dict]:
    dishes = []
    try:
        for d in collection.find({}, {"name": 1, "price": 1}):
            name = d.get("name")
            price = float(d.get("price", 100))
            if name:
                dishes.append({"name": name, "price": price})
    except Exception:
        pass
    return dishes or FALLBACK_DISHES


def rand_int(a: int, b: int) -> int:
    return random.randint(a, b)


def build_orders(count: int, year: int, month: int, dishes: List[Dict]) -> List[Dict]:
    docs: List[Dict] = []
    for _ in range(count):
        name = random.choice(NAMES)
        email = f"{name.split()[0].lower()}.{rand_int(100, 999)}@example.com"

        items = []
        for __ in range(rand_int(1, 3)):
            dish = random.choice(dishes)
            qty = rand_int(1, 4)
            items.append({"name": dish["name"], "price": dish["price"], "quantity": qty})
        total = sum(x["price"] * x["quantity"] for x in items)

        day = rand_int(1, 31)
        hour = rand_int(9, 21)
        minute = rand_int(0, 59)
        second = rand_int(0, 59)
        try:
            created_at = datetime(year, month, day, hour, minute, second)
        except ValueError:
            created_at = datetime(year, month, 28, hour, minute, second)

        docs.append({
            "user_id": None,
            "name": name,
            "email": email,
            "items": items,
            "total": total,
            "created_at": created_at,
        })
    return docs


def seed(count: int = 50, month_str: str = "2025-10") -> int:
    print(f"[seed] Starting seeding: count={count}, month_str={month_str}")
    try:
        year_s, mon_s = month_str.split("-")
        year, mon = int(year_s), int(mon_s)
        print(f"[seed] Parsed year={year}, month={mon}")
    except Exception as e:
        print(f"[seed] ERROR parsing month_str: {e}")
        raise ValueError("month_str must be in YYYY-MM format, e.g., 2025-10")

    print(f"[seed] Connecting to MongoDB: uri={MONGO_URI}")
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    print(f"[seed] Using database: {DB_NAME}")
    orders_col = db[ORDERS_COLLECTION]
    dishes_col = db[DISHES_COLLECTION]
    try:
        print("[seed] Ping Mongo...")
        client.admin.command('ping')
        print("[seed] Mongo ping OK")
    except Exception as e:
        print(f"[seed] Mongo ping FAILED: {e}")
        raise

    print("[seed] Loading dishes list...")
    dishes = get_dishes(dishes_col)
    print(f"[seed] Dishes available: {len(dishes)}")
    docs = build_orders(count, year, mon, dishes)
    print(f"[seed] Built docs: {len(docs)}")
    if not docs:
        print("[seed] No docs to insert")
        return 0
    print(f"[seed] Inserting into collection: {ORDERS_COLLECTION}")
    res = orders_col.insert_many(docs)
    inserted = len(res.inserted_ids)
    print(f"[seed] Inserted {inserted} orders")
    return inserted


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Seed synthetic orders into MongoDB.")
    parser.add_argument("--count", type=int, default=50, help="Number of orders to insert (default: 50)")
    parser.add_argument("--month", type=str, default="2025-10", help="Month in YYYY-MM (default: 2025-10)")
    args = parser.parse_args()

    try:
        inserted = seed(count=args.count, month_str=args.month)
        print(f"[seed] Done. Inserted {inserted} orders into {DB_NAME}.{ORDERS_COLLECTION} for {args.month}")
    except Exception as e:
        print(f"[seed] FAILED: {e}")
        raise
