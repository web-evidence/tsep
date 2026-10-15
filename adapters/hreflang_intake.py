"""TS23 own-original integrity guard; missing evidence remains unknown."""
from conformance.hreflang_reciprocity import integrity

def verify_target(target,version):
    integrity({'input_version':version,'target':target})
