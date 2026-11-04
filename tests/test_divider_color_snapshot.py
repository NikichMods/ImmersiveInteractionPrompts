# SPDX-License-Identifier: MPL-2.0
"""Execute successor Lua against existing host fixtures; no engine-render claim."""
import hashlib
import json
import struct
import unittest
import zlib
from unittest.mock import patch
import test_world_editor_style as style
from test_ui_child import LuaRuntime, ROOT
from test_live_resources import FIX, FONT, PNG, EXTRA, SETUP

BASE = ROOT/'research/interaction-prompts-owner/world-space/divider-color-snapshot'
SOURCES = {p.stem: p.read_text(encoding='utf8') for p in (BASE/'Scripts').glob('*.lua')}
PNG_PATH = ROOT/'assets/dividers/aphes_divider_256x32.png'
PNG_SHA = 'b56cc7741c794594eb300db63d2bbe67b0db1eaba217ccceae7c23ef829f1969'

DIAGNOSTIC = r'''
function rgba(r,g,b,a)return {R=r,G=g,B=b,A=a}end
local finish=P.actor.FinishAddComponent
set(P.actor,'FinishAddComponent',function(...)
 finish(...)
 local c=S.comp
 c.bApplyGammaCorrection=false;c.BackgroundColor=rgba(0,0,0,0)
 c.TintColorAndOpacity=rgba(1,1,1,1);c.OpacityFromTexture=1
 local rt=owned(c.p..'.RT','/Script/Engine.TextureRenderTarget2D',c);c.rt=rt
 rt.SizeX=1024;rt.SizeY=512;rt.sRGB=true;rt.TargetGamma=0
 rt.bForceLinearGamma=false;rt.RenderTargetFormat=6;rt.OverrideFormat=2;rt.ClearColor=rgba(0,0,0,0)
 local mid=c.mid
 mid.K2_GetTextureParameterValue=function(_,name)
  assert(name=='SlateUI');S.slate_reads=(S.slate_reads or 0)+1;return S.wrong_binding and S.icon or rt
 end
 mid.K2_GetVectorParameterValue=function(_,name)
  if S.missing_vectors then error('getter not available')end
  assert(name=='TintColorAndOpacity' or name=='BackColor')
  return name=='BackColor' and rgba(0,0,0,0) or rgba(1,1,1,1)
 end
 mid.K2_GetScalarParameterValue=function(_,name)assert(name=='OpacityFromTexture');return 1 end
 S.icon.sRGB=false;S.icon.TargetGamma=1;S.icon.OverrideFormat=2;S.icon.ClearColor=rgba(0,0,0,0)
 S.effect_base.BlendMode=5
 S.hint_mid.K2_GetVectorParameterValue=function()error('native parameter contract NOT ESTABLISHED')end
 S.hint_mid.K2_GetScalarParameterValue=function()error('native parameter contract NOT ESTABLISHED')end
end)
function color_lines()
 local n=0;for _,v in ipairs(S.logs)do if v:find('IIP_COLOR event=SNAPSHOT',1,true)then n=n+1 end end
 return n
end
'''

