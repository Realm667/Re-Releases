"""Exercise misplaced outputs and the legacy workspace boundary in temporary trees."""
import json
from pathlib import Path
import tempfile
import unittest
from check_work_layout import violations

class LayoutTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)/'repo'
        self.root.mkdir()

    def write(self, name, contents='test'):
        path = self.root/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents)
        return path

    def test_central_outputs_and_integration_package_are_allowed(self):
        self.write('tutnt/.codex/work/topic/result.log')
        self.write('tutnt/.codex/builds/experiment.pk3')
        self.write('tutnt_build.bat')
        self.write('tutnt.pk3')
        self.write('tutnt.pk3.build.lock')
        self.assertEqual(violations(self.root), [])

    def test_misplaced_outputs_are_reported_without_deletion(self):
        paths = [self.write(x) for x in ('tutnt-test.pk3', 'tutnt/maps/map.wad.backup1', 'tools/run.log')]
        self.assertEqual(len(violations(self.root)), 3)
        self.assertTrue(all(path.is_file() for path in paths))

    def test_plain_legacy_directory_is_reported(self):
        self.write('logs/result.log')
        self.assertTrue(any('compatibility path' in item for item in violations(self.root)))

    def test_documentation_is_kept_out_of_repository_root(self):
        self.write('_docs/utnt/UTNT_WEATHER.md')
        self.write('tutnt/.codex/notes/TNT04B_SKY_CONCEPT.md')
        self.assertEqual(violations(self.root), [])
        self.write('UTNT_WEATHER.md')
        self.write('TNT04B_SKY_CONCEPT.md')
        self.assertEqual(len(violations(self.root)), 2)

    def test_only_new_workspace_entries_are_reported(self):
        workspace = Path(self.tmp.name)/'chat'
        workspace.mkdir()
        (workspace/'old-script.py').write_text('legacy')
        config = self.write('tutnt/.codex/policy/workspace-root.json', json.dumps({
            'workspace':str(workspace), 'existing_entries':['old-script.py']}))
        self.assertEqual(violations(self.root, config), [])
        (workspace/'new-script.py').write_text('new')
        self.assertEqual(len(violations(self.root, config)), 1)

if __name__ == '__main__':
    unittest.main(verbosity=2)
