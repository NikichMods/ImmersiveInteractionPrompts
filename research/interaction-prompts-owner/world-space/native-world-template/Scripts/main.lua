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
local ARGUMENT="/Script/Genesis.TipHUDArgumentComponent"
local function action_tag(actor)
    if not valid(actor) then return nil end
    local ok,arg=pcall(function()return actor.TipHUDArgument end)
    if not ok or not is(arg,ARGUMENT) or not same(arg:GetOwner(),actor) then return nil end
    local read,tag=pcall(function()return arg.msgTag:ToString() end)
    if read and type(tag)=="string" and #tag>0 and #tag<=48 then return tag end
    return nil
end

-- Styling is a visual addition to the ORIGINAL World component / TipHUD.
-- World selection itself still comes only from the one SCS-template write.
local style,resources,probe,style_available
local styled,can_show_armed={},false
local function prepare_style()
    local ok_r,r=pcall(require,"IIPTemplateResources")
    local ok_p,p=pcall(require,"IIPTemplateProbe")
    local ok_s,s=pcall(require,"IIPTemplateStyle")
    if not (ok_r and ok_p and ok_s) then
        log("STYLE_UNAVAILABLE","reason=missing_style_module")
        return
    end
    local ok,err=pcall(r.prepare)
    if not ok then
        log("STYLE_UNAVAILABLE",("reason=%q"):format(tostring(err):sub(1,170)))
        return
    end
    resources,probe,style,style_available=r,p,s,true
    log("STYLE_ARMED",("quintus_scale=.400 world_lift=36 rgb=%.2f native_draw=1000x1000"):format(style.RGB))
end

local function on_can_show(context)
    if not style_available then return end
    local widget=context:get()
    if not valid(widget) then return end
    local info=styled[widget:GetAddress()]
    if not info or not info.state or path(widget)~=info.widget then return end
    local component=StaticFindObject(info.component)
    if not is(component,COMPONENT) or component:GetAddress()~=info.component_address
        or not same(component:GetUserWidgetObject(),widget)
        or component.Space~=WORLD then return end
    local ok,err=pcall(style.can_show,component,widget,info.state,probe,log,
        action_tag(component:GetOwner()))
    if not ok then log("STYLE_CADENCE_REJECTED",("reason=%q"):format(tostring(err):sub(1,170))) end
end
local function arm_can_show()
    if can_show_armed then return end
    local fn=StaticFindObject(TIP..":CanShow")
    if not valid(fn) or fn:type()~="UFunction" then
        log("STYLE_HOOK_UNAVAILABLE","reason=CanShow_function_unavailable")
        return
    end
    local ok,pre,post=pcall(RegisterHook,TIP..":CanShow",on_can_show)
    if ok and type(pre)=="number" and pre>0 and pre==post then
        can_show_armed=true
        log("STYLE_HOOK_ARMED","source=TipHUD:CanShow")
    else log("STYLE_HOOK_UNAVAILABLE","reason=registration") end
end

local function try_style_actor(actor)
    if not style_available then return end
    local got,component=pcall(function()return actor.ExtendedWidget end)
    if not got or not is(component,COMPONENT) then return end
    if path(component)~=path(actor)..".ExtendedWidget"
        or not same(component:GetOwner(),actor) or not same(component:GetOuter(),actor)
        or component.Space~=WORLD or component:GetCollisionEnabled()~=NO_COLLISION then return end
    local widget=component:GetUserWidgetObject()
    if not is(widget,TIP) then return end
    local id=widget:GetAddress()
    if styled[id] then
        local old=styled[id]
        if old.widget==path(widget) and old.component==path(component)
            and old.component_address==component:GetAddress() then return end
        styled[id]=nil -- Stale address from another actor cannot inherit style state.
    end
    local record={component=path(component),component_address=component:GetAddress(),
        widget=path(widget),widget_address=id,actor=path(actor)}
    -- Mark before setters; do not double-lift on a repeated BeginPlay callback.
    styled[id]=record
    local ok,result=pcall(style.start,component,widget,resources,probe,log,action_tag(actor))
    if not ok then
        log("STYLE_REJECTED",("actor=%q reason=%q"):format(path(actor),tostring(result):sub(1,170)))
        return
    end
    record.state=result
    log("STYLE_READY",("actor=%q decorated=%s"):format(path(actor),tostring(result.decorated)))
    arm_can_show()
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
    try_style_actor(actor)
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
    prepare_style()
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
