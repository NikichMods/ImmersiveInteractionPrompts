-- SPDX-License-Identifier: MPL-2.0
-- Own-child geometry only. Never mutates the native text or button.
local M={}
local function number(x)
    return type(x)=="number" and x==x and x>-4096 and x<4096
end
local function vector(v)
    return type(v)=="table" or type(v)=="userdata"
end
local function clamp(x,low,high) return math.max(low,math.min(high,x)) end
local function rejected(explain, reason)
    if explain then return nil,reason end
    return nil
end
function M.plan(i, explain)
    if type(i)~="table" then return rejected(explain,"input") end
    if not vector(i.desired) then return rejected(explain,"desired_shape") end
    if not vector(i.position) then return rejected(explain,"text_position_shape") end
    if not vector(i.alignment) then return rejected(explain,"text_alignment_shape") end
    if not vector(i.anchors) then return rejected(explain,"text_anchors_shape") end
    local d,p,a,k=i.desired,i.position,i.alignment,i.anchors
    if not(number(d.X) and number(d.Y)
        and d.X>=24 and d.X<=800 and d.Y>=14 and d.Y<=150) then return rejected(explain,"desired_size") end
    if not(number(p.X) and number(p.Y)) then return rejected(explain,"text_position") end
    if not(number(a.X) and number(a.Y) and a.X>=0 and a.X<=1 and a.Y>=0 and a.Y<=1) then
        return rejected(explain,"text_alignment")
    end
    if not(number(i.native_size) and i.native_size>=12 and i.native_size<=80) then
        return rejected(explain,"text_font_size")
    end
    if not k.Minimum or not k.Maximum
        or k.Minimum.X~=0 or k.Maximum.X~=0
        or k.Minimum.Y~=0.5 or k.Maximum.Y~=0.5 then return rejected(explain,"text_anchors") end
    local ip,ia,ik,isz=i.icon_position,i.icon_alignment,i.icon_anchors,i.icon_size
    if not(ip and ia and ik and isz and ik.Minimum and ik.Maximum) then return rejected(explain,"icon_shape") end
    if i.icon_auto~=false then return rejected(explain,"icon_autosize") end
    if not(number(ip.X) and number(ip.Y)) then return rejected(explain,"icon_position") end
    if not(number(isz.X) and number(isz.Y)) or isz.X<20 or isz.X>160
        or isz.Y<20 or isz.Y>160 then return rejected(explain,"icon_size") end
    if ik.Minimum.X~=0 or ik.Maximum.X~=0 or ik.Minimum.Y~=0.5 or ik.Maximum.Y~=0.5 then
        return rejected(explain,"icon_anchors")
    end
    if ia.X~=0 or ia.Y~=0.5 then return rejected(explain,"icon_alignment") end
    local x=p.X+(0.5-a.X)*d.X
    local lower_top=p.Y-a.Y*d.Y
    local upper_size=clamp(math.floor(i.native_size*1.20+0.5),18,38)
    local upper_height=math.ceil(upper_size*1.40)
    local width=clamp(d.X*0.85,94,190)
    local divider_height=width/8 -- Preserve authored PNG aspect 256:32.
    local divider_visible_half=divider_height/4 -- Actual nonzero alpha rows 8..24.
    local line_y=lower_top-4-divider_visible_half
    local upper_y=line_y-divider_visible_half-4-upper_height/2
    local upper_width=clamp(math.max(width,176),176,230)
    return {
        key=string.format("%.1f/%.1f/%.1f/%.1f",x,upper_y,width,d.Y),
        upper_size=upper_size,
        upper={x=x,y=upper_y,width=upper_width,height=upper_height},
        divider={x=x,y=line_y,width=width,height=divider_height}
    }
end
return M
