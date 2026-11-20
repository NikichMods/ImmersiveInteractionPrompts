-- SPDX-License-Identifier: MPL-2.0
local COMPONENT = "/Script/Genesis.ExtendedWidgetComponent"
local NPC = "/Game/MainContent/Template/BaseBlueprint/NPCInteract_Bp.NPCInteract_Bp_C"
local TIP = "/Game/MainContent/Template/UMG/TipHUD.TipHUD_C"
local ARGUMENT = "/Script/Genesis.TipHUDArgumentComponent"
local HOOK = TIP .. ":CanShow"
local LEVEL = "/Game/MainContent/Maps/sublevel_plot/1-1/1-1_plot_slumB1_main1.1-1_plot_slumB1_main1:PersistentLevel."
local LIMIT = 16
local created, ready = {}, {}
local construct_count, begin_count, ordinal = 0, 0, 0
local hooked, stopped = false, false

local function log(event, data)
    ordinal = ordinal + 1
    print(("IIP_NATIVE_WORLD event=%s seq=%d %s\n"):format(event, ordinal, data or ""))
    return ordinal
end

local function valid(object) return object ~= nil and object:IsValid() end
local function path(object) return assert(object:GetFullName():match("^[^ ]+ (.+)$")) end
local function is(object, class) return valid(object) and path(object:GetClass()) == class end
local function same(a, b) return valid(a) and valid(b) and a:GetAddress() == b:GetAddress() end

local function target(actor)
    return is(actor, NPC) and path(actor):sub(1, #LEVEL) == LEVEL
end

local function guarded(work, ...)
    if stopped then return end
    local ok, err = pcall(work, ...)
    if not ok then
        stopped = true
        log("UNAVAILABLE", ("reason=%q"):format(tostring(err):sub(1, 180)))
    end
end

local function sample(component)
    local class = component.WidgetClass
    return ("creation_method=%s space=%s widget_class=%q"):format(
        tostring(component.CreationMethod), tostring(component.Space), valid(class) and path(class) or "")
end

local function on_created(component)
    if not valid(component) or not component:GetFullName():match("%.ExtendedWidget$") then return end
    local actor = component:GetOuter()
    if not target(actor) then return end
    construct_count = construct_count + 1
    if construct_count > LIMIT then
        stopped = true
        log("LIMIT", "stage=construct limit=" .. LIMIT)
        return
    end
    local name, address = path(component), component:GetAddress()
    local seq = log("CONSTRUCT", ("component=%q %s"):format(name, sample(component)))
    local previous = created[address]
    created[address] = {name=name, seq=seq, ambiguous=previous ~= nil}
end

local function on_show(context, ...)
    assert(select("#", ...) == 0, "unexpected CanShow parameters")
    local widget = context:get()
    if not valid(widget) then return end
    local record = ready[widget:GetAddress()]
    if not record or path(widget) ~= record.widget then return end
    local actor = StaticFindObject(record.actor)
    local component = StaticFindObject(record.component)
    if not target(actor) or actor:GetAddress() ~= record.actor_address
        or not is(component, COMPONENT) or component:GetAddress() ~= record.component_address
        or not same(actor.ExtendedWidget, component) or not same(component:GetOwner(), actor)
        or not same(component:GetUserWidgetObject(), widget) then return end
    local argument = actor.TipHUDArgument
    if not is(argument, ARGUMENT) or not same(argument:GetOwner(), actor)
        or argument.msgTag:ToString() ~= "Talk" then return end

    local latest = created[record.component_address]
    local latest_seq = latest and latest.name == record.component and tostring(latest.seq) or "missing"
    log("TALK_MATCH", ("begin_seq=%d construct_at_begin=%s latest_construct_seq=%s component=%q widget=%q %s"):format(
        record.seq, record.construct_seq, latest_seq, record.component, record.widget, sample(component)))
    stopped = true
end

local function on_begin(context)
    local actor = context:get()
    if not target(actor) then return end
    local component = actor.ExtendedWidget
    if not is(component, COMPONENT) or not same(component:GetOwner(), actor) then return end
    local widget = component:GetUserWidgetObject()
    if not is(widget, TIP) then return end

    begin_count = begin_count + 1
    if begin_count > LIMIT then
        stopped = true
        log("LIMIT", "stage=begin limit=" .. LIMIT)
        return
    end

    if not hooked then
        local fn = StaticFindObject(HOOK)
        assert(valid(fn) and fn:type() == "UFunction" and fn:GetFullName() == "Function " .. HOOK
            and (fn:GetFunctionFlags() & 0x400) == 0, "unexpected CanShow function")
        local pre, post = RegisterHook(HOOK, function(...) guarded(on_show, ...) end)
        assert(type(pre) == "number" and pre > 0 and pre == post, "CanShow registration failed")
        hooked = true
    end

    local widget_address = widget:GetAddress()
    if ready[widget_address] then
        stopped = true
        log("AMBIGUOUS", "repeated widget address")
        return
    end
    local name, address = path(component), component:GetAddress()
    local early = created[address]
    local construct_seq = "missing"
    if early and early.name == name then
        construct_seq = early.ambiguous and "ambiguous" or tostring(early.seq)
    end
    local seq = log("BEGIN", ("construct_seq=%s component=%q widget=%q %s"):format(
        construct_seq, name, path(widget), sample(component)))
    ready[widget_address] = {seq=seq, construct_seq=construct_seq, component=name,
        component_address=address, actor=path(actor), actor_address=actor:GetAddress(), widget=path(widget)}
end

guarded(function()
    NotifyOnNewObject(COMPONENT, function(component)
        guarded(on_created, component)
        return stopped
    end)
    RegisterBeginPlayPostHook(function(context) guarded(on_begin, context) end)
    log("ARMED", "read_only=true")
end)
