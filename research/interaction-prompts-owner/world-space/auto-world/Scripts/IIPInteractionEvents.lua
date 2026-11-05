-- SPDX-License-Identifier: MPL-2.0
-- Read-only observation of native Open/Take/Check prompts. No World UI.
-- Normal gameplay is user-paced: no sample, elapsed-time or BeginPlay deadline.
-- A fixed per-tick work budget limits native reads; incomplete sweeps are
-- explicitly non-authoritative and cannot select a target.
local M={}
local FRAMES=30
local READS_PER_SAMPLE=48
local DETAIL_JOINS=40

local function unwrap(x)
    assert(x~=nil and type(x.get)=="function","UE4SS actor param contract")
    return x:get()
end

local function short(x)
    return tostring(x):sub(1,150)
end

local function sorted_keys(a,b)
    local out={}
    for key in pairs(a)do out[#out+1]=key end
    for key in pairs(b)do
        assert(a[key]==nil,"owner present in both registries")
        out[#out+1]=key
    end
    table.sort(out)
    return out
end

local function list(v)
    table.sort(v)
    return #v==0 and "-" or table.concat(v,",")
end

function M.start(api,source,emit,sink)
    assert(type(api)=="table" and type(source)=="table" and type(emit)=="function",
        "observer contract incomplete")
    for _,name in ipairs({"begin","finish","map_pre","loop","cancel",
        "native_alive","hint_visible"})do
        assert(type(api[name])=="function","missing event API: "..name)
    end
    for _,name in ipairs({"acquire","actor_identity","resolve_actor","snapshot"})do
        assert(type(source[name])=="function","missing source API: "..name)
    end
    sink=sink or {}
    for _,name in ipairs({"on_join","on_end","on_map","on_snapshot"})do
        assert(sink[name]==nil or type(sink[name])=="function", "invalid source sink: "..name)
    end
    local s={
        active=true,ended=false,reason="running",handle=nil,
        begin_calls=0,end_calls=0,map_calls=0,samples=0,joined=0,
        records={},pending={},by_widget={},by_component={},visible_paths_logged={},
        native_visibility={},
        registered=0,pending_count=0,ids={},serial=0,
        order={},dirty=true,cursor=1,last="not_sampled",
        choice=nil,streak=0
    }
    local function trace(event,msg)
        emit(event,msg or "")
    end
    local function invalidate()
        s.dirty=true
        s.choice=nil;s.streak=0
    end
    local function stop(reason)
        if s.ended then return end
        s.ended=true;s.active=false;s.reason=reason
        if s.handle then
            local ok,removed=pcall(api.cancel,s.handle)
            trace(ok and removed and "LOOP_CANCELLED" or "LOOP_CANCEL_UNCONFIRMED",
                "handle="..tostring(s.handle))
        end
        -- No verified global-hook unregistrar. Captured callbacks remain inert.
        s.records={};s.pending={};s.ids={};s.by_widget={};s.by_component={}
        s.visible_paths_logged={};s.native_visibility={}
        s.registered=0;s.pending_count=0;s.order={}
        trace("STOP","reason="..short(reason).." begins="..s.begin_calls..
            " joined="..s.joined.." ends="..s.end_calls.." maps="..s.map_calls..
            " samples="..s.samples.." hooks_inert=true source_native_writes=0")
    end
    local function guarded(kind,fn)
        if not s.active then return end
        local ok,err=pcall(fn)
        if not ok then stop(kind.."_contract:"..short(err))end
    end
    local function owner_id(key)
        if not s.ids[key] then
            s.serial=s.serial+1
            s.ids[key]=s.serial
        end
        return s.ids[key]
    end
    local function forget(key)
        local rec=s.records[key]
        local was_pending=s.pending[key]~=nil
        if rec then
            assert(s.by_widget[rec.widget]==key and
                s.by_component[rec.component]==key,"reverse identity contract changed")
            s.by_widget[rec.widget]=nil
            s.by_component[rec.component]=nil
            s.records[key]=nil
            s.registered=s.registered-1
        end
        if s.pending[key]then
            s.pending[key]=nil
            s.pending_count=s.pending_count-1
        end
        s.ids[key]=nil
        if (rec or was_pending) and sink.on_end then sink.on_end(key) end
        s.visible_paths_logged[key]=nil
        s.native_visibility[key]=nil
        invalidate()
    end
    local function register(rec,from)
        assert(type(rec)=="table" and type(rec.actor)=="string"
            and type(rec.component)=="string" and type(rec.widget)=="string"
            and (rec.action=="Open" or rec.action=="Take" or rec.action=="Check"),
            "interaction record incomplete")
        local old=s.records[rec.actor]
        if old then
            assert(old.widget==rec.widget and old.component==rec.component
                and old.action==rec.action,"owner rebound")
            return
        end
        assert(not s.by_component[rec.component] and not s.by_widget[rec.widget],
            "native widget/component shared across owners")
        s.by_component[rec.component]=rec.actor
        s.by_widget[rec.widget]=rec.actor
        s.records[rec.actor]=rec
        s.registered=s.registered+1
        if s.pending[rec.actor]then
            s.pending[rec.actor]=nil
            s.pending_count=s.pending_count-1
        end
        s.joined=s.joined+1
        invalidate()
        if sink.on_join then
            sink.on_join({actor=rec.actor,component=rec.component,
                widget=rec.widget,action=rec.action})
        end
        local id=owner_id(rec.actor)
        if s.joined<=DETAIL_JOINS then
            trace("JOINED","owner="..id.." action="..rec.action..
                " ready_at="..from.." sample="..s.samples..
                " actor="..string.format("%q",rec.refs.actor.path)..
                " component="..string.format("%q",rec.refs.component.path)..
                " widget="..string.format("%q",rec.refs.widget.path))
        elseif s.joined==DETAIL_JOINS+1 then
            trace("JOIN_DETAIL_SUPPRESSED","native_reads_continue=true shown_owner_details_retained=true")
        elseif s.joined%100==0 then
            trace("JOIN_SUMMARY","joined="..s.joined.." registered="..s.registered)
        end
    end
    local function begin(arg)
        guarded("BeginPlay",function()
            s.begin_calls=s.begin_calls+1
            local actor=unwrap(arg)
            if actor==nil then return end
            local rec,why=source.acquire(actor)
            if rec then
                register(rec,"beginplay")
            elseif why=="not_ready_widget" or why=="not_ready_component" then
                local identity=assert(source.actor_identity(actor),
                    "unready supported actor has no identity")
                if not s.records[identity.key] and not s.pending[identity.key] then
                    s.pending[identity.key]=identity
                    s.pending_count=s.pending_count+1
                    invalidate()
                    trace("PENDING","owner="..owner_id(identity.key)..
                        " reason="..why.." actor="..string.format("%q",identity.ref.path))
                end
            else
                assert(why=="other_action" or why=="unrelated_actor" or
                    why=="unrelated_argument" or why=="unrelated_default_object",
                    "unexpected acquisition:"..tostring(why))
            end
        end)
    end
    local function finish(arg)
        guarded("EndPlay",function()
            s.end_calls=s.end_calls+1
            if s.end_calls==1 then trace("ENDPLAY_SEEN","sample="..s.samples) end
            local actor=unwrap(arg)
            if actor==nil then return end
            local id=source.actor_identity(actor)
            if not id or (not s.records[id.key] and not s.pending[id.key])then return end
            local owner=owner_id(id.key)
            forget(id.key)
            trace("OWNER_ENDED","owner="..owner.." remaining="..
                (s.registered+s.pending_count))
        end)
    end
    local function map_pre()
        guarded("LoadMapPre",function()
            s.map_calls=s.map_calls+1
            s.records={};s.pending={};s.by_widget={};s.by_component={}
            s.visible_paths_logged={};s.native_visibility={}
            s.registered=0;s.pending_count=0;s.ids={}
            s.order={};s.cursor=1;s.last="not_sampled"
            invalidate()
            if sink.on_map then sink.on_map() end
            trace("MAP_CLEARED","map_calls="..s.map_calls)
        end)
        -- Must return nil; never override UE4SS native LoadMap result.
    end
    local function tick()
        guarded("EngineTick",function()
            s.samples=s.samples+1 -- Lifetime diagnostic counter, not a deadline.
            if s.dirty then
                s.order=sorted_keys(s.pending,s.records)
                s.cursor=1;s.dirty=false
            end
            local n=#s.order
            local scanned=math.min(n,READS_PER_SAMPLE)
            local rows,shown,ready,hidden,pending={},{},{},{},{}
            local incomplete=n>READS_PER_SAMPLE
            for i=1,scanned do
                local key=s.order[s.cursor]
                s.cursor=s.cursor%n+1
                local identity=s.pending[key]
                if identity then
                    local actor=source.resolve_actor(identity,api.native_alive)
                    if not actor then
                        local owner=owner_id(key)
                        forget(key)
                        trace("STALE_PENDING","owner="..owner.." no_native_write=true")
                    else
                        local rec,why=source.acquire(actor)
                        if rec then
                            assert(rec.actor==key,"pending owner changed identity")
                            register(rec,"retry")
                        else
                            assert(why=="not_ready_widget" or why=="not_ready_component",
                                "pending owner changed action:"..tostring(why))
                            pending[#pending+1]=owner_id(key)
                        end
                    end
                    incomplete=true
                else
                    local rec=s.records[key]
                    if rec then
                        local row,why=source.snapshot(rec,api.native_alive,api.hint_visible)
                        if not row and (why=="object_gone" or why=="object_pending_kill") then
                            local owner=owner_id(key)
                            forget(key)
                            trace("STALE_OWNER","owner="..owner.." why="..why..
                                " no_native_write=true")
                            incomplete=true
                        else
                            assert(row,why or "invalid native snapshot")
                            assert(row.action==rec.action and row.actor==key and
                                row.component==rec.component and row.widget==rec.widget,
                                "snapshot action/owner identity changed")
                            rows[#rows+1]=row
                            local label=tostring(owner_id(key))..":"..row.action
                            local last=s.native_visibility[key]
                            if not last or last.shown~=row.shown or last.ready~=row.ready then
                                s.native_visibility[key]={shown=row.shown,ready=row.ready}
                                if row.shown or (last and last.shown) then
                                    trace("OWNER_VISIBILITY","owner="..owner_id(key)..
                                        " action="..row.action..
                                        " shown="..tostring(row.shown)..
                                        " ready="..tostring(row.ready)..
                                        " observed_only=true")
                                end
                            end
                            if row.shown then
                                if not s.visible_paths_logged[key] then
                                    s.visible_paths_logged[key]=true
                                    trace("VISIBLE_OWNER","owner="..owner_id(key)..
                                        " action="..row.action..
                                        " actor="..string.format("%q",rec.refs.actor.path)..
                                        " text="..string.format("%q",row.native_text or "")..
                                        " shown=true observed_only=true")
                                end
                                shown[#shown+1]=label
                                if row.ready then ready[#ready+1]=label end
                            else hidden[#hidden+1]=label end
                        end
                    else incomplete=true end
                end
            end
            if s.pending_count>0 or #rows~=s.registered then incomplete=true end
            local state
            if incomplete then
                state="incomplete_snapshot"
                s.choice=nil;s.streak=0
            elseif #shown==0 then
                state="no_native_prompt";s.choice=nil;s.streak=0
            elseif #shown>1 then
                state="ambiguous_native_prompts";s.choice=nil;s.streak=0
            elseif #ready~=1 then
                state="native_hint_not_ready";s.choice=nil;s.streak=0
            else
                local unique=ready[1]
                if unique==s.choice then s.streak=math.min(2,s.streak+1)
                else s.choice=unique;s.streak=1 end
                state=(s.streak>=2 and "unique_observed:" or "warming:")..unique
            end
            local details
            if incomplete then
                -- Partial rotated batches are not comparable simultaneous snapshots.
                -- Do not emit a false show/hide transition merely because
                -- a different batch was scanned on the next tick.
                details="state=incomplete_snapshot total="..n..
                    " max_reads="..READS_PER_SAMPLE.." no_unique_target_claim=true"
            else
                details="state="..state.." scanned="..scanned.." total="..n..
                    " ready_owners="..list(ready).." shown_owners="..list(shown)..
                    " hidden_owners="..list(hidden).." pending_owners="..list(pending)
            end
            if sink.on_snapshot then
                -- Source-only primitive copy. No UObject wrappers cross this boundary.
                local safe={}
                for _,row in ipairs(rows)do
                    safe[#safe+1]={actor=row.actor,component=row.component,
                        widget=row.widget,action=row.action,
                        shown=row.shown,ready=row.ready}
                end
                sink.on_snapshot(safe,not incomplete)
            end
            if details~=s.last then
                s.last=details
                trace("SELECTION",details.." sample="..s.samples..
                    " observational_only=true target_selection_unproven=true")
            end
        end)
    end
    -- No manual activation/reload. A partially registered hook remains inert
    -- on failure, rather than guessing a native unregistration operation.
    local ok,err=pcall(function()
        api.begin(begin)
        api.finish(finish)
        api.map_pre(map_pre)
        s.handle=api.loop(FRAMES,tick)
        assert(type(s.handle)=="number" and s.handle>0,"invalid loop handle")
    end)
    if not ok then stop("registration:"..short(err))
    else
        trace("ARMED","actions=Open,Take,Check automatic=true interval_frames="..
            FRAMES.." max_native_reads_per_sample="..READS_PER_SAMPLE..
            " duration=until_host_exit_or_explicit_stop read_only_collector=true")
    end
    return {stop=stop,status=function()
        return {
            active=s.active,reason=s.reason,begin_calls=s.begin_calls,
            joined=s.joined,registered=s.registered,pending=s.pending_count,
            ends=s.end_calls,maps=s.map_calls,samples=s.samples,last=s.last
        }
    end}
end
return M
