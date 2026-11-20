-- SPDX-License-Identifier: MPL-2.0
local LEVEL = "/Game/MainContent/Maps/sublevel_plot/1-1/1-1_plot_slumB1_main1.1-1_plot_slumB1_main1:PersistentLevel."
local NPC = "/Game/MainContent/Template/BaseBlueprint/NPCInteract_Bp.NPCInteract_Bp_C"
local QUINTUS = "/Game/MainContent/Act/Character_BP/quintus_BP.quintus_BP_C"
local COMPONENT = "/Script/Genesis.ExtendedWidgetComponent"
local TIP = "/Game/MainContent/Template/UMG/TipHUD.TipHUD_C"
local DEFAULT_SCALE, DEFAULT_LIFT = 0.400, 36
local DEFAULT_RGB = 0.35
local scale, lift = DEFAULT_SCALE, DEFAULT_LIFT
local rgb = DEFAULT_RGB
local selected, stopped, editing
local resources, probe, decorated
local FIELD_LEVEL = "/Game/MainContent/Maps/sublevel_plot/0-1/0-1_plot_outerRimA_interact1.0-1_plot_outerRimA_interact1:PersistentLevel."
local PLACED = {
    [FIELD_LEVEL.."0-1_lootbox_01_mat_ST001"]="Open",
    [FIELD_LEVEL.."0-1_item_loot_bag_03_AP1_3"]="Take",
    [FIELD_LEVEL.."0-1_sosletter3_2"]="Check",
}

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
    if not is(component, COMPONENT) or not path(component):match("%.ExtendedWidget$") then return end
    local actor = component:GetOuter()
    if not valid(actor) or path(component) ~= path(actor)..".ExtendedWidget" then return end
    local action = PLACED[path(actor)]
    if action then
        log("PLACED_OBJECT_NOTIFY", ("action=%s creation_method=%s space=%s widget_class=%s"):format(
            action, tostring(component.CreationMethod), tostring(component.Space), tostring(valid(component.WidgetClass))))
        return
    end
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
    if selected then
        -- A fresh instance may take over only after the previous component and tree are gone.
        if valid(StaticFindObject(selected.component))
            or (selected.widget and valid(StaticFindObject(selected.widget))) then return end
        resources.cycle_cleaned()
        decorated = false
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
    -- Keep the original strict identity contract; identify the first failed predicate.
    assert(is(component, COMPONENT), "identity:component_class")
    assert(path(component) == selected.component, "identity:component_path")
    assert(component:GetAddress() == selected.component_address, "identity:component_address")
    assert(same(component:GetOwner(), actor), "identity:component_actor")
    assert(is(owner, QUINTUS), "identity:owner_class")
    assert(path(owner) == selected.owner, "identity:owner_path")
    assert(owner:GetAddress() == selected.owner_address, "identity:owner_address")
    local widget, rt = component:GetUserWidgetObject(), component:GetRenderTarget()
    if not event then return component, widget end
    local draw, current = component:GetDrawSize(), component:GetCurrentDrawSize()
    log(event, ("space=%s creation_method=%s collision=%s widget=%q render_target=%s added_to_screen=%s visible=%s decorated=%s draw=%sx%s current=%sx%s desired_size=%s rt=%s filter=%s"):format(
        tostring(component.Space), tostring(component.CreationMethod), tostring(component:GetCollisionEnabled()),
        is(widget, TIP) and path(widget) or "", tostring(valid(rt)), tostring(component.bAddedToScreen),
        tostring(component.bVisible), tostring(decorated == true),
        draw.X, draw.Y, current.X, current.Y, tostring(component.bDrawAtDesiredSize),
        valid(rt) and (rt.SizeX.."x"..rt.SizeY) or "absent", valid(rt) and tostring(rt.Filter) or "absent"))
    return component, widget
end

