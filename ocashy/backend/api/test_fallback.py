import sys
import os
import unittest
from unittest.mock import MagicMock

# 1. Mock all external/FastAPI dependencies so tests can run without having packages installed
class MockHTTPException(Exception):
    def __init__(self, status_code, detail):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"HTTP {status_code}: {detail}")

class MockFastAPI:
    def __init__(self, *args, **kwargs):
        pass
    def post(self, *args, **kwargs):
        return lambda f: f
    def get(self, *args, **kwargs):
        return lambda f: f
    def put(self, *args, **kwargs):
        return lambda f: f
    def delete(self, *args, **kwargs):
        return lambda f: f
    def add_middleware(self, *args, **kwargs):
        pass

fastapi_mock = MagicMock()
fastapi_mock.FastAPI = MockFastAPI
fastapi_mock.Query = lambda *args, **kwargs: MagicMock()
fastapi_mock.HTTPException = MockHTTPException

sys.modules['fastapi'] = fastapi_mock
sys.modules['fastapi.middleware.cors'] = MagicMock()
sys.modules['fastapi.responses'] = MagicMock()
sys.modules['fastapi_pagination'] = MagicMock()
sys.modules['decouple'] = MagicMock()
sys.modules['dotenv'] = MagicMock()
sys.modules['PyPDF2'] = MagicMock()
sys.modules['reportlab'] = MagicMock()
sys.modules['reportlab.pdfgen'] = MagicMock()
sys.modules['reportlab.lib'] = MagicMock()
sys.modules['reportlab.lib.pagesizes'] = MagicMock()
sys.modules['reportlab.platypus'] = MagicMock()
sys.modules['reportlab.lib.styles'] = MagicMock()
sys.modules['reportlab.lib.units'] = MagicMock()
sys.modules['reportlab.lib.colors'] = MagicMock()
sys.modules['reportlab.lib.utils'] = MagicMock()

# Mock Pydantic
class MockBaseModel:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
    def dict(self):
        return self.__dict__

def mock_field(*args, **kwargs):
    return MagicMock()

pydantic_mock = MagicMock()
pydantic_mock.BaseModel = MockBaseModel
pydantic_mock.Field = mock_field
sys.modules['pydantic'] = pydantic_mock

# 2. Setup path dynamically
api_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, api_dir)

from functions.db import defineDB
from functions.data import get_items
import main

class TestBackendSQLiteFallback(unittest.TestCase):
    def setUp(self):
        # We ensure the fallback database is initialized
        self.db_path = os.path.join(api_dir, "ocashy_fallback.db")
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except OSError:
                pass
        self.db = defineDB()
        self.assertIsNotNone(self.db, "Failed to initialize fallback database connection")

    def tearDown(self):
        if self.db:
            self.db.close()
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except OSError:
                pass

    def test_01_seeding_and_read(self):
        print("\n[TEST] Verifying SQLite database seeding and reading...")
        items = get_items()
        self.assertEqual(len(items), 3, "Should have seeded 3 sample products")
        self.assertEqual(items[0]['result_id'], 'B001')
        self.assertEqual(items[0]['result_name'], 'Contoh Barang A')
        self.assertEqual(items[0]['result_price'], 15000)
        print("-> Seeding and reading verified successfully!")

    def test_02_pagination_and_search(self):
        print("\n[TEST] Verifying pagination and search functions...")
        items, count = main.get_items2(page=1, limit=2)
        self.assertEqual(len(items), 2)
        self.assertEqual(count, 3)

        search_items, search_count = main.search_by_name("Barang B", page=1, limit=10)
        self.assertEqual(len(search_items), 1)
        self.assertEqual(search_items[0]['result_id'], 'B002')
        print("-> Pagination and search verified successfully!")

    def test_03_create_item(self):
        print("\n[TEST] Verifying create_item endpoint logic...")
        new_item = main.ItemUpdate(
            id_barang='B004',
            nama='Barang Baru D',
            hargaJual=50000,
            hargaBeli=35000,
            id_kategori='K03',
            kulon=10, toko=10, pink=10, wetan=10, kedungsari=10
        )
        import asyncio
        response = asyncio.run(main.create_item(new_item))
        self.assertIn("successfully created", response["message"])

        val = main.get_current_values('B004')
        self.assertIsNotNone(val)
        val_lower = {k.lower(): v for k, v in val.items()}
        self.assertEqual(val_lower.get('nama'), 'Barang Baru D')
        self.assertEqual(val_lower.get('hargajual'), 50000)
        print("-> Create item verified successfully!")

    def test_04_update_item(self):
        print("\n[TEST] Verifying update_item endpoint logic...")
        updated_item = main.ItemUpdate(
            id_barang='B001',
            nama='Contoh Barang A Updated',
            hargaJual=16000,
            hargaBeli=11000
        )
        import asyncio
        result = asyncio.run(main.update_item('B001', updated_item))
        result_lower = {k.lower(): v for k, v in result.items()}
        self.assertEqual(result_lower.get('nama'), 'Contoh Barang A Updated')
        self.assertEqual(result_lower.get('hargajual'), 16000)
        print("-> Update item verified successfully!")

    def test_05_delete_item(self):
        print("\n[TEST] Verifying delete_item endpoint logic...")
        import asyncio
        response = asyncio.run(main.delete_item('B003'))
        self.assertIn("successfully deleted", response["message"])

        val = main.get_current_values('B003')
        self.assertIsNone(val)
        print("-> Delete item verified successfully!")

if __name__ == '__main__':
    unittest.main()
