from sqlalchemy import text
from src.gears.db import DB
from src.storage.postgres.user_acct_storage import UserAcctStorage
from src.storage.user_acct_storage import ErrUsernameTaken, ErrEmailTaken
import src.storage.user_acct_models as models
import asyncio

db = DB(dsn="postgresql+asyncpg://rai:rai@localhost:5432/rai", echo=False)


async def main():
    storage = UserAcctStorage(db=db)
    try:
        result = await storage.create(
            models.CreateBody(
                username="sjjjsjsjs",
                email="fuckyou3@mail.com",
                password="fuckfuckfuck",
            )
        )
        print(result)
    except ErrEmailTaken as e:
        print(e)
    except Exception as e:
        print(e)


asyncio.run(main())
