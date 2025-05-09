"""Test that all modules can be imported correctly."""

import unittest

class TestImports(unittest.TestCase):
    """Test that all modules can be imported correctly."""

    def test_import_package(self):
        """Test that the package can be imported."""
        import dailywire_downloader
        self.assertIsNotNone(dailywire_downloader)
        self.assertEqual(dailywire_downloader.__version__, "0.1.0")

    def test_import_downloader(self):
        """Test that the downloader module can be imported."""
        from dailywire_downloader import download
        self.assertIsNotNone(download)

    def test_import_nfo(self):
        """Test that the nfo module can be imported."""
        from dailywire_downloader import nfo
        self.assertIsNotNone(nfo)

    def test_import_main(self):
        """Test that the __main__ module can be imported."""
        from dailywire_downloader import __main__
        self.assertIsNotNone(__main__)

if __name__ == "__main__":
    unittest.main()
