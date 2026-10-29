-- SPDX-License-Identifier: MPL-2.0
-- One owned native World renderer. No asset authoring or original UI writes.
local M={}
local HOST="/Game/MainContent/Template/UMG/Debug/PostionItemUMG_BP.PostionItemUMG_BP_C"
local MASK="/Engine/EngineMaterials/Widget3DPassThrough_Masked.Widget3DPassThrough_Masked"
local BASEMAT="/Engine/EngineMaterials/Widget3DPassThrough.Widget3DPassThrough"
local state=nil
local function log(e,s)print("IIP_WORLD event="..e.." "..(s or "").."\n")end
local function valid(o)return o~=nil and o:IsValid()end
local function path(o)return assert(o:GetFullName():match("^[^ ]+ (.+)$"))end
local function cls(o)return path(o:GetClass())end
local function same(a,b)return valid(a) and valid(b) and a:GetAddress()==b:GetAddress()end
local function ref(o)return {path=path(o),class=cls(o),address=o:GetAddress()}end
local function find(r)
 if not r then return nil end
 local o=StaticFindObject(r.path)
 if not valid(o)then return nil end
 assert(path(o)==r.path and cls(o)==r.class and o:GetAddress()==r.address,"own/foreign identity changed")
 return o
end
local function static(p,library,...)
 local f=StaticFindObject(p);local cdo=StaticFindObject("/Script/Engine.Default__"..library)
 assert(valid(f) and f:type()=="UFunction" and f:GetFullName()=="Function "..p and valid(cdo)
  and cls(cdo)=="/Script/Engine."..library,"static API unavailable: "..p)
 return f(cdo,...)
end
local function alive(o)
 return valid(o) and static("/Script/Engine.KismetSystemLibrary:IsValid","KismetSystemLibrary",o)==true
end
local function asset(p)
 local o=StaticFindObject(p)
 if not valid(o)then
  local loaded,found,did_load=LoadAsset(p)
  assert(found==true and did_load==true and valid(loaded),"asset NOT_LOADED: "..p)
  o=StaticFindObject(p);assert(same(o,loaded),"asset lookup/load mismatch")
 end
 assert(path(o)==p,"asset identity differs");return o
end
local function xyz(v)return {X=v.X,Y=v.Y,Z=v.Z}end
local function finite(v)
 for _,n in pairs(v)do assert(type(n)=="number" and n==n and n~=math.huge and n~=-math.huge,"non-finite value")end
 return v
end
local function vector(v)return string.format("%.9g,%.9g,%.9g",v.X,v.Y,v.Z)end
local function size(v,x,y)return v.X==x and v.Y==y end
local function material(m)
 assert(valid(m) and path(m)==MASK and cls(m)=="/Script/Engine.MaterialInstanceConstant","wrong stock material")
 local b=m.Parent;local o=m.BasePropertyOverrides
 assert(valid(b) and path(b)==BASEMAT and cls(b)=="/Script/Engine.Material"
  and b.bDisableDepthTest==false,"stock depth contract differs")
 assert(o.bOverride_BlendMode==true and o.BlendMode==1 and o.bOverride_TwoSided==true
  and o.TwoSided==true,"expected masked/two-sided stock instance")
end
local function original(s)
 local a,c,w=find(s.actor),find(s.source),find(s.original)
 assert(alive(a) and alive(c) and alive(w),"original target gone")
 assert(same(a.RootComponent,find(s.actor_root)) and same(a.ExtendedWidget,c)
  and same(c:GetOwner(),a) and same(c:GetWidget(),w),"original owner/root/widget changed")
 assert(same(w.WidgetTree,find(s.original_tree)) and same(w.TextBlock_89,find(s.original_text)),"original UI identity changed")
 local now=finite(xyz(c:K2_GetComponentLocation()))
 assert(math.abs(now.X-s.anchor.X)<0.01 and math.abs(now.Y-s.anchor.Y)<0.01
  and math.abs(now.Z-s.anchor.Z)<0.01,"source anchor moved; fixed-pose experiment stops")
 return a,c,w
