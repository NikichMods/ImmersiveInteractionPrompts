# SPDX-License-Identifier: MPL-2.0
"""Pure slot envelopes; no native UMG hint/text/render acceptance."""
import unittest
from test_ui_child import LuaRuntime, ROOT

SOURCE=(ROOT/'research/interaction-prompts-owner/world-space/composition/IIPCompositionPlan.lua').read_text(encoding='utf8')

class WorldCompositionPlan(unittest.TestCase):
    def case(self,code):
        lua=LuaRuntime(unpack_returned_tuples=True)
        lua.execute('P=(function()\n'+SOURCE+'\nend)()')
        lua.execute(code)

    def test_baseline_fits_with_border_and_gaps(self):
        self.case('local p=P.plan(127.75,37.5,38,38);'
                  'for _,k in ipairs({"upper","ornament","action","hint"})do local r=p[k];'
                  'assert(r.x>=4 and r.y>=4 and r.x+r.w<=508 and r.y+r.h<=124)end;'
                  'assert(p.upper.y+p.upper.h<p.ornament.y and p.ornament.y+p.ornament.h<p.action.y)')

    def test_center_text_excludes_key(self):
        self.case('local p=P.plan(200,36,52,38);assert(p.action.x+p.action.w/2==256 '
                  'and p.upper.x+p.upper.w/2==256 and p.ornament.x+p.ornament.w/2==256);'
                  'assert(p.hint.x+p.hint.w+8==p.action.x)')

    def test_maximum_envelope_fits(self):
        self.case('local p=P.plan(340,40,64,40);assert(p.hint.x==14 and p.hint.y==80 '
                  'and p.action.x+p.action.w==426)')

    def test_icon_and_action_row_share_center(self):
        self.case('local p=P.plan(120,30,38,38);assert(p.action.y+p.action.h/2==100 '
                  'and p.hint.y+p.hint.h/2==100)')

    def test_ornament_preserves_aspect(self):
        self.case('local p=P.plan(100,30,38,38);assert(math.abs(p.ornament.w/p.ornament.h-570/16)<0.00001)')

    def test_overflow_rejected_without_resizing_or_truncation(self):
        self.case('assert(not pcall(P.plan,341,40,38,38));assert(not pcall(P.plan,120,41,38,38));'
                  'assert(not pcall(P.plan,120,40,65,38));assert(not pcall(P.plan,120,40,38,41))')

    def test_bad_or_unmeasured_extents_rejected(self):
        self.case('for _,v in ipairs({0,-1,0/0,math.huge})do assert(not pcall(P.plan,v,30,38,38))end;'
                  'assert(not pcall(P.plan,120,30,0,38));assert(not pcall(P.plan,120,nil,38,38))')

    def test_requires_no_game_globals_and_creates_no_objects(self):
        self.case('assert(StaticFindObject==nil and StaticConstructObject==nil);'
                  'local a=P.plan(100,30,38,38);local b=P.plan(150,30,38,38);assert(a.action.w==100 and b.action.w==150)')

if __name__=='__main__':unittest.main()
