# SPDX-License-Identifier: MPL-2.0
"""Bounded coverage coordinator assembled against the exact control overlays."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import uuid

from test_tiphud_render_translation import ADAPTER, BASE, LuaRuntime, OVERLAY, RIG


class TranslationCycle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dest = Path(tempfile.gettempdir()).resolve() / f"iip-cycle-{uuid.uuid4().hex}"
        dest.mkdir()
        try:
            shutil.copytree(BASE / "Scripts", dest / "Scripts")
            shutil.copyfile(OVERLAY / "IIPPrehideTranslation.lua", dest / "Scripts/IIPPrehideTranslation.lua")
            for patch in ("first-show-observe.patch", "prehide-translation.patch", "translation-cycle.patch"):
                subprocess.run(["git", "apply", "--unidiff-zero", str(OVERLAY / patch)], cwd=dest, check=True)
            cls.scripts = {p.stem: p.read_text(encoding="utf-8")
                           for p in (dest / "Scripts").glob("*.lua")}
        finally:
            shutil.rmtree(dest)

    def case(self, lua):
        vm = LuaRuntime()
        for name, script in self.scripts.items():
            vm.compile(script, name=name)
        main = self.scripts["main"]
        for mode in ("early_assets", "combined"):
            vm.compile(main.replace('local MODE="coverage"', f'local MODE="{mode}"'))
        translation = self.scripts["IIPPrehideTranslation"]
        coverage = (OVERLAY / "IIPTranslationCoverage.lua").read_text(encoding="utf-8")
        vm.execute("Tint={new=function()end}; Prehide=(function()\n" + translation + "\nend)()\n"
                   + 'package.loaded.IIPPrehideTranslation=Prehide\n'
                   + "Coverage=(function()\n" + coverage + "\nend)()\n" + RIG
                   + ADAPTER.replace("p=Prehide.new({", "local coverage_api={")
                   .replace('},function(e,msg)logs[#logs+1]=e.." "..msg end)', "}")
                   + """
record.refs.actor.path=target
local emit=function(e,msg)logs[#logs+1]=e.." "..msg end
local function actor2()
 local a=mock("Take","Actor",11);local c=mock("Take.Comp","Component",12)
 local w=mock("Take.Widget","TipHUD",13);local t=mock("Take.Tree","Tree",14)
 local root=mock("Take.Tree.CanvasPanel_0","/Script/UMG.CanvasPanel",15)
 root.RenderTransform={Translation={X=8,Y=5}}
 function root:GetOuter()return t end
 function c:GetOwner()return a end
 function c:GetWidget()return self.Widget end
 function c:GetUserWidgetObject()return self.Widget end
 function c:GetWidgetSpace()return 1 end
 c.bVisible=false;c.bAddedToScreen=false
 a.ExtendedWidget=c;c.Widget=w;w.WidgetTree=t;t.RootWidget=root
 return a,root,{actor=key(a),component=key(c),widget=key(w),action="Take",
     refs={actor={path="take_target",address=11}}}
end
take,take_panel,take_record=actor2()
local function rec(a)if a==actor then return record elseif a==take then return take_record end end
coverage_api.acquire=rec
coverage_api.resolve_actor=function(id)if id.key==record.actor then return actor elseif id.key==take_record.actor then return take end end
local path=coverage_api.path
coverage_api.path=function(o)
 if o==take then return "take_target" elseif o==take_panel then return "Take.Tree.CanvasPanel_0" end
 return path(o)
end
coverage_api.class=function(o)return (o==panel or o==take_panel) and "/Script/UMG.CanvasPanel" or "other" end
coverage_api.matches_action=function(a,action)return rec(a).action==action end
coverage_api.qualify=function(a)return not no_input and (a==take and "take_texture" or "open_texture") end
coverage_api.brush_token=function(w)return token_override or (w==widget and "open_texture" or "take_texture") end
coverage_api.set=function(root,v)
 assert(in_pump and (root==panel or root==take_panel) and alive(root))
 writes=writes+1;root.RenderTransform.Translation={X=v.X,Y=v.Y}
end
p=Coverage.new(coverage_api,emit)
function shutdown(reason)
 in_pump=true;p.restore_all(reason,reason=="stop");in_pump=false
end
""" + lua)

    def test_separate_owners_and_stock_first(self):
        self.case("""
p.begin(actor);p.begin(take);select(nil)
assert(not select(actor) and writes==0)
select(nil);assert(tx()==16384 and writes==1)
assert(select(actor)==actor);p.shown()
assert(not select(take));select(nil);assert(writes==2)
assert(select(take)==take);p.shown()
assert(select(actor)==actor);p.shown();assert(writes==2)
shutdown("stop")
assert(writes==4 and tx()==0 and take_panel.RenderTransform.Translation.X==8)
assert(take_panel.RenderTransform.Translation.Y==5)
""")

    def test_changed_brush_and_unsupported_state_stay_stock(self):
        self.case("""
p.begin(actor);p.begin(take)
no_input=true;assert(not select(take));select(nil);assert(writes==0)
no_input=false;assert(not select(actor));token_override="other";select(nil)
assert(writes==0 and not select(actor))
token_override=nil;assert(not select(actor));select(nil);assert(writes==0)
""")

    def test_map_and_endplay_invalidate_only_matching_leases(self):
        self.case("""
p.begin(actor);select(actor);select(nil)
assert(writes==1)
p.map_pre();p.begin(take);shutdown("map_pre")
assert(tx()==0 and writes==2)
select(take);select(nil);assert(writes==3)
take_panel.live=false;p.ended(11);shutdown("stop")
assert(writes==3)
""")


if __name__ == "__main__":
    unittest.main()
