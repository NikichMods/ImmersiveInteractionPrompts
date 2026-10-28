# SPDX-License-Identifier: MPL-2.0
"""Aphes writer/UI policy mocks, not native ownership or glyph-rendering evidence."""
import unittest
from test_ui_child import FIXTURE, LuaRuntime, ROOT

SOURCE=(ROOT/'research/interaction-prompts-owner/aphes-text/Scripts/main.lua').read_text(encoding='utf8')
ADDITIONS=r'''
Key.F6=6
function require(name)assert(name=="IIPAphesConfig");if S.config_missing then error("no config")end
 return {filename=S.filename or "C:/local/Aphes.ttf"}end
io.open=function(p,mode)
 assert(p==(S.filename or "C:/local/Aphes.ttf") and mode=="rb");if S.file_missing then return nil end
 return {seek=function(_,m)if m=="end"then return S.file_bad and 4 or 13920 end return 0 end,
  read=function()return "\0\1\0\0"end,close=function()S.file_closed=true end}
end
function FName(s)return {ToString=function()return s end}end
local function str(s)return {ToString=function()return s end}end
local function ss(name,address,fields)
 fields.IsValid=function()return true end;fields.type=function()return "UScriptStruct"end
 fields.GetFullName=function()return "ScriptStruct /Script/SlateCore."..name end
 fields.GetStructAddress=function()return address end
 return fields
end
local function arr(address,data,entry,count)
 local methods={IsValid=function()return true end,type=function()return "TArray"end,
 GetArrayNum=function()return count end,GetArrayMax=function()return count end,
 GetArrayAddress=function()return address end,GetArrayDataAddress=function()return data end}
 return setmetatable({}, {__index=function(_,k)
  if type(k)=="number"then assert(k==1 and count==1,"unsafe index");return entry end
  return methods[k]
 end,__newindex=function()error("array replacement forbidden")end})
end
local face=make("/Script/Engine.FontFace","/Game/Fonts/EBGaramond-SemiBold.EBGaramond-SemiBold")
local DONOR="/Game/Fonts/EBGaramond-SemiBold_Font.EBGaramond-SemiBold_Font"
local package=make("/Script/CoreUObject.Package","/Game/Fonts/EBGaramond-SemiBold_Font")
local function font(p,outer,is_copy)
 local o=make("/Script/Engine.Font",p,outer)
 function o:GetFullName()return "Font "..self.p end
 function o:HasAnyFlags(f)assert(f==64);return not S.nontransient end
 local base=is_copy and not S.storage_alias and 20000 or 10000
 local values={FontFaceAsset=face,FontFilename=str("old.ufont"),Hinting=0,LoadingPolicy=0,SubFaceIndex=0}
 local data=setmetatable({}, {__index=function(_,k)
  if S.donor_changed and not is_copy and k=="SubFaceIndex"then return 1 end
  return values[k]
 end,__newindex=function(_,k,v)
  assert(is_copy,"DONOR WRITE");S.font_writes=(S.font_writes or 0)+1
  if S.fail_field==k then error("setter failed: "..k)end
  if k=="FontFilename"then assert(type(v)=="string");v=str(S.bad_readback and "wrong.ttf" or v)end
  values[k]=v
  if S.change_donor then S.donor_changed=true end
 end})
 values.IsValid=function()return true end;values.type=function()return "UScriptStruct"end
 values.GetFullName=function()return "ScriptStruct /Script/SlateCore.FontData"end
 values.GetStructAddress=function()return base+408 end
 local entry=ss("TypefaceEntry",base+400,{Name=str("Default"),Font=data})
 o.FontCacheType=1
 o.CompositeFont=ss("CompositeFont",base+64,{
  DefaultTypeface=ss("Typeface",base+64,{Fonts=arr(base+64,base+400,entry,S.bad_count and is_copy and 0 or 1)}),
  FallbackTypeface=ss("CompositeFallbackFont",base+96,{Typeface=ss("Typeface",base+96,{Fonts=arr(base+96,0,nil,0)})}),
  SubTypefaces=arr(base+144,0,nil,0)})
 return o
end
local donor=font(DONOR,package,false);S.donor=donor
stock.Font.FontObject=donor;stock.Font.TypefaceFontName=str("Default")
stock.Font.GetStructAddress=function()return 5000 end
local previous_find=StaticFindObject
function StaticFindObject(p)
 if p==DONOR then if S.no_donor then return nil end return donor end
 if p=="/Script/Engine.Font"then return {p=p,IsValid=function()return true end,type=function()return "UClass"end,
 GetFullName=function()return "Class "..p end}end
 return previous_find(p)
end
local previous_construct=StaticConstructObject
function StaticConstructObject(c,outer,name,flags,...)
 local n=name:ToString()
 if c.p=="/Script/Engine.Font"then
  local args={...};assert(select('#',...)==4 and args[1]==0 and args[2]==false and args[3]==false and args[4]==donor)
  assert(outer==package and n=="IIP_AphesFont_1000");S.font_created=(S.font_created or 0)+1
  if S.font_construct_fail then error("font construction failed")end
  S.own_font=font(outer.p.."."..n,outer,true);return S.own_font
 end
 local o=previous_construct(c,outer,n,flags)
 if c.p=="/Script/UMG.TextBlock"then
  function o:SetFont(v)
   if v==stock.Font and S.restore_fail and S.font_created then error("restore failed")end
   if v~=stock.Font and S.bind_fail then error("bind failed")end
   local copy={};for k,x in pairs(v)do copy[k]=x end
   copy.GetStructAddress=function()return 6000 end;self.Font=copy;S.native_font=copy.FontObject
  end
  function o:SetText(v)
   assert(v=="OPEN" or v=="READ");self.Text=str(v);S.word=v
  end
 end
 return o
end
function donor_ok()
 local a=donor.CompositeFont.DefaultTypeface.Fonts[1].Font
 return a.FontFaceAsset==face and a.FontFilename:ToString()=="old.ufont" and a.SubFaceIndex==0
end
'''


