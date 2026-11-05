-- SPDX-License-Identifier: MPL-2.0
-- READ-ONLY multi-action event probe entrypoint, not a renderer.
-- For a separately authorized test deployment, place this entrypoint and its
-- IIPInteractionSource.lua, IIPInteractionEvents.lua and IIPOpenVisibility.lua under ONE Scripts/.
local Source=require("IIPInteractionSource")
local Events=require("IIPInteractionEvents")
local Visibility=require("IIPOpenVisibility")
local function log(event,info)
    print("IIP_MULTI_ACTION event="..event.." "..(info or "").."\n")
end
local function valid(o)return o~=nil and o:IsValid()end
local function cls(o)return o:GetClass():GetFullName():match("^[^ ]+ (.+)$")end
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
    assert(EngineTickAvailable==true,"engine tick unavailable")
    local api={
        begin=RegisterBeginPlayPostHook,
        finish=RegisterEndPlayPreHook,
        map_pre=RegisterLoadMapPreHook,
        loop=LoopInGameThreadAfterFrames,
        cancel=CancelDelayedAction,
        native_alive=native_alive,
        hint_visible=function(widget)return Visibility.visible(widget,native_alive)end,
    }
    Events.start(api,Source,log)
end)
if not ok then log("UNAVAILABLE",tostring(reason):sub(1,180))end
-- Deliberately no input override, SetText, SetVisibility, component creation,
-- actor scan, native action invocation, save/settings or game-state writes.
