"""Exercise direct workspace routing without launching or changing the live game."""
import os
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch
import check_engine
from work_paths import codex_root, runtime_root, LOCAL_REPOSITORY, LOCAL_CODEX_ROOT

class WorkPathTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='utnt-work-paths-')
        self.addCleanup(self.tmp.cleanup)
        self.central = Path(self.tmp.name) / 'agent outputs with spaces'
        self.env = patch.dict(os.environ, {'UTNT_CODEX_ROOT': str(self.central)})
        self.env.start()
        self.addCleanup(self.env.stop)

    def test_explicit_output_root_and_isolated_runtime_root(self):
        self.assertEqual(codex_root(LOCAL_REPOSITORY), self.central.resolve())
        isolated = Path(self.tmp.name) / 'isolated'
        self.assertEqual(runtime_root(isolated), isolated.resolve())
        self.assertEqual(runtime_root(check_engine.ROOT), self.central.resolve())

    def test_local_production_default_and_portable_fixture(self):
        with patch.dict(os.environ, {}, clear=True):
            if os.name == 'nt':
                self.assertEqual(codex_root(LOCAL_REPOSITORY), LOCAL_CODEX_ROOT)
            fixture = Path(self.tmp.name) / 'portable'
            self.assertEqual(codex_root(fixture), fixture / 'tutnt' / '.codex')

    def test_runtime_uses_central_cwd_and_real_production_sources(self):
        with patch('check_engine.subprocess.run', return_value=SimpleNamespace(stdout=b'UTNT_TEST_END', stderr=b'', returncode=0)) as launch:
            result = check_engine.run_case('fixture-engine', 'fixture-iwad', mapname='TNT01', label='routing', quiet=True)
        self.assertTrue(result['ok'])
        args = launch.call_args.args[0]
        self.assertEqual(launch.call_args.kwargs['cwd'], self.central.resolve())
        self.assertEqual(args[args.index('-file')+1], str(check_engine.ROOT/'tutnt'))
        config = (self.central/'logs/routing.cfg').read_text()
        self.assertIn('screenshot "'+(self.central/'logs/routing.png').as_posix()+'"', config)
        self.assertEqual(Path(result['log']), self.central/'logs/routing.log')

    def test_compile_errorlog_and_engine_configuration_stay_central(self):
        code = 1337 if os.name == 'nt' else 1337 & 0xff
        with patch('check_engine.subprocess.run', return_value=SimpleNamespace(stdout=b'', stderr=b'', returncode=code)) as launch:
            result = check_engine.run_case('fixture-engine', 'fixture-iwad', label='compile-route', quiet=True)
        self.assertTrue(result['ok'])
        self.assertEqual(launch.call_args.kwargs['cwd'], self.central/'logs')
        self.assertTrue((self.central/'logs/compile-route.ini').is_file())

    def test_explicit_isolated_runtime_root_is_preserved(self):
        root = Path(self.tmp.name)/'specific runtime'
        with patch('check_engine.subprocess.run', return_value=SimpleNamespace(stdout=b'UTNT_TEST_END', stderr=b'', returncode=0)) as launch:
            result = check_engine.run_case('fixture-engine', 'fixture-iwad', root=root, mod=check_engine.ROOT/'tutnt', mapname='TNT01', quiet=True)
        self.assertTrue(result['ok'])
        self.assertEqual(launch.call_args.kwargs['cwd'], root.resolve())
        self.assertEqual(Path(result['log']).parent, root/'logs')

if __name__ == '__main__':
    unittest.main(verbosity=2)
