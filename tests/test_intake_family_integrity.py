"""Version2 intake invariants on frozen synthetic fixtures; no external collection."""
from contextlib import ExitStack
from datetime import datetime, timezone
import copy, hashlib, json, os, shutil, socket, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import tsep
from adapters import captures, comparison_intake, inspection_intake, monitoring_intake, structured_intake, intake_integrity, replay
ROOT=Path(__file__).resolve().parents[1]
class Clock(datetime):
    day=12
    @classmethod
    def now(cls,tz=None):return cls(2026,10,cls.day,12,tzinfo=timezone.utc)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def fixture(name,id):
    p=ROOT/'tests/fixtures'/name
    assert sha(p)==p.with_suffix('.sha256').read_text().strip()
    return copy.deepcopy(next(c['input']['targets'][0] for c in json.loads(p.read_bytes())['cases'] if c['id']==id))
def setup(kind,root):
    prepared=root/'prepared';review=root/'supplied.json';closure=None
    if kind=='comparison':
        t=fixture('canonical-comparison-v1.json','canonical-comparison-v1-qualified-agreement')
        rec=t.pop('inspection_records')[0];docs=t.pop('documents');q=t.pop('comparison_reviews')[0]
        write(root/'plan.json',t);write(root/'documents.json',docs)
        obs=root/'native';obs.mkdir()
        for k in ('request','response'):(obs/(k+'.json')).write_bytes(rec[k]['raw_text'].encode('utf-8'))
        write(obs/'manifest.json',dict(kind='tsep-url-inspection-observation',format_version='1',provenance='synthetic-exercise',description='Authored API files',retrieved_at=rec['retrieved_at'],http_status=200,change=None,request_sha256=sha(obs/'request.json'),response_sha256=sha(obs/'response.json')))
        comparison_intake.prepare(root/'plan.json',[obs],root/'documents.json',prepared)
        r=tsep.read_json(prepared/'review-request.json');q['binding_sha256']=r['reviews'][0]['binding_sha256'];r['reviews']=[q]
        module=comparison_intake
    elif kind=='monitoring':
        t=fixture('release-monitoring-v1.json','release-monitoring-v1-complete-cycle')
        reviews=t.pop('monitoring_reviews');q=t.pop('monitoring_closure_review')
        evidence={k:t.pop(k) for k in ('monitoring_deployment','monitoring_checkpoints')}
        write(root/'plan.json',t);write(root/'evidence.json',evidence)
        monitoring_intake.prepare(root/'plan.json',root/'evidence.json',prepared)
        r=tsep.read_json(prepared/'review-request.json');r['reviews']=reviews;write(review,r)
        monitoring_intake.closure_request(prepared,review,root/'closure')
        c=tsep.read_json(root/'closure/closure-request.json');c['review']=q;closure=root/'closure.json';write(closure,c)
        module=monitoring_intake
    else:
        t=fixture('structured-content-v1.json','structured-content-v1-complete')
        full=copy.deepcopy(t['structured_reviews']);t['structured_reviews']=[{k:r[k] for k in ('surface_id','content')} for r in full]
        write(root/'target.json',t);structured_intake.prepare(root/'target.json',prepared)
        r=tsep.read_json(prepared/'review-request.json');r['reviews']=full;module=structured_intake
    write(review,r)
    return module,prepared,review,closure

