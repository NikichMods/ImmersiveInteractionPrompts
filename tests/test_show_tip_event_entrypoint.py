# SPDX-License-Identifier: MPL-2.0
"""Exercise actual ShowTipEvent entrypoint and owner adapter with mock UE4SS."""
import unittest
from test_ui_child import LuaRuntime, ROOT
from test_beginplay_join import FIXTURE

BASE=ROOT/"research/interaction-prompts-owner/world-space/show-tip-event-observer/Scripts"
ENTRY=(BASE/"main.lua").read_text(encoding="utf-8")
MODULES=("IIPInteractionSource","IIPShowTipEventObserver")
HOST=r"""
S.game=true;S.cb={};S.cancelled=0;S.binds=0
local EVENT="/Script/Genesis.BaseGameEventObject:ShowTipEvent"
local event_fn=make(EVENT,"Function")
set(event_fn,"type",function()return "UFunction"end)
set(event_fn,"GetFunctionFlags",function()return S.native_flag and 1024 or 0 end)
local validator=make("/Script/Engine.KismetSystemLibrary:IsValid","Function")
set(validator,"type",function()return "UFunction"end)
getmetatable(validator).__call=function(_,_,obj)return obj:IsValid()end
make("/Script/Engine.Default__KismetSystemLibrary",
     "/Script/Engine.KismetSystemLibrary")
set(P.text,"GetText",function()return P.text.Text end)
RegisterBeginPlayPostHook=function(fn)S.cb.begin=fn end
RegisterEndPlayPreHook=function(fn)S.cb.finish=fn end
RegisterLoadMapPreHook=function(fn)S.cb.map=fn end
LoopInGameThreadAfterFrames=function(n,fn)
 assert(n==1);S.cb.tick=fn;return 66
end
CancelDelayedAction=function(n)
 assert(n==66);S.cancelled=S.cancelled+1;return true
end
RegisterHook=function(name,fn)
 assert(name==EVENT,"unexpected global hook")
 S.binds=S.binds+1
 if S.reject then error("script implementation unavailable") end
 S.cb.event=fn
 return 41,41
end
local function wrap(o)return {get=function()return o end}end
function begin()S.cb.begin(wrap(P.actor))end
function tick(n)for i=1,(n or 1)do S.cb.tick()end end
function emit(show)
 assert(S.cb.event)
 local r=S.cb.event(wrap(P.actor),wrap(show))
 assert(r==nil,"native return override")
end
"""

class ShowTipEntrypoint(unittest.TestCase):
    def case(self,scenario,setup=""):
        lua=LuaRuntime(unpack_returned_tuples=True)
        lua.execute(FIXTURE)
        lua.execute(HOST)
        for name in MODULES:
            content=(BASE/(name+".lua")).read_text(encoding="utf-8")
            lua.execute("package.preload['"+name+"']=function()\n"+content+"\nend")
        lua.execute("""package.preload['IIPOpenVisibility']=function()
          return {visible=function() return true end}
        end""")
        lua.execute(setup)
        lua.execute(ENTRY)
        lua.execute(scenario)

    def test_actual_entrypoint_exact_hook_and_native_snapshot(self):
        self.case(r"""
assert(S.cb.begin and S.cb.finish and S.cb.map and S.cb.tick)
assert(S.binds==0 and S.registered==0)
begin();tick()
assert(S.binds==1 and S.cb.event)
emit(true);tick()
assert(has("IIP_SHOWTIP event=HOOK_ARMED"))
assert(has("IIP_SHOWTIP event=INTENT"))
assert(has("IIP_SHOWTIP event=CORRELATED"))
assert(S.pose_reads==0 and S.released==0)
""")

    def test_unloaded_event_cleanly_does_not_register(self):
        self.case(r"""
begin();tick()
assert(S.binds==0 and S.cancelled==1)
assert(has("event=HOOK_UNAVAILABLE") and has("coverage=none"))
""","set(event_fn,'live',false)")

    def test_hook_rejection_cancels_observer_without_broad_fallback(self):
        self.case(r"""
begin();tick()
assert(S.binds==1 and S.cancelled==1)
assert(has("event=HOOK_UNAVAILABLE"))
assert(not S.cb.event and S.registered==0)
""","S.reject=true")

    def test_native_function_flag_mismatch_blocks(self):
        self.case(r"""
begin();tick()
assert(S.binds==0 and S.cancelled==1)
assert(has("unexpectedly marked native"))
""","S.native_flag=true")

if __name__=="__main__":
    unittest.main()
