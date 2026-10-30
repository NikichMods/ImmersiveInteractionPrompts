-- SPDX-License-Identifier: MPL-2.0
-- One borrowed native hint source; never writes a source widget, material or texture.
local M={}
local state=nil
local cvar_baseline=nil
local TIP="/Game/MainContent/Template/UMG/TipHUD.TipHUD_C"
local MAT="/Game/MainContent/Template/UMG/TipIconMat.TipIconMat"
local function log(e,s)print("IIP_HINT event="..e.." "..(s or "").."\n")end
local function valid(o)return o~=nil and o:IsValid()end
local function path(o)return assert(o:GetFullName():match("^[^ ]+ (.+)$"))end
local function cls(o)return path(o:GetClass())end
local function same(a,b)return valid(a) and valid(b) and a:GetAddress()==b:GetAddress()end
local function ref(o)return {path=path(o),class=cls(o),address=o:GetAddress()}end
local function id(o)return path(o).."@"..o:GetAddress()end
local function matches(o,r)return valid(o) and path(o)==r.path and cls(o)==r.class and o:GetAddress()==r.address end
local function api(p)
 local f=StaticFindObject(p)
 assert(valid(f) and f:type()=="UFunction" and f:GetFullName()=="Function "..p,"hint API unavailable: "..p)
 return f
end
local function sys(name,...)
 local f=api("/Script/Engine.KismetSystemLibrary:"..name)
 local cdo=StaticFindObject("/Script/Engine.Default__KismetSystemLibrary")
 assert(valid(cdo) and cls(cdo)=="/Script/Engine.KismetSystemLibrary","Kismet system CDO unavailable")
 return f(cdo,...)