local function place_world(component, factor, height)
    local previous = component.RelativeScale3D
    local baseline = component:K2_GetComponentLocation()
    local previous_scale = {X=previous.X,Y=previous.Y,Z=previous.Z}
    local original_position = {X=baseline.X,Y=baseline.Y,Z=baseline.Z}
    local original_scale = selected.original_scale or previous_scale
    assert(original_scale.X > 0 and original_scale.X < 100
        and original_scale.Y > 0 and original_scale.Y < 100
        and original_scale.Z > 0 and original_scale.Z < 100,
        "unexpected baseline scale")
    local delta = height - (selected.applied_lift or 0)
    local ok, reason = pcall(function()
        component:SetRelativeScale3D({X=original_scale.X*factor,Y=original_scale.Y*factor,Z=original_scale.Z*factor})
        if delta ~= 0 then component:K2_AddWorldOffset({X=0,Y=0,Z=delta},false,{},true) end
        local shifted = component:K2_GetComponentLocation()
        local actual = component.RelativeScale3D
        assert(math.abs(shifted.Z - original_position.Z - delta) < 0.1
            and math.abs(actual.X - original_scale.X*factor) < 0.001
            and math.abs(actual.Y - original_scale.Y*factor) < 0.001
            and math.abs(actual.Z - original_scale.Z*factor) < 0.001, "placement readback differs")
    end)
    if not ok then
        component:SetRelativeScale3D(previous_scale)
        component:K2_SetWorldLocation(original_position,false,{},true)
        error(reason)
    end
    selected.original_scale, selected.applied_lift = original_scale, height
    log("PLACED", ("scale_factor=%.3f lift=%.1f world_z_delta=%.1f"):format(factor,height,delta))
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
    local actor = context:get()
    if not valid(actor) then return end
    local action = PLACED[path(actor)]
    if action then
        local component = actor.ExtendedWidget
        if is(component,COMPONENT) and same(component:GetOwner(),actor) then
            log("PLACED_OBJECT_BEGIN", ("action=%s space=%s"):format(action,tostring(component.Space)))
        end
        return
    end
    if not selected or selected.begun then return end
    if valid(actor) and actor:GetAddress() == selected.actor_address and path(actor) == selected.actor then
        selected.begun = true
        local component, widget = inspect("BEGIN", actor)
        assert(component.Space == 0 and component:GetCollisionEnabled() == 0 and is(widget,TIP),
            "native World TipHUD unavailable")
        selected.widget = path(widget)
        place_world(component, scale, lift)
        local previous_interval = probe.continuous_tick(component)
        log("TICK_CONTINUOUS", ("before=%.3f after=%.3f"):format(
            previous_interval, component:GetComponentTickInterval()))
        local ok, reason = pcall(add_decoration, widget)
        if not ok then log("DECORATION_FAILED", ("reason=%q"):format(tostring(reason):sub(1,180))) end
        if rgb ~= 1 then
            local applied, result = pcall(probe.tint,component,nil,rgb)
            if applied then selected.tint = result else log("TINT_REJECTED",tostring(result)) end
        end
    end
end

local function resolve_actor()
    if not selected or not selected.original_scale then return end
    local actor = StaticFindObject(selected.actor)
    if is(actor, NPC) and actor:GetAddress() == selected.actor_address then return actor end
end

local function report(event)
    log(event, ("scale=%.3f lift=%.1f resolution=Native rgb=%.2f"):format(scale,lift,rgb))
    local actor = resolve_actor()
    if actor then inspect("SAMPLE", actor) end
end

local function resolve_world()
    local actor = resolve_actor()
    if not actor then return end
    local component, widget = inspect(nil,actor)
    if component.Space == 0 and component:GetCollisionEnabled() == 0
        and is(widget,TIP) and path(widget) == selected.widget then return component,widget end
end

local function adjust_rgb(value)
    value = math.max(0.25,math.min(1,value))
    if math.abs(rgb-value) < 0.001 then return end
    local component = assert(resolve_world(),"World TipHUD unavailable")
    selected.tint = probe.tint(component,selected.tint,value)
    rgb = value
    report("TINT")
end

local function adjust(factor, height)
    factor, height = math.min(1,math.max(0.25,factor)), math.min(100,math.max(0,height))
    local actor = resolve_actor()
    if actor then
        local component, widget = inspect("BEFORE_ADJUST", actor)
        assert(component.Space == 0 and component:GetCollisionEnabled() == 0
            and is(widget,TIP) and path(widget) == selected.widget, "World TipHUD changed")
        place_world(component,factor,height)
    end
    scale, lift = factor, height
    report("VALUES")
