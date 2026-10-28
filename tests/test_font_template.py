# SPDX-License-Identifier: MPL-2.0
"""Font-copy probe policy tests. Native Template copying/GC is not simulated evidence."""
import unittest
from test_ui_child import LuaRuntime, ROOT

SOURCE = (ROOT/'research/interaction-prompts-owner/font-template/Scripts/main.lua').read_text(encoding='utf8')
FIXTURE = r'''
S={game=false,created=0,indexes=0,writes=0,logs={},queue={}}
local DONOR="/Game/Fonts/EBGaramond-SemiBold_Font.EBGaramond-SemiBold_Font"
local function api()assert(S.game,"outside game thread")end
local function readonly(values)
 return setmetatable({}, {__index=values,__newindex=function()S.writes=S.writes+1;error("forbidden write")end})
end
local function object(kind,path,addr)
 return readonly({IsValid=function()api();return true end,GetAddress=function()api();return addr end,
 GetFullName=function()return kind.." "..path end,
 GetClass=function()return {GetFullName=function()return "Class /Script/"..(kind=="Package" and "CoreUObject.Package" or "Engine."..kind)end}end})
end
local outer=object("Package","/Game/Fonts/EBGaramond-SemiBold_Font",20)
local face=object("FontFace","/Game/Fonts/EBGaramond-SemiBold.EBGaramond-SemiBold",30)
local function struct(name,addr,fields,is_copy)
 fields.IsValid=function()api();return true end
 fields.type=function()return "UScriptStruct"end
 fields.GetFullName=function()
  return "ScriptStruct /Script/SlateCore."..(S.wrong_struct and is_copy and name=="TypefaceEntry" and "FontData" or name)
 end
 fields.GetStructAddress=function()
  api();if S.no_address and is_copy then error("no address API")end
  return S.zero_address and is_copy and 0 or addr
 end
 return readonly(fields)
end
local function array(addr,data,num,entry,is_copy)
 local methods={IsValid=function()api();return true end,type=function()return "TArray"end,
 GetArrayNum=function()return num end,GetArrayMax=function()return S.bad_capacity and 999 or num end,
 GetArrayAddress=function()return addr end,GetArrayDataAddress=function()return data end}
 return setmetatable({}, {__index=function(_,k)
  if type(k)=="number"then
   api();assert(num==1 and k==1,"unsafe indexed access");S.indexes=S.indexes+1;return entry
  end
  return methods[k]
 end,__newindex=function()S.writes=S.writes+1;error("array write")end})
end
local function font(is_copy)
 local base=is_copy and 2000 or 1000
 local field_addr=base+408
 if is_copy and (S.alias=="font_data" or S.alias=="data")then field_addr=1408 end
 local data=struct("FontData",field_addr,{
  FontFaceAsset=face,FontFilename={ToString=function()return S.donor_changed and not is_copy and "changed" or "font.ufont"end},
  Hinting=0,LoadingPolicy=0,SubFaceIndex=0},is_copy)
 local entry_addr=base+400
 if is_copy and (S.alias=="entry" or S.alias=="data")then entry_addr=1400 end
 local entry=struct("TypefaceEntry",entry_addr,{Name={ToString=function()return "Default"end},Font=data},is_copy)
 local header,buffer=base+64,base+400
 if is_copy and S.alias=="array"then header=1064 end
 if is_copy and S.alias=="data"then buffer=1400 end
 local fonts=array(header,buffer,((is_copy and S.bad_count=="copy") or (not is_copy and S.bad_count=="donor")) and 0 or 1,entry,is_copy)
 local composite=struct("CompositeFont",base+64,{
  DefaultTypeface=struct("Typeface",base+64,{Fonts=fonts},is_copy),
  FallbackTypeface=struct("CompositeFallbackFont",base+96,{
   Typeface=struct("Typeface",base+96,{Fonts=array(base+96,0,0,nil,is_copy)},is_copy)},is_copy),
  SubTypefaces=array(base+144,0,S.subtypes and 1 or 0,nil,is_copy)},is_copy)
 local kind=(S.wrong_donor and not is_copy or S.wrong_copy and is_copy)and "FontFace" or "Font"
 return readonly({IsValid=function()api();return true end,
  GetAddress=function()return base end,
  GetFullName=function()return kind.." "..(is_copy and "/Game/Fonts/EBGaramond-SemiBold_Font.IIP_FontTemplate_1000" or DONOR)end,
  GetClass=function()return {GetFullName=function()return "Class /Script/Engine."..kind end}end,
  GetOuter=function()return outer end,HasAnyFlags=function(_,flag)assert(flag==64);return not S.no_transient end,
  FontCacheType=(S.offline and is_copy)and 0 or 1,CompositeFont=composite})
end
local donor
function StaticFindObject(path)
 api();S.lookups=(S.lookups or 0)+1
 if path==DONOR then
  if S.missing then return nil end
  donor=donor or font(false);return donor
 end
 if path=="/Script/Engine.Font"then
  if S.no_class then return nil end
  return {IsValid=function()return true end,type=function()return "UClass"end,
   GetFullName=function()return "Class /Script/Engine.Font"end}
 end
 assert(path=="/Game/Fonts/EBGaramond-SemiBold_Font.IIP_FontTemplate_1000");return S.collision and donor or nil
end
function StaticConstructObject(...)
 api();local args={...};assert(select('#',...)==8)
 assert(args[1]:GetFullName()=="Class /Script/Engine.Font" and args[2]==outer and args[3]=="IIP_FontTemplate_1000")
 assert(args[4]==64 and args[5]==0 and args[6]==false and args[7]==false and args[8]==donor)
 S.created=S.created+1
 if S.construct_throws then error("native construct failure")end
 if S.null_copy then return nil end
 if S.return_donor then return donor end
 if S.mutate_donor then S.donor_changed=true end -- Fault injected in mock native layer only.
 return font(true)
end
FName=function(n)return n end;EObjectFlags={RF_Transient=64}
Key={F7=7};ModifierKey={CONTROL=1,ALT=2};EngineTickAvailable=true;EGameThreadMethod={EngineTick=1}
function IsKeyBindRegistered()return S.key_collision or false end
function RegisterKeyBind(k,m,fn)assert(k==7 and m[1]==1 and m[2]==2);S.key=fn end
function ExecuteInGameThread(fn,method)
 assert(method==1);if S.dispatch_fail then error("dispatch unavailable")end
 S.queue[#S.queue+1]=fn
end
os.time=function()return 1000 end
print=function(line)S.logs[#S.logs+1]=line end
function key()
 if S.key then S.key()end
 S.game=true;for _,fn in ipairs(S.queue)do fn()end;S.queue={};S.game=false
end
function has(text)for _,line in ipairs(S.logs)do if line:find(text,1,true)then return true end end return false end
'''


