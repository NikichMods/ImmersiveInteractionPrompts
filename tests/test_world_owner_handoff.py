# SPDX-License-Identifier: MPL-2.0
"""Actual Lua ownership FSM against a stateful fake renderer, not UE4 runtime proof."""
import unittest

from test_ui_child import LuaRuntime, ROOT

PATH=ROOT/"research/interaction-prompts-owner/world-space/owner-handoff/IIPWorldHandoff.lua"
SOURCE=PATH.read_text(encoding="utf-8")
RIG=r"""
R={owned=false,visible=false,created=0,cleaned=0,calls={},fail_create=false,
   fail_cleanup=false,dirty_after_cleanup=false,fail_hide=false,fail_resume=false}
function log(s)R.calls[#R.calls+1]=s end
local renderer={
 empty=function()return not R.owned end,
 create=function(owner,ticket)
    log("create:"..owner.actor..":"..ticket)
    if R.owned then error("DOUBLE ALLOCATION") end
    R.owned=true;R.visible=false;R.created=R.created+1
    if R.fail_create then error("partial creation") end
    return true
 end,
 hide=function()
    log("hide")
    if R.fail_hide then error("cannot hide") end
    assert(R.owned);R.visible=false;return true
 end,
 resume=function()
    log("resume")
    if R.fail_resume then error("cannot resume") end
    assert(R.owned);R.visible=true;return true
 end,
 refresh=function()
    log("refresh");assert(R.owned and R.visible);return true
 end,
 cleanup=function(reason,ticket)
    log("cleanup:"..reason..":"..ticket)
    assert(R.owned)
    if R.fail_cleanup then return false end
    if not R.dirty_after_cleanup then R.owned=false end
    R.visible=false;R.cleaned=R.cleaned+1
    return true
 end,
}
LOG={}
H=Handoff.new(renderer,function(e,msg)
 LOG[#LOG+1]=e.." "..msg
end)
function has(s)
 for _,x in ipairs(LOG)do if x:find(s,1,true)then return true end end
 return false
end
function rec(a,action)
 return {actor=a,component=a..".Component",widget=a..".Widget",action=action or "Open"}
end
function row(a,shown,ready,action)
 local r=rec(a,action);r.shown=shown;r.ready=ready==nil and true or ready;return r
end
function scan(...)
 return assert(H.observe({...},true))
end
function register(a,action)
 local ok,why=H.register(rec(a,action))
 assert(ok,why)
end
function bound(a,action)
 register(a,action)
 scan(row(a,true,true,action));assert(H.pump()=="no_target")
 scan(row(a,true,true,action));assert(H.pump()=="bound_hidden")
 assert(R.owned and R.created==1)
 assert(H.pump()=="resumed")
 assert(R.visible and H.status().selected==a)
end
function none(...)
 scan(...);return H.pump()
end
"""

