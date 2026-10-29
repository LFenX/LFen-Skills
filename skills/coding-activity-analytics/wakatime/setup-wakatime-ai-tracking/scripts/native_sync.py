"""Pin an explicitly requested manual sync to verified existing native state."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

from deploy_tracking import standard_paths, sync_status, CLI_NAMES

def native_context(profile, plugin):
    profile,resources=standard_paths(profile)
    if sync_status(profile)!='existing':
        raise RuntimeError('Fresh device floor has not been initialized; no historical import.')
    config=profile/'.wakatime.cfg'
    binary=resources/CLI_NAMES[0]
    if not config.is_file() or not binary.is_file():
        raise RuntimeError('Native config or installed CLI is missing.')
    if not plugin or '\n' in plugin or '\r' in plugin:
        raise RuntimeError('Use the actual installed collector plugin identifier.')
    env=dict(os.environ)
    env['WAKATIME_HOME']=str(resources)
    command=[str(binary),'--sync-ai-heartbeats','--plugin',plugin,
             '--config',str(config),'--internal-config',str(resources/'wakatime-internal.cfg')]
    return command,env

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile',type=Path,required=True)
    parser.add_argument('--plugin',required=True)
    parser.add_argument('--send',action='store_true',help='Upload actual new local activity; without this flag only validate context')
    args=parser.parse_args()
    try:
        command,env=native_context(args.profile,args.plugin)
        if not args.send:
            print(json.dumps({'status':'validated','cli_executed':False,'state_aligned':True}));return 0
        # No retry after timeout or uncertain network effects. CLI output can
        # contain private paths; retain neither stdout nor stderr in the report.
        result=subprocess.run(command,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=180)
        print(json.dumps({'status':'command_finished','exit_code':result.returncode,'cloud_received':'requires_readback'}))
        return result.returncode
    except subprocess.TimeoutExpired:
        print('SYNC TIMEOUT: preserve state; verify actual effects before another upload.',file=sys.stderr);return 2
    except (RuntimeError,OSError,ValueError):
        print('SYNC BLOCKED: native paths or progress are invalid; nothing reset or retried.',file=sys.stderr);return 2

if __name__=='__main__': raise SystemExit(main())
