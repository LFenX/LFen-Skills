from ar03_extended import *
RESULTS.clear();RESULTS.extend(json.loads((OUT/'results.json').read_text(encoding='utf-8')))

def main():
    for carrier in ['Full','Minimal']:
        root,task=ready(carrier,'report-identity-'+carrier)
        offer(task,carrier+'-identity-offer');decision(task,'Accepted',carrier+'-identity-accept')
        first=round_record(task,carrier+'-identity-original')
        original_bytes=Path(first['report_ref']).read_bytes()
        original_sha=hashlib.sha256(original_bytes).hexdigest()
        entry(task,first,carrier+'-identity-original',expected=lambda p:p['clean_streak']==1)
        # An ordinary evidence-file correction must not erase the identity already recorded for a round.
        Path(first['report_ref']).write_bytes(original_bytes+b'Correction: report appendix updated after capture.\n')
        state(task,carrier+'-identity-old-report-stale',lambda p:p['status']=='Stale' and p['clean_streak']==0)
        reused=round_record(task,carrier+'-identity-reused')
        Path(reused['report_ref']).write_bytes(original_bytes)
        p,proc=entry(task,reused,carrier+'-identity-reuse-recorded-content',2)
        if proc.returncode==0:
            next_record=round_record(task,carrier+'-identity-fresh-final')
            state_after,_=entry(task,next_record,carrier+'-identity-false-pass',expected=lambda p:p['status']!='Passed')
            path,document,outcome,_,_=task_parts(task)
            summary={'carrier':carrier,'task':str(task),'original_sha256':original_sha,'same_recorded_report_sha256':[x.get('report_sha256') for x in outcome['adversarial_review'] if x.get('event')=='Round'],'final_status':state_after,'artifact':str(path)}
            save(OUT/('report-identity-repro-'+carrier+'.json'),summary)
    save(OUT/'results.json',RESULTS)
if __name__=='__main__':main()
