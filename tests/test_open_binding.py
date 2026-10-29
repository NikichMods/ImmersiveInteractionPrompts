# SPDX-License-Identifier: MPL-2.0
"""Read-only event binding policy. Mocks do not prove native SetShow dispatch/pose."""
import unittest
from test_ui_child import LuaRuntime, ROOT

SOURCE=(ROOT/'research/interaction-prompts-owner/open-binding/Scripts/main.lua').read_text(encoding='utf8')
FIXTURE=r'''
S={now=1000,keys={},logs={},queue={},timers={},objects={},reads=0}
Key={F8=8,F7=7};ModifierKey={CONTROL=1,ALT=2};EngineTickAvailable=true;EGameThreadMethod={EngineTick=1}
os.time=function()return S.now end
print=function(s)S.logs[#S.logs+1]=s end
function has(s)for _,v in ipairs(S.logs)do if v:find(s,1,true)then return true end end return false end
local function api()assert(S.game,'engine access outside game context');S.reads=S.reads+1 end
local nextid=100
local function class(p,parent)
 return {IsValid=function()return true end,GetFullName=function()return 'Class '..p end,
  GetSuperStruct=function()return parent end}
end
local act=class('/Script/Engine.Actor')
local base=class('/Game/MainContent/Template/BaseBlueprint/BaseGameEventObject_BP.BaseGameEventObject_BP_C',act)
local function make(p,k,super)
 nextid=nextid+1;local o={p=p,k=k,id=nextid,live=true};S.objects[p]=o
 function o:IsValid()api();return self.live end
 function o:GetFullName()api();return self.k..' '..self.p end
 function o:GetAddress()api();return self.id end
 function o:GetClass()api();return class(self.k,super)end
 return o
end
local c=make('/World.Chest.ExtendedWidget','/Script/Genesis.ExtendedWidgetComponent');S.c=c
local a=make('/World.Chest','/Game/Test.Chest_C',base);S.actor=a
local w=make('/GameInstance.TipHUD','/Game/MainContent/Template/UMG/TipHUD.TipHUD_C');S.widget=w
local b=make('/GameInstance.TipHUD.TextBlock_89','/Script/UMG.TextBlock');S.text=b
local arg=make('/World.Chest.TipHUDArgument','/Script/Genesis.TipHUDArgumentComponent');S.arg=arg
local sender=make('/World.OtherActor','/Game/Test.Other_C',act);S.sender=sender
c.bVisible=true;c.bAddedToScreen=true;c.Widget=w;c.NewUserWidget=w;c.SenderActor=a;a.ExtendedWidget=c;a.TipHUDArgument=arg
w.TextBlock_89=b;w.Visibility=0;w.RenderOpacity=1;w.bIsEnabled=true;b.Visibility=0;b.RenderOpacity=1
b.Text={ToString=function()api();return S.text_value or 'Открыть'end}
arg.msgTag={ToString=function()api();return S.tag or 'Open'end};arg.ActionName=25
function c:GetWidget()api();return self.Widget end
function c:GetUserWidgetObject()api();return S.disagree and sender or self.Widget end
function c:GetOwner()api();return a end
function c:GetWidgetSpace()api();return 1 end
function arg:GetOwner()api();return a end
function c:K2_GetComponentLocation()api();return {X=S.x or 10,Y=20,Z=30}end
function c:K2_GetComponentRotation()api();return {Pitch=0,Yaw=90,Roll=0}end
function c:K2_GetComponentScale()api();return {X=1,Y=1,Z=1}end
function a:K2_GetActorLocation()api();return {X=10,Y=20,Z=0}end
local hook='/Script/Genesis.ExtendedWidgetComponent:SetShow'
local f={IsValid=function()api();return true end,type=function()return 'UFunction'end,
 GetFullName=function()return 'Function '..hook end,GetFunctionFlags=function()return S.script_flag and 0 or 1024 end}
function StaticFindObject(p)api();if p==hook then return f end return S.objects[p]end
function IsKeyBindRegistered()return false end
function RegisterKeyBind(k,m,fn)S.keys[k]=fn end
function RegisterHook(p,first,last)api();assert(p==hook and type(first)=='function' and type(last)=='function');S.hook=last;return 7,8 end
function UnregisterHook(p,first,last)api();assert(p==hook and first==7 and last==8);S.unregistered=(S.unregistered or 0)+1 end
function ExecuteInGameThread(fn,method)assert(method==1);S.queue[#S.queue+1]=fn end
function ExecuteInGameThreadWithDelay(ms,fn)api();assert(ms==60000);S.timers[#S.timers+1]=fn end
function flush()
 while #S.queue>0 do local q=S.queue;S.queue={};S.game=true;for _,fn in ipairs(q)do fn()end;S.game=false end
end
function key(k)S.keys[k or 8]();flush()end
function event(shown)
 assert(S.hook);S.game=true
 local r=S.hook({get=function()return c end},{get=function()return shown end},{},{})
 assert(r==nil,'native return override');S.game=false
end
function timer()S.game=true;S.timers[1]();S.game=false end
function unchanged()
 return a.ExtendedWidget==S.expected_extended and a.TipHUDArgument==arg and w.TextBlock_89==b
  and w.Visibility==0 and w.RenderOpacity==1 and b.Visibility==0 and b.RenderOpacity==1
end
'''

