-- SPDX-License-Identifier: MPL-2.0
-- Exact-build research observer. No hook on host calls, no UI/actor writes.
-- Not an installation authorization or a production selected-owner provider.
local Source=require("IIPInteractionSource")
local Visibility=require("IIPOpenVisibility")
local Observer=require("IIPSelectedOwnerObserver")
local COMPONENT="/Script/Genesis.PlayerActionComponent"
local GENESIS="/Script/Genesis.GenesisCharacter"
local PLAYER_CONTROLLER="/Script/Engine.PlayerController"
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
            "RegisterLoadMapPreHook","RegisterBeginPlayPostHook",
            "RegisterEndPlayPreHook"}) do
        assert(type(_G[name])=="function","missing UE4SS API "..name)
    end
    assert(EngineTickAvailable==true,"EngineTick unavailable")
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
    -- BeginPlayPost is already an accepted narrow actor-lifecycle seam in
    -- this project. Cache ONLY identity primitives from an observed local
    -- PlayerController, never a borrowed UObject wrapper across ticks.
    -- A controller that existed before registration is not discovered.
    local controller_id=nil
    local observer=nil
    local function context_active()
        return not observer or observer.status().active
    end
    local function controller_hook_error(where,err)
        controller_id=nil
        log("CONTROLLER_HOOK_ERROR","where="..where..
            " reason="..tostring(err):sub(1,130))
        if observer then observer.stop("controller_"..where..":"..tostring(err)) end
    end
    local function on_controller_begin(arg)
        if not context_active() then return end
        local ok,err=pcall(function()
            assert(arg and type(arg.get)=="function","missing BeginPlay actor argument")
            local candidate=arg:get()
            if not alive(candidate) or not inherited(candidate,PLAYER_CONTROLLER) then
                return
            end
            if candidate:IsLocalPlayerController()~=true then return end
            local identity={path=pathname(candidate),class=cls(candidate),
                address=candidate:GetAddress()}
            if controller_id then
                assert(controller_id.path==identity.path and
                    controller_id.class==identity.class and
                    controller_id.address==identity.address,
                    "multiple local PlayerControllers without EndPlay")
                return
            end
            controller_id=identity
            log("CONTROLLER_ACQUIRED","source=BeginPlayPost local=true"..
                " no_global_scan=true")
        end)
        if not ok then controller_hook_error("BeginPlayPost",err) end
    end
    local function on_controller_end(arg)
        if not context_active() or not controller_id then return end
        local ok,err=pcall(function()
            assert(arg and type(arg.get)=="function","missing EndPlay actor argument")
            local candidate=arg:get()
            if valid(candidate) and pathname(candidate)==controller_id.path
                and cls(candidate)==controller_id.class
                and candidate:GetAddress()==controller_id.address then
                controller_id=nil
                log("CONTROLLER_END","source=EndPlayPre no_hide_proof=true")
            end
        end)
        if not ok then controller_hook_error("EndPlayPre",err) end
    end
    local function resolve_controller()
        if not controller_id then return nil end
        -- Exact lookup, not UEHelpers.FindAllOf or any class/global sweep.
        local candidate=StaticFindObject(controller_id.path)
        if not alive(candidate) then
            controller_id=nil
            log("CONTROLLER_LOST","reason=exact_lookup_unavailable")
            return nil
        end
        assert(inherited(candidate,PLAYER_CONTROLLER) and
            pathname(candidate)==controller_id.path and
            cls(candidate)==controller_id.class and
            candidate:GetAddress()==controller_id.address,
            "cached PlayerController identity mismatch")
        if candidate:IsLocalPlayerController()~=true then
            controller_id=nil
            log("CONTROLLER_LOST","reason=no_longer_local")
            return nil
        end
        return candidate
    end
    local function read()
        local controller=resolve_controller()
        if not controller then
            return {status="GAP",reason="no_captured_local_controller"}
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
    observer=Observer.start({
        read=read,map_pre=function(fn)
            RegisterLoadMapPreHook(function(...)
                controller_id=nil
                log("CONTROLLER_RESET","source=LoadMapPre no_hide_proof=true")
                return fn(...)
            end)
        end,
        loop=LoopInGameThreadAfterFrames,cancel=CancelDelayedAction,
        native_alive=alive,
        hint_visible=function(w)return Visibility.visible(w,alive)end
    },Source,log)
    assert(observer and type(observer.stop)=="function",
        "observer initialization failed")
    RegisterBeginPlayPostHook(on_controller_begin)
    RegisterEndPlayPreHook(on_controller_end)
    log("CONTROLLER_PENDING","beginplay_capture_required=true"..
        " preexisting_controller_coverage=unknown no_global_scan=true")
end
local ok,err=pcall(main)
if not ok then log("UNAVAILABLE",tostring(err):sub(1,190)..
    " no_selected_owner_coverage=true") end
-- Never call actor interaction APIs, write the custom field or suppress TipHUD.
