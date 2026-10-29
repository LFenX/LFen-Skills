"""Local Windows deployment. Never execute the collector or upload activity."""
import argparse
import configparser
from contextlib import closing
import ctypes
from ctypes import wintypes
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import sqlite3
import subprocess
import sys
import tempfile
import time

from build_collector import BASE, PATCH_SHA, BUILD_ID

SKILL = Path(__file__).resolve().parents[1]
CLI_NAMES = ('wakatime-cli-windows-amd64.exe','wakatime-cli.exe')
STATE_NAME = 'lfen-tracking-deployment'

def digest(data):
    return hashlib.sha256(data).hexdigest()

def read(path):
    return path.read_bytes() if path.is_file() else None

def parse_ini(data):
    parser=configparser.RawConfigParser(strict=True)
    try: parser.read_string((data or b'').decode('utf-8-sig'))
    except (ValueError,UnicodeError,configparser.Error):
        raise RuntimeError('Unsupported INI syntax; no automatic rewrite.') from None
    return parser

def merge_ini(data, section, values):
    """Replace only owned scalar options; preserve every unrelated byte/section."""
    parse_ini(data)
    text=(data or b'').decode('utf-8-sig')
    newline='\r\n' if '\r\n' in text else '\n'
    headers=list(re.finditer(r'(?m)^\[([^\]\r\n]+)\][ \t]*(?:\r?\n|$)',text))
    match=next((m for m in headers if m.group(1)==section),None)
    if match:
        end=next((m.start() for m in headers if m.start()>match.start()),len(text))
        body=text[match.end():end]
        for key in values:
            body=re.sub(r'(?im)^[ \t]*'+re.escape(key)+r'[ \t]*=[^\r\n]*(?:\r?\n|$)','',body)
        if body and not body.endswith(('\r','\n')): body+=newline
        body+=''.join(f'{k} = {v}'+newline for k,v in values.items())
        text=text[:match.end()]+body+text[end:]
    else:
        text+=('' if not text or text.endswith(('\r','\n')) else newline)+'['+section+']'+newline
        text+=''.join(f'{k} = {v}'+newline for k,v in values.items())
    result=(b'\xef\xbb\xbf' if data and data.startswith(b'\xef\xbb\xbf') else b'')+text.encode('utf-8')
    before,after=parse_ini(data),parse_ini(result)
    for parser in (before,after):
        if parser.has_section(section):
            for key in values: parser.remove_option(section,key)
        if parser.has_section(section) and not dict(parser.items(section)): parser.remove_section(section)
    if {s:dict(before.items(s)) for s in before.sections()}!={s:dict(after.items(s)) for s in after.sections()}:
        raise RuntimeError('Unrelated configuration would change.')
    return result

def timestamp(value):
    try:
        result=datetime.fromisoformat(value.replace('Z','+00:00'))
        if result.tzinfo is None: raise ValueError()
        if result>datetime.now(timezone.utc): raise ValueError()
        return result
    except (TypeError,ValueError,AttributeError):
        raise RuntimeError('Invalid or future native sync timestamp.') from None

def sync_status(profile):
    resource=profile/'.wakatime'
    internal=resource/'wakatime-internal.cfg'
    checkpoint=resource/'wakatime-internal-ai-parsing.json'
    ini=parse_ini(read(internal))
    floor=ini.get('internal','ai_logs_last_parsed_at',fallback='')
    if not floor and not checkpoint.exists():
        # Any native queue on an alleged fresh device needs separate recovery.
        if any(any(folder.glob(pattern)) for folder in (resource,profile) for pattern in
               ('wakatime*.db*','offline_heartbeats.bdb*','.wakatime.bdb*')):
            raise RuntimeError('Existing offline queue: fresh initialization refused.')
        return 'fresh'
    if not floor or not checkpoint.is_file():
        raise RuntimeError('Incomplete existing native progress; no initialization or rewind.')
    at=timestamp(floor)
    try: state=json.loads(checkpoint.read_text(encoding='utf-8'))
    except (OSError,ValueError,UnicodeError):
        raise RuntimeError('Unreadable checkpoint; preserve it and stop.') from None
    if not isinstance(state,dict) or state.get('version')!=1 or not isinstance(state.get('parsers'),dict):
        raise RuntimeError('Unsupported native checkpoint.')
    if not any(abs((at-timestamp(state[k])).total_seconds())<0.000002
               for k in ('global','previous_global') if state.get(k)):
        raise RuntimeError('INI and checkpoint disagree; automatic rewind refused.')
    return 'existing'

