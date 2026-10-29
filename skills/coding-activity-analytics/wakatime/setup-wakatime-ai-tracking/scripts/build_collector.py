"""Rebuild the pinned local CLI and run its tests in a synthetic user profile."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tarfile

BASE = '37ab01e6d80dbe9a05f0ee3cd90012e988090c7a'
PATCH_SHA = '50d12b1969a8b780ec57c192a4e187875dad041a9177191b4743f359df9f5608'
BUILD_ID = '37ab01e6-lfen-session-20261029f'
SKILL = Path(__file__).resolve().parents[1]

def sha(data):
    return hashlib.sha256(data).hexdigest()

def isolated_env(root, go, cache=None):
    env = {k:v for k,v in os.environ.items() if k.upper() in
           {'SYSTEMROOT','WINDIR','SYSTEMDRIVE','COMSPEC','PATHEXT','NUMBER_OF_PROCESSORS','PROCESSOR_ARCHITECTURE'}}
    user, temp = root/'user', root/'temp'
    for p in (user, temp, user/'AppData/Roaming', user/'AppData/Local'):
        p.mkdir(parents=True, exist_ok=True)
    env.update(PATH=str(go.parent)+os.pathsep+os.defpath+os.pathsep+str(Path(os.environ.get('SYSTEMROOT','C:/Windows'))/'System32'),
               USERPROFILE=str(user), HOME=str(user), WAKATIME_HOME=str(user/'.wakatime'),
               APPDATA=str(user/'AppData/Roaming'), LOCALAPPDATA=str(user/'AppData/Local'),
               TEMP=str(temp), TMP=str(temp), GOTMPDIR=str(temp), GOTELEMETRY='off',
               GOTOOLCHAIN='local', CGO_ENABLED='0', WAKATIME_WSL='off',
               GOPROXY='https://proxy.golang.org', GOSUMDB='sum.golang.org')
    cache = Path(cache).resolve() if cache else root/'cache'
    env.update(GOMODCACHE=str(cache/'go-modules'), GOCACHE=str(cache/'go-build-cache'), GOPATH=str(cache/'go-path'))
    return env

def execute(args, cwd, env=None):
    r = subprocess.run([str(x) for x in args], cwd=cwd, env=env,
                       capture_output=True, timeout=600)
    if r.returncode:
        (Path(cwd)/'build-error.log').write_bytes(r.stdout+b'\n'+r.stderr)
        raise RuntimeError('Build command failed; see local build logs. No deployment occurred.')
    return r.stdout

def build(source, output, go, cache=None):
    if os.name != 'nt' or platform.machine().lower() not in ('amd64','x86_64'):
        raise RuntimeError('This reproducible deployment supports Windows x64 only.')
    source, output, go = Path(source).resolve(), Path(output).resolve(), Path(go).resolve()
    patch = SKILL/'assets/wakatime-session-20261029.patch'
    if sha(patch.read_bytes()) != PATCH_SHA:
        raise RuntimeError('Packaged patch digest mismatch.')
    if output.exists():
        raise RuntimeError('Use a new empty build destination; do not overwrite previous evidence.')
    output.mkdir(parents=True)
    env = isolated_env(output, go, cache)
    version = execute([go,'version'], output, env).decode().strip()
    if version != 'go version go1.27.3 windows/amd64':
        raise RuntimeError('Pinned source requires the tested Go 1.27.3 windows/amd64 toolchain.')
    # git archive includes only this commit, never dirty files, local logs or credentials.
    archive = execute(['git','-c','core.longpaths=true','-C',source,'archive','--format=tar',BASE], output)
    tree = output/'source'
    tree.mkdir()
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        for member in tar.getmembers():
            target = (tree/member.name).resolve()
            if not target.is_relative_to(tree) or member.issym() or member.islnk():
                raise RuntimeError('Unsafe archive member.')
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            elif member.isfile():
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(tar.extractfile(member).read())
            else:
                raise RuntimeError('Unsupported archive member.')
    execute(['git','apply','--check',patch], tree)
    execute(['git','apply',patch], tree)
    # All session providers resolve under the synthetic home; none inherit the
    # invoking user's Codex/Cursor/Claude directories or API configuration.
    with (output/'go-tests.jsonl').open('wb') as log:
        r = subprocess.run([str(go),'test','-json','./pkg/ai','./cmd/heartbeat','-count=1'],
                           cwd=tree,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=600)
    passed, failed = 0, []
    for line in (output/'go-tests.jsonl').read_text(encoding='utf-8',errors='replace').splitlines():
        try: event=json.loads(line)
        except ValueError: continue
        if event.get('Action')=='pass' and event.get('Test'): passed+=1
        if event.get('Action')=='fail': failed.append(event.get('Test',event.get('Package')))
    if r.returncode or failed or not passed:
        raise RuntimeError('Isolated Go tests failed; no deployable manifest created.')
    binary = output/'wakatime-cli-windows-amd64.exe'
    flags = '-s -w -X github.com/wakatime/wakatime-cli/pkg/version.Commit='+BUILD_ID+' -X github.com/wakatime/wakatime-cli/pkg/version.Version=<local-build> -X github.com/wakatime/wakatime-cli/pkg/version.OS=windows -X github.com/wakatime/wakatime-cli/pkg/version.Arch=amd64'
    execute([go,'build','-buildvcs=false','-trimpath','-ldflags',flags,'-o',binary,'.'],tree,env)
    probe_config=output/'probe.cfg'
    probe_config.write_text('[settings]\napi_url = http://127.0.0.1:9\ndebug = false\n',encoding='utf-8')
    actual=execute([binary,'--config',probe_config,'--version'],output,env).decode().strip()
    if actual != '<local-build>':
        raise RuntimeError('Unexpected CLI version marker.')
    record={'schema_version':1,'upstream_commit':BASE,'patch_sha256':PATCH_SHA,
            'build_id':BUILD_ID,'go_version':version,'platform':'windows-amd64',
            'binary':binary.name,'binary_sha256':sha(binary.read_bytes()),
            'isolated_tests':'passed','passed_test_events':passed,
            'real_profile_used':False,'cloud_activity_uploaded':False}
    (output/'build.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    return record

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True,help='Local official wakatime-cli Git checkout containing the pinned commit')
    parser.add_argument('--output',type=Path,required=True,help='New scratch directory outside the installed skill')
    parser.add_argument('--go',type=Path,required=True,help='Absolute path of Go 1.27.3 go.exe')
    parser.add_argument('--cache',type=Path,help='Optional build-cache root; contains no user telemetry')
    args=parser.parse_args()
    try: print(json.dumps(build(args.source,args.output,args.go,args.cache)))
    except (OSError,ValueError,RuntimeError,subprocess.SubprocessError):
        print('BUILD FAILED: no deployment or real profile access; inspect scratch build evidence.',file=sys.stderr)
        return 2
    return 0

if __name__=='__main__': raise SystemExit(main())
