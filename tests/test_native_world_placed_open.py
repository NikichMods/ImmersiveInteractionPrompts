# SPDX-License-Identifier: MPL-2.0
"""Bounded mock of one placed Open's creation, late loading, and original component.

This is research control-flow evidence, never proof of a real pre-OnRegister window.
"""
import unittest
from lupa import LuaRuntime
from test_ui_child import ROOT

SOURCE = (ROOT / "research/interaction-prompts-owner/world-space/native-world-quintus/Scripts/main.lua").read_text(encoding="utf-8")

FIXTURE = r"""
S={logs={},collision=1,render_target=false}
local level="/Game/MainContent/Maps/sublevel_plot/0-1/0-1_plot_outerRimA_interact1.0-1_plot_outerRimA_interact1:PersistentLevel."
OPEN=level.."0-1_lootbox_01_mat_ST001"
TAKE=level.."0-1_item_loot_bag_03_AP1_3"
CHECK=level.."0-1_sosletter3_2"
OPEN_CLASS="/Game/MainContent/Act/Discoveries_BP/common/item_lootbox02.item_lootbox02_C"
COMPONENT="/Script/Genesis.ExtendedWidgetComponent"
TIP="/Game/MainContent/Template/UMG/TipHUD.TipHUD_C"

local function obj(path,class,id)
    local t={p=path,c=class,id=id}
    function t:IsValid() return true end
    function t:GetFullName() return "Object "..self.p end
    function t:GetAddress() return self.id end
    function t:GetClass() return {GetFullName=function() return "Class "..self.c end} end
    return t
end
S.actor=obj(OPEN,OPEN_CLASS,100)
S.comp=obj(OPEN..".ExtendedWidget",COMPONENT,101)
S.widget=obj("/GameInstance.TestTipHUD",TIP,102)
S.rt=obj("/Transient.TestRT","/Script/Engine.TextureRenderTarget2D",103)
S.actor.ExtendedWidget=S.comp
S.comp.CreationMethod=0
S.comp.Space=1
S.comp.WidgetClass=nil
S.comp.bAddedToScreen=false
function S.comp:GetOuter() return S.actor end
function S.comp:GetOwner() return S.actor end
function S.comp:GetCollisionEnabled() return S.collision end
function S.comp:SetCollisionEnabled(v) if not S.refuse_collision then S.collision=v end end
function S.comp:GetUserWidgetObject() return S.widget end
function S.comp:GetRenderTarget() return S.render_target and S.rt or nil end
function StaticFindObject(p) if p==OPEN then return S.actor else return nil end end
function require(name)
    if name=="IIPQuintusResources" then return {prepare=function() end} end
    if name=="IIPQuintusProbe" then return {} end
    error("unexpected module: "..name)
end
function RegisterBeginPlayPostHook(fn) S.begin_hook=fn end
function NotifyOnNewObject(k,fn) assert(k==COMPONENT); S.new_hook=fn end
EngineTickAvailable=false
print=function(s) S.logs[#S.logs+1]=s end
function has(token)
    for _,line in ipairs(S.logs) do if line:find(token,1,true) then return true end end
    return false
end
function fire() assert(S.new_hook(S.comp)~=true) end
function begin() S.begin_hook({get=function() return S.actor end}) end
"""

class NativeWorldPlacedOpen(unittest.TestCase):
    def case(self, scenario):
        lua = LuaRuntime()
        lua.execute(FIXTURE)
        lua.execute(SOURCE)
        lua.execute(scenario)

    def test_one_exact_early_open_writes_and_retains_native_widget(self):
        self.case("""
            local widget=S.comp:GetUserWidgetObject()
            fire()
            assert(S.comp.Space==0 and S.collision==0)
            assert(S.comp:GetUserWidgetObject()==widget)
            assert(has("PLACED_OPEN_SET_WORLD"))
            S.comp.CreationMethod=2
            S.comp.WidgetClass=S.widget
            S.render_target=true
            begin()
            assert(has("PLACED_OPEN_BEGIN early_write=true same_instance=true space=0"))
            assert(has("widget=true rt=true added_to_screen=false"))
            assert(not has("event=UNAVAILABLE"))
        """)

    def test_late_or_restored_components_remain_screen(self):
        for setup in (
            "S.comp.CreationMethod=2",
            "S.comp.WidgetClass=S.widget",
            "S.comp.Space=0",
        ):
            with self.subTest(setup=setup):
                self.case(setup+"""
                    fire()
                    assert(not has("PLACED_OPEN_SET_WORLD"))
                    assert(has("PLACED_OPEN_SKIP reason=construction_state"))
                    assert(S.collision==1)
                    S.comp.Space=1
                    begin()
                    assert(has("PLACED_OPEN_BEGIN early_write=false"))
                    assert(not has("event=UNAVAILABLE"))
                """)

    def test_other_placed_actions_and_wrong_class_are_untouched(self):
        for target in ("TAKE", "CHECK"):
            self.case("S.actor.p="+target+";S.comp.p=S.actor.p..'.ExtendedWidget';"
                      "fire();assert(S.comp.Space==1 and S.collision==1);"
                      "assert(not has('PLACED_OPEN_SET_WORLD'))")
        self.case("""
            S.actor.c="/Script/Engine.Actor"
            fire()
            assert(S.comp.Space==1 and S.collision==1)
            assert(has("PLACED_OPEN_SKIP reason=actor_class"))
        """)

    def test_collision_refusal_stays_screen_without_global_stop(self):
        self.case("""
            S.refuse_collision=true
            fire()
            assert(S.comp.Space==1 and S.collision==1)
            assert(has("PLACED_OPEN_REJECTED"))
            assert(not has("event=UNAVAILABLE"))
            S.refuse_collision=false
            fire()
            assert(S.comp.Space==0 and has("PLACED_OPEN_SET_WORLD"))
        """)

    def test_serialization_overwrite_is_recorded_not_reasserted(self):
        self.case("""
            fire()
            assert(S.comp.Space==0)
            S.comp.Space=1
            S.comp.CreationMethod=2
            S.comp.WidgetClass=S.widget
            begin()
            assert(has("PLACED_OPEN_BEGIN early_write=true same_instance=true space=1"))
            assert(S.comp.Space==1)
            assert(not has("event=UNAVAILABLE"))
        """)

    def test_component_replacement_cannot_masquerade_as_trial(self):
        self.case("""
            fire()
            S.comp.id=999
            S.comp.CreationMethod=2
            S.comp.WidgetClass=S.widget
            begin()
            assert(has("PLACED_OPEN_BEGIN early_write=true same_instance=false"))
        """)

if __name__ == "__main__":
    unittest.main()