class FontTemplateTests(unittest.TestCase):
    def make(self, setup=''):
        lua=LuaRuntime(unpack_returned_tuples=True)
        lua.execute(FIXTURE+setup)
        lua.execute(SOURCE)
        return lua

    def test_one_copy_exact_template_arguments_readonly_success(self):
        lua=self.make();lua.execute('key();key();assert(S.created==1 and S.writes==0);assert(has("STORAGE_CHECK_PASS") and has("DONOR_UNCHANGED"))')

    def test_rapid_keys_queue_once(self):
        lua=self.make();lua.execute('S.key();S.key();assert(#S.queue==1);key();assert(S.created==1)')

    def test_missing_donor_stops_without_creation_or_retry(self):
        lua=self.make('S.missing=true');lua.execute('key();S.missing=false;key();assert(S.created==0 and S.indexes==0 and has("NOT_LOADED"))')

    def test_structure_rejected_before_out_of_bounds_access(self):
        for setup in ['S.bad_count="donor"','S.bad_count="copy"','S.bad_capacity=true','S.subtypes=true','S.offline=true','S.wrong_struct=true']:
            with self.subTest(setup=setup):
                lua=self.make(setup);lua.execute('key();assert(has("result=FAILED") and not has("STORAGE_CHECK_PASS") and S.writes==0)')

    def test_classes_and_name_collision(self):
        for setup in ['S.wrong_donor=true','S.wrong_copy=true','S.no_class=true','S.collision=true','S.no_transient=true']:
            with self.subTest(setup=setup):
                lua=self.make(setup);lua.execute('key();assert(has("result=FAILED") and not has("STORAGE_CHECK_PASS"))')

    def test_creation_failure_alias_and_null_no_second_attempt(self):
        for setup in ['S.construct_throws=true','S.null_copy=true','S.return_donor=true']:
            with self.subTest(setup=setup):
                lua=self.make(setup);lua.execute('key();key();assert(S.created==1 and has("result=FAILED") and has("DONOR_UNCHANGED"))')

    def test_unavailable_or_zero_addresses_never_pass(self):
        for setup in ['S.no_address=true','S.zero_address=true']:
            with self.subTest(setup=setup):
                lua=self.make(setup);lua.execute('key();assert(has("result=FAILED") and not has("STORAGE_CHECK_PASS"))')

    def test_equal_values_do_not_hide_shared_storage(self):
        for field in ['array','data','entry','font_data']:
            with self.subTest(field=field):
                lua=self.make('S.alias="'+field+'"');lua.execute('key();assert(has("result=FAILED") and not has("STORAGE_CHECK_PASS") and S.writes==0)')

    def test_donor_checked_on_native_failure_or_unexpected_change(self):
        lua=self.make('S.mutate_donor=true');lua.execute('key();assert(has("DONOR_CHECK_FAILED") and has("result=FAILED") and S.writes==0)')

    def test_missing_startup_api_collision_and_dispatch(self):
        for setup in ['StaticConstructObject=nil','S.key_collision=true','EngineTickAvailable=false']:
            with self.subTest(setup=setup):
                lua=self.make(setup);lua.execute('assert(S.key==nil and S.created==0 and has("UNAVAILABLE"))')
        lua=self.make('S.dispatch_fail=true');lua.execute('key();key();assert(S.created==0 and has("DISPATCH_FAILED"))')


if __name__ == '__main__':
    unittest.main()
