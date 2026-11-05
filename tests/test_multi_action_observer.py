# SPDX-License-Identifier: MPL-2.0
"""Real Lua multi-action, user-paced observer under read-only UE4SS mocks."""
import unittest

from test_ui_child import LuaRuntime, ROOT
from test_beginplay_join import FIXTURE

BASE=ROOT/"research/interaction-prompts-owner/world-space/multi-action"
SOURCE=(BASE/"IIPInteractionSource.lua").read_text(encoding="utf-8")
EVENTS=(BASE/"IIPInteractionEvents.lua").read_text(encoding="utf-8")
RIG=r"""
S.game=true
S.observer_callbacks={}
S.cancelled=0
set(P.text,"GetText",function()return P.text.Text end)
function wrap(o)return {get=function()return o end}end
function begin(p)S.observer_callbacks.begin(wrap((p or P).actor))end
function finish(p)S.observer_callbacks.finish(wrap((p or P).actor),wrap(2))end
function map_pre()S.observer_callbacks.map()end
function tick(n)
 for i=1,(n or 1)do S.observer_callbacks.tick()end
end
function probe()
 local api={
  begin=function(f)assert(not S.observer_callbacks.begin);S.observer_callbacks.begin=f end,
  finish=function(f)assert(not S.observer_callbacks.finish);S.observer_callbacks.finish=f end,
  map_pre=function(f)assert(not S.observer_callbacks.map);S.observer_callbacks.map=f end,
  loop=function(frames,f)assert(frames==30);S.observer_callbacks.tick=f;return 77 end,
  cancel=function(h)assert(h==77);S.cancelled=S.cancelled+1;return true end,
  native_alive=function(o)return o:IsValid()end,
  hint_visible=function(w)return w.Visibility==0 and w.RenderOpacity==1 end,
 }
 observer=Events.start(api,Source,function(ev,msg)
   S.logs[#S.logs+1]="IIP_MULTI_ACTION event="..ev.." "..msg
 end)
end
function action_pair(n,tag,text)
 local p=pair(n)
 set(p.argument,"tag",tag)
 set(p.text,"GetText",function()return p.text.Text end)
 set(p.text,"value",text)
 return p
end
"""

