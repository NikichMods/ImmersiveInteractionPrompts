-- SPDX-License-Identifier: MPL-2.0
-- Exact-build research observer. No hook on host calls, no UI/actor writes.
-- Not an installation authorization or a production selected-owner provider.
local Source=require("IIPInteractionSource")
local Visibility=require("IIPOpenVisibility")
local Observer=require("IIPSelectedOwnerObserver")
local UEHelpers=require("UEHelpers")
local COMPONENT="/Script/Genesis.PlayerActionComponent"
local GENESIS="/Script/Genesis.GenesisCharacter"
local PROPERTY="IIPResearchCommittedTipOwner_83330635"
local function log(event,fields)
    print("IIP_SELECTED_OWNER event="..event.." "..(fields or "").."\n")
end
local function valid(o) return o~=nil and o:IsValid() end
local function pathname(o)
    return assert(o:GetFullName():match("^[^ ]+ (.+)$"),"missing UObject path")
end
local function cls(o) return pathname(o:GetClass()) end
local function same(a,b)
    return valid(a) and valid(b) and a:GetAddress()==b:GetAddress()
end
local function inherited(o,path)
    local c=o:GetClass()
    for _=1,32 do
        if not valid(c) then return false end
        if pathname(c)==path then return true end
        c=c:GetSuperStruct()
    end
    error("Genesis class hierarchy bound exceeded")
end
local function key(o)
    return pathname(o).."|"..cls(o).."|"..tostring(o:GetAddress())
end
local function exact_function(p)
    local f=StaticFindObject(p)
    assert(valid(f) and f:type()=="UFunction"
        and f:GetFullName()=="Function "..p,"missing exact native function "..p)
    return f
end
local function main()
    for _,name in ipairs({"StaticFindObject","RegisterCustomProperty",
            "LoopInGameThreadAfterFrames","CancelDelayedAction",
            "RegisterLoadMapPreHook"}) do
        assert(type(_G[name])=="function","missing UE4SS API "..name)
    end
    assert(EngineTickAvailable==true,"EngineTick unavailable")
    assert(type(UEHelpers.GetPlayerController)=="function",
        "UEHelpers.GetPlayerController unavailable")
    assert(type(PropertyTypes)=="table" and
        type(PropertyTypes.WeakObjectProperty)=="table",
        "WeakObjectProperty type metadata missing")
    assert(PropertyTypes.WeakObjectProperty.Size==8,
        "weak pair layout not the verified 8 bytes")
    local component_class=StaticFindObject(COMPONENT)
    assert(valid(component_class) and component_class:type()=="UClass"
        and pathname(component_class)==COMPONENT,"exact PlayerActionComponent class missing")
    local native_valid=exact_function("/Script/Engine.KismetSystemLibrary:IsValid")
    local system_cdo=StaticFindObject("/Script/Engine.Default__KismetSystemLibrary")
    assert(valid(system_cdo) and cls(system_cdo)=="/Script/Engine.KismetSystemLibrary",
        "native IsValid CDO absent")
    local function alive(o)
        return valid(o) and native_valid(system_cdo,o)==true
    end
    -- UE4SS metadata addition only. This does not assign to the game field.
    RegisterCustomProperty({
        Name=PROPERTY,Type=PropertyTypes.WeakObjectProperty,
        BelongsToClass=COMPONENT,OffsetInternal=0x410
    })
    local controller=nil
    local function read()
        if not alive(controller) then
            controller=UEHelpers.GetPlayerController()
        end
        if not alive(controller) then
            return {status="GAP",reason="no_local_player_controller"}
        end
        local pawn=controller.Pawn
        if not alive(pawn) then return {status="GAP",reason="no_player_pawn"} end
        if not inherited(pawn,GENESIS) then
            return {status="GAP",reason="non_genesis_pawn"}
        end
        -- Exact reflected operation used by native character setup. No raw
        -- character+0x560 dereference, no global interactable search.
        local component=pawn:GetComponentByClass(component_class)
        if not alive(component) then
            return {status="GAP",reason="no_player_action_component"}
        end
        assert(cls(component)==COMPONENT and same(component:GetOwner(),pawn),
            "PlayerActionComponent ownership/class mismatch")
        local weak=component[PROPERTY]
        assert(type(weak)=="userdata" or type(weak)=="table",
            "custom weak property did not return a wrapper")
        assert(type(weak.Get)=="function",
            "custom weak property does not expose FWeakObjectPtr:Get")
        local actor=weak:Get()
        if not alive(actor) then actor=nil end
        local result={status="READY",pawn_key=key(pawn),component_key=key(component)}
        if actor then
            result.actor=actor
            result.key=key(actor)
        end
        return result
    end
    local callback=Observer.start({
        read=read,map_pre=function(fn)
            RegisterLoadMapPreHook(function(...)
                controller=nil
                return fn(...)
            end)
        end,
        loop=LoopInGameThreadAfterFrames,cancel=CancelDelayedAction,
        native_alive=alive,
        hint_visible=function(w)return Visibility.visible(w,alive)end
    },Source,log)
    assert(callback and type(callback.stop)=="function",
        "observer initialization failed")
end
local ok,err=pcall(main)
if not ok then log("UNAVAILABLE",tostring(err):sub(1,190)..
    " no_selected_owner_coverage=true") end
-- Never call actor interaction APIs, write the custom field or suppress TipHUD.
