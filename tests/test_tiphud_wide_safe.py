# SPDX-License-Identifier: MPL-2.0
"""Mixed exact-path first appearance and world-wide native stock inventory."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import uuid

import test_tiphud_translation_cycle as cycle
from test_tiphud_translation_cycle import BASE, OVERLAY, LuaRuntime


class WideSafe(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        work=Path(tempfile.gettempdir()).resolve()/f"iip-wide-safe-{uuid.uuid4().hex}"
        work.mkdir()
        try:
            shutil.copytree(BASE/"Scripts",work/"Scripts")
            shutil.copyfile(OVERLAY/"IIPPrehideTranslation.lua",
                            work/"Scripts/IIPPrehideTranslation.lua")
            for p in ("first-show-observe.patch","prehide-translation.patch",
                      "translation-cycle.patch","first-approach-fast-create.patch",
                      "wide-safe.patch"):
                subprocess.run(["git","apply","--unidiff-zero",str(OVERLAY/p)],
                               cwd=work,check=True)
            cls.scripts={p.stem:p.read_text(encoding="utf-8")
                         for p in (work/"Scripts").glob("*.lua")}
        finally:
            shutil.rmtree(work)

    def case(self,scenario):
        # The coverage fixture uses actual IIPTranslationCoverage and actual
        # IIPPrehideTranslation, not an independent fake coordinator.
        module=(OVERLAY/"IIPWideCoverage.lua").read_text(encoding="utf-8")
        cycle.TranslationCycle.setUpClass()
        cycle.TranslationCycle().case("""
package.loaded.IIPTranslationCoverage=Coverage
coverage_api.early_target=function(path)
 if path==target then return "Open" end
end
coverage_api.placement_sample=function(a,record)
 assert(a==take and record.actor==take_record.actor)
 return "sample:source=known_geometry_unknown"
end
Wide=(function()
""" + module + """
end)()
p=Wide.new(coverage_api,emit)
""" + scenario)

    def test_exact_first_approach_and_unknown_remains_stock(self):
        self.case("""
p.begin(actor);p.begin(take);select(nil)
assert(writes==1 and tx()==16384)
assert(select(actor)==actor);p.shown()
assert(not select(take))
assert(writes==1 and take_panel.RenderTransform.Translation.X==8)
local samples=0
for _,line in ipairs(logs) do
 if line:find("SURVEY_SAMPLE") then samples=samples+1 end
end
assert(samples==1)
assert(not select(take))
local again=0
for _,line in ipairs(logs) do if line:find("SURVEY_SAMPLE") then again=again+1 end end
assert(again==1)
shutdown("stop")
assert(tx()==0 and writes==2 and take_panel.RenderTransform.Translation.X==8)
""")

    def test_unknown_stays_stock_despite_qualified_direct_brush(self):
        self.case("""
p.begin(take);assert(not select(take));select(nil)
assert(not select(take));select(nil)
assert(writes==0 and take_panel.RenderTransform.Translation.X==8)
shutdown("stop");assert(writes==0)
""")

    def test_direct_target_and_endplay_map_cleanup(self):
        self.case("""
p.begin(actor);p.begin(take);select(nil)
assert(select(actor)==actor);p.shown()
assert(not select(take));assert(writes==1)
assert(select(actor)==actor)
p.ended(11)
p.begin(take);assert(not select(take))
p.map_pre();shutdown("map_pre")
assert(tx()==0 and writes==2)
""")

    def test_absent_position_is_not_permission_to_pre_hide(self):
        self.case("""
coverage_api.placement_sample=function()error("geometry unavailable")end
p=Wide.new(coverage_api,emit)
p.begin(take);assert(not select(take) and writes==0)
assert(logs[#logs]:find("SURVEY_UNAVAILABLE"))
""")

    def test_entrypoint_modes_and_native_transforms(self):
        main=self.scripts["main"]
        self.assertIn('local MODE="wide_safe"',main)
        self.assertIn('require("IIPWideCoverage")',main)
        self.assertIn('translation_api.placement_sample',main)
        self.assertIn('or MODE=="wide_safe"',main)
        self.assertIn("World.enable_fast_children()",main)
        self.assertIn("/Script/UMG.Widget:SetRenderTranslation",main)
        self.assertNotIn("/Script/UMG.UserWidget:SetColorAndOpacity",main)
        vm=LuaRuntime()
        for name,code in self.scripts.items():
            vm.compile(code,name=name)
        vm.compile((OVERLAY/"IIPWideCoverage.lua").read_text(encoding="utf-8"),
                   name="IIPWideCoverage")

if __name__=="__main__":
    unittest.main()
