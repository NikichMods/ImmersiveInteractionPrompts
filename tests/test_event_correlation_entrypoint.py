# SPDX-License-Identifier: MPL-2.0
"""Entrypoint registration contract with real Source/Observer Lua and mock host."""
import unittest
from test_ui_child import LuaRuntime, ROOT
from test_beginplay_join import FIXTURE

BASE=ROOT/"research/interaction-prompts-owner/world-space/event-driven/Scripts"
ENTRY=(BASE/"main.lua").read_text(encoding="utf-8")
MODULES=("IIPInteractionSource","IIPEventCorrelation")
HOST=r"""
S.game=true;S.cb={};S.loop_cancelled=0
EngineTickAvailable=true
RegisterBeginPlayPostHook=function(f)S.cb.begin=f end
RegisterEndPlayPreHook=function(f)S.cb.finish=f end
RegisterLoadMapPreHook=function(f)S.cb.map=f end
LoopInGameThreadAfterFrames=function(n,f)
 assert(n==1);S.cb.tick=f;return 73
end
CancelDelayedAction=function(h)
 assert(h==73);S.loop_cancelled=S.loop_cancelled+1;return true
end
local isvalid=make("/Script/Engine.KismetSystemLibrary:IsValid","Function")
set(isvalid,"type",function()return "UFunction"end)
getmetatable(isvalid).__call=function(_,_,o)return o:IsValid()end
make("/Script/Engine.Default__KismetSystemLibrary",
    "/Script/Engine.KismetSystemLibrary")
set(P.text,"GetText",function()return P.text.Text end)
function begin()
 S.cb.begin({get=function()return P.actor end})
end
function can()
 local hook=assert(S.hooks[SHOW])
 local result=hook.fn({get=function()return P.widget end})
 assert(result==nil,"CanShow native return overridden")
end
function tick(n)
 for i=1,(n or 1)do S.cb.tick()end
end
"""

class EventEntrypoint(unittest.TestCase):
    def case(self, body, setup=""):
        lua=LuaRuntime(unpack_returned_tuples=True)
        lua.execute(FIXTURE)
        lua.execute(HOST)
        for name in MODULES:
            src=(BASE/(name+".lua")).read_text(encoding="utf-8")
            lua.execute('package.preload["'+name+'"]=function()\n'+src+'\nend')
        lua.execute('package.preload["IIPOpenVisibility"]=function()\n'
                    'return {visible=function(w,alive)return alive(w) and '
                    'w.Visibility==0 and w.RenderOpacity==1 end}\nend')
        lua.execute(setup)
        lua.execute(ENTRY)
        lua.execute(body)

    def test_normal_load_registers_exact_script_hook_only_after_ready(self):
        self.case(r"""
assert(S.cb.begin and S.cb.finish and S.cb.map and S.cb.tick)
assert(S.registered==0 and not S.hooks[SHOW])
set(P.component,"bVisible",false)
begin();tick()
assert(S.registered==1 and S.hooks[SHOW].a==S.hooks[SHOW].b)
can();set(P.component,"bVisible",true);tick()
assert(has("event=CANSHOW_ARMED"))
assert(has("event=SHOW") and has("evidence=MATCHED_EVENT"))
assert(S.pose_reads==0 and S.released==0)
""")

    def test_missing_function_no_hook_and_no_coverage(self):
        self.case(r"""
begin();tick()
assert(S.registered==0 and S.loop_cancelled==1)
assert(has("event=CANSHOW_UNAVAILABLE") and has("coverage_claims=none"))
""","S.metadata_missing=true")

    def test_native_function_mismatch_fails_closed(self):
        self.case(r"""
begin();tick()
assert(S.registered==0 and S.loop_cancelled==1)
assert(has("event=STOP") and has("CanShow not verified non-native Blueprint"))
""","S.native_flag=true")

if __name__=="__main__":
    unittest.main()
