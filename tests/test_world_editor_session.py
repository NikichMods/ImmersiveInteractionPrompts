# SPDX-License-Identifier: MPL-2.0
"""Persistent same-target hide/resume, unlimited session and terminal cleanup policy.
These host mocks do not establish native rendering or gameplay lifecycle acceptance.
"""
import hashlib
import json
import unittest
from test_ui_child import LuaRuntime, ROOT
from test_world_live_editor import FIXTURE, EXTRA, CONTEXT, ORIENTATION, FRAMES, HINT_FIXTURE, LIVE, RESOURCES

DIR=ROOT/'research/interaction-prompts-owner/world-space/live-editor-session/Scripts'
SOURCES={p.stem:p.read_text(encoding='utf8') for p in DIR.glob('*.lua')}
SESSION=r'''
set(P.text,'bIsEnabled',true)
set(P.actor,'FinishAddComponent',function(_,c,manual,t)
 assert(manual and c==S.comp and c.widget==S.host and c.draw.X==512 and c.draw.Y==128)
 assert(S.host.Visibility==2);c.transform=t;c.registered=true
end)
function ready()start();settle();assert(has('event=SHOWN') and has('AUDIT_PASS') and S.panel.viewport)end
function suspend()set(P.component,'bVisible',false);yawframe()end
function resume()set(P.component,'bVisible',true);settle()end
function live()assert(not S.comp.pending and S.loop and not S.loop.removed and S.panel.viewport)end
'''

