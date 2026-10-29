# SPDX-License-Identifier: MPL-2.0
"""Host-only state policy mocks. Not native loading/Create/Slate/GC acceptance."""
import unittest
from test_viewport import FIXTURE, BEFORE
from test_ui_child import LuaRuntime, ROOT
SOURCE=(ROOT/'research/interaction-prompts-owner/userwidget-host/probe/Scripts/main.lua').read_text(encoding='utf8')
EXTRA=r"""
Key.F6=6;EObjectFlags.RF_ClassDefaultObject=16;EObjectFlags.RF_ArchetypeObject=32
local HOST='/Game/MainContent/Template/UMG/Debug/PostionItemUMG_BP.PostionItemUMG_BP_C'
local parent={IsValid=function()return true end,GetFullName=function()return 'Class /Script/UMG.UserWidget'end}
local host_class=make('/Script/UMG.WidgetBlueprintGeneratedClass',HOST)
function host_class:type()return 'UClass'end
function host_class:GetSuperStruct()if S.bad_parent then return nil end return parent end
local old=make(HOST,'/Transient.ExistingHost');S.existing=old
function old:SetVisibility()error('EXISTING HOST MUTATION')end
local fnpath='/Script/UMG.WidgetBlueprintLibrary:Create'
local cdo=make('/Script/UMG.WidgetBlueprintLibrary','/Script/UMG.Default__WidgetBlueprintLibrary')
local function build_host()
 local w=make(HOST,'/Transient.OwnHost');S.own_host=w
 local tr=make('/Script/UMG.WidgetTree',w.p..'.WidgetTree',w)
 local ro=canvas_object(tr.p..'.CanvasPanel_0',tr)
 local ma=canvas_object(tr.p..'.Main_Panel',tr);ma.parent=ro
 local va=make('/Script/UMG.TextBlock',tr.p..'.Value_Text',tr);va.parent=ma;va.Font={Size=14,GetStructAddress=function()return 100 end}
 local im=make('/Script/UMG.Image',tr.p..'.Bg_Image',tr);im.parent=ma
 ro.children={ma};ma.children={im,va};tr.RootWidget=ro
 function ro:GetChildAt(i)return self.children[i+1]end
 function ma:GetChildAt(i)return self.children[i+1]end
 w.WidgetTree=S.alias_tree and hudtree or tr;w.Value_Text=va;w.Bg_Image=im
 for _,pair in ipairs({{ma,ro},{im,ma},{va,ma}})do
  local ch,pa=pair[1],pair[2];ch.Slot=make('/Script/UMG.CanvasPanelSlot',ch.p..'.Slot',pa);ch.Slot.Parent=pa;ch.Slot.Content=ch
 end
 function ma:SetVisibility(v)assert(v==1);self.Visibility=v end
 w.Visibility=4
 function w:HasAnyFlags(f)return S.cdo_return or false end
 function w:SetVisibility(v)self.Visibility=v end
 function w:SetDesiredSizeInViewport(v)self.size=v end
 function w:SetAnchorsInViewport(v)self.anchors=v end
 function w:SetAlignmentInViewport(v)self.alignment=v end
 function w:AddToViewport(z)
  assert(z==100);S.builds=(S.builds or 0)+1;self.attached=true;self.Visibility=S.no_construct and 4 or 2
  if S.add_fail then error('partial viewport attachment')end
 end
 function w:IsInViewport()return self.attached or false end
 function w:RemoveFromParent()
  S.removes=(S.removes or 0)+1;if S.release_pending then return end;self.attached=false
 end
 function w:GetParent()return nil end
 return w
end
local create={IsValid=function()return true end,type=function()return 'UFunction'end,
 GetFullName=function()return 'Function '..fnpath end}
setmetatable(create,{__call=function(_,caller,context,c,player)
 api();assert(caller==cdo and context==hud and c==host_class and player==nil);S.creates=(S.creates or 0)+1
 if S.old_return then return old end
 return build_host()
end})
local previous_find=StaticFindObject
function StaticFindObject(p)
 if p==HOST then if not S.loaded then return nil end return host_class end
 if p==fnpath then return create end
 if p==cdo.p then return cdo end
 return previous_find(p)
end
local previous_all=FindAllOf
function FindAllOf(n)
 if n=='PostionItemUMG_BP_C'then api();return {old}end
 return previous_all(n)
end
function LoadAsset(p)
 api();assert(p==HOST);S.loads=(S.loads or 0)+1
 if S.load_fail then return nil,false,false end
 S.loaded=true;return S.wrong_load and old or host_class,true,true
end
function StaticConstructObject(c,tr,name,flags)
 api();assert(c.p=='/Script/UMG.TextBlock' and flags==64)
 local o=make('/Script/UMG.TextBlock',tr.p..'.'..name:ToString(),tr);o.ours=true;S.label=o
 function o:SetVisibility(v)self.Visibility=v end
 function o:SetFont(v)local copy={};for k,x in pairs(v)do copy[k]=x end;copy.GetStructAddress=function()return 200 end;self.Font=copy end
 function o:SetJustification(v)assert(v==1)end
 function o:SetText(v)self.Text={ToString=function()return v end}end
 return o
end
function FName(s)return {ToString=function()return s end}end
function has_own_gone()return S.own_host and not S.own_host.attached and (not S.label or not S.label.parent)end
function foreign_same()return #root.children==2 and root==hudtree.RootWidget and S.existing.Visibility==nil end
"""