class DividerIntegration(unittest.TestCase):
    def case(self, code, setup=''):
        # Reuse the established complete lifecycle/editor fixture, execute new Lua.
        with patch.object(style, 'SOURCES', SOURCES):
            return style.WorldEditorStyle().case(code, DIAGNOSTIC+setup)

    def test_initial_aspect_full_envelope_and_manual_cleanup(self):
        self.case('ready();assert(#S.tuning.fields==17);near(S.divider.Slot.size.X,300);'
                  'near(S.divider.Slot.size.Y,37.5);near(S.hint.Slot.position.Y,S.divider.Slot.position.Y);'
                  'assert(S.lower.Slot.position.Y-S.lower.Slot.size.Y/2>S.divider.Slot.position.Y+18.75);'
                  'assert(color_lines()==4 and S.slate_reads==1);tap("Multiply");'
                  'assert(has("CLEANED") and S.comp.pending and not S.panel.viewport);'
                  'assert(S.divider.Brush.ResourceObject==nil and S.hint.Brush.ResourceObject==nil)')

    def test_one_snapshot_across_edits_yaw_hide_resume_and_device_change(self):
        self.case('ready();local c,rt,mid=S.comp,S.comp.rt,S.comp.mid;'
                  'up_field("divider_thickness",2);near(S.divider.Slot.size.Y,56.25);'
                  'down_field("divider_alpha",2);near(S.divider.ColorAndOpacity.A,0.9);'
                  'for i=1,10 do yawframe()end;suspend();S.device=4;resume();'
                  'assert(S.comp==c and S.comp.rt==rt and S.comp.mid==mid and S.imports==1);'
                  'near(S.divider.Slot.size.Y,56.25);assert(color_lines()==4 and S.slate_reads==1);'
                  'tap("NumPadNine");assert(has("divider_thickness=1.5"));tap("Multiply");assert(has("CLEANED"))')

    def test_inaccessible_optional_fields_do_not_end_session_or_supply_defaults(self):
        self.case('ready();assert(has("sRGB=UNAVAILABLE") and has("TargetGamma=UNAVAILABLE")'
                  ' and has("OverrideFormat_enum=UNAVAILABLE") and has("TintColorAndOpacity=UNAVAILABLE"));'
                  'live();tap("NumPadNine");tap("Multiply");assert(has("CLEANED"))',
                  self.after_finish('S.comp.rt.sRGB=nil;S.comp.rt.TargetGamma=nil;S.comp.rt.OverrideFormat=nil;'
                                    'S.missing_vectors=true'))

    @staticmethod
    def after_finish(code):
        return "local f=P.actor.FinishAddComponent;set(P.actor,'FinishAddComponent',function(...)f(...);"+code+" end)"

    def test_bad_identity_binding_and_native_identity_are_still_fatal(self):
        for setup in [self.after_finish('S.comp.mid.Parent=S.effect_base'),
                      'S.wrong_binding=true',
                      self.after_finish('S.comp.rt.GetOuter=function()return S.retainer end')]:
            self.case('start();settle();assert(has("event=FAILED") and has("CLEANED") and S.comp.pending)', setup)

    def test_missing_own_rt_has_bounded_checks_no_retries_or_session_deadline(self):
        self.case('ready();for i=1,15 do yawframe()end;assert(color_lines()==1 and has("visible_checks=8"));'
                  'S.comp.rt=owned("/Later.RT","/Script/Engine.TextureRenderTarget2D",S.comp);'
                  'suspend();resume();assert(color_lines()==1);live();tap("Multiply")',
                  self.after_finish('S.comp.rt=nil'))

    def test_optional_getter_failure_is_recorded_once(self):
        self.case('ready();assert(color_lines()==1 and has("own_rt_getter_UNAVAILABLE"));'
                  'for i=1,8 do yawframe()end;assert(color_lines()==1);live();tap("Multiply")',
                  self.after_finish('S.comp.GetRenderTarget=function()S.rt_reads=(S.rt_reads or 0)+1;'
                                    'if S.rt_reads==2 then error("optional read unavailable")end;return S.comp.rt end'))

    def test_native_inactive_retainer_never_invents_rt_or_effect_parameters(self):
        self.case('ready();assert(has("retained=false") and has("RHI_pixel_format=UNKNOWN")'
                  ' and has("effective_tint_back_opacity=UNAVAILABLE_parameter_contract_not_established"));'
                  'live();tap("Multiply")', 'S.retainer.bRetainRender=false')

    def test_overflow_rollback_and_cleanup_retry_remain_recoverable(self):
        self.case('ready();tap("NumPadFive");up_field("upper_size",11);up_field("lower_size",9);'
                  'up_field("divider_thickness",20);up_field("gap",11);'
                  'assert(has("EDIT_REJECTED") and not has("event=FAILED"));live();'
                  'S.release_fail=true;tap("Multiply");assert(has("CLEANUP_PENDING") and not S.comp.pending);'
                  'S.release_fail=false;key();assert(has("CLEANED") and S.comp.pending)')

    def test_original_tip_and_native_material_remain_read_only(self):
        self.case('ready();assert(P.text.Font==S.original_font and S.source_image.ColorAndOpacity.R==1);'
                  'assert(S.icon.sRGB==false and S.icon.TargetGamma==1 and S.comp.rt.sRGB==true);'
                  'assert(S.comp.bApplyGammaCorrection==false and S.comp.BlendMode==1);'
                  'down_field("hint_brightness",2);suspend();resume();tap("Multiply");assert(has("CLEANED"))')


