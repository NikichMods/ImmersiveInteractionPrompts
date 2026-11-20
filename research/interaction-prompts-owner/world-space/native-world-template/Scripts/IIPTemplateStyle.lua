-- SPDX-License-Identifier: MPL-2.0
-- Visual adaptation of ORIGINAL World UWidgetComponent; native action/show/hide untouched.
local M={}
local SCALE,LIFT,RGB=.400,36,.35
local COMPONENT="/Script/Genesis.ExtendedWidgetComponent"
local TIP="/Game/MainContent/Template/UMG/TipHUD.TipHUD_C"
local function valid(o)return o~=nil and o:IsValid()end
local function path(o)return assert(o:GetFullName():match("^[^ ]+ (.+)$"))end
local function is(o,k)return valid(o) and valid(o:GetClass()) and path(o:GetClass())==k end
local function same(a,b)return valid(a) and valid(b) and a:GetAddress()==b:GetAddress()end
local function close(a,b,tol)return math.abs(a-b)<(tol or .001)end

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

local function child(tree,canvas,owned,k,name,y,w,h)
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
    slot:SetPosition({X=121.75,Y=y})
    slot:SetSize({X=w,Y=h})
    assert(same(o:GetParent(),canvas),"child parent unavailable")
    return o
end

function M.decorate(widget,resources)
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
    local ok,err=pcall(function()
        local label=child(tree,canvas,owned,"/Script/UMG.TextBlock","IIP_WQ_Aphes",-54.1484375,176,37)
        label:SetFont(stock.Font)
        assert(label.Font:GetStructAddress()~=stock.Font:GetStructAddress(),"FontInfo aliased")
        resources.font(label)
        label:SetText(FText("ACTION")) -- test lettering, NOT verified Aphes lore
        label.Font.Size=26
        label.Font.OutlineSettings.OutlineSize=1
        label.Font.OutlineSettings.OutlineColor={R=0,G=0,B=0,A=.75}
        label:SetFont(label.Font)
        label:SetJustification(1)
        label:SetColorAndOpacity({SpecifiedColor={R=.85,G=.85,B=.85,A=1},ColorUseRule=0})
        local divider=child(tree,canvas,owned,"/Script/UMG.Image","IIP_WQ_Divider",-27.19921875,142.375,17.796875)
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
    return true
end

function M.start(c,widget,resources,probe,log)
    assert(is(c,COMPONENT) and is(widget,TIP) and same(c:GetUserWidgetObject(),widget),
        "original component/widget link unavailable")
    M.geometry(c)
    log("STYLE_GEOMETRY","scale=.400 lift=36 world_z=true native_draw_unchanged=true")
    local before=probe.continuous_tick(c)
    log("STYLE_TICK",("before=%.3f after=0"):format(before))
    local decorated,reason=pcall(M.decorate,widget,resources)
    log(decorated and "STYLE_DECORATED" or "STYLE_DECORATION_REJECTED",
        decorated and "own_children=2" or ("reason=%q"):format(tostring(reason):sub(1,170)))
    local ok,base,live=pcall(probe.tint,c,nil,RGB,true)
    log(ok and "STYLE_TINT" or "STYLE_TINT_REJECTED",
        ok and ("rgb=.35 mid=%s"):format(live and "verified" or "pending")
        or ("reason=%q"):format(tostring(base):sub(1,170)))
    return {decorated=decorated,tint=ok and base or nil,tint_pending=ok and not live}
end

function M.can_show(c,widget,state,probe,log)
    if state.tint_pending then
        local ok,result=pcall(probe.verify_tint,c,state.tint,RGB)
        if not ok then
            state.tint_pending=false
            log("STYLE_TINT_UNVERIFIED",("reason=%q"):format(tostring(result):sub(1,170)))
        elseif result then
            state.tint_pending=false
            log("STYLE_TINT_VERIFIED","rgb=.35")
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
