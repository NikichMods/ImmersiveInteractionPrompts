-- SPDX-License-Identifier: MPL-2.0
-- Only this game-thread pump may mutate the owned World presentation.
local M={}

function M.start(world,source,resolve,api,emit)
    local active=true
    local handle,stop_reason,bound,creating,invalidated,ended_key
    local epoch=0
    local frame,observed_at=0,0
    local observed_key,observed_status
    local prepared=false
    local hidden=false

    local function invalidate(reason)
        if not active then return end
        epoch=epoch+1
        invalidated=reason
    end

    local function stop(reason)
        stop_reason=stop_reason or reason
        invalidate(reason)
    end

    local function release(reason)
        if world.empty() then
            bound=nil
            hidden=false
            return
        end
        -- A disappearing native owner can take the host with it. Attempt
        -- hide, then still give cleanup the chance to prove native absence.
        local hid,result=pcall(world.hide)
        if not hid or result~=true then emit("HIDE_UNCONFIRMED","reason="..reason) end
        assert(world.cleanup(reason)==true and world.empty()==true,"cleanup not confirmed")
        bound=nil
        hidden=false
        emit("RELEASED","reason="..reason)
    end

    local function terminate(reason,try_cleanup)
        active=false
        if try_cleanup then
            local ok,err=pcall(release,"terminal")
            if not ok then emit("CLEANUP_PENDING",tostring(err):sub(1,190)) end
        end
        local ok,cancelled=pcall(api.cancel,handle)
        emit("STOP","reason="..tostring(reason):sub(1,190)..
            " cancelled="..tostring(ok and cancelled==true))
    end

    local function same_context(a,b)
        return a.pawn_key==b.pawn_key and a.component_key==b.component_key
    end

    local function current()
        local row=api.read()
        assert(row and (row.status=="READY" or row.status=="GAP"),"owner read contract")
        if row.status=="READY" then
            assert(type(row.pawn_key)=="string" and type(row.component_key)=="string"
                and ((row.key==nil and row.actor==nil) or
                    (type(row.key)=="string" and row.actor~=nil)),"owner identity contract")
        end
        if row.status~=observed_status or row.key~=observed_key then
            observed_status,observed_key=row.status,row.key
            observed_at=frame
            emit("SELECTION","state="..(row.key and "owner" or
                (row.status=="READY" and "NONE" or "GAP")).." frame="..frame)
        end
        return row
    end

    local releasing=false
    local function retire(reason)
        releasing=true
        release(reason)
        releasing=false
    end

    local function step()
        if stop_reason then terminate(stop_reason,true); return end
        if invalidated then
            local reason=invalidated
            invalidated=nil
            retire(reason)
            -- Do not reuse a pre-lifecycle observation, even if callbacks
            -- already captured a new controller in the same engine tick.
            return
        end
        local token=epoch
        local row=current()
        if row.status=="READY" and row.key~=ended_key then ended_key=nil end
        if bound then
            if row.status=="GAP" or not same_context(row,bound) then
                retire("context_gap_or_replaced")
            elseif row.key==nil then
                if not hidden then
                    if not source.resolve_actor(bound.identity,api.native_alive) then
                        retire("hidden_owner_gone")
                        return
                    end
                    assert(world.hide()==true,"hide failed")
                    hidden=true
                    emit("HIDDEN","reason=none")
                end
                return
            elseif row.key==bound.key then
                if not source.matches_action(row.actor,bound.action) then
                    retire("action_changed")
                    return
                end
                if hidden then
                    assert(world.resume()==true,"resume failed")
                    hidden=false
                    emit("RESUMED","same_owner=true")
                else
                    assert(world.refresh()==true,"refresh failed")
                end
                return
            else
                retire("change_target")
            end
            if epoch~=token then return end
            row=current()
        end
        if epoch~=token or row.status~="READY" or not row.key or row.key==ended_key then return end
        local record=source.acquire(row.actor)
        if not record then return end
        assert(record.actor==row.key,"selected actor identity mismatch")
        local view=source.snapshot(record,api.native_alive,api.hint_visible)
        if not view or not view.shown or not view.ready then return end
        assert(world.empty()==true,"prior component not empty")
        if not prepared then
            world.prepare()
            world.refresh_assets()
            prepared=true
        end
        local function still_selected()
            if epoch~=token then return false end
            local latest=current()
            return epoch==token and latest.status=="READY" and latest.key==row.key
                and same_context(latest,row)
        end
        if not still_selected() then return end
        local actor,component,widget=resolve(record)
        if not actor then return end
        creating=row.key
        local created=world.create(actor,component,widget,stop,record.action,still_selected)
        creating=nil
        if created==false then
            assert(world.empty()==true,"deferred create left resources")
            return
        end
        assert(world.empty()==false,"create did not acquire World resources")
        bound={key=row.key,pawn_key=row.pawn_key,component_key=row.component_key,action=record.action,
            identity={key=record.actor,ref=record.refs.actor}}
        local age=frame-observed_at
        if not still_selected() then retire("selection_changed_during_create"); return end
        emit("BOUND","action="..record.action.." committed_read=true observer_frames="..age)
        assert(world.resume()==true,"initial resume failed")
    end

    handle=api.loop(1,function()
        if not active then return end
        frame=frame+1
        local ok,err=pcall(step)
        if not ok then
            if releasing then emit("CLEANUP_PENDING",tostring(err):sub(1,190)) end
            terminate(err,not releasing)
        end
    end)
    assert(type(handle)=="number" and handle>0,"game-thread loop unavailable")
    emit("ARMED","owner=PlayerActionComponent+0x410 native_writes=0")
    return {
        invalidate=invalidate,stop=stop,
        ended=function(address)
            local suffix="|"..tostring(address)
            local key=creating or (bound and bound.key)
            if key and key:sub(-#suffix)==suffix then
                ended_key=key
                invalidate("owner_endplay")
            end
        end,
        status=function() return {active=active} end,
    }
end

return M
