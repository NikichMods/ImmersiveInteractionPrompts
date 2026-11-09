-- SPDX-License-Identifier: MPL-2.0
-- One independent World component, driven by the committed native selection.
local Capability=require("IIPSelectedTipCapability")
local HintGate=require("IIPSelectedHintPreflight")
local M={}
-- Research-only coverage switch. True: every compatible selected native TipHUD,
-- including previously excluded Open/Take/Check. No native Screen writes.
local ALL_SELECTED_ACTIONS=true
local legacy={Open=true,Take=true,Check=true}

function M.start(world,api,emit)
    local active,prepared=true,false
    local handle,bound,creating,invalidated,stop_reason,ended_address,drifted
    local epoch=0

    local function invalidate(reason)
        epoch=epoch+1
        invalidated=reason
    end

    local function stop(reason)
        stop_reason=stop_reason or reason
        invalidate(reason)
    end

    local function release(reason)
        if not world.empty() then
            assert(world.cleanup(reason) and world.empty(),"owned cleanup not confirmed")
            emit("RELEASED","reason="..reason.." own_world_empty=true")
        end
        bound=nil
    end

    local function finish(reason)
        active=false
        local clean,problem=pcall(release,reason)
        if not clean then emit("CLEANUP_PENDING",tostring(problem):sub(1,190)) end
        local ok,cancelled=pcall(api.cancel,handle)
        emit("STOP","reason="..reason:sub(1,130).." cancelled="..
            tostring(ok and cancelled==true).." cleanup_confirmed="..tostring(clean))
    end

    local function inspect(selection)
        local actor=selection.actor
        if selection.status~="READY" or not actor or actor:GetAddress()==ended_address then return end
        local ok,row=pcall(Capability.inspect_selected,actor,api.native_alive,api.hint_visible)
        if not ok or not row or row.actor~=selection.key
            or (not ALL_SELECTED_ACTIONS and legacy[row.action]) then return end
        local _,gate=HintGate.inspect(actor,row,api.native_alive)
        if gate~="direct_brush_candidate" then return end
        return row
    end

    local function step()
        if stop_reason then finish(stop_reason);return end
        if invalidated then
            local reason=invalidated
            invalidated=nil
            release(reason)
            drifted=nil
            return
        end
        local selection=api.read()
        local token=epoch
        if selection.status=="READY" and (not selection.actor or
            selection.actor:GetAddress()~=ended_address) then ended_address=nil end
        if selection.key~=drifted then drifted=nil end
        local row=inspect(selection)
        if bound then
            if not row or row.widget~=bound.widget or row.component~=bound.component
                or row.action~=bound.action or row.actor~=bound.actor
                or selection.pawn_key~=bound.pawn_key or selection.component_key~=bound.component_key then
                release("selection_or_capability_changed")
                return
            end
            if not world.shadow_anchor_current() then
                drifted=row.actor
                release("anchor_moved")
                return
            end
            world.refresh()
            return
        end
        if not row or drifted then return end
        if not prepared then
            world.prepare()
            world.refresh_assets()
            prepared=true
        end
        local function still_selected()
            if epoch~=token then return false end
            local latest=api.read()
            if latest.pawn_key~=selection.pawn_key or latest.component_key~=selection.component_key then return false end
            local current=inspect(latest)
            return epoch==token and current~=nil and current.actor==row.actor
                and current.component==row.component and current.widget==row.widget
                and current.action==row.action
        end
        if not still_selected() then return end
        local actor=selection.actor
        local source=actor.ExtendedWidget
        creating=row.refs.actor.address
        local created=world.create(actor,source,source:GetUserWidgetObject(),stop,row.action,still_selected)
        creating=nil
        if created==false then
            assert(world.empty(),"aborted create left resources")
            return
        end
        assert(not world.empty(),"World creation returned no resources")
        if not still_selected() then release("selection_changed_during_create");return end
        if not world.shadow_anchor_current() then
            drifted=row.actor
            release("anchor_moved_during_create")
            return
        end
        row.pawn_key,row.component_key=selection.pawn_key,selection.component_key
        bound=row
        emit("BOUND","action="..row.action.." screen_untouched=true geometry_occlusion=UNKNOWN")
        world.refresh()
    end

    handle=api.loop(1,function()
        if not active then return end
        local ok,err=pcall(step)
        if not ok then
            emit("FAULT",tostring(err):sub(1,190))
            finish("fault")
        end
    end)
    assert(type(handle)=="number" and handle>0,"game-thread loop unavailable")
    emit("ARMED","mode=shadow_world screen_untouched=true")
    return {
        invalidate=invalidate,stop=stop,
        ended=function(address)
            if address==creating or (bound and address==bound.refs.actor.address) then
                ended_address=address
                invalidate("owner_endplay")
            end
        end,
        status=function()return {active=active}end,
    }
end

return M
