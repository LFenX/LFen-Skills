import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from contextlib import closing

from cursor_stop_metadata import normalize,store

class CursorMetadataTests(unittest.TestCase):
    def fixture(self,**extra):
        return {'hook_event_name':'stop','cursor_version':'1.128','conversation_id':'fixture-session','generation_id':'fixture-turn','model':'composer-2.5',**extra}

    def test_missing_is_distinct_from_zero(self):
        self.assertIsNone(normalize(self.fixture())['raw_token_counts']['input_tokens'])
        zero=normalize(self.fixture(input_tokens=0))
        self.assertEqual(zero['raw_token_counts']['input_tokens'],0)
        self.assertTrue(zero['token_fields_present'])

    def test_keeps_raw_cache_fields_without_guessing(self):
        r=normalize(self.fixture(input_tokens=1000,output_tokens=30,cache_read_tokens=700,cache_write_tokens=100))
        self.assertEqual(r['raw_token_counts'],{'input_tokens':1000,'output_tokens':30,'cache_read_tokens':700,'cache_write_tokens':100})
        self.assertEqual(r['coverage'],'parent_turn_only')
        self.assertIn('unverified',r['input_cache_convention'])

    def test_never_persists_prompts_paths_or_credentials(self):
        p=self.fixture(prompt='private-sentinel',text='private-sentinel',workspace_roots=['private-sentinel'],api_key='private-sentinel')
        r=normalize(p)
        self.assertNotIn('private-sentinel',json.dumps(r))
        self.assertNotIn('fixture-session',json.dumps(r))

    def test_generation_deduplicates_windows_double_event(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            store(normalize(self.fixture(),recorded_at='2026-10-29T01:00:00+08:00'),p)
            store(normalize(self.fixture(),recorded_at='2026-10-29T01:00:01+08:00'),p)
            with closing(sqlite3.connect(p/'cursor-stop-metadata.sqlite3')) as db:
                self.assertEqual(db.execute('SELECT count(*) FROM events').fetchone()[0],1)

    def test_does_not_merge_turns_without_generation_id(self):
        p=self.fixture();p.pop('generation_id')
        a=normalize(p,recorded_at='2026-10-29T01:00:00+08:00');b=normalize(p,recorded_at='2026-10-29T01:01:00+08:00')
        self.assertNotEqual(a['event_id'],b['event_id'])
        self.assertFalse(a['generation_dedup_available'])

    def test_rejects_other_clients_bad_counts_and_secret_model(self):
        self.assertIsNone(normalize(self.fixture(_agent_type='grok-build')))
        self.assertIsNone(normalize(self.fixture(hook_event_name='afterFileEdit')))
        self.assertIsNone(normalize(self.fixture(input_tokens=-1,model='sk-private-sentinel'))['model'])
        self.assertIsNone(normalize(self.fixture(input_tokens=True))['raw_token_counts']['input_tokens'])

if __name__=='__main__':unittest.main()
