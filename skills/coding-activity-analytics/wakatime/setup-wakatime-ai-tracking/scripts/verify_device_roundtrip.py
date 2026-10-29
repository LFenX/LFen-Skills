"""Exercise the built collector on a disposable Windows device and loopback API."""
import argparse
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import threading

from deploy_tracking import install, rollback, sync_status
from native_sync import native_context

def verify(manifest):
    received=[]
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args): pass
        def do_POST(self):
            raw=self.rfile.read(int(self.headers.get('Content-Length',0)))
            rows=json.loads(raw)
            if isinstance(rows,dict): rows=[rows]
            received.extend(rows)
            body=json.dumps({'responses':[[{'data':{'id':'00000000-0000-4000-8000-000000000001'}},201] for _ in rows]}).encode()
            self.send_response(201);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        with tempfile.TemporaryDirectory(prefix='waka-roundtrip-') as tmp:
            root=Path(tmp).resolve();profile=root/'Device 用户 Home';profile.mkdir()
            project=profile/'Local Project Without Git';project.mkdir()
            entity=project/'main.py';entity.write_text("print('fixture')\n",encoding='utf-8')
            config=profile/'.wakatime.cfg'
            mapping=re.escape(project.as_posix()).replace(':',r'\x3a')+'(/|$)'
            config.write_text('[settings]\napi_key = 00000000-0000-4000-8000-000000000000\napi_url = http://127.0.0.1:'+str(server.server_port)+'\ndebug = false\n[projectmap]\n'+mapping+' = LocalExample\n',encoding='utf-8')
            install(profile,manifest,cursor=True,fresh=True,hostname='home-fixture')
            floor=(profile/'.wakatime/wakatime-internal-ai-parsing.json').read_bytes()
            assert install(profile,manifest,cursor=True,fresh=True,hostname='home-fixture')['status']=='already_installed'
            assert floor==(profile/'.wakatime/wakatime-internal-ai-parsing.json').read_bytes()
            sessions=profile/'.codex/sessions';sessions.mkdir(parents=True)
            def row(at,kind,payload): return {'timestamp':at.isoformat().replace('+00:00','Z'),'type':kind,'payload':payload}
            def lines(rows): return ''.join(json.dumps(r)+'\n' for r in rows)
            at=datetime.now(timezone.utc)
            old=at-timedelta(days=1)
            (sessions/'old.jsonl').write_text(lines([
                row(old,'session_meta',{'id':'old-fixture','cwd':project.as_posix(),'cli_version':'0.163','source':'vscode'}),
                row(old,'turn_context',{'turn_id':'old-turn','model':'gpt-6-astra','effort':'xhigh'}),
                row(old,'event_msg',{'type':'user_message','message':'old fixture must not upload'})]),encoding='utf-8')
            opening=[row(at,'session_meta',{'id':'new-fixture','cwd':project.as_posix(),'cli_version':'0.163','source':'vscode'}),
                     row(at,'event_msg',{'type':'task_started','turn_id':'new-turn'}),
                     row(at+timedelta(milliseconds=1),'response_item',{'type':'message','role':'user','content':[{'type':'input_text','text':'fixture task'}]})]
            transcript=sessions/'new.jsonl';transcript.write_text(lines(opening),encoding='utf-8')
            def sync():
                command,_=native_context(profile,'synthetic-plugin/1')
                command+=['--log-file',str(root/'synthetic.log'),'--heartbeat-rate-limit-seconds','0']
                env={k:v for k,v in os.environ.items() if k.upper() in {'SYSTEMROOT','WINDIR','SYSTEMDRIVE','COMSPEC','PATHEXT'}}
                env.update(HOME=str(profile),USERPROFILE=str(profile),WAKATIME_HOME=str(profile/'.wakatime'),
                           APPDATA=str(profile/'AppData/Roaming'),LOCALAPPDATA=str(profile/'AppData/Local'),
                           TEMP=str(root),TMP=str(root),WAKATIME_WSL='off',PATH=os.defpath+os.pathsep+str(Path(os.environ.get('SYSTEMROOT','C:/Windows'))/'System32'))
                result=subprocess.run(command,env=env,cwd=project,capture_output=True,timeout=60)
                if result.returncode: raise RuntimeError('Synthetic collector failed; real profile was never used.')
            sync()
            assert not received,'opening with missing model must remain pending'
            complete=[row(at+timedelta(milliseconds=4),'turn_context',{'turn_id':'new-turn','cwd':project.as_posix(),'model':'gpt-6.1-sol','effort':'max'}),
                      row(at+timedelta(milliseconds=5),'response_item',{'type':'custom_tool_call','name':'apply_patch','input':"*** Begin Patch\n*** Add File: main.py\n+print('fixture')\n*** End Patch"}),
                      row(at+timedelta(milliseconds=6),'event_msg',{'type':'token_count','info':{'total_token_usage':{'input_tokens':100,'cached_input_tokens':40,'output_tokens':20}}}),
                      row(at+timedelta(milliseconds=7),'event_msg',{'type':'agent_message','message':'fixture done'})]
            transcript.write_text(lines(opening+complete),encoding='utf-8')
            sync()
            if not received:
                raise AssertionError('completed source missing from mock; synthetic diagnostic: '+(root/'synthetic.log').read_text(encoding='utf-8',errors='replace')[-7500:])
            assert all(r.get('ai_session')=='new-fixture' for r in received),'old history must stay excluded'
            assert all(r.get('project')=='LocalExample' for r in received),'non-Git project association must survive'
            assert all('gpt/6.1-sol-max codex/0.163' in r.get('user_agent','') for r in received),'actor/model must stay separate'
            assert any(r.get('language')=='Python' and r.get('type')=='file' for r in received),'actual file language must be recognized'
            tokens=[sum(r.get(k,0) for r in received) for k in ('ai_input_tokens','ai_cached_input_tokens','ai_output_tokens')]
            assert tokens==[60,40,20],('inclusive input/cache/output',tokens)
            assert all(r.get('time',0)>=at.timestamp() for r in received),'native timestamps must not be backdated'
            first=json.dumps(received,sort_keys=True)
            sync()
            assert first==json.dumps(received,sort_keys=True),'repeat sync must emit no extra heartbeats or tokens'
            assert sync_status(profile)=='existing'
            checkpoint=(profile/'.wakatime/wakatime-internal-ai-parsing.json').read_bytes()
            rollback(profile)
            assert checkpoint==(profile/'.wakatime/wakatime-internal-ai-parsing.json').read_bytes(),'rollback must not rewind collected state'
            return {'status':'passed','endpoint':'loopback_only','synthetic_profile':True,'real_credentials_used':False,
                    'old_activity_uploaded':0,'opening_before_model_uploaded':0,'completed_records':len(received),
                    'repeat_sync_additions':0,'non_git_project':'preserved','file_language':'Python',
                    'actor':'Codex','model_token':'gpt/6.1-sol-max','tokens':tokens,'rollback_preserved_progress':True}
    finally:
        server.shutdown();server.server_close();thread.join(timeout=5)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(verify(args.manifest),ensure_ascii=False))