end
local function own_tree(w)
 local t=w.WidgetTree;local r=valid(t) and t.RootWidget or nil
 assert(valid(t) and cls(t)=="/Script/UMG.WidgetTree" and same(t:GetOuter(),w),"host tree owner")
 assert(valid(r) and cls(r)=="/Script/UMG.CanvasPanel" and same(r:GetOuter(),t)
  and not valid(r:GetParent()) and r:GetChildrenCount()==1,"host root")
 local main=r:GetChildAt(0);local value,image=w.Value_Text,w.Bg_Image
 assert(valid(main) and cls(main)=="/Script/UMG.CanvasPanel" and main:GetChildrenCount()==2
  and same(main:GetOuter(),t) and same(main:GetParent(),r),"host placeholder")
 assert(valid(value) and cls(value)=="/Script/UMG.TextBlock" and valid(image) and cls(image)=="/Script/UMG.Image","host leaves")
 local seen={}
 for _,o in ipairs({r,main,value,image})do
  assert(not seen[o:GetAddress()] and same(o:GetOuter(),t),"host tree alias");seen[o:GetAddress()]=true
 end
 local children={}
 for i=0,1 do
  local o=main:GetChildAt(i)
  assert((same(o,value) or same(o,image)) and not children[o:GetAddress()]
   and same(o:GetParent(),main) and same(o.Slot.Parent,main) and same(o.Slot.Content,o),"host slot/child differs")
  children[o:GetAddress()]=true
 end
 assert(same(main.Slot.Parent,r) and same(main.Slot.Content,main),"host main slot")
 return t,r,main,value
