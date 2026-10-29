-- SPDX-License-Identifier: MPL-2.0
-- Research only. One independent native Create/Slate/cleanup test. NOT INSTALLED.
local CLASS="/Game/MainContent/Template/UMG/Debug/PostionItemUMG_BP.PostionItemUMG_BP_C"
local HUD="/Game/MainContent/Template/UMG/HUD/HUDMainUMG_BP.HUDMainUMG_BP_C"
local phase,busy,deadline="armed",false,0
local own,tree_ref,root_ref,label_ref,foreign=nil,nil,nil,nil,nil
local function log(event,detail) print("IIP_USERWIDGET_HOST event="..event.." "..(detail or "").."\n") end
local function valid(o) return o~=nil and o:IsValid() end
local function path(o) return assert(o:GetFullName():match("^[^ ]+ (.+)$")) end
local function cls(o) return path(o:GetClass()) end
local function same(a,b) return valid(a) and valid(b) and a:GetAddress()==b:GetAddress() end
local function remember(o) return {path=path(o),address=o:GetAddress(),class=cls(o)} end
local function resolve(ref)
    if not ref then return nil end
    local o=StaticFindObject(ref.path)
    if not valid(o) then return nil end
    assert(o:GetAddress()==ref.address and cls(o)==ref.class,"identity changed")
    return o
end
local function snapshot(h)
    local t=h.WidgetTree;assert(valid(t) and same(t:GetOuter(),h),"foreign tree unavailable")
    local root=t.RootWidget
    assert(valid(root) and cls(root)=="/Script/UMG.CanvasPanel" and same(root:GetOuter(),t),"foreign root unavailable")
    return {hud=remember(h),tree=remember(t),root=remember(root),count=root:GetChildrenCount()}
end
local function preservation(before)
    local h=resolve(before.hud)
    if not valid(h) then log("PRESERVATION_UNVERIFIED","reason=original_HUD_gone");return end
    local now=snapshot(h)
    assert(now.tree.address==before.tree.address and now.root.address==before.root.address
        and now.count==before.count,"original HUD tree changed; never restore external state")
    log("ORIGINAL_TREE_UNCHANGED","root_children="..now.count.." original_writes=0")
