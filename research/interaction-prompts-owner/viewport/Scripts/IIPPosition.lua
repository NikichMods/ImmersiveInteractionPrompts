-- SPDX-License-Identifier: MPL-2.0
-- Integer percentages avoid accumulation/float equality problems during tuning.
local M={}
function M.initial() return {x=50,y=78} end
function M.move(p,dx,dy)
    assert(math.type(dx)=="integer" and math.type(dy)=="integer" and math.abs(dx)+math.abs(dy)<=1,"bad step")
    return {x=math.max(10,math.min(90,p.x+dx)),y=math.max(10,math.min(90,p.y+dy))}
end
return M
