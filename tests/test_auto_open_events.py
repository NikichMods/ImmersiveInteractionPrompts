# SPDX-License-Identifier: MPL-2.0
"""Pinned-API event observer with actual Lua owner/policy modules, no live host."""
import unittest

from test_ui_child import LuaRuntime, ROOT
from test_beginplay_join import FIXTURE

BASE = ROOT / "research/interaction-prompts-owner/world-space/auto-target"
SOURCES = {name: (BASE / (name + ".lua")).read_text(encoding="utf-8")
           for name in ("IIPOpenSource", "IIPTargetPolicy", "IIPOpenEvents")}
RIG = r"""
S.game=true
S.observer_callbacks={}
S.cancelled=0
set(P.text,"GetText",function()return P.text.Text end)
function rparam(o)return {get=function()return o end}end
function begin(p)
    S.observer_callbacks.begin(rparam((p or P).actor))
end
function finish(p)
    S.observer_callbacks.finish(rparam((p or P).actor),{get=function()return 2 end})
end
function map_pre()S.observer_callbacks.map()end
function tick(n)
    for _=1,(n or 1)do S.observer_callbacks.tick()end
end
function probe()
    local api={
      begin=function(f)assert(not S.observer_callbacks.begin);S.observer_callbacks.begin=f end,
      finish=function(f)assert(not S.observer_callbacks.finish);S.observer_callbacks.finish=f end,
      map_pre=function(f)assert(not S.observer_callbacks.map);S.observer_callbacks.map=f end,
      loop=function(frames,f)
          assert(frames==30 and not S.observer_callbacks.tick)
          S.observer_callbacks.tick=f;return 55
      end,
      cancel=function(handle)assert(handle==55);S.cancelled=S.cancelled+1;return true end,
      native_alive=function(o)return o:IsValid()end,
      hint_visible=function(w)return w.Visibility==0 and w.RenderOpacity==1 end,
    }
    observer=Events.start(api,Source,Policy,function(event,msg)
        S.logs[#S.logs+1]="IIP_OPEN_AUTO event="..event.." "..msg
    end)
end
"""

