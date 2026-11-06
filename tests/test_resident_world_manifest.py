# SPDX-License-Identifier: MPL-2.0
"""Exact 17-file research successor source identity, not game acceptance."""
import hashlib
import json
import re
import unittest

from test_ui_child import ROOT

BASE = ROOT / "research/interaction-prompts-owner/world-space/auto-world-successor"
MANIFEST = json.loads((BASE / "SOURCE_MANIFEST.json").read_text(encoding="utf-8"))


class ResidentAutoWorldManifest(unittest.TestCase):
    def test_exact_checked_out_lua_hashes(self):
        self.assertEqual(MANIFEST["expected_script_count"], 17)
        self.assertEqual(MANIFEST["runtime_acceptance"], "PENDING")
        self.assertEqual(MANIFEST["status"], "SOURCE_ONLY_NOT_INSTALLED_RUNTIME_UNVERIFIED")
        expected = set(MANIFEST["files"])
        actual = {str(path.relative_to(BASE)) for path in (BASE / "Scripts").glob("*.lua")}
        self.assertEqual(expected, actual)
        for path, sha in MANIFEST["files"].items():
            self.assertRegex(sha, r"^[0-9a-f]{64}$")
            self.assertEqual(hashlib.sha256((BASE / path).read_bytes()).hexdigest(), sha, path)

    def test_dependencies_are_explicit_and_private_config_is_external(self):
        names = {p.stem for p in (BASE / "Scripts").glob("*.lua")}
        self.assertNotIn("IIPLiveConfig", names)
        for path in (BASE / "Scripts").glob("*.lua"):
            source = path.read_text(encoding="utf-8")
            imports = re.findall(r'require\(["\']([^"\']+)["\']\)', source)
            self.assertFalse(set(imports) - names - {"IIPLiveConfig"},
                             (path.name, imports))

    def test_responsiveness_is_sampling_not_a_session_timeout(self):
        observer = (BASE / "Scripts/IIPInteractionEvents.lua").read_text(encoding="utf-8")
        session = (BASE / "Scripts/IIPAutoWorldSession.lua").read_text(encoding="utf-8")
        host = (BASE / "Scripts/IIPWorldChild.lua").read_text(encoding="utf-8")
        self.assertIn("local FRAMES=3", observer)
        self.assertIn("local READS_PER_SAMPLE=48", observer)
        self.assertIn("source_sample_frames=3", session)
        self.assertIn("HOST_RECOVERY_ATTEMPT", host)
        for forbidden in ("MAX_SAMPLES", "MAX_BEGIN", "MAX_CANDIDATES"):
            self.assertNotIn(forbidden, observer)


if __name__ == "__main__":
    unittest.main()
