-- SPDX-License-Identifier: MPL-2.0
-- Resolve a primitive, already observed owner into fresh native objects.
-- No UObject wrapper crosses a game-thread callback or is cached.
local M={}
local function valid(o)return o~=nil and o:IsValid()end
local function path(o)return assert(o:GetFullName():match("^[^ ]+ (.+)$"),"native path missing")end
local function cls(o)return path(o:GetClass())end
local function same_ref(o,r)
    return valid(o) and path(o)==r.path and cls(o)==r.class
        and o:GetAddress()==r.address
end
local function actor_key(k)
    assert(type(k)=="string","invalid actor identity")
    local p,c,a=k:match("^([^|]+)|([^|]+)|(%d+)$")
    assert(p and c and a and #p<=1024,"invalid actor identity format")
    local address=tonumber(a)
    assert(type(address)=="number" and address>0,"invalid actor address")
    return {path=p,class=c,address=address}
end
function M.new(source,native_alive,hint_visible)
    assert(type(source)=="table" and type(source.acquire)=="function"
        and type(source.snapshot)=="function" and
        type(native_alive)=="function" and type(hint_visible)=="function",
        "native target resolver seam missing")
    return function(owner)
        assert(type(owner)=="table" and
            (owner.action=="Open" or owner.action=="Take" or owner.action=="Check"),
            "unsupported owner action")
        local ar=actor_key(owner.actor)
        local actor=StaticFindObject(ar.path)
        if not valid(actor) or not native_alive(actor) then return nil end
        assert(same_ref(actor,ar),"selected actor identity changed")
        local rec,why=source.acquire(actor)
        assert(rec,why or "selected owner was not reacquired")
        assert(rec.actor==owner.actor and rec.component==owner.component
            and rec.widget==owner.widget and rec.action==owner.action,
            "reacquired owner identity changed")
        local row,problem=source.snapshot(rec,native_alive,hint_visible)
        if not row then
            assert(problem=="object_gone" or problem=="object_pending_kill",
                problem or "selected owner has no fresh snapshot")
            return nil
        end
        assert(row.actor==rec.actor and row.component==rec.component
            and row.widget==rec.widget and row.action==rec.action,
            "fresh native snapshot identity changed")
        if row.shown~=true or row.ready~=true then return nil end
        local source_component=StaticFindObject(rec.refs.component.path)
        local widget=StaticFindObject(rec.refs.widget.path)
        assert(same_ref(source_component,rec.refs.component)
            and same_ref(widget,rec.refs.widget)
            and native_alive(source_component) and native_alive(widget),
            "native selected source/widget invalid after snapshot")
        -- Only native original widgets are borrowed. All writes belong
        -- to the independent own World component/host tree.
        return actor,source_component,widget
    end
end
return M
