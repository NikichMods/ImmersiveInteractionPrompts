-- SPDX-License-Identifier: MPL-2.0
-- Research only: one stock-font OPEN label. NOT installed or runtime accepted.
local CLASS = "/Game/MainContent/Template/UMG/TipHUD.TipHUD_C"
local PATH = CLASS .. ":CanShow"
local phase, owner, panel, tree, child = "armed", nil, nil, nil, nil
local deadline, busy = 0, false
local function log(event, detail)
    print("IIP_UI_CHILD event=" .. event .. " " .. (detail or "") .. "\n")
end
local function valid(o) return o ~= nil and o:IsValid() end
local function path(o) return assert(o:GetFullName():match("^[^ ]+ (.+)$")) end
local function cls(o) return path(o:GetClass()) end
local function same(a, b) return valid(a) and valid(b) and a:GetAddress() == b:GetAddress() end
local function remember(o)
    return {path=path(o), address=o:GetAddress(), class=cls(o)} -- Strings/numbers only.
end
local function resolve(ref)
    if not ref then return nil end
    local o = StaticFindObject(ref.path) -- Fresh exact lookup, never a stored raw UObject wrapper.
    if not valid(o) then return nil end
    assert(o:GetAddress() == ref.address and cls(o) == ref.class, "identity changed")
    return o
end
local function cleanup(reason)
    phase = "stopped" -- Hook inert before any nested engine calls.
    local ok, err = pcall(function()
        local label = resolve(child)
        if label then
            local t = resolve(tree)
            assert(valid(t) and same(label:GetOuter(), t), "owned child outer changed")
            label:SetVisibility(1) -- Collapse only our label before removing its slot.
            local parent = label:GetParent()
            if valid(parent) then
                assert(same(parent, resolve(panel)), "owned child reparented externally")
                log("REMOVE_BEGIN")
                assert(parent:RemoveChild(label) == true, "RemoveChild failed")
                log("REMOVED")
            end
            assert(not valid(label:GetParent()), "child still attached")
        end
        child = nil -- Detachment, not forced destruction or proof of immediate GC.
    end)
    if ok then log("CLEANED", "reason=" .. reason)
    else phase = "cleanup_failed"; log("CLEANUP_FAILED", tostring(err):sub(1,240)) end
end
local function guarded(fn)
    if busy then return end
    busy = true
    local ok, err = pcall(fn)
    if not ok then log("FAILED", tostring(err):sub(1,240)); cleanup("failure") end
    busy = false
    -- Never return pcall's bool to CanShow.
end
local function eligible(w, b)
    return w.Visibility == 0 and w.RenderOpacity > 0 and w.bIsEnabled == true
        and b.Visibility ~= 1 and b.Visibility ~= 2 and b.RenderOpacity > 0
        and b.Text:ToString() == "Открыть"
