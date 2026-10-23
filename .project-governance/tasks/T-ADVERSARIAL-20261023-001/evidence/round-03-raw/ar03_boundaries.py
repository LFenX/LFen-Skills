from ar03_extended import *
RESULTS.clear();RESULTS.extend(json.loads((OUT/'results.json').read_text(encoding='utf-8')))

def boundary_suite():
    for carrier in ['Full','Minimal']:
        root,task=ready(carrier,'boundary-'+carrier)
        offer(task,carrier+'-boundary-offer');decision(task,'Accepted',carrier+'-boundary-optin')
        future=(datetime.now(timezone.utc)+timedelta(hours=1)).isoformat()
        invalid=[
            ('future-event',{'recorded_at':future}),
            ('naive-time',{'recorded_at':'2026-10-23T00:00:00'}),
            ('missing-report',{'report_ref':str(task/'evidence/no-file.md')}),
            ('outside-report',{'report_ref':str(OUT/'run-metadata.json')}),
            ('unknown-resolution',{'resolutions':[{'finding_id':'absent','disposition':'NotAnIssue','reason':'No matching finding','evidence_refs':['ar03://bad-resolution']}]}),
            ('invented-derived-binding',{'delivery_verified_at':'2026-01-01T00:00:00Z'}),
            ('unknown-review-contract',{'review_contract_version':'future-protocol-v999'}),
        ]
        for name,kw in invalid:entry(task,round_record(task,carrier+'-'+name,**kw),carrier+'-'+name,2)
        empty=round_record(task,carrier+'-empty-report');Path(empty['report_ref']).write_bytes(b'\n \t');entry(task,empty,carrier+'-empty-report',2)
        rec=round_record(task,carrier+'-boundary-clean');entry(task,rec,carrier+'-boundary-clean',expected=lambda p:p['clean_streak']==1)
        sameid=round_record(task,carrier+'-sameid');sameid['round_id']=rec['round_id'];entry(task,sameid,carrier+'-duplicate-round-id',2)
        finding={'id':'DUP-ID','summary':'First fixture finding','evidence_refs':['ar03://duplicate-finding']}
        entry(task,round_record(task,carrier+'-duplicate-findings',findings=[finding,copy.deepcopy(finding)]),carrier+'-duplicate-findings',2)
        # Unknown delivery and unrelated tasks cannot be used as substitutes.
        other=new_task(root,'T-UNRELATED',2,project_id=task_parts(task)[3]['project_id']);finish_full(other)
        entry(task,round_record(task,carrier+'-unrelated-delivery',delivery=other),carrier+'-unrelated-delivery',2)
        # Existing authority for engineering acceptance is independent from opt-in.
        if carrier=='Full':
            cli('amend_record.py',[task/'before.json','--path','clarification.basis','--value-json','"Correction to survey explanation only"','--reason','AR03 survey metadata correction','--basis','surveyed.md'],carrier+'-survey-metadata-corrected')
            state(task,carrier+'-survey-metadata-keeps-streak',lambda p:p['clean_streak']==1)
        # Reports remain independent files, while supporting evidence may be reused.
        entry(task,round_record(task,carrier+'-boundary-clean-2'),carrier+'-boundary-clean-2',expected=lambda p:p['status']=='Passed')
        # Legacy representations are isolated compatibility fixtures, not proof of actual old human activity.
        legacy_root=OUT/('legacy-untracked-'+carrier);shutil.copytree(root,legacy_root)
        legacy=legacy_root/'.project-governance/tasks/T-PARENT';path,doc,out,_,_=task_parts(legacy);out.pop('adversarial_review');save(path,doc)
        state(legacy,carrier+'-legacy-untracked',lambda p:p['status']=='LegacyUntracked' and p['clean_streak']==0)
        entry(legacy,{'event':'Offer','recorded_at':stamp(),'prompt':'Do not enroll legacy fixture automatically','evidence_ref':'ar03://legacy'},carrier+'-legacy-no-auto-enrollment',2)
        # Prepare a legitimate old two-round representation. Original files are never altered.
        old_root=OUT/('legacy-rounds-'+carrier);shutil.copytree(root,old_root)
        old=old_root/'.project-governance/tasks/T-PARENT';path,doc,out,con,_=task_parts(old)
        for item in out['adversarial_review']:
            if item['event']=='Round':
                for key in ['review_contract_version','report_ref','report_sha256','delivery_completed_at','delivery_verified_at']:item.pop(key,None)
                item['requirements_sha256']=ar._legacy_requirements_subject(con)
        save(path,doc)
        state(old,carrier+'-legacy-pair-not-current-pass',lambda p:p['status']=='LegacyNotRevalidated' and p['clean_streak']==0)
        entry(old,round_record(old,carrier+'-legacy-no-auto-restart'),carrier+'-legacy-no-auto-restart',2)
        # Public generated Markdown must include state and delivery details; no console UI is asserted.
        proc=cli('generate_review_views.py',['--project-root',root,'--project-id',task_parts(task)[3]['project_id']],carrier+'-generate-review-views')[1]
        generated=[Path(x) for x in proc.stdout.splitlines() if x.strip()]
        view_text='\n'.join(p.read_text(encoding='utf-8') for p in generated if p.is_file() and p.suffix=='.md')
        record_case(carrier+'-review-markdown-visible',{'generated_paths':list(map(str,generated))},'generated Markdown includes adversarial status Passed and delivery',{'has_review': 'Adversarial review:' in view_text,'has_passed':'Passed' in view_text,'has_current_delivery':'current_delivery' in view_text},'Adversarial review:' in view_text and 'Passed' in view_text and 'current_delivery' in view_text)
    print('boundary/legacy complete',len(RESULTS),flush=True)

