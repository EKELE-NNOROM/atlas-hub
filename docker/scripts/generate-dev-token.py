#!/usr/bin/env python3
"""Generate a JWT for local Docker development."""

import argparse
import os
from datetime import datetime, timedelta, timezone

import jwt

DEFAULT_SECRET = "local-dev-secret-change-me"
DEFAULT_SCOPES = ["admin", "finance", "sales", "product", "hr", "executive"]


def main():
    parser = argparse.ArgumentParser(description="Generate Atlas Hub dev JWT")
    parser.add_argument("--secret", default=os.environ.get("ATLAS_JWT_SECRET", DEFAULT_SECRET))
    parser.add_argument("--sub", default="dev-user@local")
    parser.add_argument("--scopes", nargs="+", default=DEFAULT_SCOPES)
    parser.add_argument("--hours", type=int, default=24)
    args = parser.parse_args()

    payload = {
        "sub": args.sub,
        "scopes": args.scopes,
        "exp": datetime.now(timezone.utc) + timedelta(hours=args.hours),
    }
    token = jwt.encode(payload, args.secret, algorithm="HS256")
    print(token)


if __name__ == "__main__":
    main()
