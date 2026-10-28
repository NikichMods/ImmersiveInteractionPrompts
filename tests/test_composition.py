# SPDX-License-Identifier: MPL-2.0
"""Composition delta mocks: cached geometry, one stock translation, ornament import/rollback.
No engine rendering, native Slate measurement or GC acceptance is claimed.
"""
import unittest
from test_ui_child import FIXTURE, LuaRuntime, ROOT
from test_aphes_text import ADDITIONS as FONT_FIXTURE
from test_png_header import ADDITIONS as PNG_FIXTURE

BASE=ROOT/'research/interaction-prompts-owner/composition/Scripts'
SOURCE=(BASE/'main.lua').read_text(encoding='utf8')
LAYOUT=(BASE/'IIPLayout.lua').read_text(encoding='utf8')
# Reuse the accepted font fixture; widen only own-slot/style expectations for this delta.
FIX=FIXTURE.replace('assert(v.X==38 and v.Y==(label==S.label and -18 or -15));S.own_x=v.X',
    'assert(v.X==98);label.position=v;S.own_x=v.X').replace(
    'assert(v.X==140 and v.Y==(label==S.label and 28 or 2))', 'label.size=v;').replace(
    'assert(v==0)', 'assert(v==1)')
FONT=FONT_FIXTURE.replace('local copy={};for k,x in pairs(v)do copy[k]=x end',
    'local copy={};for k,x in pairs(v)do copy[k]=x end;copy.OutlineSettings={OutlineSize=2}')
PNG=PNG_FIXTURE[PNG_FIXTURE.index('local previous_find='):]
PNG=PNG[:PNG.index('local previous_construct=')]+PNG[PNG.index('local previous_construct='):].replace(
    'if name:find("_OPEN$",1) then', 'if class.p=="/Script/UMG.Image" then').replace(
    'S.label=o;S.line=nil;', 'S.line=o;')
PNG=PNG.replace('560','570').replace('112','16').replace(
    'function StaticConstructObject(class,outer,name,flags)',
    'function StaticConstructObject(class,outer,name,flags,...)').replace(
    'previous_construct(class,outer,name,flags)', 'previous_construct(class,outer,name,flags,...)')
EXTRA=r'''
stock.RenderTransform={Translation={X=0,Y=0},Shear={X=0.000011,Y=0},Angle=-0.00008}
function original_slot:GetAutoSize()return true end
function stock:GetDesiredSize()return {X=S.zero_extent and 0 or 120,Y=28}end
function stock:SetRenderTranslation(v)
 api();S.moves=(S.moves or 0)+1
 if S.restore_move_fail and v.Y==0 then error("restore failed")end
 self.RenderTransform.Translation={X=v.X,Y=v.Y}
 if S.partial_move then S.partial_move=false;error("error after stock write")end
end
local icon=make("/Script/UMG.RetainerBox",tree.p..".RetainerBox_0",tree);icon.parent=canvas
icon.Slot=make("/Script/UMG.CanvasPanelSlot",canvas.p..".IconSlot",canvas)
function icon.Slot:GetPosition()return {X=0,Y=0}end
function icon.Slot:GetSize()return {X=S.wide_icon and 128 or 32,Y=32}end
icon.Slot.GetAnchors=original_slot.GetAnchors
icon.Slot.GetAlignment=original_slot.GetAlignment
function icon.Slot:GetAutoSize()return false end
local old_construct=StaticConstructObject
function StaticConstructObject(c,...)
 local o=old_construct(c,...)
 if c.p=="/Script/UMG.TextBlock"then
  function o:SetColorAndOpacity(v)self.color=v end
 end
 return o
end
local old_require=require
function require(name)
 if name=="IIPLayout"then return S.layout end
 if name=="IIPCompositionConfig"then
  local c=old_require("IIPAphesConfig");c.separator_filename="C:/local/OPEN.png";return c
 end
 error("unexpected module")
end
local old_open=io.open
io.open=function(filename,mode)
 if filename~="C:/local/OPEN.png"then return old_open(filename,mode)end
 if S.png_missing then return nil end
 local h="\137PNG\r\n\26\n"..string.pack(">I4",13).."IHDR"..string.pack(">I4I4",570,16)..string.char(8,6,0,0,0).."CRC!"
 return {seek=function(_,m)if m=="end"then return 5000 end return 0 end,
 read=function()return h end,close=function()S.file_closed=true end}
end
function lower_original()return stock.RenderTransform.Translation.X==0 and stock.RenderTransform.Translation.Y==0
 and stock.RenderTransform.Shear.X==0.000011 and stock.RenderTransform.Angle==-0.00008 end
function change_translation()stock.RenderTransform.Translation={X=2,Y=3}end
function external_preserved()return stock.RenderTransform.Translation.X==2 and stock.RenderTransform.Translation.Y==3 end
'''

class CompositionPolicy(unittest.TestCase):
    def case(self,code,setup=''):
        lua=LuaRuntime(unpack_returned_tuples=True)
        lua.execute(FIX+FONT+PNG+EXTRA)
        lua.globals().S.layout=lua.execute(LAYOUT)
        lua.execute(setup)
        lua.execute(SOURCE)
        lua.execute(code)
        self.assertTrue(lua.eval('original_ok() and donor_ok()'))
        return lua

    def test_center_hierarchy_one_import_read_then_restore(self):
        self.case('key();call();assert(has("ATTACHED") and S.moves==1 and S.imports==1);'
          'assert(S.label.position.Y<S.line.position.Y and S.line.position.Y==0 and S.label.Font.Size==32);'
          'for i=1,20 do call()end;assert(S.moves==1 and S.imports==1);key();assert(S.word=="READ");'
          'key();assert(lower_original() and pair_detached() and S.unbound==1 and S.moves==2);'
          'key();assert(S.imports==1 and S.moves==2)')

    def test_unsupported_geometry_stops_before_allocation_or_mutation(self):
        for s in ['S.zero_extent=true','S.wide_icon=true']:
            self.case('key();call();assert(has("FAILED") and S.created==0 and not S.moves and lower_original())',s)

    def test_import_failure_never_moves_stock(self):
        for s in ['S.png_missing=true','S.import_null=true','S.function_missing=true','S.cdo_missing=true']:
            self.case('key();call();assert(has("FAILED") and not S.moves and lower_original() and pair_detached());'
                      'key();assert((S.imports or 0)<=1)',s)

    def test_partial_stock_setter_error_rolls_back(self):
        self.case('key();call();assert(has("FAILED") and lower_original() and pair_detached() and S.moves==2)',
                  'S.partial_move=true')

    def test_timeout_or_target_change_restores(self):
        for end in ['timer()','S.text="Другое";call()']:
            self.case('key();call();'+end+';assert(lower_original() and pair_detached() and S.unbound==1)')

    def test_restore_failure_retries_without_new_import(self):
        self.case('key();call();S.restore_move_fail=true;timer();assert(has("CLEANUP_FAILED") and pair_detached());'
                  'S.restore_move_fail=false;key();assert(lower_original() and has("LOWER_RESTORED") and S.imports==1)')

    def test_newer_translation_preserved_no_fighting_host(self):
        self.case('key();call();change_translation();call();assert(has("LOWER_CONFLICT") and S.moves==1 and pair_detached());'
                  'assert(external_preserved())')

    def test_texture_clear_failure_retries_detached_only(self):
        self.case('key();call();S.clear_fail=true;timer();assert(lower_original() and has("CLEANUP_FAILED"));'
                  'S.clear_fail=false;key();assert(S.imports==1 and S.unbound==1)')

if __name__=='__main__':unittest.main()

