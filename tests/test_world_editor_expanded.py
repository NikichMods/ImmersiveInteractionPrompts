# SPDX-License-Identifier: MPL-2.0
"""Expanded native DrawSize and rejected-edit rollback policy, not render acceptance."""
import hashlib
import json
import unittest
from test_ui_child import LuaRuntime, ROOT
from test_world_live_editor import FIXTURE, EXTRA, CONTEXT, ORIENTATION, FRAMES, HINT_FIXTURE, LIVE, RESOURCES
from test_world_editor_session import SESSION

DIR=ROOT/'research/interaction-prompts-owner/world-space/live-editor-expanded/Scripts'
SOURCES={p.stem:p.read_text(encoding='utf8') for p in DIR.glob('*.lua')}
EXPANDED=r'''
set(P.actor,'FinishAddComponent',function(_,c,manual,t)
 assert(manual and c==S.comp and c.widget==S.host and c.draw.X==1024 and c.draw.Y==512)
 assert(S.host.Visibility==2 and t.scale.X==0.25 and t.position.Z==62)
 c.transform=t;c.registered=true
end)
local previous_construct=StaticConstructObject
function StaticConstructObject(c,...)
 local o=previous_construct(c,...)
 if c.p=='/Script/UMG.TextBlock'then
  o.GetDesiredSize=function()
   if S.bad_measurement then return {X=0,Y=0}end
   return {X=S.wide_text and 2000 or o.Font.Size*4,Y=o.Font.Size*1.5+8}
  end
  local setfont=o.SetFont
  o.SetFont=function(_,v)
   S.font_sets=(S.font_sets or 0)+1
   if S.fail_font_at==S.font_sets then error('native font setter failed')end
   setfont(o,v)
  end
 end
 return o
end
function select_field(n)
 -- All scenarios start at the first parameter unless stated otherwise.
 for i=2,n do tap('NumPadTwo')end
end
function enlarge()
 tap('NumPadFive') -- Coarse4 font units.
 for i=1,12 do tap('NumPadSix')end
 assert(S.upper.Font.Size==96)
 tap('NumPadTwo');for i=1,9 do tap('NumPadSix')end
 assert(S.lower.Font.Size==64)
end
function overflow()
 -- From lower font selection, select divider relative Y; first decrement overlaps.
 for i=1,4 do tap('NumPadTwo')end
 for i=1,8 do tap('NumPadFour')end
end
function panel_text()return S.panel.WidgetTree.RootWidget.children[2].Text:ToString()end
'''

class ExpandedWorldEditor(unittest.TestCase):
    def case(self,code,setup=''):
        lua=LuaRuntime(unpack_returned_tuples=True)
        lua.execute(FIXTURE+EXTRA+CONTEXT+ORIENTATION+FRAMES+HINT_FIXTURE+LIVE+SESSION+EXPANDED)
        for name,source in SOURCES.items():
            if name!='main':lua.execute('package.preload["'+name+'"]=function()\n'+(RESOURCES if name=='IIPResources' else source)+'\nend')
        lua.execute(setup);lua.execute(SOURCES['main'])
        try:lua.execute(code)
        except Exception:
            print(list(lua.globals().S.logs.values())[-12:]);raise
        return lua

    def test_larger_canvas_and_fonts_beyond_old_failure(self):
        self.case('ready();assert(S.comp.draw.X==1024 and S.comp.draw.Y==512);'
                  'assert(S.upper.Font.Size==48 and S.lower.Font.Size==28);'
                  'enlarge();live();assert(S.host.Visibility==3 and not has("event=FAILED"));'
                  'suspend();resume();assert(S.upper.Font.Size==96 and S.lower.Font.Size==64);'
                  'tap("NumPadNine");assert(has("upper_size=96 lower_size=64"));tap("Multiply");assert(has("CLEANED"))')

    def test_expected_overflow_restores_values_fonts_and_keeps_panel_loop_alive(self):
        self.case('ready();enlarge();overflow();live();assert(has("EDIT_REJECTED") and not has("event=FAILED"));'
                  'assert(S.upper.Font.Size==96 and S.lower.Font.Size==64 and S.host.Visibility==3);'
                  'assert(panel_text():find("previous values restored",1,true));'
                  'tap("NumPadSeven");live();suspend();resume();tap("Multiply");assert(has("CLEANED"))')

    def test_height_overflow_repeated_rejection_is_not_a_session_stop(self):
        self.case('ready();enlarge();for i=1,3 do tap("NumPadTwo")end;'
                  'for i=1,16 do tap("NumPadSix")end;live();'
                  'assert(has("EDIT_REJECTED") and not has("event=STOP"));'
                  'tap("NumPadFour");tap("NumPadNine");tap("Multiply");assert(has("CLEANED"))')

    def test_hidden_pending_edits_are_checked_on_resume(self):
        self.case('ready();enlarge();suspend();overflow();live();resume();'
                  'assert(has("EDIT_REJECTED") and S.host.Visibility==3);live();tap("Multiply")')

    def test_real_native_failures_still_stop_and_cleanup(self):
        self.case('ready();S.fail_font_at=S.font_sets+1;tap("NumPadSix");assert(has("event=FAILED") and has("CLEANED"))')
        self.case('ready();S.bad_measurement=true;tap("NumPadSix");assert(has("event=FAILED") and has("CLEANED"))')
        self.case('ready();S.wide_text=true;set(P.text,"value","changed");yawframe();assert(has("event=FAILED") and has("CLEANED"))')

    def test_failed_rollback_does_not_continue_with_uncertain_native_state(self):
        self.case('ready();select_field(6);S.fail_font_at=S.font_sets+3;'
                  'tap("NumPadFour");tap("NumPadFour");tap("NumPadFour");'
                  'assert(has("event=FAILED") and has("CLEANED"))')

    def test_equal_settings_keep_world_baseline_after_canvas_resize(self):
        lua=LuaRuntime(unpack_returned_tuples=True)
        old=(DIR.parent.parent/'live-editor-session/Scripts/IIPTuning.lua').read_text(encoding='utf8')
        lua.execute('Old=(function()\n'+old+'\nend)();New=(function()\n'+SOURCES['IIPTuning']+'\nend)()')
        lua.execute('local p=Old.new();local a=Old.plan(p,{X=140,Y=48},{X=128,Y=38},{X=38,Y=38});'
                    'local b=New.plan(p,{X=140,Y=48},{X=128,Y=38},{X=38,Y=38});'
                    'for _,role in ipairs({"upper","lower","divider","hint"})do '
                    'assert(math.abs((a[role][1]-256)-(b[role][1]-512))<1e-9);assert(math.abs((a[role][2]-64)-(b[role][2]-256))<1e-9)end')

    def test_exact_manifest_and_unchanged_resource_input_seams(self):
        m=json.loads((DIR.parent/'SOURCE_MANIFEST.json').read_text(encoding='utf8'))
        for path,digest in m['files'].items():
            self.assertEqual(hashlib.sha256((DIR.parent/path).read_bytes()).hexdigest(),digest,path)
        for name in ['IIPResources.lua','IIPPanel.lua','IIPInputAudit.lua','IIPKeyboardBindings.lua','IIPHintSource.lua','main.lua']:
            self.assertEqual((DIR/name).read_bytes(),(DIR.parent.parent/'live-editor-session/Scripts'/name).read_bytes(),name)

if __name__=='__main__':unittest.main()
