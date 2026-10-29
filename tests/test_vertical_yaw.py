# SPDX-License-Identifier: MPL-2.0
"""Vertical yaw and bounded scheduler policy; not native cadence or visual proof."""
import unittest
from test_beginplay_join import FIXTURE
from test_world_child import EXTRA
from test_world_deferred import CONTEXT
from test_world_orientation import ORIENTATION
from test_ui_child import LuaRuntime, ROOT

DIR=ROOT/'research/interaction-prompts-owner/world-space/vertical-yaw/Scripts'
MAIN=(DIR/'main.lua').read_text(encoding='utf8')
MODULE=(DIR/'IIPWorldChild.lua').read_text(encoding='utf8')
FRAMES=r'''
S.loop_registered=0;S.cancel_calls=0;S.loop=nil;S.retired=0
function LoopInGameThreadAfterFrames(n,fn)
 assert(S.game and not S.in_script and n==1 and not S.loop)
 S.loop_registered=S.loop_registered+1;S.loop={fn=fn,handle=901};return 901
end
function CancelDelayedAction(h)
 S.cancel_calls=S.cancel_calls+1
 assert(h==901)
 if S.cancel_fail then return false end
 if S.loop and not S.loop.removed then S.loop.removed=true;return true end
 return false
end
function IsValidDelayedActionHandle(h)return S.loop and not S.loop.removed or false end
function yawframe(no_cleanup)
 if not S.loop then return end
 local a=S.loop;S.game=true;a.fn();S.game=false
 if a.removed then S.loop=nil;S.retired=S.retired+1 end
 if not no_cleanup then flush()end
end
'''

