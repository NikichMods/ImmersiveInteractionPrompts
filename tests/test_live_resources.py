# SPDX-License-Identifier: MPL-2.0
"""Exercise the actual extracted resource module with existing font/PNG native mocks."""
import unittest
from test_ui_child import LuaRuntime, ROOT
from test_composition import FIX, FONT, PNG, EXTRA

SOURCE=(ROOT/'research/interaction-prompts-owner/world-space/live-editor/Scripts/IIPResources.lua').read_text(encoding='utf8')
SETUP=r'''
local req=require
function require(n)
 if n=='IIPLiveConfig'then return req('IIPCompositionConfig')end
 return req(n)
end
S.test_widget=w;S.test_tree=tree;S.test_stock=stock
function resource_label()
 local o=StaticConstructObject(StaticFindObject('/Script/UMG.TextBlock'),S.test_tree,FName('Resource_OPEN'),64)
 o:SetFont(S.test_stock.Font)
 return o
end
function resource_line()
 return StaticConstructObject(StaticFindObject('/Script/UMG.Image'),S.test_tree,FName('Resource_Ornament'),64)
end
'''

class LiveResources(unittest.TestCase):
    def case(self,code,setup=''):
        lua=LuaRuntime(unpack_returned_tuples=True)
        lua.execute(FIX+FONT+PNG+EXTRA+SETUP)
        lua.execute('Resources=(function()\n'+SOURCE+'\nend)()')
        lua.execute('S.game=true;'+setup)
        lua.execute(code)

    def test_private_font_and_once_import_retention_release(self):
        self.case('Resources.prepare();local o=resource_label();Resources.font(o);'
                  'assert(o.Font.FontObject==S.own_font and donor_ok());'
                  'local line=resource_line();Resources.ornament(line,S.test_widget);'
                  'assert(line.Brush.ResourceObject==S.texture and S.imports==1);'
                  'assert(not pcall(Resources.ornament,line,S.test_widget));assert(S.imports==1);'
                  'o:SetFont(S.test_stock.Font);line:SetBrushResourceObject(nil);'
                  'assert(o.Font.FontObject==S.donor and line.Brush.ResourceObject==nil and donor_ok())')

    def test_font_alias_and_setter_failures_never_write_donor(self):
        for setup in ['S.storage_alias=true','S.fail_field="FontFilename"','S.bad_count=true','S.font_construct_fail=true']:
            self.case('Resources.prepare();local o=resource_label();assert(not pcall(Resources.font,o));assert(donor_ok())',setup)

    def test_resource_absence_and_invalid_import_fail_closed(self):
        self.case('assert(not pcall(Resources.prepare))','S.file_missing=true')
        self.case('Resources.prepare();local line=resource_line();assert(not pcall(Resources.ornament,line,S.test_widget));assert(S.imports==1)',
                  'S.import_null=true')

if __name__=='__main__':unittest.main()
