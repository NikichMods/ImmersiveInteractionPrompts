-- SPDX-License-Identifier: MPL-2.0
-- Source-only World ownership coordinator. Native rendering is injected;
-- this module never invokes UE4SS or resolves UObject references.
-- A new target cannot bind until the previous own resources are CLEANED.
local M={}

local function valid(v)
    return type(v)=="string" and #v>0 and #v<=1024 and not v:find("[%c]")
end
local function copy(r)
    assert(type(r)=="table" and valid(r.actor) and valid(r.component)
        and valid(r.widget) and (r.action=="Open" or r.action=="Take"
        or r.action=="Check"),"invalid owner identity")
    return {actor=r.actor,component=r.component,widget=r.widget,action=r.action}
end
local function same(a,b)
    return a.actor==b.actor and a.component==b.component
        and a.widget==b.widget and a.action==b.action
end

function M.new(renderer,emit)
    assert(type(renderer)=="table" and type(emit)=="function","handoff API unavailable")
    for _,name in ipairs({"empty","create","hide","resume","refresh","cleanup"})do
        assert(type(renderer[name])=="function","missing renderer action: "..name)
    end
    local s={records={},components={},widgets={},count=0,
        selected=nil,phase="idle",desired=nil,choice=nil,streak=0,
        epoch=0,serial=0,bound_ticket=nil,release_ticket=nil,
        force_release=false,release_reason=nil,blocked=false,
        fault=nil,stopped=false,reason="no_snapshot",
        changes=0,cleans=0,binds=0}
    local function trace(kind,info)emit(kind,info or "")end
    local function reset_choice(reason)
        s.desired=nil;s.choice=nil;s.streak=0;s.reason=reason
    end
    local function fail(why)
        if not s.fault then
            s.fault=tostring(why):sub(1,200)
            trace("FAULT","reason="..s.fault)
        end
        reset_choice("fault")
        s.force_release=true
        s.release_reason="fault"
        return nil,s.fault
    end
    local function invoke(kind,...)
        local ok,result=pcall(renderer[kind],...)
        if not ok then return fail(kind..":"..tostring(result))end
        return result
    end
    local function assert_empty()
        local x=invoke("empty")
        if x==nil then return nil end
        if x~=true then return fail("own_resources_not_clean")end
        return true
    end
    local function drop(key)
        local old=s.records[key]
        if not old then return false end
        assert(s.components[old.component]==key and
            s.widgets[old.widget]==key,"registry reverse identity mismatch")
        s.components[old.component]=nil;s.widgets[old.widget]=nil
        s.records[key]=nil;s.count=s.count-1
        reset_choice("registry_changed")
        if s.selected==key then
            s.force_release=true;s.release_reason="owner_ended"
        end
        return true
    end
    local api={}
    function api.register(input)
        if s.fault or s.stopped then return nil,"disabled" end
        local ok,r=pcall(copy,input)
        if not ok then return fail("registration:"..tostring(r))end
        local old=s.records[r.actor]
        if old then
            if not same(old,r) then return fail("actor_rebound")end
            return true,"unchanged"
        end
        if s.components[r.component] or s.widgets[r.widget] then
            return fail("shared_component_or_widget")
        end
        s.records[r.actor]=r
        s.components[r.component]=r.actor
        s.widgets[r.widget]=r.actor
        s.count=s.count+1
        reset_choice("registry_changed")
        return true,"added"
    end
    function api.end_actor(key)
        if s.stopped or s.fault then return false end
        if not valid(key) then return fail("invalid_endplay_identity")end
        return drop(key)
    end
    function api.map_pre()
        if s.stopped then return end
        s.records={};s.components={};s.widgets={};s.count=0
        reset_choice("map_cleared")
        if s.selected then
            s.force_release=true;s.release_reason="map_pre"
        end
    end
    -- A native observer may supply partial rotated batches; these must never
    -- be treated as a complete simultaneous visibility snapshot.
    function api.observe(rows,complete)
        if s.stopped or s.fault then return nil,"disabled" end
        s.epoch=s.epoch+1
        if complete~=true then
            reset_choice("incomplete_snapshot")
            return {reason=s.reason,stable=0}
        end
        if type(rows)~="table" or #rows~=s.count then
            return fail("incomplete_claimed_complete_snapshot")
        end
        local seen,visible,found,ready={},0,nil,false
        for _,row in ipairs(rows)do
            if type(row)~="table" or not valid(row.actor) or seen[row.actor] or
                type(row.shown)~="boolean" or type(row.ready)~="boolean" then
                return fail("malformed_snapshot")
            end
            local record=s.records[row.actor]
            if not record or not same(record,row)then return fail("snapshot_identity_changed")end
            seen[row.actor]=true
            if row.shown then
                visible=visible+1
                found=row.actor
                ready=row.ready
            end
        end
        local choice
        if visible==1 and ready then choice=found end
        if choice and s.choice==choice then
            s.streak=math.min(s.streak+1,2)
        else
            s.choice=choice;s.streak=choice and 1 or 0
        end
        s.desired=(s.streak>=2) and choice or nil
        if visible==0 then s.reason="no_native_prompt"
        elseif visible>1 then s.reason="ambiguous_native_prompts"
        elseif not ready then s.reason="native_hint_not_ready"
        else s.reason="unique_native_prompt" end
        return {reason=s.reason,stable=s.streak,eligible=s.desired,visible=visible}
    end
    function api.stop(reason)
        if not s.stopped then
            s.stopped=true
            reset_choice("user_stop")
            s.force_release=true
            s.release_reason=reason or "user_stop"
        end
    end
    -- Never retry a failed cleanup on every frame. A separate explicit
    -- decision must trigger retry after examining the failure.
    function api.retry_cleanup()
        assert(s.selected and s.blocked and s.phase=="cleanup_blocked",
            "no retryable cleanup")
        s.blocked=false;s.phase="release_required"
    end
    -- Call only from a separate verified game-thread boundary.
    -- One renderer mutation per pump, so reentrancy in a hook never causes
    -- an immediate destroy+construct chain.
    function api.pump()
        if s.blocked then return "cleanup_blocked" end
        if s.selected then
            local release=s.force_release or s.fault~=nil or s.stopped
                or not s.records[s.selected]
                or (s.desired~=nil and s.desired~=s.selected)
            if release then
                if s.phase=="shown"then
                    local ok=invoke("hide")
                    if ok==nil then s.phase="release_required";return "hide_failed" end
                    if ok~=true then fail("hide_not_confirmed");s.phase="release_required";return "hide_failed" end
                    s.phase="release_required"
                    return "hidden_before_release"
                end
                if not s.release_ticket then
                    s.serial=s.serial+1;s.release_ticket=s.serial
                end
                local ticket=s.release_ticket
                local cleaned=invoke("cleanup",s.release_reason or "change_target",ticket)
                if cleaned==nil or cleaned~=true then
                    if cleaned~=nil then fail("cleanup_not_confirmed")end
                    s.blocked=true;s.phase="cleanup_blocked"
                    trace("CLEANUP_BLOCKED","ticket="..ticket.." no_rebind=true")
                    return "cleanup_blocked"
                end
                -- A successful return is not enough: independently query the
                -- adapter's native ownership evidence.
                local empty=assert_empty()
                if not empty then
                    s.blocked=true;s.phase="cleanup_blocked"
                    trace("CLEANUP_BLOCKED","ticket="..ticket.." empty_not_proven=true")
                    return "cleanup_blocked"
                end
                trace("CLEANED","ticket="..ticket.." own_resources_empty=true")
                s.cleans=s.cleans+1
                s.selected=nil;s.bound_ticket=nil;s.release_ticket=nil
                s.force_release=false;s.release_reason=nil
                s.phase="idle"
                -- Fresh full snapshots after release; old observations
                -- cannot authorize allocating the next object.
                reset_choice("need_fresh_post_cleanup_snapshot")
                trace("RELEASED","ticket="..ticket.." next_bind_requires_fresh_observation=true")
                return "cleaned"
            end
            if s.desired==s.selected then
                if s.phase=="hidden" then
                    local ok=invoke("resume")
                    if ok~=true then
                        if ok~=nil then fail("resume_not_confirmed")end
                        return "resume_failed"
                    end
                    s.phase="shown"
                    return "resumed"
                end
                if s.phase=="shown" then
                    local ok=invoke("refresh")
                    if ok~=true then
                        if ok~=nil then fail("refresh_not_confirmed")end
                        return "refresh_failed"
                    end
                    return "refreshed"
                end
            else
                if s.phase=="shown" then
                    local ok=invoke("hide")
                    if ok~=true then
                        if ok~=nil then fail("hide_not_confirmed")end
                        return "hide_failed"
                    end
                    s.phase="hidden"
                    return "hidden"
                end
            end
            return "retained_hidden"
        end
        if s.stopped or s.fault then return "disabled" end
        if not s.desired or not s.records[s.desired] then return "no_target" end
        if not assert_empty() then return "disabled" end
        s.serial=s.serial+1
        local ticket=s.serial
        s.selected=s.desired -- In case create throws after partial allocation.
        s.phase="allocating";s.bound_ticket=ticket
        local owner=s.records[s.desired]
        local created=invoke("create",copy(owner),ticket)
        if created~=true then
            if created~=nil then fail("create_not_confirmed")end
            s.phase="release_required"
            return "create_failed_cleanup_required"
        end
        s.phase="hidden" -- Native World host must start hidden, not shown.
        s.binds=s.binds+1
        trace("BOUND","ticket="..ticket.." action="..owner.action..
            " native_host_acceptance_unverified=true")
        return "bound_hidden"
    end
    function api.status()
        return {registered=s.count,selected=s.selected,desired=s.desired,
            phase=s.phase,fault=s.fault,stopped=s.stopped,blocked=s.blocked,
            reason=s.reason,epoch=s.epoch,streak=s.streak,
            binds=s.binds,cleans=s.cleans,release_ticket=s.release_ticket}
    end
    return api
end
return M
