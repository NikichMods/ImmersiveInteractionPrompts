-- SPDX-License-Identifier: MPL-2.0
-- Research-only; not deployed. One exact event, no UI suppression.
local Source=require("IIPInteractionSource")
local Visibility=require("IIPOpenVisibility")
local Observer=require("IIPShowTipEventObserver")
local EVENT="/Script/Genesis.BaseGameEventObject:ShowTipEvent"
local function log(event,detail)
    print("IIP_SHOWTIP event="..event.." "..(detail or "").."\n")
end
local function valid(o) return o~=nil and o:IsValid() end
local function cls(o) return o:GetClass():GetFullName():match("^[^ ]+ (.+)$") end
local function alive(o)
    if not valid(o) then return false end
    local f=StaticFindObject("/Script/Engine.KismetSystemLibrary:IsValid")
    local c=StaticFindObject("/Script/Engine.Default__KismetSystemLibrary")
    assert(valid(f) and f:type()=="UFunction" and
        f:GetFullName()=="Function /Script/Engine.KismetSystemLibrary:IsValid"
        and valid(c) and cls(c)=="/Script/Engine.KismetSystemLibrary",
        "native IsValid unavailable")
    return f(c,o)==true
end
local function bind(callback)
    local f=StaticFindObject(EVENT)
    if not valid(f) then return false,"base event UFunction not loaded" end
    assert(f:type()=="UFunction" and
        f:GetFullName()=="Function "..EVENT,"exact event name mismatch")
    local flags=f:GetFunctionFlags()
    assert(math.type(flags)=="integer" and (flags & 0x400)==0,
        "ShowTipEvent unexpectedly marked native")
    -- An unimplemented BlueprintImplementableEvent may not support
    -- RegisterHook in UE4SS 83330635. Reject rather than broad-hook.
    local ok,pre,post=pcall(RegisterHook,EVENT,callback)
    if not ok then return false,"RegisterHook rejected: "..tostring(pre) end
    assert(math.type(pre)=="integer" and pre>0 and pre==post,
        "registration did not yield a script-hook pair")
    return true
end
local ok,err=pcall(function()
    for _,name in ipairs({"RegisterBeginPlayPostHook","RegisterEndPlayPreHook",
        "RegisterLoadMapPreHook","LoopInGameThreadAfterFrames",
        "CancelDelayedAction","StaticFindObject","RegisterHook"}) do
        assert(type(_G[name])=="function","missing API "..name)
    end
    assert(EngineTickAvailable==true,"EngineTick unavailable")
    Observer.start({
        begin=RegisterBeginPlayPostHook,finish=RegisterEndPlayPreHook,
        map_pre=RegisterLoadMapPreHook,loop=LoopInGameThreadAfterFrames,
        cancel=CancelDelayedAction,bind=bind,native_alive=alive,
        hint_visible=function(w)return Visibility.visible(w,alive)end
    },Source,log)
end)
if not ok then log("UNAVAILABLE",tostring(err):sub(1,160)) end
-- Callback returns nil. No gameplay writes, synthetic interactions or polling all owners.
