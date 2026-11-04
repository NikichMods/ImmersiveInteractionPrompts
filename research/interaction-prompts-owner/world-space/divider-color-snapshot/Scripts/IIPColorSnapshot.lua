-- SPDX-License-Identifier: MPL-2.0
-- One metadata snapshot. No setters, raw memory, pixel readback or gamma diagnosis.
local M={}
local done=false
local waits=0
local function log(scope,s)
 print("IIP_COLOR event=SNAPSHOT id=1 scope="..scope.." candidate=divider-color-snapshot-20261105 "..s.."\n")
end
local function valid(o)return o~=nil and o:IsValid()end
local function same(a,b)return valid(a) and valid(b) and a:GetAddress()==b:GetAddress()end
local function class(o)return o:GetClass():GetFullName()end
local function attempt(fn)
 local ok,v=pcall(fn)
 if ok then return v,true end
 return nil,false
end
local function number(v)
 assert(type(v)=="number" and v==v and math.abs(v)<math.huge)
 return string.format("%.9g",v)
end
local function boolean(v)assert(type(v)=="boolean");return tostring(v)end
local function color(v)return number(v.R)..","..number(v.G)..","..number(v.B)..","..number(v.A)end
local function identity(o)
 assert(valid(o));return string.format("%q",o:GetFullName().."@"..o:GetAddress())
end
local function value(fn,format)
 local v,ok=attempt(function()return (format or number)(fn())end)
 return ok and v or "UNAVAILABLE"
end
local function field(o,k,format)return value(function()return o[k]end,format)end
local function target(rt)
 return "SizeX="..field(rt,"SizeX").." SizeY="..field(rt,"SizeY")
  .." sRGB="..field(rt,"sRGB",boolean).." TargetGamma="..field(rt,"TargetGamma")
  .." bForceLinearGamma="..field(rt,"bForceLinearGamma",boolean)
  .." RenderTargetFormat_enum="..field(rt,"RenderTargetFormat")
  .." OverrideFormat_enum="..field(rt,"OverrideFormat").." ClearColor="..field(rt,"ClearColor",color)
  .." RHI_pixel_format=UNKNOWN"
end
local function vector(mid,name)
 return value(function()return mid:K2_GetVectorParameterValue(FName(name))end,color)
end
function M.frame(c,w,read_source,alive)
 if done then return end
 local rt,available=attempt(function()return c:GetRenderTarget()end)
 if not available then
  done=true;log("unavailable","reason=own_rt_getter_UNAVAILABLE");return
 end
 if not valid(rt)then
  waits=waits+1
  if waits>=8 then done=true;log("unavailable","reason=own_rt_not_ready visible_checks=8 session_continues=true")end
  return -- Only while the same native hint is visible/ready. No timer or session deadline.
 end
 done=true -- Consume before native reads; never retry a partial/failed snapshot.
 -- Real topology/ownership failures remain fatal to the existing guarded lifecycle.
 assert(alive(rt) and class(rt)=="Class /Script/Engine.TextureRenderTarget2D"
  and same(rt:GetOuter(),c),"color snapshot: own RT identity/owner changed")
 local native=read_source(w) -- Reuses the existing strict, read-only source identity guards.
 local mid=attempt(function()return c:GetMaterialInstance()end)
 local binding="UNAVAILABLE"
 if valid(mid)then
  assert(alive(mid) and class(mid)=="Class /Script/Engine.MaterialInstanceDynamic"
   and same(mid:GetOuter(),c),"color snapshot: own MID identity/owner changed")
  assert(same(mid.Parent,c:GetMaterial(0)),"color snapshot: own MID parent changed")
  local bound,ok=attempt(function()return mid:K2_GetTextureParameterValue(FName("SlateUI"))end)
  if ok then
   assert(same(bound,rt),"color snapshot: own SlateUI binding differs")
   binding="own_rt"
  end
 end
 log("component","object="..identity(c).." bApplyGammaCorrection="..field(c,"bApplyGammaCorrection",boolean)
  .." BlendMode_enum="..field(c,"BlendMode").." BackgroundColor="..field(c,"BackgroundColor",color)
  .." TintColorAndOpacity="..field(c,"TintColorAndOpacity",color).." OpacityFromTexture="..field(c,"OpacityFromTexture"))
 log("own_rt","object="..identity(rt).." "..target(rt))
 log("own_mid","object="..value(function()return mid end,identity)
  .." Outer="..value(function()return mid:GetOuter()end,identity)
  .." Parent="..value(function()return mid.Parent end,identity).." SlateUI="..binding
  .." TintColorAndOpacity="..vector(mid,"TintColorAndOpacity").." BackColor="..vector(mid,"BackColor")
  .." OpacityFromTexture="..value(function()return mid:K2_GetScalarParameterValue(FName("OpacityFromTexture"))end))
 local retained=native.mode=="retained_mid"
 local nmid=retained and native.resource or nil
 local nrt=retained and native.texture or nil
 log("native","retainer="..identity(native.retainer).." retained="..tostring(native.retained)
  .." mid="..value(function()return nmid end,identity)
  .." Outer="..value(function()return nmid:GetOuter()end,identity)
  .." Parent="..value(function()return nmid.Parent end,identity)
  .." material_blend_enum="..value(function()return nmid.Parent.BlendMode end)
  .." Icon="..value(function()return nrt end,identity).." "..target(nrt)
  .." retainer_opacity="..field(native.retainer,"RenderOpacity")
  .." child_tint="..field(native.child,"ColorAndOpacity",color)
  .." effective_tint_back_opacity=UNAVAILABLE_parameter_contract_not_established"
  .." renderer_gamma=UNAVAILABLE_internal unmodified=true complete=true")
end
return M