class OpenAutoEvents(unittest.TestCase):
    def case(self, body, setup=""):
        lua=LuaRuntime(unpack_returned_tuples=True)
        lua.execute(FIXTURE)
        for name,code in SOURCES.items():
            lua.execute({"IIPOpenSource":"Source","IIPTargetPolicy":"Policy", "IIPOpenEvents":"Events"}[name] + "=(function()\n" + code + "\nend)()")
        lua.execute(RIG)
        lua.execute(setup)
        lua.execute(body)

    def test_global_callbacks_register_on_start_without_manual_chord(self):
        self.case(r"""
probe()
assert(observer.status().active and type(S.observer_callbacks.begin)=="function")
assert(type(S.observer_callbacks.finish)=="function")
assert(type(S.observer_callbacks.map)=="function")
assert(S.registered==0) -- No experimental CanShow/SetShow hook.
begin();assert(observer.status().joined==1)
tick();assert(has("state=warming:") and observer.status().registered==1)
tick();assert(has("state=eligible:") and observer.status().joined==1)
assert(S.pose_reads==0 and S.cancelled==0)
""")

    def test_two_objects_transitions_without_assuming_last_canshow_selected(self):
        self.case(r"""
Q=pair(2)
set(Q.text,"GetText",function()return Q.text.Text end)
set(Q.component,"bVisible",false)
probe()
begin(P);begin(Q)
tick(2)
assert(has("state=eligible:") and has("visible=1"))
assert(has("shown_owners=1 ready_owners=1 hidden_owners=2 pending_owners=-"))
set(P.component,"bVisible",false)
set(Q.component,"bVisible",true)
tick(2)
assert(has("state=warming:") and observer.status().joined==2)
assert(has("shown_owners=2 ready_owners=2 hidden_owners=1 pending_owners=-"))
set(P.component,"bVisible",true)
tick()
assert(has("state=ambiguous_native_prompts"))
assert(has("shown_owners=1,2 ready_owners=1,2 hidden_owners=- pending_owners=-"))
set(P.component,"bVisible",false)
set(Q.component,"bVisible",false)
tick()
assert(has("state=no_native_prompt"))
assert(has("shown_owners=- ready_owners=- hidden_owners=1,2 pending_owners=-"))
assert(S.registered==0 and observer.status().active)
""")

    def test_pending_widget_is_bounded_and_rechecked_without_forced_initialization(self):
        self.case(r"""
set(P.component,"Widget",nil)
probe();begin()
assert(observer.status().pending==1 and observer.status().joined==0)
tick()
assert(has("state=unresolved_open_owner") and not has("event=JOINED"))
assert(has("pending_owners=1"))
set(P.component,"Widget",P.widget)
tick();assert(observer.status().pending==0 and observer.status().joined==1)
assert(has("owner=1 ready_at=retry"))
tick();assert(has("state=eligible:"))
assert(S.registered==0 and S.pose_reads==0)
""")

    def test_endplay_only_removes_the_exact_instance(self):
        self.case(r"""
Q=pair(2);set(Q.text,"GetText",function()return Q.text.Text end)
probe();begin(P);begin(Q)
tick();finish(P)
assert(observer.status().registered==1 and observer.status().ends==1)
tick(2)
assert(observer.status().joined==2 and observer.status().registered==1)
finish(P);assert(observer.status().registered==1)
finish(Q);assert(observer.status().registered==0)
tick();assert(has("state=no_native_prompt"))
""")

    def test_endplay_clears_pending_even_if_widget_never_ready(self):
        self.case(r"""
set(P.component,"Widget",nil)
probe();begin();assert(observer.status().pending==1)
finish();assert(observer.status().pending==0 and observer.status().registered==0)
tick();assert(has("state=no_native_prompt"))
""")

    def test_map_pre_clears_world_and_ignores_old_endplay(self):
        self.case(r"""
probe();begin();tick()
map_pre()
assert(observer.status().registered==0 and observer.status().maps==1)
finish()
assert(observer.status().registered==0)
tick();assert(has("event=MAP_CLEARED"))
begin();tick(2)
assert(observer.status().registered==1 and observer.status().joined==2)
""")

    def test_alias_or_bad_rebind_stops_all_reads_and_cancels_loop(self):
        self.case(r"""
Q=pair(2);set(Q.text,"GetText",function()return Q.text.Text end)
probe();begin(P)
set(P.component,"Widget",Q.widget)
tick()
assert(not observer.status().active and S.cancelled==1)
local reads=S.widget_reads
tick();begin(P)
assert(S.widget_reads==reads and has("event=STOP"))
""")

    def test_budget_stops_cleanly_without_unsafe_global_unhook(self):
        self.case(r"""
probe()
tick(241)
assert(not observer.status().active and S.cancelled==1)
assert(has("reason=EngineTick_contract:") and has("observation_budget"))
begin();tick()
assert(observer.status().joined==0)
""")

    def test_candidate_overflow_is_fail_closed_not_drop_silently(self):
        self.case(r"""
probe()
for i=1,9 do
  local p=i==1 and P or pair(i)
  begin(p)
end
assert(not observer.status().active and S.cancelled==1)
assert(has("candidate_capacity"))
""")

    def test_duplicate_beginplay_does_not_create_ambiguous_registry(self):
        self.case(r"""
probe();begin();begin()
assert(not observer.status().active)
assert(has("duplicate_owner_beginplay") and S.cancelled==1)
""")

    def test_missing_subscription_fails_without_any_native_ui_write(self):
        self.case(r"""
local api={
  begin=function(f)end,
  finish=function(f)error("EndPlay unavailable")end,
  map_pre=function(f)end,
  loop=function()return 1 end,
  cancel=function()return true end,
  native_alive=function()return true end,
  hint_visible=function()return true end,
}
local p=Events.start(api,Source,Policy,function(ev,msg)
  S.logs[#S.logs+1]="IIP_OPEN_AUTO event="..ev.." "..msg
end)
assert(not p.status().active)
assert(has("event=STOP") and has("registration:"))
assert(S.registered==0 and S.pose_reads==0)
""")

    def test_no_native_bind_release_or_world_component_side_effects(self):
        self.case(r"""
probe();begin();tick(3)
assert(StaticConstructObject==nil and LoadAsset==nil)
assert(S.registered==0 and S.pose_reads==0)
observer.stop("user")
assert(S.cancelled==1 and not observer.status().active)
assert(observer.status().registered==0 and observer.status().pending==0)
tick();assert(S.cancelled==1)
""")

if __name__=="__main__":
    unittest.main()
