# SPDX-License-Identifier: MPL-2.0
"""Execute real reentrant World modules on existing UE4 host mocks, not native acceptance."""
import unittest
from test_ui_child import LuaRuntime, ROOT
from test_world_live_editor import FIXTURE, EXTRA, CONTEXT, ORIENTATION, FRAMES, HINT_FIXTURE, LIVE
from test_compact_layout import MEASURED
from test_world_editor_style import STYLE

BASE=ROOT/"research/interaction-prompts-owner/world-space/auto-world-successor"
SOURCES={p.stem:p.read_text(encoding="utf8") for p in (BASE/"Scripts").glob("*.lua")}
ADAPTER=(BASE/"Scripts/IIPWorldRenderer.lua").read_text(encoding="utf8")
RESOURCES=r"""
local leased=false
return {
 prepare=function()end,
 font=function(o)
   if S.font_failure then error("font bind failure")end
   o.Font.FontObject=S.private_font
 end,
 ornament=function(o)
   assert(not leased,"ornament lease already exists")
   leased=true;o.Brush.ResourceObject=S.raw
   S.imports=(S.imports or 0)+1
 end,
 has_live_lease=function()return leased end,
 cycle_cleaned=function()
   assert(leased,"missing ornament lease")
   leased=false;S.released=(S.released or 0)+1
 end,
}
"""
SETUP=r"""
S.game=true
local factory=S.objects["/Script/UMG.WidgetBlueprintLibrary:Create"]
local create_once=getmetatable(factory).__call
getmetatable(factory).__call=function(...)
 local host=create_once(...)
 S.host=host;S.panel=nil
 return host
end
set(P.actor,"FinishAddComponent",function(_,c,manual,t)
 assert(manual and c==S.comp and c.widget==S.host)
 assert(c.draw.X==1024 and c.draw.Y==512)
 c.transform=t;c.registered=true
end)
World=require("IIPWorldChild")
Renderer=(function() return (function()
""" + ADAPTER + r"""
end)() end)()
R=Renderer.new(World,function(owner)
 assert(owner.actor=="A")
 return P.actor,P.component,P.widget
end,function()end)
function owner(action)return {actor="A",component="A.C",widget="A.W",action=action or "Open"}end
"""

