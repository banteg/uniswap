import asyncio

from uniwatch.db import db


async def main():
    await db.init()


if __name__ == '__main__':
    asyncio.run(main())
