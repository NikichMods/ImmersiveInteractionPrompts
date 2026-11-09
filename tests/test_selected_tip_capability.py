# SPDX-License-Identifier: MPL-2.0
"""Selected-native TipHUD reader: source-only, no action-list or actor-base assumptions."""
from pathlib import Path
import unittest
from lupa import LuaRuntime

SOURCE = (Path(__file__).resolve().parents[1] /
          "research/interaction-prompts-owner/world-space/selected-owner-world"
          "/Scripts/IIPInteractionSource.lua")
RIG = r'''
EObjectFlags={RF_ClassDefaultObject=1,RF_ArchetypeObject=2}
local function obj(path,classname,address)
 local o={_path=path,_class=classname,_address=address,_valid=true}
 function o:IsValid()return self._valid end
 function o:GetFullName()return "Object "..self._path end
 function o:GetAddress()return self._address end
 function o:GetClass()return {
  GetFullName=function()return "Class "..self._class end,
  GetSuperStruct=function()return nil end
 }end
 function o:HasAnyFlags()return false end
 return o
end
native_alive=function(o)return o~=nil and o:IsValid()end
actor=obj("/Game/Test.World.NPC1","/Game/Test.NPCInteract_Bp_C",11)
argument=obj("/Game/Test.World.NPC1.Argument","/Script/Genesis.TipHUDArgumentComponent",12)
argument.msgTag={ToString=function()return "Talk"end}
argument.ActionName=99 -- ActionName must not be assumed to equal legacy 25.
function argument:GetOwner()return actor end
actor.TipHUDArgument=argument
component=obj("/Game/Test.World.NPC1.ExtendedWidget","/Script/Genesis.ExtendedWidgetComponent",13)
function component:GetOwner()return actor end
function component:GetWidgetSpace()return 1 end
component.bVisible=true
component.bAddedToScreen=true
actor.ExtendedWidget=component
widget=obj("/Game/Test.World.NPC1.TipHUD","/Game/MainContent/Template/UMG/TipHUD.TipHUD_C",14)
function component:GetUserWidgetObject()return widget end
function component:GetWidget()return widget end
component.Widget=widget
label=obj("/Game/Test.World.NPC1.TipHUD.TextBlock_89","/Script/UMG.TextBlock",15)
label.value="Говорить"
function label:GetText()return {ToString=function()return label.value end}end
widget.TextBlock_89=label
hint=function()return true end
'''

class SelectedTipCapability(unittest.TestCase):
    def check(self,code):
        vm=LuaRuntime(unpack_returned_tuples=True)
        vm.execute(RIG)
        vm.globals().Source=vm.execute(SOURCE.read_text(encoding="utf-8"))
        vm.execute(code)

    def test_talk_on_unrelated_class_does_not_change_legacy_world_gate(self):
        self.check(r'''
local row,why=Source.inspect_selected(actor,native_alive,hint)
assert(row and why=="ready" and row.action=="Talk")
assert(row.native_text=="Говорить" and row.native_screen)
assert(row.hint_state=="visible" and row.refs.actor.address==11)
local old,reason=Source.acquire(actor)
assert(old==nil and reason=="unrelated_actor")
''')

    def test_other_actions_and_unknown_hints_remain_read_only(self):
        self.check(r'''
for _,name in ipairs({"Interact","Knock","Press","Break"})do
 argument.msgTag={ToString=function()return name end}
 local row=Source.inspect_selected(actor,native_alive,hint)
 assert(row and row.action==name)
end
hint=function()return false end
local row=Source.inspect_selected(actor,native_alive,hint)
assert(row and row.hint_state=="hidden")
hint=function()error("cannot verify input hint")end
row=Source.inspect_selected(actor,native_alive,hint)
assert(row and row.hint_state=="unknown")
''')

    def test_wrong_owner_missing_source_and_non_screen_fail_closed(self):
        self.check(r'''
function argument:GetOwner()return widget end
local row,why=Source.inspect_selected(actor,native_alive,hint)
assert(row==nil and why=="no_matching_argument")
function argument:GetOwner()return actor end
actor.ExtendedWidget=nil
row,why=Source.inspect_selected(actor,native_alive,hint)
assert(row==nil and why=="no_matching_source")
actor.ExtendedWidget=component
function component:GetWidgetSpace()return 0 end
row,why=Source.inspect_selected(actor,native_alive,hint)
assert(row==nil and why=="native_screen_not_shown")
''')

    def test_missing_text_and_invalid_widget_fail_closed(self):
        self.check(r'''
for _,value in ipairs({"",string.rep("x",513),"hello\nthere"})do
 label.value=value
 local row,why=Source.inspect_selected(actor,native_alive,hint)
 assert(row==nil and why=="native_text_not_ready")
end
label.value="Говорить"
widget._valid=false
local row,why=Source.inspect_selected(actor,native_alive,hint)
assert(row==nil and why=="no_matching_tiphud")
''')

if __name__=="__main__":
    unittest.main()
