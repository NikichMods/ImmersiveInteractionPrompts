-- SPDX-License-Identifier: MPL-2.0
-- Bounded desktop/Open geometry, not a general layout system.
local M = {}
local function number(n) return type(n)=="number" and n==n and math.abs(n)<10000 end
function M.plan(size, position, alignment, icon_position, icon_size, translation)
    for _,v in ipairs({size,position,alignment,icon_position,icon_size,translation}) do
        assert(type(v)=="table" and number(v.X) and number(v.Y), "invalid layout vector")
    end
    assert(size.X>=80 and size.X<=260 and size.Y>=20 and size.Y<=40, "unsupported cached text extent")
    assert(position.X==38 and position.Y==0 and alignment.X==0 and alignment.Y==0.5, "unsupported stock slot")
    assert(icon_position.X==0 and icon_position.Y==0 and icon_size.X>0 and icon_size.X<=38
        and icon_size.Y>0 and icon_size.Y<=128, "unsupported icon slot")
    assert(translation.X==0 and translation.Y==0, "stock translation already in use")
    local width=size.X-8 -- Four-unit inset from each text edge; never cross the key's right edge.
    local height=width*16/570 -- Preserve the single stock PNG's aspect ratio.
    return {x=position.X+size.X/2, line_y=icon_position.Y, width=width, height=height,
        label_y=icon_position.Y-height/2-8, label_width=math.max(size.X,160), label_height=40,
        -- UE4 FVector2D stores float32. An integer shift permits exact native readback/comparison.
        lower_y=math.ceil(icon_position.Y+height/2+8-(position.Y-size.Y/2))}
end
return M
