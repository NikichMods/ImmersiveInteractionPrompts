-- SPDX-License-Identifier: MPL-2.0
-- Research-only lease: shift the exact selected TipHUD root out of Screen
-- after the independent World widget reports SHOWN. Preserve native controls.
local M={}
local SHIFT_X=16384 -- Observed at 2560x1440; not a general resolution guarantee.
local function finite(n)return type(n)=="number" and n==n and math.abs(n)<math.huge end
local function xy(p)
    local t=p.RenderTransform
    assert(t and t.Translation,"native panel render translation absent")
    local x,y=t.Translation.X,t.Translation.Y
    assert(finite(x) and finite(y),"native panel translation invalid")
    return {X=x,Y=y}
end
local function same(a,b)return a.X==b.X and a.Y==b.Y end

function M.new(api,emit)
    local lease,blocked
    local function id(o)return {path=api.path(o),address=o:GetAddress()}end
    local function exact(o,r)
        return r and api.alive(o) and api.path(o)==r.path and o:GetAddress()==r.address
    end
    local function get(row,actor,for_restore)
        assert(row and row.refs and exact(actor,row.refs.actor),"selected actor changed")
        local component=actor.ExtendedWidget
        assert(exact(component,row.refs.component)
            and exact(component:GetOwner(),row.refs.actor)
            and component:GetWidgetSpace()==1
            and (for_restore or (component.bAddedToScreen==true and component.bVisible==true)),
            "selected native Screen component changed")
        local w=component:GetUserWidgetObject()
        assert(exact(w,row.refs.widget)
            and exact(component:GetWidget(),row.refs.widget)
            and exact(component.Widget,row.refs.widget)
            and (not api.alive(component.NewUserWidget)
                or exact(component.NewUserWidget,row.refs.widget)),
            "selected native TipHUD changed")
        local tree=w.WidgetTree
        assert(api.alive(tree),"native widget tree unavailable")
        local panel=tree.RootWidget
        assert(api.alive(panel) and api.class(panel)=="/Script/UMG.CanvasPanel"
            and api.path(panel):match("%.CanvasPanel_0$")
            and api.alive(panel:GetOuter())
            and panel:GetOuter():GetAddress()==tree:GetAddress(),
            "native root panel contract changed")
        return panel
    end
    local function resolve()
        if not lease then return end
        local actor=api.lookup(lease.actor.path)
        if not exact(actor,lease.actor) then return end
        local ok,p=pcall(get,lease.row,actor,true)
        if not ok or not exact(p,lease.panel) then return end
        return p
    end
    local function restore(reason)
        if not lease then return true end
        local p=resolve()
        if not p then
            emit("RESTORE_UNCONFIRMED","reason="..reason.." identity_unavailable=true")
            return false
        end
        local ok,result=pcall(function()
            local current=xy(p)
            if same(current,lease.original) then return "original_present=true" end
            assert(same(current,lease.offscreen),"native render translation changed by another writer")
            api.set(p,lease.original)
            assert(exact(p,lease.panel) and same(xy(p),lease.original),
                "native Screen restore readback differs")
            return "setter_verified=true"
        end)
        if not ok then
            emit("RESTORE_UNCONFIRMED","reason="..reason.." "..tostring(result):sub(1,160))
            return false
        end
        blocked=lease.row.actor
        lease=nil
        emit("RESTORED","reason="..reason.." "..result)
        return true
    end
    local function hide(row,actor)
        local panel=get(row,actor)
        local original=xy(panel)
        assert(math.abs(original.X)<=4096 and math.abs(original.Y)<=4096,
            "unexpected native render translation")
        local offscreen={X=original.X+SHIFT_X,Y=original.Y}
        lease={row=row,actor=id(actor),panel=id(panel),original=original,offscreen=offscreen}
        api.set(panel,offscreen)
        assert(exact(panel,lease.panel) and same(xy(panel),offscreen),
            "native render translation readback differs")
        emit("HIDDEN","offset_x="..SHIFT_X.." world_command_shown=true pixels_unverified=true")
    end
    local function observe(row,actor,world_shown)
        if lease then
            if not world_shown or not row or row.actor~=lease.row.actor then
                return restore("world_unavailable_or_selection_changed")
            end
            local panel=resolve()
            if not panel then return restore("native_identity_changed") end
            if same(xy(panel),lease.offscreen) then return true end
            -- Never overwrite another writer's transform.
            return restore("render_translation_changed")
        end
        if not row then blocked=nil;return true end
        if not world_shown or blocked==row.actor then return true end
        local ok,err=pcall(hide,row,actor)
        if not ok then
            blocked=row.actor
            emit("REFUSED","reason="..tostring(err):sub(1,160))
            if lease then return restore("failed_hide") end
        end
        return true -- Unsupported/denied means native Screen remains.
    end
    return {
        observe=observe,restore=restore,
        active=function()return lease~=nil end,
        reset_if_unselected=function()
            if not lease then blocked=nil end
        end,
    }
end
return M
