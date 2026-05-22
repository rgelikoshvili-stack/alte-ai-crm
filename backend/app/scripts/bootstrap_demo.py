from __future__ import annotations

import asyncio
import json

from app.core.database import AsyncSessionLocal
from app.services.bootstrap_service import bootstrap_local_demo_data


async def main() -> None:
    async with AsyncSessionLocal() as session:
        result = await bootstrap_local_demo_data(session)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    asyncio.run(main())

