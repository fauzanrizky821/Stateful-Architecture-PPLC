# Praktikum 5 - Django + Azure Blob

Fitur: form sederhana untuk input **nama musik**, **penyanyi**, dan upload file **MP3**. File MP3 disimpan ke **Azure Blob Storage** (bukan local). Database menggunakan **PostgreSQL** jika variabel `POSTGRES_*` diisi.

## Setup

1) Buat virtualenv lalu install dependency:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2) Copy `.env.example` menjadi `.env` lalu isi `DJANGO_SECRET_KEY`, setting PostgreSQL, dan setting Azure.

Catatan: upload akan gagal jika `AZURE_CONNECTION_STRING` / `AZURE_CONTAINER` belum diisi. Jika `POSTGRES_*` belum diisi, project tetap bisa jalan dengan SQLite untuk mode lokal.

3) Migrasi & jalankan:

```bash
python manage.py migrate
python manage.py runserver
```

Buka `http://127.0.0.1:8000/` untuk upload, dan `http://127.0.0.1:8000/library/` untuk melihat dan memutar daftar musik.
