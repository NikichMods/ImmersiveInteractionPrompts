# SPDX-License-Identifier: MPL-2.0
"""Bounded read-only CanShow facing observer: tests emulate only observation."""
import unittest
from lupa import LuaRuntime
from test_ui_child import ROOT

ROOT_SCRIPT = ROOT / "research/interaction-prompts-owner/world-space/native-world-template/Scripts"
SOURCE = (ROOT_SCRIPT / "IIPTemplateFacingObserver.lua").read_text(encoding="utf8")
MAIN = (ROOT_SCRIPT / "main.lua").read_text(encoding="utf8")

FIXTURE = r"""
S={log={},setter_calls=0,cam={X=100,Y=0,Z=100},yaw=0}
function log(event,detail) S.log[#S.log+1]=event.." "..detail end
local manager={IsValid=function()return true end,GetCameraLocation=function()return S.cam end}
S.component={
    bVisible=true,IsValid=function()return true end,
    K2_GetComponentLocation=function()return {X=0,Y=0,Z=0} end,
    K2_GetComponentRotation=function()return {Pitch=0,Yaw=S.yaw,Roll=0} end,
    K2_SetWorldRotation=function()S.setter_calls=S.setter_calls+1;error("read-only violation")end}
S.widget={RenderOpacity=1,IsValid=function()return true end,
    GetOwningPlayerCameraManager=function()return manager end}
S.info={actor="/Game/Test.Level:NPC",observer_kind="npc"}
function has(x)
    for _,s in ipairs(S.log) do if s:find(x,1,true) then return true end end
    return false
end
"""

class FacingObserverTests(unittest.TestCase):
    def run_lua(self, body):
        lua = LuaRuntime()
        lua.execute(FIXTURE)
        lua.execute("M=(function()\n" + SOURCE + "\nend)()")
        lua.execute(body)

    def test_off_by_default_and_read_only_then_f5_summary(self):
        self.run_lua("""
            local m=M.new(log)
            m:sample(S.info,S.component,S.widget)
            assert(#S.log==0)
            assert(m:toggle())
            for i=1,9 do m:sample(S.info,S.component,S.widget) end
            S.cam={X=0,Y=100,Z=100}
            for i=1,8 do m:sample(S.info,S.component,S.widget) end
            assert(not m:toggle())
            assert(has("FACING_OBS_RESULT kind=npc") and has("calls=17"))
            assert(has("camera_moves=1") and has("widget_moves=0"))
            assert(has("max_step=90.0") and S.setter_calls==0)
            m:sample(S.info,S.component,S.widget)
            assert(#S.log==3)
        """)

    def test_no_false_hidden_transition_when_no_canshow_during_hide(self):
        self.run_lua("""
            local m=M.new(log);m:toggle()
            m:sample(S.info,S.component,S.widget)
            S.component.bVisible=false
            -- No native CanShow while hidden; no fabricated hidden event.
            S.component.bVisible=true
            m:sample(S.info,S.component,S.widget)
            m:toggle()
            assert(has("visible_false=0 flips=0"))
            assert(S.setter_calls==0)
        """)

    def test_visibility_opacity_are_read_as_separate_signals(self):
        self.run_lua("""
            local m=M.new(log);m:toggle()
            m:sample(S.info,S.component,S.widget)
            S.component.bVisible=false;S.widget.RenderOpacity=0
            m:sample(S.info,S.component,S.widget)
            S.component.bVisible=true;S.widget.RenderOpacity=1
            m:sample(S.info,S.component,S.widget)
            m:toggle()
            assert(has("calls=3 visible_true=2 visible_false=1 flips=2"))
            assert(has("opacity_zero=1 opacity_positive=2"))
        """)

    def test_excludes_unscoped_actors_and_limits_actor_records(self):
        self.run_lua("""
            local m=M.new(log);m:toggle()
            m:sample({actor="other"},S.component,S.widget)
            for i=1,26 do
                m:sample({actor="actor"..i,observer_kind="possible_door"},
                    S.component,S.widget)
            end
            assert(#m.order==24 and m.dropped==2)
            m:toggle()
            assert(has("FACING_OBS_STOP actors=24 dropped=2"))
            assert(S.setter_calls==0)
        """)

    def test_null_camera_does_not_block_native_execution_or_invent_pose(self):
        self.run_lua("""
            local m=M.new(log);m:toggle()
            S.widget.GetOwningPlayerCameraManager=function()return nil end
            m:sample(S.info,S.component,S.widget)
            m:toggle()
            assert(has("calls=1") and has("poses=0"))
            assert(has("pose_errors=1") and S.setter_calls==0)
        """)

    def test_observer_uses_existing_hook_and_f5_no_new_scheduler(self):
        self.assertIn('pcall(facing_observer.sample,facing_observer,info,component,widget)', MAIN)
        self.assertIn('pcall(facing_observer.toggle,facing_observer)', MAIN)
        self.assertEqual(MAIN.count('RegisterHook,TIP..":CanShow"'), 1)
        self.assertNotIn("LoopInGameThreadAfterFrames", SOURCE)
        self.assertNotIn("SetWorldRotation", SOURCE)
        self.assertNotIn("SetShow(", SOURCE)
        self.assertNotIn("RegisterHook(", SOURCE)

    def test_billboard_layout_projects_anchors_once_at_the_same_height(self):
        self.run_lua("""
            local m=M.new(log)
            local calls=0
            local function valid()return true end
            local ctrl={IsValid=valid,ProjectWorldLocationToScreen=function(_,p,out,relative)
                assert(p.Z==100 and relative==false)
                out.X=p.X*2
                calls=calls+1
                return true
            end}
            S.widget.GetOwningPlayer=function()return ctrl end
            S.component.GetOwner=function()
                return {IsValid=valid,K2_GetActorLocation=function()return {X=100,Y=0,Z=0} end}
            end
            S.component.GetAttachParent=function()
                return {IsValid=valid,K2_GetComponentLocation=function()return {X=95,Y=0,Z=60} end}
            end
            S.component.K2_GetComponentLocation=function()return {X=90,Y=0,Z=100} end
            S.component.GetPivot=function()return {X=.5,Y=.5} end
            S.component.GetCurrentDrawSize=function()return {X=1000,Y=1000} end
            S.info.orientation="billboard"
            m:toggle()
            S.component.bVisible=false
            m:sample(S.info,S.component,S.widget)
            assert(calls==0)
            S.component.bVisible=true
            for i=1,10 do m:sample(S.info,S.component,S.widget) end
            assert(calls==3 and S.setter_calls==0)
            assert(has("actor_at_tip_x=200.0 parent_at_tip_x=190.0 component_x=180.0"))
            assert(has("pivot_u=500.0 draw_w=1000"))
            m:toggle()
        """)

if __name__ == "__main__":
    unittest.main()
