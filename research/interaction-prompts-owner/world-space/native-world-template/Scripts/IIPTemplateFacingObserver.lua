-- SPDX-License-Identifier: MPL-2.0
-- Research-only, read-only observation. No native setters, timers or extra hooks.
-- The existing native TipHUD:CanShow callback provides samples; F5 arms/summarizes.
local M={}
M.__index=M
local MAX_ACTORS,MAX_CALLS,MAX_POSES,POSE_EVERY=24,12000,450,8
local function valid(o) return o~=nil and o:IsValid() end
local function delta(a,b) return math.abs((a-b+180)%360-180) end
local function camera_pose(c,w)
    local manager=w:GetOwningPlayerCameraManager()
    assert(valid(manager),"no owning camera manager")
    local cam=manager:GetCameraLocation()
    local origin=c:K2_GetComponentLocation()
    local dx,dy=cam.X-origin.X,cam.Y-origin.Y
    assert(dx*dx+dy*dy>=1,"camera horizontal singularity")
    local direction=math.deg(math.atan(dy,dx))
    local yaw=c:K2_GetComponentRotation().Yaw
    assert(type(yaw)=="number" and yaw==yaw and type(direction)=="number"
        and direction==direction,"invalid camera/component heading")
    return direction,yaw
end

local function layout_sample(c,w)
    local controller=w:GetOwningPlayer()
    local owner=c:GetOwner()
    local locator=c:GetAttachParent()
    assert(valid(controller) and valid(owner) and valid(locator),"layout player/owner/locator missing")
    local origin=c:K2_GetComponentLocation()
    local parent=locator:K2_GetComponentLocation()
    local actor=owner:K2_GetActorLocation()
    local function screen_x(p)
        local out={}
        assert(controller:ProjectWorldLocationToScreen(p,out,false)==true
            and type(out.X)=="number" and math.abs(out.X)<math.huge,"layout projection unavailable")
        return out.X
    end
    local pivot,draw=c:GetPivot(),c:GetCurrentDrawSize()
    assert(draw.X>0 and draw.Y>0 and pivot.X>=0 and pivot.X<=1,"layout target not ready")
    -- Project each horizontal anchor at the same elevation to isolate its
    -- lateral contribution. Screenshot coordinates use the full viewport.
    return ("actor_at_tip_x=%.1f parent_at_tip_x=%.1f component_x=%.1f pivot_u=%.1f draw_w=%.0f"):format(
        screen_x({X=actor.X,Y=actor.Y,Z=origin.Z}),
        screen_x({X=parent.X,Y=parent.Y,Z=origin.Z}),screen_x(origin),pivot.X*draw.X,draw.X)
end

function M.new(log)
    assert(type(log)=="function","logger unavailable")
    return setmetatable({log=log,active=false,items={},order={},dropped=0},M)
end

function M:sample(info,component,widget)
    if not self.active or not info or not info.observer_kind then return end
    local name=info.actor
    if type(name)~="string" or not valid(component) or not valid(widget) then return end
    local item=self.items[name]
    if not item then
        if #self.order>=MAX_ACTORS then self.dropped=self.dropped+1;return end
        item={kind=info.observer_kind,actor=name,calls=0,shown=0,hidden=0,
              flips=0,opacity_zero=0,opacity_positive=0,
              poses=0,moves=0,widget_moves=0,largest_step=0,pose_errors=0}
        self.items[name]=item
        self.order[#self.order+1]=item
    end
    if item.calls>=MAX_CALLS then return end
    item.calls=item.calls+1
    local flag=component.bVisible
    if flag==true then item.shown=item.shown+1
    elseif flag==false then item.hidden=item.hidden+1 end
    if item.last_flag~=nil and item.last_flag~=flag then item.flips=item.flips+1 end
    item.last_flag=flag
    local ok_opacity,opacity=pcall(function() return widget.RenderOpacity end)
    if ok_opacity and type(opacity)=="number" then
        if opacity<=0.01 then item.opacity_zero=item.opacity_zero+1
        else item.opacity_positive=item.opacity_positive+1 end
    end
    if info.orientation=="billboard" and flag==true and ok_opacity
        and type(opacity)=="number" and opacity>.01 and not item.layout_checked then
        item.layout_checked=true
        local ok,result=pcall(layout_sample,component,widget)
        local detail=ok and result or ("reason=%q"):format(tostring(result):sub(1,140))
        self.log("FACING_OBS_LAYOUT",("actor=%q %s"):format(name,detail))
    end
    if item.poses>=MAX_POSES or (item.calls~=1 and (item.calls-1)%POSE_EVERY~=0) then return end
    local ok,bearing,yaw=pcall(camera_pose,component,widget)
    if not ok then item.pose_errors=item.pose_errors+1;return end
    item.poses=item.poses+1
    if item.first_bearing==nil then item.first_bearing=bearing end
    if item.last_bearing~=nil then
        local move=delta(bearing,item.last_bearing)
        if move>=3 then item.moves=item.moves+1 end
        item.largest_step=math.max(item.largest_step,move)
        if delta(yaw,item.last_yaw)>=3 then item.widget_moves=item.widget_moves+1 end
    end
    item.last_bearing,item.last_yaw=bearing,yaw
end

function M:toggle()
    if not self.active then
        self.active=true;self.items={};self.order={};self.dropped=0
        self.log("FACING_OBS_ARMED","scope=npc known_chest potential_door no_writes=true press_F5_again_for_summary")
        return true
    end
    self.active=false
    self.log("FACING_OBS_STOP",("actors=%d dropped=%d"):format(#self.order,self.dropped))
    for _,v in ipairs(self.order) do
        self.log("FACING_OBS_RESULT",("kind=%s actor=%q calls=%d visible_true=%d visible_false=%d flips=%d opacity_zero=%d opacity_positive=%d poses=%d camera_moves=%d widget_moves=%d max_step=%.1f start_bearing=%.1f last_bearing=%.1f last_yaw=%.1f pose_errors=%d"):format(
            v.kind,v.actor,v.calls,v.shown,v.hidden,v.flips,v.opacity_zero,v.opacity_positive,
            v.poses,v.moves,v.widget_moves,v.largest_step,
            v.first_bearing or -999,v.last_bearing or -999,v.last_yaw or -999,v.pose_errors))
    end
    return false
end

return M
