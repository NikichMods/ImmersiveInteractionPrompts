-- SPDX-License-Identifier: MPL-2.0
-- Separate owned viewport host, not an edit of the gameplay HUD or TipHUD.
local M={}
local A,state
function M.bind(api)A=api end
function M.pending()return state~=nil end
function M.create(context,text)
 assert(not state,"panel cleanup pending")
 local host=A.create_host(context)
 state={host=A.ref(host)} -- Retain primitive identity immediately after allocation.
 local tree,root,main,value=A.own_tree(host)
 state.tree,state.root=A.ref(tree),A.ref(root)
 main:SetVisibility(1);host.bIsFocusable=false
 local c=StaticFindObject("/Script/UMG.TextBlock")
 assert(A.valid(c) and c:type()=="UClass","panel TextBlock missing")
 local label=StaticConstructObject(c,tree,FName("IIP_Editor_"..os.time()),EObjectFlags.RF_Transient)
 assert(A.alive(label) and A.cls(label)=="/Script/UMG.TextBlock" and A.same(label:GetOuter(),tree),"panel label factory differs")
 state.label=A.ref(label)
 label:SetFont(value.Font);assert(label.Font:GetStructAddress()~=value.Font:GetStructAddress(),"panel font alias")
 label.Font.Size=18;label:SetFont(label.Font);label:SetJustification(0);label:SetText(FText(text))
 label:SetColorAndOpacity({SpecifiedColor={R=1,G=1,B=1,A=1},ColorUseRule=0})
 label:SetShadowOffset({X=1,Y=1});label:SetShadowColorAndOpacity({R=0,G=0,B=0,A=1})
 local slot=root:AddChildToCanvas(label)
 assert(A.same(slot.Parent,root) and A.same(slot.Content,label) and A.same(label:GetParent(),root),"panel slot mismatch")
 slot:SetAutoSize(false);slot:SetAnchors({Minimum={X=0,Y=0},Maximum={X=0,Y=0}})
 slot:SetAlignment({X=0,Y=0});slot:SetPosition({X=24,Y=100});slot:SetSize({X=600,Y=540})
 host:SetDesiredSizeInViewport({X=648,Y=660})
 host:SetAnchorsInViewport({Minimum={X=0,Y=0},Maximum={X=0,Y=0}})
 host:SetAlignmentInViewport({X=0,Y=0});host:SetPositionInViewport({X=0,Y=0},false)
 host:AddToViewport(100)
 assert(host:IsInViewport() and host.Visibility==2,"panel first Construct contract differs")
 host:SetVisibility(3);label:SetVisibility(3)
 M.text(text)
end
function M.text(text)
 local s=assert(state,"panel missing")
 local host,label=A.find(s.host),A.find(s.label)
 assert(A.alive(host) and host:IsInViewport() and A.alive(label)
  and A.same(label:GetOuter(),A.find(s.tree)) and A.same(label:GetParent(),A.find(s.root)),"panel context lost")
 label:SetText(FText(text));assert(label:GetText():ToString()==text,"panel text readback differs")
end
function M.close()
 if not state then return true end
 local s=state
 local host=A.find(s.host)
 if A.alive(host)then host:SetVisibility(1)end
 local label=A.find(s.label)
 if A.alive(label)then
  assert(A.same(label:GetOuter(),A.find(s.tree)),"panel label outer changed")
  label:SetVisibility(1)
  local parent=label:GetParent()
  if A.valid(parent)then assert(A.same(parent,A.find(s.root)),"panel label reparented");assert(parent:RemoveChild(label),"panel detach failed")end
 end
 if A.alive(host)then host:RemoveFromParent();assert(not host:IsInViewport() and not A.valid(host:GetParent()),"panel viewport release failed")end
 state=nil;return true
end
return M
