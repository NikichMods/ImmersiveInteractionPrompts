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
            for patch in ("first-show-observe.patch", "shadow-world.patch",
                          "shadow-visual-observe.patch", "shadow-host-reload.patch",
                          "shadow-all-actions.patch", "shadow-warmup-ab.patch"):
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
        self.assertIn('RegisterKeyBind(Key.F9,function()observer.on_f9()end)', main)
        self.assertIn('},log,true)', main)
        self.assertIn('on_f9=function()', self.scripts["IIPShadowWorldSession"])
        self.assertNotIn("prehide", main)
        self.assertIn("IIP_SHADOW_LAYOUT_WARN", self.scripts["IIPTuning"])
        self.assertIn('emit("CANDIDATE"', self.scripts["IIPShadowWorldSession"])
        self.assertIn("local ALL_SELECTED_ACTIONS=true", self.scripts["IIPShadowWorldSession"])
        self.assertIn("not ALL_SELECTED_ACTIONS and legacy[row.action]", self.scripts["IIPShadowWorldSession"])
        self.assertNotIn("host recovery already consumed", self.scripts["IIPWorldChild"])
        self.assertIn("host_recovery_count=host_recovery_count+1", self.scripts["IIPWorldChild"])
        hint = self.scripts["IIPHintSource"]
        self.assertIn("Gate.direct_texture(child,alive)", hint)
        self.assertNotIn('result.mode="retained_mid"', hint)
        self.assertIn('b.bDisableDepthTest==false', self.scripts["IIPWorldChild"])

    def scenario(self, code, all_selected=True, paused=False):
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
 loop=function(frames,fn)assert(frames==1);tick=fn;loop_calls=(loop_calls or 0)+1;return 42 end,
 cancel=function(id)assert(id==42);cancelled=true;return true end
}
function log(event,fields)events[event]=fields end
function clear_selection()saved=selected;selected={status="READY"}end
""")
        session=self.scripts["IIPShadowWorldSession"]
        if not all_selected:
            session=session.replace("local ALL_SELECTED_ACTIONS=true",
                                    "local ALL_SELECTED_ACTIONS=false")
        vm.globals().Session = vm.execute(session)
        vm.execute("observer=Session.start(world,api,log," +
                   ("true" if paused else "false") + ")\n" + code)

    def test_shadow_layout_warnings_do_not_block_visual_observation(self):
        vm = LuaRuntime()
        vm.globals().Tuning = vm.execute(self.scripts["IIPTuning"])
        vm.execute("""
local s=Tuning.new()
s.hint_size=128;s.hint_gap=2;s.hint_y=-50;s.divider_y=20
local plan,reason=Tuning.plan(s,{X=650,Y=65},{X=200,Y=50},{X=64,Y=64})
assert(plan and not reason,"visual overlap cannot abort shadow observation")
assert(plan.upper and plan.lower and plan.hint and plan.divider)
local ok=pcall(Tuning.plan,s,{X=0,Y=65},{X=200,Y=50},{X=64,Y=64})
assert(not ok,"invalid native extents must remain fatal")
""")

    def test_exact_host_reload_on_multiple_clean_world_creations(self):
        # Run the assembled Lua function, not a reimplementation of its policy.
        body=self.scripts["IIPWorldChild"]
        segment=body[body.index("local function asset(p)"):body.index("local function xyz(")]
        vm=LuaRuntime(unpack_returned_tuples=True)
        vm.execute("""
HOST="HostClass";MASK="Other";prepared=true;assets_refreshed=true
state=nil;host_recovery_count=0;loaded=false;calls=0
klass={}
function klass:GetSuperStruct()return {}end
function valid(o)return o~=nil end
function path(o)return "/Script/UMG.UserWidget"end
function same(a,b)return a==b end
function inspected(p,name,stage)
 assert(p==HOST and name=="host")
 return loaded and klass or nil, loaded and "LIVE" or "ABSENT_NULL"
end
function step(n,fn,...)return fn(...)end
function LoadAsset(p)
 assert(p==HOST)
 calls=calls+1;loaded=true
 return klass,true,true
end
function resource_state(obj,p)
 assert(p==HOST)
 return loaded and obj==klass and "LIVE" or "ABSENT_NULL"
end
function log()end
""")
        vm.globals().recover=vm.execute(segment+"\nreturn asset")
        vm.execute("""
assert(recover(HOST)==klass and calls==1 and host_recovery_count==1)
loaded=false;state=nil
assert(recover(HOST)==klass and calls==2 and host_recovery_count==2)
loaded=false;state=nil
assert(recover(HOST)==klass and calls==3 and host_recovery_count==3)
assert(recover(HOST)==klass and calls==3)
loaded=false;state={}
assert(not pcall(recover,HOST) and calls==3)
""")

    def test_start_paused_no_polling_until_first_f9_then_cleanup_on_second_f9(self):
        self.scenario("""
assert(observer.status().active and not observer.status().polling)
assert(loop_calls==nil and tick==nil and count==0 and not own)
observer.on_f9()
assert(observer.status().polling and loop_calls==1 and type(tick)=="function")
tick();assert(own and count==1)
observer.on_f9();tick()
assert(not observer.status().active and not observer.status().polling)
assert(not own and cleanups==1 and cancelled)
assert(events.ACTIVATED and events.STOP=="reason=manual_f9 cancelled=true cleanup_confirmed=true")
""", paused=True)

    def test_abort_while_paused_does_not_schedule_any_callbacks(self):
        self.scenario("""
assert(not observer.status().polling and loop_calls==nil)
observer.stop("registration_failed")
assert(not observer.status().active and loop_calls==nil and not cancelled)
assert(events.STOP=="reason=registration_failed cancelled=true cleanup_confirmed=true")
""", paused=True)

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

    def test_all_selected_action_families_can_create_shadow_without_native_changes(self):
        self.scenario("""
for _,tag in ipairs({"Open","Take","Check","Interact","Talk","Knock","Press"}) do
 action=tag;gate="direct_brush_candidate"
 tick();assert(own and count>0)
 clear_selection();tick();assert(not own)
 selected=saved
end
assert(count==7 and cleanups==7)
assert(not cancelled)
observer.stop("manual_f9");tick()
assert(cancelled and events.STOP=="reason=manual_f9 cancelled=true cleanup_confirmed=true")
""")

    def test_capability_loss_preserves_screen_and_only_own_world_is_cleaned(self):
        self.scenario("""
action="Open";tick();assert(own and count==1)
for _,reason in ipairs({"hold","locked","unsupported_device","brush_not_direct","unavailable"}) do
 gate=reason;tick();assert(not own and count==1)
end
action="Talk";gate="direct_brush_candidate";tick();assert(own and count==2)
gate="hold";tick();assert(not own and cleanups==2)
""")

    def test_switch_off_excludes_only_legacy_actions(self):
        self.scenario("""
for _,tag in ipairs({"Open","Take","Check"}) do
 action=tag;tick();assert(count==0)
end
action="Knock";tick();assert(own and count==1)
""", all_selected=False)

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
