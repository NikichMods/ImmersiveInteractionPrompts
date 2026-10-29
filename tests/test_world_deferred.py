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

    def test_load_only_after_match_not_before_reload_or_inside_script(self):
        self.case('''key();assert(S.loads==0 and S.registered==2);begin();show();assert(S.loads==0);flush()
        assert(S.created==1 and S.loads==1 and has('name=load_host edge=BEGIN') and has('name=load_host edge=END'))''',r'''
        S.loads=0;set(S.objects[HOST],'live',false)
        LoadAsset=function(p)
         assert(S.game and not S.in_script and S.registered==2 and p==HOST)
         S.loads=S.loads+1;set(S.objects[p],'live',true);return S.objects[p],true,true
        end''')

    def test_resource_lost_on_reload_is_refreshed(self):
        self.case("key();begin();show();set(S.objects[HOST],'live',false);flush();assert(S.loads==1 and S.created==1)",r'''
        S.loads=0;LoadAsset=function(p)
         assert(p==HOST and S.game and not S.in_script);S.loads=S.loads+1
         set(S.objects[p],'live',true);return S.objects[p],true,true
        end''')

    def test_wrong_material_refuses_before_component_allocation(self):
        self.case("start();assert(not S.comp and has('stock depth contract differs'))",'S.base.bDisableDepthTest=true')

    def test_native_create_reentry_does_not_retarget_or_recreate(self):
        self.case("start();assert(S.created==1 and S.registered==2 and not has('FAILED'));key(7);assert(has('CLEANED'))",'S.reenter=true')

    def test_registration_failure_phase_and_partial_cleanup(self):
        self.case("start();assert(has('name=finish_component edge=BEGIN') and not has('name=finish_component edge=END'));assert(has('CLEANED') and S.comp.pending)",'S.finish_fail=true')

    def test_cleanup_failure_retained_and_f7_retry(self):
        self.case("start();key(7);assert(has('CLEANUP_PENDING') and S.owned);S.destroy_fail=false;key(7);assert(has('CLEANED') and not S.owned)",'S.destroy_fail=true')

    def test_success_phase_pairs_and_timer_cancellation(self):
        self.case('''start();for _,n in ipairs({'prepare','refresh_assets','resolve_host','resolve_material','create','anchor_camera','look_at',
        'make_transform','resident_assets','component_construct','component_configure','component_material','host_create',
        'widget_bind_first_slate','private_ui','label_construct','finish_component','verify_original'})do
        assert(has('name='..n..' edge=BEGIN') and has('name='..n..' edge=END'),n)end
        timeout(45000);assert(not S.comp.pending);flush();assert(S.comp.pending)
        timeout(120000);show();flush();assert(S.created==1 and S.destroys==1)''')

    def test_load_failure_phase_does_not_invent_end_or_deadlock_proof(self):
        # A thrown error can be modeled; a genuinely blocked native call cannot.
        self.case("start();assert(has('name=load_host edge=BEGIN') and not has('name=load_host edge=END') and not S.comp)",
                  "set(S.objects[HOST],'live',false);LoadAsset=function()error('simulated native load failure')end")

    def test_missing_nil_class_is_loaded_once_then_created(self):
        self.case("start();assert(S.loads==1 and S.created==1 and has('state=ABSENT_NIL'))",r'''
        S.loads=0;local old=S.objects[HOST];S.objects[HOST]=nil
        LoadAsset=function(p)assert(p==HOST and not S.in_script);S.loads=S.loads+1;S.objects[p]=old;return old,true,true end''')

    def test_null_wrapper_is_distinguished_without_dereference(self):
        self.case("start();assert(S.loads==1 and S.created==1 and has('state=ABSENT_NULL'))",r'''
        S.loads=0;local old=S.objects[HOST]
        S.objects[HOST]={IsValid=function()return false end,GetAddress=function()return 0 end,
         GetFullName=function()error('null dereference')end}
        LoadAsset=function(p)S.loads=S.loads+1;S.objects[p]=old;return old,true,true end''')

    def test_nonzero_lua_invalid_wrapper_is_distinguished(self):
        self.case("start();assert(S.loads==1 and S.created==1 and has('state=LUA_INVALID'))",r'''
        S.loads=0;local old=S.objects[HOST]
        S.objects[HOST]={IsValid=function()return false end,GetAddress=function()return 555 end,
         GetFullName=function()error('invalid dereference')end}
        LoadAsset=function(p)S.loads=S.loads+1;S.objects[p]=old;return old,true,true end''')

    def test_native_invalid_class_load_attempt_still_rejects_pending_kill(self):
        self.case("start();assert(S.loads==1 and not S.comp and has('state=NATIVE_INVALID') and has('kind=NOT_LOADED'))",r'''
        S.loads=0;set(S.objects[HOST],'pending',true)
        LoadAsset=function(p)S.loads=S.loads+1;return S.objects[p],true,true end''')

    def test_wrong_path_is_identity_error_without_loading(self):
        self.case("start();assert(not S.comp and has('kind=IDENTITY_ERROR') and has('state=IDENTITY_MISMATCH'))",
                  "set(S.objects[HOST],'p','/Wrong.Class')")

    def test_wrong_load_return_path_is_rejected(self):
        self.case("start();assert(S.loads==1 and not S.comp and has('kind=IDENTITY_ERROR'))",r'''
        S.loads=0;S.objects[HOST]=nil
        LoadAsset=function()S.loads=S.loads+1;return make('/Wrong.Class','Class'),true,true end''')

    def test_negative_registry_result_no_component_and_no_retry(self):
        self.case("start();assert(S.loads==1 and not S.comp and has('kind=NOT_LOADED'));key();show();flush();assert(S.loads==1)",r'''
        S.loads=0;S.objects[HOST]=nil
        LoadAsset=function()S.loads=S.loads+1;return nil,false,false end''')

    def test_found_but_load_failed_refuses_no_component(self):
        self.case("start();assert(S.loads==1 and not S.comp and has('found=true did_load=false'))",r'''
        S.loads=0;S.objects[HOST]=nil
        LoadAsset=function()S.loads=S.loads+1;return nil,true,false end''')

    def test_returned_object_missing_from_fresh_lookup_refuses(self):
        self.case("start();assert(not S.comp and has('loaded asset not live on fresh lookup'))",r'''
        local old=S.objects[HOST];S.objects[HOST]=nil
        LoadAsset=function()return old,true,true end''')

    def test_load_return_and_fresh_lookup_addresses_must_match(self):
        self.case("start();assert(not S.comp and has('lookup/load address mismatch'))",r'''
        local old=S.objects[HOST];S.objects[HOST]=nil
        LoadAsset=function(p)
         local fresh=make(p,'Class');set(fresh,'type',function()return 'UClass'end)
         S.objects[p]=fresh;return old,true,true
        end''')

    def test_both_resources_each_load_at_most_once_outside_script(self):
        self.case("start();show();flush();assert(S.hostloads==1 and S.matloads==1 and S.created==1)",r'''
        S.hostloads=0;S.matloads=0;local oldhost,oldmat=S.objects[HOST],S.objects[MASK]
        S.objects[HOST]=nil;S.objects[MASK]=nil
        LoadAsset=function(p)
         assert(S.game and not S.in_script and S.registered==2)
         local o;if p==HOST then S.hostloads=S.hostloads+1;o=oldhost
         else assert(p==MASK);S.matloads=S.matloads+1;o=oldmat end
         S.objects[p]=o;return o,true,true
        end''')

    def test_material_load_failure_refuses_without_component_allocation(self):
        self.case("start();assert(S.loads==1 and not S.comp and has('name=load_material edge=END') and has('kind=NOT_LOADED'))",r'''
        S.loads=0;S.objects[MASK]=nil
        LoadAsset=function(p)assert(p==MASK and not S.in_script);S.loads=S.loads+1;return nil,false,false end''')

    def test_target_replacement_during_load_refuses_before_component(self):
        self.case("start();assert(not S.comp and has('kind=IDENTITY_ERROR') and has('stage=after_refresh'))",r'''
        local old=S.objects[HOST];S.objects[HOST]=nil
        LoadAsset=function(p)set(P.actor,'id',9999);S.objects[p]=old;return old,true,true end''')

    def test_target_hidden_during_load_refuses_before_component(self):
        self.case("start();assert(not S.comp and has('no longer visible'))",r'''
        local old=S.objects[HOST];S.objects[HOST]=nil
        LoadAsset=function(p)set(P.widget,'Visibility',2);S.objects[p]=old;return old,true,true end''')

    def test_post_load_rechecks_original_tree_owner_widget_and_open_state(self):
        for mutation in [
            "set(P.widget,'WidgetTree',make('/New.Tree','/Script/UMG.WidgetTree'))",
            "set(P.component,'Widget',make('/Other.TipHUD',WIDGET))",
            "set(P.component,'GetOwner',function()return nil end)",
            "set(P.argument,'ActionName',26)",
        ]:
            with self.subTest(mutation=mutation):
                self.case("start();assert(not S.comp and has('FAILED') and has('stage=after_refresh'))",
                          "local old=S.objects[HOST];S.objects[HOST]=nil;LoadAsset=function(p)"+mutation+";S.objects[p]=old;return old,true,true end")

    def test_anchor_is_read_fresh_after_loading_without_changing_offset(self):
        self.case("start();assert(S.created==1 and S.comp.transform.position.X==11 and S.comp.transform.position.Z==62);assert(has('stage=after_refresh world_anchor=11,20,30'))",r'''
        local old=S.objects[HOST];S.objects[HOST]=nil
        LoadAsset=function(p)set(P.component,'x',11);S.objects[p]=old;return old,true,true end''')

    def test_load_reentry_keeps_one_match_and_does_not_allocate_in_callback(self):
        self.case("start();assert(S.created==1 and has('matches=')==false);key(7);assert(has('matches=1'))",r'''
        local old=S.objects[HOST];S.objects[HOST]=nil
        LoadAsset=function(p)show();begin();S.objects[p]=old;return old,true,true end''')

    def test_cancel_requested_during_load_prevents_allocation(self):
        self.case("start();assert(not S.comp and has('reason=user'))",r'''
        local old=S.objects[HOST];S.objects[HOST]=nil
        LoadAsset=function(p)S.keys[7]();S.objects[p]=old;return old,true,true end''')

    def test_expiry_during_load_prevents_allocation(self):
        self.case("start();assert(not S.comp and has('reason=timeout'))",r'''
        local old=S.objects[HOST];S.objects[HOST]=nil
        LoadAsset=function(p)S.now=S.now+121;S.objects[p]=old;return old,true,true end''')

if __name__=='__main__':unittest.main()
