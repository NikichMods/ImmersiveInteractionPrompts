# SPDX-License-Identifier: MPL-2.0
"""Execute real reentrant World modules on existing UE4 host mocks, not native acceptance."""
import unittest
from test_ui_child import LuaRuntime, ROOT
from test_world_live_editor import FIXTURE, EXTRA, CONTEXT, ORIENTATION, FRAMES, HINT_FIXTURE, LIVE
from test_compact_layout import MEASURED
from test_world_editor_style import STYLE

BASE=ROOT/"research/interaction-prompts-owner/world-space/world-reuse"
SOURCES={p.stem:p.read_text(encoding="utf8") for p in (BASE/"Scripts").glob("*.lua")}
ADAPTER=(BASE/"IIPWorldRenderer.lua").read_text(encoding="utf8")
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
if __name__=="__main__":unittest.main()
