-- SPDX-License-Identifier: MPL-2.0
-- Bounded BeginPlay index. A first stock episode qualifies a live direct brush.
local Translation=require("IIPPrehideTranslation")
local M={}
local LIMIT=48

function M.new(api,emit)
    local owners,count,previous,queued,current,stopped={},0,nil,nil,nil,false
    local retired,active={},false
    local function close(reason,terminal)
        stopped=terminal or stopped
        for _,entry in pairs(retired) do entry.lease.restore(reason) end
        retired={}
        if terminal or (reason~="map_pre" and active) then
            for _,entry in pairs(owners) do entry.lease.restore(reason) end
            owners,count,previous,queued,current,active={},0,nil,nil,nil,false
        end
    end
    local function filter(row)
        local entry=owners[row.key]
        if row.status~="READY" then
            if active then close("context_gap",false) end
            return row
        end
        if previous~=entry then
            if previous then
                previous.lease.filter({status="READY"})
                if previous.qualified and not previous.attempted then queued=previous end
            end
            previous=entry
        end
        if not row.key and queued then
            local pending=queued
            queued=nil
            pending.attempted=true
            local a=api.resolve_actor({key=pending.record.actor,ref=pending.record.refs.actor},api.alive)
            if a then
                pending.lease.begin(a)
                pending.lease.filter({status="READY"})
            end
            active=active or pending.lease.prehidden()
        end
        current=entry
        if entry and not entry.attempted and not entry.qualified and entry.samples<120 then
            entry.samples=entry.samples+1
            local ok,token=pcall(api.qualify,row.actor,entry.record)
            if ok and token then
                entry.qualified=token
                emit("QUALIFIED","action="..entry.record.action)
            end
        end
        if entry then return entry.lease.filter(row) end
        row.actor,row.key=nil,nil
        return row
    end
    return {
        begin=function(a)
            if stopped or count>=LIMIT then return end
            local ok,r=pcall(api.acquire,a)
            if not ok or not r or owners[r.actor] then return end
            local entry={record=r,samples=0}
            local scoped=setmetatable({
                target=r.refs.actor.path,action=r.action,
                acquire=function(actor)
                    local fresh=api.acquire(actor)
                    if fresh and fresh.actor==r.actor and fresh.component==r.component
                        and fresh.widget==r.widget then return fresh end
                end,
                early_supported=function(w)
                    return entry.qualified and api.brush_token(w)==entry.qualified
                end,
            },{__index=api})
            entry.lease=Translation.new(scoped,emit)
            owners[r.actor]=entry
            count=count+1
        end,
        filter=filter,
        shown=function()if current then current.lease.shown() end end,
        prehidden=function()
            -- During NONE the old own World may be kept hidden for reuse.
            return current==nil or current.lease.prehidden()
        end,
        restore=function(reason)if current then current.lease.restore(reason) end end,
        restore_all=close,
        map_pre=function()
            for k,entry in pairs(owners) do
                if entry.lease.prehidden() then retired[k]=entry end
            end
            owners,count,previous,queued,current,active={},0,nil,nil,nil,false
        end,
        ended=function(address)
            for k,entry in pairs(retired) do
                if entry.record.refs.actor.address==address then
                    entry.lease.ended(address)
                    retired[k]=nil
                end
            end
            for key,entry in pairs(owners) do
                if entry.record.refs.actor.address==address then
                    entry.lease.ended(address)
                    if previous==entry then previous=nil end
                    if queued==entry then queued=nil end
                    if current==entry then current=nil end
                    owners[key]=nil
                    count=count-1
                    return
                end
            end
        end,
    }
end
return M
