from io import BytesIO

from miniopy_async import Minio
from miniopy_async.error import S3Error

from src import consts
from ..file_storage_models import DownloadResult, UploadBody
from ..file_storage import ErrInternal, ErrNotFound


class ArticleStorage:
    def __init__(self, client: Minio):
        self.client = client

    async def download_file(self, user_id: int, id: int) -> DownloadResult:
        try:
            response = await self.client.get_object(
                bucket_name=consts.S3_BUCKET,
                object_name=self.__key(
                    user_id=user_id,
                    id=id,
                ),
            )
            contents = await response.read()
        except S3Error as e:
            if e.code == "NoSuchKey":
                raise ErrNotFound(
                    "article-storage: download_file: not-found: {}".format(str(e))
                )
            raise ErrInternal("article-storage: download_file: {}".format(str(e)))
        except Exception as e:
            raise ErrInternal("article-storage: download_file: {}".format(str(e)))

        return DownloadResult(contents=contents)

    async def upload(self, body: UploadBody) -> None:
        response = await self.client.put_object(
            object_name=self.__key(user_id=body.user_id, id=body.id),
            bucket_name=consts.S3_BUCKET,
            data=BytesIO(body.contents),
            length=len(body.contents),
            content_type="text",
        )

    def __key(self, user_id: int, id: int) -> str:
        return "{}/{}".format(user_id, id)