@unittest.skipUnless(os.environ.get('TSEP_SOURCE_NODE'),'Explicit Node24 required for all three intake baselines')
class IntakeFamilyIntegrity(unittest.TestCase):
    def run_case(self,kind,change=None,error=None):
        with tempfile.TemporaryDirectory() as tmp,ExitStack() as stack:
            root=Path(tmp)
            stack.enter_context(patch.object(Clock,'day',10 if kind=='comparison' else 12))
            for m in (captures,comparison_intake,inspection_intake,monitoring_intake,structured_intake):stack.enter_context(patch.object(m,'datetime',Clock))
            stack.enter_context(patch.object(socket,'socket',side_effect=AssertionError('No external collection')))
            module,prepared,review,closure=setup(kind,root)
            before={str(f.relative_to(prepared)):f.read_bytes() for f in (prepared/'originals').rglob('*') if f.is_file()}
            meta=tsep.read_json(prepared/'intake.json');sup=tsep.read_json(review)
            if change:change(root,prepared,review,closure,meta,sup)
            write(prepared/'intake.json',meta);write(review,sup)
            output=root/'bundle'
            def build():
                return module.build(prepared,review,output,'AUTOMATED SYNTHETIC EXERCISE',closure) if closure else module.build(prepared,review,output,'AUTOMATED SYNTHETIC EXERCISE')
            if error:
                with self.assertRaisesRegex((ValueError,OSError),error):build()
                self.assertFalse(output.exists())
            else:
                original=intake_integrity.regular;reads=[]
                def once(path,*args):
                    if Path(path).name=='input.json':reads.append(str(path))
                    return original(path,*args)
                with patch.object(intake_integrity,'regular',side_effect=once):build()
                self.assertEqual(len(reads),1)
                self.assertEqual(tsep.read_json(output/'report.json')['results'][0]['status'],'C')
                self.assertTrue(replay.replay(output,root/'replay')['replayed'])
            self.assertEqual(before,{str(f.relative_to(prepared)):f.read_bytes() for f in (prepared/'originals').rglob('*') if f.is_file()})
    def all_paths(self,change=None,error=None):
        for kind in ('comparison','structured','monitoring'):
            with self.subTest(kind=kind):self.run_case(kind,change,error)
    def test_coherent_once_read_and_offline_replay(self):self.all_paths()
    def test_missing_input_inventory(self):
        self.all_paths(lambda r,p,q,c,m,s:m['files'].pop('input.json'),'inventory')
    def test_false_global_pointer(self):
        def change(r,p,q,c,m,s):
            m['input_sha256']='0'*64;s['input_sha256']='0'*64
            if c:
                v=tsep.read_json(c);v['input_sha256']='0'*64;write(c,v)
        self.all_paths(change,'raw input bytes')
    def test_foreign_review(self):
        self.all_paths(lambda r,p,q,c,m,s:s.update(input_sha256='0'*64),'Reviews do not bind')
    def test_unlisted_file(self):
        self.all_paths(lambda r,p,q,c,m,s:(p/'extra.txt').write_text('extra'),'Unlisted')
    def test_changed_original_detected(self):
        # Change a prepared input instead of rewriting the retained native fixture.
        self.all_paths(lambda r,p,q,c,m,s:(p/'input.json').write_text('{}'),'Changed intake file')
    def test_rehashed_input_disagrees_with_original(self):
        def change(r,p,q,c,m,s):
            v=tsep.read_json(p/'input.json');v['targets'][0]['context']['tool']='changed'
            write(p/'input.json',v);h=sha(p/'input.json');m['input_sha256']=h;m['files']['input.json']=h;s['input_sha256']=h
        self.all_paths(change,'original')
    def test_old_intake_requires_explicit_prepare(self):
        self.all_paths(lambda r,p,q,c,m,s:m.update(version='1'),'new v2')
    def test_old_review_refused(self):
        self.all_paths(lambda r,p,q,c,m,s:s.update(version='1'),'Reviews do not bind')
    def test_noncanonical_path_and_digest(self):
        for name in ('./input.json','INPUT.json','../input.json','originals/caf\u00e9.json','originals/cafe\u0301.json'):
            with self.subTest(path=name):self.all_paths(lambda r,p,q,c,m,s:m['files'].update({name:'0'*64}),'Unsafe')
        self.all_paths(lambda r,p,q,c,m,s:m['files'].update({'input.json':'A'*64}),'digest')
    def test_file_and_parent_symlinks(self):
        def change(r,p,q,c,m,s):
            original=r/'input-copy.json';shutil.copyfile(p/'input.json',original);(p/'input.json').unlink();(p/'input.json').symlink_to(original)
        self.all_paths(change,'outside|symlink|regular')
        def parent(r,p,q,c,m,s):
            shutil.move(str(p/'originals'),str(r/'native-copy'));(p/'originals').symlink_to(r/'native-copy',target_is_directory=True)
        # Original bytes are still readable unchanged through the link in the test only.
        self.all_paths(parent,'outside|symlink')
    def test_changed_blank_request(self):
        def change(r,p,q,c,m,s):
            v=tsep.read_json(p/'review-request.json');v['reviews']=[];write(p/'review-request.json',v);m['files']['review-request.json']=sha(p/'review-request.json')
        self.all_paths(change,'blank')
    def test_monitoring_foreign_closure_version(self):
        def change(r,p,q,c,m,s):
            v=tsep.read_json(c);v['version']='1';write(c,v)
        self.run_case('monitoring',change,'Reviews do not bind')
if __name__=='__main__':unittest.main()
