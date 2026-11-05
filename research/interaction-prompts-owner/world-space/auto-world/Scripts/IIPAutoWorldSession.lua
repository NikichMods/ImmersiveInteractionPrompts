-- SPDX-License-Identifier: MPL-2.0
-- Automatic session owns TWO loops: a 30-frame read-only observer and a
-- 1-frame World coordinator. Native UI changes ONLY in the latter.
-- No countdown, no manual reload, no native Screen prompt mutation.
local M={}
local function short(v)return tostring(v):sub(1,190)end

function M.start(deps,api,emit)
    assert(type(deps)=="table" and type(api)=="table" and
        type(emit)=="function","automatic session contract missing")
    for _,name in ipairs({"source","events","visibility","handoff",
        "bridge","renderer","world","target"})do
        assert(type(deps[name])=="table","missing session dependency: "..name)
    end
    for _,name in ipairs({"begin","finish","map_pre","loop","cancel",
        "native_alive"})do
        assert(type(api[name])=="function","missing game thread API: "..name)
    end
    assert(type(api.hint_visible)=="function","native visibility seam missing")
    local s={active=true,stopping=false,terminal=false,observer=nil,
        handoff=nil,renderer=nil,handle=nil,cycles=0,
        reason="running",stop_count=0,finalized=false}
    local function trace(event,info)emit(event,info or "")end
    local function stop(reason)
        if s.stopping then return end
        s.stopping=true;s.reason=short(reason or "explicit_stop")
        s.stop_count=s.stop_count+1
        if s.handoff then s.handoff.stop(s.reason)end
        if s.observer then s.observer.stop(s.reason)end
        trace("STOP_REQUESTED","reason="..s.reason.." native_UI_writes_in_hooks=0")
    end
    local function terminal(reason)
        if s.terminal then return end
        s.terminal=true;s.active=false
        s.reason=short(reason)
        if s.handle then
            local ok,result=pcall(api.cancel,s.handle)
            trace(ok and result==true and "PUMP_CANCELLED" or "PUMP_CANCEL_UNCONFIRMED",
                "handle="..tostring(s.handle))
            s.handle=nil
        end
        trace("TERMINAL","reason="..s.reason..
            " no_new_native_UI_allocations=true cycles="..s.cycles)
    end
    local function done_clean()
        if not s.handoff or not s.renderer then return false end
        local h=s.handoff.status()
        return h.selected==nil and s.renderer.empty()==true
    end
    local function pulse()
        if s.terminal then return end
        s.cycles=s.cycles+1 -- telemetry, never a lifetime cap
        if not s.observer.status().active and not s.stopping then
            stop("native_observer_stopped")
        end
        local ok,result=pcall(deps.bridge.pump,s.observer,s.handoff)
        if not ok then
            trace("PUMP_FAULT","reason="..short(result).." unrecoverable_in_loop=true")
            stop("world_pump_exception")
            if done_clean() then terminal("stopped_clean")
            else terminal("cleanup_unconfirmed_manual_host_exit_required") end
            return
        end
        local status=s.handoff.status()
        if status.blocked then
            stop("World_cleanup_blocked")
            -- No per-frame retry of a failed native cleanup.
            terminal("cleanup_blocked_manual_host_exit_required")
            return
        end
        if status.fault and not s.stopping then stop("World_handoff_fault") end
        if s.stopping and done_clean() then
            terminal("stopped_clean")
            return
        end
        if result=="cleaned" or result=="bound_hidden" or
            result=="resumed" or result=="hidden_before_release" then
            trace("STEP", "phase="..result..
                " binds="..status.binds.." cleans="..status.cleans)
        end
    end
    local ok,err=pcall(function()
        local resolver=deps.target.new(deps.source,api.native_alive,
            api.hint_visible)
        s.renderer=deps.renderer.new(deps.world,resolver,stop)
        s.handoff=deps.handoff.new(s.renderer,function(event,info)
            trace("HANDOFF_"..event,info)
        end)
        s.observer=deps.events.start({
            begin=api.begin,finish=api.finish,map_pre=api.map_pre,
            loop=api.loop,cancel=api.cancel,native_alive=api.native_alive,
            hint_visible=api.hint_visible
        },deps.source,function(event,info)
            trace("SOURCE_"..event,info)
        end,deps.bridge.sink(s.handoff))
        assert(s.observer and s.observer.status().active,
            "read-only observer could not start")
        s.handle=api.loop(1,pulse)
        assert(type(s.handle)=="number" and s.handle>0,
            "World pump game-thread handle unavailable")
    end)
    if not ok then
        stop("session_registration:"..short(err))
        terminal("session_registration_failed")
        trace("UNAVAILABLE",short(err))
    else
        trace("ARMED","actions=Open,Take,Check source_sample_frames=30"..
            " renderer_pump_frames=1 no_timers=true"..
            " native_original_UI_writes=0 manual_reload=false")
    end
    return {
        stop=stop,
        status=function()
            return {active=s.active,stopping=s.stopping,
                terminal=s.terminal,reason=s.reason,cycles=s.cycles,
                observer=s.observer and s.observer.status() or nil,
                handoff=s.handoff and s.handoff.status() or nil,
                renderer=s.renderer and s.renderer.status() or nil}
        end
    }
end
return M
