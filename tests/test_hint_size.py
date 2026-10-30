# SPDX-License-Identifier: MPL-2.0
"""One owned-slot extent change and persistent rebind policy, not pixel acceptance."""
import hashlib
import re
import unittest
from test_ui_child import LuaRuntime, ROOT
from test_beginplay_join import FIXTURE
from test_world_child import EXTRA
from test_world_deferred import CONTEXT
from test_world_orientation import ORIENTATION
from test_vertical_yaw import FRAMES
from test_hint_mirror import HINT_FIXTURE
from test_hint_ab import AB_FIXTURE

DIR=ROOT/'research/interaction-prompts-owner/world-space/hint-mirror/size/Scripts'
SOURCES={p.stem:p.read_text(encoding='utf8') for p in DIR.glob('*.lua')}
SIZE_FIXTURE=r'''
S.size_writes=0
for _,p in ipairs({'/Script/UMG.CanvasPanelSlot:SetSize','/Script/UMG.CanvasPanelSlot:GetSize'})do
 local f=make(p,'Function');set(f,'type',function()return 'UFunction'end)
end
S.retainer.Slot.SetSize=function()error('SOURCE SIZE WRITE')end
local create=S.objects['/Script/UMG.WidgetBlueprintLibrary:Create']
local oldcreate=getmetatable(create).__call
getmetatable(create).__call=function(...)
 local w=oldcreate(...);local root=w.WidgetTree.RootWidget;local add=root.AddChildToCanvas
 root.AddChildToCanvas=function(...)
  local slot=add(...);local setter=slot.SetSize
  slot.SetSize=function(_,v)
   S.size_writes=S.size_writes+1
   if S.size_set_fail then error('native own SetSize failure')end
   setter(slot,v)
   if S.bad_size_readback then slot.size={X=v.X+1,Y=v.Y}end
  end
  return slot
 end
 return w
end
function baseline()start();settle();key(8);settle();assert(has('mode=original multiplier=1 '))end
function sizepair()baseline();key(6);settle();assert(has('PAIR_READY'))end
'''