class VerticalYawPolicy(unittest.TestCase):
    def case(self,code,setup='',fixed=False):
        lua=LuaRuntime(unpack_returned_tuples=True)
        lua.execute(FIXTURE+EXTRA+CONTEXT+ORIENTATION+FRAMES)
        source=MODULE.replace('local FOLLOW_CAMERA=true','local FOLLOW_CAMERA=false') if fixed else MODULE
        lua.execute('package.preload["IIPWorldChild"]=function()\n'+source+'\nend')
        lua.execute(setup);lua.execute(MAIN)
        try:lua.execute(code)
        except Exception:
            print(list(lua.globals().S.logs.values())[-8:]);raise

    def test_initial_vertical_and_each_frame_even_stationary(self):
        self.case('start();assert(S.comp.transform.rotation.Pitch==0 and S.comp.transform.rotation.Roll==0);'
                  'for i=1,10 do yawframe()end;assert(S.sets==10 and S.loop_registered==1)')

    def test_yaw_quadrants_and_height_independence(self):
        self.case('start();for _,p in ipairs({{610,20,0},{10,620,90},{-590,20,180},{10,-580,-90}})do '
                  'S.camera={X=p[1],Y=p[2],Z=500};yawframe();assert(math.abs(S.comp.transform.rotation.Yaw-p[3])<0.001);'
                  'assert(S.comp.transform.rotation.Pitch==0 and S.comp.transform.rotation.Roll==0)end')

    def test_subdegree_change_has_no_threshold(self):
        self.case('start();yawframe();S.camera.Y=20.01;yawframe();assert(S.sets==2 and S.comp.transform.rotation.Yaw>0)')

    def test_wraparound_uses_short_error(self):
        self.case('start();S.camera={X=-590,Y=20.1,Z=162};yawframe();'
                  'S.camera.Y=19.9;yawframe();assert(not has("readback differs") and S.sets==2)')

    def test_degenerate_after_creation_keeps_last_yaw(self):
        self.case('start();orbit();yawframe();S.camera={X=10,Y=20,Z=500};yawframe();'
                  'assert(S.comp.transform.rotation.Yaw==90 and S.comp.transform.rotation.Pitch==0);key();assert(has("degenerate=1"))')

    def test_degenerate_initial_refuses_before_component_allocation(self):
        self.case('start();assert(not S.comp and S.loop_registered==0 and has("undefined at creation"))',
                  'S.camera={X=10,Y=20,Z=500}')

    def test_fixed_fallback_uses_initial_vertical_camera_yaw(self):
        self.case('start();orbit();for i=1,15 do yawframe()end;key();assert(S.sets==0 and S.comp.transform.rotation.Yaw==0 '
                  'and S.comp.transform.rotation.Pitch==0 and has("fixed_initial"))',fixed=True)

    def test_manual_f7_cancels_and_late_ready_callback_is_inert(self):
        self.case('start();local late=S.loop.fn;yawframe();S.keys[7]();'
                  'S.game=true;late();S.game=false;assert(S.sets==1);flush();assert(has("LOOP_CANCELLED") and has("CLEANED"));'
                  'S.game=true;late();S.game=false;yawframe();assert(S.sets==1 and S.loop==nil and S.retired==1)')

    def test_target_visibility_loss_stops_before_setter_between_full_checks(self):
        self.case('start();yawframe();set(P.component,"bAddedToScreen",false);yawframe();'
                  'assert(S.sets==1 and has("CLEANED") and has("LOOP_CANCELLED"))')

    def test_pending_kill_actor_camera_and_own_component(self):
        for obj in ['P.actor','S.objects["/World.Camera"]','S.comp']:
            self.case('start();yawframe();set('+obj+',"pending",true);yawframe();assert(S.sets==1 and has("CLEANED"))')

    def test_rebound_widget_stops_before_rotation(self):
        self.case('start();yawframe();set(P.component,"Widget",make("/Other.Widget",WIDGET));yawframe();assert(S.sets==1 and has("CLEANED"))')

    def test_full_topology_check_runs_every_twelve_frames(self):
        self.case('start();yawframe();set(P.actor,"RootComponent",make("/Other.Root","Root"));'
                  'for i=2,12 do yawframe()end;assert(S.sets==12);yawframe();assert(S.sets==12 and has("CLEANED"))')

    def test_source_anchor_movement_stops_periodic_check(self):
        self.case('start();yawframe();set(P.component,"K2_GetComponentLocation",function()return {X=11,Y=20,Z=30}end);'
                  'for i=2,13 do yawframe()end;assert(has("anchor moved") and has("CLEANED"))')

    def test_rotation_failure_stops_and_cancels(self):
        self.case('start();yawframe();assert(has("rotation setter failure") and has("CLEANED") and S.loop==nil)',
                  'S.setter_fail=true')

    def test_timeout_cancels_existing_loop(self):
        self.case('start();S.now=S.now+45;yawframe();assert(has("orientation_timeout") and has("CLEANED") and S.loop==nil)')

    def test_frame_cap_and_no_reregistration(self):
        self.case('start();for i=1,12001 do yawframe()end;key();assert(S.sets==12000 and S.loop_registered==1 '
                  'and has("orientation_budget") and has("CLEANED"))')

    def test_cancel_failure_is_explicit_inert_and_f7_retries(self):
        self.case('start();yawframe();S.cancel_fail=true;key(7);assert(has("LOOP_CANCEL_PENDING") and has("CLEANED"));'
                  'yawframe();assert(S.sets==1);S.cancel_fail=false;key(7);yawframe();assert(S.loop==nil)')

    def test_missing_frame_api_refuses_before_hooks(self):
        self.case('assert(has("UNAVAILABLE") and S.loop_registered==0)', 'LoopInGameThreadAfterFrames=nil')

    def test_nonfinite_camera_safe_failure(self):
        self.case('start();yawframe();S.camera.X=0/0;yawframe();assert(S.sets==1 and has("CLEANED"))')

    def test_native_timeout_also_cancels_the_loop(self):
        self.case('start();timeout(45000);flush();yawframe();assert(has("reason=world_timeout") '
                  'and has("LOOP_CANCELLED") and has("CLEANED") and S.loop==nil)')

    def test_registration_failure_cleans_without_automatic_retry(self):
        self.case('start();key();assert(has("frame registration failure") and has("CLEANED") '
                  'and S.loop_registered==1)',
                  'LoopInGameThreadAfterFrames=function()S.loop_registered=S.loop_registered+1;error("frame registration failure")end')

    def test_fast_frame_lookup_and_validity_call_budget(self):
        self.case('start();yawframe();local lookup=StaticFindObject;S.lookups=0;'
                  'StaticFindObject=function(...)S.lookups=S.lookups+1;return lookup(...)end;'
                  'yawframe();assert(S.lookups==8 and S.sets==2)')

if __name__=='__main__':unittest.main()
