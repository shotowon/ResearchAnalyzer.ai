import asyncio
import uvicorn

from src.init import logger, cfg, minio
from src import consts


async def main():
    try:
        if not await minio.bucket_exists(consts.S3_BUCKET):
            logger.info("created S3 bucket for ResearchAnalyzer.ai")
            await minio.make_bucket(consts.S3_BUCKET)

        logger.info(
            "server is starting at %s:%d", cfg.http_server.host, cfg.http_server.port
        )
        uvicorn.run(
            app="src.main:app",
            host=cfg.http_server.host,
            port=cfg.http_server.port,
            reload=True,
        )
    except Exception as e:
        logger.critical("unexpected error: %s", str(e))


if __name__ == "__main__":
    asyncio.run(main())
