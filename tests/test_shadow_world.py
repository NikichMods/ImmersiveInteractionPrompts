# SPDX-License-Identifier: MPL-2.0
"""Assemble the isolated overlay and exercise the actual shadow session."""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import unittest
import uuid

from lupa import LuaRuntime
from test_tiphud_translation_cycle import BASE, OVERLAY


class ShadowWorld(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        work = Path(tempfile.gettempdir()).resolve() / f"iip-shadow-{uuid.uuid4().hex}"
        work.mkdir()
        try:
            shutil.copytree(BASE / "Scripts", work / "Scripts")
            for name in ("IIPShadowWorldSession", "IIPSelectedTipCapability", "IIPSelectedHintPreflight"):
                shutil.copyfile(OVERLAY / f"{name}.lua", work / "Scripts" / f"{name}.lua")
            for patch in ("first-show-observe.patch", "shadow-world.patch"):
                subprocess.run(["git", "apply", "--unidiff-zero", str(OVERLAY / patch)],
                               cwd=work, check=True,
                               env={**os.environ, "GIT_CEILING_DIRECTORIES": str(work.parent)})
            cls.scripts = {p.stem: p.read_text(encoding="utf-8")
                           for p in (work / "Scripts").glob("*.lua")}
        finally:
            assert work.name.startswith("iip-shadow-") and work.resolve().parent == work.parent
            shutil.rmtree(work)

    def test_entrypoint_is_standalone_and_direct_only(self):
        vm = LuaRuntime()
        for name, text in self.scripts.items():
            vm.compile(text, name=name)
        main = self.scripts["main"]
        self.assertIn('weak:Get()', main)
        self.assertIn('Session.start(World,{', main)
        self.assertIn('require("IIPShadowWorldSession")', main)
        self.assertIn('RegisterKeyBind(Key.F9,function()observer.stop("manual_f9")end)', main)
        self.assertNotIn("prehide", main)
        hint = self.scripts["IIPHintSource"]
        self.assertIn("Gate.direct_texture(child,alive)", hint)
        self.assertNotIn('result.mode="retained_mid"', hint)
        self.assertIn('b.bDisableDepthTest==false', self.scripts["IIPWorldChild"])

    def scenario(self, code):
        vm = LuaRuntime()
        vm.execute("""
local actor={id=7}
function actor:GetAddress()return self.id end
actor.ExtendedWidget={GetUserWidgetObject=function()return {}end}
selected={status="READY",actor=actor,key="selected",pawn_key="pawn",component_key="action"}
action="Knock"
gate="direct_brush_candidate"
package.loaded.IIPSelectedTipCapability={inspect_selected=function(a)
 assert(a==actor)
 return {actor="selected",component="source",widget="widget",action=action,
         refs={actor={address=a.id}}}
end}
package.loaded.IIPSelectedHintPreflight={inspect=function()return "metadata",gate end}
events={}
count,refreshes,cleanups=0,0,0
moving=false
world={
 empty=function()return not own end,
 prepare=function()assert(not prepared);prepared=true end,
 refresh_assets=function()assert(prepared)end,
 create=function(a,c,w,stop,tag,still_selected)
  assert(a==actor and c==actor.ExtendedWidget and w and tag==action)
  assert(not own and still_selected());own=true;count=count+1
 end,
 shadow_anchor_current=function()return not moving end,
 refresh=function()assert(own);refreshes=refreshes+1 end,
 cleanup=function(reason)own=false;cleanups=cleanups+1;return true end
}
api={
 read=function()return selected end,native_alive=function()return true end,
 hint_visible=function()return true end,
 loop=function(frames,fn)assert(frames==1);tick=fn;return 42 end,
 cancel=function(id)assert(id==42);cancelled=true;return true end
}
function log(event,fields)events[event]=fields end
function clear_selection()saved=selected;selected={status="READY"}end
""")
        vm.globals().Session = vm.execute(self.scripts["IIPShadowWorldSession"])
        vm.execute("observer=Session.start(world,api,log)\n" + code)

    def test_target_loss_and_f9_release_only_owned_world(self):
        self.scenario("""
tick();assert(own and count==1 and refreshes==1)
tick();assert(count==1 and refreshes==2)
clear_selection();tick();assert(not own and cleanups==1)
selected=saved;tick();assert(own and count==2)
observer.stop("manual_f9");tick();tick()
assert(not own and cleanups==2 and cancelled and not observer.status().active)
assert(events.STOP=="reason=manual_f9 cancelled=true cleanup_confirmed=true")
""")

    def test_capability_loss_leaves_stock_and_legacy_is_excluded(self):
        self.scenario("""
action="Open";tick();assert(count==0)
action="Talk"
for _,reason in ipairs({"hold","locked","unsupported_device","brush_not_direct","unavailable"}) do
 gate=reason;tick();assert(count==0)
end
gate="direct_brush_candidate";tick();assert(own)
gate="hold";tick();assert(not own and cleanups==1)
""")

    def test_anchor_drift_and_endplay_do_not_recreate_stale_world(self):
        self.scenario("""
tick();moving=true;tick();tick()
assert(not own and count==1 and events.RELEASED:find("anchor_moved",1,true))
clear_selection();tick();selected=saved;moving=false;tick();assert(own and count==2)
observer.ended(7);tick();tick()
assert(not own and count==2 and observer.status().active)
""")

    def test_partial_failure_reports_unconfirmed_cleanup(self):
        self.scenario("""
world.create=function()own=true;error("allocation failure")end
world.cleanup=function()return false end
tick();assert(cancelled and own and events.CLEANUP_PENDING)
assert(events.STOP=="reason=fault cancelled=true cleanup_confirmed=false")
""")


if __name__ == "__main__":
    unittest.main()
