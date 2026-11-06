# SPDX-License-Identifier: MPL-2.0
"""UE4SS loader integration for automatic World prompts, without the game."""
import unittest
from test_ui_child import LuaRuntime, ROOT
from test_beginplay_join import FIXTURE
from test_multi_action_observer import RIG

BASE=ROOT/"research/interaction-prompts-owner/world-space/auto-world-successor/Scripts"
ENTRY=(BASE/"main.lua").read_text(encoding="utf8")
MODULES=("IIPInteractionSource","IIPInteractionEvents","IIPWorldHandoff",
         "IIPWorldHandoffBridge","IIPWorldRenderer","IIPWorldTarget",
         "IIPAutoWorldSession")
MOCK=r"""
S.game=true;S.cb={};S.cancelled={};S.world={owned=false,creates=0,cleans=0}
EngineTickAvailable=true
RegisterBeginPlayPostHook=function(fn)S.cb.begin=fn end
RegisterEndPlayPreHook=function(fn)S.cb.finish=fn end
RegisterLoadMapPreHook=function(fn)S.cb.map=fn end
LoopInGameThreadAfterFrames=function(n,fn)
 if n==3 then assert(not S.cb.sample);S.cb.sample=fn;return 77 end
 if n==1 then
  if S.fail_world_loop then error("World pump registration failed")end
  assert(not S.cb.frame);S.cb.frame=fn;return 88
 end
 error("unsupported loop interval")
end
CancelDelayedAction=function(handle)
 assert(handle==77 or handle==88)
 S.cancelled[handle]=(S.cancelled[handle] or 0)+1;return true
end
local isvalid=make("/Script/Engine.KismetSystemLibrary:IsValid","Function")
set(isvalid,"type",function()return "UFunction"end)
getmetatable(isvalid).__call=function(_,_,o)return o:IsValid()end
make("/Script/Engine.Default__KismetSystemLibrary",
     "/Script/Engine.KismetSystemLibrary")
"""
FAKE_WORLD=r"""
local w=S.world
return {
 prepare=function()end,refresh_assets=function()end,
 empty=function()return not w.owned end,
 create=function(a,c,widget,stop,action)
  assert(not w.owned and a and c and widget)
  w.owned=true;w.creates=w.creates+1;w.action=action
 end,
 cleanup=function()
  assert(w.owned);w.owned=false;w.cleans=w.cleans+1;return true
 end,
 hide=function()return true end,
 resume=function()return true end,
 refresh=function()return true end,
}
"""
VIS=r"""
return {visible=function(w,alive)
 return alive(w) and w.Visibility==0 and w.RenderOpacity==1
end}
"""

class AutomaticWorldEntrypoint(unittest.TestCase):
    def case(self,code,extra=""):
        lua=LuaRuntime(unpack_returned_tuples=True)
        lua.execute(FIXTURE)
        lua.execute(RIG)
        for name in MODULES:
            s=(BASE/(name+".lua")).read_text(encoding="utf8")
            lua.execute('package.preload["'+name+'"]=function()\n'+
                s+'\nend')
        lua.execute('package.preload["IIPWorldChild"]=function()\n'+
            FAKE_WORLD+'\nend')
        lua.execute('package.preload["IIPOpenVisibility"]=function()\n'+
            VIS+'\nend')
        lua.execute(MOCK)
        lua.execute(extra)
        lua.execute(ENTRY)
        lua.execute(code)

    def test_real_main_registers_both_game_thread_loops_on_normal_load(self):
        self.case(r"""
assert(S.cb.begin and S.cb.finish and S.cb.map)
assert(S.cb.sample and S.cb.frame)
assert(has("IIP_AUTO_WORLD event=ARMED actions=Open,Take,Check"))
assert(S.world.creates==0 and S.registered==0)
S.cb.begin(wrap(P.actor))
S.cb.sample();S.cb.sample()
S.cb.frame();S.cb.frame()
assert(S.world.creates==1 and S.world.action=="Open")
assert(S.registered==0)
""")

    def test_missing_ue4ss_api_is_inert_before_native_hook_registration(self):
        self.case(r"""
assert(has("IIP_AUTO_WORLD event=UNAVAILABLE"))
assert(S.cb.begin==nil and S.cb.sample==nil and S.cb.frame==nil)
assert(S.world.creates==0)
""", "RegisterEndPlayPreHook=nil")

    def test_missing_engine_tick_is_inert(self):
        self.case(r"""
assert(has("IIP_AUTO_WORLD event=UNAVAILABLE"))
assert(S.cb.begin==nil and S.cb.frame==nil)
""","EngineTickAvailable=false")

    def test_failed_second_loop_disarms_observer_and_never_creates(self):
        self.case(r"""
assert(S.cb.begin and S.cb.sample and S.cb.frame==nil)
assert(has("event=UNAVAILABLE") and S.cancelled[77]==1)
S.cb.begin(wrap(P.actor))
S.cb.sample()
assert(S.world.creates==0)
""","S.fail_world_loop=true")

if __name__=="__main__":
    unittest.main()
