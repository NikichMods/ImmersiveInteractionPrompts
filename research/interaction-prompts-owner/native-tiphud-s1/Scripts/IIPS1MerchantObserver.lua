-- SPDX-License-Identifier: MPL-2.0
-- Standalone read-only research entry point, deployed in place of S1 main.lua.
local Layout = require("IIPS1Layout")
local NPC = "/Game/MainContent/Template/BaseBlueprint/NPCInteract_Bp.NPCInteract_Bp_C"
local TIP = "/Game/MainContent/Template/UMG/TipHUD.TipHUD_C"
local COMPONENT = "/Script/Genesis.ExtendedWidgetComponent"
local HOOK = TIP .. ":CanShow"
local LIMIT = 64
local actors, widgets, count, epoch = {}, {}, 0, 0
local registered, stopped, waiting = false, false, false

local function emit(event, details)
    print("IIP_S1_MERCHANT event=" .. event .. " map=" .. epoch .. " " .. (details or "") .. "\n")
end

local function valid(o) return o ~= nil and o:IsValid() end
local function path(o) return assert(o:GetFullName():match("^[^ ]+ (.+)$")) end
local function is(o, class) return valid(o) and path(o:GetClass()) == class end
local function same(a,b) return valid(a) and valid(b) and a:GetAddress() == b:GetAddress() end

local function tag(actor)
    local argument = actor.TipHUDArgument
    if is(argument, "/Script/Genesis.TipHUDArgumentComponent") and same(argument:GetOwner(), actor) then
        return argument.msgTag:ToString()
    end
    return "unavailable"
end

local function indexable(v) return type(v) == "table" or type(v) == "userdata" end
local function vector(v)
    if not indexable(v) then return "unavailable" end
    return "(" .. tostring(v.X) .. "," .. tostring(v.Y) .. ")"
end
local function anchors(v)
    if not indexable(v) then return "unavailable" end
    return vector(v.Minimum) .. ":" .. vector(v.Maximum)
end

local function sample(w)
    local stock = w.TextBlock_89
    if not is(stock, "/Script/UMG.TextBlock") then return "text_missing" end
    local tree, canvas = w.WidgetTree, stock:GetParent()
    if not is(tree, "/Script/UMG.WidgetTree") or not same(tree:GetOuter(), w)
        or not is(canvas, "/Script/UMG.CanvasPanel") or not same(canvas:GetOuter(), tree)
        or not same(stock:GetOuter(), tree) or not path(canvas):match("%.CanvasPanel_6$") then
        return "tree_unready"
    end
    local slot = stock.Slot
    if not is(slot, "/Script/UMG.CanvasPanelSlot") or not slot:GetAutoSize() then
        return "text_slot_unready"
    end
    local icon = StaticFindObject(path(tree) .. ".RetainerBox_0")
    if not is(icon, "/Script/UMG.RetainerBox") or not same(icon:GetParent(), canvas) then
        return "icon_unready"
    end
    local icon_slot = icon.Slot
    if not is(icon_slot, "/Script/UMG.CanvasPanelSlot") then return "icon_slot_unready" end

    local text = stock.Text:ToString()
    local has_text = type(text) == "string" and text ~= ""
    local function drawable(v) return v == 0 or v == 3 or v == 4 end
    local presented = has_text and drawable(w.Visibility) and w.RenderOpacity > 0
        and w.bIsEnabled == true and drawable(stock.Visibility) and stock.RenderOpacity > 0
    local input = {
        desired=stock:GetDesiredSize(), position=slot:GetPosition(),
        alignment=slot:GetAlignment(), anchors=slot:GetAnchors(), native_size=stock.Font.Size,
        icon_position=icon_slot:GetPosition(), icon_alignment=icon_slot:GetAlignment(),
        icon_anchors=icon_slot:GetAnchors(), icon_auto=icon_slot:GetAutoSize(), icon_size=icon_slot:GetSize()
    }
    local _, reason = Layout.plan(input, true)
    return reason or "valid", input, has_text, presented, stock.Visibility
end

local function report(event, rec, component, w, reason, input, has_text, presented, text_visibility)
    local details = "id=" .. rec.id .. " added=" .. tostring(component.bAddedToScreen)
        .. " visible=" .. tostring(component.bVisible) .. " root_visibility=" .. tostring(w.Visibility)
        .. " text_visibility=" .. tostring(text_visibility) .. " text_present=" .. tostring(has_text)
        .. " presentation_ready=" .. tostring(presented) .. " check=" .. reason
    if input then
        details = details .. " desired=" .. vector(input.desired) .. " text_pos=" .. vector(input.position)
            .. " text_align=" .. vector(input.alignment) .. " text_anchors=" .. anchors(input.anchors)
            .. " font=" .. tostring(input.native_size) .. " icon_pos=" .. vector(input.icon_position)
            .. " icon_align=" .. vector(input.icon_alignment) .. " icon_anchors=" .. anchors(input.icon_anchors)
            .. " icon_size=" .. vector(input.icon_size) .. " icon_auto=" .. tostring(input.icon_auto)
    end
    emit(event, details)
