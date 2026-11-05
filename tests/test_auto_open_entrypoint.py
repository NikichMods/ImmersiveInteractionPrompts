# SPDX-License-Identifier: MPL-2.0
"""Exercise the research auto-event Lua entry and native visibility boundary."""
import unittest

from test_ui_child import LuaRuntime, ROOT
from test_beginplay_join import FIXTURE

BASE=ROOT/"research/interaction-prompts-owner/world-space/auto-target"
NAMES=("IIPOpenSource","IIPTargetPolicy","IIPOpenEvents","IIPOpenVisibility")
SOURCES={name:(BASE/(name+".lua")).read_text(encoding="utf-8") for name in NAMES}
ENTRY=(BASE/"main.lua").read_text(encoding="utf-8")

VISIBILITY_MOCK=r"""
S.game=true
Visibility=(function()
""" + SOURCES["IIPOpenVisibility"] + r"""
end)()
local t=make("/World.WidgetTree","/Script/UMG.WidgetTree")
local root=make("/World.Root","/Script/UMG.CanvasPanel")
local retainer=make(t.p..".RetainerBox_0","/Script/UMG.RetainerBox")
local leaf=make("/World.NativeHint","/Script/UMG.Image")
set(P.widget,"WidgetTree",t)
set(t,"RootWidget",root)
set(retainer,"GetOuter",function()return t end)
set(retainer,"GetParent",function()return root end)
set(root,"GetParent",function()return nil end)
set(retainer,"GetChildrenCount",function()return 1 end)
set(retainer,"GetChildAt",function()return leaf end)
set(leaf,"GetParent",function()return retainer end)
for _,o in ipairs({P.widget,P.text,root,retainer,leaf})do
 set(o,"Visibility",0);set(o,"RenderOpacity",1);set(o,"bIsEnabled",true)
end
S.native_retainer=retainer
S.native_leaf=leaf
function is_alive(o)return o~=nil and o:IsValid()end
"""

ENTRY_MOCK=r"""
S.game=true
S.callbacks={}
S.cancelled=0
set(P.text,"GetText",function()return P.text.Text end)
RegisterBeginPlayPostHook=function(fn)S.callbacks.begin=fn end
RegisterEndPlayPreHook=function(fn)S.callbacks.finish=fn end
RegisterLoadMapPreHook=function(fn)S.callbacks.map=fn end
LoopInGameThreadAfterFrames=function(frames,fn)
 assert(frames==30);S.callbacks.tick=fn;return 12
end
CancelDelayedAction=function(handle)
 assert(handle==12);S.cancelled=S.cancelled+1;return true
end
local f=make("/Script/Engine.KismetSystemLibrary:IsValid","Function")
set(f,"type",function()return "UFunction"end)
getmetatable(f).__call=function(_,_,o)return o:IsValid()end
make("/Script/Engine.Default__KismetSystemLibrary","/Script/Engine.KismetSystemLibrary")
for _,name in ipairs({"IIPOpenSource","IIPTargetPolicy","IIPOpenEvents","IIPOpenVisibility"})do
 assert(type(package.preload[name])=="function")
end
"""

class EntryAndVisibility(unittest.TestCase):
    def test_native_tip_chain_and_fade_are_read_only(self):
        lua=LuaRuntime(unpack_returned_tuples=True)
        lua.execute(FIXTURE);lua.execute(VISIBILITY_MOCK)
        lua.execute(r"""
assert(Visibility.visible(P.widget,is_alive))
set(S.native_leaf,"Visibility",1)
assert(not Visibility.visible(P.widget,is_alive))
set(S.native_leaf,"Visibility",0)
set(P.text,"RenderOpacity",0.3)
assert(not Visibility.visible(P.widget,is_alive))
set(P.text,"RenderOpacity",1)
assert(Visibility.visible(P.widget,is_alive))
set(S.native_retainer,"GetChildrenCount",function()return 2 end)
assert(not pcall(Visibility.visible,P.widget,is_alive))
assert(S.registered==0)
""")

    def preload(self,lua):
        for name,code in SOURCES.items():
            lua.execute(
                "package.preload[" + repr(name) + "]=function()\n"
                + "return (function()\n" + code + "\nend)()\nend"
            )

    def test_normal_loader_entry_registers_global_events_without_input_chord(self):
        lua=LuaRuntime(unpack_returned_tuples=True)
        lua.execute(FIXTURE)
        self.preload(lua)
        lua.execute(ENTRY_MOCK)
        lua.execute(VISIBILITY_MOCK)
        lua.execute(ENTRY)
        lua.execute(r"""
assert(type(S.callbacks.begin)=="function" and type(S.callbacks.finish)=="function")
assert(type(S.callbacks.tick)=="function" and type(S.callbacks.map)=="function")
assert(has("IIP_OPEN_AUTO event=ARMED"))
S.callbacks.begin({get=function()return P.actor end})
assert(has("IIP_OPEN_AUTO event=JOINED"))
S.callbacks.tick()
assert(has("IIP_OPEN_AUTO event=SELECTION") and not has("IIP_OPEN_AUTO event=STOP"))
assert(S.registered==0 and S.pose_reads==0)
""")

    def test_missing_loader_api_fails_closed_before_registration(self):
        lua=LuaRuntime(unpack_returned_tuples=True)
        lua.execute(FIXTURE)
        self.preload(lua)
        lua.execute(ENTRY_MOCK)
        lua.execute("RegisterEndPlayPreHook=nil")
        lua.execute(ENTRY)
        lua.execute(r"""
assert(has("IIP_OPEN_AUTO event=UNAVAILABLE"))
assert(S.callbacks.begin==nil and S.callbacks.tick==nil)
assert(S.registered==0)
""")

if __name__=="__main__":
    unittest.main()
