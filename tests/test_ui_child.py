# SPDX-License-Identifier: MPL-2.0
"""Bounded UI policy/rollback tests. Mocks do not prove UMG rendering or GC."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
try:
    from lupa.lua54 import LuaRuntime
except ModuleNotFoundError:
    sys.path.insert(0, json.loads((ROOT/'.local/environment.json').read_text(encoding='utf-8-sig'))['testLibraries'])
    from lupa.lua54 import LuaRuntime

SOURCE = (ROOT/'research/interaction-prompts-owner/ui-child/Scripts/main.lua').read_text(encoding='utf-8')
FIXTURE = r'''
S={game=false,now=1000,text="Открыть",created=0,attached=0,removed=0,logs={},queue={},timers={}}
local BASE="/Game/MainContent/Template/UMG/TipHUD.TipHUD_C"
local objects={}; local next_address=100
local function api() assert(S.game,"engine access outside game thread") end
local function make(kind,p,outer)
 next_address=next_address+1
 local o={kind=kind,p=p,addr=next_address,outer=outer,live=true}
 function o:IsValid() api(); return self.live end
 function o:GetAddress() api(); return self.addr end
 function o:GetFullName() api(); return self.kind.." "..self.p end
 function o:GetClass() api(); return {GetFullName=function()return "Class "..self.kind end} end
 function o:GetOuter() api(); return self.outer end
 function o:GetParent() api(); return self.parent end
 objects[p]=o; return o
end
local w=make(BASE,"/Transient.TipHUD")
local tree=make("/Script/UMG.WidgetTree",w.p..".WidgetTree",w)
local canvas=make("/Script/UMG.CanvasPanel",tree.p..".CanvasPanel_6",tree)
local stock=make("/Script/UMG.TextBlock",tree.p..".TextBlock_89",tree)
local original_slot=make("/Script/UMG.CanvasPanelSlot",canvas.p..".OriginalSlot",canvas)
function original_slot:GetPosition()return {X=S.bad_layout and 99 or 88,Y=0}end
function original_slot:GetAlignment()return {X=0,Y=0.5}end
function original_slot:GetAnchors()return {Minimum={X=0,Y=0.5},Maximum={X=0,Y=0.5}}end
stock.parent=canvas; stock.Slot=original_slot; stock.Visibility=0; stock.RenderOpacity=1; stock.Font={tag="unchanged_font",Size=22}
stock.Text={ToString=function()return S.text end}
setmetatable(stock,{__index=function(_,key)
 if key:match('^Set') then return function()error("ORIGINAL MUTATION")end end
end})
w.TextBlock_89=stock; w.WidgetTree=tree; w.Visibility=0; w.RenderOpacity=1; w.bIsEnabled=true
function canvas:GetChildrenCount()api();return 3 end
function canvas:AddChildToCanvas(label)
 api(); S.attached=S.attached+1; label.parent=self
 if S.attach_fail then error("attach failed after parenting") end
 local slot=make("/Script/UMG.CanvasPanelSlot",canvas.p..".OwnSlot",canvas)
 slot.Parent=self;slot.Content=label
 for _,key in ipairs({"SetAutoSize","SetAnchors","SetAlignment","SetPosition","SetSize"})do
  slot[key]=function()api();if S.slot_fail then error("slot configuration failed")end end
 end
 return slot
end
function canvas:RemoveChild(label)
 api(); if S.remove_fail then return false end
 assert(label==S.label,"removed foreign child"); label.parent=nil; S.removed=S.removed+1;return true
end
function StaticFindObject(p)
 api()
 if p==BASE..":CanShow" then
  return {IsValid=function()return not S.not_loaded end,type=function()return "UFunction"end,
   GetFullName=function()return "Function "..p end,GetFunctionFlags=function()return 0x0c420800 end}
 end
 if p=="/Script/UMG.TextBlock"then return {IsValid=function()return true end,type=function()return "UClass"end}end
 return objects[p]
end
function StaticConstructObject(class,outer,name,flags)
 api();S.created=S.created+1; assert(outer==tree and flags==64)
 local label=make("/Script/UMG.TextBlock",tree.p.."."..name,tree); S.label=label
 function label:SetVisibility(v)api();self.visibility=v end
 function label:SetFont(v)api();assert(v==stock.Font);if S.font_fail then error("font fail")end end
 function label:SetText(v)api();assert(v=="OPEN")end
 function label:SetJustification(v)api();assert(v==0)end
 return label
end
function FText(s)return s end
function FName(s)return s end
EObjectFlags={RF_Transient=64};Key={F9=9};ModifierKey={CONTROL=1,ALT=2}
EngineTickAvailable=true;EGameThreadMethod={EngineTick=1}
function IsKeyBindRegistered()return false end
function RegisterKeyBind(_,_,fn)S.key=fn end
function RegisterHook(_,fn)api();S.hook=fn;return 12,12 end
function ExecuteInGameThread(fn)S.queue[#S.queue+1]=fn end
function ExecuteInGameThreadWithDelay(_,fn)api();S.timers[#S.timers+1]=fn end
os.time=function()return S.now end
print=function(s)S.logs[#S.logs+1]=s end
function key()
 S.key();S.game=true;for _,fn in ipairs(S.queue)do fn()end;S.queue={};S.game=false
end
function call()
 w.Visibility=S.visibility or 0; w.bIsEnabled=not S.disabled; stock.Font.Size=S.font_size or 22
 S.game=true;local result=S.hook({get=function()return w end});S.game=false;assert(result==nil)
end
function timer()
 S.game=true;for _,fn in ipairs(S.timers)do fn()end;S.game=false
end
function disappear()
 for _,o in pairs(objects)do o.live=false end
end
function reparent()S.label.parent=make("/Script/UMG.CanvasPanel",tree.p..".Foreign",tree)end
function has(s)for _,x in ipairs(S.logs)do if x:find(s,1,true)then return true end end return false end
function original_ok()return stock.parent==canvas and stock.Slot==original_slot and stock.Font.tag=="unchanged_font"end
'''


class ChildPolicy(unittest.TestCase):
    def run_case(self, code):
        lua = LuaRuntime(unpack_returned_tuples=True)
        lua.execute(FIXTURE)
        lua.execute(SOURCE)
        lua.execute(code)
        self.assertTrue(lua.eval('original_ok()'))

    def test_no_writes_until_eligible(self):
        self.run_case('assert(S.created==0);key();S.text="Взять";call();assert(S.created==0)')

    def test_single_attachment_and_explicit_stop(self):
        self.run_case('key();call();for i=1,20 do call()end;assert(S.created==1 and S.attached==1);key();assert(S.removed==1);call();assert(S.created==1 and has("CLEANED"))')

    def test_timeout_without_further_callback(self):
        self.run_case('key();call();timer();assert(S.removed==1)')

    def test_target_text_change(self):
        self.run_case('key();call();S.text="Взять";call();assert(S.removed==1)')

    def test_partial_attachment_cleanup(self):
        for flag in ['attach_fail', 'slot_fail']:
            self.run_case(f'S.{flag}=true;key();call();assert(S.removed==1 and has("FAILED"));call();assert(S.created==1)')

    def test_pre_attachment_failure(self):
        self.run_case('S.font_fail=true;key();call();assert(S.created==1 and S.attached==0 and has("CLEANED"))')

    def test_missing_or_wrong_layout_no_creation(self):
        self.run_case('S.not_loaded=true;key();assert(S.created==0 and has("FAILED"))')
        self.run_case('S.bad_layout=true;key();call();assert(S.created==0 and has("FAILED"))')

    def test_remove_failure_reported_and_manual_retry(self):
        self.run_case('key();call();S.remove_fail=true;key();assert(has("CLEANUP_FAILED") and S.removed==0);S.remove_fail=false;key();assert(S.removed==1)')

    def test_destroyed_owner_not_dereferenced(self):
        self.run_case('key();call();disappear();timer();assert(S.removed==0 and has("CLEANED"))')

    def test_hidden_disabled_and_font_mismatch(self):
        for setup in ['S.visibility=2', 'S.disabled=true', 'S.font_size=56']:
            self.run_case(setup+';key();call();assert(S.created==0)')

    def test_external_reparent_is_not_removed(self):
        self.run_case('key();call();reparent();key();assert(S.removed==0 and has("CLEANUP_FAILED"))')

    def test_identity_reuse_rejected(self):
        self.run_case('key();call();S.label.addr=S.label.addr+1;key();assert(S.removed==0 and has("CLEANUP_FAILED"))')


if __name__ == '__main__':
    unittest.main()
