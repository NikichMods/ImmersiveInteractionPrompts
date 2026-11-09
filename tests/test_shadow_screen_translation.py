# SPDX-License-Identifier: MPL-2.0
"""Actual Lua shadow-only native Screen lease, with a mock of the reflected setter."""
from pathlib import Path
import unittest

from test_ui_child import LuaRuntime, ROOT

SOURCE=(ROOT / "research/interaction-prompts-owner/world-space/tiphud-render-suppression"
        / "IIPShadowScreenTranslation.lua").read_text(encoding="utf-8")

FIXTURE=r'''
local function obj(path,address,class)
 local t={path=path,address=address,class=class,valid=true}
 function t:GetAddress()return self.address end
 function t:GetOuter()return self.outer end
 return t
end
actor=obj("selected_actor",11,"/Script/Genesis.Object")
comp=obj("selected_actor.ExtendedWidget",12,"/Script/Genesis.ExtendedWidgetComponent")
widget=obj("selected_actor.TipHUD",13,"/Game/MainContent/Template/UMG/TipHUD.TipHUD_C")
tree=obj("selected_actor.TipHUD.WidgetTree",14,"/Script/UMG.WidgetTree")
panel=obj("selected_actor.TipHUD.WidgetTree.CanvasPanel_0",15,"/Script/UMG.CanvasPanel")
panel.outer=tree
panel.RenderTransform={Translation={X=3,Y=8}}
widget.WidgetTree=tree;tree.RootWidget=panel
comp.Widget=widget;comp.NewUserWidget=nil
comp.bAddedToScreen=true;comp.bVisible=true
function comp:GetOwner()return actor end
function comp:GetWidget()return widget end
function comp:GetWidgetSpace()return 1 end
function comp:GetUserWidgetObject()return widget end
actor.ExtendedWidget=comp
row={
 actor="native_selection",
 refs={
   actor={path=actor.path,address=actor.address},
   component={path=comp.path,address=comp.address},
   widget={path=widget.path,address=widget.address},
 }
}
writes=0;events={}
api={
 alive=function(o)return o~=nil and o.valid==true end,
 path=function(o)return o.path end,
 class=function(o)return o.class end,
 lookup=function(p)if p==actor.path then return actor end end,
 set=function(p,v)
   assert(p==panel and type(v.X)=="number" and type(v.Y)=="number")
   writes=writes+1
   p.RenderTransform.Translation={X=v.X,Y=v.Y}
 end,
}
function emit(e,d)events[#events+1]={event=e,details=d}end
'''

class ShadowScreenTranslation(unittest.TestCase):
    def case(self, code):
        vm=LuaRuntime(unpack_returned_tuples=True)
        vm.globals().Module=vm.execute(SOURCE)
        vm.execute(FIXTURE+"\ns=Module.new(api,emit)\n"+code)

    def test_only_hide_after_world_shown_restore_and_no_repeat_write(self):
        self.case("""
assert(s.observe(row,actor,false) and writes==0 and not s.active())
assert(s.observe(row,actor,true) and writes==1 and s.active())
assert(panel.RenderTransform.Translation.X==16387)
assert(s.observe(row,actor,true) and writes==1)
assert(s.observe(row,actor,false) and writes==2 and not s.active())
assert(panel.RenderTransform.Translation.X==3 and panel.RenderTransform.Translation.Y==8)
assert(events[1].event=="HIDDEN" and events[2].event=="RESTORED")
-- Do not re-hide the same episode after a temporary World loss.
assert(s.observe(row,actor,true) and writes==2)
assert(s.observe(nil,nil,false))
assert(s.observe(row,actor,true) and writes==3)
assert(s.restore("manual_f9") and writes==4)
""")

    def test_restore_after_native_screen_unmounted(self):
        self.case("""
assert(s.observe(row,actor,true) and writes==1)
comp.bAddedToScreen=false;comp.bVisible=false
assert(s.restore("selection_left") and writes==2)
assert(panel.RenderTransform.Translation.X==3 and not s.active())
""")

    def test_unsupported_native_root_leaves_stock(self):
        self.case("""
panel.class="/Script/UMG.TextBlock"
assert(s.observe(row,actor,true) and writes==0 and not s.active())
assert(events[1].event=="REFUSED")
""")

    def test_unexpected_writer_does_not_overwrite_foreign_transform(self):
        self.case("""
assert(s.observe(row,actor,true) and writes==1)
panel.RenderTransform.Translation={X=500,Y=8}
assert(not s.restore("changed") and writes==1)
assert(panel.RenderTransform.Translation.X==500)
assert(events[2].event=="RESTORE_UNCONFIRMED")
""")

    def test_identity_lost_does_not_write_foreign_object(self):
        self.case("""
assert(s.observe(row,actor,true) and writes==1)
panel.valid=false
assert(not s.restore("gone") and writes==1)
assert(events[2].event=="RESTORE_UNCONFIRMED")
""")

    def test_partial_setter_failure_restores_exact_original(self):
        self.case("""
local normal=api.set
api.set=function(p,v)
 normal(p,v)
 if writes==1 then error("fault after first setter") end
end
assert(s.observe(row,actor,true) and writes==2 and not s.active())
assert(panel.RenderTransform.Translation.X==3)
assert(events[1].event=="REFUSED" and events[2].event=="RESTORED")
""")

if __name__=="__main__": unittest.main()
