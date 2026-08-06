import os
import shutil
import tempfile
import unittest

from storage import Storage


class StorageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp(prefix="storage-test-", dir=".")
        self.db_path = os.path.join(self.temp_dir, "store.db")
        self.storage = Storage(self.db_path)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_persists_and_retrieves_items_across_instances(self) -> None:
        self.storage.add_item("note", "text", "hello")

        reloaded = Storage(self.db_path)
        item = reloaded.get_item("note")

        self.assertIsNotNone(item)
        self.assertEqual(item["value"], "hello")
        self.assertEqual(item["type"], "text")

        items = reloaded.list_items()
        self.assertEqual(len(items), 1)


if __name__ == "__main__":
    unittest.main()
