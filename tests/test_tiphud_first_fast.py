# SPDX-License-Identifier: MPL-2.0
"""First approach and independent child construction variant."""
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path
import unittest

import test_tiphud_translation_cycle as cycle
from test_tiphud_translation_cycle import BASE, OVERLAY, LuaRuntime
from test_selected_owner_world import host
from test_tiphud_direct_brush import DIRECT_INPUT


class FirstApproachAndFastCreate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dest=Path(tempfile.gettempdir()).resolve()/f"iip-first-fast-{uuid.uuid4().hex}"
        dest.mkdir()
        try:
            shutil.copytree(BASE/"Scripts",dest/"Scripts")
            shutil.copyfile(OVERLAY/"IIPPrehideTranslation.lua",dest/"Scripts/IIPPrehideTranslation.lua")
            for name in ("first-show-observe.patch","prehide-translation.patch",
                         "translation-cycle.patch","first-approach-fast-create.patch"):
                subprocess.run(["git","apply","--unidiff-zero",str(OVERLAY/name)],cwd=dest,check=True)
            cls.scripts={p.stem:p.read_text(encoding="utf-8") for p in (dest/"Scripts").glob("*.lua")}
        finally:
            shutil.rmtree(dest)

    def test_first_approach_and_scope(self):
        # Exercise the real coverage and per-owner lease with an explicit early allowlist.
        cycle.TranslationCycle.setUpClass()
        cycle.TranslationCycle().case("""
coverage_api.early_target=function(path)if path==target then return "Open" end end
coverage_api.qualify=function()error("must not qualify first")end
p=Coverage.new(coverage_api,emit)
p.begin(actor);p.begin(take);select(nil)
assert(tx()==16384 and writes==1)
assert(select(actor)==actor);p.shown()
assert(not select(take) and writes==1)
shutdown("stop");assert(tx()==0 and writes==2)
""")

    def test_first_approach_separate_leases_and_hold_fallback(self):
        cycle.TranslationCycle.setUpClass()
        cycle.TranslationCycle().case("""
coverage_api.early_target=function(path)
 if path==target then return "Open" elseif path=="take_target" then return "Take" end
end
p=Coverage.new(coverage_api,emit)
p.begin(actor);p.begin(take)
select(nil);select(nil);assert(writes==2)
assert(select(actor)==actor);p.shown()
assert(select(take)==take);p.shown()
unsupported=true
assert(not select(take) and take_panel.RenderTransform.Translation.X==8)
unsupported=false;assert(not select(take) and writes==3)
shutdown("stop");assert(writes==4 and tx()==0)
""")

    def test_fast_mode_builds_and_cleans_own_children(self):
        vm=LuaRuntime()
        vm.execute(host.FIXTURE + host.EXTRA + host.CONTEXT + host.ORIENTATION
                   + host.FRAMES + host.HINT_FIXTURE + host.LIVE + host.MEASURED + host.STYLE)
        for name,source in self.scripts.items():
            vm.compile(source,name=name)
            if name!="main":
                body=host.RESOURCES if name=="IIPResources" else source
                vm.execute(f'package.preload["{name}"]=function()\n{body}\nend')
        vm.execute(host.SETUP + """
NAME_None={ToString=function()return "None"end}
local construct=StaticConstructObject
local names={"Generated_Action","Generated_Aphes","Generated_Ornament","Generated_Hint"}
local count=0
function StaticConstructObject(c,outer,name,...)
 if name==NAME_None then
    count=count+1
    return construct(c,outer,assert(names[count]),...)
 end
 return construct(c,outer,name,...)
end
World.enable_fast_children()
""" + DIRECT_INPUT + """
assert(count==4 and S.host.Visibility==3 and S.brush_sets==1)
assert(S.hint.Brush.ResourceObject==S.raw)
assert(S.lower:GetText():ToString()==P.text:GetText():ToString())
assert(World.cleanup("test") and World.empty() and S.released==1)
""")


if __name__ == "__main__":
    unittest.main()
