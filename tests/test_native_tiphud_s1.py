# SPDX-License-Identifier: MPL-2.0
"""S1 source/geometry + multi-TipHUD engine mock. Not a gameplay/Slate proof."""
import unittest
from pathlib import Path
from test_ui_child import FIXTURE, LuaRuntime, ROOT
from test_aphes_text import ADDITIONS

SRC=ROOT/"research/interaction-prompts-owner/native-tiphud-s1/Scripts"
MAIN=(SRC/"main.lua").read_text(encoding="utf-8")
LAYOUT=(SRC/"IIPS1Layout.lua").read_text(encoding="utf-8")

OVERRIDES=r'''
local base_require=require
function require(name)
 if name=="IIPS1Layout"then return IIPS1Layout end
 if name=="IIPS1Config"then return {
     filename=S.filename or "C:/local/Aphes.ttf",
     separator_filename="C:/local/aphes_divider_256x32.png"
 }end
 return base_require(name)
end
stock.Font.OutlineSettings={OutlineSize=2,OutlineColor={R=0,G=0,B=0,A=1}}
function stock:GetDesiredSize()return {X=S.bad_size and 0 or 130,Y=37.5}end
function original_slot:GetAutoSize()return true end
S.widgets={};S.captions={[1]="Открыть"};S.labels={};S.images={}
local function icon_for(t,c)
 local icon=make("/Script/UMG.RetainerBox",t.p..".RetainerBox_0",t)
 icon.parent=c
 icon.Slot={
   GetPosition=function()return {X=0,Y=0}end,
   GetAlignment=function()return {X=0,Y=0.5}end,
   GetAnchors=function()return {Minimum={X=0,Y=0.5},Maximum={X=0,Y=0.5}}end,
   GetAutoSize=function()return false end,
   GetSize=function()return {X=38,Y=38}end}
 return icon
end
icon_for(tree,canvas)
S.widgets[1]={w=w,tree=tree,canvas=canvas,stock=stock}
local function spawn(id,caption)
 local root=make(BASE,"/Transient.TipHUD"..id)
 local t=make("/Script/UMG.WidgetTree",root.p..".WidgetTree",root)
 local c=make("/Script/UMG.CanvasPanel",t.p..".CanvasPanel_6",t)
 local b=make("/Script/UMG.TextBlock",t.p..".TextBlock_89",t)
 b.parent=c;b.Visibility=0;b.RenderOpacity=1
 b.Font={Size=22,FontObject=donor,TypefaceFontName=str("Default"),
  OutlineSettings={OutlineSize=2,OutlineColor={R=0,G=0,B=0,A=1}},
  GetStructAddress=function()return 5500 end}
 b.Text={ToString=function()return S.captions[id]end}
 function b:GetDesiredSize()return {X=110,Y=37.5}end
 b.Slot={GetAutoSize=function()return true end,
  GetPosition=function()return {X=38,Y=0}end,
  GetAlignment=function()return {X=0,Y=0.5}end,
  GetAnchors=function()return {Minimum={X=0,Y=0.5},Maximum={X=0,Y=0.5}}end}
 setmetatable(b,{__index=function(_,key)
   if key:match("^Set")then return function()error("ORIGINAL MUTATION")end end end})
 root.Visibility=0;root.RenderOpacity=1;root.bIsEnabled=true
 root.WidgetTree=t;root.TextBlock_89=b
 icon_for(t,c)
 S.widgets[id]={w=root,tree=t,canvas=c,stock=b}
 S.captions[id]=caption
 return root
end
spawn(2,"Подобрать")
local function canvas_methods(c)
 function c:AddChildToCanvas(item)
   item.parent=c;S.attached=S.attached+1
   local slot=make("/Script/UMG.CanvasPanelSlot",c.p..".OwnSlot"..S.attached,c)
   slot.Parent=c;slot.Content=item
   for _,key in ipairs({"SetAutoSize","SetAnchors","SetAlignment","SetPosition","SetSize"})do
     slot[key]=function(_,v)
       if key=="SetSize"then assert(v.X>0 and v.Y>0)end
       if S.fail_slot then error("slot fault")end
     end
   end
   return slot
 end
 function c:RemoveChild(item)
   if S.fail_remove then return false end
   assert(item.parent==c);item.parent=nil;S.removed=S.removed+1
   return true
 end
end
canvas_methods(canvas);canvas_methods(S.widgets[2].canvas)
local old_find=StaticFindObject
function StaticFindObject(p)
 if p=="/Script/Engine.Default__KismetRenderingLibrary"then
   return S.cdo
 end
 if p=="/Script/Engine.KismetRenderingLibrary:ImportFileAsTexture2D"then
   return S.import_fn
 end
 if p=="/Script/UMG.Image:SetBrushFromTexture" or p=="/Script/UMG.Image:SetBrushResourceObject"then
   return {IsValid=function()return true end,type=function()return "UFunction"end,
     GetFullName=function()return "Function "..p end}
 end
 return old_find(p)
end
S.cdo=make("/Script/Engine.KismetRenderingLibrary","/Script/Engine.Default__KismetRenderingLibrary")
S.import_fn=setmetatable({
   IsValid=function()return true end,type=function()return "UFunction"end,
   GetFullName=function()return "Function /Script/Engine.KismetRenderingLibrary:ImportFileAsTexture2D"end},
 {__call=function(_,cdo,context,p)
   assert(cdo==S.cdo and context~=nil and p:match("%.png$"))
   if S.fail_import then error("import fault")end
   S.imports=(S.imports or 0)+1
   local tx=make("/Script/Engine.Texture2D","/Transient.S1Texture"..S.imports)
   function tx:HasAnyFlags(f)return f==64 end
   function tx:Blueprint_GetSizeX()return 256 end
   function tx:Blueprint_GetSizeY()return 32 end
   return tx
 end})
local old_open=io.open
io.open=function(p,mode)
 if p:match("%.png$")then
   assert(mode=="rb")
   local header="\137PNG\r\n\26\n"..string.pack(">I4",13).."IHDR"
       ..string.pack(">I4I4",256,32)..string.char(8,6,0,0,0).."CRC!"
   return {seek=function(_,mode)if mode=="end"then return 2000 end return 0 end,
           read=function()return header end,close=function()end}
 end
 return old_open(p,mode)
end
local old_construct=StaticConstructObject
function StaticConstructObject(c,t,name,flags,...)
 local n=name:ToString()
 if c.p=="/Script/Engine.Font"then
   S.copies=(S.copies or 0)+1
   local o=font(t.p.."."..n,t,true)
   return o
 end
 if c.p=="/Script/UMG.TextBlock" or c.p=="/Script/UMG.Image"then
   assert(flags==64)
   local o=make(c.p,t.p.."."..n,t)
   function o:SetVisibility(v)self.Visibility=v end
   if c.p=="/Script/UMG.TextBlock"then
     S.labels[#S.labels+1]=o
     function o:SetFont(v)
       if S.fail_font_release and v==S.widgets[1].stock.Font then error("font release")end
       local copy={};for k,x in pairs(v)do copy[k]=x end
       local s=v.OutlineSettings or {OutlineSize=0,OutlineColor={}}
       copy.OutlineSettings={OutlineSize=s.OutlineSize,OutlineColor=s.OutlineColor}
       copy.GetStructAddress=function()return 6500 end
       self.Font=copy
     end
     function o:SetText(v)self.Text=str(v)end
     function o:SetColorAndOpacity(v)self.ColorAndOpacity=v end
     function o:SetJustification(v)assert(v==1)end
   else
     S.images[#S.images+1]=o
     o.Brush={DrawAs=3,ResourceObject=nil,ResourceName=str("None"),
         TintColor={SpecifiedColor={A=1},ColorUseRule=0}}
     function o:SetColorAndOpacity(v)self.ColorAndOpacity=v end
     function o:SetBrushFromTexture(t)self.Brush.ResourceObject=t end
     function o:SetBrushResourceObject(t)self.Brush.ResourceObject=t end
   end
   return o
 end
 return old_construct(c,t,name,flags,...)
end
-- New entrypoint only: post CanShow and map lifecycle.
function RegisterLoadMapPreHook(fn)S.map=fn end
function trigger(id)
 S.game=true
 local r=S.hook({get=function()return S.widgets[id].w end})
 S.game=false
 assert(r==nil)
end
function travel()
 S.game=true;S.map();S.game=false
end
function stop_s1()
 S.key();S.game=true
 for _,fn in ipairs(S.queue)do fn()end
 S.queue={}
 S.game=false
end
function original_safe()
 return original_ok() and S.widgets[2].stock.Font.Size==22
   and S.widgets[2].stock.parent==S.widgets[2].canvas
end
'''
class S1Tests(unittest.TestCase):
    def vm(self, code="", pre=""):
        vm=LuaRuntime(unpack_returned_tuples=True)
        layout=vm.execute(LAYOUT)
        vm.globals().IIPS1Layout=layout
        vm.execute(FIXTURE+ADDITIONS+OVERRIDES+pre)
        vm.globals().S.game=True
        vm.execute(MAIN)
        vm.globals().S.game=False
        vm.execute(code)
        self.assertTrue(vm.eval("original_safe()"))
        return vm

    def test_layout_follows_text_column_not_key_and_keeps_png_aspect(self):
        vm=LuaRuntime(unpack_returned_tuples=True)
        m=vm.execute(LAYOUT)
        result=m.plan(vm.eval("""{
          desired={X=130,Y=37.5},position={X=38,Y=0},
          alignment={X=0,Y=0.5},anchors={Minimum={X=0,Y=0.5},Maximum={X=0,Y=0.5}},
          native_size=22,icon_position={X=0,Y=0},icon_alignment={X=0,Y=0.5},
          icon_anchors={Minimum={X=0,Y=0.5},Maximum={X=0,Y=0.5}},
          icon_auto=false,icon_size={X=38,Y=38}}"""))
        self.assertAlmostEqual(result["upper"]["x"],103)
        self.assertAlmostEqual(result["divider"]["x"],103)
        self.assertAlmostEqual(result["divider"]["height"],result["divider"]["width"]/8)
        self.assertLess(result["upper"]["y"],result["divider"]["y"])
        self.assertLess(result["divider"]["y"],-18.75)

    def test_multi_instance_reuse_without_original_writes(self):
        self.vm('trigger(1);trigger(1);trigger(2);trigger(1);'
                'assert(#S.labels==2 and #S.images==2);'
                'assert(S.copies==1 and S.imports==1);'
                'assert(S.labels[1].Text:ToString()=="ACTION");'
                'S.captions[2]="Взять";trigger(2);'
                'assert(#S.labels==2 and S.captions[2]=="Взять");'
                'assert(has("ATTACHED"))')

    def test_map_pre_releases_each_and_can_reenter(self):
        self.vm('trigger(1);trigger(2);travel();'
                'assert(S.removed==4 and not S.images[1].parent and not S.labels[2].parent);'
                'trigger(1);assert(#S.labels==3 and S.copies==2 and S.imports==2);'
                'stop_s1();assert(S.removed==6 and has("CLEANED"))')

    def test_unsupported_state_is_stock_only(self):
        self.vm('S.bad_size=true;trigger(1);'
                'assert(#S.labels==0);'
                'S.bad_size=false;S.widgets[2].w.bIsEnabled=false;trigger(2);'
                'assert(#S.labels==0);'
                'trigger(1);assert(#S.labels==1);stop_s1();'
                'assert(not S.labels[1].parent)')

    def test_partial_import_fault_detaches_own_label(self):
        self.vm('S.fail_import=true;trigger(1);'
                'assert(#S.labels==1 and not S.labels[1].parent);'
                'assert(#S.images==1 and not S.images[1].parent);'
                'assert(not has("ATTACHED") and has("ATTACH_FAILED"))')

    def test_user_stop_does_not_change_native_action_or_button(self):
        self.vm('trigger(1);trigger(2);stop_s1();'
                'assert(S.removed==4);trigger(1);'
                'assert(#S.labels==2 and not S.labels[1].parent)')

    def test_static_native_ownership_boundary(self):
        for forbidden in ("TextBlock_89:SetText", "TextBlock_89:SetFont",
                          "TextBlock_89:SetRenderTranslation",
                          "RetainerBox_0:Set", "SetWidgetSpace",
                          "GetNowInputControllerType", "LoopInGameThreadAfterFrames"):
            self.assertNotIn(forbidden,MAIN)
        self.assertIn('RegisterHook(HOOK,observe)',MAIN)
        self.assertIn('RegisterLoadMapPreHook(map_pre)',MAIN)
        self.assertIn('label:SetText(FText("ACTION"))',MAIN)

if __name__=="__main__":
    unittest.main()
