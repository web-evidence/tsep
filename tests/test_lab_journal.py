"""Deterministic publication/interleaving checks, never real browser evidence."""
import http.client
import io
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.parse import urlsplit

from examples import same_navigation_lab as lab
from examples import source_browser_lab


class AtomicLaboratoryJournal(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.path = self.folder / 'requests.jsonl'
        self.previous = b'{"id" : "previous", "value": 1}\n'
        self.path.write_bytes(self.previous)
        self.path.chmod(0o640)
        self.row = {'id': 'next', 'value': 'caf\u00e9'}

    def split_writer(self, *, fail=False):
        real_factory = tempfile.NamedTemporaryFile
        testcase = self

        def factory(*args, **kwargs):
            stream = real_factory(*args, **kwargs)

            class SplitWrite:
                name = stream.name

                def __enter__(self):
                    stream.__enter__()
                    return self

                def write(self, data):
                    # Pause publication inside an incomplete new record. The
                    # real unlocked reader must still see the previous bytes.
                    cut = len(testcase.previous) + 7
                    stream.write(data[:cut])
                    stream.flush()
                    testcase.assertEqual(testcase.path.read_bytes(), testcase.previous)
                    testcase.assertEqual(lab.logs(testcase.folder), [{'id': 'previous', 'value': 1}])
                    if fail:
                        raise OSError('injected incomplete write')
                    stream.write(data[cut:])
                    return len(data)

                def __exit__(self, *exc):
                    return stream.__exit__(*exc)

            return SplitWrite()

        return factory

    def assert_no_temporary_file(self):
        self.assertEqual({p.name for p in self.folder.iterdir()}, {'requests.jsonl'})

    def test_readers_see_complete_snapshots_during_split_write(self):
        with patch.object(lab.tempfile, 'NamedTemporaryFile', side_effect=self.split_writer()):
            lab.append_log(self.folder, self.row)
        expected = self.previous + (json.dumps(self.row) + '\n').encode('utf-8')
        self.assertEqual(self.path.read_bytes(), expected)
        self.assertEqual(self.path.stat().st_mode & 0o777, 0o640)
        self.assertEqual(lab.logs(self.folder), [{'id': 'previous', 'value': 1}, self.row])
        self.assert_no_temporary_file()

    def test_failed_write_preserves_previous_bytes_and_cleans_temporary(self):
        with patch.object(lab.tempfile, 'NamedTemporaryFile', side_effect=self.split_writer(fail=True)):
            with self.assertRaisesRegex(OSError, 'incomplete write'):
                lab.append_log(self.folder, self.row)
        self.assertEqual(self.path.read_bytes(), self.previous)
        self.assert_no_temporary_file()

    def test_failed_replace_preserves_previous_bytes_and_cleans_temporary(self):
        with patch.object(lab.os, 'replace', side_effect=OSError('injected replace failure')):
            with self.assertRaisesRegex(OSError, 'replace failure'):
                lab.append_log(self.folder, self.row)
        self.assertEqual(self.path.read_bytes(), self.previous)
        self.assert_no_temporary_file()

    def test_preexisting_corruption_is_never_repaired_or_ignored(self):
        broken = b'{"incomplete":\n'
        self.path.write_bytes(broken)
        lab.append_log(self.folder, self.row)
        self.assertTrue(self.path.read_bytes().startswith(broken))
        with self.assertRaises(json.JSONDecodeError):
            lab.logs(self.folder)
        self.assert_no_temporary_file()

    def test_serialized_writer_threads_preserve_every_record(self):
        lock = threading.Lock()
        ready = threading.Barrier(5)
        errors = []

        def write(index):
            try:
                ready.wait(timeout=5)
                with lock:
                    lab.append_log(self.folder, {'id': index})
            except BaseException as error:
                errors.append(error)

        threads = [threading.Thread(target=write, args=(i,)) for i in range(4)]
        for thread in threads:
            thread.start()
        ready.wait(timeout=5)
        for thread in threads:
            thread.join(timeout=5)
            self.assertFalse(thread.is_alive())
        self.assertEqual(errors, [])
        rows = lab.logs(self.folder)
        self.assertEqual(rows[0], {'id': 'previous', 'value': 1})
        self.assertEqual(sorted(row['id'] for row in rows[1:]), list(range(4)))
        self.assert_no_temporary_file()

    def test_sealing_reads_published_snapshot_not_pending_files(self):
        folder = self.folder / 'laboratory'
        server, record = lab.start(folder)
        self.addCleanup(server.server_close)
        calibration = {'id': 'request-0', 'kind': 'calibration', 'complete': True,
                       'user_agent': 'AUTHORED-TEST/1'}
        with server.lock:
            lab.append_log(folder, calibration)
        # The handler stores both raw files before publishing its journal row.
        (folder/'request-1-request.bin').write_bytes(b'pending authored request')
        (folder/'request-1-response.bin').write_bytes(b'pending authored response')
        real_replace = lab.os.replace

        def seal_before_publication(source, destination):
            self.assertTrue(Path(source).is_file())
            self.assertEqual(lab.logs(folder), [calibration])
            plan = lab.seal(folder, 'AUTHORED TEST, NOT A BROWSER', '1')
            self.assertEqual(plan['calibration_id'], 'request-0')
            self.assertNotIn(Path(source).name, json.dumps(plan))
            self.assertNotIn('request-1', json.dumps(plan))
            real_replace(source, destination)

        with server.lock, patch.object(lab.os, 'replace', side_effect=seal_before_publication):
            lab.append_log(folder, {'id': 'request-1', 'kind': 'browser-favicon', 'complete': True})
        self.assertEqual(len(lab.logs(folder)), 2)
        self.assertEqual(list(folder.glob('.requests-*.tmp')), [])

    def test_handler_publication_failure_prevents_closed_evidence(self):
        folder = self.folder / 'failed-handler'
        server, record = source_browser_lab.start(folder)
        self.assertFalse(server.daemon_threads)
        self.assertTrue(server.block_on_close)
        self.assertEqual((folder/'requests.jsonl').read_bytes(), b'')
        handled = threading.Event()
        normal_error = server.handle_error

        def record_error(request, address):
            try:
                normal_error(request, address)
            finally:
                handled.set()

        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with patch.object(server, 'handle_error', side_effect=record_error), \
                    patch.object(lab.os, 'replace', side_effect=OSError('injected publication failure')), \
                    patch('sys.stderr', new_callable=io.StringIO) as errors:
                address = urlsplit(record['base'])
                connection = http.client.HTTPConnection('127.0.0.1', address.port, timeout=5)
                try:
                    connection.request('GET', address.path, headers={
                        'Host': address.netloc, 'User-Agent': 'AUTHORED-TRANSPORT/1'})
                    response = connection.getresponse()
                    self.assertEqual(response.status, 200)
                    response.read()
                finally:
                    connection.close()
                self.assertTrue(handled.wait(5), 'Handler did not report publication failure')
                self.assertIn('injected publication failure', errors.getvalue())
            server.shutdown()
            thread.join(timeout=5)
            self.assertFalse(thread.is_alive())
            with self.assertRaisesRegex(OSError, 'retention failed'):
                source_browser_lab.close(server)
            self.assertFalse((folder/'closed.json').exists())
            with self.assertRaises(FileNotFoundError):
                source_browser_lab.analyze(folder)
            self.assertEqual(lab.logs(folder), [])
            self.assertEqual(list(folder.glob('.requests-*.tmp')), [])
        finally:
            if thread.is_alive():
                server.shutdown()
                thread.join(timeout=5)
            # Bypass only the expected refusal to close for test cleanup.
            lab.socketserver.ThreadingTCPServer.server_close(server)


if __name__ == '__main__':
    unittest.main()
