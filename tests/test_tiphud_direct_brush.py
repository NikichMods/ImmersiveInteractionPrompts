# SPDX-License-Identifier: MPL-2.0
"""Assemble the exact overlays and exercise the real World/hint path."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import uuid

from test_selected_owner_world import BASE, LuaRuntime, host
from test_tiphud_tint import OVERLAY, RIG, MOCK

DIRECT_INPUT = """
local b=S.source_image.Brush
b.ImageSize={X=64,Y=64};b.UVRegion={bIsValid=0}
b.Tiling=0;b.Mirroring=0;b.ImageType=0
b.Margin={Left=0,Top=0,Right=0,Bottom=0}
b.TintColor.SpecifiedColor={R=1,G=1,B=1,A=1}
set(P.widget,"CanHoldPress",false)
set(P.widget,"ImageInteractAllowed",S.source_image)
S.lock=owned("/Tip.Lock","/Script/UMG.CanvasPanel",P.widget.WidgetTree)
S.lock.Visibility=1
set(P.widget,"CanvasPanel_2",S.lock)
set(P.text,"Visibility",0);set(P.text,"RenderOpacity",1);set(P.text,"bIsEnabled",true)
World.prepare();World.refresh_assets()
assert(World.create(P.actor,P.component,P.widget,function()end,"Open",function()return true end)~=false)
assert(World.resume())
function settle_direct()for i=1,4 do assert(World.refresh()) end end
"""


class DirectBrush(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dest = Path(tempfile.gettempdir()).resolve() / f"iip-direct-{uuid.uuid4().hex}"
        dest.mkdir()
        try:
            shutil.copytree(BASE / "Scripts", dest / "Scripts")
            for name in ("stage-a.patch", "direct-brush.patch"):
                subprocess.run(["git", "apply", "--unidiff-zero", str(OVERLAY / name)],
                               cwd=dest, check=True)
            cls.scripts = {p.stem: p.read_text(encoding="utf-8")
                           for p in (dest / "Scripts").glob("*.lua")}
            cls.scripts["IIPTipHUDTint"] = (OVERLAY / "IIPTipHUDTint.lua").read_text(encoding="utf-8")
        finally:
            shutil.rmtree(dest)

    def world(self, body):
        vm = LuaRuntime(unpack_returned_tuples=True)
        vm.execute(host.FIXTURE + host.EXTRA + host.CONTEXT + host.ORIENTATION
                   + host.FRAMES + host.HINT_FIXTURE + host.LIVE + host.MEASURED + host.STYLE)
        for name, source in self.scripts.items():
            vm.compile(source, name=name)
            if name != "main":
                body_source = host.RESOURCES if name == "IIPResources" else source
                vm.execute(f'package.preload["{name}"]=function()\n{body_source}\nend')
        vm.execute(host.SETUP + DIRECT_INPUT + body)

    def test_live_brush_change_preserves_visibility_and_tuned_slot(self):
        self.world("""
settle_direct()
local hint=S.hint
assert(World.shown() and hint.Brush.ResourceObject==S.raw and S.mat_sets==0 and S.brush_sets==1)
local size=hint.Slot:GetSize()
local brightness=hint.ColorAndOpacity.R
set(P.widget,"ColorAndOpacity",{R=1,G=1,B=1,A=0})
S.retainer.GetEffectMaterial=function()error("direct path must not read MID")end
S.device=4
assert(World.refresh() and S.brush_sets==1 and hint.Visibility==3)
local new=owned("/Hint.Gamepad","/Script/Engine.Texture2D")
S.source_image.Brush.ResourceObject=new
assert(World.refresh() and S.brush_sets==2 and hint.Brush.ResourceObject==new and hint.Visibility==3)
assert(World.shown() and hint.Slot:GetSize().X==size.X and hint.Slot:GetSize().Y==size.Y)
assert(hint.ColorAndOpacity.R==brightness and hint.ColorAndOpacity.A==1)
assert(World.refresh() and S.brush_sets==2 and S.source_image.Brush.ResourceObject==new)
assert(World.cleanup("done") and hint.Brush.ResourceObject==nil and S.source_image.Brush.ResourceObject==new)
""")

    def test_hold_lock_or_unknown_shape_disarms_suppression(self):
        for change in (
            'set(P.widget,"CanHoldPress",true)',
            'S.lock.Visibility=0',
            'S.source_image.Brush.UVRegion.bIsValid=1',
        ):
            with self.subTest(change=change):
                self.world("""
settle_direct();assert(World.shown())
""" + change + """
assert(World.refresh() and not World.shown())
settle_direct()
assert(S.hint.Brush.ResourceObject==S.hint_mid and not World.shown())
assert(World.cleanup("done"))
""")

    def test_tint_pump_refuses_unready_and_restores_on_loss(self):
        vm = LuaRuntime()
        vm.execute("Tint=(function()\n" + self.scripts["IIPTipHUDTint"] + "\nend)()\n" + RIG)
        vm.execute("Session=(function()\n" + self.scripts["IIPSelectedWorldSession"] + "\nend)()")
        vm.execute(MOCK.replace("o=Session.start", """
api.tint=tint
world.shown=function()return direct_ready end
source.acquire=function(a)
    record.actor=a.key
    return record
end
o=Session.start""") + """
function step()
    in_pump=true;select_owner(A);in_pump=false
end
step()
tint.request();step();step();assert(writes==0)
direct_ready=true;tint.request();step();step();assert(alpha()==0)
direct_ready=false;step();assert(alpha()==.75 and writes==2)
""")


if __name__ == "__main__":
    unittest.main()