end
local function observe(context, ...)
    if phase ~= "waiting" and phase ~= "attached" then return end
    local extra = select("#", ...)
    guarded(function()
        assert(extra == 0, "unexpected CanShow inputs")
        if os.time() >= deadline then cleanup("timeout"); return end
        local w = context:get()
        assert(valid(w) and cls(w) == CLASS, "unexpected TipHUD context")
        if owner and w:GetAddress() ~= owner.address then return end
        local b = w.TextBlock_89
        assert(valid(b) and cls(b) == "/Script/UMG.TextBlock", "missing stock text")
        if not eligible(w,b) then
            if phase == "attached" then cleanup("target-state-changed") end
            return
        end
        if phase == "attached" then return end -- Exactly one allocation/attachment attempt.
        phase = "attaching"
        local c, t = b:GetParent(), w.WidgetTree
        assert(valid(c) and cls(c) == "/Script/UMG.CanvasPanel", "text parent is not CanvasPanel")
        assert(path(c):match("%.CanvasPanel_6$"), "unexpected canvas identity")
        assert(valid(t) and cls(t) == "/Script/UMG.WidgetTree" and same(c:GetOuter(),t), "unexpected WidgetTree")
        assert(same(t:GetOuter(),w), "tree belongs to another widget")
        assert(same(b:GetOuter(),t) and c:GetChildrenCount() == 3, "original tree differs from baseline")
        assert(b.Font.Size == 22, "font size differs from desktop baseline")
        local source_slot = b.Slot
        assert(valid(source_slot) and cls(source_slot) == "/Script/UMG.CanvasPanelSlot", "unexpected original slot")
        local position = source_slot:GetPosition()
        local anchors = source_slot:GetAnchors()
        local alignment = source_slot:GetAlignment()
        local function scalar(n)
            return type(n) == "number" and string.format("%.17g",n) or tostring(n)
        end
        log("LAYOUT_OBSERVED", "position_type=" .. type(position)
            .. " position_x=" .. scalar(position.X) .. " position_y=" .. scalar(position.Y)
            .. " alignment_type=" .. type(alignment)
            .. " alignment_x=" .. scalar(alignment.X) .. " alignment_y=" .. scalar(alignment.Y))
        assert(position.X == 88 and position.Y == 0 and alignment.X == 0 and alignment.Y == 0.5,
               "original layout differs from retained baseline")
        assert(anchors.Minimum.X == 0 and anchors.Maximum.X == 0
               and anchors.Minimum.Y == 0.5 and anchors.Maximum.Y == 0.5, "unexpected anchors")
        local name = "IIP_UIChild_OPEN_" .. tostring(os.time())
        assert(not valid(StaticFindObject(path(t) .. "." .. name)), "own child name collision")
        local text_class = StaticFindObject("/Script/UMG.TextBlock")
        assert(valid(text_class) and text_class:type() == "UClass", "TextBlock class NOT_LOADED")
        owner, panel, tree = remember(w), remember(c), remember(t)
        log("CREATE_BEGIN")
        local label = StaticConstructObject(text_class, t, FName(name), EObjectFlags.RF_Transient)
        assert(valid(label), "construction returned invalid object")
        child = remember(label) -- Track before any later fallible call.
        log("CREATED")
        assert(child.class == "/Script/UMG.TextBlock" and same(label:GetOuter(),t), "unexpected constructed widget")
        label:SetVisibility(1) -- No default-visible flash during partial setup.
        label:SetFont(b.Font) -- Typed struct copy, used synchronously; original untouched.
        label:SetText(FText("OPEN"))
        label:SetJustification(0) -- Left; experimental fixed region above the localized line.
        log("ATTACH_BEGIN")
        local slot = c:AddChildToCanvas(label)
        assert(valid(slot) and cls(slot) == "/Script/UMG.CanvasPanelSlot", "attachment returned invalid slot")
        assert(same(label:GetParent(),c) and same(slot.Parent,c) and same(slot.Content,label), "attachment mismatch")
        log("SLOT_READY")
        slot:SetAutoSize(false)
        slot:SetAnchors({Minimum={X=0,Y=0.5},Maximum={X=0,Y=0.5}})
        slot:SetAlignment({X=0,Y=1})
        slot:SetPosition({X=88,Y=-18})
        slot:SetSize({X=140,Y=28})
        label:SetVisibility(3) -- HitTestInvisible: no new input target.
        phase = "attached"
        log("ATTACHED", "one_label=true font=stock divider=omitted duration_max=30s")
    end)
    -- No return override, no wrapper/Font/slot retained across callbacks.
end
local function control()
    if phase ~= "armed" then cleanup("user"); return end
    guarded(function()
        local fn = StaticFindObject(PATH)
        assert(valid(fn) and fn:type() == "UFunction" and fn:GetFullName() == "Function " .. PATH, "CanShow NOT_LOADED")
        assert((fn:GetFunctionFlags() & 0x400) == 0, "CanShow is native")
        phase, deadline = "waiting", os.time()+30
        local pre, post = RegisterHook(PATH, observe)
        assert(type(pre) == "number" and pre > 0 and pre == post, "unexpected hook IDs")
        ExecuteInGameThreadWithDelay(30000, function()
            if phase ~= "stopped" and phase ~= "cleanup_failed" then cleanup("timeout") end
        end)
        log("WAITING", "target=Open one_attempt=true")
    end)
end
local ok, err = pcall(function()
    for _, key in ipairs({"StaticFindObject","StaticConstructObject","RegisterHook","RegisterKeyBind",
                          "IsKeyBindRegistered","ExecuteInGameThread","ExecuteInGameThreadWithDelay"}) do
        assert(type(_G[key]) == "function", "missing API: " .. key)
    end
    assert(FName ~= nil and FText ~= nil and type(EObjectFlags) == "table"
           and type(EObjectFlags.RF_Transient) == "number", "missing constructors/flags")
    assert(EngineTickAvailable == true and type(EGameThreadMethod) == "table", "missing game-thread dispatch")
    local modifiers = {ModifierKey.CONTROL,ModifierKey.ALT}
    assert(not IsKeyBindRegistered(Key.F9,modifiers), "Ctrl+Alt+F9 collision")
    RegisterKeyBind(Key.F9,modifiers,function()
        local queued, problem = pcall(ExecuteInGameThread,control,EGameThreadMethod.EngineTick)
        if not queued then log("DISPATCH_FAILED", tostring(problem):sub(1,240)) end
    end)
end)
if ok then log("ARMED", "key=Ctrl+Alt+F9 one_session=true divider=omitted")
else phase="stopped"; log("UNAVAILABLE", tostring(err):sub(1,240)) end
