-- SPDX-License-Identifier: MPL-2.0
-- Exact own-World lease adapter. No native UI or player action is modified.
-- Requires a fresh, validating native resolver; never caches UObject wrappers.
local M={}

local function owned(o)
 assert(type(o)=="table" and type(o.actor)=="string" and
     type(o.component)=="string" and type(o.widget)=="string" and
     (o.action=="Open" or o.action=="Take" or o.action=="Check"),
     "invalid primitive owner")
 return {actor=o.actor,component=o.component,widget=o.widget,action=o.action}
end

function M.new(world,resolve,onstop)
 assert(type(world)=="table" and type(resolve)=="function" and
   type(onstop)=="function","World lease contract incomplete")
 for _,n in ipairs({"prepare","refresh_assets","create","cleanup",
   "hide","resume","refresh","empty"})do
   assert(type(world[n])=="function","missing World function: "..n)
 end
 local state=nil
 local prepared=false
 local asset_ready=false
 local serial=0
 local function empty()
   return state==nil and world.empty()==true
 end
 return {
   empty=empty,
   create=function(owner,ticket)
     local r=owned(owner)
     assert(type(ticket)=="number" and ticket>0,"invalid owner ticket")
     assert(empty(),"prior World lease not CLEANED")
     -- Set lease before any native operation: even partial creation requires
     -- cleanup, never a second bind or an unacknowledged release.
     serial=serial+1
     state={owner=r,ticket=ticket,serial=serial}
     if not prepared then
       world.prepare() -- one-time APIs/font and source-resource checks
       prepared=true
     end
     if not asset_ready then
       world.refresh_assets() -- one-time exact asset discovery/loading
       asset_ready=true
     end
     local actor,component,widget=resolve(r)
     assert(actor and component and widget,"native resolver did not return complete triple")
     world.create(actor,component,widget,onstop,r.action)
     assert(world.empty()==false,"World create returned without own resources")
     return true -- own host created hidden by the underlying World module
   end,
   hide=function()
     assert(state,"no World lease to hide")
     return world.hide()==true
   end,
   resume=function()
     assert(state,"no World lease to resume")
     return world.resume()==true
   end,
   refresh=function()
     assert(state,"no World lease to refresh")
     return world.refresh()==true
   end,
   cleanup=function(reason,ticket)
     if not state then return world.empty()==true end
     assert(type(ticket)=="number" and ticket>0,"missing release ticket")
     -- The coordinator verifies the World.EMPTY result independently
     -- before acknowledging RELEASED.
     local cleaned=world.cleanup(reason or "change_target")
     if cleaned~=true or world.empty()~=true then return false end
     state=nil
     return true
   end,
   status=function()
     return {lease=state~=nil,serial=serial,asset_ready=asset_ready,
       owner=state and state.owner.actor or nil}
   end
 }
end
return M
