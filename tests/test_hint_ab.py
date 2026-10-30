# SPDX-License-Identifier: MPL-2.0
"""Owned material comparison/projection policy. No engine/pixel acceptance."""
import unittest
from test_ui_child import LuaRuntime, ROOT
from test_beginplay_join import FIXTURE
from test_world_child import EXTRA
from test_world_deferred import CONTEXT
from test_world_orientation import ORIENTATION
from test_vertical_yaw import FRAMES
from test_hint_mirror import HINT_FIXTURE

DIR = ROOT/'research/interaction-prompts-owner/world-space/hint-mirror/ab/Scripts'
SOURCES = {p.stem: p.read_text(encoding='utf8') for p in DIR.glob('*.lua')}
AB_FIXTURE = r'''
S.effect_base.BlendMode=5;S.view_width=1920;S.view_height=1080;S.projected={};S.output_sets=0
S.camera_rotation={Pitch=0,Yaw=180,Roll=0};S.fov=90;S.rendered=true
TRANS='/Engine/EngineMaterials/Widget3DPassThrough_Translucent.Widget3DPassThrough_Translucent'
S.trans=owned(TRANS,'/Script/Engine.MaterialInstanceConstant');S.trans.Parent=S.base
S.trans.BasePropertyOverrides={bOverride_BlendMode=true,BlendMode=2,bOverride_TwoSided=true,TwoSided=true}
for _,p in ipairs({'/Script/Engine.PrimitiveComponent:SetMaterial','/Script/Engine.PrimitiveComponent:GetMaterial',
 '/Script/Engine.PlayerController:ProjectWorldLocationToScreen','/Script/Engine.PlayerController:GetViewportSize',
 '/Script/Engine.PlayerCameraManager:GetCameraRotation','/Script/Engine.PlayerCameraManager:GetFOVAngle',
 '/Script/Engine.MaterialInstanceDynamic:K2_GetVectorParameterValue','/Script/Engine.MaterialInstanceDynamic:K2_GetScalarParameterValue',
 '/Script/UMG.CanvasPanelSlot:GetAnchors','/Script/UMG.CanvasPanelSlot:GetAlignment',
 '/Script/UMG.CanvasPanelSlot:GetPosition','/Script/UMG.CanvasPanelSlot:GetAutoSize','/Script/UMG.WidgetComponent:GetPivot'})do
 local f=make(p,'Function');set(f,'type',function()return 'UFunction'end)
end
set(S.pc,'GetViewportSize',function(_,x,y)x.SizeX=S.view_width;y.SizeY=S.view_height end)
set(S.pc,'ProjectWorldLocationToScreen',function(_,point,out,relative)
 assert(S.game and relative==false);S.projected[#S.projected+1]=point
 if S.project_fail then return false end
 out.X=960+(point.Y-20)*10;out.Y=540-(point.Z-62)*10;return true
end)
set(S.objects['/World.Camera'],'GetCameraRotation',function()return S.camera_rotation end)
set(S.objects['/World.Camera'],'GetFOVAngle',function()return S.fov end)
local function white()return {R=1,G=1,B=1,A=1}end
local function clear()return {R=0,G=0,B=0,A=0}end
local function identity_transform()return {Translation={X=0,Y=0},Scale={X=1,Y=1},Shear={X=0,Y=0},Angle=0}end
local create=S.objects['/Script/UMG.WidgetBlueprintLibrary:Create']
local oldcreate=getmetatable(create).__call
getmetatable(create).__call=function(...)
 local w=oldcreate(...);w.RenderOpacity=1;w.RenderTransform=identity_transform()
 w.WidgetTree.RootWidget.RenderTransform=identity_transform()
 local root=w.WidgetTree.RootWidget;local add=root.AddChildToCanvas
 root.AddChildToCanvas=function(...)
  local slot=add(...)
  slot.SetSize=function(_,v)slot.size=v end;slot.GetSize=function()return slot.size end
  slot.SetAnchors=function(_,v)slot.anchors=v end;slot.GetAnchors=function()return slot.anchors end
  slot.SetAlignment=function(_,v)slot.alignment=v end;slot.GetAlignment=function()return slot.alignment end
  slot.SetPosition=function(_,v)slot.position=v end;slot.GetPosition=function()return slot.position end
  slot.SetAutoSize=function(_,v)slot.auto=v end;slot.GetAutoSize=function()return slot.auto end
  return slot
 end
 return w
end
local construct=StaticConstructObject
function StaticConstructObject(...)
 local o=construct(...)
 if o==S.comp then
  o.bApplyGammaCorrection=false;o.BackgroundColor=clear();o.TintColorAndOpacity=white();o.OpacityFromTexture=1
  o.rt=owned(o.p..'.RT','/Script/Engine.TextureRenderTarget2D',o)
  o.rt.SizeX=512;o.rt.SizeY=128;o.rt.sRGB=true;o.rt.bForceLinearGamma=false
  o.rt.TargetGamma=0;o.rt.RenderTargetFormat=0;o.rt.ClearColor=clear()
  o.GetRenderTarget=function()if o.registered and S.rendered then return o.rt end end
  o.GetPivot=function()return o.pivot end
  o.SetMaterial=function(_,i,m)
   assert(S.game and not S.in_script and i==0 and (m==S.stock or m==S.trans))
   if o.registered and S.switch_fail then error('native SetMaterial failure')end
   S.output_sets=S.output_sets+1;o.mat=m
   o.mid=owned(o.p..'.MID'..S.output_sets,'/Script/Engine.MaterialInstanceDynamic',o);o.mid.Parent=m
   o.mid.K2_GetTextureParameterValue=function(_,n)assert(n=='SlateUI');return o.rt end
   o.mid.K2_GetVectorParameterValue=function(_,n)if n=='TintColorAndOpacity'then return o.TintColorAndOpacity end;assert(n=='BackColor');return clear()end
   o.mid.K2_GetScalarParameterValue=function(_,n)assert(n=='OpacityFromTexture');return o.OpacityFromTexture end
  end
 elseif o==S.hint then
  o.ColorAndOpacity=white();o.RenderOpacity=1
  o.RenderTransform={Translation={X=0,Y=0},Scale={X=1,Y=1},Shear={X=0,Y=0},Angle=0}
  o.SetColorAndOpacity=function(_,v)o.color=v;o.ColorAndOpacity=v end
 end
 return o
end
function baseline()start();settle();key(8);settle();assert(has('mode=masked material='))end
function pair()baseline();key(6);settle();assert(has('PAIR_READY'))end
'''


