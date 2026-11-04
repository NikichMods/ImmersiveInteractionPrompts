# SPDX-License-Identifier: MPL-2.0
"""Execute Open owner/visibility bridge against read-only host mocks."""
import unittest

from test_ui_child import LuaRuntime, ROOT
from test_beginplay_join import FIXTURE

SOURCE = (ROOT / "research/interaction-prompts-owner/world-space/auto-target/IIPOpenSource.lua").read_text(
    encoding="utf-8"
)
EXTRA = r"""
S.game=true
set(P.text,"GetText",function()return P.text.Text end)
A=(function()
""" + SOURCE + r"""
end)()
function get()
    local r,why=A.acquire(P.actor)
    assert(r,why)
    return r
end
function native_alive(o) return o:IsValid() end
function hint_visible(w) return w.Visibility==0 end
function sample(rec)
    local out,why=A.snapshot(rec,native_alive,hint_visible)
    assert(out,why)
    return out
end
"""

class OpenSource(unittest.TestCase):
    def case(self, code):
        lua = LuaRuntime(unpack_returned_tuples=True)
        lua.execute(FIXTURE)
        lua.execute(EXTRA)
        lua.execute(code)

    def test_exact_open_join_and_native_visibility(self):
        self.case('''
local rec=get()
assert(rec.actor:find("Chest1") and rec.component:find("ExtendedWidget"))
assert(rec.widget:find("TipHUD"))
local result=sample(rec)
assert(result.shown and result.ready)
assert(result.actor==rec.actor and result.component==rec.component)
''')

    def test_can_show_callback_cannot_force_visibility(self):
        self.case('''
local rec=get()
set(P.component,"bVisible",false)
local result=sample(rec);assert(not result.shown and not result.ready)
set(P.component,"bVisible",true)
set(P.widget,"Visibility",1)
result=sample(rec);assert(not result.shown and not result.ready)
''')

    def test_native_hint_not_available_abstains(self):
        self.case('''
local rec=get()
local result=A.snapshot(rec,native_alive,function(w)return false end)
assert(result and not result.shown and not result.ready)
''')

    def test_unsupported_or_empty_action_abstains(self):
        self.case('''
local rec=get()
set(P.text,"Text",{ToString=function()return "" end})
local result=sample(rec);assert(result.shown and not result.ready)
set(P.text,"Text",{ToString=function()return "Open\\nNow" end})
result=sample(rec);assert(result.shown and not result.ready)
''')

    def test_mismatched_widget_contract_fails_closed(self):
        self.case('''
local rec=get()
Q=pair(2)
set(P.component,"Widget",Q.widget)
assert(not pcall(A.snapshot,rec,native_alive,hint_visible))
''')

    def test_actor_endplay_and_native_pending_kill_are_not_guessed(self):
        self.case('''
local rec=get()
local result,why=A.snapshot(rec,function(o)
 return o~=P.actor
end,hint_visible)
assert(result==nil and why=="object_pending_kill")
set(P.actor,"live",false)
result,why=A.snapshot(rec,native_alive,hint_visible)
assert(result==nil and why=="object_gone")
''')

    def test_other_actor_not_treated_as_open(self):
        self.case('''
local foreign=make("/World.Unrelated","/Script/Engine.Actor")
local r,why=A.acquire(foreign)
assert(r==nil and why=="unrelated_actor")
set(P.argument,"tag","Take")
r,why=A.acquire(P.actor)
assert(r==nil and why=="other_action")
''')

    def test_null_widget_waits_without_init_or_manual_beginplay(self):
        self.case('''
set(P.component,"Widget",nil)
local r,why=A.acquire(P.actor)
assert(r==nil and why=="not_ready_widget")
''')

    def test_adapter_is_read_only_and_does_not_load_assets(self):
        self.case('''
local rec=get();sample(rec)
assert(LoadAsset==nil and StaticConstructObject==nil)
assert(type(RegisterHook)=="function" and RegisterBeginPlayPostHook==nil)
assert(S.registered==0 and S.pose_reads==0)
''')

if __name__ == "__main__":
    unittest.main()
