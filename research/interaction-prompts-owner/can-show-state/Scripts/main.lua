-- SPDX-License-Identifier: MPL-2.0
-- Research only. Current fields at CanShow post; no game calls or UI writes.
local ID, PREFIX = "can-show-state", "IIP_CANSHOW"
local CLASS = "/Game/MainContent/Template/UMG/TipHUD.TipHUD_C"
local PATH = CLASS .. ":CanShow"
local phase, lines, calls = "armed", 0, 0
local started, deadline, sampled = nil, nil, nil
local seen, last, identities = {}, {}, 0 -- Strings only, never UObject/parameter wrappers.

local function quote(s)
    return '"' .. s:gsub('[%c\\"]', function(c)
        if c == '"' then return '\\"' end
        if c == '\\' then return '\\\\' end
        return string.format('\\x%02x', string.byte(c))
    end) .. '"'
end
local function write(event, fields)
    lines = lines + 1
    print(PREFIX .. " event=" .. event .. " id=" .. ID .. " " .. (fields or "") .. "\n")
end
local function finish(event, reason)
    if phase == "stopped" then return end
    phase = "stopped"
    if lines < 600 then
        write(event, "reason=" .. quote(tostring(reason):sub(1, 240)) .. " calls=" .. calls)
    end
end
local function emit(event, fields)
    if phase == "stopped" then return false end
    if lines >= 599 then finish("STOP", "line-limit"); return false end
    write(event, fields)
    return true
end
local function guarded(fn)
    local ok, err = pcall(fn)
    if not ok then finish("FAILED", err) end
    -- Intentionally no result: never return pcall's boolean as a hook override.
end
local function valid(o) return o ~= nil and o:IsValid() end
local function finite(n) return type(n) == "number" and n == n and math.abs(n) < math.huge end
local function class_path(o)
    local c = o:GetClass()
    assert(valid(c), "missing class")
    return c:GetFullName():match(" ([^ ]+)$")
end

local function observe(context, ...)
    if phase ~= "active" then return end
    local extra = select("#", ...)
    guarded(function()
        local now = os.time()
        assert(now >= started, "wall-clock moved backwards")
        if now >= deadline then finish("TIMEOUT", "ten-minute-limit"); return end
        calls = calls + 1
        assert(extra == 0, "unexpected CanShow input arguments")
        if calls == 1 and not emit("FIRST_CALL", "result=not-exposed") then return end
        if sampled == now then return end -- At most one field snapshot per wall-clock second globally.
        sampled = now
        local widget = context:get()
        assert(valid(widget), "invalid callback context")
        assert(class_path(widget) == CLASS, "unexpected widget class")
        local name, address = widget:GetFullName(), tostring(widget:GetAddress())
        local key = name .. "@" .. address
        if not seen[key] then
            assert(identities < 8, "widget identity limit")
            seen[key], identities = true, identities + 1
        end
        local visibility, opacity, enabled = widget.Visibility, widget.RenderOpacity, widget.bIsEnabled
        assert(math.type(visibility) == "integer", "visibility is not an enum integer")
        assert(finite(opacity) and type(enabled) == "boolean", "unsupported widget state fields")
        local text, text_state, text_address = "", "unavailable", "none"
        local block = widget.TextBlock_89
        if valid(block) then
            assert(class_path(block) == "/Script/UMG.TextBlock", "unexpected text block class")
            text = block.Text:ToString()
            assert(type(text) == "string" and #text <= 1024, "unsupported text value/length")
            text_state, text_address = "available", tostring(block:GetAddress())
        end
        local state = "text_state=" .. text_state .. " text=" .. quote(text)
            .. " text_address=" .. text_address .. " visibility_raw=" .. visibility
            .. " opacity=" .. tostring(opacity) .. " enabled=" .. tostring(enabled)
        if last[key] ~= state then
            last[key] = state
            emit("SNAPSHOT", "wall=" .. now .. " widget=" .. quote(name) .. " address=" .. address .. " " .. state)
        end
        -- No engine object, FText or parameter wrapper escapes this synchronous callback.
    end)
    -- Blueprint CanShow's original bool is not exposed and must remain untouched.
end

local function control()
    if phase == "active" then finish("STOP", "user"); return end
    if phase ~= "armed" then return end
    guarded(function()
        local fn = StaticFindObject(PATH)
        if not valid(fn) then finish("FAILED", "CanShow NOT_LOADED; no retry or force-load"); return end
        assert(fn:type() == "UFunction" and fn:GetFullName() == "Function " .. PATH, "unexpected function identity")
        local flags = fn:GetFunctionFlags()
        assert(math.type(flags) == "integer" and (flags & 0x400) == 0, "CanShow must be non-native")
        started, sampled = os.time(), nil
        deadline, phase = started + 600, "active"
        local pre, post = RegisterHook(PATH, observe) -- Blueprint post only; one callback, always nil.
        assert(math.type(pre) == "integer" and pre > 0 and pre == post, "unexpected script hook IDs")
        emit("REGISTERED", "flags=" .. flags .. " deadline=" .. deadline)
        -- Control-only expiry; this scheduled callback does not read any host object.
        ExecuteInGameThreadWithDelay(600000, function()
            if phase == "active" then finish("TIMEOUT", "ten-minute-limit") end
        end)
    end)
end

emit("START", "phase=armed key=Ctrl+Alt+F10 sampling=CanShow-post-only")
guarded(function()
    for _, name in ipairs({"StaticFindObject", "RegisterHook", "RegisterKeyBind", "IsKeyBindRegistered",
        "ExecuteInGameThread", "ExecuteInGameThreadWithDelay"}) do
        assert(type(_G[name]) == "function", "missing API: " .. name)
    end
    assert(type(os.time) == "function" and EngineTickAvailable == true, "engine-tick dispatch unavailable")
    assert(type(EGameThreadMethod) == "table" and type(EGameThreadMethod.EngineTick) == "number", "missing dispatch enum")
    assert(type(Key) == "table" and type(ModifierKey) == "table", "missing key enums")
    local modifiers = {ModifierKey.CONTROL, ModifierKey.ALT}
    assert(type(Key.F10) == "number" and type(modifiers[1]) == "number" and type(modifiers[2]) == "number", "missing chord codes")
    assert(not IsKeyBindRegistered(Key.F10, modifiers), "diagnostic chord already registered")
    RegisterKeyBind(Key.F10, modifiers, function()
        if phase == "stopped" then return end
        -- Key callback only schedules control; all metadata/UI access stays on the game thread.
        local ok, err = pcall(ExecuteInGameThread, control, EGameThreadMethod.EngineTick)
        if not ok then finish("FAILED", err) end
    end)
end)