class HintABPolicy(unittest.TestCase):
    def case(self, code, setup=''):
        lua = LuaRuntime(unpack_returned_tuples=True)
        lua.execute(FIXTURE+EXTRA+CONTEXT+ORIENTATION+FRAMES+HINT_FIXTURE+AB_FIXTURE)
        for name, source in SOURCES.items():
            if name != 'main':
                lua.execute('package.preload["'+name+'"]=function()\n'+source+'\nend')
        lua.execute(setup)
        lua.execute(SOURCES['main'])
        try:
            lua.execute(code)
        except Exception:
            print(list(lua.globals().S.logs.values())[-12:])
            raise

    def test_pair_one_component_two_materials_and_cleanup(self):
        self.case('pair();assert(S.created==1 and S.output_sets==2 and S.loop_registered==1);'
                  'assert(S.comp.mat==S.trans and S.comp.BlendMode==2 and S.hint.Brush.ResourceObject==S.hint_mid);'
                  'key(7);yawframe();assert(S.destroys==1 and S.loop==nil and has("CLEANED") and S.hint.Brush.ResourceObject==nil)')

    def test_projected_slot_uses_actual_world_plane_corners(self):
        self.case('baseline();assert(#S.projected==4 and has("own_slot_world=9.5,9.5") '
                  'and has("own_slot_size_px=95,95") and has("source_screen_px=UNAVAILABLE"));'
                  'local p=S.projected[1];assert(p.X==10 and p.Y==24.75 and p.Z==66.75)')

    def test_switch_is_single_and_cannot_start_before_ready(self):
        self.case('start();key(6);assert(S.output_sets==1);settle();key(8);settle();key(6);settle();key(6);'
                  'assert(has("PAIR_READY") and S.output_sets==2 and has("SWITCH_IGNORED"))')

    def test_camera_movement_rejects_before_switch(self):
        self.case('baseline();S.camera.X=S.camera.X+2;key(6);assert(has("AB camera moved") '
                  'and S.output_sets==1 and has("CLEANED"))')

    def test_camera_rotation_or_fov_change_rejects(self):
        for change in ['S.camera_rotation.Yaw=181','S.fov=91','S.view_width=1280']:
            with self.subTest(change=change):
                self.case('baseline();'+change+';key(6);assert(has("FAILED") and S.output_sets==1 and has("CLEANED"))')

    def test_small_documented_camera_tolerance_records_both_poses(self):
        self.case('baseline();S.camera.X=S.camera.X+0.5;key(6);settle();assert(has("PAIR_READY"))')

    def test_device_generation_change_does_not_compare_stale_glyph(self):
        self.case('baseline();S.device=4;settle();key(6);assert(has("AB source no longer matches baseline") '
                  'and S.output_sets==1 and has("CLEANED"))')

    def test_pending_rt_does_not_switch_or_claim_measurement(self):
        self.case('start();settle();key(6);assert(not has("event=SAMPLE mode=") and S.output_sets==1);'
                  'key(7);assert(has("CLEANED"))', 'S.rendered=false')

    def test_rt_gamma_change_between_samples_rejects(self):
        self.case('baseline();key(6);S.comp.rt.sRGB=false;settle();assert(not has("PAIR_READY") '
                  'and has("AB settings/RT/component changed") and has("CLEANED"))')

    def test_native_switch_failure_has_before_marker_and_cleanup(self):
        self.case('baseline();S.switch_fail=true;key(6);assert(has("name=own_material_switch edge=BEGIN") '
                  'and not has("name=own_material_switch edge=END") and has("CLEANED"))')

    def test_projection_failure_stops_without_fake_pixels(self):
        self.case('start();settle();key(8);settle();assert(has("AB projection failed") and not has("event=SAMPLE mode=") and has("CLEANED"))',
                  'S.project_fail=true')

    def test_missing_translucent_refuses_before_component_allocation(self):
        self.case('start();assert(not S.comp and has("FAILED"))', 'set(S.trans,"live",false)')

    def test_inactive_retainer_refuses_before_allocation(self):
        self.case('start();assert(not S.comp and has("AB requires retained AlphaComposite source"))',
                  'S.retainer.bRetainRender=false')

    def test_absent_reflected_gamma_is_not_guessed(self):
        self.case('start();settle();S.comp.bApplyGammaCorrection=nil;key(8);settle();assert(has("AB reflected gamma flags missing") '
                  'and not has("PAIR_READY") and has("CLEANED"))')

    def test_baseline_material_interference_refuses_overwrite(self):
        self.case('baseline();S.comp.BlendMode=2;key(6);assert(has("AB baseline material changed") and S.output_sets==1 and has("CLEANED"))')

    def test_visibility_failure_after_switch_still_stops_frame_loop(self):
        self.case('baseline();key(6);set(P.component,"bVisible",false);yawframe();'
                  'assert(has("FAILED") and S.loop==nil and has("CLEANED") and not has("PAIR_READY"))')

    def test_unchanged_timeout_cancels_pending_comparison(self):
        self.case('baseline();key(6);S.now=S.now+46;yawframe();assert(has("orientation_timeout") '
                  'and has("CLEANED") and S.loop==nil and not has("PAIR_READY"))')

    def test_missing_projection_api_refuses_before_allocation(self):
        self.case('key();assert(not S.comp and has("AB API missing"))',
                  'S.objects["/Script/Engine.PlayerController:ProjectWorldLocationToScreen"]=nil')

    def test_new_hint_source_during_settling_rejects_pair(self):
        self.case('baseline();key(6);S.device=4;settle();assert(has("AB hint changed between samples") '
                  'and has("CLEANED") and not has("PAIR_READY"))')

    def test_cancel_queued_switch_is_inert(self):
        self.case('baseline();S.keys[6]();S.keys[7]();flush();assert(S.output_sets==1 and has("CLEANED"));yawframe()')

    def test_frozen_sources_unchanged_and_no_geometry_workaround(self):
        import hashlib
        frozen=DIR.parents[1]/'Scripts'
        expected={'main.lua':'73e8205c4322cb6b78121b98195b3beda1825d3deaf95aa33eb30043e3e0be90',
                  'IIPWorldChild.lua':'e214651e937ac4241805d7db043e2080239dd9b1da3333ca49936b9358ed5cdc',
                  'IIPHintSource.lua':'b49d814534b1df3eabb8a4cedc45f6fdf7b847284465224046a638a7e3d4a92d'}
        for name,digest in expected.items():
            self.assertEqual(hashlib.sha256((frozen/name).read_bytes()).hexdigest(),digest)
        joined='\n'.join(SOURCES.values())
        for forbidden in ['GetCachedGeometry(', 'GetPaintSpaceGeometry(', 'GetTickSpaceGeometry(',
                          'SetBlendMode(', 'SetScalarParameterValue(', 'SetTextureParameterValue(', 'SetVectorParameterValue(']:
            self.assertNotIn(forbidden,joined)


if __name__ == '__main__':
    unittest.main()
