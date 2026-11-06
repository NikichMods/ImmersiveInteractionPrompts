-- SPDX-License-Identifier: MPL-2.0
-- Research-only read-only native prompt event correlation. NOT a World renderer.
-- Package the four Scripts files together only for a separately authorized run.
local Source=require("IIPInteractionSource")
local Visibility=require("IIPOpenVisibility")
local Correlation=require("IIPEventCorrelation")
local CANSHOW="/Game/MainContent/Template/UMG/TipHUD.TipHUD_C:CanShow"
local function log(event,fields)
    print("IIP_EVENT_CORRELATION event="..event.." "..(fields or "").."\n")
end
local function valid(o) return o~=nil and o:IsValid() end
local function cls(o) return o:GetClass():GetFullName():match("^[^ ]+ (.+)$") end
local function native_alive(o)
    if not valid(o) then return false end
    local f=StaticFindObject("/Script/Engine.KismetSystemLibrary:IsValid")
    local cdo=StaticFindObject("/Script/Engine.Default__KismetSystemLibrary")
    assert(valid(f) and f:type()=="UFunction" and
        f:GetFullName()=="Function /Script/Engine.KismetSystemLibrary:IsValid"
        and valid(cdo) and cls(cdo)=="/Script/Engine.KismetSystemLibrary",
        "native IsValid contract missing")
    return f(cdo,o)==true
end
local function bind_can_show(callback)
    local f=StaticFindObject(CANSHOW) -- lookup only; never force-load host assets
    if not valid(f) then return false,"exact UFunction not loaded" end
    assert(f:type()=="UFunction" and
        f:GetFullName()=="Function "..CANSHOW,"CanShow UFunction mismatch")
    local flags=f:GetFunctionFlags()
    assert(math.type(flags)=="integer" and (flags & 0x400)==0,
        "CanShow not verified non-native Blueprint")
    local pre,post=RegisterHook(CANSHOW,callback)
    assert(math.type(pre)=="integer" and pre>0 and pre==post,
        "unexpected non-native script-hook registration IDs")
    return true
end
local ok,e=pcall(function()
    for _,name in ipairs({"RegisterBeginPlayPostHook","RegisterEndPlayPreHook",
        "RegisterLoadMapPreHook","LoopInGameThreadAfterFrames",
        "CancelDelayedAction","StaticFindObject","RegisterHook"}) do
        assert(type(_G[name])=="function","missing UE4SS API: "..name)
    end
    assert(EngineTickAvailable==true,"EngineTick unavailable")
    Correlation.start({
        begin=RegisterBeginPlayPostHook,finish=RegisterEndPlayPreHook,
        map_pre=RegisterLoadMapPreHook,loop=LoopInGameThreadAfterFrames,
        cancel=CancelDelayedAction,bind_can_show=bind_can_show,
        native_alive=native_alive,
        hint_visible=function(w) return Visibility.visible(w,native_alive) end,
    },Source,log)
end)
if not ok then log("UNAVAILABLE",tostring(e):sub(1,180)) end
-- No CanShow boolean write, UI manipulation, synthetic action or state mutation.
