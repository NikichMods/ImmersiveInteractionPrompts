-- SPDX-License-Identifier: MPL-2.0
-- Source-only, read-only Asterigos Open owner adapter. Not a hook installer.
-- Produces primitive identity records for IIPTargetPolicy; never changes TipHUD.
local M = {}
local BASE = "/Game/MainContent/Template/BaseBlueprint/BaseGameEventObject_BP.BaseGameEventObject_BP_C"
local WIDGET = "/Game/MainContent/Template/UMG/TipHUD.TipHUD_C"
local COMPONENT = "/Script/Genesis.ExtendedWidgetComponent"
local ARGUMENT = "/Script/Genesis.TipHUDArgumentComponent"

local function valid(o) return o ~= nil and o:IsValid() end
local function path(o)
    return assert(o:GetFullName():match("^[^ ]+ (.+)$"), "full UObject path missing")
end
local function cls(o) return path(o:GetClass()) end
local function same(a,b)
    return valid(a) and valid(b) and a:GetAddress() == b:GetAddress()
end
local function inherited(o,name)
    local c = o:GetClass()
    for _ = 1,32 do
        if not valid(c) then return false end
        if path(c) == name then return true end
        c = c:GetSuperStruct()
    end
    error("class ancestor bound exceeded")
end
local function ref(o)
    local addr = o:GetAddress()
    assert(type(addr) == "number" and addr > 0, "unsupported UObject address")
    return {path = path(o), class = cls(o), address = addr}
end
local function key(r)
    return r.path .. "|" .. r.class .. "|" .. tostring(r.address)
end
local function resolve(r)
    local o = StaticFindObject(r.path)
    if not valid(o) then return nil end
    if path(o) ~= r.path or cls(o) ~= r.class or o:GetAddress() ~= r.address then
        error("identity_changed: " .. r.path)
    end
    return o
end

-- Only immutable primitive actor identity can cross an asynchronous boundary.
-- This route is safe for EndPlay even if actor-owned components are already
-- detached: unlike acquire(), it does not require the prompt or argument.
function M.actor_identity(actor)
    if not valid(actor) or not inherited(actor, BASE) then return nil end
    if actor:HasAnyFlags(EObjectFlags.RF_ClassDefaultObject | EObjectFlags.RF_ArchetypeObject) then
        return nil
    end
    local r=ref(actor)
    return {key=key(r),ref=r}
end

function M.resolve_actor(identity)
    assert(type(identity)=="table" and type(identity.ref)=="table"
        and identity.key==key(identity.ref), "invalid actor identity")
    local actor=resolve(identity.ref)
    if not actor then return nil end
    assert(inherited(actor,BASE), "actor hierarchy changed")
    return actor
end

-- Global BeginPlay supplies arbitrary actors. Unsupported actors are ignored.
-- For a supported Open actor, absence of an initialized widget is NOT_READY,
-- not permission to call InitWidget, ReceiveBeginPlay or other native setters.
function M.acquire(actor)
    if not valid(actor) or not inherited(actor,BASE) then return nil,"unrelated_actor" end
    if actor:HasAnyFlags(EObjectFlags.RF_ClassDefaultObject | EObjectFlags.RF_ArchetypeObject) then
        return nil,"unrelated_default_object"
    end
    local arg = actor.TipHUDArgument
    if not valid(arg) or cls(arg) ~= ARGUMENT then return nil,"unrelated_argument" end
    local tag = arg.msgTag:ToString()
    if tag ~= "Open" or arg.ActionName ~= 25 then return nil,"other_action" end
    assert(same(arg:GetOwner(),actor), "Open argument owner changed")

    local source = actor.ExtendedWidget
    if not valid(source) then return nil,"not_ready_component" end
    assert(cls(source) == COMPONENT and same(source:GetOwner(),actor)
        and same(actor.ExtendedWidget,source), "Open source owner mismatch")
    local w = source:GetUserWidgetObject()
    if not valid(w) then return nil,"not_ready_widget" end
    assert(cls(w) == WIDGET and same(source:GetWidget(),w) and same(source.Widget,w),
        "Open widget/storage mismatch")
    assert(not valid(source.NewUserWidget) or same(source.NewUserWidget,w),
        "Open replacement widget differs")
    local ar,cr,wr = ref(actor),ref(source),ref(w)
    return {actor=key(ar),component=key(cr),widget=key(wr),
        refs={actor=ar,component=cr,widget=wr}}, "ready"
end

-- Re-fetch all three objects for a fresh observation. The runtime adapter must
-- supply a native PendingKill-aware alive check and an effective hint visibility
-- read such as the existing IIPHintSource.is_visible() contract.
-- A false CanShow callback/event is neither read nor used as selection proof.
function M.snapshot(record, native_alive, hint_visible)
    assert(type(record)=="table" and type(record.refs)=="table"
        and type(native_alive)=="function" and type(hint_visible)=="function",
        "snapshot boundary missing")
    local ar,cr,wr=record.refs.actor,record.refs.component,record.refs.widget
    assert(record.actor==key(ar) and record.component==key(cr)
        and record.widget==key(wr), "record identity mismatch")
    local actor,source,w=resolve(ar),resolve(cr),resolve(wr)
    if not actor or not source or not w then return nil,"object_gone" end
    if not native_alive(actor) or not native_alive(source) or not native_alive(w) then
        return nil,"object_pending_kill"
    end
    assert(inherited(actor,BASE) and cls(source)==COMPONENT and cls(w)==WIDGET
        and same(source:GetOwner(),actor) and same(actor.ExtendedWidget,source)
        and same(source:GetWidget(),w) and same(source:GetUserWidgetObject(),w)
        and same(source.Widget,w), "Open source/widget contract changed")
    assert(source:GetWidgetSpace()==1, "original prompt is not Screen")
    local argument=actor.TipHUDArgument
    assert(valid(argument) and cls(argument)==ARGUMENT
        and same(argument:GetOwner(),actor) and argument.msgTag:ToString()=="Open"
        and argument.ActionName==25, "Open action source changed")
    local shown=source.bVisible==true and source.bAddedToScreen==true
    local ready=false
    if shown then
        local visible=hint_visible(w)
        shown=visible==true
        if shown then
            local b=w.TextBlock_89
            assert(valid(b) and cls(b)=="/Script/UMG.TextBlock","original action text missing")
            local text=b:GetText():ToString()
            ready=type(text)=="string" and #text>0 and #text<=512
                and not text:find("[\r\n]")
        end
    end
    return {actor=record.actor,component=record.component,widget=record.widget,
        shown=shown,ready=ready}
end
return M
