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

    def test_face_camera_keeps_world_up_and_turns_toward_the_approach_side(self):
        self.case("""
        local camera={X=10,Y=-100,Z=300}
        local manager={IsValid=function()return true end,GetCameraLocation=function()return camera end}
        local widget={GetOwningPlayerCameraManager=function()return manager end}
        assert(M.face_camera(S.component,widget))
        assert(S.rotation.Pitch==0 and S.rotation.Roll==0 and S.rotation.Yaw==-90)
        assert(S.loc.X==10 and S.loc.Y==20 and S.loc.Z==30)
        assert(S.scale.X==2 and S.scale.Y==3 and S.scale.Z==4)
        camera={X=10,Y=20,Z=300}
        assert(not M.face_camera(S.component,widget) and S.rotation_writes==1)
        """)

    def test_canshow_restores_continuous_native_component_tick(self):
        self.case("""
        local state={tint_pending=true,tint={R=.8,G=.6,B=.4,A=.7}}
        local probe={
            verify_tint=function(_,baseline,factor)
                assert(baseline.A==.7 and factor==.50)
                return true
            end,
            continuous_tick=function()S.ticks=S.ticks+1;return .2 end}
        M.can_show(S.component,{},state,probe,S.log)
        assert(S.ticks==1 and not state.tint_pending)
        assert(S.has("STYLE_TINT_VERIFIED rgb=0.50") and S.has("STYLE_CADENCE source=CanShow"))
        """)

    def test_door_plane_uses_player_side_and_restores_original_pose(self):
        self.case("""
        local c=S.component
        local actor={IsValid=function()return true end,GetAddress=function()return 99 end}
        local function part(id,x,y,z,parent)
            return {
                IsValid=function()return true end,GetOwner=function()return actor end,
                GetAddress=function()return id end,GetAttachParent=function()return parent end,
                K2_GetComponentLocation=function()return {X=x,Y=y,Z=z} end
            }
        end
        actor.RootComponent=part(1,0,0,0)
        actor.WidgetLocator=part(2,0,0,180,actor.RootComponent)
        actor.front_CharacterAlign=part(3,0,55,0)
        actor.rear_CharacterAlign=part(4,0,-60,0)
        local status="close"
        actor.CurrentState={ToString=function()return status end}
        function c:GetAttachParent()return actor.WidgetLocator end
        c.bVisible=true
        S.rotation={Yaw=90,Pitch=0,Roll=0}
        local player={X=0,Y=2,Z=0}
        local pawn={IsValid=function()return true end,K2_GetActorLocation=function()return player end}
        local w={RenderOpacity=1,GetOwningPlayerPawn=function()return pawn end}
        local state={}
        assert(not M.door_plane(c,w,actor,state,"Open") and S.loc.Y==20)
        player.Y=70
        local changed,side=M.door_plane(c,w,actor,state,"Open")
        assert(changed and side==1 and S.loc.Y==24 and S.rotation.Yaw==90)
        assert(not M.door_plane(c,w,actor,state,"Open"))
        player.Y=-70
        changed,side=M.door_plane(c,w,actor,state,"Open")
        assert(changed and side==-1 and S.loc.Y==-24 and S.rotation.Yaw==-90)
        assert(S.loc.X==10 and S.loc.Z==30)
        status="open"
        assert(M.door_plane(c,w,actor,state,"Open"))
        assert(S.loc.Y==20 and S.rotation.Yaw==90 and state.door_pose==nil)
        """)


    def test_invented_aphes_words_are_stable_distinct_ascii_per_verified_tag(self):
        self.case("""
        -- Stock InteractTipToText row names verified by the offline reader.
        local rows={"Climb","Restart","Interact","Open","Talk","Gossip","Knock",
                    "Heal","Insert","Remove","Press","Take","Break","Enter",
                    "Check","Activate","Pray","UILoadTest"}
        local used={}
        for _,tag in ipairs(rows) do
            local actual=M.token_for(tag)
            assert(actual~="ACTION" and actual:match("^[A-Z]+$"),tag)
            assert(#actual>=4 and #actual<=8)
            assert(not used[actual],actual)
            used[actual]=true
        end
        assert(M.token_for("Open")=="ANOKE" and M.token_for("Take")=="LAVO")
        assert(M.token_for("Check")=="SKERA" and M.token_for("Talk")=="LETHO")
        """)

    def test_unknown_tags_get_the_neutral_header(self):
        self.case("""
        assert(M.token_for(nil)=="ACTION")
        for _,tag in ipairs({"","None","Descend","talk","UNKNOWN_UNMAPPED"}) do
            assert(M.token_for(tag)=="ACTION",tag)
        end
        """)

    def test_fixed_placement_uses_only_the_action_tag(self):
        self.case("""
        assert(M.placement_x("Take")==70 and M.placement_x("Open")==81)
        assert(M.placement_x("Check")==93)
        assert(M.placement_x("Talk")==121.75 and M.placement_x("Interact")==121.75)
        assert(M.placement_x("Other")==80 and M.placement_x(nil)==80)
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
        assert(label.txt=="LETHO" and state.tag=="Talk" and S.has("STYLE_ACTION_UPDATED"))
        M.refresh_action(state,"Talk",S.log)
        M.refresh_action(state,"Bad",S.log)
        assert(label.txt=="LETHO" and state.tag=="Talk")
        """)


    def test_grille_inactive_state_is_reported_without_any_world_write(self):
        self.case("""
        local actor={CurrentState={ToString=function()return "Close" end}}
        local state={}
        local changed,side,reason=M.door_plane(S.component,
            {RenderOpacity=1},actor,state,"Open")
        assert(changed==false and side==nil and reason=="inactive_state=Close")
        assert(S.rotation_writes==0 and S.loc.Z==30 and state.door_pose==nil)
        """)

    def test_grille_native_visibility_skip_is_read_only(self):
        self.case("""
        local actor={CurrentState={ToString=function()return "close" end}}
        local state={}
        S.component.bVisible=false
        local changed,side,reason=M.door_plane(S.component,
            {RenderOpacity=1},actor,state,"Open")
        assert(changed==false and side==nil and reason=="native_not_visible")
        assert(S.rotation_writes==0 and S.loc.Z==30 and state.door_pose==nil)
        """)

    def test_grille_non_open_tag_does_not_touch_world_component(self):
        self.case("""
        local actor={CurrentState={ToString=function()return "close" end}}
        local state={}
        local changed,side,reason=M.door_plane(S.component,
            {RenderOpacity=1},actor,state,"Check")
        assert(changed==false and reason=="inactive_state=close")
        assert(S.rotation_writes==0 and S.loc.Z==30 and state.door_pose==nil)
        """)

    def test_rendering_decoration_needs_actual_native_tiphud(self):
        self.case("""
        assert(not pcall(M.decorate,S.component,{}))
        """)

if __name__=="__main__": unittest.main()
