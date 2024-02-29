import os
import uuid
from enum import Enum
from io import BytesIO
from urllib.parse import urlparse
import requests
from PIL import ImageOps, Image
from werkzeug.datastructures import FileStorage

from app.upload import s3


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
        self.file_data.filename = str(uuid.uuid4())
        self.file_purpose = file_purpose
        self.user_id = user_id

    @property
    def filename(self):
        extension = self.file_data.filename.split('.')[-1]
        return f'{self.file_data.filename}.{extension}'

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
            return f'https://{self.bucket}.s3.amazonaws.com/{self.s3_key}'
        except Exception as e:
            print(f"An error occurred while uploading the image: {e}")
        return None

    @classmethod
    def get(cls, filename: str, image_type: FilePurpose, user_id: int):
        """
        Get the URL of the image from Amazon S3.

        :return: URL of the image if found, None otherwise.
        """
        return f'https://{cls.bucket}.s3.amazonaws.com/{image_type.value}/{user_id}/{filename}'

    def delete_from_s3(self):
        """
        Delete the file from Amazon S3.

        :return: True if deletion is successful, False otherwise.
        """
        try:
            s3.delete_object(Bucket=self.bucket, Key=self.s3_key)
            return True
        except Exception as e:
            print(f"An error occurred while deleting the file: {e}")

        return False

    @property
    def is_valid_image(self):
        try:
            image = Image.open(self.file_data.stream)
            image.verify()
            return True
        except:
            return False

    @staticmethod
    def download_from_url(url):
        try:
            response = requests.get(url, verify=True)
            if response.status_code == 200:
                filename = os.path.basename(urlparse(url).path)
                content_type = response.headers.get("Content-Type")
                file_stream = BytesIO(response.content)
                file_storage = FileStorage(file_stream, filename=filename, content_type=content_type)
                return file_storage
            else:
                return None
        except Exception as e:
            return None


class ProfileFile(File):
    def __init__(self, file_data: FileStorage, user_id: int):
        super().__init__(file_data, FilePurpose.PROFILE_PICTURE, user_id)

    def upload(self):
        """
        Upload the image to Amazon S3 after cropping it into a square.
        :return: URL if the upload is successful, None otherwise.
        """
        try:
            image = Image.open(self.file_data.stream)
            image = ImageOps.exif_transpose(image)  # Corrects image orientation if needed

            crop_size = min(image.width, image.height)
            left = (image.width - crop_size) // 2
            top = (image.height - crop_size) // 2
            right = left + crop_size
            bottom = top + crop_size

            image = image.crop((left, top, right, bottom))  # Crop to a centered square

            image_stream = BytesIO()
            image.save(image_stream, format='PNG')  # Adjust format if needed

            # Seek to the beginning of the stream before reading
            image_stream.seek(0)

            # Create a FileStorage object from the BytesIO stream
            file_storage = FileStorage(stream=image_stream, filename=self.filename, content_type='image/png')

            s3.put_object(Body=file_storage, Bucket=self.bucket, Key=self.s3_key)

            return f'https://{self.bucket}.s3.amazonaws.com/{self.s3_key}'
        except Exception as e:
            print(f"An error occurred while uploading the image: {e}")
        return None


class PostAttachment(File):
    def __init__(self, file_data: FileStorage, user_id: int):
        super().__init__(file_data, FilePurpose.POST_ATTACHMENT, user_id)


class MessageAttachment(File):
    def __init__(self, file_data: FileStorage, user_id: int):
        super().__init__(file_data, FilePurpose.MESSAGE_ATTACHMENT, user_id)
