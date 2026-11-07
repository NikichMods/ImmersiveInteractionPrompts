# SPDX-License-Identifier: MPL-2.0
"""First-show overlay on exact World Lua and the controlled UE4 host."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import uuid

from test_selected_owner_world import BASE, LuaRuntime, MOCK, host
from test_tiphud_direct_brush import DIRECT_INPUT, OVERLAY


class FirstShow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dest = Path(tempfile.gettempdir()).resolve() / f"iip-first-show-{uuid.uuid4().hex}"
        dest.mkdir()
        try:
            shutil.copytree(BASE / "Scripts", dest / "Scripts")
            subprocess.run(
                ["git", "apply", "--unidiff-zero", str(OVERLAY / "first-show-observe.patch")],
                cwd=dest, check=True,
            )
            cls.scripts = {p.stem: p.read_text(encoding="utf-8")
                           for p in (dest / "Scripts").glob("*.lua")}
            assert len(cls.scripts) == 13
            assert cls.scripts["main"] == (BASE / "Scripts/main.lua").read_text(encoding="utf-8")
        finally:
            shutil.rmtree(dest)

    def world(self, body):
        vm = LuaRuntime()
        vm.execute(host.FIXTURE + host.EXTRA + host.CONTEXT + host.ORIENTATION
                   + host.FRAMES + host.HINT_FIXTURE + host.LIVE + host.MEASURED + host.STYLE)
        for name, source in self.scripts.items():
            vm.compile(source, name=name)
            if name != "main":
                body_source = host.RESOURCES if name == "IIPResources" else source
                vm.execute(f'package.preload["{name}"]=function()\n{body_source}\nend')
        vm.execute(host.SETUP + DIRECT_INPUT + """
local prepass=S.host.ForceLayoutPrepass
S.resume_prepasses=0
S.host.ForceLayoutPrepass=function(self)
 S.resume_prepasses=S.resume_prepasses+1
 return prepass(self)
end
assert(S.host.Visibility==3 and S.brush_sets==1 and S.mat_sets==0)
""" + body)

    def test_direct_first_show_and_same_owner_resume(self):
        self.world("""
assert(World.hide() and S.host.Visibility==1)
local new=owned("/Hint.FreshGamepad","/Script/Engine.Texture2D")
S.source_image.Brush.ResourceObject=new;S.device=4
assert(World.resume() and S.host.Visibility==3 and S.resume_prepasses==0)
assert(S.hint.Brush.ResourceObject==new and S.brush_sets==2)
assert(has("RESUME_LAYOUT") and has("reused=true"))
assert(World.cleanup("done"))
""")

    def test_resume_remeasures_changed_text_or_extent(self):
        for change in (
            'set(P.text,"value","Native action changed")',
            'S.hint_size={X=48,Y=38}',
            'set(P.widget,"CanHoldPress",true)',
        ):
            with self.subTest(change=change):
                self.world("assert(World.hide())\n" + change + """
assert(World.resume() and S.resume_prepasses==1 and has("reused=false"))
settle_direct();assert(S.host.Visibility==3)
assert(World.cleanup("done"))
""")

    def test_session_revalidates_owner_before_reveal(self):
        vm = LuaRuntime()
        vm.execute("Session=(function()\n" + self.scripts["IIPSelectedWorldSession"] + "\nend)()")
        vm.execute(MOCK + """
local create=world.create
world.create=function(...)
 local created=create(...)
 S.selected=B
 return created
end
select_owner(A)
assert(S.resumes==0 and S.releases==1 and not S.held)
""")


if __name__ == "__main__":
    unittest.main()
