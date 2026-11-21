-- SPDX-License-Identifier: MPL-2.0
-- Visual adaptation of ORIGINAL World UWidgetComponent; native action/show/hide untouched.
local M={RGB=.50}
local SCALE,LIFT=.400,36
local COMPONENT="/Script/Genesis.ExtendedWidgetComponent"
local TIP="/Game/MainContent/Template/UMG/TipHUD.TipHUD_C"
local function valid(o)return o~=nil and o:IsValid()end
local function path(o)return assert(o:GetFullName():match("^[^ ]+ (.+)$"))end
local function is(o,k)return valid(o) and valid(o:GetClass()) and path(o:GetClass())==k end
local function same(a,b)return valid(a) and valid(b) and a:GetAddress()==b:GetAddress()end
local function close(a,b,tol)return math.abs(a-b)<(tol or .001)end
-- Authored words for the 18 verified InteractTipToText row names.
-- Aphes.ttf maps uppercase ASCII; these words are fictional.
local TOKENS={
    Climb="ORTHA",
    Restart="PALINO",
    Interact="NEMARO",
    Open="ANOKE",
    Talk="LETHO",
    Gossip="PSYRA",
    Knock="KROTA",
    Heal="IATHE",
    Insert="EMVORA",
    Remove="EKLON",
    Press="PIEZA",
    Take="LAVO",
    Break="THRAKO",
    Enter="EISORA",
    Check="SKERA",
    Activate="KINERA",
    Pray="EUKRA",
    UILoadTest="DOKIRA",
}
-- Fixed placements selected by native action tag at construction.
local PLACEMENT_X={Open=81,Take=70,Check=93,Talk=121.75,Interact=121.75}
local DEFAULT_X=80

function M.token_for(tag)
    return TOKENS[tag] or "ACTION"
end

function M.placement_x(tag)
    return PLACEMENT_X[tag] or DEFAULT_X
end

function M.refresh_action(state,tag,log)
    if not state.decorated or not TOKENS[tag] or tag==state.tag then return end
    if not state.header or not state.header_address then return end
    local label=StaticFindObject(state.header)
    if not is(label,"/Script/UMG.TextBlock")
        or label:GetAddress()~=state.header_address then return end
    label:SetText(FText(M.token_for(tag)))
    state.tag=tag
    log("STYLE_ACTION_UPDATED",("tag=%s token=%s"):format(tag,M.token_for(tag)))
end

function M.geometry(c)
    assert(is(c,COMPONENT) and c.Space==0 and c:GetCollisionEnabled()==0,"not original World")
    local o=c.RelativeScale3D
    local scale={X=o.X,Y=o.Y,Z=o.Z}
    local p=c:K2_GetComponentLocation()
    local pos={X=p.X,Y=p.Y,Z=p.Z}
    assert(scale.X>0 and scale.X<100 and scale.Y>0 and scale.Y<100
        and scale.Z>0 and scale.Z<100,"unsafe native scale")
    local ok,err=pcall(function()
        c:SetRelativeScale3D({X=scale.X*SCALE,Y=scale.Y*SCALE,Z=scale.Z*SCALE})
        c:K2_AddWorldOffset({X=0,Y=0,Z=LIFT},false,{},true)
        local n,a=c:K2_GetComponentLocation(),c.RelativeScale3D
        assert(close(n.Z,pos.Z+LIFT,.1) and close(a.X,scale.X*SCALE)
            and close(a.Y,scale.Y*SCALE) and close(a.Z,scale.Z*SCALE),"transform readback")
    end)
    if not ok then
        c:SetRelativeScale3D(scale)
        c:K2_SetWorldLocation(pos,false,{},true)
        error(err)
    end
    return scale,pos
end

