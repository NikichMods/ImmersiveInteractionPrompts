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
function M.plan(i)
    if type(i)~="table" or not vector(i.desired) or not vector(i.position)
        or not vector(i.alignment) or not vector(i.anchors) then return nil end
    local d,p,a,k=i.desired,i.position,i.alignment,i.anchors
    if not(number(d.X) and number(d.Y) and number(p.X) and number(p.Y)
        and number(a.X) and number(a.Y) and number(i.native_size)
        and d.X>=24 and d.X<=800 and d.Y>=14 and d.Y<=150
        and i.native_size>=12 and i.native_size<=80
        and a.X>=0 and a.X<=1 and a.Y>=0 and a.Y<=1) then return nil end
    if not k.Minimum or not k.Maximum
        or k.Minimum.X~=0 or k.Maximum.X~=0
        or k.Minimum.Y~=0.5 or k.Maximum.Y~=0.5 then return nil end
    local ip,ia,ik,isz=i.icon_position,i.icon_alignment,i.icon_anchors,i.icon_size
    if not(ip and ia and ik and isz and ik.Minimum and ik.Maximum)
        or i.icon_auto~=false or not(number(ip.X) and number(ip.Y)
        and number(isz.X) and number(isz.Y))
        or isz.X<20 or isz.X>160 or isz.Y<20 or isz.Y>160
        or ik.Minimum.X~=0 or ik.Maximum.X~=0
        or ik.Minimum.Y~=0.5 or ik.Maximum.Y~=0.5
        or ia.X~=0 or ia.Y~=0.5 then return nil end
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
