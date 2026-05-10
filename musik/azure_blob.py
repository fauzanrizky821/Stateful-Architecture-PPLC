import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobServiceClient, BlobSasPermissions, ContentSettings, generate_blob_sas
from django.conf import settings


@dataclass(frozen=True)
class UploadedBlob:
    blob_name: str
    url: str


def _get_connection_string() -> str:
    cs = getattr(settings, 'AZURE_CONNECTION_STRING', '') or os.getenv('AZURE_CONNECTION_STRING', '')
    if not cs:
        raise RuntimeError('AZURE_CONNECTION_STRING belum di-set')
    return cs


def _parse_connection_string(connection_string: str) -> dict[str, str]:
    parts = [part for part in connection_string.split(';') if '=' in part]
    return {key: value for key, value in (part.split('=', 1) for part in parts)}


def _get_container() -> str:
    container = getattr(settings, 'AZURE_CONTAINER', '') or os.getenv('AZURE_CONTAINER', '')
    if not container:
        raise RuntimeError('AZURE_CONTAINER belum di-set')
    return container


def _get_location_prefix() -> str:
    location = (getattr(settings, 'AZURE_LOCATION', '') or os.getenv('AZURE_LOCATION', '') or '').strip('/ ')
    return location


def build_blob_sas_url(blob_url_or_name: str, expires_in_minutes: int = 60) -> str:
    """Build a read-only SAS URL for a blob stored in a private container."""
    connection_string = _get_connection_string()
    container = _get_container()
    details = _parse_connection_string(connection_string)
    account_name = details.get('AccountName', '')
    account_key = details.get('AccountKey', '')

    if not account_name or not account_key:
        raise RuntimeError('Connection string harus berisi AccountName dan AccountKey')

    parsed = urlparse(blob_url_or_name)
    if parsed.scheme and parsed.netloc:
        path = parsed.path.lstrip('/')
        if path.startswith(f'{container}/'):
            blob_name = path[len(container) + 1 :]
        else:
            blob_name = path
        base_url = f'{parsed.scheme}://{parsed.netloc}/{container}/{blob_name}' if blob_name else f'{parsed.scheme}://{parsed.netloc}/{container}'
    else:
        blob_name = blob_url_or_name.lstrip('/')
        base_url = f'https://{account_name}.blob.core.windows.net/{container}/{blob_name}'

    expiry = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)
    sas_token = generate_blob_sas(
        account_name=account_name,
        container_name=container,
        blob_name=blob_name,
        account_key=account_key,
        permission=BlobSasPermissions(read=True),
        expiry=expiry,
    )
    return f'{base_url}?{sas_token}'


def upload_mp3(file_obj, *, blob_name: str | None = None) -> UploadedBlob:
    """Upload file-like object ke Azure Blob Storage tanpa menyimpan ke local.

    - file_obj: biasanya request.FILES['file_mp3'] (UploadedFile)
    - blob_name: nama blob relatif (tanpa container). Jika None akan pakai nama file.

    Return: UploadedBlob(blob_name, url)
    """
    connection_string = _get_connection_string()
    container = _get_container()
    location = _get_location_prefix()

    original_name = getattr(file_obj, 'name', 'upload.mp3')
    filename = os.path.basename(original_name).replace('\\', '/').split('/')[-1]

    if not blob_name:
        blob_name = filename

    if location:
        blob_name = f"{location}/{blob_name}".replace('\\', '/')

    service = BlobServiceClient.from_connection_string(connection_string)
    container_client = service.get_container_client(container)

    try:
        container_client.create_container()
    except ResourceExistsError:
        pass

    blob_client = container_client.get_blob_client(blob_name)

    content_settings = ContentSettings(content_type='audio/mpeg')
    # upload_blob will stream; overwrite to simplify.
    blob_client.upload_blob(file_obj, overwrite=True, content_settings=content_settings)

    return UploadedBlob(blob_name=blob_name, url=blob_client.url)


def delete_blob(blob_path: str) -> bool:
    """Delete blob file dari Azure Blob Storage.
    
    - blob_path: nama blob atau URL. Jika URL akan extract blob name.
    
    Return: True jika berhasil, False jika file tidak ditemukan.
    """
    connection_string = _get_connection_string()
    container = _get_container()
    
    # Extract blob name dari URL atau path
    parsed = urlparse(blob_path)
    if parsed.scheme and parsed.netloc:
        path = parsed.path.lstrip('/')
        if path.startswith(f'{container}/'):
            blob_name = path[len(container) + 1:]
        else:
            blob_name = path
    else:
        blob_name = blob_path.lstrip('/')
    
    try:
        service = BlobServiceClient.from_connection_string(connection_string)
        container_client = service.get_container_client(container)
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.delete_blob()
        return True
    except Exception as e:
        print(f"Error deleting blob {blob_name}: {e}")
        return False
