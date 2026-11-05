# SPDX-License-Identifier: MPL-2.0
"""End-to-end Lua source/target/observer/handoff/renderer/session, mocked UE4 native host."""
import unittest
from test_ui_child import LuaRuntime, ROOT
from test_beginplay_join import FIXTURE
from test_multi_action_observer import RIG

DIR=ROOT/"research/interaction-prompts-owner/world-space/auto-world/Scripts"
NAMES=("IIPInteractionSource","IIPInteractionEvents","IIPWorldHandoff",
       "IIPWorldHandoffBridge","IIPWorldRenderer","IIPWorldTarget",
       "IIPAutoWorldSession")
SOURCES={n:(DIR/(n+".lua")).read_text(encoding="utf8") for n in NAMES}

MOCK=r"""
S.game=true;S.hooks={};S.cancelled={};S.world_ops={}
W={owned=false,created=0,cleans=0,prepared=0,assets=0,hides=0,
   resumes=0,refreshes=0,shown=false,fail_create=false,fail_cleanup=false,
   active=0,max_active=0,actions={}}
function ops(msg)S.world_ops[#S.world_ops+1]=msg end
local world={
 prepare=function()W.prepared=W.prepared+1 end,
 refresh_assets=function()W.assets=W.assets+1 end,
 empty=function()return not W.owned end,
 create=function(actor,component,widget,request_stop,action)
  assert(actor and component and widget and not W.owned,"overlapping World host")
  W.owned=true;W.active=W.active+1;W.max_active=math.max(W.max_active,W.active)
  W.created=W.created+1;W.actions[#W.actions+1]=action;W.shown=false
  ops("create:"..action)
  if W.fail_create then error("partial World creation")end
 end,
 hide=function()assert(W.owned);W.hides=W.hides+1;W.shown=false;return true end,
 resume=function()assert(W.owned);W.resumes=W.resumes+1;W.shown=true;return true end,
 refresh=function()assert(W.owned);W.refreshes=W.refreshes+1;return true end,
 cleanup=function()
  assert(W.owned)
  if W.fail_cleanup then return false end
  W.cleans=W.cleans+1;W.active=W.active-1;W.owned=false;W.shown=false
  ops("cleaned")
  return true
 end
}
local api={
 begin=function(fn)S.hooks.begin=fn end,
 finish=function(fn)S.hooks.finish=fn end,
 map_pre=function(fn)S.hooks.map=fn end,
 loop=function(frames,fn)
  if frames==30 then assert(not S.hooks.sample);S.hooks.sample=fn;return 77 end
  if frames==1 then assert(not S.hooks.frame);S.hooks.frame=fn;return 88 end
  error("unverified loop interval")
 end,
 cancel=function(h)
  assert(h==77 or h==88);S.cancelled[h]=(S.cancelled[h] or 0)+1;return true
 end,
 native_alive=function(o)return o:IsValid()end,
 hint_visible=function(w)return w.Visibility==0 and w.RenderOpacity==1 end
}
session=AutoSession.start({
 source=Source,events=Events,visibility={},handoff=Handoff,
 bridge=Bridge,renderer=Renderer,target=Target,world=world
},api,function(ev,msg)
 S.logs[#S.logs+1]="IIP_AUTO_WORLD event="..ev.." "..msg
end)
function join(p)S.hooks.begin(wrap((p or P).actor))end
function endplay(p)S.hooks.finish(wrap((p or P).actor))end
function map()S.hooks.map()end
function sample(n)for i=1,(n or 1)do S.hooks.sample()end end
function frame(n)for i=1,(n or 1)do S.hooks.frame()end end
function visible(p,yes)set(p.component,"bVisible",yes)end
"""