function M.upright(c,yaw)
    assert(is(c,COMPONENT) and c.Space==0 and c:GetCollisionEnabled()==0,"not original World")
    local r=c:K2_GetComponentRotation()
    local original={Pitch=r.Pitch,Yaw=r.Yaw,Roll=r.Roll}
    for _,axis in ipairs({"Pitch","Yaw","Roll"}) do
        local angle=original[axis]
        assert(type(angle)=="number" and math.abs(angle)<=360,"invalid world rotation")
    end
    local function matches(actual,expected)
        for _,axis in ipairs({"Pitch","Yaw","Roll"}) do
            local delta=(actual[axis]-expected[axis]+180)%360-180
            if not close(delta,0,.1) then return false end
        end
        return true
    end
    local upright={Pitch=0,Yaw=yaw or original.Yaw,Roll=0}
    if matches(original,upright) then return false end

    local ok,err=pcall(function()
        c:K2_SetWorldRotation(upright,false,{},true)
        assert(matches(c:K2_GetComponentRotation(),upright),"world rotation readback")
    end)
    if not ok then
        if not matches(c:K2_GetComponentRotation(),original) then
            c:K2_SetWorldRotation(original,false,{},true)
            assert(matches(c:K2_GetComponentRotation(),original),"original world rotation could not be restored")
        end
        error(err)
    end
    return true
end

function M.face_camera(c,widget)
    local manager=widget:GetOwningPlayerCameraManager()
    if not valid(manager) then return false end
    local camera=manager:GetCameraLocation()
    local origin=c:K2_GetComponentLocation()
    local dx,dy=camera.X-origin.X,camera.Y-origin.Y
    local distance_squared=dx*dx+dy*dy
    if not (distance_squared>=1 and distance_squared<math.huge) then return false end
    -- The front of the stock widget plane is local +X.
    return M.upright(c,math.deg(math.atan(dy,dx)))
end

local function point(v)
    assert(math.abs(v.X)<math.huge and math.abs(v.Y)<math.huge
        and math.abs(v.Z)<math.huge,"invalid world point")
    return {X=v.X,Y=v.Y,Z=v.Z}
end

local function same_point(a,b)
    return close(a.X,b.X,.1) and close(a.Y,b.Y,.1) and close(a.Z,b.Z,.1)
end

local function place(c,position,yaw)
    assert(is(c,COMPONENT) and c.Space==0 and c:GetCollisionEnabled()==0,"not original World")
    local before=point(c:K2_GetComponentLocation())
    local moved=not same_point(before,position)
    local function set_location(expected)
        c:K2_SetWorldLocation(expected,false,{},true)
        assert(same_point(c:K2_GetComponentLocation(),expected),"door location readback")
    end
    local ok,result=pcall(function()
        if moved then set_location(position) end
        return M.upright(c,yaw)
    end)
    if not ok then
        if moved and not same_point(c:K2_GetComponentLocation(),before) then set_location(before) end
        error(result)
    end
    return moved or result
end

