"""Supplied documentary review linkage. Never authenticates a reviewer or judgment."""
import hashlib
import json
import tsep

FIELDS={'subject','binding_sha256','reviewer','reviewed_at','disposition','rationale','synthetic'}


def named(v):return type(v) is str and bool(v.strip()) and len(v)<=4096


def binding(material):
    return hashlib.sha256(json.dumps(material,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()


def need(ok,reason):
    if not ok:raise ValueError(reason)


def read(subjects,reviews,observed_at,synthetic):
    result={'outcome':'inconclusive','authenticates_reviewer':False,'adjudicates_rationale':False,'subjects':[],
            'scope':'Completeness and linkage of supplied documentary qualification only.'}
    try:
        observed=tsep.timestamp(observed_at)
        need(type(synthetic) is bool,'Explicit provenance required')
        need(type(subjects) is list and 1<=len(subjects)<=64,'Nonempty bounded native-derived subject population required')
        need(all(type(s) is dict and named(s.get('id')) and type(s.get('qualified')) is bool and type(s.get('binding_material')) is dict for s in subjects),'Unqualified native-derived subject structure')
        need(len({s['id'] for s in subjects})==len(subjects),'Duplicate native-derived subjects')
        need(type(reviews) is list and len(reviews)<=128,'Bounded supplied review list required')
    except (ValueError,TypeError,KeyError,OverflowError) as error:
        result['reason']=str(error);return result
    expected_ids={s['id'] for s in subjects}
    result['unplanned_review_subjects']=sorted({r['subject'] for r in reviews if type(r) is dict and type(r.get('subject')) is str and r['subject'] not in expected_ids})
    for s in subjects:
        row={'subject':s['id'],'outcome':'inconclusive'}
        try:
            need(s['qualified'],'Supporting native measurements remain unqualified; review cannot cure missing evidence')
            earliest=tsep.timestamp(s['earliest_review_at'])
            need(earliest<=observed,'Supporting chronology unqualified')
            material=s['binding_material'];need(len(json.dumps(material,ensure_ascii=False,allow_nan=False).encode())<=1048576,'Subject binding exceeds bound')
            row['expected_binding_sha256']=binding(material)
            matches=[r for r in reviews if type(r) is dict and r.get('subject')==s['id']]
            need(len(matches)==1,'Required review missing or ambiguous')
            review=matches[0]
            need(set(review)==FIELDS,'Supplied review shape outside the closed profile')
            need(type(review['binding_sha256']) is str and review['binding_sha256']==row['expected_binding_sha256'],'Review does not bind current originals and subject measurements')
            need(named(review['reviewer']) and named(review['rationale']),'Named supplied reviewer and reason required')
            need(type(review['synthetic']) is bool and review['synthetic']==synthetic,'Review provenance differs from dossier')
            need(earliest<=tsep.timestamp(review['reviewed_at'])<=observed,'Review predates support or postdates observation')
            need(review['disposition'] in ('explained','defect','unresolved'),'Unsupported supplied disposition')
            row.update(outcome={'explained':'pass','defect':'fail','unresolved':'inconclusive'}[review['disposition']],
                       reviewer=review['reviewer'],rationale=review['rationale'],disposition=review['disposition'],
                       reason='Supplied documentary disposition, not authenticated judgment')
        except (ValueError,TypeError,KeyError,OverflowError,UnicodeError) as error:row['reason']=str(error)
        result['subjects'].append(row)
    outcomes=[r['outcome'] for r in result['subjects']]
    result['outcome']='fail' if 'fail' in outcomes else 'inconclusive' if 'inconclusive' in outcomes else 'pass'
    result['reason']='Independent qualified supplied defect retained' if result['outcome']=='fail' else 'Every required supplied review linked' if result['outcome']=='pass' else 'Missing or unqualified review/support remains visible'
    return result
