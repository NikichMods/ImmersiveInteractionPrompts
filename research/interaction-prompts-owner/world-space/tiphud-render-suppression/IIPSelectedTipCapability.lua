-- SPDX-License-Identifier: MPL-2.0
-- Selected-owner native TipHUD capability reader. Strictly read-only.
-- Not a general actor scanner and not permission to replace native Screen.
local M={}
local WIDGET="/Game/MainContent/Template/UMG/TipHUD.TipHUD_C"
local COMPONENT="/Script/Genesis.ExtendedWidgetComponent"
local ARGUMENT="/Script/Genesis.TipHUDArgumentComponent"
local function valid(o) return o~=nil and o:IsValid() end
local function path(o)
    return assert(o:GetFullName():match("^[^ ]+ (.+)$"),"object path missing")
end
local function cls(o)return path(o:GetClass())end
local function same(a,b)
    return valid(a) and valid(b) and a:GetAddress()==b:GetAddress()
end
local function ref(o)
    local address=o:GetAddress()
    assert(type(address)=="number" and address>0,"invalid selected object address")
    return {path=path(o),class=cls(o),address=address}
end
local function key(r)
    return r.path.."|"..r.class.."|"..tostring(r.address)
end

-- Only the native selected owner is inspected; unlike the legacy World path,
-- this does not require a particular actor ancestor or Open/Take/Check tag.
-- Read-only capability does not authorize World presentation or Screen hiding.
function M.inspect_selected(actor,native_alive,hint_visible)
    assert(type(native_alive)=="function" and type(hint_visible)=="function",
        "selected native validity/visibility gates missing")
    if not valid(actor) or not native_alive(actor) then return nil,"selected_unavailable" end
    if actor:HasAnyFlags(EObjectFlags.RF_ClassDefaultObject | EObjectFlags.RF_ArchetypeObject) then
        return nil,"selected_default_object"
    end
    local ok_arg,arg=pcall(function()return actor.TipHUDArgument end)
    if not ok_arg or not valid(arg) or not native_alive(arg)
        or cls(arg)~=ARGUMENT or not same(arg:GetOwner(),actor) then
        return nil,"no_matching_argument"
    end
    local ok_tag,tag=pcall(function()return arg.msgTag:ToString()end)
    if not ok_tag or type(tag)~="string" or #tag<1 or #tag>64
        or not tag:match("^[%w_%-]+$") then return nil,"unsupported_action_tag" end
    local ok_source,source=pcall(function()return actor.ExtendedWidget end)
    if not ok_source or not valid(source) or not native_alive(source)
        or cls(source)~=COMPONENT or not same(source:GetOwner(),actor) then
        return nil,"no_matching_source"
    end
    local widget=source:GetUserWidgetObject()
    if not valid(widget) or not native_alive(widget) or cls(widget)~=WIDGET
        or not same(source:GetWidget(),widget) or not same(source.Widget,widget)
        or (valid(source.NewUserWidget) and not same(source.NewUserWidget,widget)) then
        return nil,"no_matching_tiphud"
    end
    if source:GetWidgetSpace()~=1 or source.bVisible~=true
        or source.bAddedToScreen~=true then
        return nil,"native_screen_not_shown"
    end
    local label=widget.TextBlock_89
    if not valid(label) or not native_alive(label)
        or cls(label)~="/Script/UMG.TextBlock" then return nil,"native_text_widget_missing" end
    local ok_text,text=pcall(function()return label:GetText():ToString()end)
    if not ok_text or type(text)~="string" or #text<1 or #text>512
        or text:find("[\r\n]") then return nil,"native_text_not_ready" end
    local ok_hint,hint=pcall(hint_visible,widget)
    local hint_state=not ok_hint and "unknown" or (hint==true and "visible" or "hidden")
    local ar,cr,wr=ref(actor),ref(source),ref(widget)
    return {actor=key(ar),component=key(cr),widget=key(wr),
        refs={actor=ar,component=cr,widget=wr},action=tag,
        native_text=text,shown=true,ready=true,native_screen=true,
        hint_state=hint_state},"ready"
end

return M