-- Closed slum grille only. The root plane is a static estimate. The 24 cm
-- trial offset needs visual verification against the actual bars on both sides.
function M.door_plane(c,widget,actor,state,tag)
    local prior=state.door_pose
    if tag~="Open" or actor.CurrentState:ToString()~="close" then
        if not prior then return false end
        local changed=place(c,prior.anchor,prior.yaw)
        state.door_pose=nil
        return changed
    end
    if c.bVisible~=true or (widget.RenderOpacity or 0)<=.01 then return false end

    local locator,root=actor.WidgetLocator,actor.RootComponent
    local front,rear=actor.front_CharacterAlign,actor.rear_CharacterAlign
    for _,part in ipairs({ "WidgetLocator", "RootComponent", "front_CharacterAlign", "rear_CharacterAlign" }) do
        local component=actor[part]
        assert(valid(component) and same(component:GetOwner(),actor),"door geometry owner mismatch")
    end
    assert(same(c:GetAttachParent(),locator) and same(locator:GetAttachParent(),root),
        "door locator attachment mismatch")
    local a,b=point(front:K2_GetComponentLocation()),point(rear:K2_GetComponentLocation())
    local dx,dy=a.X-b.X,a.Y-b.Y
    local length=math.sqrt(dx*dx+dy*dy)
    assert(length>100 and length<130 and math.abs(a.Z-b.Z)<2,"door alignment spacing changed")
    local nx,ny=dx/length,dy/length
    local plane=point(root:K2_GetComponentLocation())
    local function depth(p)
        return (p.X-plane.X)*nx+(p.Y-plane.Y)*ny
    end
    assert(depth(a)>40 and depth(b)<-40 and math.abs(depth(point(locator:K2_GetComponentLocation())))<2,
        "door plane reference mismatch")
    local pawn=widget:GetOwningPlayerPawn()
    if not valid(pawn) then return false end
    local player_depth=depth(point(pawn:K2_GetActorLocation()))
    if math.abs(player_depth)<8 then return false end
    local side=player_depth>0 and 1 or -1
    local anchor=prior and prior.anchor or point(c:K2_GetComponentLocation())
    local yaw=prior and prior.yaw or c:K2_GetComponentRotation().Yaw
    local offset=side*24-depth(anchor)
    local changed=place(c,{X=anchor.X+nx*offset,Y=anchor.Y+ny*offset,Z=anchor.Z},
        math.deg(math.atan(side*ny,side*nx)))
    if not prior then state.door_pose={anchor=anchor,yaw=yaw} end
    return changed,side
end

