# SPDX-License-Identifier: MPL-2.0
from lupa import LuaRuntime

from test_ui_child import ROOT


scripts = ROOT / "research/interaction-prompts-owner/world-space/native-world-quintus/Scripts"
lua = LuaRuntime()
assert lua.eval("load")((scripts / "main.lua").read_text(encoding="utf-8"))
lua.globals().probe = lua.execute((scripts / "IIPQuintusProbe.lua").read_text(encoding="utf-8"))
lua.execute("""
local function object(class,id)
    return {IsValid=function() return true end,GetAddress=function() return id end,
        GetClass=function() return {GetFullName=function() return "Class "..class end} end}
end
FName=function(n) return n end
local component, widget = object("Component",1), object("Widget",2)
local box = object("/Script/UMG.RetainerBox",3)
local mid = object("/Script/Engine.MaterialInstanceDynamic",4)
component.bVisible=true
widget.CanHoldPress=true
widget.WidgetTree={GetFullName=function() return "WidgetTree tree" end}
component.TintColorAndOpacity={R=.8,G=.6,B=.4,A=.7}
function component:GetMaterialInstance() return mid end
function component:SetTintColorAndOpacity(v) self.TintColorAndOpacity=v end
function mid:K2_GetVectorParameterValue(k)
    assert(k=="TintColorAndOpacity")
    return component.TintColorAndOpacity
end
local base=probe.tint(component,nil,.5)
assert(component.TintColorAndOpacity.R==.4 and component.TintColorAndOpacity.A==.7)
probe.tint(component,base,1)
assert(component.TintColorAndOpacity.R==.8)

local now, rate, t=0,0,0
function mid:K2_GetScalarParameterValue(k) assert(k=="t"); return t end
function box:GetEffectMaterial() return mid end
local function fn(p,f)
    return setmetatable({IsValid=function() return true end,type=function() return "UFunction" end,
        GetFullName=function() return "Function "..p end},
        {__call=function(_,...) return f(...) end})
end
local clock="/Script/Engine.GameplayStatics:GetRealTimeSeconds"
local timer="/Script/Genesis.GameGlobal:GetToDoInteractActionPressTimer"
local objects={
    ["tree.RetainerBox_0"]=box,
    ["/Script/Engine.Default__GameplayStatics"]=object("/Script/Engine.GameplayStatics",5),
    ["/Script/Genesis.Default__GameGlobal"]=object("/Script/Genesis.GameGlobal",6),
    [clock]=fn(clock,function(_,c) assert(c==component); return now end),
    [timer]=fn(timer,function(_,out) out.outTimerRate=rate; return rate*2 end),
}
StaticFindObject=function(p,...) assert(select("#",...)==0); return objects[p] end
local next_sample
ExecuteInGameThreadWithDelay=function(ms,cb) assert(ms==16); next_sample=cb end
local redraw,manual,interval=.15,true,.1
function component:GetRedrawTime() return redraw end
function component:GetManuallyRedraw() return manual end
function component:GetComponentTickInterval() return interval end
function component:GetTickWhenOffscreen() return false end
function component:IsComponentTickEnabled() return true end
function component:SetRedrawTime(v) redraw=v end
function component:SetManuallyRedraw(v) manual=v end
function component:SetComponentTickInterval(v) interval=v end
interval=.2
local cooldown_resets=0
function component:SetComponentTickIntervalAndCooldown(v)
    assert(v==0)
    cooldown_resets=cooldown_resets+1
    interval=v
end
assert(probe.continuous_tick(component)==.2 and interval==0)
assert(probe.continuous_tick(component)==0 and interval==0)
assert(cooldown_resets==1)
interval=.1
local no_op_tick={
    GetComponentTickInterval=function() return .2 end,
    SetComponentTickIntervalAndCooldown=function() end,
}
assert(not pcall(probe.continuous_tick,no_op_tick))
local lines={}
local function log(event,data) lines[#lines+1]=event.." "..data end
local function resolve() return component,widget end
probe.hold(resolve,log,false)
assert(redraw==.15 and manual and interval==.1)
assert(not pcall(probe.hold,resolve,log,true))
now=.5; rate=.6; t=.1; next_sample()
assert(lines[#lines]:find("rate=0.6000 t=0.1000",1,true))
now=3.5; next_sample()
assert(lines[#lines]:find("window_complete",1,true))
probe.hold(resolve,log,true)
assert(redraw==0 and not manual and interval==0)
component.bVisible=false
next_sample()
assert(redraw==.15 and manual and interval==.1)
assert(lines[#lines]:find("restore=complete",1,true))
component.bVisible=true
redraw=0; manual=false; interval=0
probe.hold(resolve,log,true)
assert(lines[#lines-1]:find("changed=false",1,true))
now=7.1; next_sample()
assert(lines[#lines]:find("restore=unneeded",1,true))
""")
print("Quintus probe: continuous tick, tint, hold sampling, redraw trial and restoration passed")
