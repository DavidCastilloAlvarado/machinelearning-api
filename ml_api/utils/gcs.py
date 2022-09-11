from google.cloud import storage
from datetime import datetime
import hashlib
import joblib  # for saving algorithm and preprocessing objects
import logging

storage_client = storage.Client()


def create_name(source, folder):
    assert any([val in folder for val in ("models", "encoders")])
    date = datetime.now().strftime("%d-%m-%y")
    ext = source.split('.')[-1]
    name = hashlib.md5(str(datetime.now()).encode('ascii')).hexdigest()
    destination_blob_name = f"{folder}/{date}/{name}.{ext}"
    return destination_blob_name


def create_bucket(dataset_name):
    """Creates a new bucket. https://cloud.google.com/storage/docs/ """
    bucket = storage_client.create_bucket(dataset_name)
    print('Bucket {} created'.format(bucket.name))


def upload_blob(bucket_name, source_file_name, folder):
    """Uploads a file to the bucket. https://cloud.google.com/storage/docs/ """
    bucket = storage_client.get_bucket(bucket_name)
    destination_blob_name = create_name(source_file_name, folder)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    print('File {} uploaded to {}.'.format(
        source_file_name,
        destination_blob_name))
    return f"https://storage.cloud.google.com/{bucket_name}/{destination_blob_name}"


def list_blobs(bucket_name):
    """Lists all the blobs in the bucket. https://cloud.google.com/storage/docs/"""
    blobs = storage_client.list_blobs(bucket_name)
    for blob in blobs:
        print(blob.name)


def download_to_file(blob_url, file_destination):
    """Takes the data from your GCS Bucket and puts it into the working directory """
    assert "storage.cloud.google.com/" in blob_url, "Url file is not an storage object"
    convert_to_gs_url = blob_url.replace('https', 'gs').replace('storage.cloud.google.com/', '')
    with open(file_destination, 'wb') as file_obj:
        storage_client.download_blob_to_file(convert_to_gs_url, file_obj)
    logging.info(blob_url + " : was downloaded")
    return file_destination
