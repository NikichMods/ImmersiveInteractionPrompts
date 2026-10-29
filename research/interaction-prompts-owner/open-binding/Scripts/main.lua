-- SPDX-License-Identifier: MPL-2.0
-- Research only: natural SetShow post-event -> exact widget/component/actor/pose.
-- No installation, object enumeration, setters, Create, LoadAsset or UI ownership.
local HOOK="/Script/Genesis.ExtendedWidgetComponent:SetShow"
local COMPONENT="/Script/Genesis.ExtendedWidgetComponent"
local WIDGET="/Game/MainContent/Template/UMG/TipHUD.TipHUD_C"
local BASE="/Game/MainContent/Template/BaseBlueprint/BaseGameEventObject_BP.BaseGameEventObject_BP_C"
local phase,deadline,calls,samples="armed",0,0,0
local pre,post,target,previous=nil,nil,nil,nil
local pending=false
local function log(e,s) print("IIP_OPEN_BINDING event="..e.." "..(s or "").."\n") end
local function valid(o) return o~=nil and o:IsValid() end
local function path(o) return assert(o:GetFullName():match("^[^ ]+ (.+)$")) end
local function cls(o) return path(o:GetClass()) end
local function same(a,b) return valid(a) and valid(b) and a:GetAddress()==b:GetAddress() end
local function ref(o) return {path=path(o),class=cls(o),address=o:GetAddress()} end
local function resolve(r)
    local o=StaticFindObject(r.path)
    if not valid(o) then return nil end
    assert(cls(o)==r.class and o:GetAddress()==r.address,"identity changed")
    return o
end
local function derives(o,base)
    local c=o:GetClass()
    for _=1,32 do
        if not valid(c) then return false end
        if path(c)==base then return true end
        c=c:GetSuperStruct()
    end
    error("class ancestry exceeds bound")
end
local function stop(reason)
    if phase=="stopped" and not pre then return end
    phase="stopped" -- Inert even if unregister fails; no rearm.
    target,previous=nil,nil
    if pre and post then
        local ok,err=pcall(UnregisterHook,HOOK,pre,post)
        if ok then pre,post=nil,nil
        else log("UNREGISTER_FAILED",tostring(err):sub(1,180)) end
    end
    log("STOP","reason="..reason.." callbacks="..calls.." samples="..samples.." hook_remaining="..tostring(pre~=nil))
end
local function guard(fn)
    local ok,err=pcall(fn)
    if not ok then log("FAILED",tostring(err):sub(1,220));stop("failure") end
end
local function dispatch(fn)
    local ok,err=pcall(ExecuteInGameThread,function()guard(fn)end,EGameThreadMethod.EngineTick)
    if not ok then phase="stopped";log("DISPATCH_FAILED",tostring(err):sub(1,180)) end
end
local function finite(n)
    assert(type(n)=="number" and n==n and n~=math.huge and n~=-math.huge,"non-finite transform")
    return string.format("%.9g",n)
end
local function vector(v) return finite(v.X)..","..finite(v.Y)..","..finite(v.Z) end
local function rotation(v) return finite(v.Pitch)..","..finite(v.Yaw)..","..finite(v.Roll) end
local function eligible(w)
    if not valid(w) or cls(w)~=WIDGET then return false end
    local b=w.TextBlock_89
    assert(valid(b) and cls(b)=="/Script/UMG.TextBlock","stock text differs")
    return (w.Visibility==0 or w.Visibility==3 or w.Visibility==4) and w.RenderOpacity>0
        and w.bIsEnabled==true and b.Visibility~=1 and b.Visibility~=2
        and b.RenderOpacity>0 and b.Text:ToString()=="Открыть"
