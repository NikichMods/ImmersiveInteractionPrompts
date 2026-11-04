# SPDX-License-Identifier: MPL-2.0
"""Actual per-element native color/setter and layout policy; not glow/render proof."""
import hashlib
import json
import unittest
from test_ui_child import LuaRuntime, ROOT
from test_world_live_editor import FIXTURE, EXTRA, CONTEXT, ORIENTATION, FRAMES, HINT_FIXTURE, LIVE, RESOURCES
from test_world_editor_session import SESSION
from test_world_editor_expanded import EXPANDED

DIR=ROOT/'research/interaction-prompts-owner/world-space/live-editor-style/Scripts'
SOURCES={p.stem:p.read_text(encoding='utf8') for p in DIR.glob('*.lua')}
STYLE=r'''
local construct=StaticConstructObject
function StaticConstructObject(c,...)
 local o=construct(c,...)
 if c.p=='/Script/UMG.TextBlock'then
  o.SetColorAndOpacity=function(_,v)
   if S.color_failure then error('native color setter failed')end
   o.ColorAndOpacity=v
  end
 elseif c.p=='/Script/UMG.Image'then
  o.ColorAndOpacity={R=1,G=1,B=1,A=1}
 end
 return o
end
function select_name(name)
 local fields=S.tuning.fields;local wanted
 for i,f in ipairs(fields)do if f[1]==name then wanted=i end end
 assert(wanted,'missing field')
 while S.settings.selected~=wanted do tap('NumPadTwo')end
end
function down_field(name,n)
 select_name(name);for i=1,n do tap('NumPadFour')end
end
function up_field(name,n)
 select_name(name);for i=1,n do tap('NumPadSix')end
end
function near(a,b)assert(math.abs(a-b)<0.00001,tostring(a)..' != '..tostring(b))end
'''

