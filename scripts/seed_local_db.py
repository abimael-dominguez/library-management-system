#!/usr/bin/env python3

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.infrastructure.database import SessionLocal, init_db
from src.infrastructure.seed import seed_demo_data


def main() -> None:
    init_db()
    with SessionLocal() as db:
        seed_demo_data(db)
    print("Local database initialized and seeded.")


if __name__ == "__main__":
    main()