end
local function snapshot(component_ref,reason)
    if phase~="waiting" and phase~="bound" then return end
    if os.time()>=deadline then stop("timeout");return end
    local c=resolve(component_ref)
    if not c then if target then stop("component_gone") end;return end
    assert(cls(c)==COMPONENT,"unexpected component class")
    if target and c:GetAddress()~=target.component.address then return end
    local w=c:GetWidget()
    if not valid(w) then if target then stop("widget_rebound_or_gone") end;return end
    assert(same(w,c:GetUserWidgetObject()) and (not valid(w) or same(w,c.Widget)),"widget getters/storage disagree")
    if target and (not valid(w) or w:GetAddress()~=target.widget.address or path(w)~=target.widget.path) then
        stop("widget_rebound_or_gone");return
    end
    if c.bVisible~=true or c.bAddedToScreen~=true or not eligible(w) then
        if target then stop("target_not_visible_open") end
        return
    end
    assert(c:GetWidgetSpace()==1,"expected stock Screen component")
    local actor=c:GetOwner()
    assert(valid(actor) and derives(actor,BASE),"owner is not BaseGameEventObject_BP-derived")
    assert(same(actor.ExtendedWidget,c),"actor component backlink mismatch")
    if target then
        local saved_actor=resolve(target.actor)
        local saved_widget=resolve(target.widget)
        if not saved_actor or not saved_widget then stop("actor_or_widget_gone");return end
        assert(same(actor,saved_actor) and same(w,saved_widget),"owner/widget changed")
    end
    local argument=actor.TipHUDArgument
    assert(valid(argument) and cls(argument)=="/Script/Genesis.TipHUDArgumentComponent"
        and same(argument:GetOwner(),actor),"argument owner mismatch")
    assert(argument.msgTag:ToString()=="Open" and argument.ActionName==25,"not semantic Open/Interact")
    local new_widget,sender=c.NewUserWidget,c.SenderActor
    assert(not valid(new_widget) or same(new_widget,w),"NewUserWidget disagrees with displayed widget")
    if valid(sender) then assert(derives(sender,"/Script/Engine.Actor"),"SenderActor is not Actor") end
    local location=vector(c:K2_GetComponentLocation())
    local rot=rotation(c:K2_GetComponentRotation())
    local scale=vector(c:K2_GetComponentScale())
    local actor_location=vector(actor:K2_GetActorLocation())
    local pose=location.."|"..rot.."|"..scale.."|"..actor_location
    samples=samples+1
    if not target then
        target={component=ref(c),widget=ref(w),actor=ref(actor)};phase="bound"
        -- Full names are quoted for spaces; these paths are session identities, not selectors for future runs.
        log("MATCH","widget="..string.format("%q",path(w)).." component="..string.format("%q",path(c))
            .." actor="..string.format("%q",path(actor)).." actor_class="..string.format("%q",cls(actor))
            .." widget_address="..w:GetAddress().." component_address="..c:GetAddress().." actor_address="..actor:GetAddress()
            .." reciprocal=true tag=Open action=25 new_widget="..(valid(new_widget) and "same" or "null")
            .." sender="..(valid(sender) and string.format("%q",path(sender)) or "null")
            .." sender_is_owner="..tostring(same(sender,actor)))
    end
    log("POSE","sample="..samples.." reason="..reason.." changed="..tostring(previous~=nil and previous~=pose)
        .." component_world="..location.." rotation_pyr="..rot.." scale="..scale.." actor_world="..actor_location)
    previous=pose
    if samples>=6 then stop("sample_budget") end
end
local function observe(context,show,not_fading,fading,...)
    if phase~="waiting" and phase~="bound" then return end
    local extra=select("#",...)
    -- Hook wrappers are consumed now; only copied identity/bool enter the EngineTick queue.
    local ok,err=pcall(function()
        calls=calls+1
        if calls>=64 then phase="stopping";dispatch(function()stop("callback_budget")end);return end
        assert(extra==0 and show~=nil and not_fading~=nil and fading~=nil,"SetShow signature differs")
        local shown=show:get();assert(type(shown)=="boolean","Show is not bool")
        local c=context:get();assert(valid(c) and cls(c)==COMPONENT,"SetShow context differs")
        if target and c:GetAddress()~=target.component.address then return end
        if target and not shown then phase="stopping";dispatch(function()stop("native_hide")end);return end
        if not shown or target or pending then return end
        local copied=ref(c);pending=true
        dispatch(function()pending=false;snapshot(copied,"native_show_post_deferred")end)
    end)
    if not ok then phase="stopping";log("FAILED",tostring(err):sub(1,220));dispatch(function()stop("hook_failure")end) end
    -- Never return pcall's boolean or override a native return/argument.
end
local function control()
    if phase=="armed" then
        phase,deadline="waiting",os.time()+60
        local f=StaticFindObject(HOOK)
        assert(valid(f) and f:type()=="UFunction" and f:GetFullName()=="Function "..HOOK
            and (f:GetFunctionFlags()&0x400)~=0,"native SetShow NOT_LOADED/differs")
        pre,post=RegisterHook(HOOK,function()end,observe)
        assert(type(pre)=="number" and pre>0 and type(post)=="number" and post>0,"invalid native hook IDs")
        ExecuteInGameThreadWithDelay(60000,function()if phase~="stopped" then stop("timeout")end end)
        log("WAITING","natural_Open_only=true callbacks_max=64 samples_max=6 duration_max=60s")
    elseif phase=="bound" then snapshot(target.component,"user") end
end
local ok,err=pcall(function()
    for _,name in ipairs({"StaticFindObject","RegisterHook","UnregisterHook","RegisterKeyBind","IsKeyBindRegistered",
        "ExecuteInGameThread","ExecuteInGameThreadWithDelay"}) do assert(type(_G[name])=="function","missing API: "..name) end
    assert(EngineTickAvailable==true and type(EGameThreadMethod)=="table"
        and type(EGameThreadMethod.EngineTick)=="number","EngineTick unavailable")
    local mods={ModifierKey.CONTROL,ModifierKey.ALT}
    assert(not IsKeyBindRegistered(Key.F8,mods) and not IsKeyBindRegistered(Key.F7,mods),"control key collision")
    RegisterKeyBind(Key.F8,mods,function()dispatch(control)end)
    RegisterKeyBind(Key.F7,mods,function()dispatch(function()stop("user")end)end)
end)
if ok then log("ARMED","CtrlAltF8=arm_or_snapshot CtrlAltF7=stop one_attempt=true")
else phase="stopped";log("UNAVAILABLE",tostring(err):sub(1,220)) end
