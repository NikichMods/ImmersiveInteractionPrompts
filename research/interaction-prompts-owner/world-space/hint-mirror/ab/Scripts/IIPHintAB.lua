-- SPDX-License-Identifier: MPL-2.0
-- Two bounded readouts and one own-component material change. No source UI writes.
local M={}
local a=nil
local phase="masked"
local frames=0
local inert=false
local native_alive=nil
local requested=false
local function log(e,s)print("IIP_HINT_AB event="..e.." "..s.."\n")end
local function number(n)
 assert(type(n)=="number" and n==n and math.abs(n)<math.huge,"AB non-finite number")
 return n
end
local function fmt(n)return string.format("%.9g",number(n))end
local function vec(v)return fmt(v.X)..","..fmt(v.Y)..","..fmt(v.Z)end
local function color(v)return fmt(v.R)..","..fmt(v.G)..","..fmt(v.B)..","..fmt(v.A)end
local function valid(o)return o~=nil and o:IsValid()end
local function id(o)assert(valid(o),"AB missing object");return o:GetFullName().."@"..o:GetAddress()end
local function api(p)
 local f=StaticFindObject(p)
 assert(valid(f) and f:type()=="UFunction" and f:GetFullName()=="Function "..p,"AB API missing: "..p)
end
function M.prepare(is_alive)
 native_alive=assert(is_alive)
 for _,p in ipairs({"/Script/Engine.PrimitiveComponent:SetMaterial","/Script/Engine.PrimitiveComponent:GetMaterial",
  "/Script/Engine.PlayerController:ProjectWorldLocationToScreen","/Script/Engine.PlayerController:GetViewportSize",
  "/Script/Engine.PlayerCameraManager:GetCameraRotation","/Script/Engine.PlayerCameraManager:GetFOVAngle",
  "/Script/Engine.MaterialInstanceDynamic:K2_GetVectorParameterValue",
  "/Script/Engine.MaterialInstanceDynamic:K2_GetScalarParameterValue",
  "/Script/UMG.CanvasPanelSlot:GetAnchors","/Script/UMG.CanvasPanelSlot:GetAlignment",
  "/Script/UMG.CanvasPanelSlot:GetPosition","/Script/UMG.CanvasPanelSlot:GetAutoSize",
  "/Script/UMG.WidgetComponent:GetPivot"})do api(p)end
 log("PREPARED","screen_geometry=UNAVAILABLE_OPAQUE_FGEOMETRY own_measure=projected_slot_corners samples_max=2 switches_max=1")
end
local function view(w,cam)
 local pc=w:GetOwningPlayer();assert(valid(pc),"AB player missing")
 local x,y={},{};pc:GetViewportSize(x,y)
 local width,height=number(x.SizeX),number(y.SizeY)
 assert(width>0 and height>0,"AB viewport unavailable")
 local loc,rot=cam:GetCameraLocation(),cam:GetCameraRotation()
 local v={pc=id(pc),cam=id(cam),x=number(loc.X),y=number(loc.Y),z=number(loc.Z),
  pitch=number(rot.Pitch),yaw=number(rot.Yaw),roll=number(rot.Roll),fov=number(cam:GetFOVAngle()),width=width,height=height}
 assert(v.fov>1 and v.fov<179,"AB camera FOV outside range")
 return v,pc
end
local function comparable(v)
 assert(v.pc==a.view.pc and v.cam==a.view.cam and v.width==a.view.width and v.height==a.view.height,"AB viewport/player changed")
 for _,k in ipairs({"x","y","z"})do assert(math.abs(v[k]-a.view[k])<=1,"AB camera moved")end
 for _,k in ipairs({"pitch","yaw","roll"})do
  assert(math.abs((v[k]-a.view[k]+180)%360-180)<=0.2,"AB camera rotated")
 end
 assert(math.abs(v.fov-a.view.fov)<=0.01,"AB camera FOV changed")
