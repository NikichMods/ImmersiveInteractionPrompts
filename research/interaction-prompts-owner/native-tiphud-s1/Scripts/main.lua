-- SPDX-License-Identifier: MPL-2.0
-- SOURCE-ONLY S1 research candidate. NOT INSTALLED. NO production acceptance.
-- Add two own visual children to compatible native TipHUD_C instances.
-- Existing localized action, native hint, selection, CanShow and show/hide remain native.
local CLASS = "/Game/MainContent/Template/UMG/TipHUD.TipHUD_C"
local HOOK = CLASS .. ":CanShow"
local FONT = "/Script/Engine.Font"
local DONOR = "/Game/Fonts/EBGaramond-SemiBold_Font.EBGaramond-SemiBold_Font"
local Layout = require("IIPS1Layout")
-- The one-merchant research payload explicitly enables this at assembly.
local TALK_TEMPLATE = false
local NPC = "/Game/MainContent/Template/BaseBlueprint/NPCInteract_Bp.NPCInteract_Bp_C"
local COMPONENT = "/Script/Genesis.ExtendedWidgetComponent"
local ARGUMENT = "/Script/Genesis.TipHUDArgumentComponent"
local MERCHANT_LEVEL = "/Game/MainContent/Maps/sublevel_plot/1-1/1-1_plot_slumB1_main1"
-- Final layout from the observed Russian Talk baseline, in widget units.
local TALK_LAYOUT = {
    key="merchant_talk_fixed", upper_size=26,
    upper={x=121.75,y=-54.1484375,width=176,height=37},
    divider={x=121.75,y=-27.19921875,width=142.375,height=17.796875}
}
local prepared_talk
local ttf_filename, png_filename
local resource_serial = 0
local shared = {font=nil, texture=nil, import_attempted=false}
local entries, order, next_id = {}, {}, 0
local MAX_WIDGETS = 64 -- Bound own resources, not supported native interactions.
local stopped, busy, cleanup_failed = false, false, false
-- Research-only, bounded timing markers. UE4SS log wall-clock timestamps give
-- intervals between these milestones, NOT native/GPU first-pixel timestamps.
local TRACE_LIMIT, TRACE_TRANSITIONS = 64, 5
local trace_widgets, trace_count = {}, 0
local function log(event, details)
    print("IIP_S1 event=" .. event .. " " .. (details or "") .. "\n")
end
local function valid(o) return o ~= nil and o:IsValid() end
local function path(o) return assert(o:GetFullName():match("^[^ ]+ (.+)$")) end
local function cls(o) return path(o:GetClass()) end
local function same(a,b) return valid(a) and valid(b) and a:GetAddress() == b:GetAddress() end
local function remember(o)
    return {path=path(o), address=o:GetAddress(), class=cls(o)}
end
local function resolve(ref)
    if not ref then return nil end
    local o=StaticFindObject(ref.path)
    if not valid(o) then return nil end
    assert(o:GetAddress()==ref.address and cls(o)==ref.class, "identity replaced: "..ref.path)
    return o
end


local function address(n)
    assert(math.type(n) == "integer" and n > 0, "address unavailable")
    return n
end
local function class(o) return o:GetClass():GetFullName() end
local function structure(o, name)
    assert(valid(o) and o:type() == "UScriptStruct"
        and o:GetFullName() == "ScriptStruct /Script/SlateCore." .. name, "unexpected " .. name)
    return address(o:GetStructAddress()) -- Native storage, not Lua wrapper/metadata identity.
end
local function array(o, count)
    assert(valid(o) and o:type() == "TArray", "expected TArray")
    assert(o:GetArrayNum() == count, "unexpected array count") -- Before ANY indexed read.
    local max = o:GetArrayMax()
    assert(math.type(max) == "integer" and max >= count and max <= 256, "unexpected array capacity")
    return address(o:GetArrayAddress()), count > 0 and address(o:GetArrayDataAddress()) or 0
