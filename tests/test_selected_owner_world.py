# SPDX-License-Identifier: MPL-2.0
"""Selected-owner pump and pinned World renderer on controlled Lua hosts."""
import hashlib
import json
import re
import unittest

from test_ui_child import LuaRuntime, ROOT
import test_committed_owner_observer as observer
import test_resident_host_real_modules as host

BASE = ROOT / "research/interaction-prompts-owner/world-space/selected-owner-world"
SCRIPTS = {p.stem: p.read_text(encoding="utf-8") for p in (BASE / "Scripts").glob("*.lua")}
SESSION = SCRIPTS["IIPSelectedWorldSession"]
MOCK = """
A={action="Open",key="Open|1"};B={action="Take",key="Take|2"}
C={action="Check",key="Check|3"};D={action="Other",key="Other|4"}
S={creates=0,hides=0,resumes=0,releases=0,events={},visible=true}
api={
 read=function()
   if S.bad_read then error("stale native identity") end
   if S.gap then return {status="GAP"} end
   return {status="READY",actor=S.selected,key=S.selected and S.selected.key,
      pawn_key="pawn",component_key=S.component or "component"}
 end,
 loop=function(n,fn) assert(n==1);tick=fn;return 1 end,
 cancel=function(h) assert(h==1);S.cancelled=true;return true end,
}
source={
 matches_action=function(a,action)return a.action==action end,
 acquire=function(a)
   if a~=D then return {actor=a.key,action=a.action,refs={actor=a}} end
 end,
 snapshot=function()return {shown=S.visible,ready=S.visible}end,
 resolve_actor=function(id)return not S.gone and id.ref or nil end,
}
world={
 empty=function()return S.held==nil end,
 prepare=function()end,refresh_assets=function()end,
 create=function(a,c,w,stop,action,validate)
   if S.before_create then S.before_create() end
   if not validate() then return false end
   assert(not S.held,"duplicate component")
   S.creates=S.creates+1; S.held=action
   if S.bad_create then error("partial create") end
 end,
 hide=function()S.hides=S.hides+1;return true end,
 cleanup=function()
   S.releases=S.releases+1
   if S.bad_cleanup then return false end
   S.held=nil
   if S.after_cleanup then S.after_cleanup() end
   return true
 end,
 resume=function()S.resumes=S.resumes+1;return true end,
 refresh=function()return true end,
}
o=Session.start(world,source,function(r)return r.action,{},{}end,api,
 function(e)S.events[#S.events+1]=e end)
function select_owner(a)S.selected=a;tick()end
"""


