# SPDX-License-Identifier: MPL-2.0
"""Exact-slot selected-owner observer: Lua state machine and entrypoint mocks.

These mocks verify read-only scope, not the installed Genesis/UE4SS ABI or pixels.
"""
import unittest
from test_ui_child import LuaRuntime, ROOT

BASE = ROOT / "research/interaction-prompts-owner/world-space/committed-owner-observer/Scripts"
OBSERVER = (BASE / "IIPSelectedOwnerObserver.lua").read_text(encoding="utf-8")
ENTRY = (BASE / "main.lua").read_text(encoding="utf-8")
RIG = r"""
S={cb={},logs={},owners={},visible={},reads=0,snapshots=0,cancelled=0,
   pawn="pawn1",component="component1",selected=nil}
A={key="A",action="Open",ready=true}
B={key="B",action="Take",ready=true}
C={key="C",action="Check",ready=true}
D={key="D",action="Other",ready=true}
Source={
 acquire=function(a)
  if not a then return nil,"unrelated_actor" end
  if a.action=="Other" then return nil,"other_action" end
  if not a.ready then return nil,"not_ready_widget" end
  return {actor=a.key,component="component_"..a.key,
    widget="widget_"..a.key,action=a.action},"ready"
 end,
 snapshot=function(rec,alive,visible)
  S.snapshots=S.snapshots+1
  if S.gone==rec.actor then return nil,"object_gone" end
  local show=S.visible[rec.actor]==true
  return {actor=rec.actor,shown=show,ready=show}
 end,
}
api={
 read=function()
  S.reads=S.reads+1
  if S.boom then error("read failed") end
  if S.gap then return {status="GAP",reason="no_pawn"} end
  return {status="READY",pawn_key=S.pawn,component_key=S.component,
          actor=S.selected,key=S.selected and S.selected.key or nil}
 end,
 map_pre=function(fn) S.cb.map=fn end,
 loop=function(frames,fn) assert(frames==1);S.cb.tick=fn;return 71 end,
 cancel=function(h) assert(h==71);S.cancelled=S.cancelled+1;return true end,
 native_alive=function()return true end,
 hint_visible=function()return true end
}
o=Observer.start(api,Source,function(ev,fields)
 S.logs[#S.logs+1]=ev.." "..fields
end)
function tick(n)for i=1,(n or 1) do S.cb.tick() end end
function has(fragment)
 for _,line in ipairs(S.logs) do
  if line:find(fragment,1,true) then return true end
 end
 return false
end
"""

ENTRY_RIG = r"""
R={logs={},selected=nil,controller_resolves=0,component_lookups=0,
    writes=0,registered=0,loops=0,cb={},addr=2000}
function object(kind,path,clazz)
 R.addr=R.addr+1
 local o={kind=kind,path=path,addr=R.addr,clazz=clazz,live=true}
 function o:IsValid()return self.live end
 function o:GetAddress()return self.addr end
 function o:GetFullName()return self.kind.." "..self.path end
 function o:GetClass()return self.clazz end
 function o:type()return self.kind end
 return o
end
local function class(path)
 local c=object("Class",path,nil)
 c.clazz=c
 function c:GetSuperStruct()return nil end
 return c
end
local component_class=class("/Script/Genesis.PlayerActionComponent")
function component_class:type()return "UClass" end
local pawn_class=class("/Script/Genesis.GenesisCharacter")
local kismet_class=class("/Script/Engine.KismetSystemLibrary")
local owner_class=class("/Game/Objects.BaseGameEventObject_BP_C")
local controller_class=class("/Script/Engine.PlayerController")
local cdo=object("Object","/Script/Engine.Default__KismetSystemLibrary",kismet_class)
local f=object("Function","/Script/Engine.KismetSystemLibrary:IsValid",nil)
function f:type()return "UFunction" end
setmetatable(f,{__call=function(_,_,v)return v:IsValid()end})
P=object("GenesisCharacter","/Game/Pawn1",pawn_class)
C=object("PlayerActionComponent","/Game/Pawn1.Component",component_class)
function C:GetOwner()return P end
function P:GetComponentByClass(clazz)
 R.component_lookups=R.component_lookups+1
 assert(clazz==component_class,"wrong component class")
 return C
end
K=object("PlayerController","/Game/Controller",controller_class)
K.Pawn=P
function K:IsLocalPlayerController() return R.controller_is_local~=false end
A=object("Actor","/Game/Interact_A",owner_class)
A.action="Open"
A.key="/Game/Interact_A|/Game/Objects.BaseGameEventObject_BP_C|"..tostring(A.addr)
local weak={Get=function()return R.selected end}
setmetatable(C,{__index=function(_,k)
 if k=="IIPResearchCommittedTipOwner_83330635" then
  assert(R.registered==1,"unregistered custom field");return weak
 end
 error("unrecognized read "..tostring(k))
end,__newindex=function()R.writes=R.writes+1;error("native write")end})
function StaticFindObject(path)
 if path=="/Script/Genesis.PlayerActionComponent" then return component_class end
 if path=="/Script/Engine.KismetSystemLibrary:IsValid" then return f end
 if path=="/Script/Engine.Default__KismetSystemLibrary" then return cdo end
 if path==K.path then
  R.controller_resolves=R.controller_resolves+1;return K
 end
 return nil
end
function RegisterCustomProperty(t)
 assert(t.Name=="IIPResearchCommittedTipOwner_83330635")
 assert(t.Type==PropertyTypes.WeakObjectProperty and
        t.BelongsToClass=="/Script/Genesis.PlayerActionComponent" and
        t.OffsetInternal==0x410)
 R.registered=R.registered+1
end
PropertyTypes={WeakObjectProperty={Size=8,Name="WeakObjectProperty"}}
EngineTickAvailable=true
function LoopInGameThreadAfterFrames(frames,fn)
 assert(frames==1);R.loops=R.loops+1;R.cb.tick=fn;return 71
end
function RegisterLoadMapPreHook(fn) R.cb.map=fn end
function RegisterBeginPlayPostHook(fn) R.cb.begin=fn end
function RegisterEndPlayPreHook(fn) R.cb.finish=fn end
function begin_actor(actor)
 R.cb.begin({get=function()return actor end})
end
function finish_actor(actor)
 R.cb.finish({get=function()return actor end})
end
function CancelDelayedAction(h)assert(h==71);R.cancelled=true;return true end
print=function(t)R.logs[#R.logs+1]=t end
package.preload["IIPInteractionSource"]=function()
 return {acquire=function(a)
  return {actor=a.key,component="comp_A",widget="widget_A",action=a.action}
 end,snapshot=function(rec)
  return {actor=rec.actor,shown=R.visible==true,ready=R.visible==true}
 end}
end
package.preload["IIPOpenVisibility"]=function()
 return {visible=function()return true end}
end
function has(fragment)
 for _,line in ipairs(R.logs)do
  if line:find(fragment,1,true)then return true end
 end
 return false
end
"""

