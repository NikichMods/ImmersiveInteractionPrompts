# SPDX-License-Identifier: MPL-2.0
"""PNG experiment policy tests; no game files, importer, GPU or proprietary font needed."""
from pathlib import Path
import unittest

from test_ui_child import FIXTURE, LuaRuntime, ROOT

SOURCE = (ROOT/'research/interaction-prompts-owner/png-header/Scripts/main.lua').read_text(encoding='utf-8')
ADDITIONS = r'''
Key.F8=8
function require(name)
 assert(name=="IIPPNGConfig");if S.config_missing then error("no local config")end
 return {filename="C:/local/OPEN.png"}
end
io.open=function(filename,mode)
 assert(filename=="C:/local/OPEN.png" and mode=="rb")
 if S.file_missing then return nil end
 local header="\137PNG\r\n\26\n"..string.pack(">I4",13).."IHDR"
  ..string.pack(">I4I4",S.bad_png and 999 or 560,112)..string.char(8,6,0,0,0).."CRC!"
 return {seek=function(_,mode)if mode=="end"then return 6917 end return 0 end,
  read=function()return header end,close=function()S.file_closed=true end}
end
local previous_find=StaticFindObject
local cdo=make("/Script/Engine.KismetRenderingLibrary","/Script/Engine.Default__KismetRenderingLibrary")
local import_path="/Script/Engine.KismetRenderingLibrary:ImportFileAsTexture2D"
local import_fn={IsValid=function()return not S.function_missing end,type=function()return "UFunction"end,
 GetFullName=function()return "Function "..import_path end}
setmetatable(import_fn,{__call=function(_,calling_context,world,filename)
 api();assert(calling_context==cdo and world==w and filename=="C:/local/OPEN.png" and S.file_closed)
 S.imports=(S.imports or 0)+1
 if S.import_null then return nil end
 local tex=make("/Script/Engine.Texture2D","/Transient.ImportedTexture")
 function tex:HasAnyFlags(flags)assert(flags==64);return not S.not_transient end
 function tex:Blueprint_GetSizeX()return S.bad_texture_size and 512 or 560 end
 function tex:Blueprint_GetSizeY()return 112 end
 S.texture=tex;return tex
end})
function StaticFindObject(p)
 if p==import_path then api();return import_fn end
 if p=="/Script/Engine.Default__KismetRenderingLibrary"then api();if S.cdo_missing then return nil end;return cdo end
 if p=="/Script/UMG.Image:SetBrushFromTexture" or p=="/Script/UMG.Image:SetBrushResourceObject"then
  api();return {IsValid=function()return not S.image_api_missing end,type=function()return "UFunction"end,
   GetFullName=function()return "Function "..p end}
 end
 return previous_find(p)
end
local previous_construct=StaticConstructObject
function StaticConstructObject(class,outer,name,flags)
 local o=previous_construct(class,outer,name,flags)
 if name:find("_OPEN$",1) then
  S.label=o;S.line=nil;o.Brush.DrawAs=3
  function o:SetBrushFromTexture(tex,match_size)
   api();assert(tex==S.texture and match_size==false)
   if not S.bind_fail then self.Brush.ResourceObject=tex end
  end
  function o:SetBrushResourceObject(resource)
   api();assert(resource==nil and not self.parent,"must detach before unbinding own texture")
   if S.clear_fail then error("clear failed")end
   self.Brush.ResourceObject=nil;S.unbound=(S.unbound or 0)+1
  end
 end
 return o
end
'''


class PNGHeaderPolicy(unittest.TestCase):
    def case(self, code, setup=''):
        lua = LuaRuntime(unpack_returned_tuples=True)
        lua.execute(FIXTURE+ADDITIONS)
        lua.execute(setup)
        lua.execute(SOURCE)
        lua.execute(code)
        self.assertTrue(lua.eval('original_ok()'))

    def test_import_once_brush_retains_then_unbinds(self):
        self.case('key();call();for i=1,15 do call()end;assert(S.imports==1 and S.attached==2 and S.label.Brush.ResourceObject==S.texture and S.label.Brush.TintColor.ColorUseRule==0);key();assert(S.removed==2 and S.unbound==1 and pair_detached() and not S.label.Brush.ResourceObject);key();assert(S.imports==1)')

    def test_missing_or_wrong_png_never_imports(self):
        for setup in ['S.file_missing=true','S.bad_png=true']:
            self.case('key();call();assert(not S.imports and S.attached==0 and has("FAILED") and pair_detached())',setup)

    def test_absent_function_or_cdo_never_calls(self):
        for setup in ['S.function_missing=true','S.cdo_missing=true','S.image_api_missing=true']:
            self.case('key();call();assert(not S.imports and S.attached==0 and pair_detached())',setup)

    def test_import_failure_no_ui_and_no_retry(self):
        for setup in ['S.import_null=true','S.bad_texture_size=true','S.not_transient=true']:
            self.case('key();call();assert(S.imports==1 and S.attached==0 and has("FAILED") and pair_detached());key();assert(S.imports==1)',setup)

    def test_binding_failure_returns_to_original(self):
        self.case('key();call();assert(S.imports==1 and S.attached==0 and pair_detached() and has("FAILED"))','S.bind_fail=true')

    def test_timeout_unbinds_without_more_callbacks(self):
        self.case('key();call();timer();assert(S.removed==2 and S.unbound==1 and pair_detached())')

    def test_clear_failure_reports_and_retries_only_cleanup(self):
        self.case('key();call();S.clear_fail=true;key();assert(S.removed==2 and has("CLEANUP_FAILED") and pair_detached());S.clear_fail=false;key();assert(S.unbound==1 and S.imports==1)')

    def test_unconfigured_no_engine_calls_or_key(self):
        self.case('assert(has("UNAVAILABLE") and S.created==0 and not S.key)','S.config_missing=true')


if __name__ == '__main__':
    unittest.main()
