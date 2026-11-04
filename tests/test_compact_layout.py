# SPDX-License-Identifier: MPL-2.0
"""Run real compact Lua with measured-envelope mocks; not glyph/render proof."""
import hashlib
import json
import unittest
from unittest.mock import patch
import test_world_editor_style as style
from test_ui_child import ROOT, LuaRuntime

BASE=ROOT/'research/interaction-prompts-owner/world-space/compact-layout'
OLD=BASE.parent/'divider-color-snapshot'
SOURCES={p.stem:p.read_text(encoding='utf8') for p in (BASE/'Scripts').glob('*.lua')}
DEFAULTS=dict(upper_size=50,lower_size=30,tracking=380,outline=3,gap=2,divider_y=-2,
              divider_width=300,divider_thickness=1,divider_alpha=1,hint_size=50,
              hint_gap=12,hint_y=0,upper_brightness=.8,lower_brightness=.6,
              divider_brightness=.6,hint_brightness=.4,lower_outline=3)
MEASURED=r'''
local construct=StaticConstructObject
function StaticConstructObject(c,...)
 local o=construct(c,...)
 if c.p=='/Script/UMG.TextBlock'then
  o.GetDesiredSize=function()
   if S.bad_measurement then return {X=0,Y=0}end
   local outline=o.Font.OutlineSettings.OutlineSize or 0
   local x=S.wide_text and 2000 or o.Font.Size*4+2*outline
   if S.style_upper_wide and o==S.upper and o.Font.Size>50 then x=600 end
   return {X=x,Y=o.Font.Size*1.5+8+2*outline}
  end
 end
 return o
end
'''

class CompactIntegration(unittest.TestCase):
    def case(self,code,setup=''):
        with patch.object(style,'SOURCES',SOURCES):
            return style.WorldEditorStyle().case(code,MEASURED+setup)

    def test_adopted_defaults_and_native_outline_measured_once(self):
        lua=self.case('ready();assert(#S.tuning.fields==17);'
                      'near(S.upper.Slot.size.Y,S.upper:GetDesiredSize().Y);'
                      'near(S.lower.Slot.size.Y,S.lower:GetDesiredSize().Y);'
                      'near(S.upper.Slot.size.Y,89);near(S.lower.Slot.size.Y,59);'
                      'assert(has("guarded_alpha_h=21.0938") and not has("IIP_COLOR"));'
                      'tap("NumPadNine");tap("Multiply");assert(has("CLEANED"))')
        actual=lua.globals().S.settings
        for key,value in DEFAULTS.items():self.assertAlmostEqual(actual[key],value)

    def test_can_move_above_old_limit_and_reduce_gap_to_zero(self):
        self.case('ready();down_field("divider_y",1);assert(S.settings.divider_y==-3);'
                  'assert(not has("EDIT_REJECTED"));down_field("gap",2);assert(S.settings.gap==0);'
                  'down_field("divider_y",5);assert(S.settings.divider_y==-8);live();'
                  'down_field("divider_y",1);assert(S.settings.divider_y==-8 and has("EDIT_REJECTED"));'
                  'assert(not has("event=FAILED"));tap("Multiply");assert(has("CLEANED"))')

    def test_rejection_restores_last_layout_and_new_reset_baseline(self):
        self.case('ready();down_field("divider_y",8);assert(S.settings.divider_y==-10);'
                  'local y=S.divider.Slot.position.Y;down_field("divider_y",1);'
                  'assert(S.settings.divider_y==-10 and S.divider.Slot.position.Y==y);live();'
                  'tap("NumPadSeven");assert(S.settings.divider_y==-2);tap("Multiply")')

    def test_tuning_persists_across_hide_resume_device_and_same_component(self):
        self.case('ready();local c=S.comp;down_field("divider_y",1);'
                  'suspend();down_field("gap",2);S.device=4;resume();'
                  'assert(S.comp==c and S.settings.divider_y==-3 and S.settings.gap==0);'
                  'assert(S.imports==1 and S.hint.Brush.ResourceObject==S.hint_mid);'
                  'near(S.hint.ColorAndOpacity.R,0.4);live();tap("Multiply");assert(has("CLEANED"))')

    def test_wide_upper_text_cannot_overlap_button_after_compaction(self):
        self.case('ready();up_field("upper_size",1);assert(S.settings.upper_size==50);'
                  'assert(has("Button overlaps upper text") and has("EDIT_REJECTED"));live();tap("Multiply")',
                  'S.style_upper_wide=true')

    def test_failed_measurement_and_failed_rollback_keep_terminal_cleanup(self):
        self.case('ready();S.bad_measurement=true;up_field("upper_size",1);'
                  'assert(has("event=FAILED") and has("CLEANED"))')
        self.case('ready();down_field("divider_y",8);S.fail_font_at=S.font_sets+3;'
                  'down_field("divider_y",1);assert(has("event=FAILED") and has("CLEANED"))')

    def test_stop_releases_resources_retry_and_closed_keys_stay_inert(self):
        self.case('ready();tap("NumPadZero");tap("NumPadSix");assert(S.settings.upper_size==50);'
                  'key();yawframe();S.release_fail=true;tap("Multiply");'
                  'assert(has("CLEANUP_PENDING") and not S.comp.pending);S.release_fail=false;key();'
                  'assert(has("CLEANED") and S.comp.pending and S.divider.Brush.ResourceObject==nil)')

    def test_geometry_does_not_write_original_or_change_world_contract(self):
        self.case('ready();down_field("gap",2);down_field("divider_y",1);'
                  'assert(S.comp.draw.X==1024 and S.comp.draw.Y==512 and S.comp.BlendMode==1);'
                  'assert(S.comp.transform.position.Z==62 and S.comp.transform.scale.X==0.25);'
                  'assert(P.text.Font==S.original_font and S.source_image.ColorAndOpacity.R==1);'
                  'for i=1,6 do yawframe()end;assert(not has("IIP_COLOR"));tap("Multiply")')


