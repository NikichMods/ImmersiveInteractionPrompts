-- SPDX-License-Identifier: MPL-2.0
-- Research-only current committed owner observer. No gameplay/UMG writes.
local M={}
local MAX_VERIFY_FRAMES=12
local MAX_PENDING=16
local SUPPORTED={Open=true,Take=true,Check=true}
local NON_OWNER={unrelated_actor=true,unrelated_default_object=true,
    unrelated_argument=true,other_action=true}
local RETRY={not_ready_component=true,not_ready_widget=true}

function M.start(api,source,emit)
    for _,name in ipairs({"read","loop","cancel","map_pre","native_alive",
            "hint_visible"}) do
        assert(type(api[name])=="function","missing observer API "..name)
    end
    assert(type(source.acquire)=="function" and type(source.snapshot)=="function",
        "native source unavailable")
    local s={active=true,handle=nil,frame=0,context=nil,current_key="NONE",
        current_record=nil,pending={},samples=0,snapshots=0,transitions=0,
        matched=0,no_match=0,unresolved=0,gaps=0}
    local function log(event,detail) emit(event,detail or "") end
    local function clear()
        s.context=nil;s.current_key="NONE";s.current_record=nil;s.pending={}
    end
    local function stop(reason)
        if not s.active then return end
        s.active=false
        if s.handle then
            local ok,cancelled=pcall(api.cancel,s.handle)
            log(ok and cancelled and "LOOP_CANCELLED" or "LOOP_CANCEL_UNCONFIRMED")
        end
        clear()
        log("STOP","reason="..tostring(reason):sub(1,160)..
            " frames="..s.frame.." selected_reads="..s.samples..
            " visibility_snapshots="..s.snapshots.." transitions="..s.transitions..
            " matches="..s.matched.." no_matches="..s.no_match..
            " unresolved="..s.unresolved.." native_writes=0")
    end
    local function guarded(where,fn)
        if not s.active then return end
        local ok,err=pcall(fn)
        if not ok then stop(where..":"..tostring(err):sub(1,140)) end
    end
    local function try_acquire(actor,key)
        if not actor then return nil,"none" end
        local rec,why=source.acquire(actor)
        if rec then
            assert(SUPPORTED[rec.action] and type(rec.actor)=="string"
                and type(rec.component)=="string" and type(rec.widget)=="string",
                "invalid selected native owner")
            assert(rec.actor==key,"selected actor/TipHUD identity mismatch")
            return rec,"ready"
        end
        assert(NON_OWNER[why] or RETRY[why],
            "unexpected acquisition status "..tostring(why))
        return nil,why
    end
    local function snapshot(rec)
        s.snapshots=s.snapshots+1
        return source.snapshot(rec,api.native_alive,api.hint_visible)
    end
    local function verify(item,sel)
        local age=s.frame-item.frame
        if age<1 then return false end
        if item.old_required and not item.old_ok then
            local row,reason=snapshot(item.old)
            if not row then
                item.old_unresolved="old_"..tostring(reason)
            elseif row.actor==item.old.actor and not row.shown then
                item.old_ok=true;item.old_unresolved=nil
            end
        end
        if item.new_required and not item.new_ok then
            if not item.new and sel.key==item.new_key and sel.actor then
                local rec,why=try_acquire(sel.actor,sel.key)
                if rec then
                    item.new=rec
                    if s.current_key==item.new_key then s.current_record=rec end
                elseif NON_OWNER[why] then
                    item.new_required=false
                    item.new_unresolved="new_out_of_scope_"..why
                end
            end
            if item.new then
                local row,reason=snapshot(item.new)
                if not row then
                    item.new_unresolved="new_"..tostring(reason)
                elseif row.actor==item.new.actor and row.shown and row.ready then
                    item.new_ok=true;item.new_unresolved=nil
                end
            end
        end
        if (not item.old_required or item.old_ok)
                and (not item.new_required or item.new_ok) then
            if item.new_unresolved or item.old_unresolved then
                s.unresolved=s.unresolved+1
                log("INCOMPLETE","seq="..item.seq..
                    " reason="..tostring(item.new_unresolved or item.old_unresolved)..
                    " age_frames="..age)
            else
                s.matched=s.matched+1
                log("CORRELATED","seq="..item.seq.." from="..item.from..
                    " to="..item.to.." age_frames="..age..
                    " sampled_native_visibility=true not_pixels=true" ..
                    " complete_scope="..tostring(item.to=="NONE" or item.new~=nil))
            end
            return true
        end
        if age>=MAX_VERIFY_FRAMES then
            s.no_match=s.no_match+1
            log("NO_MATCH","seq="..item.seq.." from="..item.from..
                " to="..item.to.." age_frames="..age..
                " old_hidden="..tostring(item.old_ok or not item.old_required)..
                " new_shown="..tostring(item.new_ok or not item.new_required)..
                " coverage=bounded")
            return true
        end
        return false
    end
    local function tick()
        guarded("EngineTick",function()
            s.frame=s.frame+1
            local sel=api.read()
            s.samples=s.samples+1
            assert(type(sel)=="table" and type(sel.status)=="string",
                "invalid native selected-owner read")
            if sel.status=="GAP" then
                if s.context then
                    s.gaps=s.gaps+1
                    log("CONTEXT_GAP","reason="..tostring(sel.reason):sub(1,90)..
                        " hide_to_null_not_claimed=true")
                end
                clear();return
            end
            assert(sel.status=="READY" and type(sel.pawn_key)=="string"
                and type(sel.component_key)=="string"
                and (sel.actor==nil or type(sel.key)=="string"),
                "unexpected selected-owner read shape")
            local context=sel.pawn_key.." / "..sel.component_key
            if context~=s.context then
                if s.context then
                    log("CONTEXT_REPLACED","pending_dropped="..#s.pending..
                        " old_owner_not_cleared_proof=true")
                end
                clear();s.context=context
                log("CONTEXT","pawn_component_verified=true")
            end
            local newkey=sel.key or "NONE"
            if newkey~=s.current_key then
                local old=s.current_record
                local prev=s.current_key
                local rec,why=try_acquire(sel.actor,newkey)
                s.current_key=newkey;s.current_record=rec
                s.transitions=s.transitions+1
                log("TRANSITION","seq="..s.transitions.." from="..prev..
                    " to="..newkey.." supported="..tostring(rec~=nil)..
                    " acquisition="..tostring(why).." committed_read=true")
                local need_new=sel.actor~=nil and (rec~=nil or RETRY[why]==true)
                if old or need_new then
                    assert(#s.pending<MAX_PENDING,"pending transition bound exceeded")
                    s.pending[#s.pending+1]={
                        seq=s.transitions,frame=s.frame,from=prev,to=newkey,
                        old=old,old_required=old~=nil,old_ok=false,
                        new=rec,new_required=need_new,new_key=newkey,new_ok=false
                    }
                end
            end
            local keep={}
            for _,item in ipairs(s.pending) do
                if not verify(item,sel) then keep[#keep+1]=item end
            end
            s.pending=keep
        end)
    end
    api.map_pre(function()
        guarded("LoadMapPre",function()
            log("MAP_RESET","pending_dropped="..#s.pending)
            clear()
        end)
    end)
    s.handle=api.loop(1,tick)
    log("ARMED","read_only=true exact_slot=PlayerActionComponent+0x410"..
        " sample_every_frame=true max_visibility_per_transition=2"..
        " no_full_owner_scan=true")
    return {
        stop=stop,
        status=function()
            return {active=s.active,frame=s.frame,samples=s.samples,
                snapshots=s.snapshots,transitions=s.transitions,matched=s.matched,
                no_match=s.no_match,unresolved=s.unresolved,gaps=s.gaps,
                pending=#s.pending}
        end
    }
end
return M
