# SPDX-License-Identifier: MPL-2.0
"""Execute native-event observer + source-only handoff against Lua UE4SS mocks."""
import unittest

from test_ui_child import LuaRuntime, ROOT
from test_beginplay_join import FIXTURE
from test_multi_action_observer import RIG

ROOTDIR=ROOT/"research/interaction-prompts-owner/world-space"
SOURCE=(ROOTDIR/"multi-action/IIPInteractionSource.lua").read_text(encoding="utf-8")
EVENTS=(ROOTDIR/"owner-handoff/IIPInteractionEvents.lua").read_text(encoding="utf-8")
CONTROL=(ROOTDIR/"owner-handoff/IIPWorldHandoff.lua").read_text(encoding="utf-8")
BRIDGE=(ROOTDIR/"owner-handoff/IIPWorldHandoffBridge.lua").read_text(encoding="utf-8")

BRIDGE_RIG=r"""
R={owned=false,shown=false,created=0,cleaned=0,fail_cleanup=false}
local renderer={
 empty=function()return not R.owned end,
 create=function(r,ticket)
    assert(not R.owned,"OVERLAPPING WORLD COMPONENTS")
    R.owned=true;R.created=R.created+1;return true
 end,
 hide=function()R.shown=false;return true end,
 resume=function()assert(R.owned);R.shown=true;return true end,
 refresh=function()assert(R.owned and R.shown);return true end,
 cleanup=function()
    if R.fail_cleanup then return false end
    assert(R.owned);R.owned=false;R.shown=false;R.cleaned=R.cleaned+1;return true
 end,
}
handoff=Handoff.new(renderer,function(ev,msg)
  S.logs[#S.logs+1]="IIP_WORLD_HANDOFF event="..ev.." "..msg
end)
function probe_handoff()
 local api={
  begin=function(f)S.observer_callbacks.begin=f end,
  finish=function(f)S.observer_callbacks.finish=f end,
  map_pre=function(f)S.observer_callbacks.map=f end,
  loop=function(frames,f)assert(frames==30);S.observer_callbacks.tick=f;return 77 end,
  cancel=function(h)assert(h==77);S.cancelled=S.cancelled+1;return true end,
  native_alive=function(o)return o:IsValid()end,
  hint_visible=function(w)return w.Visibility==0 and w.RenderOpacity==1 end,
 }
 observer=Events.start(api,Source,function(ev,msg)
   S.logs[#S.logs+1]="IIP_MULTI_ACTION event="..ev.." "..msg
 end,Bridge.sink(handoff))
end
function pump()return Bridge.pump(observer,handoff)end
"""

class WorldHandoffBridge(unittest.TestCase):
    def case(self, body):
        lua=LuaRuntime(unpack_returned_tuples=True)
        lua.execute(FIXTURE)
        for name,source in [("Source",SOURCE),("Events",EVENTS),("Handoff",CONTROL),("Bridge",BRIDGE)]:
            lua.execute(name+"=(function()\n"+source+"\nend)()")
        lua.execute(RIG)
        lua.execute(BRIDGE_RIG)
        lua.execute(body)

    def test_observer_a_take_b_owner_handoff_with_fresh_samples(self):
        self.case(r"""
T=action_pair(2,"Take","Взять")
set(T.component,"bVisible",false)
probe_handoff();begin(P);begin(T)
tick(2)
assert(handoff.status().registered==2)
assert(pump()=="bound_hidden")
assert(pump()=="resumed" and R.created==1)
set(P.component,"bVisible",false)
set(T.component,"bVisible",true)
tick(2)
assert(pump()=="hidden_before_release")
assert(pump()=="cleaned")
assert(R.cleaned==1 and not R.owned)
assert(pump()=="no_target")
tick();assert(pump()=="no_target")
tick();assert(pump()=="bound_hidden")
assert(pump()=="resumed")
assert(handoff.status().selected~=nil and R.created==2)
assert(has("event=CLEANED") and has("event=RELEASED"))
assert(S.pose_reads==0)
""")

    def test_native_endplay_and_map_callbacks_queue_not_execute_native_cleanup(self):
        self.case(r"""
probe_handoff();begin(P);tick(2);assert(pump()=="bound_hidden")
assert(pump()=="resumed")
finish(P)
assert(R.owned and R.cleaned==0) -- Event callback must not mutate native UI.
assert(pump()=="hidden_before_release")
assert(pump()=="cleaned" and R.cleaned==1)
begin(P);tick(2);assert(pump()=="bound_hidden")
map_pre();assert(R.owned and R.cleaned==1)
assert(pump()=="cleaned" and R.cleaned==2)
assert(handoff.status().registered==0)
""")

    def test_bridge_stops_observer_after_renderer_fault_before_rebind(self):
        self.case(r"""
T=action_pair(2,"Take","Взять")
set(T.component,"bVisible",false)
probe_handoff();begin(P);begin(T);tick(2)
assert(pump()=="bound_hidden");assert(pump()=="resumed")
set(P.component,"bVisible",false);set(T.component,"bVisible",true);tick(2)
assert(pump()=="hidden_before_release")
R.fail_cleanup=true
assert(pump()=="cleanup_blocked")
assert(not observer.status().active and S.cancelled==1)
assert(R.owned and R.created==1)
assert(pump()=="cleanup_blocked")
""")

if __name__=="__main__":
    unittest.main()
