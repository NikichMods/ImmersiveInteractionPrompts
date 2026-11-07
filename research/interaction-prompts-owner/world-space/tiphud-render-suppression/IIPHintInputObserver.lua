-- SPDX-License-Identifier: MPL-2.0
-- Read-only snapshot of the already verified selected hint source.
local M={}
local SCALAR="/Script/Engine.MaterialInstanceDynamic:K2_GetScalarParameterValue"

local function number(n)
    assert(type(n)=="number" and n==n and math.abs(n)<math.huge,"non-finite hint field")
    return string.format("%.8g",n)
end

local function color(c)
    return table.concat({number(c.R),number(c.G),number(c.B),number(c.A)},",")
end

local function identity(o)
    assert(o and o:IsValid(),"hint resource missing")
    return string.format("%q",o:GetFullName().."@"..o:GetAddress())
end

function M.new(now,find,fname,emit)
    local requested,window
    local function stop(reason)
        if window then emit("END","reason="..reason) end
        requested,window=nil,nil
    end
    local function sample(s,w,action,ready)
        if not requested and not window then return end
        local time=now()
        if not window then
            local age=time-requested
            requested=nil
            if age<0 or age>1 or action~="Open" or not ready then
                emit("REFUSED","reason=stable_Open_required")
                return
            end
            window={start=time,ticks=0,owner=identity(w)}
            emit("BEGIN","owner="..window.owner)
        end
        local current=window
        current.ticks=current.ticks+1
        if time<current.start or time>=current.start+8 or current.ticks>480 then
            stop("budget")
            return
        end
        if (current.ticks-1)%6~=0 then return end
        assert(action=="Open" and identity(w)==current.owner,"owner changed")
        assert(s.mode=="retained_mid" and type(w.CanHoldPress)=="boolean","unsupported native hint")
        local b=s.brush
        local uv=b.UVRegion
        local region="unset"
        assert(uv.bIsValid==0 or uv.bIsValid==1,"UV validity unavailable")
        if uv.bIsValid==1 then
            region=table.concat({number(uv.Min.X),number(uv.Min.Y),number(uv.Max.X),number(uv.Max.Y)},",")
        end
        local f=find(SCALAR)
        assert(f and f:IsValid() and f:type()=="UFunction"
            and f:GetFullName()=="Function "..SCALAR,"scalar getter unavailable")
        local t=f(s.resource,fname("t"))
        number(t)
        local data="device="..number(s.device).." hold="..tostring(w.CanHoldPress)
            .." input="..identity(b.ResourceObject).." uv="..region
            .." size="..number(b.ImageSize.X)..","..number(b.ImageSize.Y)
            .." draw="..number(b.DrawAs).." tiling="..number(b.Tiling)
            .." mirror="..number(b.Mirroring).." image_type="..number(b.ImageType)
            .." margin="..table.concat({number(b.Margin.Left),number(b.Margin.Top),
                number(b.Margin.Right),number(b.Margin.Bottom)},",")
            .." tint_rule="..number(b.TintColor.ColorUseRule)
            .." tint="..color(b.TintColor.SpecifiedColor).." image_tint="..color(s.child.ColorAndOpacity)
            .." mid="..identity(s.resource).." rt="..identity(s.texture)
        local key=data.." t_bucket="..math.floor(t*20)
        if key~=current.key then
            current.key=key
            emit("SAMPLE",data.." t="..number(t).." tick="..current.ticks)
        end
    end
    return {
        request=function()
            if window or requested then stop("manual") else requested=now() end
        end,
        stop=stop,
        step=function(s,w,action,ready)
            local ok,problem=pcall(sample,s,w,action,ready)
            if not ok then
                requested,window=nil,nil
                emit("REFUSED","reason="..string.format("%q",tostring(problem):sub(1,150)))
            end
        end,
    }
end
return M