end
local function gameplay_hud()
    local all=FindAllOf("HUDMainUMG_BP_C") or {}
    assert(type(all)=="table" and #all<=8,"unexpected HUD candidates")
    local found,count=nil,0
    for _,h in ipairs(all) do
        if valid(h) and cls(h)==HUD and h:IsInViewport() then
            local pawn=h:GetOwningPlayerPawn()
            local c=valid(pawn) and pawn:GetClass() or nil
            local gameplay=false
            for _=1,24 do
                if not valid(c) then break end
                if path(c)=="/Script/Genesis.GenesisCharacter" then gameplay=true;break end
                c=c:GetSuperStruct()
            end
            if gameplay then found,count=h,count+1 end
        end
    end
    assert(count==1,"need exactly one in-viewport gameplay HUD")
    return found
end
local function target_class()
    local c=StaticFindObject(CLASS)
    if not valid(c) then
        log("LOAD_BEGIN","exact_generated_class=true attempts_max=1")
        local asset,found,loaded=LoadAsset(CLASS) -- Exact cooked registry entry, game-thread-only pinned API.
        log("LOAD_RESULT","found="..tostring(found).." loaded="..tostring(loaded))
        assert(found==true and loaded==true and valid(asset),"class load unavailable")
        c=StaticFindObject(CLASS)
        assert(same(c,asset),"loaded asset differs from exact class lookup")
    end
    assert(c:type()=="UClass" and path(c)==CLASS,"unexpected generated class")
    local parent=c:GetSuperStruct()
    assert(valid(parent) and path(parent)=="/Script/UMG.UserWidget","unexpected native parent")
    return c
end
local function api(p,cdo_path)
    local fn=StaticFindObject(p);local cdo=StaticFindObject(cdo_path)
    assert(valid(fn) and fn:type()=="UFunction" and fn:GetFullName()=="Function "..p
        and valid(cdo),"static API NOT_LOADED")
    return fn,cdo
end
local function cleanup(reason)
    phase="stopped"
    local ok,err=pcall(function()
        local w=resolve(own)
        if w then
            -- Only the identified new instance is ever hidden/unbound, not other widgets of this class.
            w:SetVisibility(1)
            local label=resolve(label_ref)
            if label then
                assert(same(label:GetOuter(),resolve(tree_ref)),"own label outer changed")
                local parent=label:GetParent()
                if valid(parent) then
                    assert(same(parent,resolve(root_ref)),"own label reparented")
                    assert(parent:RemoveChild(label),"own label detach failed")
                end
                log("LABEL_REMOVED","own_only=true")
            end
            w:RemoveFromParent()
            -- Weak Slate liveness can outlast removal; preserve identities for explicit retry, never force GC.
            assert(not w:IsInViewport() and not valid(w:GetParent()),"own viewport release pending; retry cleanup")
            log("OWNERSHIP_RELEASED","viewport_ref=false gc_not_forced=true class_cache_not_unloaded=true")
        end
    end)
    if foreign then
        local checked,problem=pcall(preservation,foreign)
        if not checked then log("PRESERVATION_CHANGED",tostring(problem):sub(1,200)) end
    end
    if ok then
        own,tree_ref,root_ref,label_ref=nil,nil,nil,nil -- Primitive identities only; no wrappers/roots retained.
        log("CLEANED","reason="..reason.." own_viewport_remaining=0")
    else phase="cleanup_failed";log("CLEANUP_FAILED",tostring(err):sub(1,220)) end
end
local function guard(fn)
    if busy then return end
    busy=true
    local ok,err=pcall(fn)
    if not ok then log("FAILED",tostring(err):sub(1,240));cleanup("failure") end
    busy=false
end
local function validate_tree(w)
    local t=w.WidgetTree
    assert(valid(t) and cls(t)=="/Script/UMG.WidgetTree" and same(t:GetOuter(),w),"tree is not independently owned")
    local root=t.RootWidget
    assert(valid(root) and cls(root)=="/Script/UMG.CanvasPanel" and same(root:GetOuter(),t)
        and not valid(root:GetParent()) and root:GetChildrenCount()==1,"unexpected private root")
    local main=root:GetChildAt(0)
    assert(valid(main) and cls(main)=="/Script/UMG.CanvasPanel" and same(main:GetOuter(),t)
        and same(main:GetParent(),root) and main:GetChildrenCount()==2,"unexpected placeholder panel")
    local value,image=w.Value_Text,w.Bg_Image
    assert(valid(value) and cls(value)=="/Script/UMG.TextBlock" and valid(image)
        and cls(image)=="/Script/UMG.Image","missing reflected private leaves")
    local seen={}
    for _,o in ipairs({root,main,value,image}) do
        assert(not seen[o:GetAddress()] and same(o:GetOuter(),t),"shared private widget identity")
        seen[o:GetAddress()]=true
    end
    local children={}
    for i=0,1 do
        local child=main:GetChildAt(i)
        assert(valid(child) and not children[child:GetAddress()],"duplicate/invalid placeholder child")
        children[child:GetAddress()]=true
        assert((same(child,value) or same(child,image)) and same(child:GetParent(),main),"foreign placeholder child")
        assert(valid(child.Slot) and same(child.Slot.Parent,main) and same(child.Slot.Content,child),"leaf slot mismatch")
    end
    assert(children[value:GetAddress()] and children[image:GetAddress()],"private leaves missing from panel")
    assert(valid(main.Slot) and same(main.Slot.Parent,root) and same(main.Slot.Content,main),"main slot mismatch")
    return t,root,main,value
end
local function run()
    if phase~="armed" then cleanup("user");return end
    phase,deadline="attempted",os.time()+60 -- Never retry loading/Create even after failure.
    guard(function()
        ExecuteInGameThreadWithDelay(60000,function()if phase~="stopped" then cleanup("timeout") end end)
        local h=gameplay_hud();foreign=snapshot(h)
        local c=target_class()
        local previous=FindAllOf("PostionItemUMG_BP_C") or {}
        assert(type(previous)=="table" and #previous<=32,"too many existing host objects")
        local existing={}
        for _,o in ipairs(previous) do if valid(o) then existing[o:GetAddress()]=true end end
        local create,cdo=api("/Script/UMG.WidgetBlueprintLibrary:Create","/Script/UMG.Default__WidgetBlueprintLibrary")
        assert(cls(cdo)=="/Script/UMG.WidgetBlueprintLibrary","wrong library CDO")
        local w=create(cdo,h,c,nil)
        assert(valid(w) and cls(w)==CLASS and not existing[w:GetAddress()] and not same(w,h)
            and not w:HasAnyFlags(EObjectFlags.RF_ClassDefaultObject|EObjectFlags.RF_ArchetypeObject),"Create returned non-new/invalid host")
        own=remember(w) -- Now cleanup may act on this verified fresh instance even if its tree check fails.
        local t,root,main,value=validate_tree(w)
        tree_ref,root_ref=remember(t),remember(root)
        assert(t:GetAddress()~=foreign.tree.address and root:GetAddress()~=foreign.root.address,"original tree alias")
        log("INSTANCE_VALIDATED","private_tree=true root_children=1 existing_instances_unchanged=true")
        main:SetVisibility(1) -- Hide only this new instance's shipped placeholder.
        local text_class=StaticFindObject("/Script/UMG.TextBlock")
        assert(valid(text_class) and text_class:type()=="UClass","TextBlock NOT_LOADED")
        local name="IIP_HostLabel_"..tostring(os.time())
        assert(not valid(StaticFindObject(path(t).."."..name)),"own label name collision")
        local label=StaticConstructObject(text_class,t,FName(name),EObjectFlags.RF_Transient)
        assert(valid(label) and cls(label)=="/Script/UMG.TextBlock" and same(label:GetOuter(),t),"own label construction differs")
        label_ref=remember(label)
        label:SetVisibility(3);label:SetFont(value.Font)
        assert(label.Font:GetStructAddress()~=value.Font:GetStructAddress(),"FontInfo alias")
        label.Font.Size=22;label:SetFont(label.Font);label:SetJustification(1)
        label:SetText(FText("USERWIDGET HOST"))
        local slot=root:AddChildToCanvas(label)
        assert(valid(slot) and same(slot.Parent,root) and same(slot.Content,label),"own label slot differs")
        slot:SetAutoSize(false);slot:SetAnchors({Minimum={X=0.5,Y=0.5},Maximum={X=0.5,Y=0.5}})
        slot:SetAlignment({X=0.5,Y=0.5});slot:SetPosition({X=0,Y=0});slot:SetSize({X=300,Y=40})
        w:SetDesiredSizeInViewport({X=320,Y=100})
        w:SetAnchorsInViewport({Minimum={X=0.5,Y=0.5},Maximum={X=0.5,Y=0.5}})
        w:SetAlignmentInViewport({X=0.5,Y=0.5})
        assert(os.time()<deadline,"creation exceeded test window")
        w:AddToViewport(100)
        assert(w:IsInViewport(),"own viewport attachment unavailable")
        assert(w.Visibility==2,"expected first Construct self-Hidden was not observed")
        log("CONSTRUCT_HIDDEN","visibility=2 observed_after_first_build=true")
        w:SetVisibility(3)
        assert(w.Visibility==3 and label.Text:ToString()=="USERWIDGET HOST","own visibility/text readback differs")
        preservation(foreign)
        phase="visible"
        log("VISIBLE","label=USERWIDGET_HOST duration_max=60s original_ui_writes=0")
    end)
end
local ok,err=pcall(function()
    for _,k in ipairs({"StaticFindObject","LoadAsset","FindAllOf","StaticConstructObject","RegisterKeyBind",
        "IsKeyBindRegistered","ExecuteInGameThread","ExecuteInGameThreadWithDelay"}) do
        assert(type(_G[k])=="function","missing API: "..k)
    end
    assert(FName~=nil and FText~=nil and EngineTickAvailable==true and type(EGameThreadMethod)=="table"
        and type(EGameThreadMethod.EngineTick)=="number" and type(EObjectFlags)=="table" and type(EObjectFlags.RF_Transient)=="number"
        and type(EObjectFlags.RF_ClassDefaultObject)=="number" and type(EObjectFlags.RF_ArchetypeObject)=="number","missing constructors/dispatch/flags")
    local mods={ModifierKey.CONTROL,ModifierKey.ALT}
    assert(not IsKeyBindRegistered(Key.F6,mods),"CtrlAlt-F6 collision")
    RegisterKeyBind(Key.F6,mods,function()
        if phase=="stopped" then return end
        local queued,problem=pcall(ExecuteInGameThread,run,EGameThreadMethod.EngineTick)
        if not queued then log("DISPATCH_FAILED",tostring(problem):sub(1,180)) end
    end)
end)
if ok then log("ARMED","key=CtrlAlt-F6 one_create_max=true one_load_max=true")
else phase="stopped";log("UNAVAILABLE",tostring(err):sub(1,220)) end
