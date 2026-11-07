-- SPDX-License-Identifier: MPL-2.0
-- Research-only stage A. Call frame/restore only from the selected World pump.
local M={}
local SETTER="/Script/UMG.UserWidget:SetColorAndOpacity"
local channels={"R","G","B","A"}

local function rgba(widget)
    local value=widget.ColorAndOpacity
    local copy={}
    for _,channel in ipairs(channels) do
        local n=value[channel]
        assert(type(n)=="number" and n==n and math.abs(n)<math.huge,"RGBA unavailable")
        copy[channel]=n
    end
    return copy
end

local function same_color(a,b)
    return a.R==b.R and a.G==b.G and a.B==b.B and a.A==b.A
end

local function unbound(widget)
    local delegate=widget.ColorAndOpacityDelegate
    return type(delegate)=="table" and delegate.Object~=nil
        and delegate.Object:IsValid()==false and delegate.Object:GetAddress()==0
        and delegate.FunctionName:ToString()=="None"
end

function M.new(source,alive,visible,find,now,emit)
    local pending,preflight,lease,locked
    local function event(name,reason)
        emit("TINT_"..name,"reason="..tostring(reason):sub(1,180))
    end
    local function exact(ref)
        local o=find(ref.path)
        if not alive(o) then return nil end
        assert(o:GetAddress()==ref.address and o:GetFullName():match("^[^ ]+ (.+)$")==ref.path
            and o:GetClass():GetFullName():match("^[^ ]+ (.+)$")==ref.class,"TipHUD lease identity mismatch")
        return o
    end
    local function resolve(record)
        local refs=record.refs
        local a,c,w=exact(refs.actor),exact(refs.component),exact(refs.widget)
        if not (a and c and w) then return nil end
        local function same(x,y)
            return alive(x) and x:GetAddress()==y:GetAddress()
        end
        assert(same(a.ExtendedWidget,c) and same(c:GetOwner(),a)
            and same(c:GetUserWidgetObject(),w) and same(c:GetWidget(),w)
            and same(c.Widget,w) and c:GetWidgetSpace()==1,"TipHUD lease ownership changed")
        return w
    end
    local function setter()
        local f=find(SETTER)
        assert(f and f:IsValid() and f:type()=="UFunction"
            and f:GetFullName()=="Function "..SETTER,"exact color setter unavailable")
        return f
    end
    local function restore(reason)
        pending,preflight=nil,nil
        if not lease then return end
        local saved=lease
        lease=nil
        local ok,result=pcall(function()
            local w=resolve(saved.record)
            if not w then return "OBJECT_UNAVAILABLE" end
            if not unbound(w) then return "WRITER_CHANGED" end
            local current=rgba(w)
            if same_color(current,saved.original) then return "ORIGINAL_PRESENT" end
            if not same_color(current,saved.zero) then return "WRITER_CHANGED" end
            local f=setter()
            local returned=pcall(f,w,saved.original)
            if not alive(w) then return "OBJECT_UNAVAILABLE" end
            if same_color(rgba(w),saved.original) then return "RESTORED" end
            error(returned and "restore readback differs" or "restore call failed")
        end)
        if ok and (result=="RESTORED" or result=="ORIGINAL_PRESENT") then
            event(result,reason)
        else
            locked=true
            event("STOPPED",result)
        end
    end
    return {
        request=function()
            if not locked then pending=(lease or preflight or pending) and "restore" or "start" end
        end,
        restore=restore,
        busy=function()return pending~=nil or preflight~=nil or lease~=nil end,
        ended=function(address)
            local record=(lease or preflight) and (lease or preflight).record
            if not address or (record and record.refs.actor.address==address) then
                local interrupted=lease~=nil
                -- EndPlay / map boundary is a signal only. Never reacquire or write here.
                lease,pending,preflight=nil,nil,nil
                if interrupted then
                    locked=true
                    event("STOPPED","lifecycle_boundary_restore_unconfirmed")
                end
            end
        end,
        frame=function(record,ready)
            local command=pending
            pending=nil
            if not lease and not command and not preflight then return end
            local ok,err=pcall(function()
                if lease then
                    local time=now()
                    if command=="restore" or not ready or record~=lease.record
                        or time>=lease.deadline or time<lease.started or lease.frames>=300 then
                        restore(command=="restore" and "manual" or "window_or_world_lost")
                        return
                    end
                    lease.frames=lease.frames+1
                    local w=assert(resolve(record),"TipHUD disappeared")
                    assert(unbound(w) and same_color(rgba(w),lease.zero),"possible competing writer")
                    local view=source.snapshot(record,alive,visible)
                    assert(view and view.shown and view.ready
                        and view.native_text==lease.text,"native readback changed")
                    return
                end
                if command=="restore" then preflight=nil; return end
                assert(ready and record and record.action=="Open","confirmed Open World required")
                local view=source.snapshot(record,alive,visible)
                assert(view and view.shown and view.ready,"native Open is unavailable")
                local w=assert(resolve(record),"exact TipHUD unavailable")
                local f=setter()
                assert(unbound(w),"color delegate absent or bound")
                local original=rgba(w)
                assert(original.A>0 and original.A<=1,"original alpha outside scope")
                if not preflight then
                    preflight={record=record,color=original,text=view.native_text}
                    return
                end
                assert(preflight.record==record and same_color(original,preflight.color)
                    and view.native_text==preflight.text,"preflight state changed")
                preflight=nil
                local zero={R=original.R,G=original.G,B=original.B,A=0}
                local started=now()
                lease={record=record,original=original,zero=zero,text=view.native_text,
                    started=started,deadline=started+5,frames=1}
                f(w,zero)
                if not lease then return end
                assert(alive(w) and same_color(rgba(w),zero),"suppression readback differs")
                event("APPLIED","Open; bounded game-thread window")
            end)
            if not ok then
                preflight=nil
                event("REFUSED",err)
                if lease then
                    restore("frame_error")
                    locked=true
                end
            end
        end,
    }
end

return M
