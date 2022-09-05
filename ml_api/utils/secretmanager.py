import google.auth
from google.cloud import secretmanager

_, PROJECT_ID = google.auth.default()


def get_payload_secret(secret_name):
    """
    Get secrets form google cloud secret manager
    """
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{PROJECT_ID}/secrets/{secret_name}/versions/latest"
    payload = client.access_secret_version(name=name).payload.data.decode("UTF-8")
    return payload