end
local function projected(c,image,host,pc)
 local slot=image.Slot;local size=slot:GetSize()
 local anchors,align,pos=slot:GetAnchors(),slot:GetAlignment(),slot:GetPosition()
 local pivot=c:GetPivot()
 assert(anchors.Minimum.X==0.5 and anchors.Minimum.Y==0.5 and anchors.Maximum.X==0.5 and anchors.Maximum.Y==0.5
  and align.X==0.5 and align.Y==0.5 and pos.X==0 and pos.Y==0 and not slot:GetAutoSize()
  and pivot.X==0.5 and pivot.Y==0.5,"AB slot no longer centered")
 for _,o in ipairs({image,image:GetParent(),host})do
  local t=o.RenderTransform
  assert(t.Translation.X==0 and t.Translation.Y==0 and t.Scale.X==1 and t.Scale.Y==1
   and t.Shear.X==0 and t.Shear.Y==0 and t.Angle==0,"AB own layout transformed")
 end
 local p,r,s=c:K2_GetComponentLocation(),c:K2_GetComponentRotation(),c:K2_GetComponentScale()
 assert(math.abs(r.Pitch)<=0.001 and math.abs(r.Roll)<=0.001,"AB nonvertical plane")
 local sn,cs=math.sin(math.rad(r.Yaw)),math.cos(math.rad(r.Yaw))
 local minx,miny,maxx,maxy=math.huge,math.huge,-math.huge,-math.huge
 local corners={}
 for _,q in ipairs({{-1,-1},{1,-1},{1,1},{-1,1}})do
  -- UE4.27 plane vertex = -FVector(0,U,V). Vertical yaw preserves world Z.
  local u,v=q[1]*number(size.X)/2,q[2]*number(size.Y)/2
  local point={X=p.X+sn*u*s.Y,Y=p.Y-cs*u*s.Y,Z=p.Z-v*s.Z}
  local out={};assert(pc:ProjectWorldLocationToScreen(point,out,false)==true,"AB projection failed/behind camera")
  local x,y=number(out.X),number(out.Y)
  corners[#corners+1]=fmt(x)..","..fmt(y)
  minx,miny,maxx,maxy=math.min(minx,x),math.min(miny,y),math.max(maxx,x),math.max(maxy,y)
 end
 assert(maxx>minx and maxy>miny,"AB projected slot degenerate")
 return " own_slot_units="..fmt(size.X)..","..fmt(size.Y).." own_slot_world="..fmt(size.X*s.Y)..","..fmt(size.Y*s.Z)
  .." own_slot_bbox_px="..fmt(minx)..","..fmt(miny)..","..fmt(maxx)..","..fmt(maxy)
  .." own_slot_size_px="..fmt(maxx-minx)..","..fmt(maxy-miny).." own_slot_corners_px="..table.concat(corners,";")
end
local function settings(c,image,host,rt,mid)
 assert(type(c.bApplyGammaCorrection)=="boolean" and type(rt.sRGB)=="boolean" and type(rt.bForceLinearGamma)=="boolean",
  "AB reflected gamma flags missing")
 assert(rt.SizeX==512 and rt.SizeY==128,"AB RT extent changed")
 assert(image.ColorAndOpacity.R==1 and image.ColorAndOpacity.G==1 and image.ColorAndOpacity.B==1
  and image.ColorAndOpacity.A==1 and image.RenderOpacity==1 and host.RenderOpacity==1,"AB own opacity/tint differs")
 assert(native_alive(rt) and native_alive(mid) and mid:GetOuter():GetAddress()==c:GetAddress()
  and mid.Parent:GetAddress()==c:GetMaterial(0):GetAddress(),"AB effective MID parent/owner differs")
 assert(mid:K2_GetTextureParameterValue(FName("SlateUI")):GetAddress()==rt:GetAddress(),"AB SlateUI binding differs")
 -- Read only the component-owned MID; never set any source or output parameter.
 return "gamma="..tostring(c.bApplyGammaCorrection).." rt_srgb="..tostring(rt.sRGB)
  .." rt_linear="..tostring(rt.bForceLinearGamma).." rt_gamma="..fmt(rt.TargetGamma).." rt_format="..fmt(rt.RenderTargetFormat)
  .." rt_clear="..color(rt.ClearColor).." component_background="..color(c.BackgroundColor)
  .." component_tint="..color(c.TintColorAndOpacity).." component_opacity="..fmt(c.OpacityFromTexture)
  .." effective_tint="..color(mid:K2_GetVectorParameterValue(FName("TintColorAndOpacity")))
  .." effective_backcolor="..color(mid:K2_GetVectorParameterValue(FName("BackColor")))
  .." effective_opacity="..fmt(mid:K2_GetScalarParameterValue(FName("OpacityFromTexture")))
  .." image_tint="..color(image.ColorAndOpacity).." image_opacity="..fmt(image.RenderOpacity)
  .." host_opacity="..fmt(host.RenderOpacity)
end
function M.frame(c,image,host,w,cam,hint)
 if not M.needs_sample()then return end
 frames=frames+1;if frames<3 or not hint then return end -- Frame boundaries, not a GPU-completion claim.
 local rt=c:GetRenderTarget();if not valid(rt)then return end
 local v,pc=view(w,cam);local mid=c:GetMaterialInstance()
 local config=settings(c,image,host,rt,mid)
 local geometry=vec(c:K2_GetComponentLocation()).."|"..vec(c:K2_GetComponentScale())
 local projection=projected(c,image,host,pc)
 assert(c.BlendMode==(phase=="masked" and 1 or 2),"AB component blend differs")
 local mat=c:GetMaterial(0);local o=mat.BasePropertyOverrides
 assert(o.bOverride_BlendMode and o.BlendMode==(phase=="masked" and 1 or 2)
  and o.bOverride_TwoSided and o.TwoSided and mat.Parent.bDisableDepthTest==false,"AB effective stock material differs")
 if a then
  comparable(v)
  assert(a.source==hint.key and a.generation==hint.generation,"AB hint changed between samples")
  assert(a.config==config and a.geometry==geometry and a.rt==id(rt) and a.component==id(c),"AB settings/RT/component changed")
 else a={view=v,source=hint.key,generation=hint.generation,config=config,geometry=geometry,rt=id(rt),component=id(c),material=id(mat)}end
 log("SAMPLE","mode="..phase.." material="..string.format("%q",id(mat)).." mid="..string.format("%q",id(mid))
  .." component_blend="..c.BlendMode.." world_blend="..o.BlendMode.." two_sided="..tostring(o.TwoSided)
  .." depth_disable="..tostring(mat.Parent.bDisableDepthTest)
  .." rt="..string.format("%q",id(rt)).." source="..string.format("%q",hint.key).." generation="..hint.generation
  .." "..config..projection.." source_screen_px=UNAVAILABLE screenshot_required=true"
  .." camera="..fmt(v.x)..","..fmt(v.y)..","..fmt(v.z).." camera_pyr="..fmt(v.pitch)..","..fmt(v.yaw)..","..fmt(v.roll)
  .." fov="..fmt(v.fov).." viewport="..v.width..","..v.height)
 if phase=="translucent" then phase="done";log("PAIR_READY","snapshots=2 pixel_equivalence_unverified=true F7_cleanup_required=true")end
end
function M.switch(c,w,cam,hint,stock)
 if inert or phase~="masked" or not a then log("SWITCH_IGNORED","reason=not_ready_or_already_switched");return false end
 local v=view(w,cam);comparable(v)
 assert(hint and a.source==hint.key and a.generation==hint.generation,"AB source no longer matches baseline")
 assert(a.component==id(c),"AB foreign component")
 assert(c.BlendMode==1 and id(c:GetMaterial(0))==a.material,"AB baseline material changed")
 phase="translucent";frames=0 -- Consume the single switch before native mutation.
 log("PHASE","name=own_material_switch edge=BEGIN component="..string.format("%q",id(c)))
 c.BlendMode=2 -- Reflected EWidgetBlendMode; SetBlendMode itself is NOT a UFunction.
 c:SetMaterial(0,stock) -- Native virtual override rebuilds own MID and marks render state dirty.
 assert(c.BlendMode==2 and c:GetMaterial(0):GetAddress()==stock:GetAddress()
  and c:GetMaterialInstance().Parent:GetAddress()==stock:GetAddress(),"AB material switch readback differs")
 log("PHASE","name=own_material_switch edge=END material="..string.format("%q",id(stock)))
 return true
end
function M.clear()inert=true end
function M.request_baseline()
 if inert or requested then return end
 requested=true;frames=0
 log("BASELINE_REQUESTED","mode=masked wait_frames=3 freeze_camera=true")
end
function M.needs_sample()return not inert and requested and phase~="done" and not (phase=="masked" and a)end
return M
