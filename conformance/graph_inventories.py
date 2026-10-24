"""Supplied native inventory reader; not a standalone TS18 verdict.

Never guesses dialect/columns, repairs originals or asserts independence.
"""
import base64
import binascii
import csv
import hashlib
import io
from pathlib import Path
from conformance import sitemap_files

RAW_LIMIT = 1048576
ROW_LIMIT = 128


class IntegrityError(ValueError):
    pass


class Unqualified(ValueError):
    pass


def need(ok, reason):
    if not ok:
        raise Unqualified(reason)


def original(record):
    need(type(record) is dict, 'Original record missing')
    encoded = record.get('base64')
    need(encoded is not None, 'Original byte container missing')
    if type(encoded) is not str or len(encoded) > 4*((RAW_LIMIT+2)//3):
        raise IntegrityError('Invalid/excessive original byte container')
    try:
        raw = base64.b64decode(encoded, validate=True)
    except (ValueError, binascii.Error) as error:
        raise IntegrityError('Invalid base64 original') from error
    if len(raw) > RAW_LIMIT or base64.b64encode(raw).decode('ascii') != encoded:
        raise IntegrityError('Noncanonical/excessive original byte container')
    declared = record.get('sha256')
    actual = hashlib.sha256(raw).hexdigest()
    if declared is not None and (type(declared) is not str or actual != declared):
        raise IntegrityError('Original self-fingerprint mismatch')
    need(declared is not None, 'Original self-fingerprint missing')
    need(record.get('complete') is True, 'Original completeness missing or false')
    return raw


def csv_urls(raw, policy):
    need(type(policy) is dict and set(policy) == {'delimiter','encoding','quotechar','doublequote','header_row','url_column'},
         'Exact explicit CSV dialect and URL mapping required')
    need(policy['delimiter'] in (',',';') and policy['encoding'] in ('utf-8','utf-8-sig')
         and policy['quotechar'] == '"' and policy['doublequote'] is True
         and type(policy['header_row']) is int and policy['header_row'] == 1
         and type(policy['url_column']) is str and bool(policy['url_column']),
         'Unsupported declared CSV dialect; no automatic retry')
    if raw.startswith(b'\xef\xbb\xbf'):
        need(policy['encoding'] == 'utf-8-sig', 'Undeclared CSV UTF-8 BOM')
    text = raw.decode(policy['encoding'])
    need('\x00' not in text, 'NUL outside CSV profile')
    reader = csv.reader(io.StringIO(text, newline=''), delimiter=policy['delimiter'],
                        quotechar=policy['quotechar'], doublequote=True, strict=True)
    header = next(reader, None)
    need(header is not None and 1 <= len(header) <= 32 and all(header)
         and len(set(header)) == len(header) and policy['url_column'] in header,
         'Missing/ambiguous declared URL column')
    column = header.index(policy['url_column']); urls = []
    for row in reader:
        need(len(urls) < ROW_LIMIT and len(row) == len(header), 'CSV row or column bound/shape unqualified')
        need(all(len(cell) <= 65536 for cell in row), 'CSV field outside bound')
        value = row[column]
        need(0 < len(value) <= 4096 and value == value.strip(), 'Missing/padded URL cell')
        urls.append(value)
    need(len(set(urls)) == len(urls), 'Repeated URL rows are not silently deduplicated')
    return urls


def sitemap_urls(raw, policy):
    need(type(policy) is dict and set(policy) == {'encoding'} and policy['encoding'] in ('identity','gzip'),
         'Explicit supported sitemap encoding required')
    reading = sitemap_files.read_native(raw, policy['encoding'], True)
    need(reading['format'] == 'pass' and reading['limits'] == 'pass' and reading['kind'] == 'urlset'
         and reading.get('xml_complete') is True, 'Native TS15 sitemap reader could not qualify a complete URLset')
    urls = reading['locations']
    need(len(urls) <= ROW_LIMIT and len(set(urls)) == len(urls), 'Sitemap population exceeds bound or repeats URLs')
    return urls


def read(record, format, policy):
    result = {'qualified':False,'authenticates_origin':False,'url_semantics_checked':False,
              'format':format,'urls':[]}
    try:
        raw = original(record)
        result['original_sha256'] = hashlib.sha256(raw).hexdigest()
        if format == 'csv':
            urls = csv_urls(raw, policy)
        elif format == 'sitemap':
            urls = sitemap_urls(raw, policy)
            result['reader'] = {'module':'conformance/sitemap_files.py',
                'sha256':hashlib.sha256(Path(sitemap_files.__file__).read_bytes()).hexdigest()}
        else:
            raise Unqualified('Unsupported original format')
        result.update(qualified=True,urls=urls,reason='Complete bounded original read with explicit format; URL and provenance qualification remains separate')
    except (Unqualified, UnicodeError, csv.Error, sitemap_files.IntakeError) as error:
        result['reason'] = str(error)
    return result
