from pathlib import Path
import os
import uuid

from azure.storage.blob import BlobServiceClient, ContentSettings
from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parent / '.env')

cs = os.getenv("AZURE_CONNECTION_STRING")
if not cs:
    raise SystemExit("AZURE_CONNECTION_STRING belum di-set di environment")

print("AZURE_CONTAINER:", os.getenv("AZURE_CONTAINER", "<missing>"))
print("AZURE_LOCATION:", os.getenv("AZURE_LOCATION", "<missing>"))

svc = BlobServiceClient.from_connection_string(cs)

# list containers (melihat apakah autentikasi berhasil)
print("Containers:", [c.name for c in svc.list_containers()])

# coba upload small blob ke container yang kamu pakai
container = os.getenv("AZURE_CONTAINER", "303blobstorage")
blob_name = f"debug-{uuid.uuid4().hex}.txt"
blob_client = svc.get_blob_client(container=container, blob=blob_name)
content = b"hello from test\n"
blob_client.upload_blob(content, overwrite=True, content_settings=ContentSettings(content_type="text/plain"))
print("Uploaded:", blob_client.url)