end
local function alive(o)return valid(o) and sys("IsValid",o)==true end
local function finite(n)return type(n)=="number" and n==n and math.abs(n)<math.huge end
local function source(w)
 local isvalid=api("/Script/Engine.KismetSystemLibrary:IsValid")
 local cdo=StaticFindObject("/Script/Engine.Default__KismetSystemLibrary")
 assert(valid(cdo) and cls(cdo)=="/Script/Engine.KismetSystemLibrary","native validity CDO unavailable")
 local function alive(o)return valid(o) and isvalid(cdo,o)==true end
 local function visible(o)
  assert(alive(o) and (o.Visibility==0 or o.Visibility==3 or o.Visibility==4)
   and o.RenderOpacity==1 and o.bIsEnabled==true,"hint source hidden/faded/disabled")
 end
 visible(w);assert(cls(w)==TIP,"unexpected hint owner")
 local tree=w.WidgetTree;assert(alive(tree) and cls(tree)=="/Script/UMG.WidgetTree","hint tree missing")
 local r=StaticFindObject(path(tree)..".RetainerBox_0")
 visible(r);assert(cls(r)=="/Script/UMG.RetainerBox" and same(r:GetOuter(),tree),"hint Retainer identity")
 local chain=r
 for i=1,8 do
  visible(chain)
  local parent=chain:GetParent()
  if not valid(parent)then assert(same(chain,tree.RootWidget),"hint ancestry root mismatch");break end
  assert(i<8,"hint ancestry bound");chain=parent
 end
 assert(r:GetChildrenCount()==1,"unsupported hint child count")
 local child=r:GetChildAt(0);visible(child)
 assert(cls(child)=="/Script/UMG.Image" and same(child:GetParent(),r),"unsupported native hint leaf")
 local slot=r.Slot
 assert(alive(slot) and cls(slot)=="/Script/UMG.CanvasPanelSlot" and same(slot.Content,r)
  and same(slot.Parent,r:GetParent()),"native hint slot changed")
 local size=slot:GetSize()
 assert(finite(size.X) and finite(size.Y) and size.X>=16 and size.X<=96 and size.Y>=16 and size.Y<=96,"unsupported hint dimensions")
 local pc=w:GetOwningPlayer();assert(alive(pc),"hint owning player missing")
 local c=pc:GetClass();local controller=false
 for _=1,32 do
  if not valid(c)then break end
  if path(c)=="/Script/Genesis.GenesisPlayerController"then controller=true;break end
  c=c:GetSuperStruct()
 end
 assert(controller,"unsupported hint player class")
 local device=pc:GetNowInputControllerType()
 assert(math.type(device)=="integer" and device>=1 and device<=5,"unknown/default input device")
 local global=sys("GetConsoleVariableIntValue","Slate.EnableRetainedRendering")
 -- Shipping Slate does not register the development-only cvar refresh delegate.
 -- Zero is also the getter's missing-cvar result: do not infer a safe mode from it.
 assert(global==1 and global==cvar_baseline,"unsupported/changed global retainer mode")
 assert(type(r.bRetainRender)=="boolean","retainer desire unavailable")
 local result={retainer=r,child=child,size=size,device=device,player=pc,retained=r.bRetainRender,
  brush=child.Brush,phase=r.Phase,phases=r.PhaseCount,render_phase=r.RenderOnPhase,render_invalid=r.RenderOnInvalidation}
 if r.bRetainRender then
  assert(r.TextureParameter:ToString()=="Icon" and r.RenderOnPhase==true and r.PhaseCount==1 and r.Phase==0,"unsupported retained render schedule/parameter")
  local mid=r:GetEffectMaterial()
  assert(alive(mid) and cls(mid)=="/Script/Engine.MaterialInstanceDynamic","native effect MID not ready")
  local parent=mid.Parent
  assert(alive(parent) and cls(parent)=="/Script/Engine.Material" and path(parent)==MAT and parent.MaterialDomain==5,"unsupported native hint material")
  local tex=mid:K2_GetTextureParameterValue(FName("Icon"))
  assert(alive(tex) and cls(tex)=="/Script/Engine.TextureRenderTarget2D","Icon final render target not ready")
  assert(finite(tex.SizeX) and finite(tex.SizeY) and tex.SizeX>=1 and tex.SizeX<=1024 and tex.SizeY>=1 and tex.SizeY<=1024,"unsupported Icon target size")
  assert(type(tex.bForceLinearGamma)=="boolean" and math.type(tex.RenderTargetFormat)=="integer"
   and math.type(parent.BlendMode)=="integer","hint gamma/blend metadata unavailable")
  result.mode="retained_mid";result.resource=mid;result.texture=tex
  result.extra=" Icon_rt="..tex.SizeX.."x"..tex.SizeY.." linear_gamma="..tostring(tex.bForceLinearGamma)
   .." rt_format="..tostring(tex.RenderTargetFormat).." source_blend="..tostring(parent.BlendMode)
 else
  local b=child.Brush;local tex=b.ResourceObject
  assert(alive(tex) and cls(tex)=="/Script/Engine.Texture2D" and child.bFlipForRightToLeftFlowDirection==false,"unsupported inactive-retainer brush")
  assert(b.DrawAs==3 and finite(b.ImageSize.X) and finite(b.ImageSize.Y) and b.ImageSize.X>0 and b.ImageSize.Y>0,"unsupported child image brush")
  assert(b.TintColor.ColorUseRule==0,"unsupported inherited child brush tint")
  local t=child.RenderTransform
  assert(t.Translation.X==0 and t.Translation.Y==0 and t.Scale.X==1 and t.Scale.Y==1
   and t.Shear.X==0 and t.Shear.Y==0 and t.Angle==0,"unsupported child image transform")
  result.mode="child_brush";result.resource=tex;result.texture=tex
  result.extra=" brush_size="..b.ImageSize.X.."x"..b.ImageSize.Y.." DrawAs="..b.DrawAs.." tint_rule="..b.TintColor.ColorUseRule
 end
 result.key=result.mode.."|"..id(r).."|"..id(child).."|"..id(pc).."|"..device.."|"..id(result.resource).."|"..id(result.texture).."|"..size.X..","..size.Y.."|"..result.extra
 result.description="mode="..result.mode.." device="..device.." retained="..tostring(r.bRetainRender)
  .." global=1 retainer="..string.format("%q",id(r)).." child="..string.format("%q",id(child))
  .." brush="..tostring(result.brush:GetStructAddress())
  .." resource="..string.format("%q",id(result.resource)).." texture="..string.format("%q",id(result.texture))
  .." slot="..size.X.."x"..size.Y.." phase="..tostring(r.Phase).."/"..tostring(r.PhaseCount)
  .." on_phase="..tostring(r.RenderOnPhase).." on_invalidation="..tostring(r.RenderOnInvalidation)..result.extra
 return result