class DividerResources(unittest.TestCase):
    def case(self, code, setup=''):
        lua=LuaRuntime(unpack_returned_tuples=True)
        # Actual successor resource module; established native-import/font fixture
        # adapted only to the approved file dimensions.
        lua.execute(FIX+FONT+PNG.replace('570','256').replace('16','32')+
                    EXTRA.replace('570,16','S.bad_png and 999 or 256,32')+SETUP)
        lua.execute('Resources=(function()\n'+SOURCES['IIPResources']+'\nend)()')
        lua.execute('S.game=true;'+setup)
        lua.execute(code)

    def test_actual_transient_import_once_binding_release_and_font_donor(self):
        self.case('Resources.prepare();local label=resource_label();Resources.font(label);'
                  'local line=resource_line();Resources.ornament(line,S.test_widget);'
                  'assert(line.Brush.ResourceObject==S.texture and S.imports==1);'
                  'assert(not pcall(Resources.ornament,line,S.test_widget));assert(S.imports==1);'
                  'line:SetBrushResourceObject(nil);label:SetFont(S.test_stock.Font);'
                  'assert(line.Brush.ResourceObject==nil and donor_ok())')

    def test_invalid_header_dimensions_and_import_failure_do_not_bind(self):
        for setup in ['S.bad_png=true','S.file_missing=true']:
            self.case('assert(not pcall(Resources.prepare));assert(not S.imports)',setup)
        for setup in ['S.import_null=true','S.not_transient=true','S.bad_texture_size=true','S.bind_fail=true']:
            self.case('Resources.prepare();local line=resource_line();'
                      'assert(not pcall(Resources.ornament,line,S.test_widget));'
                      'assert(S.imports==1);line:SetBrushResourceObject(nil)',setup)

    def test_wrong_png_bit_depth_color_type_and_interlace_rejected(self):
        for offset,byte in [(25,16),(26,2),(29,1)]:
            self.case('assert(not pcall(Resources.prepare));assert(not S.imports)',
                      f'local op=io.open;io.open=function(...)local f=op(...);local rd=f.read;'
                      f'f.read=function(...)local h=rd(...);if h:sub(1,8)=="\\137PNG\\r\\n\\26\\n"then '
                      f'h=h:sub(1,{offset-1})..string.char({byte})..h:sub({offset+1})end;return h end;return f end')


class AssetAndGeometry(unittest.TestCase):
    def test_approved_png_identity_rgba_ihdr_and_chunk_integrity(self):
        data=PNG_PATH.read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(),PNG_SHA)
        self.assertEqual(data[:8],b'\x89PNG\r\n\x1a\n')
        self.assertEqual(struct.unpack('>IIBBBBB',data[16:29]),(256,32,8,6,0,0,0))
        pos=8; chunks=[]
        while pos<len(data):
            n=struct.unpack('>I',data[pos:pos+4])[0]
            chunk=data[pos+4:pos+8+n];crc=struct.unpack('>I',data[pos+8+n:pos+12+n])[0]
            self.assertEqual(zlib.crc32(chunk)&0xffffffff,crc)
            chunks.append(chunk[:4]);pos+=12+n
        self.assertEqual(pos,len(data));self.assertEqual(chunks[-1],b'IEND')

    def test_full_envelopes_remain_separated_across_supported_divider_range(self):
        lua=LuaRuntime(unpack_returned_tuples=True)
        lua.execute('T=(function()\n'+SOURCES['IIPTuning']+'\nend)()')
        lua.execute('local s=T.new();for _,width in ipairs({100,300,640})do '
                    'for _,thick in ipairs({0.5,1,2.5,6})do s.divider_width=width;s.divider_thickness=thick;'
                    'local p=T.plan(s,{X=208,Y=86},{X=120,Y=53},{X=38,Y=38});'
                    'if p then assert(p.divider[4]==width*32/256*thick);'
                    'assert(p.upper[2]+p.upper[4]/2<=p.divider[2]-p.divider[4]/2);'
                    'assert(p.divider[2]+p.divider[4]/2<=p.lower[2]-p.lower[4]/2);'
                    'assert(p.lower[2]+p.lower[4]/2<=508)end end end')

    def test_frozen_predecessor_and_manifest(self):
        old=BASE.parent/'live-editor-style'
        manifest=json.loads((old/'SOURCE_MANIFEST.json').read_text())
        for name,sha in manifest['files'].items():
            self.assertEqual(hashlib.sha256((old/name).read_bytes()).hexdigest(),sha)
        new=json.loads((BASE/'SOURCE_MANIFEST.json').read_text())
        for name,sha in new['files'].items():
            self.assertEqual(hashlib.sha256((BASE/name).read_bytes()).hexdigest(),sha)
        for name in ['main.lua','IIPComposition.lua','IIPPanel.lua','IIPInputAudit.lua','IIPKeyboardBindings.lua']:
            self.assertEqual((BASE/'Scripts'/name).read_bytes(),(old/'Scripts'/name).read_bytes())


if __name__=='__main__':unittest.main()
