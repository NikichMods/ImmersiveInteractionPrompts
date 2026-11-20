-- SPDX-License-Identifier: MPL-2.0
local LEVEL = "/Game/MainContent/Maps/sublevel_plot/1-1/1-1_plot_slumB1_main1.1-1_plot_slumB1_main1:PersistentLevel."
local NPC = "/Game/MainContent/Template/BaseBlueprint/NPCInteract_Bp.NPCInteract_Bp_C"
local QUINTUS = "/Game/MainContent/Act/Character_BP/quintus_BP.quintus_BP_C"
local COMPONENT = "/Script/Genesis.ExtendedWidgetComponent"
local TIP = "/Game/MainContent/Template/UMG/TipHUD.TipHUD_C"
local selected, stopped, sampled

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
    log(event, ("space=%s creation_method=%s collision=%s widget=%q render_target=%s added_to_screen=%s"):format(
        tostring(component.Space), tostring(component.CreationMethod), tostring(component:GetCollisionEnabled()),
        is(widget, TIP) and path(widget) or "", tostring(valid(rt)), tostring(component.bAddedToScreen)))
end

local function on_begin(context)
    if not selected then return end
    local actor = context:get()
    if valid(actor) and actor:GetAddress() == selected.actor_address and path(actor) == selected.actor then
        inspect("BEGIN", actor)
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