end

local function guarded(work, ...)
    if stopped then return end
    local ok, err = pcall(work, ...)
    if not ok then
        stopped = true
        emit("UNAVAILABLE", "reason=" .. string.format("%q", tostring(err):sub(1,180)))
    end
end

local function observe(context, ...)
    assert(select("#", ...) == 0, "unexpected CanShow parameters")
    local w = context:get()
    if not valid(w) then return end
    local rec = widgets[w:GetAddress()]
    if not rec or rec.done then return end
    local actor = StaticFindObject(rec.actor)
    local component = StaticFindObject(rec.component)
    if not is(actor, NPC) or actor:GetAddress() ~= rec.actor_address
        or not is(component, COMPONENT) or component:GetAddress() ~= rec.component_address
        or not same(actor.ExtendedWidget, component) or not same(component:GetOwner(), actor)
        or not is(w, TIP) or path(w) ~= rec.widget or not same(component:GetUserWidgetObject(), w) then
        rec.done = true
        emit("IDENTITY_LOST", "id=" .. rec.id)
        return
    end
    if tag(actor) ~= "Talk" then return end

    local reason, input, text, presented, visibility = sample(w)
    if not rec.first then
        rec.first = true
        report("CANSHOW_FIRST", rec, component, w, reason, input, text, presented, visibility)
    end
    if input and reason ~= "valid" and not rec.rejected then
        rec.rejected = true
        report("LAYOUT_FIRST_REJECT", rec, component, w, reason, input, text, presented, visibility)
    end
    if reason == "valid" and not rec.valid then
        rec.valid = true
        report("LAYOUT_FIRST_VALID", rec, component, w, reason, input, text, presented, visibility)
    end
    if reason == "valid" and presented then
        rec.done = true
        report("CANSHOW_ELIGIBLE", rec, component, w, reason, input, text, presented, visibility)
    end
end

local function register()
    if registered then return end
    local fn = StaticFindObject(HOOK)
    if not valid(fn) then
        if not waiting then emit("WAITING"); waiting = true end
        return
    end
    assert(fn:type() == "UFunction" and fn:GetFullName() == "Function " .. HOOK
        and (fn:GetFunctionFlags() & 0x400) == 0, "unexpected CanShow function")
    local a,b = RegisterHook(HOOK, function(...) guarded(observe, ...) end)
    assert(type(a) == "number" and a > 0 and a == b, "CanShow registration failed")
    registered = true
    emit("READY", "read_only=true")
end

local function begin(context)
    register()
    local actor = context:get()
    if not is(actor, NPC) then return end
    local key = path(actor) .. "@" .. tostring(actor:GetAddress())
    if actors[key] then return end
    if count == LIMIT then
        count = count + 1
        emit("LIMIT", "npc_per_map=" .. LIMIT)
    end
    if count > LIMIT then return end
    count = count + 1
    actors[key] = true
    local component = actor.ExtendedWidget
    if not is(component, COMPONENT) or not same(component:GetOwner(), actor) then
        emit("BEGIN_MISS", "id=" .. count .. " check=component actor=" .. string.format("%q", path(actor)))
        return
    end
    local w = component:GetUserWidgetObject()
    if not is(w, TIP) then
        emit("BEGIN_MISS", "id=" .. count .. " check=widget actor=" .. string.format("%q", path(actor)))
        return
    end
    local rec = {id=count, actor=path(actor), actor_address=actor:GetAddress(), component=path(component),
                 component_address=component:GetAddress(), widget=path(w)}
    if widgets[w:GetAddress()] then
        widgets[w:GetAddress()].done = true
        emit("IDENTITY_AMBIGUOUS", "id=" .. rec.id)
        return
    end
    widgets[w:GetAddress()] = rec
    emit("BEGIN_MATCH", "id=" .. rec.id .. " tag=" .. string.format("%q", tag(actor))
        .. " actor=" .. string.format("%q", rec.actor) .. " widget=" .. string.format("%q", rec.widget))
    report("BEGIN_SAMPLE", rec, component, w, sample(w))
end

guarded(function()
    RegisterLoadMapPreHook(function()
        if stopped then return end
        actors, widgets, count, epoch = {}, {}, 0, epoch + 1
    end)
    RegisterBeginPlayPostHook(function(context) guarded(begin, context) end)
    register()
    emit("ARMED", "read_only=true")
end)
