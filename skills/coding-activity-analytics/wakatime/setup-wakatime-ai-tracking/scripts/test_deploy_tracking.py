import configparser
from datetime import datetime, timezone, timedelta
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from contextlib import closing

import build_collector as build
import deploy_tracking as deploy
import native_sync

@unittest.skipUnless(os.name=='nt','Windows-only deployment and DPAPI')
class DeviceDeploymentTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='waka-device-')
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name).resolve()
        self.profile=self.root/'用户 Home Space'
        self.profile.mkdir()
        self.resource=self.profile/'.wakatime'
        self.config=self.profile/'.wakatime.cfg'
        self.built=self.root/'build';self.built.mkdir()
        self.binary=self.built/'wakatime-cli-windows-amd64.exe'
        content=b'synthetic-non-executable-binary'
        self.binary.write_bytes(content)
        self.manifest=self.built/'build.json'
        self.manifest.write_text(json.dumps({'schema_version':1,'upstream_commit':build.BASE,'patch_sha256':build.PATCH_SHA,'build_id':build.BUILD_ID,'platform':'windows-amd64','go_version':'go version go1.27.3 windows/amd64','binary':self.binary.name,'binary_sha256':build.sha(content),'isolated_tests':'passed'}),encoding='utf-8')
        self.env=patch.dict(os.environ,{},clear=False);self.env.start();self.addCleanup(self.env.stop)
        os.environ.pop('WAKATIME_HOME',None)

    def existing(self):
        self.resource.mkdir(exist_ok=True)
        at=(datetime.now(timezone.utc)-timedelta(minutes=1)).isoformat()
        (self.resource/'wakatime-internal.cfg').write_text('[internal]\nai_logs_last_parsed_at = '+at+'\nbackoff_at = old\n',encoding='utf-8')
        (self.resource/'wakatime-internal-ai-parsing.json').write_text(json.dumps({'version':1,'global':at,'previous_global':at,'parsers':{}}),encoding='utf-8')

    def test_plan_and_inspect_have_no_profile_side_effect(self):
        original=b'[settings]\napi_key = private-fixture\n[projectmap]\n^C:/Work(/|$) = LocalApp\n'
        self.config.write_bytes(original)
        before={p.relative_to(self.profile):p.read_bytes() for p in self.profile.rglob('*') if p.is_file()}
        self.assertEqual(deploy.inspect(self.profile)['sync_state'],'fresh')
        plan=deploy.plan(self.profile,self.manifest,cursor=True,fresh=True,hostname='home-test')
        self.assertEqual(plan['sync_mode'],'fresh')
        self.assertEqual(before,{p.relative_to(self.profile):p.read_bytes() for p in self.profile.rglob('*') if p.is_file()})

    def test_fresh_install_idempotence_encrypted_backup_and_rollback(self):
        original=b'\xef\xbb\xbf; keep comment\r\n[settings]\r\napi_key = private-fixture\r\nhostname = old-name\r\n[projectmap]\r\n^C:/Local(/|$) = LocalApp\r\n'
        self.config.write_bytes(original)
        hooks=self.profile/'.cursor/hooks.json';hooks.parent.mkdir()
        previous={'version':1,'unrelated':{'preserve':True},'hooks':{'stop':[{'command':'old-stop'}],'afterFileEdit':[{'command':'old-edit'}]}}
        hooks.write_text(json.dumps(previous),encoding='utf-8');hook_before=hooks.read_bytes()
        with patch('subprocess.run',side_effect=AssertionError('No process execution during install')):
            result=deploy.install(self.profile,self.manifest,cursor=True,fresh=True,hostname='home-test')
        self.assertEqual(result['status'],'installed')
        at=(self.resource/'wakatime-internal-ai-parsing.json').read_bytes()
        self.assertEqual(deploy.sync_status(self.profile),'existing')
        installed=json.loads(hooks.read_text(encoding='utf-8'))
        self.assertEqual(installed['hooks']['stop'][0],previous['hooks']['stop'][0])
        self.assertEqual(installed['hooks']['afterFileEdit'],previous['hooks']['afterFileEdit'])
        self.assertTrue(installed['unrelated']['preserve'])
        self.assertIn(b'api_key = private-fixture',self.config.read_bytes())
        state=self.resource/deploy.STATE_NAME
        self.assertFalse(any(b'private-fixture' in p.read_bytes() for p in state.iterdir()))
        self.assertEqual(deploy.install(self.profile,self.manifest,cursor=True,fresh=True,hostname='home-test')['status'],'already_installed')
        self.assertEqual(at,(self.resource/'wakatime-internal-ai-parsing.json').read_bytes())
        self.assertEqual(deploy.rollback(self.profile)['status'],'rolled_back')
        self.assertEqual(self.config.read_bytes(),original)
        self.assertEqual(hooks.read_bytes(),hook_before)
        self.assertFalse((self.resource/deploy.CLI_NAMES[0]).exists())
        self.assertEqual(at,(self.resource/'wakatime-internal-ai-parsing.json').read_bytes())
        self.assertTrue((self.resource/'cursor-stop-metadata.sqlite3').exists())
        self.assertEqual(deploy.rollback(self.profile)['status'],'already_rolled_back')

    def test_existing_progress_and_queue_bytes_preserved(self):
        self.existing()
        queue=self.resource/'wakatime-offline.db';queue.write_bytes(b'corrupt-fixture-not-opened')
        self.config.write_text('[settings]\napi_key = private-fixture\n',encoding='utf-8')
        before={p.name:p.read_bytes() for p in self.resource.iterdir() if p.is_file()}
        deploy.install(self.profile,self.manifest)
        for name,value in before.items(): self.assertEqual((self.resource/name).read_bytes(),value)
        deploy.rollback(self.profile)
        for name,value in before.items(): self.assertEqual((self.resource/name).read_bytes(),value)

    def test_rollback_stops_before_overwriting_later_user_changes(self):
        deploy.install(self.profile,self.manifest,fresh=True)
        self.config.write_bytes(self.config.read_bytes()+b'; user added local key\n')
        binary=(self.resource/deploy.CLI_NAMES[0]).read_bytes()
        with self.assertRaisesRegex(RuntimeError,'changed after installation'): deploy.rollback(self.profile)
        self.assertEqual(binary,(self.resource/deploy.CLI_NAMES[0]).read_bytes())
        self.assertTrue(self.config.read_bytes().endswith(b'; user added local key\n'))
        self.assertTrue(deploy.install(self.profile,self.manifest)['rollback_requires_config_merge'])

    def test_fresh_state_is_explicit_and_old_queue_blocks_it(self):
        with self.assertRaisesRegex(RuntimeError,'requires --fresh-device'): deploy.plan(self.profile,self.manifest)
        self.resource.mkdir();(self.resource/'wakatime-offline.db').write_bytes(b'old')
        with self.assertRaisesRegex(RuntimeError,'offline queue'): deploy.plan(self.profile,self.manifest,fresh=True)

    def test_missing_corrupt_and_mismatched_state_never_reset(self):
        self.existing()
        state=self.resource/'wakatime-internal-ai-parsing.json'
        for raw in (b'corrupt-fixture',json.dumps({'version':1,'global':'2026-01-01T00:00:00Z','parsers':{}}).encode()):
            state.write_bytes(raw)
            with self.assertRaises(RuntimeError): deploy.plan(self.profile,self.manifest)
            self.assertEqual(state.read_bytes(),raw)
        state.unlink()
        with self.assertRaisesRegex(RuntimeError,'Incomplete'): deploy.plan(self.profile,self.manifest)

    def test_existing_progress_rejects_fresh_flag(self):
        self.existing()
        with self.assertRaisesRegex(RuntimeError,'Existing progress'): deploy.plan(self.profile,self.manifest,fresh=True)

    def test_custom_resource_environment_refused(self):
        os.environ['WAKATIME_HOME']=str(self.profile)
        with self.assertRaisesRegex(RuntimeError,'WAKATIME_HOME'): deploy.plan(self.profile,self.manifest,fresh=True)

    def test_old_hook_is_not_duplicated(self):
        hook=self.profile/'.cursor/hooks.json';hook.parent.mkdir()
        original=b'{"version":1,"hooks":{"stop":[{"command":"some/cursor-stop-metadata.cmd"}]}}'
        hook.write_bytes(original)
        with self.assertRaisesRegex(RuntimeError,'explicit migration'): deploy.plan(self.profile,self.manifest,cursor=True,fresh=True)
        self.assertEqual(hook.read_bytes(),original)

    def test_malformed_configuration_is_preserved_and_not_echoed(self):
        self.config.write_bytes(b'[settings]\napi_key = private-fixture\n[settings]\n')
        original=self.config.read_bytes()
        result=subprocess.run([sys.executable,'-B',str(Path(deploy.__file__)),'plan','--profile',str(self.profile),'--manifest',str(self.manifest),'--fresh-device'],capture_output=True)
        self.assertEqual(result.returncode,2)
        self.assertNotIn(b'private-fixture',result.stdout+result.stderr)
        self.assertEqual(self.config.read_bytes(),original)

    def test_tampered_binary_blocks_deployment(self):
        self.binary.write_bytes(b'changed')
        with self.assertRaisesRegex(RuntimeError,'digest mismatch'): deploy.plan(self.profile,self.manifest,fresh=True)
        self.assertFalse(self.resource.exists())

    def test_real_windows_launcher_paths_spaces_and_unicode(self):
        deploy.install(self.profile,self.manifest,cursor=True,fresh=True)
        hooks=json.loads((self.profile/'.cursor/hooks.json').read_text(encoding='utf-8'))
        command=hooks['hooks']['stop'][0]['command']
        fixture={'hook_event_name':'stop','cursor_version':'3.24.18','conversation_id':'fixture-session','generation_id':'fixture-generation','model':'grok-4.7-xhigh','input_tokens':1000,'output_tokens':20,'cache_read_tokens':600,'cache_write_tokens':0,'prompt':'private-content-fixture','api_key':'private-content-fixture'}
        env=dict(os.environ);env['WAKATIME_HOME']=str(self.root/'divergent')
        for _ in range(2):
            result=subprocess.run(command,input=json.dumps(fixture).encode(),shell=True,capture_output=True,env=env,timeout=10)
            self.assertEqual(result.returncode,0)
            self.assertEqual(result.stdout.strip(),b'{}')
        journal=self.resource/'cursor-stop-metadata.sqlite3'
        with closing(sqlite3.connect('file:'+journal.as_posix()+'?mode=ro',uri=True)) as db:
            rows=db.execute('select metadata from events').fetchall()
        self.assertEqual(len(rows),1)
        self.assertNotIn('private-content-fixture',rows[0][0])
        self.assertNotIn('fixture-session',rows[0][0])
        self.assertFalse((self.root/'divergent').exists())

    def test_manual_sync_pins_native_resources_without_execution(self):
        deploy.install(self.profile,self.manifest,fresh=True)
        with patch('subprocess.run',side_effect=AssertionError('dry run must not execute')):
            command,env=native_sync.native_context(self.profile,'synthetic-plugin/1')
        self.assertEqual(env['WAKATIME_HOME'],str(self.resource))
        self.assertEqual(command[command.index('--config')+1],str(self.config))
        self.assertEqual(command[command.index('--internal-config')+1],str(self.resource/'wakatime-internal.cfg'))

    def test_future_checkpoint_and_manifest_escape_rejected(self):
        self.existing()
        at=(datetime.now(timezone.utc)+timedelta(days=1)).isoformat()
        (self.resource/'wakatime-internal.cfg').write_text('[internal]\nai_logs_last_parsed_at = '+at,encoding='utf-8')
        with self.assertRaisesRegex(RuntimeError,'future'): deploy.sync_status(self.profile)
        with self.assertRaisesRegex(RuntimeError,'outside managed'): deploy.managed_path(self.profile,'../unrelated.txt')

    def test_native_and_legacy_queue_names_block_fresh_without_reading(self):
        for relative in ('.wakatime/offline_heartbeats.bdb','.wakatime/.wakatime.bdb','.wakatime.bdb'):
            queue=self.profile/relative;queue.parent.mkdir(exist_ok=True)
            queue.write_bytes(b'corrupt-fixture')
            with self.assertRaisesRegex(RuntimeError,'offline queue'): deploy.plan(self.profile,self.manifest,fresh=True)
            self.assertEqual(queue.read_bytes(),b'corrupt-fixture')
            queue.unlink()

    def test_existing_credential_routing_and_xdg_are_not_shadowed(self):
        for value in ('[settings]\nimport_cfg = private-source.cfg\n','[settings]\n[project_api_key]\nLocal = private-fixture\n'):
            self.config.write_text(value,encoding='utf-8')
            with self.assertRaisesRegex(RuntimeError,'credential routing'): deploy.plan(self.profile,self.manifest,fresh=True)
            self.assertEqual(self.config.read_text(encoding='utf-8'),value)
        self.config.unlink()
        alt=self.profile/'.config/wakatime/wakatime.cfg';alt.parent.mkdir(parents=True)
        alt.write_text('[settings]\napi_key = private-fixture\n',encoding='utf-8')
        with patch.dict(os.environ,{'XDG_CONFIG_HOME':str(self.profile/'.config')}):
            with self.assertRaisesRegex(RuntimeError,'XDG'): deploy.plan(self.profile,self.manifest,fresh=True)
        self.assertFalse(self.config.exists())

    def test_unknown_launcher_and_bad_journal_are_preserved(self):
        self.resource.mkdir()
        script=self.resource/'cursor-stop-metadata.py';script.write_bytes(b'owned-by-someone-else')
        with self.assertRaisesRegex(RuntimeError,'Unmanaged'): deploy.plan(self.profile,self.manifest,cursor=True,fresh=True)
        self.assertEqual(script.read_bytes(),b'owned-by-someone-else');script.unlink()
        journal=self.resource/'cursor-stop-metadata.sqlite3';journal.write_bytes(b'corrupt-fixture')
        with self.assertRaisesRegex(RuntimeError,'journal schema'): deploy.plan(self.profile,self.manifest,cursor=True,fresh=True)
        self.assertEqual(journal.read_bytes(),b'corrupt-fixture')

    def test_partial_write_recovery_and_requested_option_conflict(self):
        original_atomic=deploy.atomic
        def interrupted(path,data):
            if path.name==deploy.CLI_NAMES[1]: raise OSError('synthetic interruption')
            original_atomic(path,data)
        with patch.object(deploy,'atomic',side_effect=interrupted):
            with self.assertRaises(OSError): deploy.install(self.profile,self.manifest,fresh=True)
        self.assertEqual(deploy.rollback(self.profile)['status'],'rolled_back')
        self.assertFalse((self.resource/deploy.CLI_NAMES[0]).exists())
        other=self.root/'other';other.mkdir()
        deploy.install(other,self.manifest,fresh=True,hostname='home-test')
        with self.assertRaisesRegex(RuntimeError,'options differ'): deploy.install(other,self.manifest,hostname='new-name')

    def test_redirected_managed_target_is_not_read_or_replaced(self):
        outside=self.root/'outside.cfg';outside.write_bytes(b'private-fixture')
        try: self.config.symlink_to(outside)
        except OSError: self.skipTest('symlink privilege unavailable')
        with self.assertRaisesRegex(RuntimeError,'Redirected managed'): deploy.plan(self.profile,self.manifest,fresh=True)
        self.assertEqual(outside.read_bytes(),b'private-fixture')

    def test_local_sharing_error_recovery_never_overwrites_concurrent_change(self):
        target=self.profile/'example';target.write_bytes(b'before')
        original_atomic=deploy.atomic
        attempts=[]
        def transient(path,data):
            attempts.append(1)
            if len(attempts)<3: raise PermissionError('synthetic sharing violation')
            original_atomic(path,data)
        with patch.object(deploy,'atomic',side_effect=transient): deploy.write_known(target,b'after',b'before')
        self.assertEqual(target.read_bytes(),b'after')
        def concurrent(path,data):
            path.write_bytes(b'new-user-value')
            raise PermissionError('synthetic concurrent sharing violation')
        with patch.object(deploy,'atomic',side_effect=concurrent):
            with self.assertRaisesRegex(RuntimeError,'changed concurrently'): deploy.write_known(target,b'desired',b'after')
        self.assertEqual(target.read_bytes(),b'new-user-value')

if __name__=='__main__': unittest.main()
