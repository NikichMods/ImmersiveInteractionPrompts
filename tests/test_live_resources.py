# SPDX-License-Identifier: MPL-2.0
"""Exercise the actual extracted resource module with existing font/PNG native mocks."""
import unittest
from test_ui_child import LuaRuntime, ROOT
from test_composition import FIX, FONT, PNG, EXTRA

SOURCE=(ROOT/'research/interaction-prompts-owner/world-space/live-editor/Scripts/IIPResources.lua').read_text(encoding='utf8')
TEMPLATE_SOURCE=(ROOT/'research/interaction-prompts-owner/world-space/native-world-template/Scripts/IIPTemplateResources.lua').read_text(encoding='utf8')
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
    def case(self,code,setup='',source=SOURCE):
        lua=LuaRuntime(unpack_returned_tuples=True)
        ornament=PNG+EXTRA
        if source==TEMPLATE_SOURCE:
            ornament=ornament.replace("570","256").replace("return 16 end","return 32 end")
            ornament=ornament.replace(">I4I4\",256,16",">I4I4\",256,32")
        lua.execute(FIX+FONT+ornament+SETUP)
        lua.execute('Resources=(function()\n'+source+'\nend)()')
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

    def test_template_replaces_invalid_successful_texture_then_stops_on_failed_import(self):
        self.case("""
            Resources.prepare()
            local first,second,third=resource_line(),resource_line(),resource_line()
            Resources.ornament(first,S.test_widget)
            local original=S.texture
            Resources.ornament(second,S.test_widget)
            assert(S.imports==1 and second.Brush.ResourceObject==original)
            original.IsValid=function()return false end
            Resources.ornament(third,S.test_widget)
            assert(S.imports==2 and third.Brush.ResourceObject==S.texture and S.texture~=original)
            S.texture.IsValid=function()return false end
            S.import_null=true
            assert(not pcall(Resources.ornament,resource_line(),S.test_widget))
            assert(not pcall(Resources.ornament,resource_line(),S.test_widget))
            assert(S.imports==3)
        """,source=TEMPLATE_SOURCE)

if __name__=='__main__':unittest.main()