class HintSizePolicy(unittest.TestCase):
    def case(self,code,setup=''):
        lua=LuaRuntime(unpack_returned_tuples=True)
        lua.execute(FIXTURE+EXTRA+CONTEXT+ORIENTATION+FRAMES+HINT_FIXTURE+AB_FIXTURE+SIZE_FIXTURE)
        for name,source in SOURCES.items():
            if name!='main':lua.execute('package.preload["'+name+'"]=function()\n'+source+'\nend')
        lua.execute(setup);lua.execute(SOURCES['main'])
        try:lua.execute(code)
        except Exception:
            print(list(lua.globals().S.logs.values())[-12:]);raise

    def test_one_owned_slot_change_preserves_source_and_component(self):
        self.case('sizepair();local v=S.hint.Slot:GetSize();assert(v.X==57 and v.Y==57);'
                  'assert(S.hint_size.X==38 and S.hint_size.Y==38 and S.size_writes==2);'
                  'assert(S.created==1 and S.output_sets==1 and S.comp.mat==S.stock and S.comp.BlendMode==1);'
                  'assert(S.comp.transform.scale.X==0.25 and S.comp.draw.X==512 and S.comp.draw.Y==128 '
                  'and S.comp.transform.position.Z==62 and S.loop_registered==1);'
                  'assert(has("mode=enlarged multiplier=1.5") and has("own_slot_canvas_bounds=227.5,35.5,284.5,92.5"));'
                  'key(7);yawframe();assert(S.destroys==1 and S.loop==nil and has("CLEANED"))')

    def test_initial_and_enlarged_world_corners_project_with_same_center(self):
        self.case('sizepair();assert(#S.projected==10);local a,b=S.projected[1],S.projected[6];'
                  'assert(a.X==10 and a.Y==24.75 and a.Z==66.75);'
                  'assert(b.X==10 and b.Y==27.125 and b.Z==69.125);'
                  'local center=S.projected[10];assert(center.X==10 and center.Y==20 and center.Z==62 '
                  'and has("own_slot_center_px=960,540"));'
                  'assert(has("own_slot_size_px=95,95") and has("own_slot_size_px=142.5,142.5"));'
                  'assert(S.hint.Slot:GetPosition().X==0 and S.hint.Slot:GetAlignment().X==0.5)')

    def test_enlargement_survives_device_rebind_after_pair(self):
        self.case('sizepair();S.device=4;settle();local v=S.hint.Slot:GetSize();'
                  'assert(v.X==57 and v.Y==57 and S.hint.Visibility==3 and has("multiplier=1.5 own_slot=57.0,57.0"));'
                  'S.device=1;settle();assert(S.hint.Slot:GetSize().X==57 and S.output_sets==1)')

    def test_enlargement_survives_mid_and_rt_replacement(self):
        self.case('sizepair();S.hint_mid=new_mid("/Hint.Replaced");S.icon=new_icon("/Hint.NewRT");settle();'
                  'assert(S.hint.Slot:GetSize().X==57 and S.hint.Brush.ResourceObject==S.hint_mid and S.output_sets==1)')

    def test_changed_native_extent_preserves_aspect_and_factor(self):
        self.case('sizepair();S.hint_size={X=40,Y=32};settle();local v=S.hint.Slot:GetSize();'
                  'assert(v.X==60 and v.Y==48 and S.hint_size.X==40 and S.hint_size.Y==32)')

    def test_oversize_planned_variant_refuses_before_allocation(self):
        self.case('start();assert(not S.comp and has("scaled hint exceeds own Canvas envelope"))',
                  'S.hint_size={X=38,Y=85}')

    def test_oversize_source_rebind_hides_and_cleans(self):
        self.case('sizepair();S.hint_size={X=38,Y=85};yawframe();'
                  'assert(S.hint.Visibility==1 and S.hint.Brush.ResourceObject==nil and has("CLEANED"))')

    def test_largest_supported_height_and_non_square_aspect(self):
        self.case('sizepair();local v=S.hint.Slot:GetSize();assert(v.X==144 and v.Y==126 '
                  'and has("own_slot_canvas_bounds=184,1,328,127"))', 'S.hint_size={X=96,Y=84}')

    def test_early_and_repeated_switch_are_inert(self):
        self.case('start();key(6);settle();key(8);settle();key(6);settle();key(6);'
                  'assert(has("PAIR_READY") and S.size_writes==2 and has("SWITCH_IGNORED"))')

    def test_source_change_between_pair_rejects_comparison(self):
        self.case('baseline();S.device=4;settle();key(6);assert(has("size source no longer matches baseline") '
                  'and not has("PAIR_READY") and has("CLEANED"))')

    def test_source_change_during_enlarged_capture_rejects(self):
        self.case('baseline();key(6);S.device=4;settle();'
                  'assert(has("size hint changed between samples") and has("CLEANED") and not has("PAIR_READY"))')

    def test_camera_change_before_size_mutation_rejects(self):
        self.case('baseline();local n=S.size_writes;S.camera.X=S.camera.X+2;key(6);'
                  'assert(S.size_writes==n and has("size camera moved") and has("CLEANED"))')

    def test_native_setsize_failure_has_phase_and_cleanup(self):
        self.case('baseline();S.size_set_fail=true;key(6);'
                  'assert(has("name=own_size_switch edge=BEGIN") and not has("name=own_size_switch edge=END") '
                  'and has("CLEANED"))')

    def test_bad_size_readback_is_not_accepted(self):
        self.case('baseline();S.bad_size_readback=true;key(6);'
                  'assert(has("own size readback differs") and has("CLEANED") and not has("PAIR_READY"))')

    def test_unexpected_layout_transform_rejects(self):
        self.case('baseline();key(6);S.hint.RenderTransform.Angle=1;settle();'
                  'assert(has("size own layout transformed") and has("CLEANED") and not has("PAIR_READY"))')

    def test_unrelated_gamma_or_material_change_invalidates_pair(self):
        for change in ['S.comp.bApplyGammaCorrection=true','S.comp.BlendMode=2']:
            with self.subTest(change=change):
                self.case('baseline();key(6);'+change+';settle();assert(not has("PAIR_READY") and has("CLEANED"))')

    def test_unexpected_slot_reset_after_pair_is_detected(self):
        self.case('sizepair();S.hint.Slot.size={X=38,Y=38};for i=1,12 do yawframe()end;'
                  'assert(has("own extent changed outside size experiment") and has("CLEANED"))')

    def test_projection_failure_has_no_fake_screen_measurement(self):
        self.case('start();settle();key(8);settle();assert(has("size projection failed") and has("CLEANED"))',
                  'S.project_fail=true')

    def test_missing_setsize_contract_refuses_before_allocation(self):
        self.case('key();assert(not S.comp and has("size API missing"))',
                  'S.objects["/Script/UMG.CanvasPanelSlot:SetSize"]=nil')

    def test_queued_cancel_prevents_enlargement(self):
        self.case('baseline();S.keys[6]();S.keys[7]();flush();yawframe();assert(S.size_writes==1 and has("CLEANED"))')

    def test_unchanged_timeout_and_visibility_guards(self):
        for change in ['S.now=S.now+46','set(P.component,"bVisible",false)']:
            with self.subTest(change=change):
                self.case('baseline();key(6);'+change+';yawframe();assert(has("CLEANED") and S.loop==nil and not has("PAIR_READY"))')

    def test_frozen_ab_bytes_and_restricted_mutation_surface(self):
        frozen=DIR.parents[1]/'ab/Scripts'
        expected={'main.lua':'6c863701ec1a0174c66175d2631ffe831f0f208295604e96d8341a7388fb6c1c',
                  'IIPWorldChild.lua':'2f026c71e801c6ad80f1f97d860a0dee5692e7325afd1f6de104bd491114b29d',
                  'IIPHintSource.lua':'66b0d6b7b8b96ae7dd03ffe9a58803920ebf658752d686dc1c34ba647e9a03d9',
                  'IIPHintAB.lua':'09d4acc0dc221bfa74ce3b9d4bc8b153d0199190e6bbfd5497001e53c178bd62'}
        for name,digest in expected.items():self.assertEqual(hashlib.sha256((frozen/name).read_bytes()).hexdigest(),digest)
        joined='\n'.join(SOURCES.values())
        for word in ['Widget3DPassThrough_Translucent','GetCachedGeometry(', 'GetPaintSpaceGeometry(',
                     'SetScalarParameterValue(', 'SetTextureParameterValue(', 'SetVectorParameterValue(', 'SetRenderScale(']:
            self.assertNotIn(word,joined)
        self.assertEqual(joined.count(':SetMaterial('),1)  # Initial stock Masked configuration only.
        self.assertIsNone(re.search(r'\.BlendMode\s*=(?!=)',joined))


if __name__=='__main__':unittest.main()
