-- SPDX-License-Identifier: MPL-2.0
-- Research-only correlation: exact script CanShow -> actual native visibility.
-- No native writes, no manufactured CanShow return, no World/Screen renderer.
local M={}
local HOOK_CLASS="/Game/MainContent/Template/UMG/TipHUD.TipHUD_C"
local AUDIT_EVERY=60
local PENDING_EVERY=30
local MAX_AUDIT=48
local MAX_PENDING=48
local WATCH_FRAMES=60 -- Correlation window, NOT a session deadline.
local function valid(o) return o~=nil and o:IsValid() end
local function path(o)
    return assert(o:GetFullName():match("^[^ ]+ (.+)$"),"UObject full path missing")
end
local function identity(w)
    assert(valid(w),"invalid CanShow context")
    assert(path(w:GetClass())==HOOK_CLASS,"CanShow widget class mismatch")
    local a=w:GetAddress()
    assert(type(a)=="number" and a>0,"invalid CanShow widget address")
    return path(w).."|"..HOOK_CLASS.."|"..tostring(a)
end
local function short(s) return tostring(s):sub(1,180) end
local function count(t)
    local n=0
    for _ in pairs(t) do n=n+1 end
    return n
end
local function sorted(t)
    local a={}
    for k in pairs(t) do a[#a+1]=k end
    table.sort(a)
    return a
end

function M.start(api,source,emit)
    assert(type(api)=="table" and type(source)=="table" and type(emit)=="function")
    for _,k in ipairs({"begin","finish","map_pre","loop","cancel",
        "bind_can_show","native_alive","hint_visible"}) do
        assert(type(api[k])=="function","missing API "..k)
    end
    for _,k in ipairs({"acquire","actor_identity","resolve_actor","snapshot"}) do
        assert(type(source[k])=="function","missing source "..k)
    end
    local s={active=true,frame=0,handle=nil,hook=false,records={},pending={},
        widgets={},queue={},head=1,active_owner=nil,
        callbacks=0,matched=0,unmatched=0,shows=0,hides=0,
        audits=0,incomplete=0,missed=0,ambiguous=0,
        begin_calls=0,end_calls=0,map_calls=0,owner_serial=0,
        last_audit=nil}
    local function trace(e,fields) emit(e,fields or "") end
    local function stop(reason)
        if not s.active then return end
        s.active=false
        if s.handle then
            local ok,removed=pcall(api.cancel,s.handle)
            trace(ok and removed and "LOOP_CANCELLED" or "LOOP_CANCEL_UNCONFIRMED","")
        end
        s.records={};s.pending={};s.widgets={};s.queue={};s.active_owner=nil
        trace("STOP","reason="..short(reason).." frame="..s.frame..
            " callbacks="..s.callbacks.." matched="..s.matched..
            " unmatched="..s.unmatched.." shows="..s.shows..
            " hides="..s.hides.." audits="..s.audits..
            " missed_observed="..s.missed.." ambiguous_audits="..s.ambiguous..
            " hook_inert=true native_writes=0")
    end
    local function guard(where,fn)
        if not s.active then return end
        local ok,e=pcall(fn)
        if not ok then stop(where..":"..short(e)) end
    end
    local function enqueue(k)
        local r=s.records[k]
        if not r or r.queued then return end
        r.queued=true;s.queue[#s.queue+1]=k
    end
    local function pop()
        local k=s.queue[s.head]
        if k==nil then
            s.queue={};s.head=1
            return nil
        end
        s.queue[s.head]=false;s.head=s.head+1
        local r=s.records[k]
        if r then r.queued=false end
        if s.head>#s.queue then
            s.queue={};s.head=1
        end
        return k
    end
    local function forget(k)
        local r=s.records[k]
        if r then
            assert(s.widgets[r.data.widget]==k,"widget reverse lookup changed")
            s.widgets[r.data.widget]=nil
            s.records[k]=nil
        end
        s.pending[k]=nil
        if s.active_owner==k then s.active_owner=nil end
    end
    local function register(rec)
        assert(type(rec)=="table" and type(rec.actor)=="string"
            and type(rec.widget)=="string" and type(rec.component)=="string"
            and (rec.action=="Open" or rec.action=="Take" or rec.action=="Check"),
            "incomplete native record")
        local prior=s.records[rec.actor]
        if prior then
            assert(prior.data.widget==rec.widget and prior.data.component==rec.component
                and prior.data.action==rec.action,"native owner rebound")
            return
        end
        assert(not s.widgets[rec.widget],"duplicate widget-to-owner identity")
        s.owner_serial=s.owner_serial+1
        s.records[rec.actor]={data=rec,id=s.owner_serial,shown=false,
            observed=false,hidden_observed=false,event_after_hide=false,
            last_event=nil,queued=false}
        s.widgets[rec.widget]=rec.actor
        s.pending[rec.actor]=nil
        trace("OWNER_JOIN","owner="..s.owner_serial.." action="..rec.action)
    end
    local function begin(arg)
        guard("BeginPlay",function()
            s.begin_calls=s.begin_calls+1
            assert(arg and type(arg.get)=="function","actor param contract")
            local actor=arg:get()
            if actor==nil then return end
            local rec,why=source.acquire(actor)
            if rec then register(rec)
            elseif why=="not_ready_component" or why=="not_ready_widget" then
                local id=assert(source.actor_identity(actor),"pending actor identity")
                s.pending[id.key]=id
            else
                assert(why=="other_action" or why=="unrelated_actor" or
                    why=="unrelated_argument" or why=="unrelated_default_object",
                    "unexpected action source: "..tostring(why))
            end
        end)
    end
    local function finish(arg)
        guard("EndPlay",function()
            s.end_calls=s.end_calls+1
            assert(arg and type(arg.get)=="function","actor param contract")
            local actor=arg:get()
            if actor==nil then return end
            local id=source.actor_identity(actor)
            if id and (s.records[id.key] or s.pending[id.key]) then
                local r=s.records[id.key]
                forget(id.key)
                trace("OWNER_END","owner="..(r and r.id or "?"))
            end
        end)
    end
    local function map_pre()
        guard("LoadMapPre",function()
            s.map_calls=s.map_calls+1
            s.records={};s.pending={};s.widgets={};s.queue={};s.head=1
            s.active_owner=nil;s.last_audit=nil
            trace("MAP_RESET","map="..s.map_calls.." hook_across_map_not_runtime_verified=true")
        end)
    end
    -- This is a SCRIPT post-hook; the hook's return is always NIL.
    -- The callback only reads immutable widget identity and queues one key.
    local function can_show(context,...)
        if not s.active then return end
        local n=select("#",...)
        guard("CanShow",function()
            assert(n==0,"CanShow unexpected arguments")
            assert(context and type(context.get)=="function","CanShow context missing")
            local k=identity(context:get())
            s.callbacks=s.callbacks+1
            local owner=s.widgets[k]
            if not owner then
                s.unmatched=s.unmatched+1
                return
            end
            s.matched=s.matched+1
            local r=assert(s.records[owner],"widget reverse lookup stale")
            r.last_event=s.frame
            r.event_after_hide=true
            if not r.shown then enqueue(owner) end
        end)
        -- Never return guard's pcall boolean or a native CanShow override.
    end
    local function sample(k,where)
        local r=s.records[k]
        if not r then return end
        local row,why=source.snapshot(r.data,api.native_alive,api.hint_visible)
        if row==nil and (why=="object_gone" or why=="object_pending_kill") then
            forget(k);trace("OWNER_STALE","owner="..r.id.." source="..where)
            return
        end
        assert(row and row.actor==k and row.widget==r.data.widget and
            row.component==r.data.component and row.action==r.data.action,
            "native snapshot identity mismatch: "..tostring(why))
        local visible=row.shown==true and row.ready==true
        if not visible then
            if r.shown then
                s.hides=s.hides+1
                trace("HIDE","owner="..r.id.." action="..row.action..
                    " frame="..s.frame.." source="..where)
                r.event_after_hide=false
            end
            r.hidden_observed=true
            r.shown=false
            if s.active_owner==k then s.active_owner=nil end
            return false
        end
        if not r.shown then
            s.shows=s.shows+1
            local age=r.last_event and s.frame-r.last_event or nil
            local evidence
            if not r.event_after_hide then
                evidence=r.hidden_observed and "NO_EVENT_SINCE_OBSERVED_HIDE"
                    or "PREEXISTING_OR_MISSED_UNKNOWN"
                if r.hidden_observed then s.missed=s.missed+1 end
            else evidence="MATCHED_EVENT_NOT_SELECTION_PROOF" end
            trace("SHOW","owner="..r.id.." action="..row.action..
                " frame="..s.frame.." source="..where..
                " event_age_frames="..tostring(age or "unknown")..
                " evidence="..evidence..
                " native_text="..string.format("%q",row.native_text or ""))
        end
        r.shown=true;r.observed=true
        if where=="FAST" then s.active_owner=k end
        return true
    end
    local function tick()
        guard("EngineTick",function()
            s.frame=s.frame+1
            if s.frame%PENDING_EVERY==0 and next(s.pending) then
                local keys=sorted(s.pending)
                for i=1,math.min(#keys,MAX_PENDING) do
                    local k=keys[i]
                    local actor=source.resolve_actor(s.pending[k],api.native_alive)
                    if not actor then forget(k)
                    else
                        local rec,why=source.acquire(actor)
                        if rec then
                            assert(rec.actor==k,"pending actor rebound")
                            register(rec)
                        else
                            assert(why=="not_ready_component" or why=="not_ready_widget",
                                "pending actor action changed")
                        end
                    end
                end
            end
            -- Must be initialized by actual owner BeginPlay first: no forced load.
            if not s.hook and next(s.records) then
                local ok,why=api.bind_can_show(can_show)
                if not ok then
                    trace("CANSHOW_UNAVAILABLE","reason="..short(why or "not_loaded")..
                        " coverage_claims=none")
                    stop("CANSHOW_NOT_READY")
                    return
                end
                s.hook=true
                trace("CANSHOW_ARMED","frame="..s.frame..
                    " pre_arm_events_unobserved=true returned_bool_unavailable=true")
            end
            local active=s.active_owner
            if active then sample(active,"FAST") end
            local k=pop()
            if k and k~=active and s.records[k] then
                local shown=sample(k,"FAST")
                local r=s.records[k]
                if r and shown~=true and r.last_event and
                    s.frame-r.last_event<WATCH_FRAMES then
                    enqueue(k)
                elseif r and shown~=true then
                    trace("EVENT_NO_VISIBLE_WITHIN_WINDOW","owner="..r.id..
                        " window_frames="..WATCH_FRAMES..
                        " transient_visibility_unknown=true")
                end
            end
            if s.frame%AUDIT_EVERY==0 and next(s.records) then
                s.audits=s.audits+1
                local keys=sorted(s.records)
                local n=#keys
                if n>MAX_AUDIT or next(s.pending) then
                    s.incomplete=s.incomplete+1
                    trace("AUDIT_INCOMPLETE","total="..n..
                        " pending="..count(s.pending)..
                        " max_reads="..MAX_AUDIT..
                        " unique_owner_claim=false")
                else
                    local visible={}
                    for _,owner in ipairs(keys) do
                        if sample(owner,"AUDIT") then
                            local r=s.records[owner]
                            if r then visible[#visible+1]=r.id..":"..r.data.action end
                        end
                    end
                    local state=#visible==0 and "none" or
                        (#visible==1 and "unique_observed" or "ambiguous")
                    if #visible>1 then s.ambiguous=s.ambiguous+1 end
                    local info="state="..state.." observed="..table.concat(visible,",")..
                        " frame="..s.frame.." complete=true"..
                        " selected_target_authority=unproved"
                    if info~=s.last_audit or s.audits%5==0 then
                        trace("AUDIT",info..
                            " callbacks="..s.callbacks.." matched="..s.matched..
                            " unmatched="..s.unmatched)
                        s.last_audit=info
                    end
                end
            end
        end)
    end
    local ok,e=pcall(function()
        api.begin(begin);api.finish(finish);api.map_pre(map_pre)
        s.handle=api.loop(1,tick)
        assert(type(s.handle)=="number" and s.handle>0,"invalid loop handle")
    end)
    if not ok then stop("registration:"..short(e))
    else trace("ARMED","read_only=true actions=Open,Take,Check"..
        " audit_every_frames="..AUDIT_EVERY.." audit_max="..MAX_AUDIT..
        " native_writes=0 timeout=none") end
    return {stop=stop,status=function()
        return {active=s.active,frame=s.frame,hook=s.hook,
            owners=count(s.records),pending=count(s.pending),
            callbacks=s.callbacks,matched=s.matched,unmatched=s.unmatched,
            shows=s.shows,hides=s.hides,audits=s.audits,
            incomplete=s.incomplete,missed=s.missed,ambiguous=s.ambiguous}
    end}
end
return M
