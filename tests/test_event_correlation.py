# SPDX-License-Identifier: MPL-2.0
"""Event correlation observer under real Lua / strict read-only UE4SS mocks."""
import unittest
from test_ui_child import LuaRuntime, ROOT
from test_beginplay_join import FIXTURE

BASE=ROOT/"research/interaction-prompts-owner/world-space/event-driven/Scripts"
SOURCE=(BASE/"IIPInteractionSource.lua").read_text(encoding="utf-8")
OBS=(BASE/"IIPEventCorrelation.lua").read_text(encoding="utf-8")
RIG2=r"""
S.game=true;S.cb={};S.cancelled=0;S.hook_attempts=0
function wrap(o)return {get=function()return o end}end
set(P.text,"GetText",function()return P.text.Text end)
function probe()
 local api={
  begin=function(fn)S.cb.begin=fn end,
  finish=function(fn)S.cb.finish=fn end,
  map_pre=function(fn)S.cb.map=fn end,
  loop=function(frames,fn)assert(frames==1);S.cb.tick=fn;return 71 end,
  cancel=function(h)assert(h==71);S.cancelled=S.cancelled+1;return true end,
  native_alive=function(o)return o:IsValid()end,
  hint_visible=function(w)return w.Visibility==0 and w.RenderOpacity==1 end,
  bind_can_show=function(fn)
   S.hook_attempts=S.hook_attempts+1
   if S.unloaded then return false,"not_loaded" end
   S.cb.can=fn;return true
  end
 }
 observer=Observer.start(api,Source,function(ev,msg)
   S.logs[#S.logs+1]="EVENT_CORRELATION event="..ev.." "..msg
 end)
end
function emit_can(p,...)
 assert(S.cb.can)
 local result=S.cb.can(wrap((p or P).widget),...)
 assert(result==nil,"CanShow result replaced")
end
function begin(p)S.cb.begin(wrap((p or P).actor))end
function finish(p)S.cb.finish(wrap((p or P).actor))end
function map_pre()S.cb.map()end
function tick(n)for i=1,(n or 1)do S.cb.tick()end end
function action_pair(n,tag,text)
 local p=pair(n)
 set(p.argument,"tag",tag)
 set(p.text,"GetText",function()return p.text.Text end)
 set(p.text,"value",text)
 return p
end
"""

