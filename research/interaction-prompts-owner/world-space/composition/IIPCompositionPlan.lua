-- SPDX-License-Identifier: MPL-2.0
-- Pure provisional slot plan, not a runtime mod or a text-measurement implementation.
local M={}
local function finite(n)return type(n)=="number" and n==n and math.abs(n)<math.huge end
function M.plan(text_width,text_height,hint_width,hint_height)
 for _,n in ipairs({text_width,text_height,hint_width,hint_height})do assert(finite(n),"non-finite extent")end
 assert(text_width>0 and text_width<=340 and text_height>0 and text_height<=40,"action extent outside plan")
 assert(hint_width>0 and hint_width<=64 and hint_height>0 and hint_height<=40,"hint extent outside plan")
 local action_left=256-text_width/2
 return {width=512,height=128,
  upper={x=36,y=4,w=440,h=48},
  ornament={x=156,y=64-100*16/570,w=200,h=200*16/570},
  action={x=action_left,y=100-text_height/2,w=text_width,h=text_height},
  hint={x=action_left-8-hint_width,y=100-hint_height/2,w=hint_width,h=hint_height}}
end
return M
