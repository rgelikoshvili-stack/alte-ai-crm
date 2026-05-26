from __future__ import annotations

import argparse
import asyncio
import secrets
import string
from pathlib import Path

from sqlalchemy import select

from app.core.config import get_settings
from app.core.database import AsyncSessionLocal
from app.models import User
from app.services.security_service import hash_password


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SECRET_OUTPUT = PROJECT_ROOT / ".local-secrets" / "temporary_crm_admin_credentials.txt"


def generate_password(length: int = 24) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    while True:
        password = "".join(secrets.choice(alphabet) for _ in range(length))
        if (
            any(char.islower() for char in password)
            and any(char.isupper() for char in password)
            and any(char.isdigit() for char in password)
            and any(char in "!@#$%^&*()-_=+" for char in password)
        ):
            return password


async def create_or_update_admin(email: str, name: str, role: str, password: str) -> dict[str, str | bool]:
    settings = get_settings()
    if settings.ENVIRONMENT.lower().strip() != "production":
        raise RuntimeError("Refusing to create production admin unless ENVIRONMENT=production")
    if role not in {"admin", "operator"}:
        raise RuntimeError("Role must be admin or operator")

    async with AsyncSessionLocal() as session:
        user = await session.scalar(select(User).where(User.email == email))
        created = user is None
        if user is None:
            user = User(name=name, email=email, role=role, is_active=True)
            session.add(user)
        user.name = name
        user.role = role
        user.is_active = True
        user.password_hash = hash_password(password)
        await session.commit()
        return {"email": email, "role": role, "created": created}


def write_credentials(email: str, password: str, role: str) -> None:
    SECRET_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    SECRET_OUTPUT.write_text(
        "\n".join(
            [
                "Temporary Alte CRM admin credentials",
                "Do not commit this file.",
                f"email={email}",
                f"role={role}",
                f"password={password}",
                "",
            ]
        ),
        encoding="utf-8",
    )


async def main_async() -> None:
    parser = argparse.ArgumentParser(description="Create or update a temporary production CRM admin user.")
    parser.add_argument("--email", required=True)
    parser.add_argument("--name", default="Temporary CRM Admin")
    parser.add_argument("--role", default="admin", choices=["admin", "operator"])
    args = parser.parse_args()

    password = generate_password()
    result = await create_or_update_admin(args.email.strip().lower(), args.name, args.role, password)
    write_credentials(args.email.strip().lower(), password, args.role)
    action = "created" if result["created"] else "updated"
    print(f"Temporary CRM {result['role']} user {action}: {result['email']}")
    print(f"Credentials written to: {SECRET_OUTPUT.relative_to(PROJECT_ROOT)}")


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
