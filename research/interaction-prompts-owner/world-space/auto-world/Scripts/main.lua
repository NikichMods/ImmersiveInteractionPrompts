-- SPDX-License-Identifier: MPL-2.0
-- SOURCE-ONLY automatic World candidate. Not accepted until authorized UE4 run.
-- Normal load: no manual key chord, reload, CanShow override or native Screen write.
local function log(event,info)
    print("IIP_AUTO_WORLD event="..event.." "..(info or "").."\n")
end
local function valid(o)return o~=nil and o:IsValid()end
local function cls(o)
    return o:GetClass():GetFullName():match("^[^ ]+ (.+)$")
end
local function native_alive(o)
    if not valid(o)then return false end
    local f=StaticFindObject("/Script/Engine.KismetSystemLibrary:IsValid")
    local cdo=StaticFindObject("/Script/Engine.Default__KismetSystemLibrary")
    assert(valid(f) and f:type()=="UFunction" and
        f:GetFullName()=="Function /Script/Engine.KismetSystemLibrary:IsValid"
        and valid(cdo) and cls(cdo)=="/Script/Engine.KismetSystemLibrary",
        "native IsValid contract missing")
    return f(cdo,o)==true
end
local ok,reason=pcall(function()
    for _,name in ipairs({"RegisterBeginPlayPostHook","RegisterEndPlayPreHook",
        "RegisterLoadMapPreHook","LoopInGameThreadAfterFrames",
        "CancelDelayedAction","StaticFindObject"})do
        assert(type(_G[name])=="function","missing UE4SS API: "..name)
    end
    assert(EngineTickAvailable==true,"verified game-thread EngineTick unavailable")
    local Source=require("IIPInteractionSource")
    local Events=require("IIPInteractionEvents")
    local Visibility=require("IIPOpenVisibility")
    local Handoff=require("IIPWorldHandoff")
    local Bridge=require("IIPWorldHandoffBridge")
    local Renderer=require("IIPWorldRenderer")
    local Target=require("IIPWorldTarget")
    local World=require("IIPWorldChild")
    local Session=require("IIPAutoWorldSession")
    Session.start({
        source=Source,events=Events,visibility=Visibility,handoff=Handoff,
        bridge=Bridge,renderer=Renderer,target=Target,world=World
    },{
        begin=RegisterBeginPlayPostHook,
        finish=RegisterEndPlayPreHook,
        map_pre=RegisterLoadMapPreHook,
        loop=LoopInGameThreadAfterFrames,
        cancel=CancelDelayedAction,
        native_alive=native_alive,
        hint_visible=function(widget)return Visibility.visible(widget,native_alive)end,
    },log)
end)
if not ok then log("UNAVAILABLE",tostring(reason):sub(1,190))end
-- World writes are restricted to our own transient component and widget tree.
-- Original TipHUD, action semantics, saves and settings remain untouched.