class WorldOwnerHandoff(unittest.TestCase):
    def case(self,body):
        lua=LuaRuntime(unpack_returned_tuples=True)
        lua.execute("Handoff=(function()\n"+SOURCE+"\nend)()")
        lua.execute(RIG)
        lua.execute(body)

    def test_stable_two_samples_before_first_bind_and_no_early_show(self):
        self.case(r"""
register("A")
scan(row("A",true));assert(H.pump()=="no_target")
assert(not R.owned)
scan(row("A",true));assert(H.pump()=="bound_hidden")
assert(R.owned and not R.visible)
assert(H.pump()=="resumed")
assert(H.pump()=="refreshed")
assert(R.created==1 and R.cleaned==0)
""")

    def test_same_owner_hide_resume_preserves_native_allocation_without_timeout(self):
        self.case(r"""
bound("A")
for i=1,600 do
 scan(row("A",false));assert(H.pump()=="hidden" or H.pump()=="retained_hidden")
 scan(row("A",false));assert(H.pump()=="retained_hidden")
 scan(row("A",true));assert(H.pump()=="retained_hidden")
 scan(row("A",true));assert(H.pump()=="resumed")
end
assert(R.created==1 and R.cleaned==0 and H.status().phase=="shown")
assert(H.status().epoch>2000)
""")

    def test_a_none_b_requires_cleaned_and_two_post_cleanup_snapshots(self):
        self.case(r"""
register("A");register("B")
scan(row("A",true),row("B",false));scan(row("A",true),row("B",false))
assert(H.pump()=="bound_hidden");assert(H.pump()=="resumed")
scan(row("A",false),row("B",false));assert(H.pump()=="hidden")
scan(row("A",false),row("B",true));assert(H.pump()=="retained_hidden")
scan(row("A",false),row("B",true))
assert(H.pump()=="cleaned" and not R.owned)
assert(has("CLEANED ticket=") and has("RELEASED ticket="))
assert(H.pump()=="no_target")
-- Old B snapshot cannot create a new component after cleanup.
scan(row("A",false),row("B",true));assert(H.pump()=="no_target")
scan(row("A",false),row("B",true));assert(H.pump()=="bound_hidden")
assert(H.pump()=="resumed")
assert(R.created==2 and R.cleaned==1 and R.visible)
""")

    def test_b_none_a_and_direct_a_to_b_never_overlap(self):
        self.case(r"""
register("A");register("B")
scan(row("A",false),row("B",true));scan(row("A",false),row("B",true))
assert(H.pump()=="bound_hidden");assert(H.pump()=="resumed")
scan(row("A",true),row("B",false))
assert(H.pump()=="hidden")
scan(row("A",true),row("B",false))
assert(H.pump()=="cleaned")
scan(row("A",true),row("B",false))
assert(H.pump()=="no_target")
scan(row("A",true),row("B",false))
assert(H.pump()=="bound_hidden");assert(H.pump()=="resumed")
assert(R.created==2 and R.cleaned==1)
""")

    def test_ambiguous_multiple_native_prompts_never_selects_guess(self):
        self.case(r"""
register("A");register("B")
scan(row("A",true),row("B",true));scan(row("A",true),row("B",true))
assert(H.pump()=="no_target" and H.status().reason=="ambiguous_native_prompts")
scan(row("A",true),row("B",false));scan(row("A",true),row("B",false))
assert(H.pump()=="bound_hidden");assert(H.pump()=="resumed")
scan(row("A",true),row("B",true))
assert(H.pump()=="hidden")
assert(R.owned and R.cleaned==0)
""")

    def test_incomplete_rotating_sweeps_hide_but_never_bind(self):
        self.case(r"""
bound("A")
for i=1,500 do
 H.observe({row("A",true)},false)
 assert(H.pump()=="hidden" or H.pump()=="retained_hidden")
end
assert(R.owned and R.created==1 and R.cleaned==0)
assert(H.status().reason=="incomplete_snapshot")
""")

    def test_endplay_of_selected_owner_requires_teardown(self):
        self.case(r"""
bound("A")
assert(H.end_actor("A"))
assert(H.pump()=="hidden_before_release")
assert(H.pump()=="cleaned")
assert(H.status().selected==nil and H.status().registered==0)
assert(R.cleaned==1 and not R.owned)
""")

    def test_map_clear_while_active_retains_no_old_selection(self):
        self.case(r"""
bound("A");H.map_pre()
assert(H.status().registered==0)
assert(H.pump()=="hidden_before_release")
assert(H.pump()=="cleaned")
register("B","Take")
scan(row("B",true,true,"Take"));assert(H.pump()=="no_target")
scan(row("B",true,true,"Take"));assert(H.pump()=="bound_hidden")
""")

    def test_cleanup_failure_blocks_any_other_bind_until_explicit_retry(self):
        self.case(r"""
register("A");register("B")
scan(row("A",true),row("B",false));scan(row("A",true),row("B",false))
assert(H.pump()=="bound_hidden");assert(H.pump()=="resumed")
scan(row("A",false),row("B",true));scan(row("A",false),row("B",true))
assert(H.pump()=="hidden_before_release")
R.fail_cleanup=true
assert(H.pump()=="cleanup_blocked" and H.status().blocked and R.owned)
for i=1,100 do assert(H.pump()=="cleanup_blocked")end
assert(not has("RELEASED") and R.created==1)
R.fail_cleanup=false
H.retry_cleanup()
assert(H.pump()=="cleaned" and not R.owned)
scan(row("A",false),row("B",true));scan(row("A",false),row("B",true))
-- Cleanup failed once -> terminal fault, no automatic second allocation.
assert(H.pump()=="disabled" and H.status().fault~=nil and R.created==1)
""")

    def test_cleanup_return_without_empty_proof_is_never_acknowledged(self):
        self.case(r"""
bound("A")
H.stop("user");assert(H.pump()=="hidden_before_release")
R.dirty_after_cleanup=true
assert(H.pump()=="cleanup_blocked")
assert(not has("CLEANED") and not has("RELEASED"))
assert(R.owned and H.status().blocked)
""")

    def test_partial_create_failure_retains_ownership_until_cleanup(self):
        self.case(r"""
register("A");scan(row("A",true));scan(row("A",true))
R.fail_create=true
assert(H.pump()=="create_failed_cleanup_required")
assert(R.owned and H.status().selected=="A")
assert(H.pump()=="cleaned")
assert(not R.owned and H.status().fault~=nil)
assert(H.pump()=="disabled" and R.created==1)
""")

    def test_identity_rebound_and_alias_faults_cannot_allocate(self):
        self.case(r"""
register("A")
local ok,why=H.register({actor="A",component="evil",widget="A.Widget",action="Open"})
assert(ok==nil and why and H.status().fault)
assert(H.pump()=="disabled" and R.created==0)
""")
        self.case(r"""
register("A")
local ok,why=H.register({actor="B",component="A.Component",widget="B.Widget",action="Take"})
assert(ok==nil and why and H.status().fault)
assert(H.pump()=="disabled" and R.created==0)
""")

    def test_partial_claimed_complete_is_fault_not_target(self):
        self.case(r"""
register("A");register("B")
local r,err=H.observe({row("A",true)},true)
assert(r==nil and err and H.status().fault)
assert(H.pump()=="disabled" and R.created==0)
""")

    def test_unready_hint_and_action_spoof_never_bind(self):
        self.case(r"""
register("A")
scan(row("A",true,false));scan(row("A",true,false))
assert(H.pump()=="no_target")
scan(row("A",true));scan(row("A",true));assert(H.pump()=="bound_hidden")
""")
        self.case(r"""
register("A")
local r,err=H.observe({row("A",true,true,"Check")},true)
assert(r==nil and err and H.status().fault)
""")

    def test_stop_cleanup_disables_new_bind_and_no_timer(self):
        self.case(r"""
bound("A")
H.stop("user")
assert(H.pump()=="hidden_before_release");assert(H.pump()=="cleaned")
for i=1,10000 do assert(H.pump()=="disabled")end
assert(R.created==1 and R.cleaned==1)
assert(H.status().stopped)
""")

    def test_renderer_hide_error_fails_closed_and_runs_cleanup(self):
        self.case(r"""
bound("A")
R.fail_hide=true
scan(row("A",false))
assert(H.pump()=="hide_failed")
assert(H.status().fault and H.status().phase=="release_required")
assert(H.pump()=="cleaned" and not R.owned)
assert(H.pump()=="disabled" and R.created==1)
-- The failed native hide is never retried or mistaken for a safe new bind.
""")

if __name__=="__main__":
    unittest.main()