def standard_paths(profile):
    profile=Path(profile).resolve()
    if not profile.is_dir(): raise RuntimeError('Profile directory must already exist.')
    if os.environ.get('WAKATIME_HOME'):
        raise RuntimeError('Custom WAKATIME_HOME detected; verify native paths manually first.')
    resources=profile/'.wakatime'
    cursor=profile/'.cursor'
    for path in (resources,cursor):
        if path.resolve()!=path or not path.resolve().is_relative_to(profile):
            raise RuntimeError('Redirected resources are outside this standard-path installer.')
    for path in (profile/'.wakatime.cfg',cursor/'hooks.json',resources/STATE_NAME,
                 *(resources/n for n in CLI_NAMES),resources/'cursor-stop-metadata.py',
                 resources/'cursor-stop-metadata.cmd',resources/'cursor-stop-metadata.sqlite3',
                 resources/'wakatime-internal.cfg',resources/'wakatime-internal-ai-parsing.json'):
        if path.resolve()!=path:
            raise RuntimeError('Redirected managed files require manual routing verification.')
    return profile,resources

def require_windows():
    if os.name!='nt' or platform.machine().lower() not in ('amd64','x86_64'):
        raise RuntimeError('Automated deployment supports Windows x64 only.')

class Blob(ctypes.Structure):
    _fields_=[('size',wintypes.DWORD),('data',ctypes.POINTER(ctypes.c_ubyte))]

def seal(data, decrypt=False):
    crypt=ctypes.WinDLL('crypt32',use_last_error=True)
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.LocalFree.argtypes=[wintypes.HLOCAL]
    kernel.LocalFree.restype=wintypes.HLOCAL
    buffer=ctypes.create_string_buffer(data)
    source=Blob(len(data),ctypes.cast(buffer,ctypes.POINTER(ctypes.c_ubyte)))
    target=Blob()
    if decrypt:
        fn=crypt.CryptUnprotectData
        fn.argtypes=[ctypes.POINTER(Blob),ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,wintypes.DWORD,ctypes.POINTER(Blob)]
        ok=fn(ctypes.byref(source),None,None,None,None,1,ctypes.byref(target))
    else:
        fn=crypt.CryptProtectData
        fn.argtypes=[ctypes.POINTER(Blob),wintypes.LPCWSTR,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,wintypes.DWORD,ctypes.POINTER(Blob)]
        ok=fn(ctypes.byref(source),'WakaTime device-local deployment',None,None,None,1,ctypes.byref(target))
    if not ok: raise RuntimeError('Device-local encrypted backup failed.')
    try: return ctypes.string_at(target.data,target.size)
    finally: kernel.LocalFree(ctypes.cast(target.data,wintypes.HLOCAL))

def atomic(path, data):
    path.parent.mkdir(parents=True,exist_ok=True)
    stage=path.with_name(path.name+'.lfen-stage')
    with stage.open('xb') as stream:
        stream.write(data);stream.flush();os.fsync(stream.fileno())
    try: os.replace(stage,path)
    finally:
        if stage.is_file(): stage.unlink()

def write_known(path, desired, expected):
    """Bounded Windows sharing-error recovery, only while exact effects are known."""
    for delay in (0,0.05,0.1,0.2,0.4,0.8):
        if delay: time.sleep(delay)
        actual=read(path)
        if actual==desired: return
        if actual!=expected:
            raise RuntimeError('Managed file changed concurrently; preserve and stop.')
        try:
            if desired is None: path.unlink()
            else: atomic(path,desired)
            if read(path)!=desired: raise RuntimeError('Managed write effect could not be verified.')
            return
        except PermissionError:
            # Unlike an unknown HTTP mutation, a failed local operation has a
            # readable exact before/after state. Never retry over a new value.
            continue
    raise RuntimeError('Managed file is unavailable; preserve journal and pause producers before recovery.')

