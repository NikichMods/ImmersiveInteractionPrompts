# SPDX-License-Identifier: MPL-2.0
"""Bounded camera comparison policy. No native rotation/marshalling or visual PASS."""
import unittest
from test_beginplay_join import FIXTURE
from test_world_child import EXTRA
from test_world_deferred import CONTEXT
from test_ui_child import LuaRuntime, ROOT

DIR=ROOT/'research/interaction-prompts-owner/world-space/orientation/Scripts'
MAIN=(DIR/'main.lua').read_text(encoding='utf8')
MODULE=(DIR/'IIPWorldChild.lua').read_text(encoding='utf8')
ORIENTATION=r'''
Key.F6=6;S.camera={X=610,Y=20,Z=162};S.sets=0
local setter=make('/Script/Engine.SceneComponent:K2_SetWorldRotation','Function')
set(setter,'type',function()return 'UFunction'end)
set(S.objects['/World.Camera'],'GetCameraLocation',function()return S.camera end)
local look=S.objects['/Script/Engine.KismetMathLibrary:FindLookAtRotation']
getmetatable(look).__call=function(_,cdo,a,b)
 local x,y,z=b.X-a.X,b.Y-a.Y,b.Z-a.Z
 return {Pitch=math.deg(math.atan(z,math.sqrt(x*x+y*y))),Yaw=math.deg(math.atan(y,x)),Roll=0}
end
function ExecuteInGameThreadWithDelay(ms,fn)
 assert(S.game and (ms==100 or ms==45000 or ms==120000))
 S.timers[#S.timers+1]={ms=ms,fn=fn}
end
local construct=StaticConstructObject
function StaticConstructObject(...)
 local o=construct(...)
 if o==S.comp then
  o.K2_SetWorldRotation=function(_,r,sweep,hit,teleport)
   assert(S.game and not S.in_script and o==S.comp and o.registered)
   assert(sweep==false and type(hit)=='table' and next(hit)==nil and teleport==true)
   S.sets=S.sets+1
   if S.setter_fail then error('rotation setter failure')end
   o.transform.rotation={Pitch=r.Pitch,Yaw=r.Yaw,Roll=r.Roll}
   if S.move_on_set then local p=o.transform.position;o.transform.position={X=p.X+1,Y=p.Y,Z=p.Z} end
  end
 end
 return o
end
function pulse(no_flush)
 local found
 for i,t in ipairs(S.timers)do if t.ms==100 then table.remove(S.timers,i);found=t;break end end
 assert(found,'no pending orientation timer');S.game=true;found.fn();S.game=false
 if not no_flush then flush()end
end
function pending_poll_timers()
 local n=0;for _,t in ipairs(S.timers)do if t.ms==100 then n=n+1 end end;return n
end
function orbit()S.camera={X=10,Y=620,Z=162}end
'''

