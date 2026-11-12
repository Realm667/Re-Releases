"""Verify ZDCMP1 isolation and the unchanged routing of shared UTNT tools."""
import os
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

import check_engine
from check_zdcmp1_layout import violations
import zdcmp1_paths as paths
from work_paths import codex_root


class ProjectPathTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(dir=paths.temporary_root(), prefix='zdc-path-contracts-')
        self.addCleanup(self.directory.cleanup)
        self.base = Path(self.directory.name)
        self.local = self.base / 'ZDCMP1 workspace with spaces'
        self.local.mkdir()
        self.other = self.base / 'other mod'
        self.environment = patch.dict(os.environ, {'ZDCMP1_WORKSPACE': str(self.local), 'UTNT_CODEX_ROOT': str(self.other),
                                                 'ZDCMP1_ENGINE': '', 'ZDCMP1_IWAD': '', 'ZDCMP1_ACC': ''})
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def test_project_selection_does_not_change_shared_default(self):
        self.assertEqual(paths.data_root(), self.local / '.codex')
        self.assertEqual(codex_root(), self.other.resolve())

    def test_direct_shared_runtime_selects_only_zdcmp1(self):
        result_stub = SimpleNamespace(stdout=b'UTNT_TEST_END', stderr=b'', returncode=0)
        with patch('check_engine.subprocess.run', return_value=result_stub) as launch:
            result = check_engine.run_case('engine', 'iwad', mod=check_engine.ROOT / 'zdcmp1', mapname='MAP01', quiet=True)
        self.assertTrue(result['ok'])
        self.assertEqual(launch.call_args.kwargs['cwd'], self.local / '.codex')
        self.assertFalse(self.other.exists())
        with patch('check_engine.subprocess.run', return_value=result_stub) as launch:
            check_engine.run_case('engine', 'iwad', mod=check_engine.ROOT / 'tutnt', mapname='TNT01', quiet=True)
        self.assertEqual(launch.call_args.kwargs['cwd'], self.other.resolve())

    def test_explicit_output_root_survives_project_detection(self):
        isolated = self.base / 'explicit output'
        with patch('check_engine.subprocess.run', return_value=SimpleNamespace(stdout=b'UTNT_TEST_END', stderr=b'', returncode=0)) as launch:
            paths.run_case('engine', 'iwad', root=isolated, mod=check_engine.ROOT / 'zdcmp1', mapname='MAP01', quiet=True)
        self.assertEqual(launch.call_args.kwargs['cwd'], isolated.resolve())

    def test_arbitrarily_named_comparison_package_stays_in_project(self):
        with patch('check_engine.subprocess.run', return_value=SimpleNamespace(stdout=b'UTNT_TEST_END', stderr=b'', returncode=0)) as launch:
            paths.run_case('engine', 'iwad', mod=self.base / 'baseline.pk3', mapname='MAP01', quiet=True)
        self.assertEqual(launch.call_args.kwargs['cwd'], self.local / '.codex')

    def test_private_tools_override_another_projects_environment(self):
        engine = self.local / 'dependencies/uzdoom/uzdoom.exe'
        iwad = self.local / 'dependencies/iwads/DOOM2.WAD'
        # The engine extension is platform-dependent; no process is launched.
        if os.name != 'nt': engine = engine.with_suffix('')
        for p in (engine, iwad):
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(b'fixture')
        with patch.dict(os.environ, {'UTNT_ENGINE': str(self.other / 'engine'), 'UTNT_IWAD': str(self.other / 'iwad')}):
            self.assertEqual(paths.tool_default('engine'), str(engine))
            with patch.object(tempfile, 'tempdir', None):
                paths.configure_environment()
                self.assertEqual(Path(tempfile.gettempdir()), self.local / '.codex/cache/temp')
                self.assertEqual(os.environ['UTNT_CODEX_ROOT'], str(self.other))
                self.assertEqual(os.environ['UTNT_ENGINE'], str(engine))

    def test_portable_checkout_requires_an_explicit_workspace(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(paths, 'ROOT', self.base / 'checkout'):
            with self.assertRaisesRegex(ValueError, 'ZDCMP1_WORKSPACE'):
                paths.workspace()

    def test_layout_ignores_other_mods_and_finds_own_outputs(self):
        repo = self.base / 'repo'
        (repo / 'zdcmp1').mkdir(parents=True)
        (repo / 'tutnt').mkdir()
        (repo / 'tutnt/foreign.log').write_text('unrelated')
        self.assertEqual(violations(repo, self.local), [])
        (repo / 'zdcmp1/unwanted.log').write_text('own output')
        self.assertTrue(any('unwanted.log' in issue for issue in violations(repo, self.local)))

    def test_layout_does_not_load_another_projects_policy(self):
        issues = violations(self.base / 'repo', self.local, self.other / 'workspace-root.json')
        self.assertEqual(issues, ['ZDCMP1 workspace policy must be inside its own workspace'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
