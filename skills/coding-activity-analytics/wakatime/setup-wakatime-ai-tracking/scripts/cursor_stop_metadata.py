"""Capture allowlisted Cursor stop metadata locally; never upload payloads."""
import hashlib
import argparse
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
from contextlib import closing
from datetime import datetime, timezone

TOKEN_FIELDS=('input_tokens','output_tokens','cache_read_tokens','cache_write_tokens')

def clean_slug(value):
    if not isinstance(value,str) or not re.fullmatch(r'[A-Za-z0-9._:/-]{1,128}',value):return None
    if re.search(r'wakatime_|sk-|api[_-]?key|https?://|[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}',value,re.I):return None
    return value

def opaque(value):
    return hashlib.sha256(str(value).encode('utf-8')).hexdigest() if value else None

def normalize(payload,recorded_at=None):
    if not isinstance(payload,dict) or payload.get('hook_event_name') not in (None,'stop'):return None
    client=payload.get('_agent_type')
    if client and str(client).lower() not in ('cursor','cursor-agent'):return None
    if not payload.get('cursor_version') and not client:return None
    tokens={k:payload[k] if isinstance(payload.get(k),int) and not isinstance(payload.get(k),bool) and 0<=payload[k]<10**15 else None for k in TOKEN_FIELDS}
    generation=opaque(payload.get('generation_id'))
    conversation=opaque(payload.get('conversation_id') or payload.get('session_id'))
    result={'schema_version':1,'tool':'Cursor','recorded_at':recorded_at or datetime.now(timezone.utc).isoformat(),
            'model':clean_slug(payload.get('model')),'provider':clean_slug(payload.get('provider')),
            'client_version':clean_slug(payload.get('cursor_version')),
            'conversation_hash':conversation,'generation_hash':generation,
            'raw_token_counts':tokens,'token_fields_present':any(v is not None for v in tokens.values()),
            'coverage':'parent_turn_only','input_cache_convention':'unverified; raw fields retained separately',
            'source':'Cursor stop hook; no conversation content captured'}
    seed=[conversation,generation,result['model'],tokens]
    if not generation:seed.append(result['recorded_at'])
    result['event_id']=hashlib.sha256(json.dumps(seed,sort_keys=True).encode()).hexdigest()
    result['generation_dedup_available']=bool(generation)
    return result

def store(record,directory):
    directory.mkdir(parents=True,exist_ok=True)
    with closing(sqlite3.connect(directory/'cursor-stop-metadata.sqlite3',timeout=2)) as db:
        db.execute('CREATE TABLE IF NOT EXISTS events (event_id TEXT PRIMARY KEY, recorded_at TEXT NOT NULL, metadata TEXT NOT NULL)')
        db.execute('INSERT OR IGNORE INTO events VALUES (?,?,?)',(record['event_id'],record['recorded_at'],json.dumps(record,ensure_ascii=False)))
        db.commit()

def main():
    try:
        parser=argparse.ArgumentParser()
        parser.add_argument('--directory',type=Path,default=Path.home()/'.wakatime')
        args=parser.parse_args()
        raw=sys.stdin.buffer.read(4*1024*1024+1)
        if len(raw)>4*1024*1024:return
        encoding='utf-16' if raw.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8-sig'
        record=normalize(json.loads(raw.decode(encoding)))
        if record:
            # WAKATIME_HOME is a resources directory in the CLI. Never append
            # another .wakatime or inherit a divergent hook environment.
            store(record,args.directory.resolve())
    except Exception:
        # Telemetry cannot block the user's agent or echo private input.
        pass
    finally:
        print('{}')

if __name__=='__main__':main()
