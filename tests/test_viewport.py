# SPDX-License-Identifier: MPL-2.0
"""Screen-position policy mocks, not native HUD layout/render/GC evidence."""
import unittest
from test_ui_child import FIXTURE, LuaRuntime, ROOT
from test_composition import FONT, PNG

BASE=ROOT/'research/interaction-prompts-owner/viewport/Scripts'
SOURCE=(BASE/'main.lua').read_text(encoding='utf8')
POSITION=(BASE/'IIPPosition.lua').read_text(encoding='utf8')
FIXTURE=FIXTURE.replace('{GetFullName=function()return "Class "..self.kind end}',
    '{GetFullName=function()return "Class "..self.kind end,IsValid=function()return true end,GetSuperStruct=function()return nil end}')
BEFORE=r"""
function identity()return {Translation={X=0,Y=0},Scale={X=1,Y=1},Shear={X=0,Y=0},Angle=0}end
local HUD="/Game/MainContent/Template/UMG/HUD/HUDMainUMG_BP.HUDMainUMG_BP_C"
local hud=make(HUD,"/Transient.GameHUD")
local hudtree=make("/Script/UMG.WidgetTree",hud.p..".WidgetTree",hud)
local function canvas_object(p,outer)
 local c=make("/Script/UMG.CanvasPanel",p,outer);c.children={};c.RenderTransform=identity()
 function c:GetChildrenCount()return #self.children end
 function c:AddChildToCanvas(o)
  api();assert(o.ours,"foreign child attached");table.insert(self.children,o);o.parent=self
  if S.attach_failure then error("attach error after parenting")end
  local sl=make("/Script/UMG.CanvasPanelSlot",self.p..".Slot"..#self.children,self)
  sl.Parent=self;sl.Content=o;sl.anchors={}
  function sl:SetAutoSize(v)assert(v==false)end
  function sl:SetAnchors(v)
   local function f(x)return string.unpack('f',string.pack('f',x))end
   self.anchors={Minimum={X=f(v.Minimum.X),Y=f(v.Minimum.Y)},Maximum={X=f(v.Maximum.X),Y=f(v.Maximum.Y)}}
  end
  function sl:GetAnchors()return self.anchors end
  function sl:SetAlignment(v)self.alignment=v end
  function sl:SetPosition(v)assert(v.X==0 or c~=root);self.position=v end
  function sl:SetSize(v)self.size=v end
  function sl:SetZOrder(v)self.z=v end
  o.Slot=sl;return sl
 end
 function c:RemoveChild(o)
  api();assert(o.ours,"FOREIGN REMOVAL")
  if S.remove_failure then return false end
  for i,x in ipairs(self.children)do if x==o then table.remove(self.children,i);o.parent=nil;return true end end
  return false
 end
 return c
end
local root=canvas_object(hudtree.p..".Main_Panel",hudtree)
root.children={{stock=true},{stock=true}};S.host=root
hudtree.RootWidget=root;hud.WidgetTree=hudtree
hud.RenderTransform=identity();hud.Visibility=4;hud.RenderOpacity=1
function hud:IsInViewport()return not S.hud_gone end
local pawn=make("/Script/Genesis.GenesisCharacter","/Transient.Hilda")
function hud:GetOwningPlayerPawn()return pawn end
function hud:GetAnchorsInViewport()return {Minimum={X=0,Y=0},Maximum={X=S.bad_hud and 0 or 1,Y=1}}end
function hud:GetAlignmentInViewport()return {X=0,Y=0}end
function FindAllOf(n)api();assert(n=="HUDMainUMG_BP_C");S.lookups=(S.lookups or 0)+1
 if S.duplicate then return {hud,hud}end
 return {hud}
end
function stock:GetDesiredSize()return {X=127.75,Y=37.5}end
local retainer=make("/Script/UMG.RetainerBox",tree.p..".RetainerBox_0",tree);retainer.parent=canvas
local src_hint=make("/Script/UMG.Image",tree.p..".ImageInteractAllowed",tree);src_hint.parent=retainer
src_hint.Brush={ResourceObject=make("/Script/Engine.MaterialInstanceDynamic","/Transient.HintMID"),DrawAs=3}
src_hint.ColorAndOpacity={R=1,G=1,B=1,A=1}
function retainer:GetChildAt(i)assert(i==0);return src_hint end
local old_find=StaticFindObject
function StaticFindObject(p)
 if p=="/Script/UMG.CanvasPanel"then return {p=p,IsValid=function()return true end,type=function()return 'UClass'end}end
 if p=="/Script/UMG.WidgetLayoutLibrary:GetViewportSize"then
  return setmetatable({IsValid=function()return true end,type=function()return 'UFunction'end,
   GetFullName=function()return 'Function '..p end}, {__call=function(_,c,h)
   assert(c.kind=='/Script/UMG.WidgetLayoutLibrary' and h==hud);return {X=2560,Y=1440}end})
 end
 if p=="/Script/UMG.Default__WidgetLayoutLibrary"then return make("/Script/UMG.WidgetLayoutLibrary",p)end
 return old_find(p)
end
function StaticConstructObject(c,outer,n,flags)
 api();assert(outer==hudtree and flags==64);S.created=S.created+1
 local o
 if c.p=="/Script/UMG.CanvasPanel"then o=canvas_object(outer.p..'.'..n,outer);S.own_canvas=o
 else o=make(c.p,outer.p..'.'..n,outer)end
 o.ours=true;o.Font={};o.RenderTransform=identity()
 function o:SetVisibility(v)self.Visibility=v end
 function o:SetFont(v)self.Font=v end
 function o:SetText(v)self.text=v end
 function o:SetJustification(v)assert(v==1)end
 function o:SetColorAndOpacity(v)self.color=v end
 function o:SetShadowOffset(v)self.shadow=v end
 function o:SetShadowColorAndOpacity(v)self.shadow_color=v end
 o.Brush={DrawAs=3,ResourceName={ToString=function()return 'None'end},TintColor={}}
 function o:SetBrush(v)
  local copy={};for k,x in pairs(v)do copy[k]=x end;self.Brush=copy
 end
 function o:SetBrushResourceObject(v)assert(v==nil);self.Brush.ResourceObject=nil end
 if n:find('_Lower',1,true)then S.lower=o end
 if n:find('_Upper',1,true)then S.upper=o end
 if n:find('_Coords',1,true)then S.coords=o end
 return o
end
"""
AFTER=r"""
local prev_require=require
Key.LEFT_ARROW=37;Key.RIGHT_ARROW=39;Key.UP_ARROW=38;Key.DOWN_ARROW=40;Key.HOME=36;Key.F7=7
S.keys={}
function RegisterKeyBind(key,mods,fn)S.keys[key]=fn end
function IsKeyBindRegistered(key)return S.collision and key==Key.DOWN_ARROW end
function require(n)
 if n=='IIPPosition'then return S.position_module end
 assert(n=='IIPViewportConfig');local c=prev_require('IIPAphesConfig');c.separator_filename='C:/local/OPEN.png';return c
end
local old_open=io.open
io.open=function(p,m)
 if p~='C:/local/OPEN.png'then return old_open(p,m)end
 local h='\137PNG\r\n\26\n'..string.pack('>I4',13)..'IHDR'..string.pack('>I4I4',570,16)..string.char(8,6,0,0,0)..'CRC!'
 return {seek=function(_,mode)if mode=='end'then return 4948 end return 0 end,read=function()return h end,close=function()S.file_closed=true end}
end
function press(k)
 local fn=assert(S.keys[k]);fn();S.game=true;for _,f in ipairs(S.queue)do f()end;S.queue={};S.game=false
end
function detached()return S.own_canvas and not S.own_canvas.parent and #S.host.children==2 end
"""
# PNG importer fixture expects the original TipHUD world. Here world is the selected HUD.
PNG=PNG.replace('world==w','world==hud')
# Avoid the glyph-change-only expectations of the previous text fixture on new lower/indicator text.
FONT=FONT.replace('assert(v=="OPEN" or v=="READ");self.Text=str(v);S.word=v', 'self.Text=str(v);S.word=v;self.text=v')
# Keep native font copies independent, including typed outline settings, and support partial release fault injection.
FONT=FONT.replace('copy.OutlineSettings={OutlineSize=2}',
    'copy.OutlineSettings={OutlineSize=v.OutlineSettings and v.OutlineSettings.OutlineSize or 2}')
