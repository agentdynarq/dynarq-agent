"""Tests for the file_reader and http_fetch tools, including their guardrails.

These run fully offline: the SSRF checks happen before any network call, so we
can assert that private URLs are refused without touching the network, and the
HTML-to-text helper is pure.
"""
import os
import tempfile
import unittest

from dynarq_agent.tools.file_reader import read_file
from dynarq_agent.tools.http_fetch import _html_to_text, _validate, fetch_url


class TestFileReader(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        with open(os.path.join(self.tmp, "note.txt"), "w", encoding="utf-8") as fh:
            fh.write("hello from the sandbox")

    def test_reads_file(self):
        self.assertEqual(read_file("note.txt", base_dir=self.tmp), "hello from the sandbox")

    def test_truncates(self):
        with open(os.path.join(self.tmp, "big.txt"), "w", encoding="utf-8") as fh:
            fh.write("x" * 100)
        out = read_file("big.txt", max_chars=10, base_dir=self.tmp)
        self.assertIn("truncated", out)

    def test_blocks_path_traversal(self):
        out = read_file("../../etc/passwd", base_dir=self.tmp)
        self.assertTrue(out.startswith("Error: path escapes"))

    def test_blocks_absolute_escape(self):
        outside = os.path.abspath(os.sep)  # filesystem root, outside the temp base
        out = read_file(outside, base_dir=self.tmp)
        self.assertTrue(out.startswith("Error"))

    def test_missing_file(self):
        self.assertTrue(read_file("nope.txt", base_dir=self.tmp).startswith("Error: no such file"))

    def test_directory_refused(self):
        self.assertIn("directory", read_file(".", base_dir=self.tmp))


class TestHttpFetchGuards(unittest.TestCase):
    def test_rejects_non_http_scheme(self):
        self.assertTrue(fetch_url("file:///etc/passwd").startswith("Error: only http"))
        self.assertTrue(fetch_url("ftp://example.com").startswith("Error: only http"))

    def test_rejects_loopback_and_private(self):
        for url in ("http://localhost/", "http://127.0.0.1/", "http://169.254.169.254/",
                    "http://10.0.0.1/", "http://192.168.1.1/"):
            self.assertTrue(fetch_url(url).startswith("Error: refusing"), url)

    def test_validate_accepts_public_shape(self):
        # A normal public host passes validation (DNS resolves to a public IP).
        self.assertIsNone(_validate("https://example.com/path"))

    def test_missing_host(self):
        self.assertTrue(fetch_url("http:///nohost").startswith("Error: URL has no host"))


class TestHtmlToText(unittest.TestCase):
    def test_strips_tags_scripts_and_unescapes(self):
        html_doc = "<html><style>.x{}</style><body><h1>Title</h1>" \
                   "<script>evil()</script><p>Caf&eacute; &amp; tea</p></body></html>"
        text = " ".join(_html_to_text(html_doc).split())
        self.assertIn("Title", text)
        self.assertIn("Café & tea", text)
        self.assertNotIn("evil()", text)
        self.assertNotIn("<", text)


if __name__ == "__main__":
    unittest.main()