class WorldEditorStyle(unittest.TestCase):
    def case(self,code,setup=''):
        lua=LuaRuntime(unpack_returned_tuples=True)
        lua.execute(FIXTURE+EXTRA+CONTEXT+ORIENTATION+FRAMES+HINT_FIXTURE+LIVE+SESSION+EXPANDED+STYLE)
        for name,source in SOURCES.items():
            if name=='main':continue
            extra=''
            if name=='IIPTuning':
                extra='S.tuning=m;local new=m.new;m.new=function()S.settings=new();return S.settings end;'
            lua.execute('package.preload["'+name+'"]=function() local m=(function()\n'+
                        (RESOURCES if name=='IIPResources' else source)+'\nend)();'+extra+'return m end')
        lua.execute(setup);lua.execute(SOURCES['main'])
        try:lua.execute(code)
        except Exception:
            print(list(lua.globals().S.logs.values())[-12:]);raise
        return lua

    def test_last_observed_values_thicker_divider_and_button_on_divider_row(self):
        self.case('ready();assert(S.upper.Font.Size==52 and S.lower.Font.Size==30 and S.upper.Font.LetterSpacing==400);'
                  'near(S.hint.Slot.position.Y,S.divider.Slot.position.Y);'
                  'near(S.divider.Slot.size.Y,240*16/570*2);'
                  'up_field("divider_thickness",2);near(S.divider.Slot.size.Y,240*16/570*2.5);'
                  'assert(S.divider.Slot.size.X==240);up_field("hint_y",4);'
                  'near(S.hint.Slot.position.Y,S.divider.Slot.position.Y+4);tap("Multiply");assert(has("CLEANED"))')

    def test_four_independent_brightness_controls_do_not_change_alpha_or_original(self):
        self.case('ready();down_field("upper_brightness",2);down_field("lower_brightness",4);'
                  'down_field("divider_brightness",6);down_field("hint_brightness",8);'
                  'near(S.upper.ColorAndOpacity.SpecifiedColor.R,0.9);near(S.lower.ColorAndOpacity.SpecifiedColor.R,0.8);'
                  'near(S.divider.ColorAndOpacity.R,0.7);near(S.hint.ColorAndOpacity.R,0.6);'
                  'assert(S.upper.ColorAndOpacity.SpecifiedColor.A==1 and S.lower.ColorAndOpacity.SpecifiedColor.A==1);'
                  'assert(S.divider.ColorAndOpacity.A==1 and S.hint.ColorAndOpacity.A==1);'
                  'assert(P.text.Font==S.original_font and S.source_image.ColorAndOpacity.R==1);'
                  'tap("NumPadNine");assert(has("upper_brightness=0.9") and has("hint_brightness=0.6"));tap("Multiply")')

    def test_hint_brightness_survives_device_mid_rebind_and_suspend(self):
        self.case('ready();down_field("hint_brightness",8);S.device=4;settle();near(S.hint.ColorAndOpacity.R,0.6);'
                  'S.hint_mid=new_mid("/Hint.StyledMID");settle();near(S.hint.ColorAndOpacity.R,0.6);'
                  'suspend();resume();near(S.hint.ColorAndOpacity.R,0.6);'
                  'assert(S.hint.Brush.ResourceObject==S.hint_mid);tap("Multiply");assert(has("CLEANED"))')

    def test_inactive_hint_uses_fresh_source_color_without_cumulative_dimming(self):
        self.case('ready();down_field("hint_brightness",8);'
                  'for i=1,30 do yawframe()end;near(S.hint.ColorAndOpacity.R,0.48);near(S.hint.ColorAndOpacity.A,0.75);'
                  'S.source_image.ColorAndOpacity.R=0.5;yawframe();near(S.hint.ColorAndOpacity.R,0.3);'
                  'assert(S.source_image.ColorAndOpacity.G==0.7);tap("Multiply")',
                  'S.retainer.bRetainRender=false;S.source_image.ColorAndOpacity={R=0.8,G=0.7,B=0.6,A=0.75}')

    def test_lower_outline_is_optional_and_does_not_raise_fill_brightness(self):
        self.case('ready();assert(S.lower.Font.OutlineSettings.OutlineSize==0);'
                  'down_field("lower_brightness",4);up_field("lower_outline",1);'
                  'assert(S.lower.Font.OutlineSettings.OutlineSize==1);near(S.lower.ColorAndOpacity.SpecifiedColor.R,0.8);'
                  'assert(S.lower.Font.OutlineSettings.OutlineColor.R==0 and S.upper.Font.OutlineSettings.OutlineSize==0);'
                  'assert(S.original_font.OutlineSettings.OutlineSize==0);tap("Multiply")')

    def test_new_field_bounds_restore_previous_layout_without_stopping(self):
        self.case('ready();tap("NumPadFive");up_field("hint_size",10);up_field("hint_y",45);'
                  'live();assert(has("EDIT_REJECTED") and not has("event=FAILED"));'
                  'assert(S.hint.Slot.position.Y+S.hint.Slot.size.Y/2<=508);'
                  'tap("NumPadFive");down_field("hint_brightness",4);near(S.hint.ColorAndOpacity.R,0.8);tap("Multiply")')

    def test_panel_pages_all_controls_with_same_line_count_and_closed_keys_inert(self):
        lua=self.case('ready();local first=panel_text();select_name("lower_outline");local last=panel_text();'
                  'S.first_page=first;S.last_page=last;'
                  'assert(first:find("Parameters 1-9 / 17",1,true) and last:find("Parameters 9-17 / 17",1,true));'
                  'tap("NumPadZero");tap("NumPadSix");assert(S.lower.Font.OutlineSettings.OutlineSize==0);'
                  'key();yawframe();tap("Multiply")')
        self.assertEqual(lua.globals().S.first_page.count('\n'),lua.globals().S.last_page.count('\n'))
        self.assertLessEqual(lua.globals().S.first_page.count('\n'),20)

    def test_native_color_failure_still_cleans(self):
        self.case('ready();S.color_failure=true;down_field("upper_brightness",1);'
                  'assert(has("event=FAILED") and has("CLEANED") and S.comp.pending)')

    def test_identity_manifest_and_unchanged_world_input_resource_seams(self):
        manifest=json.loads((DIR.parent/'SOURCE_MANIFEST.json').read_text(encoding='utf8'))
        for path,digest in manifest['files'].items():
            self.assertEqual(hashlib.sha256((DIR.parent/path).read_bytes()).hexdigest(),digest,path)
        for name in ['main.lua','IIPWorldChild.lua','IIPPanel.lua','IIPResources.lua','IIPInputAudit.lua','IIPKeyboardBindings.lua']:
            self.assertEqual((DIR/name).read_bytes(),(DIR.parent.parent/'live-editor-expanded/Scripts'/name).read_bytes(),name)

if __name__=='__main__':unittest.main()