class WorldOrientationPolicy(unittest.TestCase):
    def case(self,code,setup=''):
        lua=LuaRuntime(unpack_returned_tuples=True)
        lua.execute(FIXTURE+EXTRA+CONTEXT+ORIENTATION)
        lua.execute('package.preload["IIPWorldChild"]=function()\n'+MODULE+'\nend')
        lua.execute(setup);lua.execute(MAIN)
        try:lua.execute(code)
        except Exception:
            print(list(lua.globals().S.logs.values())[-12:]);raise

    def test_fixed_baseline_monitors_but_never_sets_rotation(self):
        self.case("start();orbit();pulse();frame();key();assert(S.sets==0 and has('mode=fixed') and has('ORIENT_SAMPLE'));key(7);assert(has('reason=user') and has('CLEANED'));pulse();assert(pending_poll_timers()==0)")

    def test_follow_rotates_only_own_registered_component_and_freezes_on_toggle(self):
        self.case("start();orbit();key(6);pulse();assert(S.sets==1 and math.abs(S.comp.transform.rotation.Yaw-90)<0.001);pulse();assert(S.sets==1);key(6);S.camera={X=610,Y=20,Z=162};pulse();assert(S.sets==1);key(7);pulse();assert(has('CLEANED'))")

    def test_delay_only_queues_explicit_engine_tick_before_write(self):
        self.case("start();key(6);orbit();pulse(true);assert(S.sets==0 and #S.queue==1);flush();assert(S.sets==1 and pending_poll_timers()==1)")

    def test_no_accumulating_timers_or_stationary_writes(self):
        self.case("start();key(6);for i=1,20 do assert(pending_poll_timers()==1);pulse()end;assert(S.sets==0);key(7);pulse();assert(pending_poll_timers()==0)")

    def test_sub_degree_jitter_does_not_invoke_setter(self):
        self.case("start();key(6);S.camera.Y=21;pulse();assert(S.sets==0)")

    def test_original_hidden_without_canshow_event_stops_and_cleans(self):
        self.case("start();set(P.widget,'Visibility',2);pulse();assert(S.comp.pending and has('FAILED') and has('CLEANED'));assert(pending_poll_timers()==0)")

    def test_source_actor_destroyed_stops_before_any_write(self):
        self.case("start();key(6);orbit();set(P.actor,'live',false);pulse();assert(S.sets==0 and has('CLEANED'));assert(pending_poll_timers()==0)")

    def test_changed_component_widget_identity_stops(self):
        self.case("start();set(P.component,'Widget',make('/Other.UI',WIDGET));pulse();assert(S.sets==0 and has('CLEANED'))")

    def test_known_different_screen_added_open_stops_without_retarget(self):
        self.case("key();begin();begin(Q);show();flush();show(Q);flush();assert(has('reason=other_visible_open') and S.created==1 and has('CLEANED'))",'Q=pair(2)')

    def test_known_other_widget_not_screen_added_does_not_false_stop(self):
        self.case("key();begin();begin(Q);show();flush();show(Q);flush();assert(not has('other_visible_open') and not S.comp.pending);key(7)","Q=pair(2);set(Q.component,'bAddedToScreen',false)")

    def test_camera_manager_change_and_range_are_refused(self):
        self.case("start();set(S.objects['/World.Camera'],'live',false);pulse();assert(has('camera manager') and has('CLEANED'))")
        self.case("start();S.camera={X=5000,Y=20,Z=162};pulse();assert(has('camera distance') and has('CLEANED'))")

    def test_near_vertical_camera_refused(self):
        self.case("start();S.camera={X=10,Y=20,Z=662};pulse();assert(has('near vertical') and S.sets==0 and has('CLEANED'))")

    def test_setter_failure_triggers_deferred_cleanup(self):
        self.case("start();key(6);orbit();pulse();assert(has('rotation setter failure') and has('CLEANED'))",'S.setter_fail=true')

    def test_setter_position_side_effect_is_detected(self):
        self.case("start();key(6);orbit();pulse();assert(has('own position changed') and has('CLEANED'))",'S.move_on_set=true')

    def test_missing_rotation_metadata_refuses_before_hook_registration(self):
        self.case("key();assert(S.registered==0 and not S.comp and has('rotation API unavailable'))","S.objects['/Script/Engine.SceneComponent:K2_SetWorldRotation']=nil")

    def test_late_timer_and_queued_update_inert_after_manual_stop(self):
        self.case("start();key(6);orbit();pulse(true);S.keys[7]();flush();assert(S.sets==0 and has('CLEANED'));assert(S.sets==0 and pending_poll_timers()==0)")

    def test_hard_poll_cap_stops_without_wall_clock_progress(self):
        self.case("start();for i=1,450 do pulse()end;assert(has('reason=orientation_budget') and has('CLEANED') and pending_poll_timers()==0)")

    def test_wall_deadline_and_native_world_timeout_both_stop_updates(self):
        self.case("start();S.now=S.now+45;pulse();assert(has('reason=orientation_timeout') and has('CLEANED'))")
        self.case("start();timeout(45000);flush();pulse();assert(has('CLEANED') and pending_poll_timers()==0)")

    def test_dispatch_failure_is_inert_and_explicit_cleanup_can_retry(self):
        self.case("start();S.dispatch_fail=true;pulse();assert(has('DISPATCH_FAILED') and has('CLEANUP_DISPATCH_FAILED'));S.dispatch_fail=false;key(7);assert(has('CLEANED'))")

if __name__=='__main__':unittest.main()