class EventCorrelation(unittest.TestCase):
    def case(self,code):
        lua=LuaRuntime(unpack_returned_tuples=True)
        lua.execute(FIXTURE)
        lua.execute("Source=(function()\n"+SOURCE+"\nend)()")
        lua.execute("Observer=(function()\n"+OBS+"\nend)()")
        lua.execute(RIG2)
        lua.execute(code)

    def test_callback_is_read_only_and_no_native_bool_override(self):
        self.case(r"""
probe();begin();tick()
assert(observer.status().hook and S.hook_attempts==1)
local reads=S.widget_reads
for i=1,200 do emit_can() end
assert(S.widget_reads==reads and observer.status().matched==200)
assert(observer.status().shows==0 and S.pose_reads==0)
assert(S.registered==0 and S.released==0)
assert(not has("event=SHOW"))
""")

    def test_open_take_check_show_hide_and_correlated_frame_age(self):
        self.case(r"""
local T=action_pair(2,"Take","Взять")
local C=action_pair(3,"Check","Проверить")
for _,p in ipairs({P,T,C})do set(p.component,"bVisible",false)end
probe();begin(P);begin(T);begin(C);tick()
for _,p in ipairs({P,T,C})do
 emit_can(p);set(p.component,"bVisible",true);tick()
 assert(has("action="..(p==P and "Open" or p==T and "Take" or "Check")))
 set(p.component,"bVisible",false);tick()
end
assert(observer.status().shows==3 and observer.status().hides==3)
assert(has("evidence=MATCHED_EVENT_NOT_SELECTION_PROOF"))
assert(observer.status().matched==3 and observer.status().unmatched==0)
""")

    def test_rapid_unmatched_callbacks_do_not_select_target(self):
        self.case(r"""
local T=action_pair(2,"Take","Взять")
set(P.component,"bVisible",false)
probe();begin(P);tick()
for i=1,100 do emit_can(T) end
assert(observer.status().unmatched==100)
tick(3)
assert(observer.status().shows==0 and observer.status().owners==1)
assert(not has("event=SHOW"))
""")

    def test_unloaded_can_show_fails_closed_without_coverage_claim(self):
        self.case(r"""
S.unloaded=true
probe();begin(P);tick()
assert(not observer.status().active and S.cancelled==1)
assert(not S.cb.can and has("event=CANSHOW_UNAVAILABLE"))
assert(has("coverage_claims=none") and has("native_writes=0"))
local reads=S.widget_reads
begin(P);tick(100)
assert(S.widget_reads==reads)
""")

    def test_duplicate_widget_blocks_session_and_callbacks_inert(self):
        self.case(r"""
local T=action_pair(2,"Take","Взять")
set(T.component,"Widget",P.widget)
set(T.component,"NewUserWidget",P.widget)
probe();begin(P);begin(T)
assert(not observer.status().active and S.cancelled==1)
assert(has("duplicate widget-to-owner identity"))
local before=S.widget_reads
tick(2)
assert(S.widget_reads==before)
""")

    def test_partial_audit_is_explicitly_non_authoritative(self):
        self.case(r"""
probe()
for i=1,50 do
 local p=i==1 and P or action_pair(i,"Take","Взять")
 set(p.component,"bVisible",false);begin(p)
end
tick(60)
assert(observer.status().owners==50)
assert(observer.status().incomplete==1)
assert(has("event=AUDIT_INCOMPLETE"))
assert(has("unique_owner_claim=false"))
assert(not has("event=AUDIT state=unique_observed"))
""")

    def test_audit_detects_native_show_without_prior_matched_event(self):
        self.case(r"""
set(P.component,"bVisible",false)
probe();begin();tick(60)
set(P.component,"bVisible",true);tick(60)
assert(observer.status().shows==1 and observer.status().missed==1)
assert(has("NO_EVENT_SINCE_OBSERVED_HIDE"))
assert(has("selected_target_authority=unproved"))
""")

    def test_two_simultaneous_visible_are_diagnostic_ambiguity(self):
        self.case(r"""
local T=action_pair(2,"Take","Взять")
probe();begin(P);begin(T);tick(60)
assert(observer.status().ambiguous==1)
assert(has("state=ambiguous"))
assert(not has("authoritative_target=true"))
""")

    def test_pending_owner_is_indexed_on_retry_then_event_usable(self):
        self.case(r"""
local T=action_pair(2,"Take","Взять")
set(T.component,"Widget",nil)
set(T.component,"bVisible",false)
probe();begin(T)
assert(observer.status().pending==1)
set(T.component,"Widget",T.widget)
tick(30)
assert(observer.status().owners==1 and observer.status().pending==0)
emit_can(T);set(T.component,"bVisible",true);tick()
assert(observer.status().shows==1)
""")

    def test_endplay_map_reset_and_stop_leave_callbacks_inert(self):
        self.case(r"""
probe();begin();tick();emit_can();finish()
assert(observer.status().owners==0)
map_pre();assert(observer.status().owners==0)
begin();tick();assert(observer.status().owners==1)
observer.stop("user");assert(S.cancelled==1 and not observer.status().active)
local reads=S.widget_reads
emit_can();tick();begin();finish();map_pre()
assert(reads==S.widget_reads)
assert(has("event=STOP") and has("native_writes=0"))
""")

    def test_no_arbitrary_session_timer_or_callback_cap(self):
        self.case(r"""
set(P.component,"bVisible",false)
probe();begin();tick()
for i=1,9500 do emit_can() end
tick(240)
assert(observer.status().active and observer.status().callbacks==9500)
assert(S.cancelled==0 and observer.status().matched==9500)
""")

    def test_unexpected_hook_args_never_override_and_stop(self):
        self.case(r"""
probe();begin();tick()
emit_can(P,123)
assert(not observer.status().active and S.cancelled==1)
assert(has("CanShow unexpected arguments"))
""")

if __name__=="__main__":
    unittest.main()