end
function M.pending()return state~=nil end
function M.cleanup(reason)
 if not state then return true end
 local s=state;s.active=false;s.onstop=nil
 local errors={}
 local function attempt(fn)local ok,err=pcall(fn);if not ok then errors[#errors+1]=tostring(err):sub(1,180)end end
 attempt(function()
  local w=find(s.host);if alive(w)then w:SetVisibility(1)end
  local label=find(s.label)
  if alive(label)then
   assert(same(label:GetOuter(),find(s.tree)),"own label tree changed")
   local parent=label:GetParent()
   if valid(parent)then assert(same(parent,find(s.root)),"own label parent changed");assert(parent:RemoveChild(label),"own label detach failed")end
  end
 end)
 attempt(function()
  local c=find(s.component)
  if alive(c)then
   local w=find(s.host);local bound=c:GetWidget()
   assert(not valid(bound) or same(bound,w),"foreign widget rebound to own component; refuse detach")
   c:SetWidget(nil);assert(not valid(c:GetWidget()),"own widget holder remains")
   c:K2_DestroyComponent(c) -- Verified self-caller permission, virtual native destruction/release.
   assert(not alive(c),"native component destruction not confirmed")
   log("COMPONENT_DESTROYED","pending_kill_checked=true gc_not_forced=true")
  end
 end)
 attempt(function()
  local w=find(s.host)
  if alive(w)then w:RemoveFromParent();assert(not w:IsInViewport() and not valid(w:GetParent()),"own host still attached")end
 end)
 if #errors>0 then log("CLEANUP_PENDING",table.concat(errors," | "));return false end
 state=nil;log("CLEANED","reason="..reason.." own_widget_holder=false own_component_alive=false gc_not_forced=true")
 return true
end
function M.validate()
 local s=state;if not s or not s.active then return end
 original(s)
 local c=find(s.component);local w=find(s.host)
 assert(alive(c) and alive(w) and same(c:GetWidget(),w),"own component/host gone or rebound")
end
function M.sample(reason)
 local s=state;if not s or not s.active then return end
 M.validate()
 local c,w=find(s.component),find(s.host)
 assert(c:GetWidgetSpace()==0 and c:GetCollisionEnabled()==0 and c:GetGenerateOverlapEvents()==false
  and c.bReceiveHardwareInput==false and c:GetWindowFocusable()==false,"own safety state changed")
 assert(w.Visibility==3 and c.bVisible==true and c.bHiddenInGame==false,"own visible state changed")
 assert(size(c:GetDrawSize(),512,128) and size(c:GetCurrentDrawSize(),512,128),"own draw size changed")
 local m=find(s.material);material(m)
 local mid=c:GetMaterialInstance();assert(alive(mid) and same(mid:GetOuter(),c) and same(mid.Parent,m),"own MID parent/owner")
 local rt=c:GetRenderTarget()
 if not alive(rt)then log("RENDER_PENDING","reason="..reason.." visibility=3 space=0 no_render_success_claim=true");return end
 assert(rt.SizeX==512 and rt.SizeY==128,"render target size differs")
 local p=finite(xyz(c:K2_GetComponentLocation()))
 assert(math.abs(p.X-s.position.X)<0.01 and math.abs(p.Y-s.position.Y)<0.01
  and math.abs(p.Z-s.position.Z)<0.01,"own fixed position changed")
 local r=c:K2_GetComponentRotation();finite({Pitch=r.Pitch,Yaw=r.Yaw,Roll=r.Roll})
 local scale=finite(xyz(c:K2_GetComponentScale()))
 assert(math.abs(scale.X-0.25)<0.0001 and math.abs(scale.Y-0.25)<0.0001
  and math.abs(scale.Z-0.25)<0.0001,"own scale changed")
 log("STATE","reason="..reason.." component="..string.format("%q",path(c)).." render_target="..rt:GetAddress()
  .." rt=512x128 visibility=3 hidden_in_game=false space=0 collision=0 overlap=false hardware=false focus=false"
  .." material=stock_masked depth_disable=false fixed_world="..vector(p)
  .." rotation_pyr="..string.format("%.9g,%.9g,%.9g",r.Pitch,r.Yaw,r.Roll).." scale="..vector(scale).." original_writes=0")
end
function M.create(actor,source,w,onstop)
 assert(state==nil,"one own World composition only")
 for _,name in ipairs({"StaticConstructObject","LoadAsset","ExecuteInGameThreadWithDelay"})do
  assert(type(_G[name])=="function","missing World API: "..name)
 end
 assert(FName~=nil and FText~=nil,"name/text constructors unavailable") -- Pinned callable userdata, not plain functions.
 assert(type(EObjectFlags.RF_Transient)=="number","transient flag unavailable")
 local anchor=finite(xyz(source:K2_GetComponentLocation()))
 local cam=w:GetOwningPlayerCameraManager();assert(alive(cam),"camera manager unavailable")
 local camera=finite(xyz(cam:GetCameraLocation()))
 local position={X=anchor.X,Y=anchor.Y,Z=anchor.Z+32} -- One quad height above anchor; separate stock overlay.
 local dx,dy,dz=camera.X-position.X,camera.Y-position.Y,camera.Z-position.Z
 local distance=math.sqrt(dx*dx+dy*dy+dz*dz);assert(distance>=80 and distance<=1500,"camera distance outside first-test envelope")
 local rot=static("/Script/Engine.KismetMathLibrary:FindLookAtRotation","KismetMathLibrary",position,camera)
 finite({Pitch=rot.Pitch,Yaw=rot.Yaw,Roll=rot.Roll})
 local transform=static("/Script/Engine.KismetMathLibrary:MakeTransform","KismetMathLibrary",position,rot,{X=0.25,Y=0.25,Z=0.25})
 local host_class=asset(HOST);assert(host_class:type()=="UClass" and path(host_class:GetSuperStruct())=="/Script/UMG.UserWidget","host class differs")
 local stock=asset(MASK);material(stock)
 local component_class=StaticFindObject("/Script/UMG.WidgetComponent")
 assert(valid(component_class) and component_class:type()=="UClass","WidgetComponent NOT_LOADED")
 local s={active=true,onstop=onstop,actor=ref(actor),source=ref(source),original=ref(w),actor_root=ref(actor.RootComponent),
  original_tree=ref(w.WidgetTree),original_text=ref(w.TextBlock_89),anchor=anchor,position=position,material=ref(stock)}
 state=s
 local name="IIP_WorldTest_"..os.time()
 assert(not valid(StaticFindObject(path(actor).."."..name)),"own component name collision")
 local c=StaticConstructObject(component_class,actor,FName(name),EObjectFlags.RF_Transient)
 assert(alive(c) and cls(c)=="/Script/UMG.WidgetComponent" and same(c:GetOuter(),actor)
  and same(c:GetOwner(),actor) and not same(c,source),"own component factory differs")
 s.component=ref(c)
 assert(c:HasAnyFlags(EObjectFlags.RF_Transient) and c.CreationMethod==0 and not valid(c.WidgetClass)
  and not valid(c:GetWidget()) and not valid(c:GetRenderTarget()),"unexpected component initial state")
 c:SetWidgetSpace(0);assert(c.BlendMode==1 and c.GeometryMode==0,"expected native masked/plane defaults")
 c:SetTwoSided(true);c:SetDrawSize({X=512,Y=128});c:SetPivot({X=0.5,Y=0.5})
 c:SetCollisionEnabled(0);c:SetGenerateOverlapEvents(false);c.bReceiveHardwareInput=false
 c:SetWindowFocusable(false);c:SetTickWhenOffscreen(true);c:SetMaterial(0,stock)
 assert(same(c:GetMaterial(0),stock) and c:GetCollisionEnabled()==0 and not c:GetGenerateOverlapEvents()
  and not c.bReceiveHardwareInput and not c:GetWindowFocusable(),"pre-registration guards differ")
 local create=StaticFindObject("/Script/UMG.WidgetBlueprintLibrary:Create")
 local cdo=StaticFindObject("/Script/UMG.Default__WidgetBlueprintLibrary")
 assert(valid(create) and create:type()=="UFunction" and create:GetFullName()=="Function /Script/UMG.WidgetBlueprintLibrary:Create"
  and valid(cdo) and cls(cdo)=="/Script/UMG.WidgetBlueprintLibrary","Create unavailable")
 local host=create(cdo,w,host_class,nil)
 assert(alive(host) and cls(host)==HOST and not same(host,w)
  and not host:HasAnyFlags(EObjectFlags.RF_ClassDefaultObject|EObjectFlags.RF_ArchetypeObject),"fresh host factory differs")
 s.host=ref(host)
 c:SetWidget(host) -- Own native UPROPERTY/Slate holder before any deferred callback.
 assert(same(c:GetWidget(),host) and host.Visibility==2,"first own Slate/Construct Hidden differs")
 local tree,root,main,value=own_tree(host);s.tree,s.root=ref(tree),ref(root)
 assert(not same(tree,w.WidgetTree),"original tree alias");main:SetVisibility(1);host.bIsFocusable=false
 local text_class=StaticFindObject("/Script/UMG.TextBlock");assert(valid(text_class) and text_class:type()=="UClass","TextBlock unavailable")
 local label=StaticConstructObject(text_class,tree,FName(name.."_Label"),EObjectFlags.RF_Transient)
 assert(alive(label) and cls(label)=="/Script/UMG.TextBlock" and same(label:GetOuter(),tree),"own label factory")
 s.label=ref(label);label:SetFont(value.Font);assert(label.Font:GetStructAddress()~=value.Font:GetStructAddress(),"FontInfo alias")
 label.Font.Size=36;label:SetFont(label.Font);label:SetJustification(1);label:SetText(FText("WORLD TEST"));label:SetVisibility(3)
 label:SetColorAndOpacity({SpecifiedColor={R=0.1,G=1,B=1,A=1},ColorUseRule=0})
 local slot=root:AddChildToCanvas(label);assert(valid(slot) and same(slot.Parent,root) and same(slot.Content,label),"own label slot")
 slot:SetAnchors({Minimum={X=0.5,Y=0.5},Maximum={X=0.5,Y=0.5}});slot:SetAlignment({X=0.5,Y=0.5})
 slot:SetPosition({X=0,Y=0});slot:SetSize({X=500,Y=60});slot:SetAutoSize(false)
 host:SetVisibility(3)
 actor:FinishAddComponent(c,true,transform) -- Manual attachment; no root promotion; configure before native registration.
 assert(same(actor.RootComponent,find(s.actor_root)) and not valid(c:GetAttachParent()) and c:GetWidgetSpace()==0,"manual registration/root contract")
 original(s)
 log("CREATED","component="..string.format("%q",path(c)).." native_registration_requested=true scale=0.25"
  .." draw=512x128 physical=128x32 offset_world_z=32 fixed_pose=true camera_distance="..string.format("%.3f",distance)
  .." expected_rotation_pyr="..string.format("%.9g,%.9g,%.9g",rot.Pitch,rot.Yaw,rot.Roll))
 ExecuteInGameThreadWithDelay(45000,function()
  if state==s and s.active and s.onstop then s.onstop("world_timeout")end
 end)
end
return M
