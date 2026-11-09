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
            shutil.copyfile(OVERLAY/"IIPSelectedTipCapability.lua",
                            work/"Scripts/IIPSelectedTipCapability.lua")
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
coverage_api.describe_other_action=function()return "Talk","/Game/TestNpc_C"end
coverage_api.selected_probe=function(a)
 assert(a==take,"unexpected selected sample")
 return "widget_class=TipHUD localized_text=present"
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

    def test_two_saves_one_process_first_world_then_stock_survey(self):
        # Same Lua VM: MapPre, old lease cleanup, next save's BeginPlay, then F4.
        # The new owner is deliberately not in the three-object first-pass gate.
        self.case("""
p.begin(actor);p.begin(take);select(nil)
assert(writes==1 and tx()==16384)
assert(select(actor)==actor);p.shown()
p.map_pre()
shutdown("map_pre") -- game-thread lifecycle invalidation cleanup
assert(writes==2 and tx()==0)
p.ended(actor:GetAddress())
p.begin(take) -- next save, newly observed non-allowlisted owner
assert(not select(take))
assert(writes==2 and take_panel.RenderTransform.Translation.X==8)
local seen=0
for _,line in ipairs(logs) do
 if line:find("SURVEY_SAMPLE") then seen=seen+1 end
end
assert(seen==1)
shutdown("stop") -- F4 only after the second save
assert(writes==2 and take_panel.RenderTransform.Translation.X==8)
""")

    def test_rearm_after_map_without_stop_on_same_known_path(self):
        # Simulates loading a second save in the same level. The source path
        # repeats while the old lease is retired; no stale single-shot block.
        self.case("""
p.begin(actor);select(nil);assert(tx()==16384)
assert(select(actor)==actor);p.shown()
p.map_pre()
shutdown("map_pre")
assert(tx()==0 and writes==2)
p.begin(actor);select(nil)
assert(tx()==16384 and writes==3)
assert(select(actor)==actor);p.shown()
shutdown("stop")
assert(tx()==0 and writes==4)
""")

    def test_multiple_map_boundaries_before_owner_endplay(self):
        # Map callbacks may precede the EndPlay of the old objects.
        self.case("""
p.begin(actor);select(nil)
assert(writes==1 and tx()==16384)
p.map_pre();p.map_pre()
shutdown("map_pre")
assert(writes==2 and tx()==0)
p.ended(actor:GetAddress())
p.begin(take);assert(not select(take))
assert(writes==2)
shutdown("stop");assert(writes==2)
""")

    def test_unrecognized_action_is_reported_read_only(self):
        self.case("""
local native=coverage_api.acquire
coverage_api.acquire=function(a)
 if a==take then return nil,"other_action" end
 return native(a)
end
p=Wide.new(coverage_api,emit)
p.begin(take);p.begin(take)
assert(writes==0)
local reports=0
for _,line in ipairs(logs) do
 if line:find("OTHER_ACTION_STOCK") then reports=reports+1 end
end
assert(reports==1)
""")

    def test_unsupported_selected_owner_is_sampled_once_without_hiding(self):
        self.case("""
local native=coverage_api.acquire
coverage_api.acquire=function(a)
 if a==take then return nil,"other_action" end
 return native(a)
end
local calls=0
coverage_api.selected_probe=function(a)
 assert(a==take)
 calls=calls+1
 if calls<3 then return nil end
 return "tag=Press widget_class=TipHUD localized_text=present"
end
p=Wide.new(coverage_api,emit)
p.begin(take)
for _=1,6 do assert(not select(take)) end
assert(calls==3 and writes==0 and take_panel.RenderTransform.Translation.X==8)
local samples=0
for _,line in ipairs(logs) do
 if line:find("SELECTED_NATIVE_SURVEY",1,true) then
  assert(line:find("stock_only=true",1,true))
  assert(line:find("tag=Press",1,true))
  samples=samples+1
 end
end
assert(samples==1)
""")

    def test_unavailable_selected_owner_keeps_original(self):
        self.case("""
local native=coverage_api.acquire
coverage_api.acquire=function(a)
 if a==take then return nil,"other_action" end
 return native(a)
end
local calls=0
coverage_api.selected_probe=function()
 calls=calls+1
 return nil
end
p=Wide.new(coverage_api,emit)
for _=1,12 do assert(not select(take)) end
assert(calls==8 and writes==0)
local n=0
for _,line in ipairs(logs) do
 if line:find("SELECTED_UNAVAILABLE",1,true) then n=n+1 end
end
assert(n==1)
""")

    def test_absent_position_is_not_permission_to_pre_hide(self):
        self.case("""
coverage_api.placement_sample=function()error("geometry unavailable")end
p=Wide.new(coverage_api,emit)
p.begin(take);assert(not select(take) and writes==0)
assert(logs[#logs]:find("SURVEY_UNAVAILABLE"))
""")

    def test_entrypoint_rearms_controller_after_map_and_marks_log_boundary(self):
        # Exercise the assembled main.lua callbacks, not just module.map_pre.
        from test_committed_owner_observer import ENTRY_RIG
        vm=LuaRuntime(unpack_returned_tuples=True)
        vm.execute(ENTRY_RIG + """
local find=StaticFindObject
function StaticFindObject(path)
 if path=="/Script/UMG.Widget:SetRenderTranslation" or
    path=="/Script/Engine.GameplayStatics:GetRealTimeSeconds" then
    return object("UFunction",path,nil)
 end
 if path=="/Script/Engine.Default__GameplayStatics" then
    return object("Object",path,class("/Script/Engine.GameplayStatics"))
 end
 return find(path)
end
local find_exact=StaticFindObject
function StaticFindObject(path)
 local o=find_exact(path)
 if o and o.kind=="UFunction" then
    o.kind="Function";o.type=function()return "UFunction"end
 end
 return o
end
package.preload.IIPWorldChild=function()
 return {enable_fast_children=function()R.fast=true end}
end
package.preload.IIPWorldTarget=function()return {new=function()return function()end end}end
package.preload.IIPSelectedTipCapability=function()return {inspect_selected=function()end}end
package.preload.IIPPrehideTranslation=function()return {}end
package.preload.IIPSelectedWorldSession=function()
 return {start=function()
  R.session_started=true
  return {
   stop=function(reason)R.stopped=reason end,
   invalidate=function(reason)R.invalidated=reason end,
   ended=function()end,
   status=function()return {active=true}end
  }
 end}
end
package.preload.IIPTranslationCoverage=function()return {}end
package.preload.IIPWideCoverage=function()
 return {new=function()
  R.wide=true
  return {
   begin=function(a)if a==A then R.owner_begins=(R.owner_begins or 0)+1 end end,
   ended=function()end,
   map_pre=function()R.map_resets=(R.map_resets or 0)+1 end
  }
 end}
end
Key={F4=115}
function IsKeyBindRegistered()return false end
function RegisterKeyBind()end
""")
        vm.execute(self.scripts["main"])
        vm.execute("""
assert(R.wide and R.fast and R.session_started,
       "main did not start: "..table.concat(R.logs," | "))
assert(R.cb.map and R.cb.begin and R.cb.finish)
begin_actor(K)
assert(has("CONTROLLER_ACQUIRED"))
R.cb.map()
assert(R.map_resets==1 and R.invalidated=="map_pre")
assert(has("MAP_PRE old_context_invalidated=true"))
begin_actor(K)  -- a controller may be recreated/re-begun after loading
local n=0
for _,line in ipairs(R.logs) do
 if line:find("event=CONTROLLER_ACQUIRED",1,true) then n=n+1 end
end
assert(n==2 and not R.stopped)
R.cb.map()
assert(R.map_resets==2 and R.invalidated=="map_pre")
begin_actor(K)
assert(not R.stopped)
""")

    def test_entrypoint_modes_and_native_transforms(self):
        main=self.scripts["main"]
        self.assertIn('local MODE="wide_safe"',main)
        self.assertIn('require("IIPWideCoverage")',main)
        self.assertIn('log("MAP_PRE","old_context_invalidated=true")',main)
        self.assertIn('translation_api.placement_sample',main)
        self.assertIn('or MODE=="wide_safe"',main)
        self.assertIn("World.enable_fast_children()",main)
        self.assertIn("translation_api.selected_probe",main)
        self.assertIn("/Script/UMG.Widget:SetRenderTranslation",main)
        self.assertNotIn("/Script/UMG.UserWidget:SetColorAndOpacity",main)
        vm=LuaRuntime()
        for name,code in self.scripts.items():
            vm.compile(code,name=name)
        vm.compile((OVERLAY/"IIPWideCoverage.lua").read_text(encoding="utf-8"),
                   name="IIPWideCoverage")

if __name__=="__main__":
    unittest.main()
