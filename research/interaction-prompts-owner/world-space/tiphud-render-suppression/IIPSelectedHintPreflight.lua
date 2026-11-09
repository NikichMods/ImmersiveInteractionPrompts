-- SPDX-License-Identifier: MPL-2.0
-- Native selected TipHUD input metadata. Read-only, stock-only.
-- Candidate classification is not a World rendering or remap guarantee.
local M={}
local function valid(o)return o~=nil and o:IsValid()end
local function path(o)return assert(o:GetFullName():match("^[^ ]+ (.+)$"))end
local function cls(o)return path(o:GetClass())end
local function white(c)return c.R==1 and c.G==1 and c.B==1 and c.A==1 end
local function shape(image)
 local b,t=image.Brush,image.RenderTransform
 local m=b.Margin
 return image.bFlipForRightToLeftFlowDirection==false
  and t.Translation.X==0 and t.Translation.Y==0
  and t.Scale.X==1 and t.Scale.Y==1
  and t.Shear.X==0 and t.Shear.Y==0 and t.Angle==0
  and b.DrawAs==3 and b.Tiling==0 and b.Mirroring==0 and b.ImageType==0
  and b.ImageSize.X==64 and b.ImageSize.Y==64 and b.UVRegion.bIsValid==0
  and m.Left==0 and m.Top==0 and m.Right==0 and m.Bottom==0
  and b.TintColor.ColorUseRule==0 and white(b.TintColor.SpecifiedColor)
  and white(image.ColorAndOpacity)
end
function M.direct_texture(image,alive)
 if not alive(image) or cls(image)~="/Script/UMG.Image" then return nil end
 local tex=image.Brush.ResourceObject
 if shape(image) and alive(tex) and cls(tex)=="/Script/Engine.Texture2D"
  and path(tex)~="/Game/MainContent/Assets/UIImage/UI_Widgets/ico_ps4_FaceButton_UP.ico_ps4_FaceButton_UP" then
  return tex
 end
end
local function read(actor,row,alive)
 assert(type(row)=="table" and type(row.refs)=="table")
 local source=actor.ExtendedWidget
 assert(alive(actor) and alive(source)
  and source:GetAddress()==row.refs.component.address
  and source:GetOwner():GetAddress()==actor:GetAddress(),"source changed")
 local w=source:GetUserWidgetObject()
 assert(alive(w) and w:GetAddress()==row.refs.widget.address,"TipHUD changed")
 local hold=w.CanHoldPress
 assert(type(hold)=="boolean","hold unknown")
 local lock=w.CanvasPanel_2
 assert(alive(lock),"locked branch unknown")
 local lock_hidden=lock.Visibility==1
 local pc=w:GetOwningPlayer()
 assert(alive(pc),"controller missing")
 local device=pc:GetNowInputControllerType()
 assert(type(device)=="number" and device>=1 and device<=5,"device unknown")
 local image=w.ImageInteractAllowed
 assert(alive(image) and cls(image)=="/Script/UMG.Image","allowed image missing")
 local tex=image.Brush.ResourceObject
 local direct=M.direct_texture(image,alive)~=nil
 local gate="direct_brush_candidate"
 if row.hint_state~="visible" then gate="hint_not_visible"
 elseif hold then gate="hold"
 elseif not lock_hidden then gate="locked"
 elseif device~=1 and device~=4 then gate="unsupported_device"
 elseif not direct then gate="brush_not_direct" end
 return "hint_gate="..gate.." hold="..tostring(hold)
  .." locked_hidden="..tostring(lock_hidden)
  .." device="..tostring(device)
  .." source_type="..(valid(tex) and cls(tex) or "unavailable")
  .." remap_equivalence=UNKNOWN geometry_occlusion=UNKNOWN",gate
end
function M.inspect(actor,row,alive)
 local ok,s,gate=pcall(read,actor,row,alive)
 if not ok then return nil,"unavailable" end
 assert(type(s)=="string" and #s<=360,"report bound")
 return s,gate
end
return M
