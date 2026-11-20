# SPDX-License-Identifier: MPL-2.0
"""Quintus visual defaults on native World; no synthetic inheritance or runtime claim."""
import unittest
from lupa import LuaRuntime
from test_ui_child import ROOT

SRC=(ROOT/"research/interaction-prompts-owner/world-space/native-world-template/Scripts/IIPTemplateStyle.lua").read_text(encoding="utf8")
FIXTURE=r"""
S={loc={X=10,Y=20,Z=30},scale={X=2,Y=3,Z=4},collision=0,logs={},ticks=0}
S.rotation={Pitch=-24,Yaw=172,Roll=13}
S.rotation_writes=0
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
function c:K2_GetComponentRotation()
    return S.rotation
end
function c:K2_SetWorldRotation(r,sweep,hit,teleport)
    assert(sweep==false and type(hit)=="table" and teleport==true)
    S.rotation_writes=S.rotation_writes+1
    S.rotation={Pitch=r.Pitch,Yaw=r.Yaw,Roll=r.Roll}
    if S.reject_rotation and S.rotation_writes==1 then S.rotation.Yaw=88 end
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

    def test_upright_removes_world_tilt_without_changing_heading_or_other_geometry(self):
        self.case("""
        assert(M.upright(S.component))
        assert(S.rotation.Pitch==0 and S.rotation.Roll==0 and S.rotation.Yaw==172)
        assert(S.loc.X==10 and S.loc.Y==20 and S.loc.Z==30)
        assert(S.scale.X==2 and S.scale.Y==3 and S.scale.Z==4)
        assert(not M.upright(S.component) and S.rotation_writes==1)
        """)

    def test_failed_orientation_readback_restores_original_transform(self):
        self.case("""
        S.reject_rotation=true
        assert(not pcall(M.upright,S.component))
        assert(S.rotation_writes==2)
        assert(S.rotation.Pitch==-24 and S.rotation.Roll==13 and S.rotation.Yaw==172)
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


    def test_action_tokens_are_provisional_and_tag_based(self):
        self.case("""
        assert(M.token_for("Open")=="OPEN" and M.token_for("Take")=="TAKE")
        assert(M.token_for("Check")=="CHECK" and M.token_for("Talk")=="TALK")
        assert(M.token_for("Interact")=="ACTION" and M.token_for(nil)=="ACTION")
        """)

    def test_early_measured_native_center_without_changing_stock_slot(self):
        self.case("""
        local slot={
            Content={GetAddress=function() return 222 end, IsValid=function() return true end},
            GetAutoSize=function() return true end,
            GetPosition=function()return {X=38,Y=0} end,
            GetAlignment=function()return {X=0,Y=.5} end,
            GetAnchors=function()return {Minimum={X=0},Maximum={X=0}} end,
            GetClass=function()return {IsValid=function() return true end,
                GetFullName=function()return "Class /Script/UMG.CanvasPanelSlot" end}end,
            IsValid=function()return true end
        }
        local stock={Slot=slot,
            Text={ToString=function()return "Взять" end},
            GetDesiredSize=function()return {X=72,Y=37} end,
            GetAddress=function()return 222 end,IsValid=function()return true end}
        local x,mode=M.center_for(stock,"Take")
        assert(x==74 and mode=="measured")
        """)

    def test_unready_or_placeholder_geometry_uses_immediate_tag_fallback(self):
        self.case("""
        local stock={Text={ToString=function()return "???" end}}
        local x,mode=M.center_for(stock,"Take")
        assert(x==70 and mode=="fallback")
        x,mode=M.center_for(stock,"Talk")
        assert(x==121.75 and mode=="fallback")
        x,mode=M.center_for(stock,"Open")
        assert(x==81 and mode=="fallback")
        x,mode=M.center_for(stock,"Check")
        assert(x==93 and mode=="fallback")
        x,mode=M.center_for(stock,"Other")
        assert(x==80 and mode=="fallback")
        """)

    def test_action_refresh_updates_only_owned_label_once(self):
        self.case("""
        local label={p="/Game/Test.WidgetTree.IIP_WQ_Aphes",txt="ACTION"}
        function label:IsValid()return true end
        function label:GetAddress()return 888 end
        function label:GetFullName()return "TextBlock "..self.p end
        function label:GetClass()return {
            IsValid=function()return true end,
            GetFullName=function()return "Class /Script/UMG.TextBlock" end}end
        function label:SetText(v)self.txt=v end
        StaticFindObject=function(p)if p==label.p then return label end end
        FText=function(v)return v end
        local state={decorated=true,header=label.p,header_address=888,tag="Interact"}
        M.refresh_action(state,"Talk",S.log)
        assert(label.txt=="TALK" and state.tag=="Talk" and S.has("STYLE_ACTION_UPDATED"))
        M.refresh_action(state,"Talk",S.log)
        M.refresh_action(state,"Bad",S.log)
        assert(label.txt=="TALK" and state.tag=="Talk")
        """)

    def test_rendering_decoration_needs_actual_native_tiphud(self):
        self.case("""
        assert(not pcall(M.decorate,S.component,{}))
        """)

if __name__=="__main__": unittest.main()
