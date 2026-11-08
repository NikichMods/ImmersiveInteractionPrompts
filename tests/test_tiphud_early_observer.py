# SPDX-License-Identifier: MPL-2.0
"""Early TipHUD observer assembly and read-only correlation."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import uuid

from test_selected_owner_world import BASE, LuaRuntime
from test_tiphud_tint import OVERLAY

RIG = """
logs={}
function object(id)
    return {id=id,GetAddress=function(self)return self.id end}
end
actor,comp,w,tex=object(1),object(2),object(3),object(4)
actor.ExtendedWidget=comp
actor.TipHUDArgument={msgTag={ToString=function()return "Open" end}}
comp.Widget=w
function comp:GetUserWidgetObject()return self.Widget end
function comp:GetWidgetSpace()return 1 end
comp.bVisible=false;comp.bAddedToScreen=false
w.CanHoldPress=false
w.CanvasPanel_2={Visibility=1}
w.ImageInteractAllowed={Visibility=0,Brush={UVRegion={bIsValid=0}}}
w.ColorAndOpacity={R=1,G=1,B=1,A=1}
local empty={IsValid=function()return false end,GetAddress=function()return 0 end}
w.ColorAndOpacityDelegate={Object=empty,FunctionName={ToString=function()return "None" end}}
local function key(o)return "identity|"..o.id end
local function path(o)
    return o==actor and "/Game/MainContent/Maps/sublevel_plot/0-1/0-1_plot_outerRimA_interact1.0-1_plot_outerRimA_interact1:PersistentLevel.0-1_lootbox_01_mat_ST001" or "other"
end
local source={acquire=function(a)
    assert(a==actor)
    if not comp.Widget then return nil,"not_ready_widget" end
    return {widget=key(comp.Widget),component=key(comp)}
end}
function show()
    comp.bVisible=true;comp.bAddedToScreen=true
    w.ImageInteractAllowed.Brush.ResourceObject=tex
end
obs=Early.new(source,function(o)return o~=nil end,path,key,function()return true end,
    function(e,fields)logs[#logs+1]=e.." "..fields end)
"""


class EarlyTipObserver(unittest.TestCase):
    def test_patch_and_modules_compile(self):
        dest = Path(tempfile.gettempdir()).resolve() / f"iip-early-{uuid.uuid4().hex}"
        dest.mkdir()
        try:
            shutil.copytree(BASE / "Scripts", dest / "Scripts")
            subprocess.run(["git", "apply", "--unidiff-zero", str(OVERLAY / "first-show-observe.patch")],
                           cwd=dest, check=True)
            subprocess.run(["git", "apply", "--unidiff-zero", str(OVERLAY / "early-tip-observe.patch")],
                           cwd=dest, check=True)
            vm = LuaRuntime()
            for file in (dest / "Scripts").glob("*.lua"):
                vm.compile(file.read_text(encoding="utf-8"), name=file.name)
            entry = (dest / "Scripts/main.lua").read_text(encoding="utf-8")
            self.assertIn("early.begin(candidate)", entry)
            self.assertIn("early.read(actor)", entry)
            self.assertNotIn("SetColorAndOpacity", entry)
        finally:
            shutil.rmtree(dest)

    def case(self, body):
        vm = LuaRuntime()
        lua = (OVERLAY / "IIPEarlyTipHUDObserver.lua").read_text(encoding="utf-8")
        vm.execute("Early=(function()\n" + lua + "\nend)()\n" + RIG + body)

    def test_early_pair_with_late_brush_and_two_episodes(self):
        self.case("""
obs.begin(object(7));assert(#logs==0)
obs.begin(actor);obs.begin(actor)
assert(#logs==1 and logs[1]:find("added=false") and logs[1]:find('brush="-"',1,true))
assert(logs[1]:find("binding=empty") and logs[1]:find("hold=false"))
obs.read(actor);assert(#logs==2 and logs[2]:find("early_match=true"))
show();obs.read(actor);obs.read(actor)
assert(#logs==3 and logs[3]:find("SCREEN_READY") and logs[3]:find("identity|4",1,true))
obs.read(nil);obs.read(actor)
assert(#logs==5 and logs[5]:find("episode=2"))
obs.read(nil);obs.read(actor);assert(#logs==5)
assert(w.ColorAndOpacity.A==1 and comp.bVisible and comp.bAddedToScreen)
""")

    def test_replacement_and_ended_invalidate_correlation(self):
        self.case("""
obs.begin(actor)
comp.NewUserWidget=object(8);show();obs.read(actor)
assert(logs[2]:find("early_match=false") and logs[2]:find("identity|8",1,true))
obs.ended(1);obs.read(nil);obs.read(actor)
assert(logs[4]:find("early_match=unknown"))
obs.reset();obs.read(actor);assert(logs[6]:find("episode=1"))
""")

    def test_unavailable_widget_and_bounded_wait(self):
        self.case("""
comp.Widget=nil;obs.begin(actor);obs.read(actor)
assert(logs[1]:find("not_ready_widget"))
for i=1,140 do obs.read(actor) end
assert(#logs==3 and logs[3]:find("SCREEN_UNOBSERVED"))
""")


if __name__ == "__main__":
    unittest.main()
