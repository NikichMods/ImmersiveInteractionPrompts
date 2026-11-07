# SPDX-License-Identifier: MPL-2.0
"""Input observer policy and assembly against exact Selected-owner World files."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import uuid

from test_selected_owner_world import BASE, LuaRuntime

OVERLAY = BASE.parent / "tiphud-render-suppression"
RIG = """
time=100; events={}; reads=0; t=0
function object(name)
    return {IsValid=function()return true end,GetFullName=function()return name end,
        GetAddress=function()return 42 end}
end
w=object("TipHUD");w.CanHoldPress=true
local get=object("Function /Script/Engine.MaterialInstanceDynamic:K2_GetScalarParameterValue")
function get:type()return "UFunction" end
setmetatable(get,{__call=function(_,m,key)
    assert(m==s.resource and key=="t")
    reads=reads+1;return t
end})
local color={R=1,G=1,B=1,A=1}
s={mode="retained_mid",device=1,resource=object("MID"),texture=object("RT"),
    child={ColorAndOpacity=color},brush={UVRegion={bIsValid=0},
        ResourceObject=object("Keyboard"),ImageSize={X=64,Y=64},
        DrawAs=3,Tiling=0,Mirroring=0,ImageType=1,Margin={Left=0,Top=0,Right=0,Bottom=0},
        TintColor={ColorUseRule=0,SpecifiedColor=color}}}
o=Observer.new(function()return time end,function()return not missing and get end,
    function(key)return key end,function(e,fields)events[#events+1]=e.." "..fields end)
function step(action,ready)o.step(s,w,action or "Open",ready~=false)end
function batch()for i=1,6 do step()end end
"""


class HintInputObserver(unittest.TestCase):
    def test_overlay_applies_and_compiles(self):
        dest = Path(tempfile.gettempdir()).resolve() / f"iip-hint-{uuid.uuid4().hex}"
        dest.mkdir()
        try:
            shutil.copytree(BASE / "Scripts", dest / "Scripts")
            subprocess.run(
                ["git", "apply", "--unidiff-zero", str(OVERLAY / "stage-c-observe.patch")],
                cwd=dest, check=True,
            )
            lua = LuaRuntime()
            scripts = dest / "Scripts"
            for path in scripts.glob("*.lua"):
                lua.compile(path.read_text(encoding="utf-8"), name=path.name)
            self.assertEqual(
                {p.name for p in scripts.glob("*.lua") if p.read_bytes() != (BASE / "Scripts" / p.name).read_bytes()},
                {"main.lua", "IIPComposition.lua", "IIPHintSource.lua"},
            )
        finally:
            shutil.rmtree(dest)

    def case(self, body):
        vm = LuaRuntime()
        source = (OVERLAY / "IIPHintInputObserver.lua").read_text(encoding="utf-8")
        vm.execute("Observer=(function()\n" + source + "\nend)()\n" + RIG + body)

    def test_device_uv_and_hold_changes_with_deduplication(self):
        self.case("""
batch();assert(reads==0)
o.request();step();batch();assert(reads==2 and #events==2)
s.device=4;s.brush.ResourceObject=object("Controller")
s.brush.UVRegion={bIsValid=1,Min={X=0,Y=0},Max={X=.5,Y=.5}}
batch();assert(events[3]:find("device=4") and events[3]:find("uv=0,0,0.5,0.5",1,true))
t=.55;batch();assert(events[4]:find("t=0.55",1,true))
o.request();batch();assert(events[5]=="END reason=manual" and reads==4)
""")

    def test_scope_timeout_and_missing_api(self):
        self.case("""
o.request();step("Take");assert(reads==0)
o.request();step("Open",false);assert(reads==0)
o.request();time=102;step();assert(reads==0)
o.request();step();time=110;step();assert(reads==1 and events[#events]=="END reason=budget")
o.request();step();o.stop("world_hidden");batch();assert(reads==2)
o.request();missing=true;step();batch()
assert(reads==2 and events[#events]:find("scalar getter unavailable"))
""")


if __name__ == "__main__":
    unittest.main()
