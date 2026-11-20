# SPDX-License-Identifier: MPL-2.0
"""Quintus visual defaults on native World; no synthetic inheritance or runtime claim."""
import unittest
from lupa import LuaRuntime
from test_ui_child import ROOT

SRC=(ROOT/"research/interaction-prompts-owner/world-space/native-world-template/Scripts/IIPTemplateStyle.lua").read_text(encoding="utf8")
FIXTURE=r"""
S={loc={X=10,Y=20,Z=30},scale={X=2,Y=3,Z=4},collision=0,logs={},ticks=0}
local c={p="/Game/Test.World.ExtendedWidget",cls="/Script/Genesis.ExtendedWidgetComponent",
         Space=0}
function c:IsValid()return true end
function c:GetFullName()return "Object "..self.p end
function c:GetAddress()return 111 end
function c:GetClass()return {IsValid=function()return true end,GetFullName=function()
    return "Class "..c.cls end}end
function c:GetCollisionEnabled()return S.collision end
function c:K2_GetComponentLocation()return {X=S.loc.X,Y=S.loc.Y,Z=S.loc.Z} end
function c:SetRelativeScale3D(v)
    S.scale={X=v.X,Y=v.Y,Z=v.Z}
    if S.reject_scale then S.scale.X=99 end
end
function c:K2_AddWorldOffset(v)
    S.loc.Z=S.loc.Z+v.Z
end
function c:K2_SetWorldLocation(p)
    S.loc={X=p.X,Y=p.Y,Z=p.Z}
end
setmetatable(c,{__index=function(_,k)if k=="RelativeScale3D"then return S.scale end end})
S.component=c
function S.log(event,data)S.logs[#S.logs+1]=event.." "..data end
function S.has(p)
    for _,s in ipairs(S.logs)do if s:find(p,1,true)then return true end end
    return false
end
"""
class NativeTemplateVisual(unittest.TestCase):
    def case(self,body):
        lua=LuaRuntime()
        lua.execute(FIXTURE)
        lua.execute('M=(function()\n'+SRC+'\nend)()')
        lua.execute(body)

    def test_global_z_lift_and_relative_scale_exact_and_once(self):
        self.case("""
        local old,pos=M.geometry(S.component)
        assert(pos.Z==30 and old.X==2)
        assert(math.abs(S.loc.Z-66)<.001)
        assert(math.abs(S.scale.X-.8)<.001)
        assert(math.abs(S.scale.Y-1.2)<.001)
        assert(math.abs(S.scale.Z-1.6)<.001)
        assert(S.loc.X==10 and S.loc.Y==20)
        """)

    def test_reject_non_world_and_collision_component_without_writes(self):
        for setup in ("S.component.Space=1","S.collision=1","S.scale.X=-1"):
            with self.subTest(setup=setup):
                self.case(setup+"""
                assert(not pcall(M.geometry,S.component))
                assert(S.loc.Z==30 and S.scale.Y==3)
                """)

    def test_bad_transform_readback_rolls_back(self):
        self.case("""
        S.reject_scale=true
        assert(not pcall(M.geometry,S.component))
        assert(S.loc.Z==30)
        assert(S.scale.Y==3 and S.scale.Z==4)
        """)

    def test_canshow_restores_continuous_native_component_tick(self):
        self.case("""
        local state={tint_pending=true,tint={R=.8,G=.6,B=.4,A=.7}}
        local probe={
            verify_tint=function()return true end,
            continuous_tick=function()S.ticks=S.ticks+1;return .2 end}
        M.can_show(S.component,{},state,probe,S.log)
        assert(S.ticks==1 and not state.tint_pending)
        assert(S.has("STYLE_TINT_VERIFIED") and S.has("STYLE_CADENCE source=CanShow"))
        """)

    def test_rendering_decoration_needs_actual_native_tiphud(self):
        self.case("""
        assert(not pcall(M.decorate,S.component,{}))
        """)

if __name__=="__main__": unittest.main()
