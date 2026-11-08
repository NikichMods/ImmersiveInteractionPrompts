-- SPDX-License-Identifier: MPL-2.0
-- Safe wide inventory: native owner discovery is game-wide for Open/Take/Check.
-- Only exact already-tested placements are eligible for first-frame suppression.
-- Unknown geometry keeps the native Screen. No new native writes.
local Coverage=require("IIPTranslationCoverage")
local M={}
local LIMIT=256

function M.new(api,emit)
    assert(type(api)=="table" and type(api.early_target)=="function"
        and type(api.acquire)=="function" and type(api.placement_sample)=="function",
        "wide inventory gates unavailable")
    local core=Coverage.new(api,emit)
    local unknown,count,over_limit={},0,false

    local function checked(record)
        return record and type(record.actor)=="string" and type(record.refs)=="table"
            and type(record.refs.actor)=="table"
            and (record.action=="Open" or record.action=="Take" or record.action=="Check")
    end
    local function begin(actor)
        local ok,record=pcall(api.acquire,actor)
        if not ok or not checked(record) then return end
        if api.early_target(record.refs.actor.path)==record.action then
            -- The existing coordinator still performs all its early-identity
            -- and actual prehide guards. This wrapper never grants a lease.
            core.begin(actor)
            return
        end
        if unknown[record.actor] then return end
        if count>=LIMIT then
            if not over_limit then emit("SURVEY_LIMIT","unverified_objects_stock_only=true");over_limit=true end
            return
        end
        unknown[record.actor]={record=record,sampled=false}
        count=count+1
        emit("STOCK_UNVERIFIED","action="..record.action.." class="..
            tostring(record.refs.actor.class).." reason=placement_unknown")
    end
    local function filter(row)
        if row and row.status=="READY" and row.key then
            local entry=unknown[row.key]
            if entry and not entry.sampled then
                entry.attempts=(entry.attempts or 0)+1
                local ok,detail=pcall(function()
                    local record=entry.record
                    local fresh=api.acquire(row.actor)
                    assert(checked(fresh) and fresh.actor==record.actor
                        and fresh.component==record.component and fresh.widget==record.widget
                        and fresh.action==record.action, "survey owner changed")
                    return api.placement_sample(row.actor,record)
                end)
                if not ok or detail~=nil or entry.attempts>=8 then
                    entry.sampled=true
                    local event=ok and detail and "SURVEY_SAMPLE" or "SURVEY_UNAVAILABLE"
                    emit(event,"action="..entry.record.action.." "..
                        (ok and tostring(detail or "native_not_ready") or tostring(detail):sub(1,140))..
                        " stock_only=true")
                end
            end
        end
        -- Still forward the real selection into the stock/World coordinator
        -- so it can process NONE, owner transitions and release itself.
        return core.filter(row)
    end
    return {
        begin=begin,filter=filter,
        shown=core.shown,prehidden=core.prehidden,
        restore=core.restore,restore_all=core.restore_all,
        map_pre=function()
            core.map_pre()
            unknown,count,over_limit={},0,false
        end,
        ended=function(address)
            core.ended(address)
            for key,entry in pairs(unknown) do
                if entry.record.refs.actor.address==address then
                    unknown[key]=nil;count=count-1
                end
            end
        end,
    }
end
return M