class UserWidgetHostPolicy(unittest.TestCase):
    def case(self,code,setup=''):
        l=LuaRuntime(unpack_returned_tuples=True)
        l.execute(FIXTURE+BEFORE+EXTRA);l.execute(setup);l.execute(SOURCE)
        try:l.execute(code)
        except Exception:
            print(list(l.globals().S.logs.values()));raise
        self.assertTrue(l.eval('original_ok() and foreign_same()'))

    def test_exact_load_create_hidden_show_cleanup_one_attempt(self):
        self.case('key();assert(S.loads==1 and S.creates==1 and has("CONSTRUCT_HIDDEN") and has("VISIBLE"));'
                  'key();assert(has_own_gone() and has("OWNERSHIP_RELEASED") and has("CLEANED"));'
                  'key();assert(S.loads==1 and S.creates==1)')

    def test_resident_class_skips_load(self):
        self.case('key();assert(not S.loads and S.creates==1 and has("VISIBLE"));key();assert(has_own_gone())','S.loaded=true')

    def test_bad_load_or_parent_refused_before_create(self):
        for setup in ['S.load_fail=true','S.wrong_load=true','S.bad_parent=true']:
            self.case('key();assert(has("FAILED") and not S.creates);key();assert((S.loads or 0)<=1)',setup)

    def test_existing_or_default_instance_never_mutated(self):
        for setup in ['S.old_return=true','S.cdo_return=true']:
            self.case('key();assert(has("FAILED") and not has("VISIBLE") and not S.removes)',setup)

    def test_foreign_tree_alias_fails_before_viewport_or_label(self):
        self.case('key();assert(has("FAILED") and not S.builds and not S.label and has_own_gone())','S.alias_tree=true')

    def test_unexpected_construct_or_partial_add_cleans_own(self):
        for setup in ['S.no_construct=true','S.add_fail=true']:
            self.case('key();assert(has("FAILED") and has_own_gone() and has("CLEANED"))',setup)

    def test_timeout_removes_without_any_further_user_input(self):
        self.case('key();timer();assert(has_own_gone() and has("reason=timeout"))')

    def test_cleanup_pending_keeps_identity_for_explicit_retry_only(self):
        self.case('key();S.release_pending=true;key();assert(has("CLEANUP_FAILED") and not S.label.parent);'
                  'S.release_pending=false;key();assert(has_own_gone() and S.creates==1 and S.loads==1)')

if __name__=='__main__':unittest.main()
