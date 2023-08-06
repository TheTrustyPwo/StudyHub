import uuid
from enum import Enum

from werkzeug.datastructures import FileStorage

from app.upload import s3


cache = {}


class FilePurpose(Enum):
    PROFILE_PICTURE = 'profile_picture'
    MESSAGE_ATTACHMENT = 'message_attachment'
    POST_ATTACHMENT = 'post_attachment'

    @classmethod
    def has_key(cls, name):
        return name.upper() in cls.__members__


class File:
    endpoint = 'https://thepwo.s3.ap-southeast-1.amazonaws.com'
    bucket = 'thepwo'

    def __init__(self, file_data: FileStorage, file_purpose: FilePurpose, user_id: int):
        self.file_data = file_data
        self.random_hash = str(uuid.uuid4())
        self.file_purpose = file_purpose
        self.user_id = user_id

    @property
    def filename(self):
        extension = self.file_data.filename.split('.')[-1]
        return f'{self.random_hash}.{extension}'

    @property
    def s3_key(self):
        return f'{self.file_purpose.value}/{self.user_id}/{self.filename}'

    def upload(self):
        """
        Upload the image to Amazon S3.
        :return: True if the upload is successful, False otherwise.
        """
        try:
            s3.put_object(Body=self.file_data, Bucket=self.bucket, Key=self.s3_key)
            cache[self.s3_key] = s3.generate_presigned_url('get_object', Params={'Bucket': cls.bucket, 'Key': self.s3_key})
            return f'{self.endpoint}/{self.s3_key}'
        except Exception as e:
            print(f"An error occurred while uploading the image: {e}")
        return None

    @classmethod
    def get(cls, filename: str, image_type: FilePurpose, user_id: int):
        """
        Get the URL of the image from Amazon S3.

        :return: URL of the image if found, None otherwise.
        """
        try:
            s3_key = f'{image_type.value}/{user_id}/{filename}'
            if s3_key not in cache:
                cache[s3_key] = s3.generate_presigned_url('get_object', Params={'Bucket': cls.bucket, 'Key': s3_key})
            return cache[s3_key]
        except Exception as e:
            print(f"An error occurred while getting the image: {e}")
        return None

    # def delete_from_s3(self, file_extension):
    #     """
    #     Delete the image from Amazon S3.
    #
    #     :param file_extension: File extension of the image.
    #     :return: True if deletion is successful, False otherwise.
    #     """
    #     s3 = boto3.client('s3', region_name=AWS_REGION)
    #     s3_key = self.get_s3_key(file_extension)
    #
    #     try:
    #         s3.delete_object(Bucket=BUCKET_NAME, Key=s3_key)
    #         return True
    #     except NoCredentialsError:
    #         print("AWS credentials not found. Make sure you have configured them.")
    #     except Exception as e:
    #         print(f"An error occurred while deleting the image: {e}")
    #
    #     return False


class ProfileFile(File):
    def __init__(self, file_data: FileStorage, user_id: int):
        super().__init__(file_data, FilePurpose.PROFILE_PICTURE, user_id)


class PostAttachment(File):
    def __init__(self, file_data: FileStorage, user_id: int):
        super().__init__(file_data, FilePurpose.POST_ATTACHMENT, user_id)


class MessageAttachment(File):
    def __init__(self, file_data: FileStorage, user_id: int):
        super().__init__(file_data, FilePurpose.MESSAGE_ATTACHMENT, user_id)
