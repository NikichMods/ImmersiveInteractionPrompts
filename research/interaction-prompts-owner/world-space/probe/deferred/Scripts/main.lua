-- SPDX-License-Identifier: MPL-2.0
-- Research only. Proven binding + one owned World renderer. Never installed automatically.
local World=require("IIPWorldChild")
local BASE="/Game/MainContent/Template/BaseBlueprint/BaseGameEventObject_BP.BaseGameEventObject_BP_C"
local WIDGET="/Game/MainContent/Template/UMG/TipHUD.TipHUD_C"
local COMPONENT="/Script/Genesis.ExtendedWidgetComponent"
local BEGIN=BASE..":ReceiveBeginPlay"
local SHOW=WIDGET..":CanShow"
local phase,deadline="armed",0
local hooks,candidates,seen={}, {}, {}
local target,previous=nil,nil
local final_result=nil
local acquiring=false
local cleanup_queued=false
local cancel_requested=false
local dispatch
local count={init=0,open=0,not_ready=0,ready=0,show=0,visible=0,unmatched=0,match=0,poses=0}
local checkpoints=0
local function log(e,s) print("IIP_WORLD_V2_BIND event="..e.." "..(s or "").."\n") end
local function valid(o) return o~=nil and o:IsValid() end
local function instance(o)
    return valid(o) and not o:HasAnyFlags(EObjectFlags.RF_ClassDefaultObject|EObjectFlags.RF_ArchetypeObject)
end
local function path(o) return assert(o:GetFullName():match("^[^ ]+ (.+)$")) end
local function cls(o) return path(o:GetClass()) end
local function same(a,b) return valid(a) and valid(b) and a:GetAddress()==b:GetAddress() end
local function ref(o) return {path=path(o),class=cls(o),address=o:GetAddress()} end
local function key(r) return r.path.."|"..r.class.."|"..r.address end
local function matches(o,r) return valid(o) and path(o)==r.path and cls(o)==r.class and o:GetAddress()==r.address end
local function resolve(r)
    local o=StaticFindObject(r.path)
    assert(matches(o,r),"IDENTITY: missing/replaced "..r.path)
    return o
end
local function derives(o,base)
    local c=o:GetClass()
    for _=1,32 do
        if not valid(c) then return false end
        if path(c)==base then return true end
        c=c:GetSuperStruct()
    end
    error("CONTRACT: ancestry bound")
end
local function function_ready(p)
    local f=StaticFindObject(p)
    assert(valid(f),"NOT_LOADED: "..p)
    assert(f:type()=="UFunction" and f:GetFullName()=="Function "..p
        and (f:GetFunctionFlags()&0x400)==0,"CONTRACT: expected exact non-native function")
end
local function release(p)
    local ids=hooks[p]
    if not ids then return end
    local ok,err=pcall(UnregisterHook,p,ids[1],ids[2])
    if ok then hooks[p]=nil
    else log("UNREGISTER_PENDING",tostring(err):sub(1,180)) end