class WorldReuseRealModules(unittest.TestCase):
 def case(self,code):
  L=LuaRuntime(unpack_returned_tuples=True)
  L.execute(FIXTURE+EXTRA+CONTEXT+ORIENTATION+FRAMES+HINT_FIXTURE+LIVE+MEASURED+STYLE)
  for n,source in SOURCES.items():
   if n=="main":continue
   L.execute('package.preload["'+n+'"]=function()\n'+
     (RESOURCES if n=="IIPResources" else source)+'\nend')
  L.execute(SETUP)
  L.execute(code)

 def test_one_owner_created_hidden_and_cleanup_releases_lease(self):
  self.case(r"""
assert(R.empty())
assert(R.create(owner("Open"),1))
assert(S.created==1 and S.imports==1 and S.host.Visibility==2)
assert(R.resume() and R.refresh())
assert(R.cleanup("switch",2) and R.empty())
assert(S.released==1 and S.comp.pending and S.panel==nil)
""")

 def test_second_owner_uses_sequential_components_and_no_editor(self):
  self.case(r"""
assert(R.create(owner("Open"),1))
local first=S.comp.p
assert(R.cleanup("switch",2))
assert(R.create(owner("Take"),3))
assert(S.comp.p~=first and S.imports==2 and S.panel==nil)
assert(R.cleanup("switch",4) and R.empty())
assert(S.released==2)
""")
 def test_failed_unbind_blocks_second_component_until_verified_cleanup(self):
  self.case(r"""
assert(R.create(owner("Open"),1))
S.detach_fail=true
assert(R.cleanup("change",2)==false)
assert(not R.empty())
assert(not pcall(R.create,owner("Take"),3))
assert(S.imports==1)
S.detach_fail=false
assert(R.cleanup("retry",2) and R.empty())
assert(R.create(owner("Take"),3))
assert(S.imports==2)
assert(R.cleanup("done",4) and R.empty())
""")

 def test_all_seventeen_adopted_layout_values_are_used(self):
  self.case(r"""
local tuning=require("IIPTuning")
assert(#tuning.fields==17)
local t=tuning.new()
local expected={
 upper_size=50,lower_size=30,tracking=350,outline=3,lower_outline=3,
 gap=0,divider_y=-6,divider_width=300,divider_thickness=1.25,
 divider_alpha=1,hint_size=50,hint_gap=10,hint_y=0,
 upper_brightness=0.6,lower_brightness=0.5,
 divider_brightness=0.5,hint_brightness=0.5
}
for k,v in pairs(expected)do assert(t[k]==v,k)end
""")
 def test_fourth_host_recovers_from_absent_with_one_exact_load(self):
  self.case(r"""
assert(R.create(owner("Open"),1))
assert(R.cleanup("to_Check",2))
assert(R.create(owner("Check"),3))
assert(R.cleanup("to_Take",4))
assert(R.create(owner("Take"),5))
assert(R.cleanup("to_Check",6))
local old=S.objects[HOST]
local fresh=make(HOST,"Class")
set(fresh,"type",function()return "UClass"end)
set(fresh,"GetSuperStruct",function()return old:GetSuperStruct()end)
S.objects[HOST]=nil
local loads=0
function LoadAsset(p)
 assert(p==HOST and S.game)
 loads=loads+1
 S.objects[HOST]=fresh
 return fresh,true,true
end
assert(R.create(owner("Check"),7))
assert(loads==1 and S.created==4)
assert(has("event=HOST_RECOVERY_ATTEMPT") and has("event=HOST_RECOVERED"))
assert(S.imports==4)
assert(R.cleanup("final",8) and R.empty() and S.released==4)
""")

 def test_exact_absent_null_ue4ss_wrapper_is_recovered(self):
  self.case(r"""
assert(R.create(owner("Open"),1))
assert(R.cleanup("switch",2))
local old=S.objects[HOST]
local replacement=make(HOST,"Class")
set(replacement,"type",function()return "UClass"end)
set(replacement,"GetSuperStruct",function()return old:GetSuperStruct()end)
S.objects[HOST]=nil
local stub=make("/Absent.Null.Host","Class")
set(stub,"live",false)
set(stub,"GetAddress",function()return 0 end)
local regular_lookup=StaticFindObject
function StaticFindObject(p)
 if p==HOST and S.objects[HOST]==nil then return stub end
 return regular_lookup(p)
end
local calls=0
function LoadAsset(p)
 assert(p==HOST)
 calls=calls+1
 S.objects[HOST]=replacement
 return replacement,true,true
end
assert(R.create(owner("Check"),3))
assert(calls==1 and S.created==2)
assert(has("state=ABSENT_NULL one_exact_load=true"))
assert(R.cleanup("final",4) and R.empty())
""")

 def test_absent_host_failed_exact_reload_fails_closed_without_second_component(self):
  self.case(r"""
assert(R.create(owner("Open"),1))
assert(R.cleanup("switch",2))
S.objects[HOST]=nil
local tries=0
function LoadAsset(p)
 assert(p==HOST)
 tries=tries+1
 return nil,false,false
end
assert(not pcall(R.create,owner("Take"),3))
assert(tries==1 and S.created==1 and not R.empty())
assert(has("HOST_RECOVERY_RESULT") and not has("HOST_RECOVERED"))
assert(R.cleanup("failed_create",4) and R.empty())
""")

 def test_host_identity_mismatch_does_not_load_or_substitute(self):
  self.case(r"""
assert(R.create(owner("Open"),1))
assert(R.cleanup("switch",2))
local wrong=make(HOST,"/Script/Engine.Material")
S.objects[HOST]=wrong
local tries=0
function LoadAsset(p)tries=tries+1;error("unexpected guessed load")end
assert(not pcall(R.create,owner("Take"),3))
assert(tries==0 and S.created==1)
assert(R.cleanup("bad_class",4) and R.empty())
""")

 def test_missing_stock_material_never_uses_host_recovery(self):
  self.case(r"""
assert(R.create(owner("Open"),1))
assert(R.cleanup("switch",2))
S.objects[MASK]=nil
local tries=0
function LoadAsset(p)tries=tries+1;error("unexpected material fallback")end
assert(not pcall(R.create,owner("Check"),3))
assert(tries==0 and S.created==1)
assert(R.cleanup("material_missing",4) and R.empty())
""")

if __name__=="__main__":unittest.main()