end

local function audit_game_keys(bindings)
    local reserved = {}
    for _, entry in ipairs(bindings) do reserved[entry[2]] = true end
    local name = "/Script/Genesis.GameGlobal:GetKeyByVirtualKey"
    local fn = StaticFindObject(name)
    local cdo = StaticFindObject("/Script/Genesis.Default__GameGlobal")
    assert(valid(fn) and fn:type() == "UFunction" and fn:GetFullName() == "Function "..name
        and is(cdo,"/Script/Genesis.GameGlobal"), "game key audit unavailable")
    for _, id in ipairs(require("IIPQuintusKeyboardBindings")) do
        local key = fn(cdo,FName(id))
        assert(type(key) == "table" and key.KeyName ~= nil,"game key audit result unavailable")
        assert(not reserved[key.KeyName:ToString()],"game key conflict: "..id)
    end
end

local function register_editor()
    local function reject_preset() log("PRESET_UNAVAILABLE", "resolution=Native layout_scale_unverified=true") end
    local bindings
    bindings = {
        {"F5","F5",function()
            audit_game_keys(bindings)
            editing = true
            report("EDITOR_OPEN")
        end,true},
        {"F8","F8",function() editing = false; report("EDITOR_CLOSED") end},
        {"NUM_EIGHT","NumPadEight",function() adjust(scale,lift+2) end},
        {"NUM_TWO","NumPadTwo",function() adjust(scale,lift-2) end},
        {"ADD","Add",function() adjust(scale+0.025,lift) end},
        {"SUBTRACT","Subtract",function() adjust(scale-0.025,lift) end},
        {"NUM_SEVEN","NumPadSeven",reject_preset},
        {"NUM_NINE","NumPadNine",reject_preset},
        {"NUM_ONE","NumPadOne",function() probe.hold(resolve_world,log,false) end},
        {"NUM_THREE","NumPadThree",function() probe.hold(resolve_world,log,true) end},
        {"NUM_FOUR","NumPadFour",function() adjust_rgb(rgb-0.10) end},
        {"NUM_SIX","NumPadSix",function() adjust_rgb(rgb+0.10) end},
        {"NUM_FIVE","NumPadFive",function() report("VALUES") end},
        {"NUM_ZERO","NumPadZero",function() adjust_rgb(DEFAULT_RGB); adjust(DEFAULT_SCALE,DEFAULT_LIFT) end},
    }
    assert(EngineTickAvailable == true, "game thread unavailable")
    for _, entry in ipairs(bindings) do
        assert(type(Key[entry[1]]) == "number" and not IsKeyBindRegistered(Key[entry[1]]),
            "UE4SS key unavailable: "..entry[1])
    end
    for _, entry in ipairs(bindings) do
        RegisterKeyBind(Key[entry[1]],function()
            if stopped or (not editing and not entry[4]) then return end
            ExecuteInGameThread(function()
                if stopped or (not editing and not entry[4]) then return end
                local ok, reason = pcall(entry[3])
                if not ok then
                    editing = false
                    log("EDITOR_REJECTED", ("reason=%q"):format(tostring(reason):sub(1,180)))
                end
            end,EGameThreadMethod.EngineTick)
        end)
    end
    log("EDITOR_KEYS", "open=F5 close=F8 resolution=Native")
end

guarded(function()
    resources = require("IIPQuintusResources")
    probe = require("IIPQuintusProbe")
    resources.prepare()
    RegisterBeginPlayPostHook(function(context) guarded(on_begin, context) end)
    NotifyOnNewObject(COMPONENT, function(component)
        guarded(on_created, component)
        return stopped == true
    end)
    local ok, reason = pcall(register_editor)
    if not ok then log("EDITOR_UNAVAILABLE", ("reason=%q"):format(tostring(reason):sub(1,180))) end
    log("ARMED", "resolution=Native")
end)