end
local function close_acquisition(reason)
    if not acquiring then return end
    acquiring=false;seen={} -- Freeze only the already checked pairs; no further initialization reads.
    release(BEGIN)
    log("ACQUISITION_CLOSED","reason="..reason.." init="..count.init
        .." retained="..#candidates.." selection_continues=true deadline_unchanged=true")
end
local function remaining() local n=0;for _ in pairs(hooks)do n=n+1 end;return n end
local function result()
    if count.match>0 then return count.poses>0 and "MATCHED" or "MATCH_WITHOUT_POSE" end
    if count.init==0 then return "NO_BEGINPLAY" end
    if count.open==0 then return "NO_OPEN_CANDIDATE" end
    if count.ready==0 then return "NO_READY_WIDGET" end
    if count.show==0 then return "NO_CANSHOW" end
    if count.visible==0 then return "NO_VISIBLE_OPEN" end
    return "NO_MATCH"
end
local function stop(reason,outcome)
    if phase=="stopped" and remaining()==0 and not World.pending() then return end
    final_result=final_result or outcome or result() -- Cleanup retry must not erase the original failure.
    phase="stopped" -- Before attempting removal, including when metadata is temporarily absent.
    acquiring=false
    candidates,seen,target,previous={}, {}, nil,nil
    release(BEGIN);release(SHOW)
    if World.pending() and not cleanup_queued then
        cleanup_queued=true
        local ok,err=pcall(ExecuteInGameThread,function()
            cleanup_queued=false
            local cleaned,problem=pcall(World.cleanup,reason)
            if not cleaned then log("CLEANUP_PENDING",tostring(problem):sub(1,180)) end
        end,EGameThreadMethod.EngineTick)
        if not ok then cleanup_queued=false;log("CLEANUP_DISPATCH_FAILED",tostring(err):sub(1,180)) end
    end
    log("STOP","reason="..reason.." result="..final_result
        .." init="..count.init.." open="..count.open.." not_ready="..count.not_ready.." ready="..count.ready
        .." show="..count.show.." visible_open="..count.visible.." unmatched="..count.unmatched
        .." matches="..count.match.." poses="..count.poses.." hooks_remaining="..remaining()
        .." cleanup_queued="..tostring(cleanup_queued))
end
local function guard(fn)
    local ok,err=pcall(fn)
    if not ok then
        local message=tostring(err)
        local outcome=message:find("IDENTITY:",1,true) and "IDENTITY_ERROR"
            or (message:find("NOT_LOADED:",1,true) and "NOT_LOADED" or "CONTRACT_ERROR")
        log("FAILED","kind="..outcome.." detail="..message:sub(1,220));stop("failure",outcome)
    end
end
local function active()
    if phase~="waiting" and phase~="pending" and phase~="creating" and phase~="bound" then return false end
    if os.time()>=deadline then stop("timeout");return false end
    return true
end
local function relations(actor,c,w)
    assert(instance(actor) and derives(actor,BASE),"IDENTITY: wrong actor base/default")
    assert(instance(c) and cls(c)==COMPONENT and same(actor.ExtendedWidget,c)
        and same(c:GetOwner(),actor),"IDENTITY: actor/component reciprocal link")
    local arg=actor.TipHUDArgument
    assert(valid(arg) and cls(arg)=="/Script/Genesis.TipHUDArgumentComponent"
        and same(arg:GetOwner(),actor),"IDENTITY: argument owner")
    assert(arg.msgTag:ToString()=="Open" and arg.ActionName==25,"IDENTITY: Open/Interact changed")
    assert(instance(w) and cls(w)==WIDGET and same(c:GetWidget(),w)
        and same(c:GetUserWidgetObject(),w) and same(c.Widget,w),"IDENTITY: widget storage/getters")
    assert(not valid(c.NewUserWidget) or same(c.NewUserWidget,w),"IDENTITY: NewUserWidget differs")
end
local function eligible(w)
    assert(valid(w) and cls(w)==WIDGET,"CONTRACT: CanShow context")
    local b=w.TextBlock_89
    assert(valid(b) and cls(b)=="/Script/UMG.TextBlock","CONTRACT: stock TextBlock")
    return (w.Visibility==0 or w.Visibility==3 or w.Visibility==4) and w.RenderOpacity>0
        and w.bIsEnabled==true and b.Visibility~=1 and b.Visibility~=2 and b.RenderOpacity>0
        and b.Text:ToString()=="Открыть"
end
local function scalar(n)
    assert(type(n)=="number" and n==n and n~=math.huge and n~=-math.huge,"CONTRACT: non-finite pose")
    return string.format("%.9g",n)
end
local function vector(v) return scalar(v.X)..","..scalar(v.Y)..","..scalar(v.Z) end
local function pose(reason)
    if not active() or phase~="bound" then return end
    local actor,c,w=resolve(target.actor),resolve(target.component),resolve(target.widget)
    relations(actor,c,w)
    if not eligible(w) or c.bVisible~=true or c.bAddedToScreen~=true then stop("target_not_visible");return end
    assert(c:GetWidgetSpace()==1,"CONTRACT: expected stock Screen component")
    local loc=vector(c:K2_GetComponentLocation())
    local r=c:K2_GetComponentRotation();local rot=scalar(r.Pitch)..","..scalar(r.Yaw)..","..scalar(r.Roll)
    local scale=vector(c:K2_GetComponentScale());local origin=vector(actor:K2_GetActorLocation())
    local current=loc.."|"..rot.."|"..scale.."|"..origin
    count.poses=count.poses+1
    log("POSE","n="..count.poses.." reason="..reason.." changed="..tostring(previous~=nil and previous~=current)
        .." component_world="..loc.." rotation_pyr="..rot.." scale="..scale.." actor_world="..origin)
    previous=current
    World.sample(reason)
    if count.poses>=4 then stop("pose_budget") end
end
local function acquire(context,...)
    if phase~="waiting" or not acquiring then return end
    local extra=select("#",...)
    guard(function()
        if not active() then return end
        count.init=count.init+1
        if count.init>=128 then close_acquisition("init_budget");return end
        assert(extra==0,"CONTRACT: ReceiveBeginPlay inputs")
        local actor=context:get()
        assert(instance(actor) and derives(actor,BASE),"CONTRACT: BeginPlay actor context/default")
        local arg=actor.TipHUDArgument
        assert(valid(arg) and cls(arg)=="/Script/Genesis.TipHUDArgumentComponent"
            and same(arg:GetOwner(),actor),"IDENTITY: initial argument owner")
        if arg.msgTag:ToString()~="Open" or arg.ActionName~=25 then return end
        local actor_ref=ref(actor);local actor_key=key(actor_ref)
        if seen[actor_key] then return end -- No automatic retry, even after NOT_READY.
        if count.open>=8 then stop("candidate_budget");return end
        seen[actor_key]=true;count.open=count.open+1
        local c=actor.ExtendedWidget
        assert(valid(c) and cls(c)==COMPONENT and same(c:GetOwner(),actor),"IDENTITY: initial component owner")
        local w=c:GetUserWidgetObject()
        if not valid(w) then
            count.not_ready=count.not_ready+1
            log("NOT_READY","actor="..string.format("%q",actor_ref.path).." reason=null_widget no_retry=true")
            return
        end
        relations(actor,c,w)
        candidates[#candidates+1]={actor=actor_ref,component=ref(c),widget=ref(w)}
        count.ready=count.ready+1
        log("ACQUIRED","n="..count.ready.." actor="..string.format("%q",actor_ref.path)
            .." component="..string.format("%q",path(c)).." widget="..string.format("%q",path(w)))
    end)
    -- Always nil: never propagate guard/pcall result into the script function.
end
local function select_widget(context,...)
    if phase~="waiting" and phase~="bound" then return end
    local extra=select("#",...)
    guard(function()
        if not active() then return end
        count.show=count.show+1
        if count.show>=4096 then stop("show_budget");return end
        assert(extra==0,"CONTRACT: CanShow inputs")
        local w=context:get()
        if phase=="bound" then
            if not matches(w,target.widget) then return end
            -- Bound UI state only; transforms remain manual after the first snapshot.
            local actor,c=resolve(target.actor),resolve(target.component)
            relations(actor,c,w)
            World.validate()
            if not eligible(w) or c.bVisible~=true or c.bAddedToScreen~=true then stop("target_not_visible") end
            return
        end
        if not eligible(w) then return end
        count.visible=count.visible+1
        local found,n=nil,0
        for _,candidate in ipairs(candidates)do
            if matches(w,candidate.widget) then found,n=candidate,n+1 end
        end
        if n==0 then count.unmatched=count.unmatched+1;return end
        assert(n==1,"IDENTITY: ambiguous widget join")
        local actor,c,saved=resolve(found.actor),resolve(found.component),resolve(found.widget)
        assert(same(w,saved),"IDENTITY: callback widget differs")
        relations(actor,c,w)
        if c.bVisible~=true or c.bAddedToScreen~=true then count.unmatched=count.unmatched+1;return end
        assert(c:GetWidgetSpace()==1,"CONTRACT: selected component is not Screen")
        target=found;candidates,seen={}, {};phase="pending";count.match=1
        target.tree=ref(w.WidgetTree);target.text=ref(w.TextBlock_89);target.root=ref(actor.RootComponent)
        if acquiring then acquiring=false;release(BEGIN) end -- Already closed acquisition is never restarted.
        log("MATCH","reciprocal=true actor="..string.format("%q",path(actor)).." actor_class="..string.format("%q",cls(actor))
            .." component="..string.format("%q",path(c)).." widget="..string.format("%q",path(w))
            .." actor_address="..actor:GetAddress().." component_address="..c:GetAddress().." widget_address="..w:GetAddress())
        local selected=target -- Primitive identities only; no UObject/callback context captured.
        dispatch(function()
            if phase~="pending" or target~=selected or cancel_requested or not active() then return end
            log("CREATE_DISPATCHED","executor=EngineTick fresh_identity_check=true")
            local a,component,widget=resolve(selected.actor),resolve(selected.component),resolve(selected.widget)
            assert(World.target_alive(a,component,widget),"IDENTITY: target pending kill before creation")
            relations(a,component,widget)
            assert(same(widget.WidgetTree,resolve(selected.tree)) and same(widget.TextBlock_89,resolve(selected.text))
                and same(a.RootComponent,resolve(selected.root)),"IDENTITY: UI/tree/root changed before creation")
            assert(eligible(widget) and component.bVisible==true and component.bAddedToScreen==true
                and component:GetWidgetSpace()==1,"CONTRACT: target no longer visible Screen Open")
            phase="creating" -- Reentrant BeginPlay/CanShow cannot mutate orchestration during native work.
            World.create(a,component,widget,function(reason)guard(function()stop(reason)end)end)
            phase="bound"
            pose("match")
        end)
        log("CREATE_QUEUED","executor=EngineTick callback_returns_before_creation=true")
    end)
    -- No return override, including failure/stop/duplicate/unmatched paths.
end
local function register(p,callback)
    local a,b=RegisterHook(p,callback) -- One callback: pinned script dispatch is already post.
    hooks[p]={a,b}
    assert(type(a)=="number" and a>0 and a==b,"CONTRACT: expected equal script hook IDs")
    log("REGISTERED","path="..p.." id="..a.." phase=script_post")
end
local function control()
    if phase~="armed" and not active() then return end
    if phase=="armed" then
        phase,deadline="preparing",os.time()+120 -- One attempt. Loading time is included.
        World.prepare() -- Explicit EngineTick control before installing either script callback.
        assert(os.time()<deadline,"preparation exceeded observation deadline")
        phase="waiting"
        function_ready(BEGIN);function_ready(SHOW)
        acquiring=true
        register(BEGIN,acquire);register(SHOW,select_widget)
        ExecuteInGameThreadWithDelay(120000,function()if phase~="stopped" then stop("timeout")end end)
        log("WAITING","reload_manually_once=true candidates_max=8 init_max=128 show_max=4096 poses_max=4 duration_max=120s")
    elseif phase=="bound" then pose("user")
    elseif phase=="waiting" and checkpoints<2 then
        checkpoints=checkpoints+1
        -- Same names may resolve to new UFunctions after reload; no registration wrappers/addresses retained.
        function_ready(BEGIN);function_ready(SHOW)
        log("CHECKPOINT","metadata_loaded=true init="..count.init.." ready="..count.ready.." show="..count.show)
    end
end
dispatch=function(fn)
    local ok,err=pcall(ExecuteInGameThread,function()guard(fn)end,EGameThreadMethod.EngineTick)
    if not ok then
        phase="stopped";candidates,seen,target,previous={}, {}, nil,nil
        acquiring=false
        final_result=final_result or "DISPATCH_FAILED"
        log("DISPATCH_FAILED","hooks_inert=true explicit_stop_or_exit_required=true "..tostring(err):sub(1,160))
    end
end
local ok,err=pcall(function()
    for _,name in ipairs({"StaticFindObject","RegisterHook","UnregisterHook","RegisterKeyBind","IsKeyBindRegistered",
        "ExecuteInGameThread","ExecuteInGameThreadWithDelay"})do assert(type(_G[name])=="function","missing API: "..name)end
    assert(EngineTickAvailable==true and type(EGameThreadMethod)=="table"
        and type(EGameThreadMethod.EngineTick)=="number","EngineTick unavailable")
    assert(type(EObjectFlags)=="table" and type(EObjectFlags.RF_ClassDefaultObject)=="number"
        and type(EObjectFlags.RF_ArchetypeObject)=="number","object flags unavailable")
    local mods={ModifierKey.CONTROL,ModifierKey.ALT}
    assert(not IsKeyBindRegistered(Key.F8,mods) and not IsKeyBindRegistered(Key.F7,mods),"control key collision")
    RegisterKeyBind(Key.F8,mods,function()if phase~="stopped" then dispatch(control)end end)
    RegisterKeyBind(Key.F7,mods,function()
        cancel_requested=true -- Lua intent only; cancels queued creation before engine dispatch.
        if phase~="stopped" or remaining()>0 or World.pending() then dispatch(function()stop("user")end)end
    end)
end)
if ok then log("ARMED","CtrlAltF8=start_or_pose CtrlAltF7=stop no_automatic_reload=true")
else phase="stopped";log("UNAVAILABLE",tostring(err):sub(1,200))end
