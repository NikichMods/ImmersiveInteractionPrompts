-- SPDX-License-Identifier: MPL-2.0
-- Research only: one HUD-root screen-position sample. Original TipHUD stays untouched.
local CLASS="/Game/MainContent/Template/UMG/TipHUD.TipHUD_C"
local PATH=CLASS..":CanShow"
local HUD="/Game/MainContent/Template/UMG/HUD/HUDMainUMG_BP.HUDMainUMG_BP_C"
local phase,busy,deadline="armed",false,0
local owner,tree,host,panel,lower_ref,coords_ref=nil,nil,nil,nil,nil,nil
local owned={}
local Position=require("IIPPosition")
local position=Position.initial()
local ttf_filename,png_filename,import_attempted,font_identity=nil,nil,false,nil
local FONT="/Script/Engine.Font"
local DONOR="/Game/Fonts/EBGaramond-SemiBold_Font.EBGaramond-SemiBold_Font"
local function log(event,detail) print("IIP_VIEWPORT event="..event.." "..(detail or "").."\n") end
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
local function cleanup(reason)
    phase="stopped"
    local hidden,hide_error=pcall(function()
        local c=resolve(panel)
        if c then c:SetVisibility(1) end
    end)
    if not hidden then log("HIDE_FAILED",tostring(hide_error):sub(1,180)) end
    local pending={}
    for i=#owned,1,-1 do
        local ref=owned[i]
        local ok,err=pcall(function()
            -- Preserve the own stock-font carrier while an earlier child needs release retry.
            if ref.role=="lower" and #pending>0 then error("lower retained for cleanup retry") end
            local o=resolve(ref)
            if o then
                assert(same(o:GetOuter(),resolve(tree)),"own object outer changed")
                o:SetVisibility(1)
                if ref.role=="upper" then
                    local lower=resolve(lower_ref)
                    assert(valid(lower),"own lower font reference unavailable")
                    o:SetFont(lower.Font)
                    assert(same(o.Font.FontObject,lower.Font.FontObject),"font release differs")
                    log("FONT_RELEASED","own_upper=true")
                elseif ref.role=="ornament" or ref.role=="hint" then
                    -- Detach first; cleanup retries never rebind or reload.
                    local parent=o:GetParent()
                    if valid(parent) then
                        assert(same(parent,resolve(panel)),"child reparented")
                        assert(parent:RemoveChild(o),"child detach failed")
                    end
                    o:SetBrushResourceObject(nil)
                    assert(not valid(o.Brush.ResourceObject),"brush release differs")
                    log("BRUSH_RELEASED","role="..ref.role)
                end
                local parent=o:GetParent()
                if valid(parent) then
                    assert(same(parent,resolve(panel)),"child reparented")
                    assert(parent:RemoveChild(o),"child detach failed")
                end
                log("REMOVED","role="..ref.role)
            end
        end)
        if not ok then table.insert(pending,1,ref);log("CLEANUP_ITEM_FAILED",ref.role.." "..tostring(err):sub(1,180)) end
    end
    owned=pending
    local detached,detach_error=pcall(function()
        if #pending>0 then error("hidden own canvas retained for cleanup retry") end
        local c=resolve(panel)
        if c then
            local parent=c:GetParent()
            if valid(parent) then
                assert(same(parent,resolve(host)),"own canvas reparented")
                assert(parent:RemoveChild(c),"root detach failed")
            end
            assert(not valid(c:GetParent()),"own canvas still attached")
        end
    end)
    if not detached then log("ROOT_DETACH_FAILED",tostring(detach_error):sub(1,180)) end
    if #pending==0 and detached and hidden then log("CLEANED","reason="..reason.." own_children_remaining=0")
    else phase="cleanup_failed";log("CLEANUP_FAILED","remaining="..#pending) end
end
local function create(kind,t,name,role)
    local c=StaticFindObject("/Script/UMG."..kind)
    assert(valid(c) and c:type()=="UClass","class NOT_LOADED: "..kind)
    assert(not valid(StaticFindObject(path(t).."."..name)),"own name collision")
    local o=StaticConstructObject(c,t,FName(name),EObjectFlags.RF_Transient)
    assert(valid(o) and cls(o)=="/Script/UMG."..kind and same(o:GetOuter(),t),"own construction differs")
    local ref=remember(o);ref.role=role
    if role=="canvas" then panel=ref else owned[#owned+1]=ref end
    o:SetVisibility(1)
    return o,ref
end
local function attach(parent,o,x,y,width,height,ax,ay)
    local s=parent:AddChildToCanvas(o)
    assert(valid(s) and cls(s)=="/Script/UMG.CanvasPanelSlot" and same(s.Content,o)
        and same(s.Parent,parent) and same(o:GetParent(),parent),"own attachment differs")
    s:SetAutoSize(false);s:SetAnchors({Minimum={X=0,Y=0},Maximum={X=0,Y=0}})
    s:SetAlignment({X=ax,Y=ay});s:SetPosition({X=x,Y=y});s:SetSize({X=width,Y=height})
    return s
end
local function descendant(o,target)
    if not valid(o) then return false end
    local c=o:GetClass()
    for _=1,24 do
        if not valid(c) then return false end
        if path(c)==target then return true end
        c=c:GetSuperStruct()
    end
    return false
end
local function identity_transform(o)
    local t=o.RenderTransform
    return t.Translation.X==0 and t.Translation.Y==0 and t.Scale.X==1 and t.Scale.Y==1
        and t.Shear.X==0 and t.Shear.Y==0 and t.Angle==0
end
local function find_hud()
    local candidates=FindAllOf("HUDMainUMG_BP_C") or {} -- One class query, once on creation; no monitoring.
    assert(type(candidates)=="table" and #candidates<=8,"unexpected HUD candidate set")
    local found,count=nil,0
    for _,h in ipairs(candidates) do
        if valid(h) and cls(h)==HUD and h:IsInViewport()
            and descendant(h:GetOwningPlayerPawn(),"/Script/Genesis.GenesisCharacter") then
            found,count=h,count+1
        end
    end
    assert(count==1,"need exactly one in-viewport gameplay HUD")
    local a,al=found:GetAnchorsInViewport(),found:GetAlignmentInViewport()
    assert(a.Minimum.X==0 and a.Minimum.Y==0 and a.Maximum.X==1 and a.Maximum.Y==1
        and al.X==0 and al.Y==0 and identity_transform(found),"HUD is not an untransformed stretched viewport host")
    local t=found.WidgetTree
    assert(valid(t) and same(t:GetOuter(),found),"HUD WidgetTree unavailable")
    local root=t.RootWidget
    assert(valid(root) and cls(root)=="/Script/UMG.CanvasPanel" and path(root)==path(t)..".Main_Panel"
        and same(root:GetOuter(),t) and not valid(root:GetParent()) and identity_transform(root),"unsupported HUD root")
    assert(root:GetChildrenCount()>=2 and root:GetChildrenCount()<=16,"unexpected HUD root child count")
    assert(found.Visibility~=1 and found.Visibility~=2 and found.RenderOpacity>0,"HUD not visible")
    return found,t,root
end
local function viewport_size(h)
    local p="/Script/UMG.WidgetLayoutLibrary:GetViewportSize"
    local fn=StaticFindObject(p)
    local cdo=StaticFindObject("/Script/UMG.Default__WidgetLayoutLibrary")
    assert(valid(fn) and fn:type()=="UFunction" and fn:GetFullName()=="Function "..p
        and valid(cdo) and cls(cdo)=="/Script/UMG.WidgetLayoutLibrary","viewport size API NOT_LOADED")
    local size=fn(cdo,h)
    assert(type(size)=="table" and type(size.X)=="number" and type(size.Y)=="number"
        and size.X>=800 and size.X<=16384 and size.Y>=600 and size.Y<=16384,"unsupported viewport")
    return size
end
local function position_sample(action)
    local h,c=resolve(owner),resolve(panel)
    assert(valid(h) and h:IsInViewport() and valid(c),"own viewport sample unavailable")
    local root=resolve(host)
    local ha=h:GetAnchorsInViewport()
    assert(valid(root) and identity_transform(h) and identity_transform(root)
        and ha.Minimum.X==0 and ha.Minimum.Y==0 and ha.Maximum.X==1 and ha.Maximum.Y==1,
        "viewport host geometry changed")
    local s=c.Slot
    assert(valid(s) and same(c:GetParent(),resolve(host)),"own canvas detached")
    s:SetAnchors({Minimum={X=position.x/100,Y=position.y/100},Maximum={X=position.x/100,Y=position.y/100}})
    local a=s:GetAnchors()
    assert(math.abs(a.Minimum.X-position.x/100)<0.000001 and math.abs(a.Minimum.Y-position.y/100)<0.000001
        and a.Maximum.X==a.Minimum.X and a.Maximum.Y==a.Minimum.Y,"position readback differs")
    local indicator=resolve(coords_ref)
    assert(valid(indicator),"own indicator unavailable")
    indicator:SetText(FText(string.format("TEST  X=%d%%  Y=%d%%",position.x,position.y)))
    local size=viewport_size(h)
    log("POSITION",string.format("action=%s x_percent=%d y_percent=%d viewport_w=%.0f viewport_h=%.0f space=HUD-root anchors_stretched=true",
        action,position.x,position.y,size.X,size.Y))
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
        assert(string.unpack(">I4",header,17) == 570 and string.unpack(">I4",header,21) == 16,
               "PNG dimensions differ from prepared artifact")
        assert(header:byte(25) == 8 and header:byte(26) == 6
               and header:byte(27) == 0 and header:byte(28) == 0 and header:byte(29) == 0,
               "expected non-interlaced 8-bit RGBA PNG")
    end)
    file:close()
    assert(ok,err)
end
local function configure_ornament(image, widget)
    assert(not import_attempted, "second import refused")
    validate_png() -- Bounded read only; the native importer still validates/decodes the file.
    local function_path = "/Script/Engine.KismetRenderingLibrary:ImportFileAsTexture2D"
    local fn = StaticFindObject(function_path)
    local cdo = StaticFindObject("/Script/Engine.Default__KismetRenderingLibrary")
    assert(valid(fn) and fn:type() == "UFunction" and fn:GetFullName() == "Function " .. function_path,
           "ImportFileAsTexture2D NOT_LOADED")
    assert(valid(cdo) and cls(cdo) == "/Script/Engine.KismetRenderingLibrary", "rendering library CDO NOT_LOADED")
    for _, method in ipairs({"SetBrushFromTexture","SetBrushResourceObject"}) do
        local method_path = "/Script/UMG.Image:" .. method
        local target = StaticFindObject(method_path)
        assert(valid(target) and target:type() == "UFunction"
            and target:GetFullName() == "Function " .. method_path, "Image method NOT_LOADED: " .. method)
    end
    local brush = image.Brush
    assert(brush.DrawAs == 3 and not valid(brush.ResourceObject)
        and brush.ResourceName:ToString() == "None", "unexpected fresh header brush")
    brush.TintColor = {SpecifiedColor={R=1,G=1,B=1,A=1},ColorUseRule=0}
    import_attempted = true -- Never retry even on null result, binding failure or cleanup retry.
    log("IMPORT_BEGIN", "size=570x16 once=true")
    -- StaticFindObject yields an unbound UFunction. First argument is its explicit calling CDO.
    local texture = fn(cdo,widget,png_filename)
    assert(valid(texture) and cls(texture) == "/Script/Engine.Texture2D", "import returned no Texture2D")
    assert(texture:HasAnyFlags(EObjectFlags.RF_Transient), "imported texture is not transient")
    assert(texture:Blueprint_GetSizeX() == 570 and texture:Blueprint_GetSizeY() == 16,
           "imported dimensions mismatch")
    image:SetColorAndOpacity({R=1,G=1,B=1,A=1})
    image:SetBrushFromTexture(texture,false) -- Own fixed slot, stock PNG aspect ratio.
    assert(same(image.Brush.ResourceObject,texture) and image.Brush.DrawAs == 3
        and image.Brush.TintColor.ColorUseRule == 0 and image.Brush.TintColor.SpecifiedColor.A == 1,
           "texture brush reference not established")
    log("TEXTURE_BOUND", "size=570x16 brush_ref=true transient=true")
    -- UImage.Brush.ResourceObject retains the texture. No raw wrapper or extra GC root escapes.
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
        local font_name = "IIP_AphesFont_" .. tostring(os.time())
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


local function guarded(fn)
    if busy then return end
    busy=true
    local ok,err=pcall(fn)
    if not ok then log("FAILED",tostring(err):sub(1,240));cleanup("failure") end
    busy=false
end
local function observe(context,...)
    if phase~="waiting" then return end -- Not a continuing TipHUD monitor.
    local extra=select('#',...)
    guarded(function()
        assert(extra==0,"unexpected CanShow inputs")
        if os.time()>=deadline then cleanup("timeout");return end
        local w=context:get()
        assert(valid(w) and cls(w)==CLASS,"unexpected TipHUD")
        local b=w.TextBlock_89
        if w.Visibility~=0 or w.RenderOpacity<=0 or not w.bIsEnabled or not valid(b)
            or b.Visibility==1 or b.Visibility==2 or b.Text:ToString()~="Открыть" then return end
        phase="creating" -- Exactly one attempt, even if it fails.
        assert(cls(b)=="/Script/UMG.TextBlock" and b.Font.Size==22,"unsupported original text")
        local h,t,root=find_hud()
        viewport_size(h)
        owner,tree,host=remember(h),remember(t),remember(root)
        local name="IIP_Viewport_"..tostring(os.time())
        local canvas=create("CanvasPanel",t,name,"canvas")
        local root_slot=attach(root,canvas,0,0,320,132,0.5,0.5)
        root_slot:SetZOrder(100)
        local lower,lr=create("TextBlock",t,name.."_Lower","lower");lower_ref=lr
        lower:SetFont(b.Font)
        assert(lower.Font:GetStructAddress()~=b.Font:GetStructAddress(),"stock FontInfo alias")
        lower:SetText(FText(b.Text:ToString())) -- Static localized snapshot, not a live interaction driver.
        lower:SetJustification(1)
        local size=b:GetDesiredSize()
        assert(type(size)=="table" and size.X>=80 and size.X<=260 and size.Y>=20 and size.Y<=40,"unsupported sample extent")
        attach(canvas,lower,160,76,size.X,size.Y,0.5,0.5)
        local source_tree=w.WidgetTree
        local retainer=StaticFindObject(path(source_tree)..".RetainerBox_0")
        assert(valid(retainer) and cls(retainer)=="/Script/UMG.RetainerBox","original hint branch unavailable")
        local source_hint=retainer:GetChildAt(0)
        assert(valid(source_hint) and cls(source_hint)=="/Script/UMG.Image"
            and same(source_hint:GetParent(),retainer) and valid(source_hint.Brush.ResourceObject),"original hint image unavailable")
        local hint=create("Image",t,name.."_Hint","hint")
        hint:SetBrush(source_hint.Brush) -- Value copy; shared resource read-only, never mutate its material parameters.
        hint:SetColorAndOpacity(source_hint.ColorAndOpacity)
        assert(same(hint.Brush.ResourceObject,source_hint.Brush.ResourceObject),"hint resource copy differs")
        attach(canvas,hint,160-size.X/2-8-19,76,38,38,0.5,0.5)
        local ornament=create("Image",t,name.."_Ornament","ornament")
        configure_ornament(ornament,h)
        attach(canvas,ornament,160,48,200,6,0.5,0.5)
        local upper=create("TextBlock",t,name.."_Upper","upper")
        upper:SetFont(lower.Font);font_identity=configure_font(upper)
        upper.Font.Size=28;upper.Font.LetterSpacing=150
        upper.Font.OutlineSettings.OutlineSize=0
        upper.Font.OutlineSettings.OutlineMaterial=nil
        upper:SetFont(upper.Font)
        upper:SetShadowOffset({X=0,Y=0});upper:SetShadowColorAndOpacity({R=0,G=0,B=0,A=0})
        upper:SetColorAndOpacity({SpecifiedColor={R=1,G=1,B=1,A=1},ColorUseRule=0})
        upper:SetJustification(1);upper:SetText(FText("OPEN"))
        assert(upper.Font.OutlineSettings.OutlineSize==0 and upper.Font.Size==28 and upper.Font.LetterSpacing==150,"upper style readback differs")
        attach(canvas,upper,160,0,280,40,0.5,0)
        local indicator,ir=create("TextBlock",t,name.."_Coords","coords");coords_ref=ir
        indicator:SetFont(lower.Font);indicator.Font.Size=12;indicator:SetFont(indicator.Font)
        indicator:SetJustification(1)
        attach(canvas,indicator,160,112,300,20,0.5,0)
        position_sample("initial")
        for _,ref in ipairs(owned) do resolve(ref):SetVisibility(3) end
        canvas:SetVisibility(3) -- Own subtree is hit-test invisible; no focus/input-mode calls.
        phase="active"
        log("ATTACHED","space=HUD-root own_children=5 own_canvas=1 original_tip_untouched=true sample_only=true max_seconds=180")
    end)
    -- No return value overrides CanShow; source widget is borrowed read-only in this callback.
end
local function control(action,dx,dy)
    if phase=="stopped" then return end
    if action=="toggle" then
        if phase~="armed" then cleanup("user");return end
        guarded(function()
            local fn=StaticFindObject(PATH)
            assert(valid(fn) and fn:type()=="UFunction" and fn:GetFullName()=="Function "..PATH
                and (fn:GetFunctionFlags()&0x400)==0,"CanShow NOT_LOADED/native")
            phase,deadline="waiting",os.time()+180
            local pre,post=RegisterHook(PATH,observe)
            assert(type(pre)=="number" and pre>0 and pre==post,"unexpected hook IDs")
            ExecuteInGameThreadWithDelay(180000,function()
                if phase~="stopped" then cleanup("timeout") end
            end)
            log("WAITING","one_open_snapshot=true controls=CtrlAlt-arrows/Home/F7/F6")
        end)
    elseif phase=="active" then
        guarded(function()
            if os.time()>=deadline then cleanup("timeout");return end
            if action=="move" then position=Position.move(position,dx,dy)
            elseif action=="reset" then position=Position.initial() end
            position_sample(action) -- 'commit' is a structured log only; no config/save writes.
        end)
    end
end
local ok,err=pcall(function()
    local c=require("IIPViewportConfig")
    assert(type(c)=="table","missing private config")
    ttf_filename,png_filename=c.filename,c.separator_filename
    for _,pair in ipairs({{ttf_filename,"ttf"},{png_filename,"png"}}) do
        local value,suffix=pair[1],pair[2]
        assert(type(value)=="string" and #value<=1024 and value:match("^[A-Za-z]:[/\\]")
            and value:lower():match("%."..suffix.."$") and not value:find("[%z\r\n\128-\255]"),"bad private input path")
    end
    for _,api in ipairs({"StaticFindObject","StaticConstructObject","FindAllOf","RegisterHook","RegisterKeyBind",
                         "IsKeyBindRegistered","ExecuteInGameThread","ExecuteInGameThreadWithDelay"}) do
        assert(type(_G[api])=="function","missing API: "..api)
    end
    assert(FName~=nil and FText~=nil and EngineTickAvailable==true and type(EGameThreadMethod)=="table"
        and type(EObjectFlags)=="table" and type(EObjectFlags.RF_Transient)=="number","missing dispatch/constructors")
    local mods={ModifierKey.CONTROL,ModifierKey.ALT}
    local bindings={{Key.F6,"toggle"},{Key.LEFT_ARROW,"move",-1,0},{Key.RIGHT_ARROW,"move",1,0},
        {Key.UP_ARROW,"move",0,-1},{Key.DOWN_ARROW,"move",0,1},{Key.HOME,"reset"},{Key.F7,"commit"}}
    for _,b in ipairs(bindings) do assert(type(b[1])=="number" and not IsKeyBindRegistered(b[1],mods),"missing/colliding control") end
    for _,b in ipairs(bindings) do
        RegisterKeyBind(b[1],mods,function()
            if phase=="stopped" then return end
            local queued,problem=pcall(ExecuteInGameThread,function()control(b[2],b[3],b[4])end,EGameThreadMethod.EngineTick)
            if not queued then log("DISPATCH_FAILED",tostring(problem):sub(1,180)) end
        end)
    end
end)
if ok then log("ARMED","key=CtrlAlt-F6 start_xy=50,78 step_percent=1 bounds=10..90 one_attempt=true")
else phase="stopped";log("UNAVAILABLE",tostring(err):sub(1,240)) end
