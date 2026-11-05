# SPDX-License-Identifier: MPL-2.0
"""Source-only World lease checks; not native engine acceptance."""
import unittest
from test_ui_child import LuaRuntime, ROOT
SOURCE=(ROOT/"research/interaction-prompts-owner/world-space/world-reuse/IIPWorldRenderer.lua").read_text(encoding="utf8")
RIG=r"""
S={owned=false,creates=0,cleans=0,prepare=0,assets=0,fail=false}
local world={
 prepare=function()S.prepare=S.prepare+1 end,
 refresh_assets=function()S.assets=S.assets+1 end,
 empty=function()return not S.owned end,
 create=function(a,c,w,stop,action)
   assert(not S.owned);S.owned=true;S.creates=S.creates+1
   if S.fail=="create"then error("partial creation")end
 end,
 cleanup=function()
   if S.fail=="cleanup"then return false end
   S.owned=false;S.cleans=S.cleans+1;return true
 end,
 hide=function()return true end,
 resume=function()return true end,
 refresh=function()return true end
}
R=Renderer.new(world,function(o)
  return o.actor,o.component,o.widget
end,function()end)
function record(i,action)
 return {actor="Actor"..i,component="Component"..i,widget="Tip"..i,action=action or "Open"}
end
"""
class RendererLease(unittest.TestCase):
 def case(self,code):
  L=LuaRuntime(unpack_returned_tuples=True)
  L.execute("Renderer=(function()\n"+SOURCE+"\nend)()")
  L.execute(RIG)
  L.execute(code)
 def test_two_owners_and_repeated_focus(self):
  self.case('assert(R.create(record(1),1));for i=1,100 do assert(R.hide() and R.resume() and R.refresh())end;'
    'assert(S.creates==1);assert(R.cleanup("change",2));assert(R.create(record(2,"Take"),3));'
    'assert(R.cleanup("change",4));assert(R.create(record(3,"Check"),5));'
    'assert(S.creates==3 and S.cleans==2 and S.prepare==1 and S.assets==1)')
 def test_cleanup_failure_keeps_lease(self):
  self.case('R.create(record(1),1);S.fail="cleanup";assert(R.cleanup("change",2)==false);'
    'assert(not pcall(R.create,record(2),3) and S.creates==1);'
    'S.fail=false;assert(R.cleanup("retry",2) and R.empty());assert(R.create(record(2),3))')
 def test_partial_create_cannot_overlap(self):
  self.case('S.fail="create";assert(not pcall(R.create,record(1),1));'
    'assert(not R.empty() and not pcall(R.create,record(2),2));'
    'S.fail=false;assert(R.cleanup("partial",3) and R.create(record(2),4))')
 def test_invalid_action_never_allocates(self):
  self.case('assert(not pcall(R.create,record(1,"Climb"),1));assert(S.creates==0)')
if __name__=="__main__":unittest.main()