end
local function snapshot(o)
    assert(valid(o) and class(o) == "Class " .. FONT, "expected UFont")
    assert(o.FontCacheType == 1, "expected Runtime cache") -- Installed EFontCacheType.
    local composite, state = o.CompositeFont, {object=address(o:GetAddress())}
    state.composite = structure(composite,"CompositeFont")
    local typeface = composite.DefaultTypeface
    state.typeface = structure(typeface,"Typeface")
    local fonts = typeface.Fonts
    state.array, state.data = array(fonts,1)
    -- Pin the first native array element to its buffer; never probe until count==1.
    local entry = fonts[1]
    state.entry = structure(entry,"TypefaceEntry")
    assert(state.entry == state.data, "entry is not native first-element storage")
    assert(entry.Name:ToString() == "Default", "unexpected typeface name")
    local data = entry.Font
    state.font_data = structure(data,"FontData")
    local face = data.FontFaceAsset
    if valid(face) then assert(class(face) == "Class /Script/Engine.FontFace", "expected FontFace") end
    state.face = valid(face) and address(face:GetAddress()) or 0 -- Shared face before configuration; nil only on the private copy.
    state.filename = data.FontFilename:ToString()
    assert(type(state.filename) == "string" and #state.filename <= 1024, "unexpected filename")
    state.hinting, state.loading, state.subface = data.Hinting, data.LoadingPolicy, data.SubFaceIndex
    assert(math.type(state.hinting) == "integer" and state.hinting >= 0 and state.hinting <= 4
        and math.type(state.loading) == "integer" and state.loading >= 0 and state.loading <= 2
        and state.subface == 0, "unexpected FontData values")
    local fallback = composite.FallbackTypeface
    state.fallback = structure(fallback,"CompositeFallbackFont")
    state.fallback_typeface = structure(fallback.Typeface,"Typeface")
    state.fallback_array = array(fallback.Typeface.Fonts,0) -- No index into an empty array.
    state.subtypes = array(composite.SubTypefaces,0)
    return state,data
end
local function equal(a,b,keys)
    for _,key in ipairs(keys) do assert(a[key] == b[key], "mismatch: " .. key) end
end
local STORAGE = {"composite","typeface","array","data","entry","font_data",
                 "fallback","fallback_typeface","fallback_array","subtypes"}
local VALUES = {"face","filename","hinting","loading","subface"}

local function check_file()
    local f = assert(io.open(ttf_filename,"rb"), "local TTF unavailable")
    local ok,err = pcall(function()
        assert(f:seek("end") == 13920, "TTF size differs from retained Aphes")
        f:seek("set",0)
        assert(f:read(4) == "\0\1\0\0", "expected TrueType sfnt header")
    end)
    f:close(); assert(ok,err) -- Exact SHA256 must also be checked during future authorized installation.
end
local function configure_font(label)
    check_file()
    local donor = StaticFindObject(DONOR)
    if not valid(donor) then log("NOT_LOADED","donor=true"); error("donor NOT_LOADED; no forced load") end
    assert(donor:GetFullName() == "Font " .. DONOR, "donor identity changed")
    local before = snapshot(donor)
    assert(before.face > 0, "donor has no FontFace")
    local copy
    local ok,err = pcall(function()
        local font_class = StaticFindObject(FONT)
        assert(valid(font_class) and font_class:type() == "UClass"
            and font_class:GetFullName() == "Class " .. FONT, "Font class NOT_LOADED")
        local font_outer = donor:GetOuter() -- Same resident-package Outer contract as the completed creation probe.
        assert(valid(font_outer) and class(font_outer) == "Class /Script/CoreUObject.Package", "font package unavailable")
        resource_serial = resource_serial + 1
        local font_name = "IIP_S1_Font_" .. tostring(os.time()) .. "_" .. tostring(resource_serial)
        local copy_path = path(font_outer) .. "." .. font_name
        assert(not valid(StaticFindObject(copy_path)), "private font name collision")
        copy = StaticConstructObject(font_class,font_outer,FName(font_name),EObjectFlags.RF_Transient,
                                     0,false,false,donor)
        assert(valid(copy) and not same(copy,donor) and copy:GetFullName() == "Font " .. copy_path,
               "private font construction failed")
        assert(same(copy:GetOuter(),font_outer) and copy:HasAnyFlags(EObjectFlags.RF_Transient), "private font ownership differs")
        local initial,data = snapshot(copy)
        equal(before,initial,VALUES)
        for _,key in ipairs(STORAGE) do assert(before[key] ~= initial[key], "storage alias before write: " .. key) end
        -- Allocation-specific write guard, reusing completed storage evidence; not a new storage experiment.
        log("FONT_WRITE_BEGIN","own_copy_only=true")
        data.FontFaceAsset = nil
        data.FontFilename = ttf_filename -- Lua string branch: owning native FString assignment, not userdata SetCharArray.
        data.LoadingPolicy = 0 -- installed LazyLoad
        data.Hinting = 0 -- installed Default
        data.SubFaceIndex = 0
        local configured = snapshot(copy)
        equal(initial,configured,STORAGE)
        assert(configured.face == 0 and configured.filename == ttf_filename
            and configured.loading == 0 and configured.hinting == 0 and configured.subface == 0, "FontData setter readback differs")
        log("FONT_CONFIGURED","face_asset=nil filename_readback=true policy=LazyLoad")
        -- Own native-initialized FontInfo; do not fabricate a struct or alter the original TextBlock's FontInfo.
        label.Font.FontObject = copy
        label.Font.TypefaceFontName = FName("Default")
        label:SetFont(label.Font)
        assert(same(label.Font.FontObject,copy) and label.Font.TypefaceFontName:ToString() == "Default", "font bind readback differs")
        log("FONT_BOUND","reference=own_TextBlock.FontObject")
    end)
    local unchanged,problem = pcall(function()
        local current = snapshot(donor)
        equal(before,current,{"object"}); equal(before,current,STORAGE); equal(before,current,VALUES)
    end)
    log(unchanged and "DONOR_UNCHANGED" or "DONOR_CHECK_FAILED","after_setter_attempt=true")
    assert(unchanged,problem); assert(ok,err)
    return remember(copy) -- Primitive identity only; actual root is the owned TextBlock's FontObject property.
end

local function make(class, tree, prefix, role, record)
    next_id = next_id + 1
    local name = prefix .. tostring(next_id)
    assert(not valid(StaticFindObject(path(tree).."."..name)), "own widget name collision")
    local o=StaticConstructObject(class,tree,FName(name),EObjectFlags.RF_Transient)
    assert(valid(o) and same(o:GetOuter(),tree), "own construction failed")
    local ref=remember(o)
    ref.role=role
    record.owned[#record.owned+1]=ref
    o:SetVisibility(1) -- Collapsed until fully configured.
    return o
end
local function place(canvas, item, layout)
    local slot=canvas:AddChildToCanvas(item)
    assert(valid(slot) and cls(slot)=="/Script/UMG.CanvasPanelSlot"
        and same(slot.Parent,canvas) and same(slot.Content,item), "own slot attachment failed")
    slot:SetAutoSize(false)
    slot:SetAnchors({Minimum={X=0,Y=0.5}, Maximum={X=0,Y=0.5}})
    slot:SetAlignment({X=0.5,Y=0.5})
    slot:SetPosition({X=layout.x,Y=layout.y})
    slot:SetSize({X=layout.width,Y=layout.height})
    assert(same(item:GetParent(),canvas), "own parent changed")
end

local function validate_png()
    local file = assert(io.open(png_filename,"rb"), "local PNG is missing/unreadable")
    local ok, err = pcall(function()
        local size = assert(file:seek("end"))
        assert(size > 33 and size <= 1048576, "PNG file size outside experiment bounds")
        file:seek("set",0)
        local header = assert(file:read(33))
        assert(header:sub(1,8) == "\137PNG\r\n\26\n" and header:sub(13,16) == "IHDR", "invalid PNG header")
        assert(string.unpack(">I4",header,9) == 13, "invalid IHDR length")
        assert(string.unpack(">I4",header,17) == 256 and string.unpack(">I4",header,21) == 32,
               "PNG dimensions differ from prepared artifact")
        assert(header:byte(25) == 8 and header:byte(26) == 6
               and header:byte(27) == 0 and header:byte(28) == 0 and header:byte(29) == 0,
               "expected non-interlaced 8-bit RGBA PNG")
    end)
    file:close()
    assert(ok,err)
end

local function bind_divider(image, widget)
    local brush=image.Brush
    assert(brush.DrawAs==3 and not valid(brush.ResourceObject)
        and brush.ResourceName:ToString()=="None", "unexpected new Image brush")
    brush.TintColor={SpecifiedColor={R=1,G=1,B=1,A=1},ColorUseRule=0}
    local texture=resolve(shared.texture)
    if not texture then
        assert(not shared.import_attempted, "texture import already attempted")
        validate_png()
        local p="/Script/Engine.KismetRenderingLibrary:ImportFileAsTexture2D"
        local fn=StaticFindObject(p)
        local cdo=StaticFindObject("/Script/Engine.Default__KismetRenderingLibrary")
        assert(valid(fn) and fn:type()=="UFunction" and fn:GetFullName()=="Function "..p,
            "ImportFileAsTexture2D NOT_LOADED")
        assert(valid(cdo) and cls(cdo)=="/Script/Engine.KismetRenderingLibrary",
            "rendering library CDO NOT_LOADED")
        for _,method in ipairs({"SetBrushFromTexture","SetBrushResourceObject"}) do
            local route="/Script/UMG.Image:"..method
            local f=StaticFindObject(route)
            assert(valid(f) and f:type()=="UFunction" and f:GetFullName()=="Function "..route,
                "Image setter NOT_LOADED")
        end
        shared.import_attempted=true
        texture=fn(cdo,widget,png_filename)
        assert(valid(texture) and cls(texture)=="/Script/Engine.Texture2D"
            and texture:HasAnyFlags(EObjectFlags.RF_Transient)
            and texture:Blueprint_GetSizeX()==256 and texture:Blueprint_GetSizeY()==32,
            "authored PNG import invalid")
        shared.texture=remember(texture)
        log("TEXTURE_IMPORTED","width=256 height=32 once_per_map=true")
    end
    image:SetColorAndOpacity({R=0.75,G=0.75,B=0.75,A=1})
    image:SetBrushFromTexture(texture,false)
    assert(same(image.Brush.ResourceObject,texture),"divider texture not retained")
end

local function release(record)
    local t=resolve(record.tree)
    local parent=resolve(record.canvas)
    local stock=resolve(record.stock)
    local pending={}
    for i=#record.owned,1,-1 do
        local ref=record.owned[i]
        local ok,err=pcall(function()
            local item=resolve(ref)
            if item then
                assert(t and same(item:GetOuter(),t), "own widget outer differs")
                item:SetVisibility(1)
                local current=item:GetParent()
                if valid(current) then
                    assert(parent and same(current,parent), "own widget reparented externally")
                    assert(current:RemoveChild(item)==true, "own widget remove failed")
                end
                assert(not valid(item:GetParent()),"own widget remains attached")
                if ref.role=="divider" and valid(item.Brush.ResourceObject) then
                    item:SetBrushResourceObject(nil)
                    assert(not valid(item.Brush.ResourceObject),"own texture reference remains")
                elseif ref.role=="label" then
                    assert(stock and stock.Font~=nil,"native font carrier unavailable")
                    local original=stock.Font
                    item:SetFont(original) -- Only the OWN TextBlock.
                    assert((not valid(original.FontObject) and not valid(item.Font.FontObject))
                        or same(original.FontObject,item.Font.FontObject),"own font release failed")
                end
            end
        end)
        if not ok then
            pending[#pending+1]=ref
            log("CLEANUP_ITEM_FAILED","role="..ref.role.." error="..tostring(err):sub(1,150))
        end
    end
    record.owned=pending
    return #pending==0
end
local function clear(reason)
    local failed=false
    for i=#order,1,-1 do
        local id=order[i]
        local r=entries[id]
        if r then
            local ok,done=pcall(release,r)
            if not ok or not done then failed=true
                log("RELEASE_FAILED","reason="..reason.." id="..tostring(i)) end
        end
    end
    if failed then
        stopped=true; cleanup_failed=true
        log("STOP_BLOCKED","reason="..reason.." manual_closed_host_rollback_required=true")
        return false
    end
    entries={};order={}
    prepared_talk=nil
    trace_widgets={};trace_count=0
    shared={font=nil,texture=nil,import_attempted=false}
    log("CLEANED","reason="..reason.." own_widgets=0")
    return true
end
-- ESlateVisibility 0=Visible, 3=HitTestInvisible, 4=SelfHitTestInvisible.
-- All three can paint. 1=Collapsed and 2=Hidden must stay native-only.
local function can_paint(visibility)
    return visibility==0 or visibility==3 or visibility==4
end
local function visibility_reason(w,stock)
    if not can_paint(w.Visibility) then return "root_visibility" end
    if w.RenderOpacity<=0 then return "root_opacity" end
    if w.bIsEnabled~=true then return "root_disabled" end
    if not can_paint(stock.Visibility) then return "native_text_visibility" end
    if stock.RenderOpacity<=0 then return "native_text_opacity" end
end
local function native_structure(w,stock)
    local t=w.WidgetTree
    local canvas=stock:GetParent()
    if not valid(t) or cls(t)~="/Script/UMG.WidgetTree" or not same(t:GetOuter(),w)
        or not valid(canvas) or cls(canvas)~="/Script/UMG.CanvasPanel"
        or not same(canvas:GetOuter(),t) or not same(stock:GetOuter(),t)
        or not path(canvas):match("%.CanvasPanel_6$") then
        return nil,"native_tree_unready"
    end
    local slot=stock.Slot
    if not valid(slot) or cls(slot)~="/Script/UMG.CanvasPanelSlot"
        or not slot:GetAutoSize() then return nil,"native_slot_unready" end
    local icon=StaticFindObject(path(t)..".RetainerBox_0")
    if not valid(icon) or not same(icon:GetParent(),canvas) then return nil,"native_icon_unready" end
    local islot=icon.Slot
    if not valid(islot) or cls(islot)~="/Script/UMG.CanvasPanelSlot" then
        return nil,"native_icon_slot_unready"
    end
    return {tree=t,canvas=canvas,slot=slot,icon_slot=islot}
end
local function native_candidate(w)
    if not valid(w) or cls(w)~=CLASS then return nil,"invalid_tiphud" end
    local stock=w.TextBlock_89
    if not valid(stock) or cls(stock)~="/Script/UMG.TextBlock" then
        return nil,"native_text_missing"
    end
    local reason=visibility_reason(w,stock)
    if reason then return nil,reason end
    local rendered=stock.Text:ToString()
    if type(rendered)~="string" or rendered=="" then return nil,"native_text_empty" end
    local structure
    structure,reason=native_structure(w,stock)
    if not structure then return nil,reason end
    local slot,islot=structure.slot,structure.icon_slot
    -- Only native original children. Own geometry must not change their slot/font/brush.
    local layout=Layout.plan({
        desired=stock:GetDesiredSize(), position=slot:GetPosition(),
        alignment=slot:GetAlignment(), anchors=slot:GetAnchors(),
        native_size=stock.Font.Size, icon_position=islot:GetPosition(),
        icon_alignment=islot:GetAlignment(), icon_anchors=islot:GetAnchors(),
        icon_auto=islot:GetAutoSize(), icon_size=islot:GetSize()
    })
    if not layout then return nil,"native_measurement_unready" end
    return {id=path(w),widget=remember(w),stock=remember(stock),
        tree=remember(structure.tree),canvas=remember(structure.canvas),layout=layout,
        root_visibility=w.Visibility}
end
local function decorate(candidate,collapsed)
    local w=assert(resolve(candidate.widget))
    local stock=assert(resolve(candidate.stock))
    local t=assert(resolve(candidate.tree))
    local canvas=assert(resolve(candidate.canvas))
    local text_class=StaticFindObject("/Script/UMG.TextBlock")
    local image_class=StaticFindObject("/Script/UMG.Image")
    assert(valid(text_class) and text_class:type()=="UClass"
        and valid(image_class) and image_class:type()=="UClass","UMG primitive classes NOT_LOADED")
    local record={id=candidate.id,widget=candidate.widget,stock=candidate.stock,
        tree=candidate.tree,canvas=candidate.canvas,owned={},layout_key=candidate.layout.key}
    -- Record before the first mutable operation, so failure can detach partial children.
    entries[candidate.id]=record
    order[#order+1]=candidate.id
    local ok,reason=pcall(function()
        local label=make(text_class,t,"IIP_S1_Label_","label",record)
        label:SetFont(stock.Font) -- Native typed copy, OWN TextBlock only.
        assert(label.Font:GetStructAddress()~=stock.Font:GetStructAddress(),"FontInfo aliased")
        local font=resolve(shared.font)
        if not font then
            assert(shared.font==nil, "shared font lost; not safe to duplicate")
            shared.font=configure_font(label)
        else
            label.Font.FontObject=font
            label.Font.TypefaceFontName=FName("Default")
            label:SetFont(label.Font)
            assert(same(label.Font.FontObject,font),"shared font bind failed")
        end
        label:SetText(FText("ACTION")) -- Neutral research glyphs, NOT a verified Aphes translation.
        assert(label.Text:ToString()=="ACTION","own glyph readback mismatch")
        label.Font.Size=candidate.layout.upper_size
        label.Font.OutlineSettings.OutlineSize=1
        label.Font.OutlineSettings.OutlineColor={R=0,G=0,B=0,A=0.75}
        label:SetFont(label.Font)
        label:SetJustification(1)
        label:SetColorAndOpacity({SpecifiedColor={R=0.85,G=0.85,B=0.85,A=1},ColorUseRule=0})
        place(canvas,label,candidate.layout.upper)
        local divider=make(image_class,t,"IIP_S1_Divider_","divider",record)
        bind_divider(divider,w)
        place(canvas,divider,candidate.layout.divider)
        if not collapsed then
            label:SetVisibility(3);divider:SetVisibility(3) -- HitTestInvisible.
        end
    end)
    if not ok then
        log("ATTACH_FAILED","reason="..tostring(reason):sub(1,180))
        stopped=true -- A partial failed attempt never silently retries shared resources.
        if not release(record) then
            stopped=true;cleanup_failed=true
            log("STOP_BLOCKED","attach cleanup incomplete")
        else
            entries[candidate.id]=nil
            table.remove(order,#order)
        end
        return
    end
    if not collapsed then
        log("ATTACHED","original_action_and_hint_untouched=true own_children=2 root_visibility="..tostring(candidate.root_visibility))
    end
    return record
end

local function prepare_talk(actor)
    if not valid(actor) or cls(actor)~=NPC then return end
    local prefix=MERCHANT_LEVEL..".1-1_plot_slumB1_main1:PersistentLevel.NPCInteract_Bp_C_"
    local actor_path=path(actor)
    if actor_path:sub(1,#prefix)~=prefix or not actor_path:sub(#prefix+1):match("^%d+$") then return end
    if prepared_talk then
        assert(prepared_talk.actor.address==actor:GetAddress()
            and prepared_talk.actor.path==actor_path,"ambiguous merchant owner")
        return
    end
    local component=actor.ExtendedWidget
    if not valid(component) or cls(component)~=COMPONENT
        or not same(component:GetOwner(),actor) then
        log("TEMPLATE_UNAVAILABLE","reason=component")
        return
    end
    local w=component:GetUserWidgetObject()
    if not valid(w) or cls(w)~=CLASS or component.bAddedToScreen~=false
        or component.bVisible~=false then
        log("TEMPLATE_UNAVAILABLE","reason=early_widget")
        return
    end
    local stock=w.TextBlock_89
    if not valid(stock) or cls(stock)~="/Script/UMG.TextBlock" then
        log("TEMPLATE_UNAVAILABLE","reason=native_text_missing")
        return
    end
    local structure,reason=native_structure(w,stock)
    if not structure then log("TEMPLATE_UNAVAILABLE","reason="..reason);return end
    local candidate={id=path(w),widget=remember(w),stock=remember(stock),
        tree=remember(structure.tree),canvas=remember(structure.canvas),layout=TALK_LAYOUT}
    log("TEMPLATE_PREPARE_BEGIN","source=BeginPlayPost width="..TALK_LAYOUT.divider.width)
    local record=decorate(candidate,true)
    if not record then return end
    prepared_talk={actor=remember(actor),component=remember(component),record=record,shown=false}
    log("TEMPLATE_PREPARED","own_children=2 collapsed=true")
end

local function show_talk(w)
    local state=prepared_talk
    if not state or not valid(w) or w:GetAddress()~=state.record.widget.address then return end
    local r=state.record
    local actor,component=resolve(state.actor),resolve(state.component)
    assert(actor and component and same(actor.ExtendedWidget,component)
        and same(component:GetOwner(),actor) and same(component:GetUserWidgetObject(),w)
        and same(resolve(r.widget),w),"merchant identity changed")
    local stock,canvas=resolve(r.stock),resolve(r.canvas)
    assert(stock and canvas and same(w.WidgetTree,resolve(r.tree))
        and same(w.TextBlock_89,stock) and same(stock:GetParent(),canvas),
        "merchant native tree changed")
    local argument=actor.TipHUDArgument
    local is_talk=valid(argument) and cls(argument)==ARGUMENT
        and same(argument:GetOwner(),actor) and argument.msgTag:ToString()=="Talk"
    local reason
    if not is_talk then reason="action"
    elseif component.bAddedToScreen~=true or component.bVisible~=true then reason="component_hidden"
    else reason=visibility_reason(w,stock) end
    local shown=reason==nil
    if not state.first then
        state.first=true
        log("TEMPLATE_FIRST_CANSHOW","eligible="..tostring(shown).." reason="..(reason or "ready"))
    end
    if shown==state.shown then return end
    local label,divider=resolve(r.owned[1]),resolve(r.owned[2])
    assert(label and divider and same(label:GetParent(),canvas) and same(divider:GetParent(),canvas),
        "merchant own children detached")
    local visibility=shown and 3 or 1
    label:SetVisibility(visibility)
    divider:SetVisibility(visibility)
    state.shown=shown
    log(shown and "TEMPLATE_SHOWN" or "TEMPLATE_COLLAPSED","source=CanShow geometry_reads=0")
end

-- One trace per exact widget path/address, capped to avoid per-callback log spam.
-- No new hook, timer, engine query, native write or retained UE wrapper.
local function trace_first(w)
    if not valid(w) or cls(w)~=CLASS then return nil end
    local key=path(w).."@"..tostring(w:GetAddress())
    local t=trace_widgets[key]
    if t then return t end
    if trace_count>=TRACE_LIMIT then return nil end
    trace_count=trace_count+1
    t={index=trace_count,last_gate=nil,gate_changes=0,eligible=false}
    trace_widgets[key]=t
    log("TRACE_FIRST_CALLBACK","widget="..t.index.." root_visibility="..tostring(w.Visibility))
    return t
end
local function trace_gate(t,reason,w)
    if not t or t.eligible or t.gate_changes>=TRACE_TRANSITIONS then return end
    local gate=tostring(reason).."@"..tostring(w.Visibility)
    if t.last_gate==gate then return end
    t.last_gate=gate
    t.gate_changes=t.gate_changes+1
    log("TRACE_PENDING","widget="..t.index.." reason="..tostring(reason)
        .." root_visibility="..tostring(w.Visibility))
end
local function trace_eligible(t,c)
    if not t or t.eligible then return end
    t.eligible=true
    log("TRACE_ELIGIBLE","widget="..t.index.." root_visibility="
        ..tostring(c.root_visibility))
end

local function observe(context,...)
    if stopped or busy then return end
    local argc=select("#",...)
    if argc~=0 then
        stopped=true
        log("STOP","unexpected CanShow parameters")
        clear("unexpected_signature")
        return
    end
    busy=true
    local ok,err=pcall(function()
        local w=context:get()
        if TALK_TEMPLATE then show_talk(w);return end
        local trace=trace_first(w)
        local c,reason=native_candidate(w)
        if not c then
            trace_gate(trace,reason,w)
            return -- Unsupported state stays entirely stock.
        end
        trace_eligible(trace,c)
        local prev=entries[c.id]
        if prev then
            if prev.widget.address~=c.widget.address or prev.widget.class~=c.widget.class then
                stopped=true;log("STOP","TipHUD identity reused")
                clear("identity_replaced")
                return
            end
            -- The lower native text/icon/device still owns its content and semantics.
            -- Update ONLY own child geometry if the native label's measured extent changed.
            if prev.layout_key~=c.layout.key then
                local label=assert(resolve(prev.owned[1]))
                local divider=assert(resolve(prev.owned[2]))
                local canvas=assert(resolve(prev.canvas))
                assert(same(label:GetParent(),canvas) and same(divider:GetParent(),canvas),
                    "owned children no longer in native canvas")
                local u,d=label.Slot,divider.Slot
                assert(valid(u) and valid(d),"own canvas slots unavailable")
                label.Font.Size=c.layout.upper_size
                label:SetFont(label.Font)
                u:SetPosition({X=c.layout.upper.x,Y=c.layout.upper.y})
                u:SetSize({X=c.layout.upper.width,Y=c.layout.upper.height})
                d:SetPosition({X=c.layout.divider.x,Y=c.layout.divider.y})
                d:SetSize({X=c.layout.divider.width,Y=c.layout.divider.height})
                prev.layout_key=c.layout.key
                log("LAYOUT_REFRESH","own_children_only=true")
            end
            return
        end
        if #order>=MAX_WIDGETS then
            local old=table.remove(order,1)
            local rec=entries[old]
            if rec and not release(rec) then
                stopped=true;cleanup_failed=true
                log("STOP_BLOCKED","capacity eviction cleanup failed");return
            end
            entries[old]=nil
            log("EVICTED","max_widgets="..MAX_WIDGETS)
        end
        if trace then
            log("TRACE_ATTACH_BEGIN","widget="..trace.index)
        end
        decorate(c)
    end)
    if not ok then
        stopped=true
        log("STOP","unexpected_host_exception="..tostring(err):sub(1,180))
        clear("unexpected_fault")
    end
    busy=false
end
local function map_pre()
    if stopped and #order==0 then return end
    busy=true
    local ok,err=pcall(clear,"map_pre")
    if not ok then stopped=true;log("STOP","map_cleanup_exception="..tostring(err):sub(1,180)) end
    busy=false
end
local function stop_control()
    if stopped and not cleanup_failed and #order==0 then return end
    stopped=true
    clear("user_stop")
end
local hook_registered=false
local waiting_logged=false
local function try_hook()
    if stopped or hook_registered then return end
    local fn=StaticFindObject(HOOK)
    if not valid(fn) then
        if not waiting_logged then
            waiting_logged=true
            log("WAITING","CanShow_NOT_LOADED retry=BeginPlayPost")
        end
        return
    end
    assert(fn:type()=="UFunction","CanShow reflected type mismatch")
    assert(fn:GetFullName()=="Function "..HOOK,"CanShow reflected name mismatch")
    assert((fn:GetFunctionFlags() & 0x400)==0,"CanShow unexpectedly native")
    local pre,post=RegisterHook(HOOK,observe)
    assert(type(pre)=="number" and pre>0 and pre==post,"CanShow hook registration failed")
    hook_registered=true
    log("READY","native_tiphud=true input_stock=true stop=Ctrl+Alt+F9")
end
local function retry_hook(context)
    if busy then return end
    local ok,err=pcall(function()
        try_hook()
        if TALK_TEMPLATE and not stopped then
            busy=true
            prepare_talk(context:get())
        end
    end)
    busy=false
    if not ok then
        stopped=true
        log("UNAVAILABLE",tostring(err):sub(1,200))
        if TALK_TEMPLATE then clear("prepare_fault") end
    end
end
local ok,err=pcall(function()
    local config=require("IIPS1Config")
    assert(type(config)=="table","missing IIPS1Config")
    ttf_filename=config.filename
    png_filename=config.separator_filename
    for _,p in ipairs({ttf_filename,png_filename}) do
        assert(type(p)=="string" and #p<=1024
            and p:match("^[A-Za-z]:[/\\]") and not p:find("[%z\r\n\128-\255]"),
            "expected local absolute ASCII path")
    end
    assert(ttf_filename:lower():match("%.ttf$") and png_filename:lower():match("%.png$"),
        "wrong asset extensions")
    for _,name in ipairs({"StaticFindObject","StaticConstructObject","RegisterHook",
        "RegisterLoadMapPreHook","RegisterKeyBind","IsKeyBindRegistered",
        "ExecuteInGameThread","RegisterBeginPlayPostHook"}) do
        assert(type(_G[name])=="function","missing UE4SS API: "..name)
    end
    assert(EngineTickAvailable==true and FName and FText and type(EObjectFlags)=="table",
        "native game-thread or struct constructors unavailable")
    local chord={ModifierKey.CONTROL,ModifierKey.ALT}
    assert(not IsKeyBindRegistered(Key.F9,chord),"Ctrl+Alt+F9 collision")
    RegisterLoadMapPreHook(map_pre)
    RegisterKeyBind(Key.F9,chord,function()
        local sent,error=pcall(ExecuteInGameThread,stop_control,EGameThreadMethod.EngineTick)
        if not sent then log("DISPATCH_FAILED",tostring(error):sub(1,180)) end
    end)
    RegisterBeginPlayPostHook(retry_hook)
    try_hook()
end)
if ok then log("ARMED","initialization=event_driven stop=Ctrl+Alt+F9")
else stopped=true;log("UNAVAILABLE",tostring(err):sub(1,200)) end