class AutomaticWorldSession(unittest.TestCase):
    def case(self, body, setup=""):
        L=LuaRuntime(unpack_returned_tuples=True)
        L.execute(FIXTURE)
        for name in NAMES:
            L.execute(name+"=(function()\n"+SOURCES[name]+"\nend)()")
        L.execute(RIG)
        L.execute('Source=IIPInteractionSource;Events=IIPInteractionEvents;'
                  'Handoff=IIPWorldHandoff;Bridge=IIPWorldHandoffBridge;'
                  'Renderer=IIPWorldRenderer;Target=IIPWorldTarget;'
                  'AutoSession=IIPAutoWorldSession')
        L.execute(setup)
        L.execute(MOCK)
        L.execute(body)

    def test_open_none_take_none_check_confirmed_release_before_bind(self):
        self.case(r"""
T=action_pair(2,"Take","Взять")
C=action_pair(3,"Check","Проверить")
visible(T,false);visible(C,false)
join(P);join(T);join(C)
sample(2);frame(2)
assert(W.created==1 and W.actions[1]=="Open" and W.shown)
visible(P,false);sample();frame()
assert(W.owned and not W.shown and W.cleans==0)
visible(T,true);sample(2);frame(2)
assert(W.cleans==1 and not W.owned and W.created==1)
assert(S.world_ops[1]=="create:Open" and S.world_ops[2]=="cleaned")
sample(2);frame(2)
assert(W.created==2 and W.actions[2]=="Take" and W.shown)
visible(T,false);sample();frame()
visible(C,true);sample(2);frame(2)
assert(W.cleans==2 and not W.owned)
sample(2);frame(2)
assert(W.created==3 and W.actions[3]=="Check" and W.max_active==1)
assert(has("event=HANDOFF_CLEANED") and has("event=HANDOFF_RELEASED"))
assert(S.registered==0)
""")

    def test_same_owner_hide_resume_keeps_single_component(self):
        self.case(r"""
join(P);sample(2);frame(2)
assert(W.created==1 and W.shown)
for i=1,20 do
 visible(P,false);sample();frame()
 assert(not W.shown and W.owned)
 visible(P,true);sample(2);frame()
 assert(W.shown and W.owned)
end
assert(W.created==1 and W.cleans==0 and W.max_active==1)
""")

    def test_two_visible_or_partial_snapshots_never_choose_owner(self):
        self.case(r"""
T=action_pair(2,"Take","Взять")
join(P);join(T)
sample(2);frame(4)
assert(W.created==0 and has("ambiguous_native_prompts"))
visible(T,false);sample(2);frame(2)
assert(W.created==1)
""")
        self.case(r"""
join(P)
for i=2,54 do
 local p=action_pair(i,"Take","Взять")
 visible(p,false);join(p)
end
sample(3);frame(4)
assert(W.created==0 and session.status().active)
assert(has("incomplete_snapshot"))
""")

    def test_native_endplay_requests_cleanup_only_on_frame(self):
        self.case(r"""
join(P);sample(2);frame(2)
endplay(P)
assert(W.owned and W.cleans==0)
frame(2)
assert(not W.owned and W.cleans==1 and W.max_active==1)
assert(session.status().active)
""")

    def test_map_transition_cleans_on_frame_and_resets_registry(self):
        self.case(r"""
join(P);sample(2);frame(2)
map();assert(W.owned and W.cleans==0)
frame(2);assert(not W.owned and W.cleans==1)
assert(session.status().handoff.registered==0)
""")

    def test_stale_actor_at_last_resolve_never_creates_world(self):
        self.case(r"""
join(P);sample(2)
set(P.actor,"live",false)
frame(3)
assert(W.created==0 and not session.status().active)
assert(has("world_handoff_fault") or has("World_handoff_fault") or has("HANDOFF_FAULT"))
""")

    def test_partial_world_allocation_cleans_then_stops_automatically(self):
        self.case(r"""
W.fail_create=true
join(P);sample(2);frame(4)
assert(W.created==1 and W.cleans==1)
assert(not W.owned and W.max_active==1)
assert(not session.status().active and session.status().terminal)
assert(S.cancelled[77]==1 and S.cancelled[88]==1)
frame(10);assert(W.created==1 and W.cleans==1)
""")

    def test_cleanup_failure_blocks_rebinding_and_cancels_both_loops(self):
        self.case(r"""
T=action_pair(2,"Take","Взять");visible(T,false)
join(P);join(T);sample(2);frame(2)
W.fail_cleanup=true
visible(P,false);visible(T,true);sample(2);frame(4)
assert(W.created==1 and W.owned and W.max_active==1)
assert(session.status().terminal and not session.status().active)
assert(has("cleanup_blocked") and not has("event=HANDOFF_RELEASED"))
assert(S.cancelled[77]==1 and S.cancelled[88]==1)
frame(20);assert(W.created==1)
""")

    def test_explicit_stop_cleans_then_disarms_while_engine_callbacks_inert(self):
        self.case(r"""
join(P);sample(2);frame(2)
session.stop("user")
assert(W.owned)
frame(3)
assert(not W.owned and W.cleans==1 and not session.status().active)
local old=W.created
join(P);sample();frame(5)
assert(W.created==old and S.cancelled[77]==1 and S.cancelled[88]==1)
""")

    def test_unbounded_user_session_no_timer_and_changing_not_logged_each_frame(self):
        self.case(r"""
sample(260);frame(512)
assert(session.status().active and session.status().cycles==512)
assert(W.created==0 and S.cancelled[77]==nil and S.cancelled[88]==nil)
assert(#S.logs<40)
""")

if __name__=="__main__":
    unittest.main()
