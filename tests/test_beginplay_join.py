# SPDX-License-Identifier: MPL-2.0
"""Two-script read-only join policy. Not engine reload/dispatch/GC acceptance."""
import unittest
from test_ui_child import LuaRuntime, ROOT

SOURCE=(ROOT/'research/interaction-prompts-owner/open-binding/beginplay-probe/Scripts/main.lua').read_text(encoding='utf8')
FIXTURE=r'''
S={game=false,now=1000,objects={},fields={},hooks={},keys={},timers={},queue={},logs={},nextid=100,
 registered=0,released=0,pose_reads=0,context_reads=0,widget_reads=0}
BASE='/Game/MainContent/Template/BaseBlueprint/BaseGameEventObject_BP.BaseGameEventObject_BP_C'
WIDGET='/Game/MainContent/Template/UMG/TipHUD.TipHUD_C'
BEGIN=BASE..':ReceiveBeginPlay';SHOW=WIDGET..':CanShow'
Key={F8=8,F7=7};ModifierKey={CONTROL=1,ALT=2};EngineTickAvailable=true;EGameThreadMethod={EngineTick=1}
EObjectFlags={RF_ClassDefaultObject=16,RF_ArchetypeObject=32}
os.time=function()return S.now end
print=function(s)S.logs[#S.logs+1]=s end
function has(s)for _,v in ipairs(S.logs)do if v:find(s,1,true)then return true end end return false end
local function api()assert(S.game,'engine access outside game context')end
local function klass(p,parent)
 return {IsValid=function()api();return true end,GetFullName=function()api();return 'Class '..p end,
  GetSuperStruct=function()api();return parent end}
end
local actor_base=klass('/Script/Engine.Actor');local bp_base=klass(BASE,actor_base)
function make(p,k,parent)
 S.nextid=S.nextid+1
 local r={p=p,k=k,id=S.nextid,live=true};local o={}
 setmetatable(o,{__index=r,__newindex=function(_,key)error('GAME WRITE: '..key)end})
 S.fields[o]=r;S.objects[p]=o
 r.IsValid=function()api();return r.live end
 r.GetFullName=function()api();return r.k..' '..r.p end
 r.GetAddress=function()api();return r.id end
 r.GetClass=function()api();return klass(r.k,parent)end
 r.HasAnyFlags=function(_,mask)api();return ((r.flags or 0)&mask)~=0 end
 return o
end
function set(o,k,v)S.fields[o][k]=v end -- Test-world changes, never exposed by the source's API.
function pair(n,widget)
 local a=make('/World.Chest'..n,'/Game/Test.Chest_C',bp_base)
 local c=make(a.p..'.ExtendedWidget','/Script/Genesis.ExtendedWidgetComponent')
 local arg=make(a.p..'.TipHUDArgument','/Script/Genesis.TipHUDArgumentComponent')
 local w=widget or make('/GameInstance.TipHUD'..n,WIDGET)
 local b=widget and widget.TextBlock_89 or make(w.p..'.TextBlock_89','/Script/UMG.TextBlock')
 set(a,'ExtendedWidget',c);set(a,'TipHUDArgument',arg)
 set(c,'GetOwner',function()api();return a end);set(arg,'GetOwner',function()api();return a end)
 set(arg,'msgTag',{ToString=function()api();return arg.tag or 'Open'end});set(arg,'ActionName',25)
 set(c,'Widget',w);set(c,'NewUserWidget',w);set(c,'bVisible',true);set(c,'bAddedToScreen',true)
 set(c,'GetWidget',function()api();S.widget_reads=S.widget_reads+1;return c.Widget end)
 set(c,'GetUserWidgetObject',function()api();S.widget_reads=S.widget_reads+1;return c.Widget end)
 set(c,'GetWidgetSpace',function()api();return 1 end)
 set(c,'K2_GetComponentLocation',function()api();S.pose_reads=S.pose_reads+1;return {X=c.x or 10,Y=20,Z=30}end)
 set(c,'K2_GetComponentRotation',function()api();return {Pitch=0,Yaw=90,Roll=0}end)
 set(c,'K2_GetComponentScale',function()api();return {X=1,Y=1,Z=1}end)
 set(a,'K2_GetActorLocation',function()api();return {X=10,Y=20,Z=0}end)
 if not widget then
  set(w,'TextBlock_89',b);set(w,'Visibility',0);set(w,'RenderOpacity',1);set(w,'bIsEnabled',true)
  set(b,'Visibility',0);set(b,'RenderOpacity',1)
  set(b,'Text',{ToString=function()api();return b.value or 'Открыть'end})
 end
 return {actor=a,component=c,widget=w,text=b,argument=arg}
end
P=pair(1)
function metadata()
 for _,p in ipairs({BEGIN,SHOW})do
  local f=make(p,'Function');set(f,'type',function()return 'UFunction'end)
  set(f,'GetFunctionFlags',function()api();return S.native_flag and 1024 or 0 end)
 end
end
metadata()
function StaticFindObject(p)api();if S.metadata_missing and (p==BEGIN or p==SHOW)then return nil end;return S.objects[p]end
function RegisterHook(p,fn,...)
 api();assert(p==BEGIN or p==SHOW);assert(select('#',...)==0,'invented separate script post callback')
 if S.fail_second and p==SHOW then error('second registration failed')end
 S.registered=S.registered+1;local id=10+S.registered
 local other=S.bad_ids and id+1 or id
 S.hooks[p]={fn=fn,a=id,b=other};return id,other
end
function UnregisterHook(p,a,b)
 api();if S.unload or S.unregister_fail==p then error('metadata unavailable')end
 local h=assert(S.hooks[p]);assert(h.a==a and h.b==b,'wrong ownership');S.hooks[p]=nil;S.released=S.released+1
end
function IsKeyBindRegistered()return S.collision or false end
function RegisterKeyBind(k,mods,fn)S.keys[k]=fn end
function ExecuteInGameThread(fn,method)
 assert(method==1);if S.dispatch_fail then error('dispatch unavailable')end;S.queue[#S.queue+1]=fn
end
function ExecuteInGameThreadWithDelay(ms,fn)api();assert(ms==120000);S.timers[#S.timers+1]=fn end
function flush()
 while #S.queue>0 do local q=S.queue;S.queue={};S.game=true;for _,fn in ipairs(q)do fn()end;S.game=false end
end
function key(k)S.keys[k or 8]();flush()end
function emit(p,o,...)
 local h=S.hooks[p];if not h then return end
 S.game=true
 local returned=h.fn({get=function()S.context_reads=S.context_reads+1;return o end},...)
 assert(returned==nil,'RETURN OVERRIDE');S.game=false
end
function begin(p,...)emit(BEGIN,(p or P).actor,...)end
function show(p,...)emit(SHOW,(p or P).widget,...)end
function timer()S.game=true;S.timers[1]();S.game=false end
'''