class AphesTextPolicy(unittest.TestCase):
    def case(self, code, setup=''):
        lua=LuaRuntime(unpack_returned_tuples=True)
        lua.execute(FIXTURE+ADDITIONS+setup)
        lua.execute(SOURCE)
        lua.execute(code)
        self.assertTrue(lua.eval('original_ok()'))
        return lua

    def test_open_read_same_label_then_native_font_release(self):
        self.case('key();call();local first=S.label;assert(has("FONT_BOUND") and S.word=="OPEN" and donor_ok());key();assert(S.word=="READ" and S.label==first);key();assert(pair_detached() and S.native_font==S.donor and has("FONT_RELEASED") and has("CLEANED"));key();assert(S.font_created==1 and S.font_writes==5)')

    def test_missing_config_disables_before_key(self):
        self.case('assert(S.key==nil and has("UNAVAILABLE"))','S.config_missing=true;S.key=nil;')
        for filename in ['relative.ttf','C:/локал/Aphes.ttf','C:/local/Aphes.png']:
            with self.subTest(filename=filename):
                self.case('assert(S.key==nil and has("UNAVAILABLE"))','S.filename="'+filename+'";')
        self.case('key();call();assert(has("FONT_BOUND") and donor_ok())',r'S.filename=[[C:\local\Aphes.ttf]];')

    def test_missing_or_invalid_file_no_font_writes(self):
        for setup in ['S.file_missing=true;','S.file_bad=true;']:
            with self.subTest(setup=setup):
                self.case('key();call();assert(has("FAILED") and (S.font_writes or 0)==0 and donor_ok() and pair_detached())',setup)

    def test_absent_donor_no_fallback_or_repeated_creation(self):
        self.case('key();call();call();key();assert(has("NOT_LOADED") and not S.font_created and donor_ok() and pair_detached())','S.no_donor=true;')

    def test_mutation_guard_and_constructor_fail_closed(self):
        for setup in ['S.storage_alias=true;','S.bad_count=true;','S.font_construct_fail=true;','S.nontransient=true;']:
            with self.subTest(setup=setup):
                self.case('key();call();assert(has("FAILED") and (S.font_writes or 0)==0 and donor_ok() and pair_detached())',setup)

    def test_each_setter_failure_contains_partial_own_writes(self):
        for field in ['FontFaceAsset','FontFilename','LoadingPolicy','Hinting','SubFaceIndex']:
            with self.subTest(field=field):
                self.case('key();call();assert(has("FAILED") and has("DONOR_UNCHANGED") and donor_ok() and pair_detached())','S.fail_field="'+field+'";')

    def test_readback_or_bind_failure_restores_own_label(self):
        for setup in ['S.bad_readback=true;','S.bind_fail=true;']:
            with self.subTest(setup=setup):
                self.case('key();call();assert(has("FAILED") and donor_ok() and pair_detached() and S.native_font==S.donor)',setup)

    def test_donor_postcheck_detects_native_fault(self):
        self.case('key();call();assert(has("DONOR_CHECK_FAILED") and pair_detached() and not has("ATTACHED"))','S.change_donor=true;')

    def test_timeout_and_state_change_cleanup(self):
        self.case('key();call();timer();assert(pair_detached() and S.native_font==S.donor)')
        self.case('key();call();S.text="Другое";call();assert(pair_detached() and S.native_font==S.donor)')

    def test_release_failure_keeps_font_until_explicit_retry(self):
        self.case('key();call();S.restore_fail=true;key();key();assert(pair_detached() and has("CLEANUP_FAILED") and S.label.Font.FontObject==S.own_font);S.restore_fail=false;key();assert(has("CLEANED") and S.native_font==S.donor and S.font_created==1)')


if __name__=='__main__':unittest.main()
