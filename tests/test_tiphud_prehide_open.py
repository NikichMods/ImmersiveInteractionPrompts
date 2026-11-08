# SPDX-License-Identifier: MPL-2.0
"""Pre-hide overlay assembly, exact-instance lease and selected pump."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import uuid

from test_selected_owner_world import BASE, LuaRuntime, MOCK
from test_tiphud_tint import OVERLAY, RIG

ADAPTER = """
target="/Game/MainContent/Maps/sublevel_plot/0-1/0-1_plot_outerRimA_interact1.0-1_plot_outerRimA_interact1:PersistentLevel.0-1_lootbox_01_mat_ST001"
function key(o)return o:GetFullName().."|"..o:GetAddress() end
record.actor=key(actor);record.component=key(component);record.widget=key(widget)
component.bVisible=false;component.bAddedToScreen=false
local setter=objects["/Script/UMG.UserWidget:SetColorAndOpacity"]
p=Prehide.new({
    alive=alive,key=key,path=function(a)return a==actor and target or "other" end,
    acquire=function()return record end,resolve_actor=function()return objects.actor end,
    matches_action=function()return record.action=="Open" end,
    supported=function()return not unsupported end,
    set=function(w,c)setter(w,c) end,now=function()return clock end,mode="test",
},function(e,why)logs[#logs+1]=e.." "..why end)
function select(a)
    in_pump=true
    local r=p.filter({status="READY",actor=a,key=a and key(a)})
    in_pump=false
    return r.actor
end
function restore()
    in_pump=true;p.restore("test");in_pump=false
end
"""

class PrehideOpen(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dest = Path(tempfile.gettempdir()).resolve() / f"iip-prehide-{uuid.uuid4().hex}"
        dest.mkdir()
        try:
            shutil.copytree(BASE / "Scripts", dest / "Scripts")
            for patch in ("first-show-observe.patch", "prehide-open.patch"):
                subprocess.run(["git", "apply", "--unidiff-zero", str(OVERLAY / patch)],
                               cwd=dest, check=True)
            cls.scripts = {p.stem: p.read_text(encoding="utf-8")
                           for p in (dest / "Scripts").glob("*.lua")}
            subprocess.run(["git", "apply", "--unidiff-zero", str(OVERLAY / "prehide-early-assets.patch")],
                           cwd=dest, check=True)
            cls.mode_b = (dest / "Scripts/main.lua").read_text(encoding="utf-8")
            cls.module = (OVERLAY / "IIPPrehideOpen.lua").read_text(encoding="utf-8")
        finally:
            shutil.rmtree(dest)

    def case(self, body):
        vm = LuaRuntime()
        for name, script in self.scripts.items():
            vm.compile(script, name=name)
        vm.compile(self.mode_b, name="mode_b")
        self.assertEqual(self.mode_b, self.scripts["main"].replace(
            "false -- Mode A", "true -- Mode B: asset preparation only"))
        vm.execute("Tint={new=function()end}; Prehide=(function()\n" + self.module
                   + "\nend)()\n" + RIG + ADAPTER + body)

    def test_arm_once_repeated_approach_and_manual_restore(self):
        self.case("""
p.begin(actor);assert(writes==0);select(nil);assert(alpha()==0 and writes==1)
assert(select(actor)==actor);p.shown();clock=101;assert(select(actor)==actor)
select(nil);clock=102;assert(select(actor)==actor);p.shown();assert(writes==1)
restore();assert(alpha()==.75 and writes==2)
p.begin(actor);select(nil);assert(not select(actor) and writes==2)
local c=widget.ColorAndOpacity;assert(c.R==.125 and c.G==.25 and c.B==.5)
""")

    def test_deadline_and_unsupported_state_are_stock_only(self):
        self.case("""
p.begin(actor);select(nil);assert(select(actor)==actor)
clock=100.5;assert(not select(actor) and writes==2 and alpha()==.75)
assert(not select(actor) and writes==2)
""")
        self.case("""
p.begin(actor);select(nil);unsupported=true
assert(not select(actor) and writes==2 and alpha()==.75)
""")

    def test_late_binding_stale_and_foreign_writer(self):
        for setup in ("component.bAddedToScreen=true", "bind()", "unsupported=true",
                      'record.action="Take"', "component.Widget=actor"):
            with self.subTest(setup=setup):
                self.case(setup + """
p.begin(actor);select(nil);assert(writes==0 and alpha()==.75)
""")
        for change in ("component.Widget=actor", "widget.live=false",
                       "widget.ColorAndOpacity.A=.4", "p.ended(1)"):
            with self.subTest(change=change):
                self.case("p.begin(actor);select(nil);" + change + """
assert(not select(actor) and writes==1)
""")

    def test_partial_setter_error_restores(self):
        self.case("""
after_write=function(c)if c.A==0 then error("partial setter")end end
p.begin(actor);select(nil)
assert(writes==2 and alpha()==.75 and not select(actor))
""")

    def session(self, body):
        self.case("Session=(function()\n" + self.scripts["IIPSelectedWorldSession"] + "\nend)()\n"
                  + MOCK.replace("o=Session.start", """
A=actor;A.key=key(actor);A.action="Open"
api.prehide=p;api.early_assets=true
world.prepare=function()S.prepared=(S.prepared or 0)+1 end
world.direct_input=function()return not bad_brush end
world.direct_shown=function()return not bad_show end
local create=world.create
world.create=function(...)
    if fail_create then error("test failure")end
    return create(...)
end
o=Session.start""") + """
function pump(a)
    in_pump=true;select_owner(a);in_pump=false
end
p.begin(actor);pump(nil)
assert(S.prepared==1 and S.creates==0 and alpha()==0)
""" + body)

    def test_early_assets_then_world_and_lifecycle_restore(self):
        for stop in ('o.stop("manual")', 'o.invalidate("map_pre")'):
            with self.subTest(stop=stop):
                self.session("""
pump(A);assert(S.prepared==1 and S.creates==1 and S.held and alpha()==0)
pump(nil);pump(A);assert(S.creates==1 and writes==1)
""" + stop + """
assert(alpha()==0);pump(A)
assert(alpha()==.75 and S.releases==1 and not S.held)
""")

    def test_late_brush_and_world_error_never_reveal_again(self):
        for failure in ("bad_brush=true", "bad_show=true", "fail_create=true"):
            with self.subTest(failure=failure):
                self.session(failure + """
pump(A);assert(alpha()==.75 and not S.held)
local creates=S.creates
bad_brush=false;bad_show=false;fail_create=false;pump(A)
assert(S.creates==creates and not S.held)
""")


if __name__ == "__main__":
    unittest.main()
