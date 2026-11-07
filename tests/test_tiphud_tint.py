# SPDX-License-Identifier: MPL-2.0
"""Stage A overlay and real tint/session Lua modules with a controlled host."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import uuid

from test_selected_owner_world import BASE, MOCK, LuaRuntime

OVERLAY = BASE.parent / "tiphud-render-suppression"
RIG = """
clock=100
logs={}
writes=0
local function object(path,class,address)
    local o={live=true}
    function o:GetAddress()return address end
    function o:GetFullName()return "Object "..path end
    function o:GetClass()return {GetFullName=function()return "BlueprintGeneratedClass "..class end}end
    return o,{path=path,class=class,address=address}
end
actor,ar=object("actor","actorClass",1)
component,cr=object("component","componentClass",2)
widget,wr=object("widget","TipHUD_C",3)
actor.ExtendedWidget=component
component.Widget=widget
function component:GetOwner()return actor end
function component:GetWidget()return self.Widget end
function component:GetUserWidgetObject()return self.Widget end
function component:GetWidgetSpace()return 1 end
local null={IsValid=function()return false end,GetAddress=function()return 0 end}
local function name(s)return {ToString=function()return s end}end
widget.ColorAndOpacityDelegate={Object=null,FunctionName=name("None")}
widget.ColorAndOpacity={R=.125,G=.25,B=.5,A=.75}
function alive(o)return o~=nil and o.live end
local set={IsValid=function()return true end,type=function()return "UFunction" end}
function set:GetFullName()return "Function /Script/UMG.UserWidget:SetColorAndOpacity" end
setmetatable(set,{__call=function(_,w,c)
    assert(in_pump and w==widget and alive(w) and alive(actor) and alive(component))
    writes=writes+1
    if before_write then before_write(c) end
    w.ColorAndOpacity={R=c.R,G=c.G,B=c.B,A=c.A}
    if after_write then after_write(c) end
end})
objects={actor=actor,component=component,widget=widget,
    ["/Script/UMG.UserWidget:SetColorAndOpacity"]=set}
record={action="Open",refs={actor=ar,component=cr,widget=wr}}
view={shown=true,ready=true,native_text="Открыть"}
tint=Tint.new({snapshot=function()return view end},alive,nil,
    function(path)return objects[path] end,function()return clock end,
    function(event,reason)logs[#logs+1]=event.." "..reason end)
function pump(ready)
    in_pump=true;tint.frame(record,ready~=false);in_pump=false
end
function start()
    tint.request();assert(not in_pump)
    pump();pump()
end
function alpha()return widget.ColorAndOpacity.A end
function bind()widget.ColorAndOpacityDelegate.FunctionName=name("ComputeColor")end
"""

class TintStageA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dest = Path(tempfile.gettempdir()).resolve() / f"iip-tint-{uuid.uuid4().hex}"
        dest.mkdir()
        try:
            shutil.copytree(BASE / "Scripts", dest / "Scripts")
            subprocess.run(["git", "apply", "--unidiff-zero", str(OVERLAY / "stage-a.patch")],
                           cwd=dest, check=True)
            cls.scripts = {p.stem: p.read_text(encoding="utf-8")
                           for p in (dest / "Scripts").glob("*.lua")}
        finally:
            shutil.rmtree(dest)

    def case(self, script):
        lua = LuaRuntime()
        for name, body in self.scripts.items():
            lua.compile(body, name=name)
        lua.execute("Tint=(function()\n" + (OVERLAY / "IIPTipHUDTint.lua").read_text(
            encoding="utf-8") + "\nend)()")
        lua.execute(RIG + script)

    def test_manual_timeout_repeat_and_exact_rgba(self):
        self.case("""
start();assert(writes==1 and alpha()==0)
pump();assert(writes==1)
tint.request();pump();assert(writes==2 and alpha()==.75)
start();clock=105;pump();assert(writes==4 and alpha()==.75)
local c=widget.ColorAndOpacity;assert(c.R==.125 and c.G==.25 and c.B==.5)
start();for i=1,300 do pump() end
assert(writes==6 and alpha()==.75)
""")

    def test_refuses_ambiguous_preflight(self):
        for case in (
            'objects["/Script/UMG.UserWidget:SetColorAndOpacity"]=nil',
            'wr.address=100',
            'widget.ColorAndOpacity.R=0/0',
            'widget.ColorAndOpacityDelegate=nil',
            'bind()',
            'record.action="Take"',
            'view.ready=false',
            'component.Widget=actor',
        ):
            with self.subTest(case=case):
                self.case(case + "\nstart();assert(writes==0)")
        self.case("""
tint.request();pump(false);pump();assert(writes==0)
tint.request();pump();widget.ColorAndOpacity.A=.5;pump();assert(writes==0)
""")

    def test_respects_writer_and_stale_identity(self):
        for change, expected in (
            ("widget.ColorAndOpacity.A=.6", ".6"),
            ("bind()", "0"),
            ("widget.live=false", "0"),
            ("objects.actor=nil", "0"),
            ("wr.address=20", "0"),
            ("tint.ended(1)", "0"),
        ):
            with self.subTest(change=change):
                self.case(f"""
start();{change};pump();tint.request();pump();pump()
assert(writes==1 and alpha()=={expected} and logs[#logs]:find("TINT_STOPPED"))
""")

    def test_restore_after_partial_setter_and_world_loss(self):
        self.case("""
after_write=function(c)if c.A==0 then error("partial call")end end
start();assert(writes==2 and alpha()==.75)
tint.request();pump();pump();assert(writes==2)
""")
        self.case("""
start();pump(false);assert(writes==2 and alpha()==.75)
start();view.native_text="changed";pump()
assert(writes==4 and alpha()==.75 and view.shown)
""")
        self.case("""
start();before_write=function(c)if c.A>0 then error("restore failed")end end
tint.request();pump();assert(writes==2 and alpha()==0 and logs[#logs]:find("TINT_STOPPED"))
tint.request();pump();pump();assert(writes==2)
""")

    def test_patched_session_restores_before_hide_release_and_stop(self):
        session = self.scripts["IIPSelectedWorldSession"]
        injected = MOCK.replace("o=Session.start", """
api.tint=tint
world.shown=function()return true end
local acquire=source.acquire
source.acquire=function(a)
    local r=acquire(a)
    if r==nil then return nil end
    record.actor,record.action=a.key,a.action
    record.refs.actor=ar
    return record
end
local hide,cleanup=world.hide,world.cleanup
world.hide=function()assert(alpha()==.75);return hide()end
world.cleanup=function(...)assert(alpha()==.75);return cleanup(...)end
o=Session.start""")
        self.case("Session=(function()\n" + session + "\nend)()\n" + injected + """
function step(a)
    in_pump=true;select_owner(a);in_pump=false
end
function arm()
    tint.request();step(A);step(A)
    assert(alpha()==0)
end
step(A);arm();step(nil);assert(S.hides==1)
step(A);arm();step(B);assert(S.releases==1)
step(A);arm();o.stop("test");assert(alpha()==0)
step(A);assert(S.cancelled and S.releases==3 and writes==6)
""")

if __name__ == "__main__":
    unittest.main()