def unfinished_suite():
    for carrier in ['Full','Minimal']:
        root=OUT/('unfinished-'+carrier);root.mkdir();(root/'src').mkdir();(root/'src/label.txt').write_text('label=v1',encoding='utf-8')
        if carrier=='Full':
            task=new_task(root,'T-NOT-DONE',1)
        else:
            task=minimal_fixture_record(root,'T-NOT-DONE').parent
        before=hashlib.sha256((task/('before.json' if carrier=='Full' else 'task-record.json')).read_bytes()).hexdigest()
        entry(task,{'event':'Offer','recorded_at':stamp(),'prompt':'Synthetic premature offer','evidence_ref':'ar03://too-early'},carrier+'-no-saved-engineering-result',2)
        after=hashlib.sha256((task/('before.json' if carrier=='Full' else 'task-record.json')).read_bytes()).hexdigest()
        record_case(carrier+'-early-offer-preserves-record',{'task':str(task)},'rejected offer leaves source record unchanged',{'sha_before':before,'sha_after':after},before==after)
        if carrier=='Full':
            con=g.read_json(task/'before.json');g.amend_record(task/'before.json',dotted_path='requirement_items',new_value=source_review(con),reason='AR03 fixture disclosure',basis='src/label.txt')
            g.append_run_event(task,run_id='R-BLOCK',attempt_id='A-BLOCK',event_type='run_started',summary='Synthetic fixture stopped before delivery',status='started')
            g.append_run_event(task,run_id='R-BLOCK',attempt_id='A-BLOCK',event_type='run_finished',summary='Synthetic fixture environment blocked',status='blocked')
            g.close_task(task,status='Blocked',established_facts=['Synthetic environmental blocker'],actual_changes=[],verification=[{'result':'Blocked','summary':'No verified delivery','evidence_refs':['ar03://blocked']}])
        else:
            con=g.read_json(task/'task-record.json')['task_contract'];m.record_minimal_review(task,requirement_items=source_review(con),reason='AR03 fixture disclosure',basis='src/label.txt')
            m.append_minimal_event(task,event_type='run_started',summary='Synthetic fixture started',status='started')
            m.close_minimal_record(task,status='Blocked',established_facts=['Synthetic environmental blocker'],actual_changes=[],verification=['Blocked::No verified delivery::ar03://blocked'])
        state(task,carrier+'-nonimplemented-notapplicable',lambda p:p['status']=='NotApplicable' and p['clean_streak']==0)
        entry(task,{'event':'Offer','recorded_at':stamp(),'prompt':'Synthetic offer despite incomplete delivery','evidence_ref':'ar03://notapplicable'},carrier+'-nonimplemented-offer-refused',2)
    print('unfinished complete',len(RESULTS),flush=True)

if __name__=='__main__':
    try:boundary_suite();unfinished_suite()
    except Exception:
        (OUT/'final-suite-exception.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
    finally:save(OUT/'results.json',RESULTS)
