-- SPDX-License-Identifier: MPL-2.0
local LEVEL = "/Game/MainContent/Maps/sublevel_plot/1-1/1-1_plot_slumB1_main1.1-1_plot_slumB1_main1:PersistentLevel."
local NPC = "/Game/MainContent/Template/BaseBlueprint/NPCInteract_Bp.NPCInteract_Bp_C"
local QUINTUS = "/Game/MainContent/Act/Character_BP/quintus_BP.quintus_BP_C"
local COMPONENT = "/Script/Genesis.ExtendedWidgetComponent"
local TIP = "/Game/MainContent/Template/UMG/TipHUD.TipHUD_C"
local SCALE, LIFT = 0.65, 38
local selected, stopped, sampled
local resources, decorated

local function log(event, details)
    print("IIP_NATIVE_WORLD_QUINTUS event=" .. event .. " " .. (details or "") .. "\n")
end

local function valid(object) return object ~= nil and object:IsValid() end
local function path(object) return assert(object:GetFullName():match("^[^ ]+ (.+)$")) end
local function is(object, class) return valid(object) and path(object:GetClass()) == class end
local function same(a, b) return valid(a) and valid(b) and a:GetAddress() == b:GetAddress() end

local function in_level(actor, class, name)
    if not is(actor, class) then return false end
    local prefix, actor_path = LEVEL .. name, path(actor)
    return actor_path:sub(1, #prefix) == prefix and actor_path:sub(#prefix + 1):match("^%d+$") ~= nil
end

local function guarded(work, ...)
    if stopped then return end
    local ok, err = pcall(work, ...)
    if not ok then
        stopped = true
        log("UNAVAILABLE", ("reason=%q"):format(tostring(err):sub(1, 180)))
    end
end

local function on_created(component)
    if selected or not is(component, COMPONENT) or not path(component):match("%.ExtendedWidget$") then return end
    local actor = component:GetOuter()
    if not in_level(actor, NPC, "NPCInteract_Bp_C_") or path(component) ~= path(actor) .. ".ExtendedWidget" then return end
    local owner = actor:GetOwner()
    if not in_level(owner, QUINTUS, "quintus_BP_C_") then
        log("SKIP", "reason=quintus_owner_missing")
        return
    end
    if component.CreationMethod ~= 0 or component.Space ~= 1 or valid(component.WidgetClass) then
        log("SKIP", "reason=construction_state")
        return
    end

    selected = {actor=path(actor), actor_address=actor:GetAddress(), component=path(component),
        component_address=component:GetAddress(), owner=path(owner), owner_address=owner:GetAddress()}
    -- A World widget can have a collision body. Leave gameplay traces unaffected.
    component:SetCollisionEnabled(0)
    assert(component:GetCollisionEnabled() == 0, "NoCollision did not apply")
    component.Space = 0
    assert(component.Space == 0, "Space write failed")
    log("SET_WORLD", ("component=%q owner=%q collision=0"):format(selected.component, selected.owner))
end

local function inspect(event, actor)
    local component, owner = actor.ExtendedWidget, actor:GetOwner()
    assert(is(component, COMPONENT) and path(component) == selected.component
        and component:GetAddress() == selected.component_address and same(component:GetOwner(), actor)
        and is(owner, QUINTUS) and path(owner) == selected.owner and owner:GetAddress() == selected.owner_address,
        "component or Quintus identity changed")
    local widget, rt = component:GetUserWidgetObject(), component:GetRenderTarget()
    log(event, ("space=%s creation_method=%s collision=%s widget=%q render_target=%s added_to_screen=%s visible=%s decorated=%s"):format(
        tostring(component.Space), tostring(component.CreationMethod), tostring(component:GetCollisionEnabled()),
        is(widget, TIP) and path(widget) or "", tostring(valid(rt)), tostring(component.bAddedToScreen),
        tostring(component.bVisible), tostring(decorated == true)))
    return component, widget
end

local function place_world(component)
    local scale = component.RelativeScale3D
    local baseline = component:K2_GetComponentLocation()
    local original_scale = {X=scale.X,Y=scale.Y,Z=scale.Z}
    local original_position = {X=baseline.X,Y=baseline.Y,Z=baseline.Z}
    assert(original_scale.X > 0 and original_scale.Y > 0 and original_scale.Z > 0,
        "unexpected baseline scale")
    local ok, reason = pcall(function()
        component:SetRelativeScale3D({X=scale.X*SCALE,Y=scale.Y*SCALE,Z=scale.Z*SCALE})
        component:K2_AddWorldOffset({X=0,Y=0,Z=LIFT},false,{},true)
        local shifted = component:K2_GetComponentLocation()
        local actual = component.RelativeScale3D
        assert(math.abs(shifted.Z - original_position.Z - LIFT) < 0.1
            and math.abs(actual.X - original_scale.X*SCALE) < 0.001
            and math.abs(actual.Y - original_scale.Y*SCALE) < 0.001
            and math.abs(actual.Z - original_scale.Z*SCALE) < 0.001, "placement readback differs")
        log("PLACED", ("scale_factor=%.2f world_z_delta=%.1f"):format(SCALE, shifted.Z-original_position.Z))
    end)
    if not ok then
        component:SetRelativeScale3D(original_scale)
        component:K2_SetWorldLocation(original_position,false,{},true)
        error(reason)
    end
end

local function add_child(tree, canvas, owned, class, name, y, width, height)
    local widget_class = StaticFindObject(class)
    assert(valid(widget_class) and widget_class:type() == "UClass"
        and widget_class:GetFullName() == "Class " .. class, "UMG child class unavailable")
    assert(not valid(StaticFindObject(path(tree) .. "." .. name)), "owned child name already exists")
    local child = StaticConstructObject(widget_class,tree,FName(name),EObjectFlags.RF_Transient)
    assert(is(child, class) and same(child:GetOuter(),tree), "own child construction failed")
    owned[#owned+1] = child
    child:SetVisibility(1)
    local slot = canvas:AddChildToCanvas(child)
    assert(is(slot, "/Script/UMG.CanvasPanelSlot") and same(slot.Parent,canvas) and same(slot.Content,child),
        "owned slot unavailable")
    slot:SetAutoSize(false)
    slot:SetAnchors({Minimum={X=0,Y=0.5},Maximum={X=0,Y=0.5}})
    slot:SetAlignment({X=0.5,Y=0.5})
    slot:SetPosition({X=121.75,Y=y})
    slot:SetSize({X=width,Y=height})
    assert(same(child:GetParent(),canvas), "owned child parent differs")
    return child
end

local function add_decoration(widget)
    local stock, tree = widget.TextBlock_89, widget.WidgetTree
    assert(is(stock, "/Script/UMG.TextBlock") and is(tree, "/Script/UMG.WidgetTree")
        and same(tree:GetOuter(),widget) and same(stock:GetOuter(),tree), "native Talk tree unavailable")
    local canvas = stock:GetParent()
    assert(is(canvas, "/Script/UMG.CanvasPanel") and same(canvas:GetOuter(),tree)
        and path(canvas):match("%.CanvasPanel_6$"), "native Talk canvas unavailable")
    local icon = StaticFindObject(path(tree)..".RetainerBox_0")
    assert(is(icon, "/Script/UMG.RetainerBox") and same(icon:GetParent(),canvas), "native hint unavailable")
    local owned = {}
    local ok, reason = pcall(function()
        local label = add_child(tree,canvas,owned,"/Script/UMG.TextBlock","IIP_WQ_Aphes",-54.1484375,176,37)
        label:SetFont(stock.Font)
        assert(label.Font:GetStructAddress() ~= stock.Font:GetStructAddress(), "FontInfo aliased")
        resources.font(label)
        label:SetText(FText("ACTION"))
        label.Font.Size = 26
        label.Font.OutlineSettings.OutlineSize = 1
        label.Font.OutlineSettings.OutlineColor = {R=0,G=0,B=0,A=0.75}
        label:SetFont(label.Font)
        label:SetJustification(1)
        label:SetColorAndOpacity({SpecifiedColor={R=0.85,G=0.85,B=0.85,A=1},ColorUseRule=0})
        local divider = add_child(tree,canvas,owned,"/Script/UMG.Image","IIP_WQ_Divider",-27.19921875,142.375,17.796875)
        resources.ornament(divider,widget)
        divider:SetColorAndOpacity({R=0.75,G=0.75,B=0.75,A=1})
        label:SetVisibility(3)
        divider:SetVisibility(3)
    end)
    if not ok then
        for _, child in ipairs(owned) do
            child:SetVisibility(1)
            if same(child:GetParent(),canvas) then child:RemoveFromParent() end
        end
        error(reason)
    end
    decorated = true
    log("DECORATED", "native_canvas=CanvasPanel_6 own_children=2")
end

local function on_begin(context)
    if not selected or selected.begun then return end
    local actor = context:get()
    if valid(actor) and actor:GetAddress() == selected.actor_address and path(actor) == selected.actor then
        selected.begun = true
        local component, widget = inspect("BEGIN", actor)
        assert(component.Space == 0 and component:GetCollisionEnabled() == 0 and is(widget,TIP),
            "native World TipHUD unavailable")
        place_world(component)
        local ok, reason = pcall(add_decoration, widget)
        if not ok then log("DECORATION_FAILED", ("reason=%q"):format(tostring(reason):sub(1,180))) end
    end
end

local function sample()
    if sampled then return end
    sampled = true
    if not selected then log("SAMPLE", "result=no_target"); return end
    local actor = StaticFindObject(selected.actor)
    assert(is(actor, NPC) and actor:GetAddress() == selected.actor_address, "NPC identity changed")
    inspect("SAMPLE", actor)
end

guarded(function()
    resources = require("IIPQuintusResources")
    resources.prepare()
    local chord = {ModifierKey.CONTROL, ModifierKey.ALT}
    assert(EngineTickAvailable == true and not IsKeyBindRegistered(Key.F5, chord),
        "sample key or game thread unavailable")
    RegisterKeyBind(Key.F5, chord, function()
        guarded(ExecuteInGameThread, function() guarded(sample) end, EGameThreadMethod.EngineTick)
    end)
    RegisterBeginPlayPostHook(function(context) guarded(on_begin, context) end)
    NotifyOnNewObject(COMPONENT, function(component)
        guarded(on_created, component)
        return selected ~= nil or stopped == true
    end)
    log("ARMED", "sample=Ctrl+Alt+F5")
end)
