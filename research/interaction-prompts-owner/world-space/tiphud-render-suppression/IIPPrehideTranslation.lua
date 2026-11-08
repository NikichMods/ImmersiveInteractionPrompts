-- SPDX-License-Identifier: MPL-2.0
-- One placed Open. Move only the native TipHUD's own CanvasPanel_0 render
-- subtree. Never move the ExtendedWidgetComponent or change native visibility.
-- Exact-host research candidate; source-only, not runtime accepted.
local M={}
local TARGET="/Game/MainContent/Maps/sublevel_plot/0-1/0-1_plot_outerRimA_interact1.0-1_plot_outerRimA_interact1:PersistentLevel.0-1_lootbox_01_mat_ST001"
local OFFSCREEN_X=16384 -- Research-only at verified 2560x1440; not a global screen guarantee.

local function finite(n)
    return type(n)=="number" and n==n and math.abs(n)<math.huge
end
local function pos(p)
    local t=p.RenderTransform
    assert(t~=nil and t.Translation~=nil,"render translation inaccessible")
    local x,y=t.Translation.X,t.Translation.Y
    assert(finite(x) and finite(y),"invalid render translation")
    return {X=x,Y=y}
end
local function same(a,b)
    return a.X==b.X and a.Y==b.Y
end
local function identity(api,o)
    return {path=api.path(o),address=o:GetAddress()}
end
local function same_identity(api,o,id)
    return api.alive(o) and id and api.path(o)==id.path
        and o:GetAddress()==id.address
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
        local tree=w.WidgetTree
        if not api.alive(tree) then return end
        local p=tree.RootWidget
        if not api.alive(p) or api.class(p)~="/Script/UMG.CanvasPanel"
            or not api.path(p):match("%.CanvasPanel_0$") 
            or not api.alive(p:GetOuter()) or p:GetOuter():GetAddress()~=tree:GetAddress()
            then return end
        return w,c,p
    end
    local function get_saved(saved)
        local a=api.resolve_actor({key=saved.record.actor,ref=saved.record.refs.actor},api.alive)
        local w,c,p=resolve(a,saved.record)
        if not w or not same_identity(api,p,saved.panel) then return end
        return a,w,c,p
    end
    local function restore(reason)
        pending,started,shown,blocked=nil,nil,nil,true
        if not lease then return end
        local saved=lease
        lease=nil
        local ok,detail=pcall(function()
            local a,w,c,p=get_saved(saved)
            assert(p,"original root panel or instance unavailable")
            local current=pos(p)
            if same(current,saved.original) then return " original_present=true" end
            assert(same(current,saved.offscreen),"render transform changed by another writer")
            api.set(p,saved.original)
            assert(api.alive(p) and same(pos(p),saved.original),"restore readback differs")
            return " setter_verified=true"
        end)
        emit(ok and "RESTORED" or "RESTORE_UNCONFIRMED",
            reason..(ok and detail or " "..tostring(detail):sub(1,160)))
    end
    local function arm(row)
        if not pending or blocked or row.status~="READY" then return end
        local r=pending
        if row.key and row.key~=r.actor then return end
        pending=nil
        if row.key==r.actor then
            blocked=true
            emit("REFUSED","already selected")
            return
        end
        local a=api.resolve_actor({key=r.actor,ref=r.refs.actor},api.alive)
        local w,c,p=resolve(a,r)
        assert(w and p and c.bAddedToScreen==false and c.bVisible==false,
            "early Screen boundary or native root unavailable")
        assert(api.matches_action(a,"Open") and api.supported(w),
            "early action or state changed")
        local original=pos(p)
        assert(math.abs(original.X)<=4096 and math.abs(original.Y)<=4096,
            "unexpected native render translation")
        local offscreen={X=original.X+OFFSCREEN_X,Y=original.Y}
        lease={record=r,panel=identity(api,p),original=original,offscreen=offscreen}
        api.set(p,offscreen)
        assert(api.alive(p) and same_identity(api,p,lease.panel)
            and same(pos(p),offscreen),"early render translation readback differs")
        emit("PREHIDDEN","mode="..api.mode.." offscreen_x="..OFFSCREEN_X)
    end
    local function check(row)
        arm(row)
        if not lease then return false end
        if row.status~="READY" then restore("context_gap");return false end
        if row.key~=lease.record.actor then
            started,shown=nil,nil
            return false
        end
        local a,w,c,p=get_saved(lease)
        local reason
        if not p then reason="identity_changed"
        else
            local current=pos(p)
            if not same(current,lease.offscreen) then
                reason=string.format("translation_changed x=%.9g y=%.9g",
                    current.X,current.Y)
            elseif not api.matches_action(row.actor,"Open") then reason="action_changed"
            else
                local supported,detail=api.supported(w)
                if not supported then reason=detail or "unsupported_state" end
            end
        end
        if reason then restore(reason);return false end
        local time=api.now(row.actor)
        assert(finite(time) and time>=0,"clock unavailable")
        if not started then started=time;emit("SELECTED","render_translation_offscreen=true")end
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
            else emit("EARLY_PAIR_UNAVAILABLE","target_beginplay") end
        end,
        map_pre=function()pending=nil end,
        filter=function(row)
            local ok,permit=pcall(check,row)
            if not ok then
                restore("probe_error")
                emit("REFUSED",tostring(permit):sub(1,160))
                permit=false
            end
            if not permit then row.actor,row.key=nil,nil end
            return row
        end,
        shown=function()
            if not shown then shown=true;emit("WORLD_COMMAND","pixels_unverified=true") end
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