class WorldEditorSession(unittest.TestCase):
    def case(self,code,setup=''):
        lua=LuaRuntime(unpack_returned_tuples=True)
        lua.execute(FIXTURE+EXTRA+CONTEXT+ORIENTATION+FRAMES+HINT_FIXTURE+LIVE+SESSION)
        for name,source in SOURCES.items():
            if name!='main':
                lua.execute('package.preload["'+name+'"]=function()\n'+(RESOURCES if name=='IIPResources' else source)+'\nend')
        lua.execute(setup);lua.execute(SOURCES['main'])
        try:lua.execute(code)
        except Exception:
            print(list(lua.globals().S.logs.values())[-18:]);raise
        return lua

    def test_focus_loss_and_return_reuses_same_native_allocations(self):
        self.case('ready();local c,h,u,f=S.comp,S.host,S.upper,S.upper.Font.FontObject;'
                  'tap("NumPadSix");suspend();live();assert(S.host.Visibility==1 and S.hint.Brush.ResourceObject==nil);'
                  'assert(has("event=HIDDEN") and not has("event=FAILED") and not has("LOOP_CANCELLED"));'
                  'S.device=4;resume();live();assert(S.host.Visibility==3 and has("event=RESUMING"));'
                  'assert(S.comp==c and S.host==h and S.upper==u and S.upper.Font.FontObject==f);'
                  'assert(S.upper.Font.Size==33 and S.created==2 and S.imports==1);tap("Multiply");assert(has("CLEANED"))')

    def test_repeated_visibility_fades_and_not_screen_added_are_reversible(self):
        for change,undo in [('set(P.widget,"Visibility",2)','set(P.widget,"Visibility",0)'),
                            ('set(P.widget,"RenderOpacity",0.5)','set(P.widget,"RenderOpacity",1)'),
                            ('set(P.text,"Visibility",1)','set(P.text,"Visibility",0)'),
                            ('set(P.component,"bAddedToScreen",false)','set(P.component,"bAddedToScreen",true)'),
                            ('S.retainer.Visibility=1','S.retainer.Visibility=0'),
                            ('S.source_image.RenderOpacity=0.5','S.source_image.RenderOpacity=1')]:
            self.case('ready();for i=1,4 do '+change+';for j=1,14 do yawframe()end;'
                      'assert(S.host.Visibility==1);live();'+undo+';settle();assert(S.host.Visibility==3)end;'
                      'assert(not has("event=FAILED") and S.imports==1);tap("Multiply");assert(has("CLEANED"))')

    def test_editor_remains_usable_while_target_hidden_and_keeps_parameters(self):
        self.case('ready();suspend();tap("NumPadSix");tap("NumPadNine");assert(has("event=VALUES"));'
                  'tap("NumPadZero");assert(not S.panel.viewport);tap("NumPadSix");key();yawframe();'
                  'resume();assert(S.upper.Font.Size==33);tap("Multiply");assert(has("CLEANED"))')

    def test_no_outer_wait_show_frame_or_hint_change_budget(self):
        self.case('key();S.now=S.now+10000;for i=1,140 do begin()end;'
                  'set(P.widget,"Visibility",2);for i=1,4200 do show()end;'
                  'assert(S.registered==2 and not has("event=STOP"));set(P.widget,"Visibility",0);show();flush();settle();'
                  'S.now=S.now+100000;for i=1,12010 do yawframe()end;live();'
                  'for i=1,10 do suspend();S.device=(i%2)+1;resume()end;'
                  'assert(S.host.Visibility==3 and not has("event=FAILED") and #S.timers==0);'
                  'tap("Multiply");assert(has("CLEANED"))')

    def test_other_open_callback_does_not_terminate_selected_target_session(self):
        self.case('key();begin();begin(Q);show();flush();settle();suspend();show(Q);flush();'
                  'assert(not has("other_visible_open") and not has("event=STOP"));resume();live();tap("Multiply")',
                  'Q=pair(2)')

    def test_distance_excursion_hides_and_resumes_instead_of_stopping(self):
        self.case('ready();S.camera={X=5000,Y=20,Z=162};yawframe();assert(S.host.Visibility==1);live();'
                  'S.camera={X=610,Y=20,Z=162};settle();assert(S.host.Visibility==3);tap("Multiply")')

    def test_real_identity_or_source_contract_failure_still_cleans(self):
        for condition in ['set(P.actor,"live",false)', 'set(P.component,"Widget",make("/Foreign.UI",WIDGET))',
                          'S.icon=nil','S.poll_failure=true','S.wide_text=true;set(P.text,"value","changed")']:
            self.case('ready();'+condition+';yawframe();assert(has("event=FAILED") and has("CLEANED") and S.comp.pending)')

    def test_suspended_context_loss_stop_and_retired_callback_are_safe(self):
        self.case('ready();suspend();local cb=S.loop.fn;tap("Multiply");assert(has("CLEANED") and S.comp.pending);'
                  'local writes=S.sets;S.game=true;cb();S.game=false;assert(S.sets==writes and S.destroys==1)')
        self.case('ready();suspend();set(P.actor,"live",false);yawframe();assert(has("CLEANED"))')

    def test_cleanup_failure_remains_retryable(self):
        self.case('ready();S.release_fail=true;tap("Multiply");assert(has("CLEANUP_PENDING") and not S.comp.pending);'
                  'S.release_fail=false;key();assert(has("CLEANED") and S.comp.pending)')

    def test_resumed_source_is_hidden_until_new_stable_samples(self):
        self.case('ready();suspend();S.hint_mid=new_mid("/Hint.ResumeMID");set(P.component,"bVisible",true);'
                  'yawframe();assert(S.host.Visibility==2 and S.hint.Brush.ResourceObject==nil);'
                  'yawframe();assert(S.host.Visibility==2);yawframe();assert(S.host.Visibility==3 '
                  'and S.hint.Brush.ResourceObject==S.hint_mid);tap("Multiply")')

    def test_manifest_and_frozen_predecessor(self):
        m=json.loads((DIR.parent/'SOURCE_MANIFEST.json').read_text(encoding='utf8'))
        for path,digest in m['files'].items():
            self.assertEqual(hashlib.sha256((DIR.parent/path).read_bytes()).hexdigest(),digest,path)
        for name in ['main','IIPWorldChild']:
            self.assertNotIn('ExecuteInGameThreadWithDelay',SOURCES[name])
        self.assertNotIn('st.changes<=8',SOURCES['IIPHintSource'])
        predecessor=DIR.parent.parent/'live-editor/Scripts'
        for name in ['IIPResources.lua','IIPPanel.lua','IIPTuning.lua','IIPInputAudit.lua','IIPKeyboardBindings.lua']:
            self.assertEqual((DIR/name).read_bytes(),(predecessor/name).read_bytes(),name)

if __name__=='__main__':unittest.main()
