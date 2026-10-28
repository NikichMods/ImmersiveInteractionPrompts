-- SPDX-License-Identifier: MPL-2.0
-- Research only: stock-font OPEN plus one resource-free UImage divider. Not installed/run.
local CLASS = "/Game/MainContent/Template/UMG/TipHUD.TipHUD_C"
local PATH = CLASS .. ":CanShow"
local phase, owner, panel, tree = "armed", nil, nil, nil
local owned = {} -- At most two path/address/class/role records; never retained engine wrappers.
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
    local pending = {}
    for i = #owned,1,-1 do
        local ref = owned[i]
        local ok, err = pcall(function()
            local object = resolve(ref)
            if object then
                local t = resolve(tree)
                assert(valid(t) and same(object:GetOuter(), t), "owned child outer changed")
                object:SetVisibility(1)
                local parent = object:GetParent()
                if valid(parent) then
                    assert(same(parent, resolve(panel)), "owned child reparented externally")
                    log("REMOVE_BEGIN", "role=" .. ref.role)
                    assert(parent:RemoveChild(object) == true, "RemoveChild failed")
                    log("REMOVED", "role=" .. ref.role)
                end
                assert(not valid(object:GetParent()), "child still attached")
            end
        end)
        if not ok then
            pending[#pending+1] = ref
            log("CLEANUP_ITEM_FAILED", "role=" .. ref.role .. " " .. tostring(err):sub(1,240))
        end
    end
    owned = pending -- Keep only failed identities for explicit retry; still try the other child.
    if #pending == 0 then log("CLEANED", "reason=" .. reason .. " own_children_remaining=0")
    else phase = "cleanup_failed"; log("CLEANUP_FAILED", "remaining=" .. #pending) end
end

local function create(class, t, name, role)
    assert(not valid(StaticFindObject(path(t) .. "." .. name)), "own name collision")
    log("CREATE_BEGIN", "role=" .. role)
    local object = StaticConstructObject(class,t,FName(name),EObjectFlags.RF_Transient)
    assert(valid(object), "construction returned invalid object")
    local ref = remember(object); ref.role = role; owned[#owned+1] = ref
    assert(same(object:GetOuter(),t), "unexpected constructed outer")
    log("CREATED", "role=" .. role)
    object:SetVisibility(1)
    return object
end
local function attach(c, object, role, x, y, width, height, align_y)
    log("ATTACH_BEGIN", "role=" .. role)
    local slot = c:AddChildToCanvas(object)
    assert(valid(slot) and cls(slot) == "/Script/UMG.CanvasPanelSlot", "attachment returned invalid slot")
    assert(same(object:GetParent(),c) and same(slot.Parent,c) and same(slot.Content,object), "attachment mismatch")
    slot:SetAutoSize(false)
    slot:SetAnchors({Minimum={X=0,Y=0.5},Maximum={X=0,Y=0.5}})
    slot:SetAlignment({X=0,Y=align_y})
    slot:SetPosition({X=x,Y=y})
    slot:SetSize({X=width,Y=height})
    log("SLOT_READY", "role=" .. role)
end
local function configure_line(line)
    local brush = line.Brush -- Native-initialized owned struct, not a zero-filled Lua brush.
    local has_resource, resource_name = valid(brush.ResourceObject), brush.ResourceName:ToString()
    log("BRUSH_DEFAULT", "draw_as=" .. tostring(brush.DrawAs) .. " resource_object=" .. tostring(has_resource)
        .. " resource_name=" .. resource_name:sub(1,80) .. " dynamic=" .. tostring(brush.bIsDynamicallyLoaded)
        .. " has_uobject=" .. tostring(brush.bHasUObject))
    assert(not has_resource and resource_name == "None",
           "Image brush has unexpected default resource")
    assert(brush.bIsDynamicallyLoaded == false and brush.bHasUObject == false,
           "Image brush default resource flags differ")
    log("BRUSH_BEGIN", "resource=none mode=Box margins=0")
    brush.DrawAs, brush.ImageType, brush.Tiling, brush.Mirroring = 1,0,0,0
    brush.ImageSize = {X=140,Y=2}
    brush.Margin = {Left=0,Top=0,Right=0,Bottom=0}
    brush.TintColor = {SpecifiedColor={R=1,G=1,B=1,A=1},ColorUseRule=0}
    line:SetBrush(brush) -- Complete typed copy; native setter performs the widget update.
    line:SetColorAndOpacity({R=1,G=1,B=1,A=1})
    local actual = line.Brush
    assert(actual.DrawAs == 1 and actual.ImageType == 0 and actual.Tiling == 0 and actual.Mirroring == 0,
           "brush enum readback mismatch")
    assert(actual.ImageSize.X == 140 and actual.ImageSize.Y == 2
        and actual.Margin.Left == 0 and actual.Margin.Top == 0
        and actual.Margin.Right == 0 and actual.Margin.Bottom == 0, "brush size/margin readback mismatch")
    assert(not valid(actual.ResourceObject) and actual.ResourceName:ToString() == "None"
        and actual.TintColor.ColorUseRule == 0 and actual.TintColor.SpecifiedColor.A == 1
        and actual.TintColor.SpecifiedColor.R == 1 and actual.TintColor.SpecifiedColor.G == 1
        and actual.TintColor.SpecifiedColor.B == 1,
        "brush resource/tint readback mismatch")
    local color = line.ColorAndOpacity
    assert(color.R == 1 and color.G == 1 and color.B == 1 and color.A == 1, "Image color readback mismatch")
    log("BRUSH_READY", "draw_as=Box resource=none size=140x2 rgba=1,1,1,1")
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
        assert(position.X == 38 and position.Y == 0 and alignment.X == 0 and alignment.Y == 0.5,
               "original layout differs from measured Open baseline")
        assert(anchors.Minimum.X == 0 and anchors.Maximum.X == 0
               and anchors.Minimum.Y == 0.5 and anchors.Maximum.Y == 0.5, "unexpected anchors")
        local name = "IIP_UIChild_" .. tostring(os.time())
        local text_class = StaticFindObject("/Script/UMG.TextBlock")
        assert(valid(text_class) and text_class:type() == "UClass", "TextBlock class NOT_LOADED")
        local image_class = StaticFindObject("/Script/UMG.Image")
        assert(valid(image_class) and image_class:type() == "UClass", "Image class NOT_LOADED")
        owner, panel, tree = remember(w), remember(c), remember(t)
        local label = create(text_class,t,name .. "_OPEN","label")
        assert(cls(label) == "/Script/UMG.TextBlock", "unexpected label class")
        label:SetFont(b.Font) -- Typed struct copy, used synchronously; original untouched.
        label:SetText(FText("OPEN"))
        label:SetJustification(0) -- Left; experimental fixed region above the localized line.
        attach(c,label,"label",position.X,position.Y-18,140,28,1)
        local line = create(image_class,t,name .. "_Divider","divider")
        assert(cls(line) == "/Script/UMG.Image", "unexpected divider class")
        configure_line(line)
        attach(c,line,"divider",position.X,position.Y-15,140,2,0.5)
        label:SetVisibility(3) -- Neither child can receive input; show only after pair configured.
        line:SetVisibility(3)
        phase = "attached"
        log("ATTACHED", "own_children=2 font=stock divider=Image-Box duration_max=30s")
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
if ok then log("ARMED", "key=Ctrl+Alt+F9 one_session=true divider=Image-Box")
else phase="stopped"; log("UNAVAILABLE", tostring(err):sub(1,240)) end
