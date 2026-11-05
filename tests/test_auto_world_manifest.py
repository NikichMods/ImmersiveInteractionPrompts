# SPDX-License-Identifier: MPL-2.0
import hashlib, json, unittest
from test_ui_child import ROOT
BASE=ROOT/'research/interaction-prompts-owner/world-space/auto-world'
class ManifestCheck(unittest.TestCase):
 def test_hashes(self):
  manifest=json.loads((BASE/'SOURCE_MANIFEST.json').read_text())
  self.assertEqual(manifest['count'],17)
  self.assertEqual(set(manifest['files']),set('Scripts/'+p.name for p in (BASE/'Scripts').glob('*.lua')))
  for path,expected in manifest['files'].items():
   self.assertEqual(hashlib.sha256((BASE/path).read_bytes()).hexdigest(),expected,path)
if __name__=='__main__':unittest.main()
