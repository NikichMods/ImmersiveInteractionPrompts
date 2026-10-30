# SPDX-License-Identifier: MPL-2.0
"""Borrowed hint policy and integration mock; no pixel/device acceptance."""
import unittest
from test_beginplay_join import FIXTURE
from test_world_child import EXTRA
from test_world_deferred import CONTEXT
from test_world_orientation import ORIENTATION
from test_vertical_yaw import FRAMES
from test_ui_child import LuaRuntime, ROOT

DIR=ROOT/'research/interaction-prompts-owner/world-space/hint-mirror/Scripts'
MAIN=(DIR/'main.lua').read_text(encoding='utf8')
WORLD=(DIR/'IIPWorldChild.lua').read_text(encoding='utf8')
HINT=(DIR/'IIPHintSource.lua').read_text(encoding='utf8')
HINT_FIXTURE=r'''
S.device=1;S.cvar=1;S.hint_size={X=38,Y=38};S.mat_sets=0;S.brush_sets=0
local function meta(p,fn)
 local f=make(p,'Function');set(f,'type',function()return 'UFunction'end)
 if fn then setmetatable(f,{__index=S.fields[f],__call=function(_,cdo,...)assert(S.game);return fn(...)end})end
 return f
end
for _,p in ipairs({'/Script/UMG.RetainerBox:GetEffectMaterial','/Script/UMG.Image:SetBrushFromMaterial',
 '/Script/UMG.Image:SetBrush','/Script/UMG.Image:SetBrushResourceObject',
 '/Script/Engine.MaterialInstanceDynamic:K2_GetTextureParameterValue','/Script/UMG.Widget:GetOwningPlayer',
 '/Script/Genesis.GenesisPlayerController:GetNowInputControllerType'})do meta(p)end
meta('/Script/Engine.KismetSystemLibrary:GetConsoleVariableIntValue',function(n)
 assert(n=='Slate.EnableRetainedRendering');return S.cvar
end)
local function visible(o)o.Visibility=0;o.RenderOpacity=1;o.bIsEnabled=true;return o end
local tree=P.widget.WidgetTree
S.source_root=visible(owned(tree.p..'.CanvasPanel_6','/Script/UMG.CanvasPanel',tree))
set(tree,'RootWidget',S.source_root)
S.retainer=visible(owned(tree.p..'.RetainerBox_0','/Script/UMG.RetainerBox',tree));S.retainer.parent=S.source_root
local r=S.retainer;r.bRetainRender=true;r.Phase=0;r.PhaseCount=1;r.RenderOnPhase=true;r.RenderOnInvalidation=false
r.TextureParameter={ToString=function()return 'Icon'end}
r.Slot=owned(r.p..'.Slot','/Script/UMG.CanvasPanelSlot',S.source_root)
r.Slot.Parent=S.source_root;r.Slot.Content=r;r.Slot.GetSize=function()return S.hint_size end
S.source_image=visible(owned(r.p..'.Image','/Script/UMG.Image',tree));S.source_image.parent=r
r.GetChildrenCount=function()return S.child_count or 1 end;r.GetChildAt=function()return S.source_image end
S.source_image.bFlipForRightToLeftFlowDirection=false
S.source_image.RenderTransform={Translation={X=0,Y=0},Scale={X=1,Y=1},Shear={X=0,Y=0},Angle=0}
S.source_image.ColorAndOpacity={R=1,G=1,B=1,A=1}
S.raw=owned('/Hint.RawTexture','/Script/Engine.Texture2D')
S.source_image.Brush={ResourceObject=S.raw,DrawAs=3,ImageSize={X=38,Y=38},TintColor={ColorUseRule=0},UV=0,GetStructAddress=function()return 600 end}
S.effect_base=owned('/Game/MainContent/Template/UMG/TipIconMat.TipIconMat','/Script/Engine.Material')
S.effect_base.MaterialDomain=5;S.effect_base.BlendMode=2
function new_icon(p)
 local t=owned(p,'/Script/Engine.TextureRenderTarget2D');t.SizeX=38;t.SizeY=38;t.bForceLinearGamma=false;t.RenderTargetFormat=0;return t
end
S.icon=new_icon('/Hint.IconRT')
function new_mid(p)
 local m=owned(p,'/Script/Engine.MaterialInstanceDynamic');m.Parent=S.effect_base
 m.K2_GetTextureParameterValue=function(_,name)assert(name=='Icon');return S.icon end
 m.SetTextureParameterValue=function()error('SOURCE TEXTURE WRITE')end
 m.SetScalarParameterValue=function()error('SOURCE SCALAR WRITE')end
 return m
end
S.hint_mid=new_mid('/Hint.EffectMID');r.GetEffectMaterial=function()return S.hint_mid end
S.pc=make('/Player.PC','/Script/Genesis.GenesisPlayerController')
set(S.pc,'GetNowInputControllerType',function()return S.device end)
set(P.widget,'GetOwningPlayer',function()return S.pc end)
local image_class=make('/Script/UMG.Image','Class');set(image_class,'type',function()return 'UClass'end)
local construct=StaticConstructObject
function StaticConstructObject(k,outer,name,...)
 if k==image_class then
  local o=owned(outer.p..'.'..name,'/Script/UMG.Image',outer);S.label=o;S.hint=o
  o.Brush={DrawAs=3,GetStructAddress=function()return 700 end}
  o.SetBrushResourceObject=function(_,v)if S.release_fail and v==nil then error('own release failure')end;o.Brush.ResourceObject=v end
  o.SetBrushFromMaterial=function(_,m)S.mat_sets=S.mat_sets+1;o.Brush.ResourceObject=m end
  o.SetBrush=function(_,b)
   S.brush_sets=S.brush_sets+1
   local v={};for k,x in pairs(b)do v[k]=x end;v.GetStructAddress=function()return 700 end;o.Brush=v
  end
  o.SetColorAndOpacity=function(_,v)o.color=v end
  return o
 end
 return construct(k,outer,name,...)
end
set(P.actor,'FinishAddComponent',function(_,c,manual,t)
 assert(c==S.comp and manual and not c.registered and c.space==0 and c.collision==0 and not c.overlaps)
 assert(c.draw.X==512 and c.draw.Y==128 and c.mat==S.stock and c.widget==S.host and S.host.Visibility==3)
 assert(S.hint and S.hint.Visibility==1 and S.hint.Text==nil)
 assert(t.position.Z==62 and t.scale.X==0.25);c.transform=t;c.registered=true
end)
function settle()for i=1,3 do yawframe()end end
'''

