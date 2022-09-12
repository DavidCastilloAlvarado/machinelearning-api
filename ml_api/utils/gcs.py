import hashlib
import logging
from datetime import datetime

from google.cloud import storage


def create_name(source, folder):
    assert any([val in folder for val in ("models", "encoders")])
    date = datetime.now().strftime("%d-%m-%y")
    ext = source.split(".")[-1]
    name = hashlib.md5(str(datetime.now()).encode("ascii")).hexdigest()
    destination_blob_name = f"{folder}/{date}/{name}.{ext}"
    return destination_blob_name


def upload_blob(bucket_name, source_file_name, folder):
    """Uploads a file to the bucket. https://cloud.google.com/storage/docs/"""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    destination_blob_name = create_name(source_file_name, folder)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    print(f"File {source_file_name} uploaded to {destination_blob_name}.")
    return f"https://storage.cloud.google.com/{bucket_name}/{destination_blob_name}"


def download_to_file(blob_url, file_destination):
    storage_client = storage.Client()
    """Takes the data from your GCS Bucket and puts it into the working directory"""
    assert "storage.cloud.google.com/" in blob_url, "Url file is not an storage object"
    convert_to_gs_url = blob_url.replace("https", "gs").replace(
        "storage.cloud.google.com/", ""
    )
    with open(file_destination, "wb") as file_obj:
        storage_client.download_blob_to_file(convert_to_gs_url, file_obj)
    logging.info(blob_url + " : was downloaded")
    return file_destination
