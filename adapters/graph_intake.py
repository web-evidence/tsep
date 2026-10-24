"""TS18 original transport guard; no review, acquisition or repair."""
from conformance.graph_reconciliation import transport
from adapters.incoming_links_intake import verify_target as verify_documents

def verify_target(target,version):
    transport(target)
    if type(target) is dict:
        verify_documents({'incoming_links':{'documents':target.get('graph_documents')}},version)