def cursor_config(data, command):
    try: obj=json.loads((data or b'{"version":1,"hooks":{}}').decode('utf-8-sig'))
    except (ValueError,UnicodeError): raise RuntimeError('Unsupported Cursor hooks JSON.') from None
    if not isinstance(obj,dict) or obj.get('version',1)!=1 or not isinstance(obj.get('hooks',{}),dict):
        raise RuntimeError('Unsupported Cursor hook schema.')
    stops=obj.setdefault('hooks',{}).setdefault('stop',[])
    if not isinstance(stops,list): raise RuntimeError('Unsupported Cursor stop entries.')
    if any('cursor-stop-metadata' in str(entry) for entry in stops):
        raise RuntimeError('An existing Cursor metadata hook needs explicit migration; no duplicate added.')
    stops.append({'command':command})
    obj.setdefault('version',1)
    return (json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode('utf-8')

def artifact_binary(manifest):
    try: record=json.loads(Path(manifest).read_text(encoding='utf-8'))
    except (ValueError,UnicodeError): raise RuntimeError('Invalid local build manifest.') from None
    if any(record.get(k)!=v for k,v in {'schema_version':1,'upstream_commit':BASE,'patch_sha256':PATCH_SHA,'build_id':BUILD_ID,'platform':'windows-amd64','isolated_tests':'passed','binary':'wakatime-cli-windows-amd64.exe','go_version':'go version go1.27.3 windows/amd64'}.items()):
        raise RuntimeError('Unsupported or unverified build manifest.')
    binary=Path(manifest).resolve().parent/record['binary']
    content=binary.read_bytes()
    if digest(content)!=record.get('binary_sha256'): raise RuntimeError('Built binary digest mismatch.')
    return content,record

def plan(profile, manifest, cursor=False, fresh=False, hostname=None, grok_version=None):
    require_windows()
    profile,resources=standard_paths(profile)
    binary,build=artifact_binary(manifest)
    config=profile/'.wakatime.cfg'
    selected=parse_ini(read(config))
    if selected.get('settings','import_cfg',fallback='') or any(selected.has_section(s) and dict(selected.items(s)) for s in ('api_urls','project_api_key')):
        raise RuntimeError('Imported or project-specific credential routing needs manual verification.')
    alternative=Path(os.environ.get('XDG_CONFIG_HOME') or profile/'.config')/'wakatime/wakatime.cfg'
    if not config.exists() and alternative.exists():
        raise RuntimeError('Existing XDG config would be shadowed; verify actual native routing first.')
    status=sync_status(profile)
    if status=='fresh' and not fresh: raise RuntimeError('New device requires --fresh-device to set a current-time floor.')
    if status=='existing' and fresh: raise RuntimeError('Existing progress must be preserved; omit --fresh-device.')
    now=datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
    options={'ai_tool_identity':'true','ai_strict_patch_paths':'true'}
    if hostname:
        if not re.fullmatch(r'[A-Za-z0-9._-]{1,64}',hostname): raise RuntimeError('Use an explicit simple, unique machine name.')
        options['hostname']=hostname
    if grok_version:
        if not re.fullmatch(r'\d+(?:\.\d+){1,3}',grok_version): raise RuntimeError('Invalid measured Grok Bot software version.')
        options['ai_grok_bot_version']=grok_version
    writes={resources/name:binary for name in CLI_NAMES}
    initial={}
    if cursor:
        wrapper=resources/'cursor-stop-metadata.cmd'
        if wrapper.exists() or (resources/'cursor-stop-metadata.py').exists():
            raise RuntimeError('Unmanaged metadata launcher already exists; explicit migration required.')
        for value in (str(sys.executable),str(resources)):
            if any(c in value for c in ('"','%','\r','\n')): raise RuntimeError('Unsupported shell-sensitive executable/profile path.')
        command=subprocess.list2cmdline([str(wrapper)])
        options.update(ai_cursor_stop_metadata=(resources/'cursor-stop-metadata.sqlite3').as_posix(),ai_cursor_stop_since=now)
        writes[resources/'cursor-stop-metadata.py']=(SKILL/'scripts/cursor_stop_metadata.py').read_bytes()
        writes[wrapper]=('@echo off\r\n"'+sys.executable+'" -B -X utf8 "%~dp0cursor-stop-metadata.py" --directory "%~dp0."\r\n').encode('utf-8')
        hook_path=profile/'.cursor/hooks.json'
        writes[hook_path]=cursor_config(read(hook_path),command)
        journal=resources/'cursor-stop-metadata.sqlite3'
        if journal.exists():
            try:
                with closing(sqlite3.connect('file:'+journal.as_posix()+'?mode=ro',uri=True)) as db:
                    columns={r[1] for r in db.execute('PRAGMA table_info(events)')}
                if not {'event_id','recorded_at','metadata'}.issubset(columns): raise ValueError()
            except (sqlite3.Error,ValueError):
                raise RuntimeError('Existing metadata journal schema is incompatible; preserve and stop.') from None
        else:
            with tempfile.TemporaryDirectory(prefix='waka-empty-journal-') as tmp:
                path=Path(tmp)/'journal.sqlite3'
                with closing(sqlite3.connect(path)) as db:
                    db.execute('CREATE TABLE events (event_id TEXT PRIMARY KEY, recorded_at TEXT NOT NULL, metadata TEXT NOT NULL)')
                    db.commit()
                initial[journal]=path.read_bytes()
    writes[config]=merge_ini(read(config),'settings',options)
    if status=='fresh':
        internal=resources/'wakatime-internal.cfg'
        initial[internal]=merge_ini(read(internal),'internal',{'ai_logs_last_parsed_at':now})
        initial[resources/'wakatime-internal-ai-parsing.json']=(json.dumps({'version':1,'global':now,'previous_global':now,'parsers':{}},indent=2)+'\n').encode()
    # Never replace private journals or queues. Initial floor/journal remain on
    # rollback to avoid rewinding progress after real events have been collected.
    return {'profile':profile,'writes':writes,'initial':initial,'options':options,'cursor_command':command if cursor else None,'build':build,'sync_mode':status,'floor':now if status=='fresh' else None}

def save(state, record):
    atomic(state/'deployment.json',(json.dumps(record,indent=2)+'\n').encode('utf-8'))

def installed(profile, state, manifest):
    record=json.loads((state/'deployment.json').read_text(encoding='utf-8'))
    _,build=artifact_binary(manifest)
    if record['status']!='applied' or record['build_sha256']!=build['binary_sha256']:
        raise RuntimeError('Existing deployment is incomplete or differs; inspect and roll back first.')
    changed=False
    for entry in record['files']:
        path=managed_path(profile,entry['path'])
        actual=read(path)
        if entry['path']=='.wakatime.cfg':
            parser=parse_ini(actual)
            if any(parser.get('settings',k,fallback=None)!=v for k,v in record['options'].items()):
                raise RuntimeError('Owned WakaTime options changed; no silent overwrite.')
        elif entry['path']=='.cursor/hooks.json':
            obj=json.loads(actual.decode('utf-8-sig')) if actual else {}
            if sum(isinstance(h,dict) and h.get('command')==record['cursor_command'] for h in obj.get('hooks',{}).get('stop',[]))!=1:
                raise RuntimeError('Cursor hook registration changed.')
        elif actual is None or digest(actual)!=entry['after']:
            raise RuntimeError('Installed artifact changed; inspect before reapplying.')
        changed|=(actual is None or digest(actual)!=entry['after'])
    sync_status(profile)
    return {'status':'already_installed','cloud_activity_uploaded':False,'rollback_requires_config_merge':changed}

def managed_path(profile, relative):
    allowed={'.wakatime.cfg','.cursor/hooks.json',*('.wakatime/'+n for n in CLI_NAMES),'.wakatime/cursor-stop-metadata.py','.wakatime/cursor-stop-metadata.cmd'}
    path=profile/relative
    if relative not in allowed or path.resolve()!=path or not path.is_relative_to(profile):
        raise RuntimeError('Manifest target is outside managed files.')
    return path

def install(profile, manifest, cursor=False, fresh=False, hostname=None, grok_version=None):
    require_windows()
    profile,resources=standard_paths(profile)
    state=resources/STATE_NAME
    if (state/'deployment.json').exists():
        record=json.loads((state/'deployment.json').read_text(encoding='utf-8'))
        if (cursor and not record.get('cursor_command')) or any(value and record.get('options',{}).get(key)!=value for key,value in [('hostname',hostname),('ai_grok_bot_version',grok_version)]):
            raise RuntimeError('Requested options differ from this deployment; explicit migration required.')
        return installed(profile,state,manifest)
    prepared=plan(profile,manifest,cursor,fresh,hostname,grok_version)
    if state.exists(): raise RuntimeError('Unfinished deployment directory; inspect before retry.')
    state.mkdir(parents=True)
    record={'schema_version':1,'status':'prepared','build_sha256':prepared['build']['binary_sha256'],
            'options':prepared['options'],'cursor_command':prepared['cursor_command'],
            'sync_mode':prepared['sync_mode'],'fresh_floor':prepared['floor'],
            'files':[],'applied':[],'initializations_preserved_on_rollback':[]}
    before={p:read(p) for p in prepared['writes']}
    initial_before={p:read(p) for p in prepared['initial']}
    for index,(path,content) in enumerate(prepared['writes'].items()):
        original=before[path]
        if original is not None:
            encrypted=seal(original)
            if seal(encrypted,True)!=original: raise RuntimeError('Encrypted backup did not round-trip.')
            (state/f'{index}.dpapi').write_bytes(encrypted)
        record['files'].append({'path':path.relative_to(profile).as_posix(),'before':digest(original) if original is not None else None,'after':digest(content)})
    save(state,record)
    for path,original in {**before,**initial_before}.items():
        if read(path)!=original: raise RuntimeError('A collector changed files during preparation; stop producers before deployment.')
    record['status']='applying';save(state,record)
    # Commit a crash-recovery intent before each write. Recovery checks actual
    # before/after digests, including a crash between a write and journal update.
    for index,(path,content) in enumerate(prepared['writes'].items()):
        record['applied'].append(index);save(state,record)
        write_known(path,content,before[path])
    for path,content in prepared['initial'].items():
        if read(path)!=initial_before[path]: raise RuntimeError('Initial progress changed concurrently; preserve and stop.')
        write_known(path,content,initial_before[path])
        record['initializations_preserved_on_rollback'].append(path.relative_to(profile).as_posix());save(state,record)
    record['status']='applied';save(state,record)
    result=installed(profile,state,manifest)
    result.update(status='installed',sync_mode=prepared['sync_mode'],fresh_floor_set=bool(prepared['floor']),network_requests=0)
    return result

def rollback(profile):
    require_windows()
    profile,resources=standard_paths(profile)
    state=resources/STATE_NAME
    record=json.loads((state/'deployment.json').read_text(encoding='utf-8'))
    if record['status']=='rolled_back': return {'status':'already_rolled_back'}
    restorations=[]
    for index in reversed(record['applied']):
        entry=record['files'][index]
        path=managed_path(profile,entry['path'])
        actual=read(path)
        value=digest(actual) if actual is not None else None
        if value==entry['before']: continue
        if value!=entry['after']: raise RuntimeError('A managed file changed after installation; merge manually, never overwrite it.')
        original=seal((state/f'{index}.dpapi').read_bytes(),True) if entry['before'] is not None else None
        if original is not None and digest(original)!=entry['before']: raise RuntimeError('Backup digest mismatch.')
        restorations.append((path,original,actual))
    record['status']='rolling_back';save(state,record)
    for path,original,expected in restorations:
        write_known(path,original,expected)
    record['status']='rolled_back';save(state,record)
    return {'status':'rolled_back','checkpoints_and_journal_preserved':True,'cloud_activity_uploaded':False}

def inspect(profile):
    profile,resources=standard_paths(profile)
    try: status=sync_status(profile)
    except RuntimeError: status='blocked_state_needs_inspection'
    state=resources/STATE_NAME/'deployment.json'
    return {'platform':platform.system()+'-'+platform.machine(),'python':platform.python_version(),
            'standard_profile':True,'sync_state':status,'config_present':(profile/'.wakatime.cfg').is_file(),
            'cli_present':{n:(resources/n).is_file() for n in CLI_NAMES},
            'deployment_present':state.is_file(),'cloud_activity_uploaded':False,'cli_executed':False}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['inspect','plan','install','rollback'])
    parser.add_argument('--profile',type=Path,required=True)
    parser.add_argument('--manifest',type=Path)
    parser.add_argument('--fresh-device',action='store_true')
    parser.add_argument('--cursor',action='store_true')
    parser.add_argument('--hostname')
    parser.add_argument('--grok-bot-version',help='Software version measured from this device, never a model version')
    parser.add_argument('--collectors-stopped',action='store_true',help='Required for install/rollback; confirm producers are paused')
    args=parser.parse_args()
    try:
        if args.action=='inspect': result=inspect(args.profile)
        elif args.action=='rollback':
            if not args.collectors_stopped: raise RuntimeError('Pause collectors first.')
            result=rollback(args.profile)
        else:
            if not args.manifest: raise RuntimeError('--manifest is required.')
            if args.action=='install':
                if not args.collectors_stopped: raise RuntimeError('Pause collectors first.')
                result=install(args.profile,args.manifest,args.cursor,args.fresh_device,args.hostname,args.grok_bot_version)
            else:
                prepared=plan(args.profile,args.manifest,args.cursor,args.fresh_device,args.hostname,args.grok_bot_version)
                result={'status':'planned','sync_mode':prepared['sync_mode'],'managed_file_count':len(prepared['writes']),'current_time_floor_planned':bool(prepared['floor']),'network_requests':0,'profile_modified':False}
        print(json.dumps(result,ensure_ascii=False))
        return 0
    except (OSError,ValueError,KeyError,TypeError,configparser.Error,RuntimeError) as exc:
        # Error messages from our own validation are fixed text. Do not echo
        # parser/OS exceptions containing credentials or private config lines.
        message=str(exc) if type(exc) is RuntimeError else 'Local state could not be read; preserve it and inspect locally.'
        print(json.dumps({'status':'blocked','reason':message,'cloud_activity_uploaded':False}),file=sys.stderr)
        return 2

if __name__=='__main__': raise SystemExit(main())
