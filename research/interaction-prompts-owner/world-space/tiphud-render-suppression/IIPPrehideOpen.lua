-- SPDX-License-Identifier: MPL-2.0
-- One placed Open. Native color writes are confined to the EngineTick pump.
local M={}
local TARGET="/Game/MainContent/Maps/sublevel_plot/0-1/0-1_plot_outerRimA_interact1.0-1_plot_outerRimA_interact1:PersistentLevel.0-1_lootbox_01_mat_ST001"

local function color(w)
    local c=w.ColorAndOpacity
    local result={}
    for _,k in ipairs({"R","G","B","A"}) do
        local n=c[k]
        assert(type(n)=="number" and n==n and math.abs(n)<math.huge,"invalid RGBA")
        result[k]=n
    end
    return result
end

local function same(a,b)
    return a.R==b.R and a.G==b.G and a.B==b.B and a.A==b.A
end

local function unbound(w)
    local d=w.ColorAndOpacityDelegate
    return type(d)=="table" and d.Object~=nil and d.Object:IsValid()==false
        and d.Object:GetAddress()==0 and d.FunctionName:ToString()=="None"
end

function M.new(api,emit)
    local pending,lease,started,shown,blocked
    local function resolve(a,r)
        if not api.alive(a) or api.key(a)~=r.actor then return end
        local c=a.ExtendedWidget
        if not api.alive(c) or api.key(c)~=r.component then return end
        local w=c:GetUserWidgetObject()
        if not api.alive(w) or api.key(w)~=r.widget
            or not api.alive(c:GetOwner()) or api.key(c:GetOwner())~=r.actor
            or not api.alive(c.Widget) or api.key(c.Widget)~=r.widget
            or not api.alive(c:GetWidget()) or api.key(c:GetWidget())~=r.widget
            or api.alive(c.NewUserWidget) or c:GetWidgetSpace()~=1 then return end
        return w,c
    end
    local function restore(reason)
        pending,started,shown,blocked=nil,nil,nil,true
        if not lease then return end
        local saved=lease
        lease=nil
        local ok,why=pcall(function()
            local a=api.resolve_actor({key=saved.record.actor,ref=saved.record.refs.actor},api.alive)
            local w=resolve(a,saved.record)
            assert(w and unbound(w),"original instance or binding unavailable")
            local current=color(w)
            if same(current,saved.original) then return end
            assert(same(current,saved.zero),"color changed by another writer")
            api.set(w,saved.original)
            assert(api.alive(w) and same(color(w),saved.original),"restore readback differs")
        end)
        emit(ok and "RESTORED" or "RESTORE_UNCONFIRMED",reason..(ok and "" or " "..tostring(why):sub(1,140)))
    end
    local function arm(row)
        if not pending or blocked or row.status~="READY" then return end
        local r=pending
        if row.key and row.key~=r.actor then return end
        pending=nil
        if row.key==r.actor then blocked=true;emit("REFUSED","already selected");return end
        local a=api.resolve_actor({key=r.actor,ref=r.refs.actor},api.alive)
        local w,c=resolve(a,r)
        assert(w and c.bAddedToScreen==false and c.bVisible==false,"early Screen boundary lost")
        assert(api.matches_action(a,"Open") and api.supported(w),"early action or state changed")
        assert(unbound(w),"color delegate unavailable or bound")
        local original=color(w)
        assert(original.A>0 and original.A<=1,"original alpha outside scope")
        local zero={R=original.R,G=original.G,B=original.B,A=0}
        lease={record=r,original=original,zero=zero}
        api.set(w,zero)
        if not lease then return end
        assert(api.alive(w) and same(color(w),zero),"early tint readback differs")
        emit("PREHIDDEN","mode="..api.mode)
    end
    local function check(row)
        arm(row)
        if not lease then return false end
        if row.status~="READY" then restore("context_gap");return false end
        if row.key~=lease.record.actor then
            started,shown=nil,nil
            return false
        end
        local w=resolve(row.actor,lease.record)
        if not w or not unbound(w) or not same(color(w),lease.zero)
            or not api.matches_action(row.actor,"Open") or not api.supported(w) then
            restore("native_contract_lost")
            return false
        end
        local time=api.now(row.actor)
        assert(type(time)=="number" and time>=0 and time<math.huge,"clock unavailable")
        if not started then started=time;emit("SELECTED","alpha=0")end
        if not shown and (time<started or time-started>=0.5) then
            restore("world_deadline")
            return false
        end
        return true
    end
    return {
        begin=function(a)
            if blocked or lease or pending or api.path(a)~=TARGET then return end
            local r=api.acquire(a)
            if r and r.action=="Open" then
                pending=r
                emit("EARLY_PAIR","queued=true")
            else
                emit("EARLY_PAIR_UNAVAILABLE","target_beginplay")
            end
        end,
        map_pre=function()pending=nil end,
        filter=function(row)
            local ok,permit=pcall(check,row)
            if not ok then restore("probe_error");emit("REFUSED",tostring(permit):sub(1,150));permit=false end
            if not permit then row.actor,row.key=nil,nil end
            return row
        end,
        shown=function()
            if not shown then shown=true;emit("WORLD_COMMAND","pixels_unverified=true")end
        end,
        prehidden=function()return lease~=nil end,
        restore=restore,
        ended=function(address)
            local r=(lease and lease.record) or pending
            if r and r.refs.actor.address==address then
                if lease then emit("RESTORE_UNCONFIRMED","owner_endplay") end
                pending,lease,started,shown,blocked=nil,nil,nil,nil,true
            end
        end,
    }
end
return M