class HintMirrorPolicy(unittest.TestCase):
    def case(self,code,setup=''):
        lua=LuaRuntime(unpack_returned_tuples=True)
        lua.execute(FIXTURE+EXTRA+CONTEXT+ORIENTATION+FRAMES+HINT_FIXTURE)
        lua.execute('package.preload["IIPHintSource"]=function()\n'+HINT+'\nend')
        lua.execute('package.preload["IIPWorldChild"]=function()\n'+WORLD+'\nend')
        lua.execute(setup);lua.execute(MAIN)
        try:lua.execute(code)
        except Exception:
            print(list(lua.globals().S.logs.values())[-8:]);raise

    def test_retained_mid_read_only_binding_and_manual_cleanup(self):
        self.case('start();assert(S.hint.Visibility==1);settle();assert(S.hint.Brush.ResourceObject==S.hint_mid '
                  'and S.hint.Visibility==3 and S.mat_sets==1);yawframe();assert(S.mat_sets==1);'
                  'key(7);yawframe();assert(has("LOOP_CANCELLED") and has("RELEASED") and has("CLEANED") '
                  'and S.hint.Brush.ResourceObject==nil and S.icon.SizeX==38)')

    def test_inactive_retainer_copies_full_child_brush_and_refreshes_content(self):
        self.case('start();settle();assert(S.hint.Brush.ResourceObject==S.raw and S.mat_sets==0);'
                  'S.source_image.Brush.UV=0.5;yawframe();assert(S.hint.Brush.UV==0.5 and S.brush_sets>=2)',
                  'S.retainer.bRetainRender=false')

    def test_device_change_hides_releases_then_rebinds_automatically(self):
        self.case('start();settle();S.device=4;yawframe();assert(S.hint.Visibility==1 and S.hint.Brush.ResourceObject==nil);'
                  'settle();assert(S.hint.Visibility==3 and has("device=4"));S.device=1;settle();'
                  'assert(S.mat_sets==3 and has("sources=3")==false);key(7);assert(has("sources=3"))')

    def test_mid_replacement_refreshes_borrowed_reference(self):
        self.case('start();settle();local old=S.hint_mid;S.hint_mid=new_mid("/Hint.NewMID");settle();'
                  'assert(S.hint.Brush.ResourceObject==S.hint_mid and S.hint_mid~=old)')

    def test_icon_rt_replacement_rebinds_without_writing_texture(self):
        self.case('start();settle();S.icon=new_icon("/Hint.NewRT");settle();assert(S.mat_sets==2 and has("/Hint.NewRT"))')

    def test_inactive_to_active_transition_is_bounded(self):
        self.case('start();settle();S.retainer.bRetainRender=true;settle();assert(S.hint.Brush.ResourceObject==S.hint_mid)',
                  'S.retainer.bRetainRender=false')

    def test_active_without_texture_refuses_before_component_allocation(self):
        self.case('start();assert(not S.comp and has("Icon final render target not ready"))','S.icon=nil')

    def test_active_without_mid_has_no_brush_fallback(self):
        self.case('start();assert(not S.comp and has("MID not ready"))','S.hint_mid=nil')

    def test_texture_disappears_after_bind_stops_and_cleans(self):
        self.case('start();settle();S.icon=nil;yawframe();assert(has("FAILED") and has("CLEANED") and S.loop==nil)')

    def test_source_material_domain_mismatch_refuses(self):
        self.case('start();assert(not S.comp and has("unsupported native hint material"))','S.effect_base.MaterialDomain=0')

    def test_child_shape_mismatch_refuses(self):
        self.case('start();assert(not S.comp and has("child count"))','S.child_count=2')

    def test_render_schedule_and_parameter_refuse(self):
        self.case('start();assert(not S.comp and has("render schedule/parameter"))','S.retainer.PhaseCount=2')
        self.case('start();assert(not S.comp and has("render schedule/parameter"))',
                  'S.retainer.TextureParameter={ToString=function()return "Texture"end}')

    def test_global_zero_is_not_assumed_safe_inactive_mode(self):
        self.case('key();assert(not S.comp and has("global retainer cvar"))','S.cvar=0')

    def test_global_change_after_binding_stops(self):
        self.case('start();settle();S.cvar=0;yawframe();assert(has("global retainer mode") and has("CLEANED"))')

    def test_unknown_device_fails_closed(self):
        self.case('start();assert(not S.comp and has("unknown/default input device"))','S.device=0')

    def test_source_pending_kill_stops(self):
        self.case('start();settle();S.hint_mid.pending=true;yawframe();assert(has("CLEANED") and S.loop==nil)')

    def test_source_visibility_loss_never_leaves_old_symbol(self):
        self.case('start();settle();S.retainer.Visibility=2;yawframe();assert(has("CLEANED") and S.hint.Brush.ResourceObject==nil)')

    def test_oversize_hint_refuses_without_resizing_world_target(self):
        self.case('start();assert(not S.comp and has("unsupported hint dimensions"))','S.hint_size={X=97,Y=38}')

    def test_unsupported_raw_material_is_not_guessed(self):
        self.case('start();assert(not S.comp and has("inactive-retainer brush"))',
                  'S.retainer.bRetainRender=false;S.source_image.Brush.ResourceObject=S.hint_mid')

    def test_source_change_budget_stops_churn(self):
        self.case('start();settle();for i=1,7 do S.device=i%2+1;settle()end;S.device=1;yawframe(true);'
                  'assert(S.hint.Visibility==1 and S.hint.Brush.ResourceObject==nil);flush();'
                  'assert(has("source-change budget") and has("CLEANED"))')

    def test_timeout_and_late_callback_inertness(self):
        self.case('start();settle();local late=S.loop.fn;timeout(45000);flush();'
                  'local before=S.sets;S.game=true;late();S.game=false;assert(S.sets==before and has("CLEANED"))')

    def test_resource_clear_failure_is_explicit_and_retryable(self):
        self.case('start();settle();S.release_fail=true;key(7);assert(has("CLEANUP_PENDING"));'
                  'S.release_fail=false;key(7);assert(has("RELEASED") and has("CLEANED"))')

    def test_missing_reflected_hint_api_refuses_before_allocation(self):
        self.case('key();assert(not S.comp and has("hint API unavailable"))',
                  'set(S.objects["/Script/Engine.MaterialInstanceDynamic:K2_GetTextureParameterValue"],"live",false)')

    def test_detached_own_image_still_releases_only_its_resource(self):
        self.case('start();settle();S.hint.parent=nil;key(7);assert(has("CLEANED") '
                  'and S.hint.Brush.ResourceObject==nil and S.hint_mid.Parent==S.effect_base)')

    def test_source_mutators_are_absent(self):
        for forbidden in ('SetTextureParameterValue(', 'SetScalarParameterValue(', 'GetDynamicMaterial(',
                          'SetEffectMaterial(', 'SetRetainRendering(', 'RequestRender('):
            self.assertNotIn(forbidden,HINT)

if __name__=='__main__':unittest.main()