FONT=FONT.replace('if v==stock.Font and S.restore_fail and S.font_created then', 'if S.restore_fail and self==S.upper and S.font_created then')

class ViewportPolicy(unittest.TestCase):
    def case(self,code,setup=''):
        lua=LuaRuntime(unpack_returned_tuples=True)
        lua.execute(FIXTURE+BEFORE+FONT+PNG+AFTER)
        lua.globals().S.position_module=lua.execute(POSITION)
        lua.execute(setup);lua.execute(SOURCE)
        try:lua.execute(code)
        except Exception:
            print(list(lua.globals().S.logs.values()));raise
        self.assertTrue(lua.eval('original_ok() and donor_ok()'))
        return lua

    def test_create_style_move_commit_reset_cleanup_once(self):
        self.case('press(6);call();assert(has("ATTACHED") and S.imports==1 and S.lookups==1);'
          'assert(S.upper.Font.Size==28 and S.upper.Font.LetterSpacing==150 and S.upper.Font.OutlineSettings.OutlineSize==0);'
          'press(39);press(38);assert(S.coords.text=="TEST  X=51%  Y=77%");press(7);assert(has("action=commit x_percent=51 y_percent=77"));'
          'press(36);assert(S.coords.text=="TEST  X=50%  Y=78%");press(6);assert(detached() and has("CLEANED"));'
          'press(6);assert(S.imports==1 and S.lookups==1)')

    def test_position_is_independent_after_snapshot(self):
        self.case('press(6);call();local n=S.created;S.text="Другое";for i=1,20 do call()end;'
                  'press(39);assert(S.created==n and S.lookups==1 and not detached());press(6);assert(detached())')

    def test_reject_ambiguous_or_transformed_host_without_creation(self):
        for setup in ['S.bad_hud=true','S.duplicate=true']:
            self.case('press(6);call();assert(S.created==0 and has("FAILED") and #S.host.children==2)',setup)

    def test_import_failure_cleans_canvas_without_original_writes(self):
        self.case('press(6);call();assert(has("FAILED") and detached() and not has("ATTACHED"));press(6);assert(S.imports==1)',
                  'S.import_null=true')

    def test_attachment_partial_failure_removes_owned_only(self):
        self.case('press(6);call();assert(has("FAILED") and detached())','S.attach_failure=true')

    def test_timeout_and_viewport_loss(self):
        self.case('press(6);call();timer();assert(detached() and has("reason=timeout"))')
        self.case('press(6);call();S.hud_gone=true;press(39);assert(has("FAILED") and detached())')

    def test_cleanup_retry_keeps_carrier_and_no_new_import(self):
        self.case('press(6);call();S.restore_fail=true;press(6);assert(has("CLEANUP_FAILED") and S.lower.parent==S.own_canvas);'
                  'S.restore_fail=false;press(6);assert(detached() and S.imports==1)')

    def test_bounds_and_key_preflight(self):
        self.case('press(6);call();for i=1,100 do press(37);press(40)end;'
                  'assert(S.coords.text=="TEST  X=10%  Y=90%");press(6);assert(detached())')
        self.case('assert(has("UNAVAILABLE") and next(S.keys)==nil)','S.collision=true')

if __name__=='__main__':unittest.main()
