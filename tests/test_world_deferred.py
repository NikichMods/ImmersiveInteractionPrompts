# SPDX-License-Identifier: MPL-2.0
"""Deferred lifecycle policy; mocks cannot establish native deadlock resolution."""
import unittest
from test_beginplay_join import FIXTURE
from test_world_child import EXTRA
from test_ui_child import LuaRuntime, ROOT

DIR=ROOT/'research/interaction-prompts-owner/world-space/probe/deferred/Scripts'
MAIN=(DIR/'main.lua').read_text(encoding='utf8')
MODULE=(DIR/'IIPWorldChild.lua').read_text(encoding='utf8')
CONTEXT=r'''
local oldemit=emit
function emit(...)
 local game,inside=S.game,S.in_script
 S.in_script=true;oldemit(...);S.in_script=inside;S.game=game
end
local oldconstruct=StaticConstructObject
function StaticConstructObject(...)
 assert(not S.in_script,'construction in script callback')
 return oldconstruct(...)
end
local factory=S.objects['/Script/UMG.WidgetBlueprintLibrary:Create']
local oldcall=getmetatable(factory).__call
getmetatable(factory).__call=function(...)
 assert(not S.in_script,'Create in script callback')
 if S.reenter then show()end
 return oldcall(...)
end
local oldfinish=P.actor.FinishAddComponent
set(P.actor,'FinishAddComponent',function(...)
 assert(not S.in_script,'registration in script callback')
 return oldfinish(...)
end)
local oldkey=key
function start()key();begin();show();flush()end
function pending_match()key();begin();show()end
'''

class DeferredWorldPolicy(unittest.TestCase):
    def case(self,code,setup=''):
        lua=LuaRuntime(unpack_returned_tuples=True)
        lua.execute(FIXTURE+EXTRA+CONTEXT)
        lua.execute('package.preload["IIPWorldChild"]=function()\n'+MODULE+'\nend')
        lua.execute(setup);lua.execute(MAIN)
        try:lua.execute(code)
        except Exception:
            print(list(lua.globals().S.logs.values()));raise

    def test_match_only_enqueues_then_tick_creates_and_cleanup_is_deferred(self):
        self.case('''pending_match();assert(not S.comp and #S.queue==1 and has('CREATE_QUEUED'))
        show();assert(#S.queue==1);flush();assert(S.created==1 and S.comp.registered)
        frame();key();assert(has('event=STATE'))
        set(P.widget,'Visibility',2);show();assert(not S.comp.pending and #S.queue==1)
        flush();assert(S.comp.pending and has('CLEANED') and has('hooks_remaining=0'))''')

    def test_f7_cancels_creation_already_in_queue(self):
        self.case("pending_match();key(7);assert(not S.comp and has('reason=user'));flush();assert(not S.comp)")

    def test_expired_queued_match_never_constructs(self):
        self.case("pending_match();S.now=S.now+121;flush();assert(not S.comp and has('reason=timeout'))")

    def test_identity_replacement_before_tick_refuses_creation(self):
        self.case("pending_match();set(P.actor,'id',90000);flush();assert(not S.comp and has('IDENTITY_ERROR'))")

    def test_pending_kill_before_tick_refuses_creation_despite_lua_validity(self):
        self.case("pending_match();set(P.actor,'pending',true);flush();assert(not S.comp and has('target pending kill'))")

    def test_private_original_tree_replacement_is_rechecked(self):
        self.case("pending_match();set(P.widget,'WidgetTree',make('/Replaced.Tree','/Script/UMG.WidgetTree'));flush();assert(not S.comp and has('UI/tree/root changed'))")

    def test_target_hide_before_tick_refuses_creation(self):
        self.case("pending_match();set(P.widget,'Visibility',2);flush();assert(not S.comp and has('no longer visible'))")

    def test_preload_only_before_hooks_then_no_reload_in_create(self):
        self.case('''key();assert(S.loads==1 and S.registered==2);begin();show();flush()
        assert(S.created==1 and S.loads==1 and has('name=load_host edge=BEGIN') and has('name=load_host edge=END'))''',r'''
        S.loads=0;set(S.objects[HOST],'live',false)
        LoadAsset=function(p)
         assert(S.game and not S.in_script and S.registered==0 and p==HOST)
         S.loads=S.loads+1;set(S.objects[p],'live',true);return S.objects[p],true,true
        end''')

    def test_asset_lost_on_map_change_no_fallback_load(self):
        self.case("key();begin();show();set(S.objects[HOST],'live',false);flush();assert(not S.comp and has('NOT_LOADED'))")

    def test_preparation_failure_registers_no_hooks_or_components(self):
        self.case("key();assert(not S.comp and S.registered==0 and has('stock depth contract differs'))",'S.base.bDisableDepthTest=true')

    def test_native_create_reentry_does_not_retarget_or_recreate(self):
        self.case("start();assert(S.created==1 and S.registered==2 and not has('FAILED'));key(7);assert(has('CLEANED'))",'S.reenter=true')

    def test_registration_failure_phase_and_partial_cleanup(self):
        self.case("start();assert(has('name=finish_component edge=BEGIN') and not has('name=finish_component edge=END'));assert(has('CLEANED') and S.comp.pending)",'S.finish_fail=true')

    def test_cleanup_failure_retained_and_f7_retry(self):
        self.case("start();key(7);assert(has('CLEANUP_PENDING') and S.owned);S.destroy_fail=false;key(7);assert(has('CLEANED') and not S.owned)",'S.destroy_fail=true')

    def test_success_phase_pairs_and_timer_cancellation(self):
        self.case('''start();for _,n in ipairs({'prepare','resolve_host','resolve_material','create','anchor_camera','look_at',
        'make_transform','resident_assets','component_construct','component_configure','component_material','host_create',
        'widget_bind_first_slate','private_ui','label_construct','finish_component','verify_original'})do
        assert(has('name='..n..' edge=BEGIN') and has('name='..n..' edge=END'),n)end
        timeout(45000);assert(not S.comp.pending);flush();assert(S.comp.pending)
        timeout(120000);show();flush();assert(S.created==1 and S.destroys==1)''')

    def test_preload_nonreturn_simulation_does_not_invent_end_or_deadlock_proof(self):
        # A thrown error can be modeled; a genuinely blocked native call cannot.
        self.case("key();assert(has('name=load_host edge=BEGIN') and not has('name=load_host edge=END') and S.registered==0)",
                  "set(S.objects[HOST],'live',false);LoadAsset=function()error('simulated native load failure')end")

if __name__=='__main__':unittest.main()
