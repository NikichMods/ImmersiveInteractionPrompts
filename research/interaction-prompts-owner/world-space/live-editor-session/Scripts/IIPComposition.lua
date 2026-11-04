-- SPDX-License-Identifier: MPL-2.0
-- Four own children. Original TipHUD is a read-only content source.
local Hint=require("IIPHintSource")
local Resources=require("IIPResources")
local Tuning=require("IIPTuning")
local M={}
local state
local function valid(o)return o~=nil and o:IsValid()end
local function path(o)return assert(o:GetFullName():match("^[^ ]+ (.+)$"))end
local function cls(o)return path(o:GetClass())end
local function same(a,b)return valid(a) and valid(b) and a:GetAddress()==b:GetAddress()end
local function ref(o)return {path=path(o),address=o:GetAddress(),class=cls(o)}end
local function find(r)
 if not r then return nil end
 local o=StaticFindObject(r.path);if not valid(o)then return nil end
 assert(o:GetAddress()==r.address and cls(o)==r.class,"composition identity changed");return o
end
local function log(e,s)print("IIP_COMPOSITION event="..e.." "..(s or "").."\n")end
local function child(s,kind,role,name)
 local tree,root=find(s.tree),find(s.root)
 local c=StaticFindObject("/Script/UMG."..kind)
 assert(valid(c) and c:type()=="UClass","composition class missing: "..kind)
 assert(not valid(StaticFindObject(path(tree).."."..name)),"composition name collision")
 local o=StaticConstructObject(c,tree,FName(name),EObjectFlags.RF_Transient)
 assert(valid(o) and cls(o)=="/Script/UMG."..kind and same(o:GetOuter(),tree),"own child factory differs")
 s[role]=ref(o) -- Record before any configuration or attachment can throw.
 o:SetVisibility(1)
 local slot=root:AddChildToCanvas(o)
 assert(valid(slot) and same(slot.Parent,root) and same(slot.Content,o) and same(o:GetParent(),root),"own child attachment differs")
 slot:SetAutoSize(false);slot:SetAnchors({Minimum={X=0,Y=0},Maximum={X=0,Y=0}})
 slot:SetAlignment({X=0.5,Y=0.5})
 return o
end
function M.prepare()Resources.prepare()end
function M.pending()return state~=nil end
function M.start(host,root,w,name,settings)
 assert(not state,"one composition only")
 state={host=ref(host),tree=ref(host.WidgetTree),root=ref(root),original=ref(w),settings=settings}
 local s=state
 assert(not same(host.WidgetTree,w.WidgetTree),"composition aliases original tree")
 local lower=child(s,"TextBlock","lower",name.."_Action")
 lower:SetFont(w.TextBlock_89.Font)
 assert(lower.Font:GetStructAddress()~=w.TextBlock_89.Font:GetStructAddress(),"action FontInfo alias")
 s.stock_font_ready=true
 lower:SetJustification(1)
 local upper=child(s,"TextBlock","upper",name.."_Aphes")
 upper:SetFont(lower.Font);Resources.font(upper)
 upper:SetText(FText("OPEN"));upper:SetJustification(1)
 upper:SetShadowOffset({X=0,Y=0});upper:SetShadowColorAndOpacity({R=0,G=0,B=0,A=0})
 upper:SetColorAndOpacity({SpecifiedColor={R=1,G=1,B=1,A=1},ColorUseRule=0})
 local divider=child(s,"Image","divider",name.."_Ornament");Resources.ornament(divider,w)
 local hint=child(s,"Image","hint",name.."_Hint");Hint.start(w,hint)
 -- Hidden participates in prepass, Collapsed does not. Host stays hidden until World setup finishes.
 for _,role in ipairs({"upper","lower","divider"})do find(s[role]):SetVisibility(2)end
 settings.dirty=true;M.update(w)
 log("CREATED","children=4 original_writes=0 technical_upper=OPEN")
end
local function owned(s,role)
 local o=find(s[role]);assert(valid(o) and same(o:GetOuter(),find(s.tree)) and same(o:GetParent(),find(s.root)),"own composition child changed: "..role)
 assert(same(o.Slot.Parent,find(s.root)) and same(o.Slot.Content,o),"own slot changed");return o
