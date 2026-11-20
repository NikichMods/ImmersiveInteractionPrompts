-- SPDX-License-Identifier: MPL-2.0
-- Visual adaptation of ORIGINAL World UWidgetComponent; native action/show/hide untouched.
local M={}
local SCALE,LIFT,RGB=.400,36,.45
local COMPONENT="/Script/Genesis.ExtendedWidgetComponent"
local TIP="/Game/MainContent/Template/UMG/TipHUD.TipHUD_C"
local function valid(o)return o~=nil and o:IsValid()end
local function path(o)return assert(o:GetFullName():match("^[^ ]+ (.+)$"))end
local function is(o,k)return valid(o) and valid(o:GetClass()) and path(o:GetClass())==k end
local function same(a,b)return valid(a) and valid(b) and a:GetAddress()==b:GetAddress()end
local function close(a,b,tol)return math.abs(a-b)<(tol or .001)end
-- Provisional visual tokens only. Aphes font renders their glyphs;
-- these are NOT lore translations and the native localized action is untouched.
local TOKENS={Open="OPEN",Take="TAKE",Check="CHECK",Talk="TALK"}
-- One-shot safe placements for the known Russian test route if the host
-- has not measured its text by BeginPlay. Talk preserves the accepted baseline.
-- These are NOT measured widths or generic localization guarantees.
local FALLBACK_X={Open=81,Take=70,Check=93,Talk=121.75,Interact=121.75}
local DEFAULT_X=80
local CANVAS_SLOT="/Script/UMG.CanvasPanelSlot"

function M.token_for(tag)
    return TOKENS[tag] or "ACTION"
end

function M.center_for(stock,tag)
    local fallback=FALLBACK_X[tag] or DEFAULT_X
    -- The native text's final slot/desired width can be unavailable before
    -- the first Slate prepass. Do not wait or update the geometry after reveal.
    local ok,x=pcall(function()
        local slot=stock.Slot
        assert(is(slot,CANVAS_SLOT) and same(slot.Content,stock)
            and slot:GetAutoSize(),"original text slot unavailable")
        local raw=stock.Text:ToString()
        assert(type(raw)=="string" and #raw>0 and raw~="???"
            and not raw:match("^%?+$"),"placeholder or empty native text")
        local size,pos,alignment=stock:GetDesiredSize(),slot:GetPosition(),slot:GetAlignment()
        local anchors=slot:GetAnchors()
        assert(type(size.X)=="number" and size.X>=20 and size.X<=600
            and type(size.Y)=="number" and size.Y>0 and size.Y<=150
            and type(pos.X)=="number" and type(alignment.X)=="number"
            and alignment.X>=0 and alignment.X<=1
            and anchors.Minimum.X==anchors.Maximum.X
            and anchors.Minimum.X==0,"unready native layout")
        local center=pos.X+size.X*(.5-alignment.X)
        assert(center>=20 and center<=400,"measured center outside bounds")
        return center
    end)
    if ok then return x,"measured" end
    return fallback,"fallback"
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

function M.upright(c)
    assert(is(c,COMPONENT) and c.Space==0 and c:GetCollisionEnabled()==0,"not original World")
    local r=c:K2_GetComponentRotation()
    local original={Pitch=r.Pitch,Yaw=r.Yaw,Roll=r.Roll}
    for _,axis in ipairs({"Pitch","Yaw","Roll"}) do
        local angle=original[axis]
        assert(type(angle)=="number" and math.abs(angle)<=360,"invalid world rotation")
    end
    if close(original.Pitch,0,.1) and close(original.Roll,0,.1) then return false end

    local function matches(expected)
        local actual=c:K2_GetComponentRotation()
        for _,axis in ipairs({"Pitch","Yaw","Roll"}) do
            local delta=(actual[axis]-expected[axis]+180)%360-180
            if not close(delta,0,.1) then return false end
        end
        return true
    end
    local upright={Pitch=0,Yaw=original.Yaw,Roll=0}
    local ok,err=pcall(function()
        c:K2_SetWorldRotation(upright,false,{},true)
        assert(matches(upright),"world rotation readback")
    end)
    if not ok then
        if not matches(original) then
            c:K2_SetWorldRotation(original,false,{},true)
            assert(matches(original),"original world rotation could not be restored")
        end
        error(err)
    end
    return true
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
    local x,mode=M.center_for(stock,tag)
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
            center_x=x,center_mode=mode,tag=tag}
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
        decorated and ("own_children=2 tag=%s token=%s x=%.2f center=%s"):format(
            tostring(tag),M.token_for(tag),info.center_x,info.center_mode)
            or ("reason=%q"):format(tostring(info):sub(1,170)))
    local ok,base,live=pcall(probe.tint,c,nil,RGB,true)
    log(ok and "STYLE_TINT" or "STYLE_TINT_REJECTED",
        ok and ("rgb=.45 mid=%s"):format(live and "verified" or "pending")
        or ("reason=%q"):format(tostring(base):sub(1,170)))
    return {decorated=decorated,tint=ok and base or nil,tint_pending=ok and not live,
        header=decorated and info.header or nil,
        header_address=decorated and info.header_address or nil,tag=tag}
end

function M.can_show(c,widget,state,probe,log,tag)
    M.refresh_action(state,tag,log)
    if state.tint_pending then
        local ok,result=pcall(probe.verify_tint,c,state.tint,RGB)
        if not ok then
            state.tint_pending=false
            log("STYLE_TINT_UNVERIFIED",("reason=%q"):format(tostring(result):sub(1,170)))
        elseif result then
            state.tint_pending=false
            log("STYLE_TINT_VERIFIED","rgb=.45")
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
