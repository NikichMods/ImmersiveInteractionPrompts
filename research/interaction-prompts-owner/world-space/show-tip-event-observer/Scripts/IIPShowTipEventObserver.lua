-- SPDX-License-Identifier: MPL-2.0
-- Read-only actor ShowTipEvent(bool) -> independent stock TipHUD snapshot.
-- An INTENT is not proof of rendered pixels. No UI writes or hook returns.
local M={}
local VERIFY_FRAMES=12
local MAX_PENDING=12

function M.start(api,source,emit)
    for _,n in ipairs({"begin","finish","map_pre","loop","cancel","bind",
        "native_alive","hint_visible"}) do
        assert(type(api[n])=="function","missing API "..n)
    end
    local s={active=true,hook=false,handle=nil,frame=0,owners={},pending={},
        seq=0,intents=0,matched=0,expired=0,unresolved=0,other=0}
    local function log(event,fields) emit(event,fields or "") end
    local function stop(reason)
        if not s.active then return end
        s.active=false
        if s.handle then
            local ok,cancelled=pcall(api.cancel,s.handle)
            log(ok and cancelled and "LOOP_CANCELLED" or "LOOP_CANCEL_UNCONFIRMED")
        end
        s.owners={};s.pending={}
        log("STOP","reason="..tostring(reason):sub(1,160)..
            " intents="..s.intents.." matched="..s.matched..
            " expired="..s.expired.." native_writes=0 hook_inert=true")
    end
    local function safe(where,fn)
        if not s.active then return end
        local ok,err=pcall(fn)
        if not ok then stop(where..":"..tostring(err):sub(1,150)) end
    end
    local function add(actor)
        local rec,why=source.acquire(actor)
        if not rec then
            assert(why=="unrelated_actor" or why=="unrelated_default_object"
                or why=="unrelated_argument" or why=="other_action"
                or why=="not_ready_component" or why=="not_ready_widget",
                "unexpected source status "..tostring(why))
            return nil
        end
        assert((rec.action=="Open" or rec.action=="Take" or rec.action=="Check")
            and type(rec.actor)=="string" and type(rec.widget)=="string"
            and type(rec.component)=="string","invalid native owner")
        local existing=s.owners[rec.actor]
        if existing then
            assert(existing.widget==rec.widget and existing.component==rec.component
                and existing.action==rec.action,"actor rebound")
        else
            s.owners[rec.actor]=rec
            log("OWNER_JOIN","action="..rec.action)
        end
        return rec
    end
    local function on_begin(arg)
        safe("BeginPlay",function()
            assert(arg and type(arg.get)=="function","missing BeginPlay context")
            local actor=arg:get()
            if actor then add(actor) end
        end)
    end
    local function on_finish(arg)
        safe("EndPlay",function()
            assert(arg and type(arg.get)=="function","missing EndPlay context")
            local actor=arg:get()
            if not actor then return end
            local id=source.actor_identity(actor)
            if not id then return end
            if s.owners[id.key] then
                s.owners[id.key]=nil
                for i=#s.pending,1,-1 do
                    if s.pending[i].actor==id.key then table.remove(s.pending,i) end
                end
                log("OWNER_END","pending_cleared=true")
            end
        end)
    end
    local function on_map()
        safe("LoadMapPre",function()
            s.owners={};s.pending={}
            log("MAP_RESET","hook_after_map_unverified=true")
        end)
    end
    -- Read borrowed UE4SS callback parameters only inside the callback.
    -- Every exit returns nil; do not modify host function results.
    local function on_event(context,show_arg,...)
        if not s.active then return end
        local extra=select("#",...)
        safe("ShowTipEvent",function()
            assert(extra==0,"unexpected event parameter count")
            assert(context and type(context.get)=="function","missing actor context")
            assert(show_arg and type(show_arg.get)=="function","missing bool parameter")
            local show=show_arg:get()
            assert(type(show)=="boolean","event Show not boolean")
            local actor=context:get()
            assert(actor~=nil,"event actor nil")
            local id=source.actor_identity(actor)
            if not id then s.other=s.other+1;return end
            local rec=s.owners[id.key] or add(actor)
            if not rec then
                s.unresolved=s.unresolved+1
                log("UNRESOLVED","indexed=false")
                return
            end
            assert(#s.pending<MAX_PENDING,"pending bound exceeded")
            s.seq=s.seq+1;s.intents=s.intents+1
            log("INTENT","seq="..s.seq.." action="..rec.action..
                " show="..tostring(show).." frame="..s.frame..
                " decision_not_pixels=true")
            s.pending[#s.pending+1]={seq=s.seq,actor=rec.actor,show=show,
                frame=s.frame}
        end)
    end
    local function tick()
        safe("EngineTick",function()
            s.frame=s.frame+1
            if not s.hook and next(s.owners) then
                local ok,reason=api.bind(on_event)
                if not ok then
                    log("HOOK_UNAVAILABLE","reason="..tostring(reason):sub(1,120)..
                        " coverage=none")
                    stop("HOOK_UNAVAILABLE")
                    return
                end
                s.hook=true
                log("HOOK_ARMED","pre_arm_events_unknown=true")
            end
            local keep={}
            for _,event in ipairs(s.pending) do
                local age=s.frame-event.frame
                if age<1 then
                    keep[#keep+1]=event
                else
                    local rec=s.owners[event.actor]
                    if not rec then
                        s.unresolved=s.unresolved+1
                        log("DROPPED","seq="..event.seq.." reason=owner_gone")
                    else
                        local row,why=source.snapshot(rec,api.native_alive,api.hint_visible)
                        if not row then
                            s.unresolved=s.unresolved+1
                            log("DROPPED","seq="..event.seq.." reason="..tostring(why))
                        else
                            assert(row.actor==rec.actor and row.component==rec.component
                                and row.widget==rec.widget and row.action==rec.action,
                                "snapshot identity changed")
                            local shown=row.shown==true and row.ready==true
                            if shown==event.show then
                                s.matched=s.matched+1
                                log("CORRELATED","seq="..event.seq.." action="..rec.action..
                                    " show="..tostring(event.show).." age_frames="..age..
                                    " native_visible="..tostring(shown)..
                                    " sampled_not_pixels=true")
                            elseif age>=VERIFY_FRAMES then
                                s.expired=s.expired+1
                                log("NO_MATCH","seq="..event.seq..
                                    " within_frames="..VERIFY_FRAMES..
                                    " later_visibility_unknown=true")
                            else
                                keep[#keep+1]=event
                            end
                        end
                    end
                end
            end
            s.pending=keep
        end)
    end
    api.begin(on_begin)
    api.finish(on_finish)
    api.map_pre(on_map)
    s.handle=api.loop(1,tick)
    log("ARMING","wait_for_ready_owner=true no_full_scan=true")
    return {
        callback=on_event,stop=stop,
        status=function()
            local n=0
            for _ in pairs(s.owners) do n=n+1 end
            return {active=s.active,hook=s.hook,owners=n,frame=s.frame,
                intents=s.intents,matched=s.matched,expired=s.expired,
                unresolved=s.unresolved,pending=#s.pending}
        end
    }
end
return M
