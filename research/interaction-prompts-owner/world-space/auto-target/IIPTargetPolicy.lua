-- SPDX-License-Identifier: MPL-2.0
-- Source-only target arbitration. No UE4SS calls or native object references.
-- The adapter MUST supply a complete, fresh snapshot of the registered actors.
-- CanShow callbacks alone are never evidence of a selected/visible target.
local M = {}

local function valid_id(v)
    return type(v) == "string" and #v > 0 and #v <= 1024
        and not v:find("[%c]")
end

local function fail(s, why)
    if not s.fault then s.fault = why end
    s.force_release = true
    s.choice = nil
    s.streak = 0
    return nil, s.fault
end

function M.new(capacity)
    assert(type(capacity) == "number" and math.type(capacity) == "integer"
        and capacity >= 1 and capacity <= 4096, "explicit candidate capacity required")
    return {
        capacity = capacity, records = {}, by_widget = {}, by_component = {},
        count = 0, choice = nil, streak = 0, selected = nil, pending = nil,
        force_release = false, fault = nil, serial = 0, reason = "no_snapshot",
    }
end

-- All identities are primitive class/path/address-qualified keys, not UObject wrappers.
-- An actor may be re-created with a new key. Rebinding an existing key silently
-- is forbidden: it could attach a World component to a different native owner.
function M.register(s, actor, component, widget)
    if s.fault then return nil, s.fault end
    if not valid_id(actor) or not valid_id(component) or not valid_id(widget) then
        return fail(s, "invalid_identity")
    end
    local old = s.records[actor]
    if old then
        if old.component == component and old.widget == widget then return true, "unchanged" end
        return fail(s, "actor_rebound_without_endplay")
    end
    if s.by_component[component] or s.by_widget[widget] then
        return fail(s, "component_or_widget_alias")
    end
    if s.count >= s.capacity then return fail(s, "candidate_capacity_exceeded") end
    s.records[actor] = {component = component, widget = widget}
    s.by_component[component] = actor
    s.by_widget[widget] = actor
    s.count = s.count + 1
    -- Registering another actor makes any previous visibility sweep incomplete.
    s.choice = nil
    s.streak = 0
    return true, "added"
end

function M.end_actor(s, actor)
    local rec = s.records[actor]
    if not rec then return false end
    s.records[actor] = nil
    s.by_widget[rec.widget] = nil
    s.by_component[rec.component] = nil
    s.count = s.count - 1
    s.choice = nil
    s.streak = 0
    if s.selected == actor or (s.pending and s.pending.actor == actor) then
        s.force_release = true
    end
    return true
end

-- Call at map teardown. A pending bind still needs its eventual release handshake.
function M.clear_world(s)
    s.records = {}
    s.by_widget = {}
    s.by_component = {}
    s.count = 0
    s.choice = nil
    s.streak = 0
    s.reason = "world_cleared"
    if s.selected or s.pending then s.force_release = true end
end

-- Each row is a freshly revalidated native actor/component/widget triple and
-- two BOOLEAN facts. shown means *effective* source screen presentation,
-- NOT merely CanShow dispatch or a stored raw visibility enum. ready includes
-- current native action and input hint eligibility; exact acquisition belongs
-- to the host adapter, not to this policy.
--
-- A complete sweep is required: zero rows cannot prove that an unseen actor
-- is hidden, and two simultaneously shown actors must never be guessed by
-- distance, registration order or most-recent CanShow.
function M.observe(s, rows)
    if s.fault then return nil, s.fault end
    if type(rows) ~= "table" or #rows ~= s.count then
        return fail(s, "incomplete_visibility_snapshot")
    end
    local seen, visible, chosen, ready = {}, 0, nil, false
    for _,row in ipairs(rows) do
        if type(row) ~= "table" or not valid_id(row.actor)
            or not valid_id(row.component) or not valid_id(row.widget)
            or type(row.shown) ~= "boolean" or type(row.ready) ~= "boolean"
            or seen[row.actor] then
            return fail(s, "invalid_visibility_snapshot")
        end
        local rec = s.records[row.actor]
        if not rec or rec.component ~= row.component or rec.widget ~= row.widget then
            return fail(s, "stale_visibility_identity")
        end
        seen[row.actor] = true
        if row.shown then
            visible = visible + 1
            chosen = row.actor
            ready = row.ready
        end
    end
    local next_choice
    if visible == 1 and ready then next_choice = chosen end
    if next_choice and next_choice == s.choice then
        s.streak = math.min(s.streak + 1, 2)
    else
        s.choice = next_choice
        s.streak = next_choice and 1 or 0
    end
    if visible == 0 then s.reason = "no_native_prompt"
    elseif visible > 1 then s.reason = "ambiguous_native_prompts"
    elseif not ready then s.reason = "native_hint_not_ready"
    else s.reason = "unique_native_prompt" end
    if s.selected and s.selected ~= next_choice then s.force_release = true end
    return {reason = s.reason, visible = visible, eligible = next_choice, stable = s.streak}
end

local function command(s, kind, actor)
    s.serial = s.serial + 1
    s.pending = {kind = kind, actor = actor, ticket = s.serial}
    return {kind = kind, actor = actor, ticket = s.serial}
end

-- An integration must perform an action and then acknowledge it. This prevents
-- building a second World component before the first one's CLEANED handshake.
function M.next(s)
    if s.pending then return {kind = "wait", reason = "ack_pending"} end
    if s.selected and (s.force_release or s.fault
            or not s.records[s.selected] or s.choice ~= s.selected) then
        return command(s, "release", s.selected)
    end
    if s.fault then return {kind = "disabled", reason = s.fault} end
    if not s.selected and not s.force_release and s.choice
            and s.streak >= 2 and s.records[s.choice] then
        return command(s, "bind", s.choice)
    end
    return {kind = "none", reason = s.reason}
end

-- Acknowledge only after the owning World operation succeeded. Do NOT call
-- 'released' until native ownership was actually cleared.
function M.bound(s, ticket)
    local p = s.pending
    assert(p and p.kind == "bind" and p.ticket == ticket, "unexpected bind ack")
    s.selected = p.actor
    s.pending = nil
    if s.fault or not s.records[p.actor] or s.choice ~= p.actor then
        s.force_release = true
    end
    return not s.force_release
end

-- If creation failed or only partially completed, cleanup remains mandatory.
function M.bind_failed(s, ticket, why)
    local p = s.pending
    assert(p and p.kind == "bind" and p.ticket == ticket, "unexpected failed bind")
    fail(s, why or "bind_failed")
    s.selected = p.actor -- May refer to a partial allocation, requiring cleanup.
    s.pending = nil
    return M.next(s)
end

function M.released(s, ticket)
    local p = s.pending
    assert(p and p.kind == "release" and p.ticket == ticket
        and p.actor == s.selected, "unexpected release ack")
    s.selected = nil
    s.pending = nil
    s.force_release = false
    -- Never bind on the basis of a snapshot taken before releasing the owner.
    s.choice = nil
    s.streak = 0
    s.reason = s.fault and "disabled" or "need_fresh_visibility"
    return not s.fault
end

function M.error(s, reason)
    return fail(s, reason or "adapter_contract_failed")
end

function M.status(s)
    return {
        count = s.count, active = s.selected, pending = s.pending ~= nil,
        disabled = s.fault ~= nil, reason = s.fault or s.reason,
    }
end

return M
