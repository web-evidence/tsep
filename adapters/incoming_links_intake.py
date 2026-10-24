"""TS16 transport guard; no native verdict or digest repair."""
import base64
import binascii
import hashlib

import tsep
from conformance.evaluate import binding_digest
from conformance.http import raw_bytes, Unknown


def verify_dom(document):
    render = document.get('render')
    states = render.get('states') if isinstance(render, dict) else None
    if not isinstance(states, list):
        return
    for state in states:
        structured = state.get('structured_dom') if isinstance(state, dict) else None
        if not isinstance(structured, dict):
            continue
        snapshot, declared = structured.get('snapshot'), structured.get('snapshot_sha256')
        if snapshot is not None and declared is not None:
            try:
                actual = binding_digest(snapshot)
            except (TypeError, ValueError, UnicodeError) as error:
                raise tsep.Invalid('TS16 DOM integrity: unhashable supplied snapshot') from error
            tsep.require(isinstance(declared, str) and declared == actual,
                         'TS16 DOM integrity: snapshot self-fingerprint mismatch')
        acquisition = structured.get('acquisition')
        support = acquisition.get('support') if isinstance(acquisition, dict) else None
        if not isinstance(support, list):
            continue
        for item in support:
            if not isinstance(item, dict):
                continue
            content, declared = item.get('content'), item.get('sha256')
            if isinstance(content, str) and declared is not None:
                try:
                    actual = hashlib.sha256(content.encode('utf-8')).hexdigest()
                except UnicodeError as error:
                    raise tsep.Invalid('TS16 DOM integrity: unhashable supplied support') from error
                tsep.require(isinstance(declared, str) and declared == actual,
                             'TS16 DOM integrity: support self-fingerprint mismatch')


def verify_target(target, input_version):
    """Check supplied originals even without a plan or matching document/state ID.

    Missing/null evidence remains a native qualification concern. Present malformed
    original containers or inconsistent self-digests refuse transport. Association
    hashes and plan chronology are not self-digests and remain native concerns.
    """
    incoming = target.get('incoming_links')
    if not isinstance(incoming, dict):
        return
    inventory = incoming.get('inventory')
    if isinstance(inventory, dict) and inventory.get('base64') is not None:
        encoded = inventory['base64']
        tsep.require(type(encoded) is str and len(encoded) <= 4*((131072+2)//3),
                     'TS16 inventory integrity: invalid or excessive byte container')
        try:
            original = base64.b64decode(encoded, validate=True)
        except (ValueError, binascii.Error) as error:
            raise tsep.Invalid('TS16 inventory integrity: invalid base64') from error
        tsep.require(len(original) <= 131072 and base64.b64encode(original).decode('ascii') == encoded,
                     'TS16 inventory integrity: noncanonical or excessive bytes')
        declared = inventory.get('sha256')
        if declared is not None:
            tsep.require(type(declared) is str and declared == hashlib.sha256(original).hexdigest(),
                         'TS16 inventory integrity: original self-fingerprint mismatch')
    documents = incoming.get('documents')
    if not isinstance(documents, list):
        return
    for document in documents:
        if not isinstance(document, dict):
            continue
        hops = document.get('http')
        tsep.require(hops is None or (type(hops) is list and all(type(h) is dict for h in hops)),
                     'TS16 HTTP structure: expected exchange objects or absent/null evidence')
        for hop in hops or []:
            for field in ('request', 'response'):
                if isinstance(hop.get(field), dict):
                    tsep.require(input_version == '2', 'Binary HTTP records require input_version2')
                    try:
                        raw_bytes(hop[field])
                    except Unknown as error:
                        raise tsep.Invalid('HTTP evidence integrity error: '+str(error)) from error
        verify_dom(document)