end
function M.update(w)
 local s=assert(state,"missing composition");assert(same(w,find(s.original)),"composition original changed")
 local upper,lower,divider,hint=owned(s,"upper"),owned(s,"lower"),owned(s,"divider"),owned(s,"hint")
 Hint.update(w,hint)
 local text=w.TextBlock_89:GetText():ToString()
 assert(type(text)=="string" and #text>0 and #text<=512 and not text:find("[\r\n]"),"unsupported current action")
 local p=s.settings
 local extent=Hint.extent()
 if not extent then return end -- Source not yet sampled; never guess its aspect ratio.
 local sizekey=extent.X..","..extent.Y
 if not p.dirty and s.text==text and s.sizekey==sizekey then return end
 if s.text~=text then lower:SetText(FText(text));assert(lower:GetText():ToString()==text,"own action readback differs")end
 upper.Font.Size=p.upper_size;upper.Font.LetterSpacing=p.tracking
 upper.Font.OutlineSettings.OutlineSize=p.outline;upper.Font.OutlineSettings.OutlineMaterial=nil
 upper.Font.OutlineSettings.OutlineColor={R=0,G=0,B=0,A=1}
 upper:SetFont(upper.Font)
 lower.Font.Size=p.lower_size;lower:SetFont(lower.Font)
 assert(upper.Font.Size==p.upper_size and upper.Font.LetterSpacing==p.tracking
  and upper.Font.OutlineSettings.OutlineSize==p.outline and lower.Font.Size==p.lower_size,"own font readback differs")
 local host=find(s.host);host:ForceLayoutPrepass() -- Only own subtree; measures actual Slate desired sizes.
 local plan=Tuning.plan(p,upper:GetDesiredSize(),lower:GetDesiredSize(),extent)
 for role,v in pairs(plan)do
  local o=owned(s,role);local slot=o.Slot
  slot:SetPosition({X=v[1],Y=v[2]});slot:SetSize({X=v[3],Y=v[4]})
  local pos,sz=slot:GetPosition(),slot:GetSize()
  assert(math.abs(pos.X-v[1])<0.001 and math.abs(pos.Y-v[2])<0.001
   and math.abs(sz.X-v[3])<0.001 and math.abs(sz.Y-v[4])<0.001,"own slot readback differs")
 end
 divider:SetColorAndOpacity({R=1,G=1,B=1,A=p.divider_alpha})
 assert(math.abs(divider.ColorAndOpacity.A-p.divider_alpha)<0.001,"divider opacity readback differs")
 for _,o in ipairs({upper,lower,divider})do o:SetVisibility(3)end
 s.text,s.sizekey,p.dirty=text,sizekey,false
 log("LAYOUT","action="..string.format("%q",text).." "..Tuning.snapshot(p))
end
function M.pause()
 local s=assert(state,"pause composition missing")
 Hint.pause(owned(s,"hint"))
end
function M.cleanup()
 if not state then return true end
 local s=state;local errors={}
 for _,role in ipairs({"hint","divider","upper","lower"})do
  local ok,err=pcall(function()
   if role=="lower" and #errors>0 then error("font carrier retained for retry")end
   local o=find(s[role]);if not valid(o)then s[role]=nil;return end
   assert(same(o:GetOuter(),find(s.tree)),"cleanup foreign tree")
   o:SetVisibility(1)
   if role=="hint"then Hint.cleanup(o)
   elseif role=="divider"then o:SetBrushResourceObject(nil);assert(not valid(o.Brush.ResourceObject),"ornament release failed")
   elseif role=="upper" and s.stock_font_ready then
    local lower=find(s.lower);assert(valid(lower),"font carrier gone")
    o:SetFont(lower.Font);assert(same(o.Font.FontObject,lower.Font.FontObject),"private font release failed")
   end
   local parent=o:GetParent()
   if valid(parent)then assert(same(parent,find(s.root)),"cleanup child reparented");assert(parent:RemoveChild(o),"child detach failed")end
   assert(not valid(o:GetParent()),"child remains attached");s[role]=nil
  end)
  if not ok then errors[#errors+1]=role..":"..tostring(err):sub(1,160)end
 end
 if #errors>0 then log("CLEANUP_PENDING",table.concat(errors," | "));return false end
 state=nil;log("RELEASED","own_children=0 font_holder=false ornament_holder=false");return true
end
return M
