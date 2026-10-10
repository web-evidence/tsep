"""Offline report presentation: fidelity, evidence integrity and inert content. Apache-2.0."""
import base64
import copy
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import tsep
from adapters.captures import build
from reports.html import render, write


class Document(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.tags, self.links, self.downloads, self.ids, self.text = [], [], {}, [], []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        self.tags.append((tag, values))
        if 'id' in values:
            self.ids.append(values['id'])
        if tag == 'a':
            self.links.append(values.get('href', ''))
            if 'download' in values:
                self.downloads[values['download']] = base64.b64decode(values['href'].split(',', 1)[1], validate=True)

    def handle_data(self, data):
        self.text.append(data)


class HTMLReport(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.data = tsep.read_json(ROOT/'examples/captures/ts01-markers.json')

    def tearDown(self):
        self.temp.cleanup()

    def bundle(self, name='bundle', data=None, access='synthetic', **options):
        source = self.root/(name+'.json')
        source.write_text(json.dumps(data or self.data, ensure_ascii=False), encoding='utf-8')
        output = self.root/name
        build(source, output, assessor='Synthetic author', label='Synthetic HTML test',
              selection_method='Explicit fixture only', access=access, **options)
        return output/'report.json'

    def test_original_bytes_downloads_and_escaped_capture_are_portable(self):
        data = copy.deepcopy(self.data)
        data['targets'][0]['context']['network'] = '</pre><script>alert(1)</script><img src="https://invalid.example/x">'
        path = self.bundle(data=data)
        before = {p.relative_to(path.parent): p.read_bytes() for p in path.parent.rglob('*') if p.is_file()}
        with patch('socket.socket', side_effect=AssertionError('network forbidden')):
            source = render(path, language='fr')
        page = Document(source)
        report = tsep.read_json(path)
        self.assertEqual(page.downloads['current-report.json'], path.read_bytes())
        for artifact in report['artifacts']:
            self.assertEqual(page.downloads['current-'+artifact['id']+'.bin'], (path.parent/artifact['path']).read_bytes())
        self.assertIn('&lt;script&gt;alert(1)&lt;/script&gt;', source)
        self.assertFalse(any(tag in ('script', 'img', 'iframe', 'object') for tag, attrs in page.tags))
        self.assertTrue(all(link.startswith(('#', 'data:application/octet-stream;base64,')) for link in page.links))
        self.assertTrue(any(attrs.get('http-equiv') == 'Content-Security-Policy' and "default-src 'none'" in attrs['content'] for tag, attrs in page.tags))
        self.assertEqual(len(page.ids), len(set(page.ids)))
        self.assertTrue(all(link[1:] in page.ids for link in page.links if link.startswith('#')))
        self.assertIn('Preuves synthétiques présentes', source)
        self.assertEqual(source, render(path, language='fr'))
        self.assertEqual(before, {p.relative_to(path.parent): p.read_bytes() for p in path.parent.rglob('*') if p.is_file()})

    def test_verdicts_and_missing_observations_are_not_recomputed(self):
        for case in ('pass', 'fail', 'partial'):
            path = ROOT/'examples'/case/'report.json'
            source = render(path)
            report = tsep.read_json(path)
            self.assertIn(tsep.validate(report, path.parent)['decision'], source)
            for result in report['results']:
                self.assertIn('class="badge '+result['status']+'"', source)
                for atom in result.get('atomic_results', []):
                    self.assertIn(atom['outcome']+' · ', source)
        path = self.bundle(data=tsep.read_json(ROOT/'examples/captures/ts07-source-only.json'), mode='semiAuto')
        source = render(path)
        self.assertIn('Absent observations (1)', source)
        self.assertIn('TS07-A03', source)
        self.assertNotIn('class="badge C"', source)

    def test_comparison_identifies_same_inputs_not_merely_same_targets(self):
        first = self.bundle('first')
        second = self.bundle('second')
        source = render(second, compare=first, language='fr')
        self.assertIn('Même fichier de captures fourni', source)
        self.assertIn('0 résultats atomiques différents', source)
        page = Document(source)
        self.assertEqual(page.downloads['before-report.json'], first.read_bytes())
        data = copy.deepcopy(self.data)
        data['targets'][0]['intent']['expected_body_sha256'] = '0'*64
        third = self.bundle('third', data=data)
        self.assertIn('Capture identity not established', render(third, compare=first))
        changed_scope = self.bundle('extra-control', selected=['TS01', 'TS02'])
        with self.assertRaisesRegex(tsep.Invalid, 'identical protocol'):
            render(changed_scope, compare=first)

    def test_previous_evidence_access_is_visible_and_binary_bytes_survive(self):
        first = self.bundle('restricted', access='restricted')
        second = self.bundle('public', access='public')
        source = render(second, compare=first)
        self.assertIn('Declared restricted evidence included', source)
        synthetic = self.bundle('synthetic')
        self.assertIn('Synthetic evidence present', render(second, compare=synthetic))
        report = tsep.read_json(first)
        artifact = report['artifacts'][0]
        file = first.parent/artifact['path']
        file.write_bytes(b'\x00\xff\x01')
        artifact['sha256'] = tsep.digest(file)
        first.write_text(json.dumps(report), encoding='utf-8')
        page = Document(render(first))
        self.assertEqual(page.downloads['current-'+artifact['id']+'.bin'], b'\x00\xff\x01')
        self.assertIn('Binary evidence', ''.join(page.text))

    def test_invalid_evidence_and_size_bound_leave_no_html(self):
        path = self.bundle()
        output = self.root/'report.html'
        with patch('reports.html.MAX_EMBED_BYTES', len(path.read_bytes()) + 10):
            with self.assertRaisesRegex(tsep.Invalid, 'exceeds'):
                write(path, output)
        self.assertFalse(output.exists())
        report = tsep.read_json(path)
        (path.parent/report['artifacts'][0]['path']).write_text('tampered')
        with self.assertRaises(tsep.Invalid):
            write(path, output)
        self.assertFalse(output.exists())

    def test_cli_new_output_only_and_gate_is_not_the_exit_status(self):
        path = ROOT/'examples/fail/report.json'
        output = self.root/'failure.html'
        command = [sys.executable, str(ROOT/'tsep.py'), 'html', str(path), '--output', str(output), '--lang', 'fr']
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['sha256'], tsep.digest(output))
        self.assertIn('NO_GO', output.read_text())
        before = output.read_bytes()
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 64)
        self.assertEqual(output.read_bytes(), before)
        link = self.root/'link.html'
        link.symlink_to(self.root/'absent')
        with self.assertRaises(tsep.Invalid):
            write(path, link)
        self.assertFalse((self.root/'absent').exists())


if __name__ == '__main__':
    unittest.main()