class MultiActionObserver(unittest.TestCase):
    def case(self, body, setup=""):
        lua=LuaRuntime(unpack_returned_tuples=True)
        lua.execute(FIXTURE)
        lua.execute("Source=(function()\n"+SOURCE+"\nend)()")
        lua.execute("Events=(function()\n"+EVENTS+"\nend)()")
        lua.execute(RIG)
        lua.execute(setup)
        lua.execute(body)

    def test_three_static_action_families_are_read_only(self):
        self.case(r"""
T=action_pair(2,"Take","Взять")
C=action_pair(3,"Check","Проверить")
probe();begin(P);begin(T);begin(C)
assert(observer.status().registered==3 and observer.status().joined==3)
assert(has("owner=1 action=Open") and has("owner=2 action=Take"))
assert(has("owner=3 action=Check"))
assert(S.registered==0 and S.pose_reads==0)
assert(StaticConstructObject==nil and LoadAsset==nil)
""")

    def test_native_visibility_switches_open_take_check_without_world_binding(self):
        self.case(r"""
T=action_pair(2,"Take","Взять")
C=action_pair(3,"Check","Проверить")
set(T.component,"bVisible",false);set(C.component,"bVisible",false)
probe();begin(P);begin(T);begin(C)
tick(2);assert(has("state=unique_observed:1:Open"))
set(P.component,"bVisible",false);set(T.component,"bVisible",true)
tick(2);assert(has("state=unique_observed:2:Take"))
assert(has("event=VISIBLE_OWNER owner=2 action=Take"))
assert(has("observed_only=true"))
set(T.component,"bVisible",false);set(C.component,"bVisible",true)
tick(2);assert(has("state=unique_observed:3:Check"))
set(C.component,"bVisible",false);tick()
assert(has("state=no_native_prompt"))
assert(observer.status().active and S.cancelled==0)
assert(has("target_selection_unproven=true"))
""")

    def test_two_visible_including_different_actions_never_chooses_one(self):
        self.case(r"""
T=action_pair(2,"Take","Взять")
probe();begin(P);begin(T);tick(3)
assert(has("state=ambiguous_native_prompts"))
assert(not has("state=unique_observed:"))
set(T.component,"bVisible",false);tick()
assert(has("state=warming:1:Open"))
tick();assert(has("state=unique_observed:1:Open"))
""")

    def test_timed_and_callback_budgets_do_not_stop_normal_observation(self):
        self.case(r"""
probe();begin()
tick(250)
assert(observer.status().active and observer.status().samples==250)
local unrelated=make("/World.OtherActor","/Script/Engine.Actor")
for i=1,8200 do S.observer_callbacks.begin(wrap(unrelated)) end
assert(observer.status().begin_calls==8201 and observer.status().active)
tick(250)
assert(observer.status().samples==500 and S.cancelled==0)
assert(not has("observation_budget") and not has("beginplay_budget"))
assert(#S.logs<35) -- Change-only logs despite hundreds of samples.
""")

    def test_more_than_eight_supported_actors_not_fatal(self):
        self.case(r"""
probe()
for i=1,12 do
 local a=i==1 and P or action_pair(i,i%2==0 and "Take" or "Check","Взять")
 begin(a)
end
assert(observer.status().registered==12 and observer.status().active)
tick(2)
assert(has("state=ambiguous_native_prompts") and S.cancelled==0)
""")

    def test_partial_sweep_reports_uncertainty_and_continues(self):
        self.case(r"""
probe()
for i=1,55 do
 local a=i==1 and P or action_pair(i,"Take","Взять")
 if i>1 then set(a.component,"bVisible",false) end
 begin(a)
end
tick(3)
assert(observer.status().registered==55 and observer.status().active)
assert(has("state=incomplete_snapshot") and has("total=55"))
assert(not has("state=unique_observed:") and S.cancelled==0)
local before=#S.logs
tick(200) -- Rotating partial batches must not log pseudo-hide every tick.
assert(observer.status().active and #S.logs-before<8)
""")

    def test_visible_owner_logged_even_after_join_detail_throttle(self):
        self.case(r"""
probe()
for i=1,50 do
 local a=i==1 and P or action_pair(i,"Take","Взять")
 set(a.component,"bVisible",i==50)
 begin(a)
end
tick(2)
assert(observer.status().active and observer.status().registered==50)
assert(has("event=JOIN_DETAIL_SUPPRESSED"))
assert(has("event=VISIBLE_OWNER"))
assert(has("action=Take") and has("text="))
assert(has("state=incomplete_snapshot"))
assert(not has("state=unique_observed:"))
""")

    def test_pending_supported_widget_waits_without_manual_beginplay(self):
        self.case(r"""
T=action_pair(2,"Take","Взять")
set(T.component,"Widget",nil)
probe();begin(T);assert(observer.status().pending==1)
tick();assert(has("state=incomplete_snapshot"))
set(T.component,"Widget",T.widget)
tick()
assert(observer.status().registered==1 and observer.status().pending==0)
assert(has("owner=1 action=Take ready_at=retry"))
tick(2);assert(has("state=unique_observed:1:Take"))
""")

    def test_pending_becoming_invalid_is_removed_not_full_stop(self):
        self.case(r"""
T=action_pair(2,"Take","Взять")
set(T.component,"Widget",nil)
probe();begin(T)
set(T.actor,"live",false)
tick()
assert(observer.status().active and observer.status().pending==0)
assert(has("event=STALE_PENDING") and S.cancelled==0)
""")

    def test_native_owner_destruction_without_endplay_is_not_a_false_selection(self):
        self.case(r"""
T=action_pair(2,"Take","Взять")
set(T.component,"bVisible",false)
probe();begin(P);begin(T);tick(2)
set(P.actor,"live",false);tick()
assert(observer.status().active and observer.status().registered==1)
assert(has("event=STALE_OWNER"))
assert(not has("event=STOP"))
""")

    def test_endplay_and_map_invalidate_exact_active_registrations(self):
        self.case(r"""
T=action_pair(2,"Take","Взять")
probe();begin(P);begin(T)
finish(P);assert(observer.status().registered==1)
tick();assert(has("event=OWNER_ENDED") and observer.status().ends==1)
map_pre();assert(observer.status().registered==0 and observer.status().maps==1)
finish(T);assert(observer.status().registered==0)
begin(T);tick(2)
assert(observer.status().registered==1 and observer.status().joined==3)
""")

    def test_wrong_action_for_existing_owner_is_identity_contract_failure(self):
        self.case(r"""
probe();begin()
set(P.argument,"tag","Take")
tick()
assert(not observer.status().active and S.cancelled==1)
assert(has("event=STOP") and has("interaction action source changed"))
local before=S.widget_reads;tick();begin()
assert(S.widget_reads==before)
""")

    def test_other_action_is_ignored_not_registered_as_supported(self):
        self.case(r"""
T=action_pair(2,"Climb","Подняться")
probe();begin(T)
tick()
assert(observer.status().registered==0 and observer.status().active)
assert(not has("event=JOINED"))
""")

    def test_reused_widget_across_two_owners_is_contract_fault(self):
        self.case(r"""
T=action_pair(2,"Take","Взять")
set(T.component,"Widget",P.widget)
set(T.component,"NewUserWidget",P.widget)
probe();begin(P);begin(T)
assert(not observer.status().active and S.cancelled==1)
assert(has("native widget/component shared across owners"))
""")

    def test_explicit_stop_cancels_loop_and_leaves_hooks_inert(self):
        self.case(r"""
probe();begin();tick(2)
observer.stop("user")
assert(not observer.status().active and S.cancelled==1)
assert(observer.status().registered==0)
local reads=S.widget_reads
begin();tick();finish()
assert(S.widget_reads==reads and S.cancelled==1)
""")

    def test_failed_registration_leaves_callbacks_inert(self):
        self.case(r"""
local api={
 begin=function(f)S.observer_callbacks.begin=f end,
 finish=function(f)error("EndPlay unavailable")end,
 map_pre=function(f)end,
 loop=function(f)error("loop should not install")end,
 cancel=function(h)return true end,
 native_alive=function(o)return o:IsValid()end,
 hint_visible=function(w)return true end,
}
local p=Events.start(api,Source,function(ev,msg)
  S.logs[#S.logs+1]=ev.." "..msg
end)
assert(not p.status().active and has("STOP"))
assert(S.observer_callbacks.begin~=nil)
S.observer_callbacks.begin(wrap(P.actor))
assert(p.status().joined==0)
""")

if __name__=="__main__":
    unittest.main()