class OpenBindingPolicy(unittest.TestCase):
    def case(self,code,setup=''):
        lua=LuaRuntime(unpack_returned_tuples=True)
        lua.execute(FIXTURE);lua.execute(setup);lua.execute('S.expected_extended=S.actor.ExtendedWidget');lua.execute(SOURCE)
        try:lua.execute(code)
        except Exception:
            print(list(lua.globals().S.logs.values()));raise
        self.assertTrue(lua.eval('unchanged()'))

    def test_exact_event_reciprocal_binding_and_changed_pose(self):
        self.case('key();event(true);assert(not has("event=MATCH"));flush();assert(has("event=MATCH") and has("sender_is_owner=true"));'
                  'S.x=11;key();assert(has("changed=true"));key(7);assert(has("reason=user") and S.unregistered==1)')

    def test_no_event_is_negative_not_guessed_actor(self):
        self.case('key();timer();assert(not has("event=MATCH") and has("callbacks=0") and has("reason=timeout"))')

    def test_irrelevant_text_not_selected(self):
        self.case('key();event(true);flush();assert(not has("event=MATCH"));timer()',"S.text_value='Взять'")

    def test_pointer_and_backlink_contradictions_fail(self):
        for setup in ['S.disagree=true','S.actor.ExtendedWidget=S.sender','S.arg.ActionName=0','S.c.NewUserWidget=S.sender']:
            self.case('key();event(true);flush();assert(has("event=FAILED") and not has("event=MATCH") and S.unregistered==1)',setup)

    def test_sender_is_diagnostic_not_assumed_owner(self):
        self.case('key();event(true);flush();assert(has("event=MATCH") and has("sender_is_owner=false"))','S.c.SenderActor=S.sender')

    def test_manual_sample_detects_gone_or_rebound(self):
        for change,reason in [('S.c.live=false','component_gone'),('S.c.Widget=S.sender','widget_rebound_or_gone')]:
            # Both getter/storage paths agree for a rebound; it is not a guessed replacement target.
            self.case('key();event(true);flush();'+change+';key();assert(has("reason='+reason+'"))')

    def test_native_hide_and_late_queued_event_are_inert(self):
        self.case('key();S.keys[7]();event(true);flush();assert(not has("event=MATCH"));'
                  'local reads=S.reads;event(true);flush();assert(S.reads==reads)')
        self.case('key();event(true);flush();event(false);flush();assert(has("reason=native_hide"))')

    def test_callback_sample_and_time_bounds(self):
        self.case('key();for i=1,64 do event(false)end;flush();assert(has("reason=callback_budget"))')
        self.case('key();event(true);flush();for i=1,5 do key()end;assert(has("reason=sample_budget") and has("samples=6"))')
        self.case('key();event(true);S.now=1061;flush();assert(has("reason=timeout") and not has("event=MATCH"))')

    def test_missing_native_flag_stops_without_hook(self):
        self.case('key();assert(has("event=FAILED") and not S.hook)','S.script_flag=true')

if __name__=='__main__':unittest.main()
