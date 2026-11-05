-- SPDX-License-Identifier: MPL-2.0
-- Autonomous, READ-ONLY event observer for the verified Open owner family.
-- Does not install a World component or acknowledge hypothetical bind/release.
-- UE4SS registration and sampling calls are injected by the entrypoint.
local M={}
local FRAMES=30
local MAX_BEGIN=8192
local MAX_SAMPLES=240
local MAX_CANDIDATES=8

local function unwrap(x)
    assert(x~=nil and type(x.get)=="function","UE4SS actor param contract")
    return x:get()
end
local function label(result,pending)
    if pending>0 then return "unresolved_open_owner" end
    if result.eligible then
        return (result.stable>=2 and "eligible:" or "warming:")..result.eligible
    end
    return result.reason
end
local function sorted_keys(t)
    local keys={}
    for k in pairs(t)do keys[#keys+1]=k end
    table.sort(keys)
    return keys
end

function M.start(api,source,policy,emit)
    assert(type(api)=="table" and type(source)=="table" and type(policy)=="table"
        and type(emit)=="function","missing event source/selector contract")
    for _,n in ipairs({"begin","finish","map_pre","loop","cancel","native_alive","hint_visible"})do
        assert(type(api[n])=="function","missing event API: "..n)
    end
    for _,n in ipairs({"acquire","actor_identity","resolve_actor","snapshot"})do
        assert(type(source[n])=="function","missing Open source API: "..n)
    end
    local s={active=true,ended=false,handle=nil,begin_calls=0,end_calls=0,map_calls=0,
        samples=0,joined=0,records={},pending={},last="not_sampled",
        selector=policy.new(MAX_CANDIDATES),reason="running"}
    local function count()
        local n=0
        for _ in pairs(s.records)do n=n+1 end
        for _ in pairs(s.pending)do n=n+1 end
        return n
    end
    local function trace(event,info)
        emit(event,info or "")
    end
    local function stop(reason)
        if s.ended then return end
        s.active=false;s.ended=true;s.reason=reason
        if s.handle then
            local ok,res=pcall(api.cancel,s.handle)
            trace(ok and res and "LOOP_CANCELLED" or "LOOP_CANCEL_UNCONFIRMED",
                "handle="..tostring(s.handle))
        end
        -- Global UE4SS lifecycle hooks have no locally established unregister.
        -- All captured callbacks are inert from this point to normal process exit.
        s.pending={};s.records={}
        trace("STOP","reason="..reason.." begins="..s.begin_calls..
            " joined="..s.joined.." ends="..s.end_calls.." maps="..s.map_calls..
            " samples="..s.samples.." hooks_inert=true native_writes=0")
    end
    local function guarded(kind,fn)
        if not s.active then return end
        local ok,err=pcall(fn)
        if not ok then stop(kind.."_contract:"..tostring(err):sub(1,130))end
    end
    local function add_record(rec)
        local ok,reason=policy.register(s.selector,rec.actor,rec.component,rec.widget)
        assert(ok,reason)
        s.records[rec.actor]=rec
        s.pending[rec.actor]=nil
        s.joined=s.joined+1
        trace("JOINED","number="..s.joined.." active_owner_count="..count())
    end
    local function begin(arg)
        guarded("BeginPlay",function()
            s.begin_calls=s.begin_calls+1
            assert(s.begin_calls<=MAX_BEGIN,"beginplay_budget")
            local actor=unwrap(arg)
            if actor==nil then return end
            local rec,reason=source.acquire(actor)
            if rec then
                assert(not s.pending[rec.actor] and not s.records[rec.actor],
                    "duplicate_owner_beginplay")
                assert(count()<MAX_CANDIDATES,"candidate_capacity")
                add_record(rec)
            elseif reason=="not_ready_widget" or reason=="not_ready_component" then
                local identity=assert(source.actor_identity(actor),
                    "pending Open identity missing")
                if not s.pending[identity.key] and not s.records[identity.key]then
                    assert(count()<MAX_CANDIDATES,"pending_capacity")
                    s.pending[identity.key]=identity
                    trace("OPEN_PENDING","reason="..reason.." active_owner_count="..count())
                end
            elseif reason=="other_action" or reason=="unrelated_actor"
                or reason=="unrelated_default_object" or reason=="unrelated_argument" then
                return
            else
                error("unexpected Open source result: "..tostring(reason))
            end
        end)
    end
    local function finish(arg)
        guarded("EndPlay",function()
            s.end_calls=s.end_calls+1
            local actor=unwrap(arg)
            if actor==nil then return end
            local id=source.actor_identity(actor)
            if not id then return end
            local present=s.pending[id.key]~=nil or s.records[id.key]~=nil
            if not present then return end
            s.pending[id.key]=nil
            s.records[id.key]=nil
            policy.end_actor(s.selector,id.key)
            trace("OWNER_ENDED","remaining="..count())
        end)
    end
    local function map_pre()
        guarded("LoadMapPre",function()
            s.map_calls=s.map_calls+1
            s.records={};s.pending={}
            policy.clear_world(s.selector)
            s.last="not_sampled"
            trace("MAP_CLEARED","before_new_actor_generation=true")
        end)
        -- Strictly nil return: do not override host load-map callback bool.
    end
    local function tick()
        guarded("EngineTick",function()
            s.samples=s.samples+1
            assert(s.samples<=MAX_SAMPLES,"observation_budget")
            -- Pending Open actors may gain their native widget after BeginPlay.
            -- Only previously observed primitive identities are revisited;
            -- never enumerate the World or synthesize widget initialization.
            for _,id in ipairs(sorted_keys(s.pending))do
                local identity=s.pending[id]
                local actor=source.resolve_actor(identity)
                assert(actor,"pending_actor_gone_without_endplay")
                local rec,reason=source.acquire(actor)
                if rec then
                    assert(rec.actor==id and s.records[id]==nil,"pending_identity_changed")
                    add_record(rec)
                else
                    assert(reason=="not_ready_widget" or reason=="not_ready_component",
                        "pending_actor_contract_changed:"..tostring(reason))
                end
            end
            local pending=0
            for _ in pairs(s.pending)do pending=pending+1 end
            if pending>0 then
                if s.last~="unresolved_open_owner"then
                    s.last="unresolved_open_owner"
                    trace("SELECTION","state=unresolved_open_owner count="..pending..
                        " no_target_claim=true")
                end
                return
            end
            if s.selector.count==0 then
                if s.last~="no_native_prompt"then
                    s.last="no_native_prompt"
                    trace("SELECTION","state=no_native_prompt no_target_claim=true")
                end
                return
            end
            local rows={}
            for _,id in ipairs(sorted_keys(s.records))do
                local row,reason=source.snapshot(s.records[id],api.native_alive,api.hint_visible)
                assert(row,reason or "missing_snapshot")
                rows[#rows+1]=row
            end
            local result,reason=policy.observe(s.selector,rows)
            assert(result,reason)
            local state=label(result,0)
            if state~=s.last then
                s.last=state
                trace("SELECTION","state="..state.." count="..#rows..
                    " visible="..result.visible.." stable="..result.stable..
                    " observational_only=true no_target_claim=true")
            end
        end)
        -- Read-only bounded recorder: no policy.next / bind / World allocation.
    end

    -- Register once at startup. A partial registration failure only leaves
    -- inert callbacks; source-only research must not invent unregistrars.
    local ok,err=pcall(function()
        api.begin(begin)
        api.finish(finish)
        api.map_pre(map_pre)
        s.handle=api.loop(FRAMES,tick)
        assert(type(s.handle)=="number" and s.handle>0,"invalid loop handle")
    end)
    if not ok then stop("registration:"..tostring(err):sub(1,130))
    else trace("ARMED","automatic=true hooks=BeginPlayPost,EndPlayPre,LoadMapPre interval_frames="..
        FRAMES.." max_candidates="..MAX_CANDIDATES.." no_world_component=true")
    end
    return {stop=stop,status=function()
        return {active=s.active,reason=s.reason,begin_calls=s.begin_calls,
            samples=s.samples,joined=s.joined,ends=s.end_calls,maps=s.map_calls,
            pending=s.ended and 0 or count()-s.selector.count,
            registered=s.ended and 0 or s.selector.count,last=s.last}
    end}
end
return M