class CommittedOwnerObserver(unittest.TestCase):
    def case(self, source):
        lua=LuaRuntime(unpack_returned_tuples=True)
        lua.execute("Observer=(function()\n"+OBSERVER+"\nend)()")
        lua.execute(RIG)
        lua.execute(source)

    def test_open_take_direct_switch_leave_and_visibility_match(self):
        self.case(r"""
tick(3)
S.selected=A;S.visible.A=true;tick(2)
S.selected=B;S.visible.A=false;S.visible.B=true;tick(2)
S.selected=nil;S.visible.B=false;tick(2)
assert(o.status().matched==3 and o.status().no_match==0)
assert(o.status().transitions==3)
assert(has("from=A to=B") and has("from=B to=NONE"))
assert(has("CORRELATED seq=2") and has("complete_scope=true"))
local n=S.snapshots
tick(50)
assert(S.snapshots==n and S.reads==59)
assert(S.cancelled==0)
""")

    def test_no_false_match_when_native_visibility_disagrees(self):
        self.case(r"""
S.selected=A;tick(13)
assert(o.status().matched==0 and o.status().no_match==1)
assert(has("NO_MATCH seq=1") and has("new_shown=false"))
""")

    def test_missing_owner_widget_retries_only_selected_actor(self):
        self.case(r"""
A.ready=false;S.selected=A;S.visible.A=true;tick()
assert(o.status().pending==1 and o.status().matched==0)
tick(2);A.ready=true;tick(2)
assert(o.status().matched==1 and o.status().pending==0)
S.selected=nil;S.visible.A=false;tick(2)
assert(o.status().matched==2)
""")

    def test_context_loss_does_not_claim_hide_to_null(self):
        self.case(r"""
S.selected=A;S.visible.A=true;tick(2)
S.gap=true;tick()
assert(o.status().gaps==1 and o.status().pending==0)
assert(has("hide_to_null_not_claimed=true"))
S.gap=false;S.pawn="pawn2";S.component="component2"
S.selected=B;S.visible.B=true;tick(2)
assert(o.status().matched==2)
assert(has("CONTEXT pawn_component_verified=true"))
""")

    def test_component_replacement_resets_old_correlation(self):
        self.case(r"""
S.selected=A;S.visible.A=true;tick(2)
S.component="component2";S.selected=B;S.visible.B=true;tick(2)
assert(o.status().matched==2)
assert(o.status().transitions==2)
assert(has("CONTEXT_REPLACED"))
""")

    def test_other_interaction_not_misreported_as_open_take_check(self):
        self.case(r"""
S.selected=D;tick(2)
assert(o.status().matched==0 and o.status().snapshots==0)
S.selected=A;S.visible.A=true;tick(2)
assert(o.status().matched==1)
assert(has("supported=false acquisition=other_action"))
""")

    def test_switch_into_unsupported_owner_is_partial_not_full_match(self):
        self.case(r"""
S.selected=A;S.visible.A=true;tick(2)
S.selected=D;S.visible.A=false;tick(2)
assert(o.status().matched==1 and o.status().unresolved==1)
assert(has("PARTIAL_CORRELATION seq=2"))
assert(has("no_full_owner_claim=true"))
assert(not has("CORRELATED seq=2"))
""")

    def test_map_stop_and_read_failure_are_inert(self):
        self.case(r"""
S.selected=A;tick();S.cb.map()
assert(o.status().pending==0 and has("MAP_RESET"))
o.stop("manual")
local n=S.reads
tick(100)
assert(S.reads==n and S.cancelled==1 and has("native_writes=0"))
""")
        self.case(r"""
S.boom=true;tick()
assert(not o.status().active and S.cancelled==1)
assert(has("read failed") and has("STOP"))
""")

    def test_no_arbitrary_duration_or_full_owner_scan(self):
        self.case(r"""
tick(1100)
assert(o.status().active and S.cancelled==0)
assert(o.status().snapshots==0 and o.status().samples==1100)
""")

    def entry(self,body,setup=""):
        lua=LuaRuntime(unpack_returned_tuples=True)
        lua.execute("Observer=(function()\n"+OBSERVER+"\nend)()")
        lua.execute(ENTRY_RIG)
        lua.execute('package.preload["IIPSelectedOwnerObserver"]=function() return Observer end')
        lua.execute(setup)
        lua.execute(ENTRY)
        lua.execute(body)

    def test_entrypoint_reads_exact_component_and_weak_slot_only(self):
        self.entry(r"""
assert(R.registered==1 and R.cb.tick and R.cb.map and R.cb.begin and R.cb.finish)
assert(R.writes==0)
R.cb.tick();assert(R.controller_resolves==0 and R.component_lookups==0)
begin_actor(K)
assert(has("CONTROLLER_ACQUIRED") and has("CONTROLLER_PENDING"))
R.selected=A;R.visible=true;R.cb.tick();R.cb.tick()
assert(has("CORRELATED") and has("from=NONE"))
R.selected=nil;R.visible=false;R.cb.tick();R.cb.tick()
assert(has("from="..A.key.." to=NONE"))
assert(R.component_lookups==4 and R.controller_resolves==4)
assert(R.writes==0)
""")

    def test_entrypoint_rejects_unknown_weak_layout_without_registering(self):
        self.entry(r"""
assert(R.registered==0 and R.cb.tick==nil)
assert(has("UNAVAILABLE") and has("no_selected_owner_coverage=true"))
""","PropertyTypes.WeakObjectProperty.Size=16")

    def test_entrypoint_missing_beginplay_has_no_class_search_or_coverage(self):
        self.entry(r"""
assert(R.registered==1 and R.cb.begin and R.cb.finish)
assert(has("CONTROLLER_PENDING"))
FindAllOf=function()error("forbidden global enumeration")end
for i=1,500 do R.cb.tick() end
assert(R.controller_resolves==0 and R.component_lookups==0 and
       R.registered==1 and R.writes==0)
assert(not has("CONTROLLER_ACQUIRED"))
assert(not has("CORRELATED"))
""")

    def test_entrypoint_filters_nonlocal_and_unrelated_beginplay(self):
        self.entry(r"""
begin_actor(A)
R.controller_is_local=false;begin_actor(K)
R.cb.tick()
assert(R.controller_resolves==0 and R.component_lookups==0)
R.controller_is_local=true;begin_actor(K)
R.selected=A;R.visible=true;R.cb.tick();R.cb.tick()
assert(has("CONTROLLER_ACQUIRED") and has("CORRELATED"))
assert(R.controller_resolves==2 and R.writes==0)
""")

    def test_entrypoint_controller_end_and_map_reset_are_gaps_not_hides(self):
        self.entry(r"""
begin_actor(K);R.selected=A;R.visible=true
R.cb.tick();R.cb.tick()
assert(has("CORRELATED"))
finish_actor(K);R.cb.tick()
assert(has("CONTROLLER_END") and R.controller_resolves==2)
begin_actor(K);R.cb.tick()
assert(R.controller_resolves==3)
R.cb.map();R.cb.tick()
assert(has("CONTROLLER_RESET") and R.controller_resolves==3)
assert(R.writes==0)
""")

    def test_entrypoint_changed_cached_controller_identity_fails_closed(self):
        self.entry(r"""
begin_actor(K)
K.addr=K.addr+1
R.cb.tick()
assert(R.cancelled and has("identity mismatch") and R.writes==0)
""")

    def test_entrypoint_rejects_component_identity_change(self):
        self.entry(r"""
C.GetOwner=function()return nil end
begin_actor(K);R.selected=A;R.cb.tick()
assert(R.cancelled and has("ownership/class mismatch"))
assert(R.writes==0)
""")

if __name__=="__main__":
    unittest.main()