class SelectedOwnerWorld(unittest.TestCase):
    def case(self, lua):
        vm = LuaRuntime(unpack_returned_tuples=True)
        vm.execute("Session=(function()\n" + SESSION + "\nend)()")
        vm.execute(MOCK + lua)

    def test_three_actions_via_none_and_same_owner_reuse(self):
        self.case("""
select_owner(A);select_owner(nil);select_owner(A)
assert(S.creates==1 and S.hides==1 and S.resumes==2)
select_owner(nil);select_owner(B);select_owner(nil);select_owner(C);select_owner(nil)
assert(S.creates==3 and S.releases==2 and S.held=="Check")
""")

    def test_direct_switch_and_new_selection_during_cleanup(self):
        self.case("""
select_owner(A);select_owner(B)
assert(S.held=="Take" and S.events[#S.events-1]=="RELEASED" and S.events[#S.events]=="BOUND")
S.after_cleanup=function()S.selected=A end
select_owner(C)
assert(S.held=="Open" and S.creates==3 and S.releases==2)
""")

    def test_last_guard_rejects_target_changed_inside_create(self):
        self.case("""
S.before_create=function()S.selected=B end
select_owner(A);assert(S.creates==0)
S.before_create=nil;tick();assert(S.held=="Take")
""")

    def test_gap_context_replacement_map_and_endplay(self):
        self.case("""
select_owner(A)
S.gap=true;tick();assert(not S.held)
S.gap=false;tick();assert(S.held=="Open")
S.component="second";tick();assert(S.creates==3)
o.invalidate("map_pre");assert(S.held);tick();assert(not S.held)
tick();o.ended(1);assert(S.held);tick();tick();assert(not S.held)
select_owner(B);assert(S.held=="Take")
""")

    def test_pending_unsupported_and_no_session_timeout(self):
        self.case("""
S.visible=false;select_owner(A);assert(S.creates==0)
S.visible=true;select_owner(D);assert(S.creates==0)
for i=1,10000 do tick()end
select_owner(C);assert(S.held=="Check" and not S.cancelled)
C.action="Other";tick();assert(not S.held)
""")

    def test_stale_and_gone_actor(self):
        self.case("""
select_owner(A);S.gone=true;select_owner(nil);assert(not S.held)
S.bad_read=true;select_owner(B);assert(S.cancelled and S.creates==1)
""")

    def test_partial_create_and_failed_release(self):
        self.case("""
S.bad_create=true;S.bad_cleanup=true;select_owner(A)
assert(S.cancelled and S.releases==1 and S.creates==1)
select_owner(B);assert(S.creates==1 and S.releases==1)
""")
        self.case("""
select_owner(A);S.bad_cleanup=true;select_owner(B)
assert(S.cancelled and S.releases==1 and S.creates==1)
""")

    def test_entrypoint_capture_map_gap_and_no_scan(self):
        vm = LuaRuntime(unpack_returned_tuples=True)
        vm.execute(observer.ENTRY_RIG)
        vm.execute('package.preload.IIPSelectedWorldSession=function()\n' + SESSION + '\nend')
        vm.execute("""
FindAllOf=function()error("forbidden")end
ForEachUObject=FindAllOf
package.preload.IIPWorldChild=function()return {empty=function()return true end}end
package.preload.IIPWorldTarget=function()return {new=function()return function()end end}end
""")
        vm.execute(SCRIPTS["main"])
        vm.execute("""
R.cb.tick();assert(not has("CONTROLLER_ACQUIRED"))
begin_actor(K);assert(has("CONTROLLER_ACQUIRED"))
R.cb.tick();assert(not R.cancelled)
R.cb.map();R.cb.tick();assert(not R.cancelled)
""")

    def test_real_world_guard_and_one_host_recovery(self):
        vm = LuaRuntime(unpack_returned_tuples=True)
        vm.execute(host.FIXTURE + host.EXTRA + host.CONTEXT + host.ORIENTATION
                   + host.FRAMES + host.HINT_FIXTURE + host.LIVE + host.MEASURED + host.STYLE)
        for name, body in SCRIPTS.items():
            if name != "main":
                vm.execute(f'package.preload["{name}"]=function()\n'
                           + (host.RESOURCES if name == "IIPResources" else body) + '\nend')
        vm.execute(host.SETUP + """
local function create(guard)
 return World.create(P.actor,P.component,P.widget,function()end,"Open",guard)
end
World.prepare();World.refresh_assets()
assert(create(function()return false end)==false and World.empty())
create(function()return true end)
set(P.text,"Visibility",0);set(P.text,"RenderOpacity",1);set(P.text,"bIsEnabled",true)
assert(S.created==1 and World.resume())
set(P.text,"value","Native localized action")
S.device=4
for i=1,4 do assert(World.refresh())end
assert(S.lower:GetText():ToString()=="Native localized action",table.concat(S.logs," | "))
assert(has("event=SOURCE_BOUND") and has("device=4"))
set(P.component,"bAddedToScreen",false)
assert(World.refresh() and S.host.Visibility==1)
set(P.component,"bAddedToScreen",true)
for i=1,4 do assert(World.refresh())end
assert(S.created==1 and has("event=RESUMING"))
assert(World.cleanup("done"))
local host_class=S.objects[HOST]
S.objects[HOST]=nil
local loads=0
function LoadAsset(p)assert(p==HOST);loads=loads+1;S.objects[p]=host_class;return host_class,true,true end
create(function()return true end)
assert(S.created==2 and loads==1 and World.cleanup("done"))
S.objects[HOST]=nil
assert(not pcall(create,function()return true end))
assert(S.created==2 and loads==1 and World.empty())
""")

    def test_manifest_and_closed_module_set(self):
        manifest = json.loads((BASE / "SOURCE_MANIFEST.json").read_text(encoding="utf-8"))
        paths = {p.relative_to(BASE).as_posix(): p for p in (BASE / "Scripts").glob("*.lua")}
        self.assertEqual(set(manifest["files"]), set(paths))
        for name, path in paths.items():
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), manifest["files"][name])
        imports = set(re.findall(r'require\("([^"]+)"\)', "\n".join(SCRIPTS.values())))
        self.assertFalse(imports - set(SCRIPTS) - {"IIPLiveConfig"})
        self.assertNotRegex("\n".join(SCRIPTS.values()), r"\b(?:FindAllOf|ForEachUObject|FindObjects)\s*\(")


if __name__ == "__main__":
    unittest.main()
