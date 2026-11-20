-- SPDX-License-Identifier: MPL-2.0
local M = {}
local active
local MID = "/Script/Engine.MaterialInstanceDynamic"

local function valid(o) return o ~= nil and o:IsValid() end
local function is(o, class)
    return valid(o) and o:GetClass():GetFullName() == "Class " .. class
end

local function color(value)
    return {R=value.R,G=value.G,B=value.B,A=value.A}
end

local function equal(a,b)
    return math.abs(a.R-b.R) < 0.001 and math.abs(a.G-b.G) < 0.001
        and math.abs(a.B-b.B) < 0.001 and math.abs(a.A-b.A) < 0.001
end

function M.tint(component, baseline, factor)
    local material = component:GetMaterialInstance()
    assert(is(material,MID),"World MID unavailable")
    local previous = color(component.TintColorAndOpacity)
    assert(equal(previous,material:K2_GetVectorParameterValue(FName("TintColorAndOpacity"))),
        "component tint differs from World MID")
    baseline = baseline or previous
    local next_color = {R=baseline.R*factor,G=baseline.G*factor,B=baseline.B*factor,A=baseline.A}
    local ok, reason = pcall(function()
        component:SetTintColorAndOpacity(next_color)
        assert(equal(next_color,component.TintColorAndOpacity)
            and equal(next_color,material:K2_GetVectorParameterValue(FName("TintColorAndOpacity"))),
            "World tint readback differs")
    end)
    if not ok then
        component:SetTintColorAndOpacity(previous)
        error(reason)
    end
    return baseline
end

-- Preserve the host timer and its MID: only remove the proven component tick limit.
function M.continuous_tick(component)
    local previous = component:GetComponentTickInterval()
    assert(type(previous) == "number" and previous >= 0, "component tick interval unavailable")
    if previous > 0 then component:SetComponentTickIntervalAndCooldown(0) end
    assert(component:GetComponentTickInterval() == 0, "continuous component tick not applied")
    return previous
end

local function static(class, name)
    local path = class .. ":" .. name
    local fn = StaticFindObject(path)
    local cdo_path = class:gsub("%.([^%.]+)$",".Default__%1")
    local cdo = StaticFindObject(cdo_path)
    assert(valid(fn) and fn:type() == "UFunction" and fn:GetFullName() == "Function "..path
        and is(cdo,class), "reflected getter unavailable: "..name)
    return function(...) return fn(cdo,...) end
end

function M.hold(resolve, log, trial)
    assert(not active,"hold capture already running")
    local component, widget = resolve()
    assert(valid(component) and valid(widget) and component.bVisible and widget.CanHoldPress,
        "visible hold TipHUD required")
    local clock = static("/Script/Engine.GameplayStatics","GetRealTimeSeconds")
    local timer = static("/Script/Genesis.GameGlobal","GetToDoInteractActionPressTimer")
    local retainer = StaticFindObject(widget.WidgetTree:GetFullName():match("^[^ ]+ (.+)$")..".RetainerBox_0")
    assert(is(retainer,"/Script/UMG.RetainerBox"),"native RetainerBox unavailable")
    local material = retainer:GetEffectMaterial()
    assert(is(material,MID),"hold MID unavailable")
    local component_id, widget_id = component:GetAddress(), widget:GetAddress()
    local retainer_id, material_id = retainer:GetAddress(), material:GetAddress()
    local redraw, manual = component:GetRedrawTime(), component:GetManuallyRedraw()
    local interval = component:GetComponentTickInterval()
    local started, parameter = clock(component), FName("t")
    local mode = trial and "native_fast" or "observe"
    local n, last_rate, last_t = 0
    local changed_redraw, changed_manual, changed_interval
    active = true
    local function matches(c,w)
        return valid(c) and valid(w) and c:GetAddress() == component_id and w:GetAddress() == widget_id
    end
    local function finish(reason)
        active = nil
        local restored, result = pcall(function()
            if not (changed_redraw or changed_manual or changed_interval) then return "unneeded" end
            local c,w = resolve()
            if not matches(c,w) then return "identity_unavailable" end
            if changed_redraw and c:GetRedrawTime() == 0 then c:SetRedrawTime(redraw) end
            if changed_manual and c:GetManuallyRedraw() == false then c:SetManuallyRedraw(manual) end
            if changed_interval and c:GetComponentTickInterval() == 0 then c:SetComponentTickInterval(interval) end
            return "complete"
        end)
        log("HOLD_END", ("mode=%s samples=%d reason=%q restore=%s"):format(mode,n,reason,restored and result or "error"))
        if not restored then log("HOLD_RESTORE_FAILED", tostring(result)) end
    end
    local function sample()
        local ok, err = pcall(function()
            local c,w = resolve()
            if not matches(c,w) then finish("identity_changed"); return end
            local elapsed = clock(c)-started
            if n >= 180 or elapsed >= 3.5 then finish("window_complete"); return end
            if not c.bVisible then finish("hidden"); return end
            local box = StaticFindObject(w.WidgetTree:GetFullName():match("^[^ ]+ (.+)$")..".RetainerBox_0")
            assert(is(box,"/Script/UMG.RetainerBox") and box:GetAddress() == retainer_id,"hold RetainerBox changed")
            local mid = box:GetEffectMaterial()
            assert(is(mid,MID) and mid:GetAddress() == material_id,"hold MID changed")
            local out = {}
            local time = timer(out)
            local rate, t = out.outTimerRate, mid:K2_GetScalarParameterValue(parameter)
            assert(type(rate) == "number" and type(t) == "number", "hold readback unavailable")
            n = n+1
            if rate ~= last_rate or t ~= last_t or n%20 == 0 then
                log("HOLD_SAMPLE", ("mode=%s n=%d ms=%.0f timer=%s rate=%.4f t=%.4f"):format(mode,n,elapsed*1000,tostring(time),rate,t))
                last_rate,last_t = rate,t
            end
            ExecuteInGameThreadWithDelay(16,sample)
        end)
        if not ok then finish(tostring(err):sub(1,160)) end
    end
    local ok, err = pcall(function()
        if trial then
            if redraw > 0 then changed_redraw=true; component:SetRedrawTime(0) end
            if manual then changed_manual=true; component:SetManuallyRedraw(false) end
            if interval > 0 then changed_interval=true; component:SetComponentTickInterval(0) end
        end
        log("HOLD_BEGIN", ("mode=%s redraw=%.4f manual=%s interval=%.4f tick_mode=%s tick_enabled=%s offscreen=%s changed=%s"):format(
            mode,redraw,tostring(manual),interval,tostring(component.TickMode),tostring(component:IsComponentTickEnabled()),
            tostring(component:GetTickWhenOffscreen()),tostring(not not (changed_redraw or changed_manual or changed_interval))))
        sample()
    end)
    if not ok then finish(tostring(err):sub(1,160)) end
end

return M