class BeginPlayJoinPolicy(unittest.TestCase):
    def case(self,code,setup=''):
        lua=LuaRuntime(unpack_returned_tuples=True)
        lua.execute(FIXTURE);lua.execute(setup);lua.execute(SOURCE)
        try:lua.execute(code)
        except Exception:
            print(list(lua.globals().S.logs.values()));raise

    def test_two_post_script_hooks_exact_join_and_manual_pose(self):
        self.case('key();assert(S.registered==2);begin();assert(has("event=ACQUIRED") and S.pose_reads==0);'
                  'show();assert(has("event=MATCH") and has("event=POSE") and not S.hooks[BEGIN]);'
                  'show();assert(S.pose_reads==1);set(P.component,"x",11);key();assert(has("changed=true"));'
                  'key(7);assert(has("result=MATCHED") and S.released==2)')

    def test_registration_records_survive_mock_function_recreation(self):
        self.case('key();S.unload=true;set(S.objects[BEGIN],"live",false);set(S.objects[SHOW],"live",false);'
                  'metadata();S.unload=false;begin();key();show();assert(has("event=MATCH") and S.registered==2)')

    def test_no_beginplay_even_with_visible_open_is_distinct(self):
        self.case('key();show();timer();assert(has("result=NO_BEGINPLAY") and S.pose_reads==0)')

    def test_not_ready_has_no_automatic_retry(self):
        self.case('key();set(P.component,"Widget",nil);begin();local n=S.widget_reads;'
                  'set(P.component,"Widget",P.widget);begin();assert(S.widget_reads==n);'
                  'show();timer();assert(has("event=NOT_READY") and has("result=NO_READY_WIDGET") and S.pose_reads==0)')

    def test_no_open_no_visible_and_no_join_are_distinct(self):
        self.case('key();set(P.argument,"tag","Take");begin();timer();assert(has("result=NO_OPEN_CANDIDATE"))')
        self.case('key();begin();timer();assert(has("result=NO_CANSHOW"))')
        self.case('key();begin();set(P.text,"value","Взять");show();timer();assert(has("result=NO_VISIBLE_OPEN"))')
        self.case('key();begin();local other=pair(2);show(other);timer();assert(has("result=NO_MATCH") and S.pose_reads==0)')

    def test_partial_registration_failure_releases_first(self):
        self.case('key();assert(has("event=FAILED") and S.registered==1 and S.released==1 and not S.hooks[BEGIN])',
                  'S.fail_second=true')

    def test_missing_metadata_native_flag_and_bad_ids_fail_closed(self):
        for setup in ['S.metadata_missing=true','S.native_flag=true']:
            self.case('key();assert(has("event=FAILED") and S.registered==0)',setup)
        self.case('key();assert(has("event=FAILED") and S.released==1)','S.bad_ids=true')

    def test_cleanup_failure_is_inert_then_explicit_retry(self):
        self.case('key();S.unregister_fail=BEGIN;key(7);assert(not S.hooks[SHOW] and S.hooks[BEGIN]);'
                  'local n=S.context_reads;begin();assert(S.context_reads==n);'
                  'S.unregister_fail=nil;key(7);assert(not S.hooks[BEGIN] and S.released==2);'
                  'key();assert(S.registered==2)')

    def test_deadline_applies_after_blocking_load_before_context_read(self):
        self.case('key();S.now=1121;begin();assert(S.context_reads==0 and has("reason=timeout"))')
        self.case('key();S.now=1121;show();assert(S.context_reads==0 and has("reason=timeout"))')
        self.case('key();S.now=1121;key();assert(has("reason=timeout") and not has("event=CHECKPOINT"))')

    def test_exact_callback_and_candidate_caps(self):
        self.case('key();set(P.argument,"tag","Take");for i=1,128 do begin()end;'
                  'assert(has("event=ACQUISITION_CLOSED") and not S.hooks[BEGIN] and S.hooks[SHOW]);'
                  'show();key(7);assert(has("init=128") and has("result=NO_OPEN_CANDIDATE"))')
        self.case('key();for i=1,4096 do show()end;assert(has("reason=show_budget") and has("show=4096") and S.pose_reads==0)')
        self.case('key();for i=1,9 do begin(pair(i+10))end;assert(has("reason=candidate_budget") and has("ready=8"))')

    def test_four_pose_limit_does_not_autosample_or_rearm(self):
        self.case('key();begin();show();for i=1,3 do key()end;assert(S.pose_reads==4 and has("reason=pose_budget"));'
                  'key();timer();assert(S.registered==2 and S.pose_reads==4)')

    def test_reciprocal_identity_error_prevents_pose(self):
        self.case('key();begin();set(P.actor,"ExtendedWidget",nil);show();assert(has("kind=IDENTITY_ERROR") and S.pose_reads==0)')
        self.case('key();begin();set(P.component,"Widget",nil);show();assert(has("kind=IDENTITY_ERROR") and S.pose_reads==0)')

    def test_missing_or_replaced_cached_identity_is_not_retargeted(self):
        self.case('key();begin();S.objects[P.actor.p]=nil;show();assert(has("kind=IDENTITY_ERROR") and S.pose_reads==0)')
        self.case('key();begin();S.objects[P.actor.p]=make(P.actor.p,P.actor.k);show();'
                  'assert(has("kind=IDENTITY_ERROR") and S.pose_reads==0)')

    def test_ambiguous_widget_join_is_refused(self):
        self.case('key();begin();local other=pair(2,P.widget);begin(other);show();'
                  'assert(has("kind=IDENTITY_ERROR") and S.pose_reads==0)')

    def test_hidden_target_stops_without_ui_writes(self):
        self.case('key();begin();show();set(P.widget,"Visibility",2);show();'
                  'assert(has("reason=target_not_visible") and S.pose_reads==1)')

    def test_unexpected_callback_arguments_never_override(self):
        self.case('key();begin(nil,123);assert(has("kind=CONTRACT_ERROR") and S.pose_reads==0)')
        self.case('key();show(nil,123);assert(has("kind=CONTRACT_ERROR") and S.pose_reads==0)')

    def test_null_newwidget_allowed_but_other_widget_refused(self):
        self.case('key();set(P.component,"NewUserWidget",nil);begin();show();assert(has("event=MATCH"))')
        self.case('key();set(P.component,"NewUserWidget",pair(2).widget);begin();assert(has("kind=IDENTITY_ERROR"))')

    def test_dispatch_failure_leaves_callbacks_inert(self):
        self.case('key();S.dispatch_fail=true;key(7);local n=S.context_reads;begin();show();'
                  'assert(S.context_reads==n and has("event=DISPATCH_FAILED"));'
                  'S.dispatch_fail=false;key(7);assert(S.released==2)')

    def test_startup_collision_is_unavailable(self):
        self.case('assert(has("event=UNAVAILABLE") and S.registered==0)','S.collision=true')

    def test_default_and_archetype_objects_never_form_a_pair(self):
        self.case('key();set(P.actor,"flags",16);begin();assert(has("event=FAILED") and S.pose_reads==0)')
        self.case('key();set(P.component,"flags",32);begin();assert(has("kind=IDENTITY_ERROR") and S.pose_reads==0)')
        self.case('key();set(P.widget,"flags",16);begin();assert(has("kind=IDENTITY_ERROR") and S.pose_reads==0)')

    def test_nonfinite_pose_fails_without_emitting_a_snapshot(self):
        self.case('key();begin();set(P.component,"x",math.huge);show();'
                  'assert(has("event=MATCH") and not has("event=POSE") and has("kind=CONTRACT_ERROR"))')

    def test_cleanup_retry_preserves_original_identity_failure(self):
        self.case('key();begin();show();S.unregister_fail=SHOW;set(P.component,"Widget",nil);show();'
                  'assert(has("kind=IDENTITY_ERROR"));S.unregister_fail=nil;key(7);'
                  'assert(S.logs[#S.logs]:find("result=IDENTITY_ERROR",1,true))')

    def test_real_run_regression_three_pairs_survive_init_cutoff(self):
        self.case('key();begin();local two=pair(2);local three=pair(3);begin(two);begin(three);'
                  'local other=pair(99);set(other.argument,"tag","Take");for i=1,125 do begin(other)end;'
                  'assert(has("retained=3") and not S.hooks[BEGIN] and S.hooks[SHOW]);'
                  'local reads=S.context_reads;begin(other);assert(S.context_reads==reads);'
                  'show(two);assert(has("event=MATCH") and has("actor=\\"/World.Chest2\\"") and S.pose_reads==1);'
                  'key(7);assert(has("result=MATCHED") and has("init=128"))')

    def test_closed_acquisition_stays_inert_if_unregistration_pending(self):
        self.case('key();begin();S.unregister_fail=BEGIN;for i=1,127 do begin()end;'
                  'local reads=S.context_reads;for i=1,20 do begin()end;assert(S.context_reads==reads);'
                  'show();assert(has("event=MATCH") and S.pose_reads==1);S.unregister_fail=nil;'
                  'key(7);assert(S.released==2 and has("init=128"))')

    def test_init_close_does_not_extend_deadline_or_pose_cap(self):
        self.case('key();begin();for i=1,127 do begin()end;S.now=1121;show();'
                  'assert(has("reason=timeout") and S.pose_reads==0)')
        self.case('key();begin();for i=1,127 do begin()end;show();for i=1,3 do key()end;'
                  'assert(S.pose_reads==4 and has("reason=pose_budget"))')

if __name__=='__main__':unittest.main()