end
function M.prepare()
 for _,p in ipairs({"/Script/UMG.RetainerBox:GetEffectMaterial","/Script/UMG.Image:SetBrushFromMaterial",
  "/Script/UMG.Image:SetBrush","/Script/UMG.Image:SetBrushResourceObject",
  "/Script/Engine.MaterialInstanceDynamic:K2_GetTextureParameterValue",
  "/Script/Engine.KismetSystemLibrary:GetConsoleVariableIntValue","/Script/UMG.Widget:GetOwningPlayer",
  "/Script/Genesis.GenesisPlayerController:GetNowInputControllerType"})do api(p)end
 cvar_baseline=sys("GetConsoleVariableIntValue","Slate.EnableRetainedRendering")
 assert(cvar_baseline==1,"unsupported or missing global retainer cvar")
end
function M.preflight(w)
 local s=source(w);log("PREFLIGHT",s.description.." original_read_only=true")
end
local function own(image)
 assert(alive(image) and cls(image)=="/Script/UMG.Image","own mirror missing/pending kill")
 if state then
  assert(matches(image,state.image) and matches(image:GetOuter(),state.tree)
   and matches(image:GetParent(),state.root),"own mirror ownership changed")
 end
 local slot=image.Slot
 assert(alive(slot) and same(slot.Content,image) and same(slot.Parent,image:GetParent()),"own mirror slot changed")
 return slot
end
function M.start(w,image)
 assert(state==nil,"one hint instance only")
 local slot=own(image)
 assert(not same(image:GetOuter(),w.WidgetTree),"original/own tree alias")
 assert(image.Brush.DrawAs==3 and not valid(image.Brush.ResourceObject),"own image defaults differ")
 state={image=ref(image),tree=ref(image:GetOuter()),root=ref(image:GetParent()),original=ref(w),
  frames=0,changes=0,stable=0,pending=nil,bound=nil,description="unbound"}
 image:SetVisibility(1)
 M.update(w,image)
end
function M.update(w,image)
 assert(state and matches(w,state.original),"original hint widget changed")
 local slot=own(image);local st=state
 local ok,s=pcall(source,w)
 if not ok then
  st.bound=nil;image:SetVisibility(1);image:SetBrushResourceObject(nil)
  error(s) -- Fail closed immediately, before queued component cleanup.
 end
 st.frames=st.frames+1
 if s.key~=st.pending then
  image:SetVisibility(1);image:SetBrushResourceObject(nil);st.bound=nil
  st.changes=st.changes+1;assert(st.changes<=8,"hint source-change budget")
  st.pending=s.key;st.bound=nil;st.stable=1;st.description=s.description
  log("SOURCE_PENDING","change="..st.changes.." "..s.description.." own_hidden=true")
  return
 end
 st.stable=st.stable+1
 if st.stable<3 then return end -- Two frame boundaries, not proof that GPU pixels are fresh.
 local changed=st.bound~=s.key
 if s.mode=="retained_mid" then
  if changed then
   image:SetBrushFromMaterial(s.resource)
   image:SetColorAndOpacity({R=1,G=1,B=1,A=1})
  end
 else
  image:SetBrush(s.brush);image:SetColorAndOpacity(s.child.ColorAndOpacity)
  assert(image.Brush:GetStructAddress()~=s.brush:GetStructAddress(),"child/own brush storage alias")
 end
 if changed then slot:SetSize({X=s.size.X,Y=s.size.Y})end
 assert(same(image.Brush.ResourceObject,s.resource),"own hint resource readback differs")
 if changed then image:SetVisibility(3)end
 if changed then log("SOURCE_BOUND",s.description.." readonly_reference=true pixel_equivalence_unverified=true")end
 st.bound=s.key;st.description=s.description
end
function M.sample(reason)
 if not state then return end
 local w=StaticFindObject(state.original.path);assert(matches(w,state.original),"sample owner changed")
 local s=source(w)
 log("SAMPLE","reason="..reason.." bound="..tostring(state.bound==s.key).." "..s.description)
end
function M.summary(reason)
 if state then log("SUMMARY","reason="..reason.." frames="..state.frames.." sources="..state.changes.." bound="..tostring(state.bound~=nil))end
end
function M.cleanup(image)
 if alive(image)then
  if state then assert(matches(image,state.image) and matches(image:GetOuter(),state.tree),"cleanup own image identity changed")end
  assert(cls(image)=="/Script/UMG.Image","cleanup own image type")
  image:SetVisibility(1);image:SetBrushResourceObject(nil)
  assert(not valid(image.Brush.ResourceObject),"own hint resource remains")
 end
 state=nil;log("RELEASED","borrowed_resource_reference=false original_material_unchanged_by_probe=true")
end
return M
