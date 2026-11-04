# SPDX-License-Identifier: MPL-2.0
"""Execute the source-only Open-target arbiter. No UE4SS/host selection proof."""
import unittest

from test_ui_child import LuaRuntime, ROOT

SOURCE = (ROOT / "research/interaction-prompts-owner/world-space/auto-target/IIPTargetPolicy.lua").read_text(
    encoding="utf-8"
)
FIXTURE = r"""
P=(function()
""" + SOURCE + r"""
end)()
s=P.new(4)
function add(a)
    local ok,why=P.register(s,a,a..".ExtendedWidget",a..".TipHUD")
    assert(ok,why)
end
function row(a,shown,ready)
    return {actor=a,component=a..".ExtendedWidget",widget=a..".TipHUD",
        shown=shown,ready=ready}
end
function scan(...)
    local result,err=P.observe(s,{...})
    assert(result,err)
    return result
end
function act(kind)
    local a=P.next(s)
    assert(a.kind==kind,a.kind.." (expected "..kind..")")
    return a
end
"""

class AutoTargetPolicy(unittest.TestCase):
    def case(self, body):
        lua = LuaRuntime(unpack_returned_tuples=True)
        lua.execute(FIXTURE)
        lua.execute(body)

    def test_two_fresh_complete_snapshots_before_binding(self):
        self.case('''
add("A");add("B")
local a=scan(row("A",true,true),row("B",false,true))
assert(a.visible==1 and a.stable==1)
act("none")
a=scan(row("A",true,true),row("B",false,true))
assert(a.stable==2 and a.eligible=="A")
local cmd=act("bind")
assert(cmd.actor=="A" and cmd.ticket>0)
act("wait")
assert(P.bound(s,cmd.ticket))
act("none")
assert(P.status(s).active=="A")
''')

    def test_can_show_callback_is_not_visibility_proof(self):
        self.case('''
add("A")
local r=row("A",false,true);r.can_show=true
local a=scan(r)
assert(a.eligible==nil and a.reason=="no_native_prompt")
scan(r);act("none")
assert(P.status(s).active==nil)
''')

    def test_two_simultaneously_visible_are_ambiguous_and_release_existing(self):
        self.case('''
add("A");add("B")
scan(row("A",true,true),row("B",false,true))
scan(row("A",true,true),row("B",false,true))
local b=act("bind");P.bound(s,b.ticket)
local r=scan(row("A",true,true),row("B",true,true))
assert(r.reason=="ambiguous_native_prompts" and r.eligible==nil)
local x=act("release");assert(x.actor=="A")
act("wait");P.released(s,x.ticket)
act("none")
scan(row("A",false,true),row("B",true,true))
act("none")
scan(row("A",false,true),row("B",true,true))
local y=act("bind");assert(y.actor=="B")
''')

    def test_change_of_target_never_overlaps_two_owned_components(self):
        self.case('''
add("A");add("B")
scan(row("A",true,true),row("B",false,true))
scan(row("A",true,true),row("B",false,true))
local b=act("bind");P.bound(s,b.ticket)
scan(row("A",false,true),row("B",true,true))
local release=act("release");assert(release.actor=="A")
scan(row("A",false,true),row("B",true,true))
act("wait")
P.released(s,release.ticket)
act("none") -- Old B observation is invalidated after teardown.
scan(row("A",false,true),row("B",true,true))
scan(row("A",false,true),row("B",true,true))
local c=act("bind");assert(c.actor=="B" and c.ticket>release.ticket)
''')

    def test_not_ready_source_does_not_bind(self):
        self.case('''
add("A")
scan(row("A",true,false));scan(row("A",true,false))
act("none")
assert(P.status(s).reason=="native_hint_not_ready")
scan(row("A",true,true));act("none")
scan(row("A",true,true));act("bind")
''')

    def test_endplay_for_active_target_requires_release(self):
        self.case('''
add("A");scan(row("A",true,true));scan(row("A",true,true))
local b=act("bind");P.bound(s,b.ticket)
assert(P.end_actor(s,"A"))
assert(P.status(s).count==0)
local x=act("release");assert(x.actor=="A")
P.released(s,x.ticket);act("none")
assert(not P.end_actor(s,"A"))
''')

    def test_endplay_while_binding_forces_release_after_ack(self):
        self.case('''
add("A");scan(row("A",true,true));scan(row("A",true,true))
local b=act("bind")
assert(P.end_actor(s,"A"))
assert(not P.bound(s,b.ticket))
local x=act("release");assert(x.actor=="A")
P.released(s,x.ticket);act("none")
''')

    def test_map_change_invalidates_records_and_snapshot(self):
        self.case('''
add("A");scan(row("A",true,true));scan(row("A",true,true))
local b=act("bind");P.bound(s,b.ticket)
P.clear_world(s);assert(P.status(s).count==0)
local x=act("release");P.released(s,x.ticket)
act("none")
add("B");act("none")
scan(row("B",true,true));act("none")
scan(row("B",true,true));act("bind")
''')

    def test_alias_rebound_and_capacity_fail_closed(self):
        self.case('''
add("A")
local ok,why=P.register(s,"B","A.ExtendedWidget","B.TipHUD")
assert(ok==nil and why=="component_or_widget_alias")
assert(P.status(s).disabled)
act("disabled")
''')
        self.case('''
add("A")
local ok,why=P.register(s,"A","Changed.Component","A.TipHUD")
assert(ok==nil and why=="actor_rebound_without_endplay")
act("disabled")
''')
        self.case('''
for _,k in ipairs({"A","B","C","D"})do add(k)end
local ok,why=P.register(s,"E","E.ExtendedWidget","E.TipHUD")
assert(ok==nil and why=="candidate_capacity_exceeded")
act("disabled")
''')

    def test_incomplete_duplicate_and_stale_snapshot_fail_closed(self):
        self.case('''
add("A");add("B")
local ok,why=P.observe(s,{row("A",true,true)})
assert(ok==nil and why=="incomplete_visibility_snapshot")
act("disabled")
''')
        self.case('''
add("A");add("B")
local ok,why=P.observe(s,{row("A",true,true),row("A",true,true)})
assert(ok==nil and why=="invalid_visibility_snapshot")
act("disabled")
''')
        self.case('''
add("A")
local r=row("A",true,true);r.widget="foreign.Widget"
local ok,why=P.observe(s,{r})
assert(ok==nil and why=="stale_visibility_identity")
act("disabled")
''')

    def test_failure_with_active_target_cleans_before_disabling(self):
        self.case('''
add("A");scan(row("A",true,true));scan(row("A",true,true))
local b=act("bind");P.bound(s,b.ticket)
P.error(s,"unexpected_native_state")
local r=act("release");act("wait")
P.released(s,r.ticket)
local x=act("disabled");assert(x.reason=="unexpected_native_state")
''')

    def test_partial_creation_failure_requires_cleanup(self):
        self.case('''
add("A");scan(row("A",true,true));scan(row("A",true,true))
local b=act("bind")
local x=P.bind_failed(s,b.ticket,"native_create_failed")
assert(x.kind=="release" and x.actor=="A")
act("wait")
P.released(s,x.ticket)
act("disabled")
''')

    def test_wrong_ticket_refused_without_state_mutation(self):
        self.case('''
add("A");scan(row("A",true,true));scan(row("A",true,true))
local b=act("bind")
assert(not pcall(P.bound,s,b.ticket+1))
assert(P.status(s).pending and not P.status(s).active)
P.bound(s,b.ticket)
assert(not pcall(P.released,s,b.ticket))
assert(P.status(s).active=="A")
''')

    def test_idempotent_registration_and_distinct_actor_identity(self):
        self.case('''
add("A")
local ok,why=P.register(s,"A","A.ExtendedWidget","A.TipHUD")
assert(ok and why=="unchanged" and P.status(s).count==1)
assert(P.end_actor(s,"A"))
assert(P.register(s,"A","New.Component","New.Widget"))
assert(P.status(s).count==1)
''')

    def test_no_host_side_effects_or_frozen_candidate_change(self):
        self.case('''
assert(StaticFindObject==nil and RegisterHook==nil and RegisterBeginPlayPostHook==nil)
assert(StaticConstructObject==nil and ExecuteInGameThread==nil)
assert(P.status(s).count==0 and P.next(s).kind=="none")
''')

if __name__ == "__main__":
    unittest.main()
