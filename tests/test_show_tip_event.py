# SPDX-License-Identifier: MPL-2.0
"""ShowTipEvent research observer under a strict, read-only Lua host mock."""
import unittest
from test_ui_child import LuaRuntime, ROOT

BASE=ROOT/"research/interaction-prompts-owner/world-space/show-tip-event-observer/Scripts"
OBSERVER=(BASE/"IIPShowTipEventObserver.lua").read_text(encoding="utf-8")
RIG=r"""
S={cb={},logs={},actors={},cancelled=0,reads=0,binds=0}
local function wrap(x)return {get=function()return x end}end
function actor(id,action)
 local a={key=id,action=action,visible=false}
 a.record={actor=id,component="component_"..id,widget="widget_"..id,action=action}
 S.actors[id]=a
 return a
end
A=actor("A","Open");B=actor("B","Take");C=actor("C","Check")
Source={
 acquire=function(a)
  if a and a.record then return a.record,"ready" end
  return nil,"unrelated_actor"
 end,
 actor_identity=function(a)if a and a.key then return {key=a.key} end end,
 snapshot=function(rec)
  S.reads=S.reads+1
  local a=S.actors[rec.actor]
  if not a then return nil,"gone" end
  return {actor=rec.actor,component=rec.component,widget=rec.widget,
          action=rec.action,shown=a.visible,ready=a.visible}
 end,
}
api={
 begin=function(fn)S.cb.begin=fn end,
 finish=function(fn)S.cb.finish=fn end,
 map_pre=function(fn)S.cb.map=fn end,
 loop=function(n,fn)assert(n==1);S.cb.tick=fn;return 63 end,
 cancel=function(n)assert(n==63);S.cancelled=S.cancelled+1;return true end,
 bind=function(fn)
  S.binds=S.binds+1
  if S.unavailable then return false,"no script function" end
  S.cb.event=fn;return true
 end,
 native_alive=function()return true end,
 hint_visible=function()return true end,
}
observer=Observer.start(api,Source,function(name,fields)
 S.logs[#S.logs+1]=name.." "..fields
end)
function begin(a)S.cb.begin(wrap(a))end
function finish(a)S.cb.finish(wrap(a))end
function tick(n)for i=1,(n or 1)do S.cb.tick()end end
function event(a,show,...)
 assert(S.cb.event)
 local r=S.cb.event(wrap(a),wrap(show),...)
 assert(r==nil,"must not replace host return")
end
function has(fragment)
 for _,line in ipairs(S.logs)do
  if line:find(fragment,1,true)then return true end
 end
 return false
end
"""

class ShowTipEvent(unittest.TestCase):
    def case(self,code):
        lua=LuaRuntime(unpack_returned_tuples=True)
        lua.execute("Observer=(function()\n"+OBSERVER+"\nend)()")
        lua.execute(RIG)
        lua.execute(code)

    def test_arms_after_native_owner_without_global_snapshot_sweep(self):
        self.case(r"""
tick(5);assert(S.binds==0 and S.reads==0)
begin(A);tick()
assert(S.binds==1 and observer.status().hook)
assert(observer.status().owners==1 and S.reads==0)
""")

    def test_ordered_open_take_handoff_and_independent_visibility(self):
        self.case(r"""
begin(A);begin(B);begin(C);tick()
event(A,true);A.visible=true;tick()
event(A,false);event(B,true)
A.visible=false;B.visible=true;tick()
assert(observer.status().intents==3 and observer.status().matched==3)
assert(S.reads==3)
assert(has("CORRELATED seq=1 action=Open show=true"))
assert(has("INTENT seq=2 action=Open show=false"))
assert(has("INTENT seq=3 action=Take show=true"))
assert(has("CORRELATED seq=2 action=Open show=false"))
assert(has("CORRELATED seq=3 action=Take show=true"))
""")

    def test_event_without_visible_result_is_not_pass(self):
        self.case(r"""
begin(A);tick()
event(A,true);tick(13)
assert(observer.status().intents==1)
assert(observer.status().matched==0 and observer.status().expired==1)
assert(has("NO_MATCH seq=1"))
""")

    def test_missing_script_hook_stops_without_claiming_coverage(self):
        self.case(r"""
S.unavailable=true;begin(A);tick()
assert(not observer.status().active and S.cancelled==1)
assert(has("HOOK_UNAVAILABLE") and has("coverage=none"))
local n=S.reads
tick(100);assert(S.reads==n)
""")

    def test_invalid_bool_or_extra_arguments_stops_inert(self):
        self.case(r"""
begin(A);tick();event(A,1)
assert(not observer.status().active and S.cancelled==1)
assert(observer.status().intents==0 and has("not boolean"))
""")
        self.case(r"""
begin(A);tick();event(A,true,123)
assert(not observer.status().active and has("parameter count"))
""")

    def test_map_endplay_and_stop_do_not_keep_stale_state(self):
        self.case(r"""
begin(A);tick();event(A,true)
finish(A);tick()
assert(observer.status().owners==0 and observer.status().pending==0)
begin(B);S.cb.map();tick()
assert(observer.status().owners==0)
observer.stop("manual")
assert(S.cancelled==1 and not observer.status().active)
local n=S.reads
event(B,true);tick(100)
assert(S.reads==n and has("native_writes=0"))
""")

    def test_bounded_pending_events_fail_closed(self):
        self.case(r"""
begin(A);tick()
for i=1,13 do event(A,true) end
assert(not observer.status().active and S.cancelled==1)
assert(has("pending bound exceeded"))
""")

if __name__=="__main__":
    unittest.main()
