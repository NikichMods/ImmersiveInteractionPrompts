-- SPDX-License-Identifier: MPL-2.0
-- Pure glue between the verified read-only interaction observer and
-- IIPWorldHandoff. Native callbacks only pass primitive facts; native
-- own-World operations must run later on a separate game-thread pump.
local M={}
function M.sink(handoff)
    assert(type(handoff)=="table","missing World handoff controller")
    for _,name in ipairs({"register","end_actor","map_pre","observe","stop","pump","status"})do
        assert(type(handoff[name])=="function","missing handoff function: "..name)
    end
    return {
        on_join=function(record)
            local ok,reason=handoff.register(record)
            assert(ok,reason or "handoff registry rejected native actor")
        end,
        on_end=function(actor)
            -- A previously pending-only actor may not be in the handoff registry.
            handoff.end_actor(actor)
        end,
        on_map=function()handoff.map_pre()end,
        on_snapshot=function(rows,complete)
            local observed,why=handoff.observe(rows,complete)
            assert(observed,why or "handoff snapshot rejected")
        end
    }
end
function M.pump(observer,handoff)
    assert(type(observer)=="table" and type(observer.status)=="function"
        and type(observer.stop)=="function","missing observer lifecycle")
    if not observer.status().active then handoff.stop("source_observer_stopped")end
    local result=handoff.pump()
    local status=handoff.status()
    if status.fault and observer.status().active then
        -- If World ownership cannot be proved, stop the read-only observer.
        -- Do not keep issuing new native actions on each EngineTick.
        observer.stop("world_handoff_fault")
    end
    return result
end
return M