local function child(tree,canvas,owned,k,name,y,w,h,x)
    local cls=StaticFindObject(k)
    assert(valid(cls) and cls:type()=="UClass" and cls:GetFullName()=="Class "..k,"UMG class unavailable")
    assert(not valid(StaticFindObject(path(tree).."."..name)),"own child already exists")
    local o=StaticConstructObject(cls,tree,FName(name),EObjectFlags.RF_Transient)
    assert(is(o,k) and same(o:GetOuter(),tree),"transient child unavailable")
    owned[#owned+1]=o
    o:SetVisibility(1) -- Collapsed until configured
    local slot=canvas:AddChildToCanvas(o)
    assert(is(slot,"/Script/UMG.CanvasPanelSlot") and same(slot.Parent,canvas)
        and same(slot.Content,o),"canvas slot unavailable")
    slot:SetAutoSize(false)
    slot:SetAnchors({Minimum={X=0,Y=.5},Maximum={X=0,Y=.5}})
    slot:SetAlignment({X=.5,Y=.5})
    slot:SetPosition({X=x,Y=y})
    slot:SetSize({X=w,Y=h})
    assert(same(o:GetParent(),canvas),"child parent unavailable")
    return o
end

function M.decorate(widget,resources,tag)
    assert(is(widget,TIP),"not native TipHUD")
    local stock,tree=widget.TextBlock_89,widget.WidgetTree
    assert(is(stock,"/Script/UMG.TextBlock") and is(tree,"/Script/UMG.WidgetTree")
        and same(tree:GetOuter(),widget) and same(stock:GetOuter(),tree),"native TipHUD tree changed")
    local canvas=stock:GetParent()
    assert(is(canvas,"/Script/UMG.CanvasPanel") and same(canvas:GetOuter(),tree)
        and path(canvas):match("%.CanvasPanel_6$"),"native canvas changed")
    local hint=StaticFindObject(path(tree)..".RetainerBox_0")
    assert(is(hint,"/Script/UMG.RetainerBox") and same(hint:GetParent(),canvas),"native hint changed")
    local owned={}
    local x=M.placement_x(tag)
    local label
    local ok,err=pcall(function()
        label=child(tree,canvas,owned,"/Script/UMG.TextBlock","IIP_WQ_Aphes",-54.1484375,176,37,x)
        label:SetFont(stock.Font)
        assert(label.Font:GetStructAddress()~=stock.Font:GetStructAddress(),"FontInfo aliased")
        resources.font(label)
        label:SetText(FText(M.token_for(tag))) -- visual sample; NOT Aphes translation
        label.Font.Size=26
        label.Font.OutlineSettings.OutlineSize=1
        label.Font.OutlineSettings.OutlineColor={R=0,G=0,B=0,A=.75}
        label:SetFont(label.Font)
        label:SetJustification(1)
        label:SetColorAndOpacity({SpecifiedColor={R=.85,G=.85,B=.85,A=1},ColorUseRule=0})
        local divider=child(tree,canvas,owned,"/Script/UMG.Image","IIP_WQ_Divider",-27.19921875,142.375,17.796875,x)
        resources.ornament(divider,widget)
        divider:SetColorAndOpacity({R=.75,G=.75,B=.75,A=1})
        label:SetVisibility(3) -- HitTestInvisible, visible and noninteractive
        divider:SetVisibility(3)
    end)
    if not ok then
        for _,o in ipairs(owned) do
            o:SetVisibility(1)
            if same(o:GetParent(),canvas) then o:RemoveFromParent() end
        end
        error(err)
    end
    return {header=path(label),header_address=label:GetAddress(),
            x=x}
end

function M.start(c,widget,resources,probe,log,tag)
    assert(is(c,COMPONENT) and is(widget,TIP) and same(c:GetUserWidgetObject(),widget),
        "original component/widget link unavailable")
    M.geometry(c)
    log("STYLE_GEOMETRY","scale=.400 lift=36 world_z=true native_draw_unchanged=true")
    local upright_ok,changed=pcall(M.upright,c)
    log(upright_ok and "STYLE_ORIENTATION" or "STYLE_ORIENTATION_REJECTED",
        upright_ok and ("world_z=true yaw_preserved=true changed=%s"):format(tostring(changed))
        or ("reason=%q"):format(tostring(changed):sub(1,170)))
    local tick_ok,before=pcall(probe.continuous_tick,c)
    log(tick_ok and "STYLE_TICK" or "STYLE_TICK_REJECTED",
        tick_ok and ("before=%.3f after=0"):format(before)
        or ("reason=%q"):format(tostring(before):sub(1,170)))
    local decorated,info=pcall(M.decorate,widget,resources,tag)
    log(decorated and "STYLE_DECORATED" or "STYLE_DECORATION_REJECTED",
        decorated and ("own_children=2 tag=%s token=%s x=%.2f placement=fixed"):format(
            tostring(tag),M.token_for(tag),info.x)
            or ("reason=%q"):format(tostring(info):sub(1,170)))
    local ok,base,live=pcall(probe.tint,c,nil,M.RGB,true)
    log(ok and "STYLE_TINT" or "STYLE_TINT_REJECTED",
        ok and ("rgb=%.2f mid=%s"):format(M.RGB,live and "verified" or "pending")
        or ("reason=%q"):format(tostring(base):sub(1,170)))
    return {decorated=decorated,tint=ok and base or nil,tint_pending=ok and not live,
        header=decorated and info.header or nil,
        header_address=decorated and info.header_address or nil,tag=tag}
end

function M.can_show(c,widget,state,probe,log,tag)
    M.refresh_action(state,tag,log)
    if state.tint_pending then
        local ok,result=pcall(probe.verify_tint,c,state.tint,M.RGB)
        if not ok then
            state.tint_pending=false
            log("STYLE_TINT_UNVERIFIED",("reason=%q"):format(tostring(result):sub(1,170)))
        elseif result then
            state.tint_pending=false
            log("STYLE_TINT_VERIFIED",("rgb=%.2f"):format(M.RGB))
        end
    end
    local ok,before=pcall(probe.continuous_tick,c)
    if not ok then
        log("STYLE_CADENCE_REJECTED",("reason=%q"):format(tostring(before):sub(1,170)))
    elseif before>0 then
        log("STYLE_CADENCE",("source=CanShow before=%.3f after=0"):format(before))
    end
end
return M
