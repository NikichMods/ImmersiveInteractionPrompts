-- SPDX-License-Identifier: MPL-2.0
-- RESEARCH ONLY. Run INSTEAD of the old native-world-quintus experiment.
-- No component/actor hooks or new renderers: write one specific SCS template once.
local GENERATED_CLASS = "/Game/MainContent/Template/BaseBlueprint/BaseGameEventObject_BP.BaseGameEventObject_BP_C"
local TEMPLATE = GENERATED_CLASS..":ExtendedWidget_GEN_VARIABLE"
local COMPONENT = "/Script/Genesis.ExtendedWidgetComponent"
local TIP = "/Game/MainContent/Template/UMG/TipHUD.TipHUD_C"
local LEVEL = "/Game/MainContent/Maps/sublevel_plot/0-1/0-1_plot_outerRimA_interact1.0-1_plot_outerRimA_interact1:PersistentLevel."
local OBJECTS = {
    [LEVEL.."0-1_lootbox_01_mat_ST001"]="Open",
    [LEVEL.."0-1_item_loot_bag_03_AP1_3"]="Take",
    [LEVEL.."0-1_sosletter3_2"]="Check",
}
local OPEN = LEVEL.."0-1_lootbox_01_mat_ST001"
local WORLD, SCREEN, NO_COLLISION = 0, 1, 0
local status = "UNATTEMPTED"

local function log(event, detail)
    print("IIP_WORLD_TEMPLATE event="..event.." "..(detail or "").."\n")
end
local function valid(obj) return obj ~= nil and obj:IsValid() end
local function path(obj)
    return assert(obj:GetFullName():match("^[^ ]+ (.+)$"),"unreadable object path")
end
local function is(obj, class)
    return valid(obj) and valid(obj:GetClass()) and path(obj:GetClass()) == class
end
local function same(a,b)
    return valid(a) and valid(b) and a:GetAddress() == b:GetAddress()
end

local function install_template_trial()
    if status ~= "UNATTEMPTED" then return end
    status = "STOPPED"
    -- Must happen before loading the known placed Open, not during its BeginPlay.
    if valid(StaticFindObject(OPEN)) then
        log("SKIP","reason=target_already_loaded")
        return
    end
    local template = StaticFindObject(TEMPLATE)
    if not valid(template) then
        -- UE4SS resolves an Asset Registry ObjectPath, including the object name.
        local ok, reason = pcall(LoadAsset, GENERATED_CLASS)
        if not ok then log("SKIP",("reason=load_asset_failed detail=%q"):format(tostring(reason):sub(1,120)));return end
        template = StaticFindObject(TEMPLATE)
    end
    if not is(template,COMPONENT) or path(template) ~= TEMPLATE then
        log("SKIP","reason=template_unavailable_or_identity")
        return
    end
    local prior_space, prior_collision = template.Space, template:GetCollisionEnabled()
    log("TEMPLATE_FOUND",("space=%s collision=%s"):format(tostring(prior_space),tostring(prior_collision)))
    if prior_space ~= SCREEN then
        log("SKIP","reason=template_not_screen")
        return
    end
    local ok,reason=pcall(function()
        template:SetCollisionEnabled(NO_COLLISION)
        assert(template:GetCollisionEnabled() == NO_COLLISION,"template collision readback")
        template.Space = WORLD
        assert(template.Space == WORLD,"template Space readback")
    end)
    if not ok then
        -- Restore our template write only; no edits to placed actors.
        if valid(template) then
            pcall(function()
                template.Space = prior_space
                template:SetCollisionEnabled(prior_collision)
            end)
        end
        log("REJECTED",("reason=%q"):format(tostring(reason):sub(1,180)))
        return
    end
    status = "WRITTEN"
    log("TEMPLATE_WORLD","space=0 collision=0 write=one_shot")
end

local function sample(label,actor)
    local action=OBJECTS[path(actor)]
    if not action then return end
    local component=actor.ExtendedWidget
    if not is(component,COMPONENT) or path(component) ~= path(actor)..".ExtendedWidget"
        or not same(component:GetOwner(),actor) then
        log(label,("action=%s reason=component_identity"):format(action))
        return
    end
    local widget,rt=component:GetUserWidgetObject(),component:GetRenderTarget()
    log(label,("action=%s template_status=%s space=%s collision=%s widget=%s rt=%s added_to_screen=%s"):format(
        action,status,tostring(component.Space),tostring(component:GetCollisionEnabled()),
        tostring(is(widget,TIP)),tostring(valid(rt)),tostring(component.bAddedToScreen)))
end

local function on_begin(context)
    local actor = context:get()
    if not valid(actor) then return end
    if not OBJECTS[path(actor)] then return end
    local ok, reason=pcall(sample,"PLACED_BEGIN",actor)
    if not ok then log("READ_REJECTED",("reason=%q"):format(tostring(reason):sub(1,180))) end
end

local function manual_sample()
    for actor_path,_ in pairs(OBJECTS) do
        local actor=StaticFindObject(actor_path)
        if valid(actor) then
            local ok,reason=pcall(sample,"PLACED_SAMPLE",actor)
            if not ok then log("READ_REJECTED",("reason=%q"):format(tostring(reason):sub(1,180))) end
        end
    end
end

-- Use the verified engine-tick queue; LoadAsset must only run on the game thread.
if EngineTickAvailable ~= true or not EGameThreadMethod or not EGameThreadMethod.EngineTick then
    log("SKIP","reason=engine_thread_unavailable")
else
    RegisterBeginPlayPostHook(on_begin)
    ExecuteInGameThread(function()
        local ok,reason=pcall(install_template_trial)
        if not ok then log("REJECTED",("reason=%q"):format(tostring(reason):sub(1,180))) end
    end,EGameThreadMethod.EngineTick)
    if Key and type(Key.F5)=="number" and not IsKeyBindRegistered(Key.F5) then
        RegisterKeyBind(Key.F5,function()
            ExecuteInGameThread(manual_sample,EGameThreadMethod.EngineTick)
        end)
        log("SAMPLE_KEY","key=F5")
    else
        log("SAMPLE_KEY_UNAVAILABLE","key=F5")
    end
    log("ARMED","scope=shared_SCS_template_once no_per_instance_mutations=true")
end
