# SPDX-License-Identifier: MPL-2.0
"""Source-only bounded TipHUD CanvasPanel_0 translation and overlay assembly."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import uuid

from test_selected_owner_world import BASE, LuaRuntime, MOCK
from test_tiphud_tint import OVERLAY, RIG

ROOT = OVERLAY / "IIPPrehideTranslation.lua"

ADAPTER = r'''
local function mock(name,cl,address)
    local obj={live=true}
    function obj:GetAddress()return address end
    function obj:GetFullName()return "Object "..name end
    function obj:GetClass()return {GetFullName=function()return "Class "..cl end}end
    return obj
end
tree=mock("WidgetTree","/Script/UMG.WidgetTree",5)
panel=mock("WidgetTree.CanvasPanel_0","/Script/UMG.CanvasPanel",4)
function panel:GetOuter()return tree end
panel.RenderTransform={Translation={X=0,Y=0},Scale={X=1,Y=1},Angle=0,Shear={X=0,Y=0}}
tree.RootWidget=panel
widget.WidgetTree=tree
local target="/Game/MainContent/Maps/sublevel_plot/0-1/0-1_plot_outerRimA_interact1.0-1_plot_outerRimA_interact1:PersistentLevel.0-1_lootbox_01_mat_ST001"
function key(o)return o:GetFullName().."|"..o:GetAddress()end
record.actor=key(actor);record.component=key(component);record.widget=key(widget)
component.bVisible=false;component.bAddedToScreen=false
writes=0
p=Prehide.new({
 alive=alive,key=key,
 path=function(o)if o==actor then return target end
     if o==panel then return "WidgetTree.CanvasPanel_0" end
     return "other" end,
 class=function(o)if o==panel then return "/Script/UMG.CanvasPanel" end return "other" end,
 acquire=function()return record end,
 resolve_actor=function()return objects.actor end,
 matches_action=function()return record.action=="Open" end,
 supported=function()return not unsupported end,
 set=function(o,v)
   assert(in_pump and o==panel and alive(panel))
   writes=writes+1
   panel.RenderTransform.Translation={X=v.X,Y=v.Y}
   if after_write then after_write(v)end
 end,
 now=function()return clock end,
 mode="translation-test",
},function(e,msg)logs[#logs+1]=e.." "..msg end)
function select(a)
 in_pump=true
 local r=p.filter({status="READY",actor=a,key=a and key(a)})
 in_pump=false
 return r.actor
end
function restore()
 in_pump=true;p.restore("manual");in_pump=false
end
function tx()return panel.RenderTransform.Translation.X end
'''

class TipHUDRenderTranslation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dest = Path(tempfile.gettempdir()).resolve() / f"iip-translation-{uuid.uuid4().hex}"
        dest.mkdir()
        try:
            shutil.copytree(BASE / "Scripts", dest / "Scripts")
            for patch in ("first-show-observe.patch", "prehide-translation.patch"):
                subprocess.run(["git", "apply", "--unidiff-zero", str(OVERLAY / patch)],
                               cwd=dest, check=True)
            cls.scripts = {p.stem: p.read_text(encoding="utf-8")
                           for p in (dest / "Scripts").glob("*.lua")}
        finally:
            shutil.rmtree(dest)

    def case(self, content):
        vm=LuaRuntime()
        for name,src in self.scripts.items():
            vm.compile(src,name=name)
        source=ROOT.read_text(encoding="utf-8")
        vm.compile(source,name="IIPPrehideTranslation")
        vm.execute("Tint={new=function()return {}end}\n"
                   + "Prehide=(function()\n"+source+"\nend)()\n"
                   + RIG + ADAPTER + content)

    def test_single_early_write_two_approaches_and_exact_restore(self):
        self.case("""
p.begin(actor);assert(writes==0);select(nil)
assert(tx()==16384 and writes==1)
assert(select(actor)==actor);p.shown()
select(nil);assert(tx()==16384)
clock=101;assert(select(actor)==actor and writes==1)
restore()
assert(tx()==0 and writes==2)
assert(widget.ColorAndOpacity.A==.75)
assert(panel.RenderTransform.Scale.X==1 and panel.RenderTransform.Angle==0)
p.begin(actor);select(nil);assert(tx()==0 and writes==2)
""")

    def test_foreign_writer_original_present_no_overwrite(self):
        self.case("""
p.begin(actor);select(nil);assert(tx()==16384)
panel.RenderTransform.Translation.X=0
assert(not select(actor) and writes==1 and tx()==0)
assert(logs[#logs]:find("translation_changed"))
""")

    def test_foreign_writer_nonoriginal_no_overwrite(self):
        self.case("""
p.begin(actor);select(nil)
panel.RenderTransform.Translation.X=99
assert(not select(actor) and tx()==99 and writes==1)
assert(logs[#logs]:find("RESTORE_UNCONFIRMED"))
""")

    def test_unsupported_or_stale_early_pair(self):
        for setup in (
            "unsupported=true",
            'record.action="Take"',
            "component.bAddedToScreen=true",
            "component.bVisible=true",
            "tree.RootWidget=widget",
            "panel.live=false",
            "panel.RenderTransform.Translation.X=5000",
            "component.Widget=actor",
        ):
            with self.subTest(setup=setup):
                self.case(setup+"""
p.begin(actor);select(nil)
assert(writes==0)
""")

    def test_missing_subtree_or_partial_setter_rollback(self):
        self.case("""
tree.RootWidget=nil;p.begin(actor);select(nil);assert(writes==0)
""")
        self.case("""
after_write=function(v)if v.X>1000 then error("partial native setter")end end
p.begin(actor);select(nil)
assert(writes==2 and tx()==0)
assert(not select(actor))
""")

    def test_world_fallback_and_deadline(self):
        self.case("""
p.begin(actor);select(nil);assert(select(actor)==actor)
clock=100.5;assert(not select(actor) and writes==2 and tx()==0)
""")
        self.case("""
p.begin(actor);select(nil);unsupported=true
assert(not select(actor) and writes==2 and tx()==0)
""")

    def test_render_translation_independent_from_native_visibility_and_color(self):
        self.case("""
p.begin(actor);select(nil);assert(tx()==16384)
widget.ColorAndOpacity.A=1
assert(select(actor)==actor)
assert(component.bVisible==false and component.bAddedToScreen==false)
assert(widget.RenderOpacity==nil and panel.RenderTransform.Scale.X==1)
restore()
""")

    def test_patch_no_alpha_tint_writer_and_direct_brush(self):
        from pathlib import Path
        main=self.scripts["main"]
        self.assertIn('require("IIPPrehideTranslation")',main)
        self.assertIn('"/Script/UMG.Widget:SetRenderTranslation"',main)
        self.assertNotIn('"/Script/UMG.UserWidget:SetColorAndOpacity"',main)
        self.assertIn('world.direct_input(widget)',self.scripts["IIPSelectedWorldSession"])
        self.assertIn('prehide.filter(row)',self.scripts["IIPSelectedWorldSession"])
        self.assertIn('function M.direct_shown()',self.scripts["IIPWorldChild"])

if __name__ == "__main__":
    unittest.main()