class CompactGeometry(unittest.TestCase):
    def tuning(self):
        lua=LuaRuntime(unpack_returned_tuples=True)
        lua.execute('T=(function()\n'+SOURCES['IIPTuning']+'\nend)()')
        return lua

    def test_golden_visible_intervals_and_full_text_metrics(self):
        self.tuning().execute('local s=T.new();local p=assert(T.plan(s,{X=206,Y=80},{X=126,Y=50},{X=38,Y=38}));'
                              'assert(p.upper[2]==237 and p.upper[4]==80);'
                              'assert(p.divider[2]==296.75 and p.divider[4]==37.5);'
                              'assert(p.lower[2]==335.296875);'
                              's.divider_y=-10;assert(T.plan(s,{X=206,Y=80},{X=126,Y=50},{X=38,Y=38}));'
                              's.divider_y=-11;local p,why=T.plan(s,{X=206,Y=80},{X=126,Y=50},{X=38,Y=38});'
                              'assert(not p and why=="Divider overlaps upper text")')

    def test_independent_alpha_and_text_envelopes_for_accepted_grid(self):
        self.tuning().execute('''local accepted=0;local rejected=0
for _,font in ipairs({20,50,96})do for _,outline in ipairs({0,3})do
 for _,width in ipairs({100,300,640})do for _,thickness in ipairs({0.5,1,6})do
  for _,gap in ipairs({0,2,48})do for _,dy in ipairs({-32,-10,-3,-2,32})do
   local s=T.new();s.upper_size=font;s.outline=outline;s.divider_width=width
   s.divider_thickness=thickness;s.gap=gap;s.divider_y=dy
   local ux,uy=font*4+2*outline,font*1.5+8+2*outline
   local p=T.plan(s,{X=ux,Y=uy},{X=126,Y=59},{X=38,Y=38})
   if p then
    accepted=accepted+1;local u,d,l,h=p.upper,p.divider,p.lower,p.hint
    -- Independently use the actual asset's alpha bbox; policy's padded
    -- boundary must be stricter than these visible intervals.
    local alpha_top=d[2]-d[4]/4;local alpha_bottom=d[2]+d[4]/4
    assert(u[4]==uy and l[4]==59)
    assert(u[2]+u[4]/2<alpha_top and l[2]-l[4]/2>alpha_bottom)
    assert(d[2]-d[4]/2>=4 and d[2]+d[4]/2<=508)
    assert(l[2]+l[4]/2+1<=508 and h[2]-h[4]/2>=4 and h[2]+h[4]/2<=508)
    local hx0,hx1=h[1]-h[3]/2,h[1]+h[3]/2
    local hy0,hy1=h[2]-h[4]/2,h[2]+h[4]/2
    assert(hx1<=512-ux/2-1 or hx0>=512+ux/2+1 or hy1<=u[2]-u[4]/2-1 or hy0>=u[2]+u[4]/2+1)
   else rejected=rejected+1 end
  end end end end end end
assert(accepted>0 and rejected>0)''')

    def test_canvas_text_button_and_negative_gap_limits_remain(self):
        self.tuning().execute('''local s=T.new()
assert(not T.plan(s,{X=2000,Y=80},{X=126,Y=50},{X=38,Y=38}))
s.gap=-1;assert(not T.plan(s,{X=206,Y=80},{X=126,Y=50},{X=38,Y=38}))
s.gap=0;s.hint_y=-1000;assert(not T.plan(s,{X=206,Y=80},{X=126,Y=50},{X=38,Y=38}))
s.hint_y=0;s.divider_width=640;s.divider_thickness=6
assert(not T.plan(s,{X=206,Y=300},{X=126,Y=100},{X=38,Y=38}))
assert(not pcall(T.plan,s,{X=206,Y=0},{X=126,Y=50},{X=38,Y=38}))''')

    def test_manifest_and_unchanged_frozen_seams(self):
        m=json.loads((BASE/'SOURCE_MANIFEST.json').read_text())
        for rel,digest in m['files'].items():self.assertEqual(hashlib.sha256((BASE/rel).read_bytes()).hexdigest(),digest)
        old=json.loads((OLD/'SOURCE_MANIFEST.json').read_text())
        for rel,digest in old['files'].items():self.assertEqual(hashlib.sha256((OLD/rel).read_bytes()).hexdigest(),digest)
        for name in ['main.lua','IIPResources.lua','IIPHintSource.lua','IIPPanel.lua','IIPInputAudit.lua','IIPKeyboardBindings.lua']:
            self.assertEqual((BASE/'Scripts'/name).read_bytes(),(OLD/'Scripts'/name).read_bytes())
        self.assertNotIn('IIPColorSnapshot',SOURCES)

if __name__=='__main__':unittest.main()
