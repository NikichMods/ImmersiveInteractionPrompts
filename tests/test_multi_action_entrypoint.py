# SPDX-License-Identifier: MPL-2.0
"""Exercise the standalone multi-action diagnostic loader under UE4SS mocks."""
import unittest

from test_ui_child import LuaRuntime, ROOT
from test_beginplay_join import FIXTURE

BASE=ROOT/"research/interaction-prompts-owner/world-space/multi-action"
MODULES=("IIPInteractionSource","IIPInteractionEvents","IIPOpenVisibility")
ENTRY=(BASE/"main.lua").read_text(encoding="utf-8")
MOCK=r"""
S.game=true
S.callbacks={}
set(P.text,"GetText",function()return P.text.Text end)
RegisterBeginPlayPostHook=function(f)S.callbacks.begin=f end
RegisterEndPlayPreHook=function(f)S.callbacks.finish=f end
RegisterLoadMapPreHook=function(f)S.callbacks.map=f end
LoopInGameThreadAfterFrames=function(frames,f)
  assert(frames==30);S.callbacks.tick=f;return 77
end
CancelDelayedAction=function(h)
  assert(h==77);S.cancelled=(S.cancelled or 0)+1;return true
end
"""

class MultiActionEntrypoint(unittest.TestCase):
    def case(self,code,setup=""):
        lua=LuaRuntime(unpack_returned_tuples=True)
        lua.execute(FIXTURE)
        for name in MODULES:
            module=(BASE/(name+".lua")).read_text(encoding="utf-8")
            lua.execute("package.preload["+repr(name)+"]=function()\n"+
                "return (function()\n"+module+"\nend)()\nend")
        lua.execute(MOCK)
        lua.execute(setup)
        lua.execute(ENTRY)
        lua.execute(code)

    def test_load_and_native_event_subscription_without_user_arm(self):
        self.case(r"""
assert(type(S.callbacks.begin)=="function")
assert(type(S.callbacks.finish)=="function")
assert(type(S.callbacks.map)=="function")
assert(type(S.callbacks.tick)=="function")
assert(has("IIP_MULTI_ACTION event=ARMED actions=Open,Take,Check"))
S.callbacks.begin({get=function()return P.actor end})
assert(has("IIP_MULTI_ACTION event=JOINED owner=1 action=Open"))
assert(S.registered==0 and S.pose_reads==0)
""")

    def test_unavailable_api_does_not_register_any_hook(self):
        self.case(r"""
assert(has("IIP_MULTI_ACTION event=UNAVAILABLE"))
assert(S.callbacks.begin==nil and S.callbacks.tick==nil)
assert(S.registered==0)
""","RegisterEndPlayPreHook=nil")

if __name__=="__main__":
    unittest.main()
