-- SPDX-License-Identifier: MPL-2.0
-- Research only: compact Aphes / local stock ornament / translated stock action. NOT INSTALLED.
local CLASS = "/Game/MainContent/Template/UMG/TipHUD.TipHUD_C"
local PATH = CLASS .. ":CanShow"
local phase, owner, panel, tree = "armed", nil, nil, nil
local owned = {} -- At most two path/address/class/role records; never retained engine wrappers.
local deadline, busy = 0, false
local ttf_filename, font_identity, word = nil, nil, "OPEN"
local Layout = require("IIPLayout")
local png_filename, import_attempted, shifted = nil, false, nil
local FONT = "/Script/Engine.Font"
local DONOR = "/Game/Fonts/EBGaramond-SemiBold_Font.EBGaramond-SemiBold_Font"
local function log(event, detail)
    print("IIP_COMPOSITION event=" .. event .. " " .. (detail or "") .. "\n")
end
local function valid(o) return o ~= nil and o:IsValid() end
local function path(o) return assert(o:GetFullName():match("^[^ ]+ (.+)$")) end
local function cls(o) return path(o:GetClass()) end
local function same(a, b) return valid(a) and valid(b) and a:GetAddress() == b:GetAddress() end
local function remember(o)
    return {path=path(o), address=o:GetAddress(), class=cls(o)} -- Strings/numbers only.
end
local function resolve(ref)
    if not ref then return nil end
    local o = StaticFindObject(ref.path) -- Fresh exact lookup, never a stored raw UObject wrapper.
    if not valid(o) then return nil end
    assert(o:GetAddress() == ref.address and cls(o) == ref.class, "identity changed")
    return o
end
local function restore_lower()
    if not shifted then return end
    local b = resolve(shifted.ref)
    if b then
        local v=b.RenderTransform.Translation
        if v.X==shifted.x and v.Y==shifted.y then
            b:SetRenderTranslation({X=shifted.old_x,Y=shifted.old_y})
            local restored=b.RenderTransform.Translation
            assert(restored.X==shifted.old_x and restored.Y==shifted.old_y, "lower restore readback differs")
            log("LOWER_RESTORED","translation_only=true")
        elseif v.X==shifted.old_x and v.Y==shifted.old_y then
            log("LOWER_RESTORED","already_original=true")
        else
            -- A newer host/third-party write owns this value. Never overwrite it or keep enforcing ours.
            log("LOWER_CONFLICT","external_translation_preserved=true")
        end
    else log("LOWER_GONE","no_live_object_to_restore=true") end
    shifted=nil
end
local function cleanup(reason)
    phase = "stopped" -- Hook inert before any nested engine calls.
    local restored,restore_error=pcall(restore_lower)
    if not restored then log("LOWER_RESTORE_FAILED",tostring(restore_error):sub(1,240)) end
    local pending = {}
    for i = #owned,1,-1 do
        local ref = owned[i]
        local ok, err = pcall(function()
            local object = resolve(ref)
            if object then
                local t = resolve(tree)
                assert(valid(t) and same(object:GetOuter(), t), "owned child outer changed")
                object:SetVisibility(1)
                local parent = object:GetParent()
                if valid(parent) then
                    assert(same(parent, resolve(panel)), "owned child reparented externally")
                    log("REMOVE_BEGIN", "role=" .. ref.role)
                    assert(parent:RemoveChild(object) == true, "RemoveChild failed")
                    log("REMOVED", "role=" .. ref.role)
                end
                assert(not valid(object:GetParent()), "child still attached")
                if ref.role == "divider" and valid(object.Brush.ResourceObject) then
                    object:SetBrushResourceObject(nil)
                    assert(not valid(object.Brush.ResourceObject), "texture reference not cleared")
                    log("TEXTURE_UNBOUND","own_image_detached=true")
                end
                if ref.role == "label" then
                    local w = resolve(owner)
                    assert(valid(w) and valid(w.TextBlock_89), "stock FontInfo source unavailable for release")
                    local stock_font = w.TextBlock_89.Font
                    object:SetFont(stock_font) -- Typed synchronous read/copy; never assign into the original.
                    local expected = stock_font.FontObject
                    assert((valid(expected) and same(object.Font.FontObject,expected))
                        or (not valid(expected) and not valid(object.Font.FontObject)), "stock font restore differs")
                    log("FONT_RELEASED", "own_label_detached=true gc_not_forced=true")
                end
            end
        end)
        if not ok then
            pending[#pending+1] = ref
            log("CLEANUP_ITEM_FAILED", "role=" .. ref.role .. " " .. tostring(err):sub(1,240))
        end
    end
    owned = pending -- Keep only failed identities for explicit retry; still try the other child.
    if #pending == 0 and not shifted then log("CLEANED", "reason=" .. reason .. " own_children_remaining=0")
    else phase = "cleanup_failed"; log("CLEANUP_FAILED", "remaining=" .. #pending) end
end

local function create(class, t, name, role)
    assert(not valid(StaticFindObject(path(t) .. "." .. name)), "own name collision")
    log("CREATE_BEGIN", "role=" .. role)
    local object = StaticConstructObject(class,t,FName(name),EObjectFlags.RF_Transient)
    assert(valid(object), "construction returned invalid object")
    local ref = remember(object); ref.role = role; owned[#owned+1] = ref
    assert(same(object:GetOuter(),t), "unexpected constructed outer")
    log("CREATED", "role=" .. role)
    object:SetVisibility(1)
    return object
end
local function attach(c, object, role, x, y, width, height, align_y)
    log("ATTACH_BEGIN", "role=" .. role)
    local slot = c:AddChildToCanvas(object)
    assert(valid(slot) and cls(slot) == "/Script/UMG.CanvasPanelSlot", "attachment returned invalid slot")
    assert(same(object:GetParent(),c) and same(slot.Parent,c) and same(slot.Content,object), "attachment mismatch")
    slot:SetAutoSize(false)
    slot:SetAnchors({Minimum={X=0,Y=0.5},Maximum={X=0,Y=0.5}})
    slot:SetAlignment({X=0.5,Y=align_y})
    slot:SetPosition({X=x,Y=y})
    slot:SetSize({X=width,Y=height})
    log("SLOT_READY", "role=" .. role)
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
local function configure_line(image, widget)
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
    busy = true
    local ok, err = pcall(fn)
    if not ok then log("FAILED", tostring(err):sub(1,240)); cleanup("failure") end
    busy = false
    -- Never return pcall's bool to CanShow.
end
local function eligible(w, b)
    return w.Visibility == 0 and w.RenderOpacity > 0 and w.bIsEnabled == true
        and b.Visibility ~= 1 and b.Visibility ~= 2 and b.RenderOpacity > 0
        and b.Text:ToString() == "Открыть"
end
local function observe(context, ...)
    if phase ~= "waiting" and phase ~= "attached" then return end
    local extra = select("#", ...)
    guarded(function()
        assert(extra == 0, "unexpected CanShow inputs")
        if os.time() >= deadline then cleanup("timeout"); return end
        local w = context:get()
        assert(valid(w) and cls(w) == CLASS, "unexpected TipHUD context")
        if owner and w:GetAddress() ~= owner.address then return end
        local b = w.TextBlock_89
        assert(valid(b) and cls(b) == "/Script/UMG.TextBlock", "missing stock text")
        if not eligible(w,b) then
            if phase == "attached" then cleanup("target-state-changed") end
            return
        end
        if phase == "attached" then
            local v=b.RenderTransform.Translation
            assert(shifted and v.X==shifted.x and v.Y==shifted.y,"host changed lower translation; stop")
            return -- No repeated writes, imports, layout forcing or allocations.
        end
        phase = "attaching"
        local c, t = b:GetParent(), w.WidgetTree
        assert(valid(c) and cls(c) == "/Script/UMG.CanvasPanel", "text parent is not CanvasPanel")
        assert(path(c):match("%.CanvasPanel_6$"), "unexpected canvas identity")
        assert(valid(t) and cls(t) == "/Script/UMG.WidgetTree" and same(c:GetOuter(),t), "unexpected WidgetTree")
        assert(same(t:GetOuter(),w), "tree belongs to another widget")
        assert(same(b:GetOuter(),t) and c:GetChildrenCount() == 3, "original tree differs from baseline")
        assert(b.Font.Size == 22, "font size differs from desktop baseline")
        local source_slot = b.Slot
        assert(valid(source_slot) and cls(source_slot) == "/Script/UMG.CanvasPanelSlot", "unexpected original slot")
        assert(source_slot:GetAutoSize(), "stock text no longer auto-sized")
        local position = source_slot:GetPosition()
        local anchors = source_slot:GetAnchors()
        local alignment = source_slot:GetAlignment()
        local function scalar(n)
            return type(n) == "number" and string.format("%.17g",n) or tostring(n)
        end
        log("LAYOUT_OBSERVED", "position_type=" .. type(position)
            .. " position_x=" .. scalar(position.X) .. " position_y=" .. scalar(position.Y)
            .. " alignment_type=" .. type(alignment)
            .. " alignment_x=" .. scalar(alignment.X) .. " alignment_y=" .. scalar(alignment.Y))
        assert(position.X == 38 and position.Y == 0 and alignment.X == 0 and alignment.Y == 0.5,
               "original layout differs from measured Open baseline")
        assert(anchors.Minimum.X == 0 and anchors.Maximum.X == 0
               and anchors.Minimum.Y == 0.5 and anchors.Maximum.Y == 0.5, "unexpected anchors")
        local icon=StaticFindObject(path(t)..".RetainerBox_0")
        assert(valid(icon) and same(icon:GetParent(),c),"stock key branch unavailable")
        local icon_slot=icon.Slot
        assert(valid(icon_slot) and cls(icon_slot)=="/Script/UMG.CanvasPanelSlot", "unexpected icon slot")
        local ia,ial=icon_slot:GetAnchors(),icon_slot:GetAlignment()
        assert(ia.Minimum.X==0 and ia.Maximum.X==0 and ia.Minimum.Y==0.5 and ia.Maximum.Y==0.5
            and ial.X==0 and ial.Y==0.5 and not icon_slot:GetAutoSize(),"unsupported key geometry")
        local desired=b:GetDesiredSize() -- Cached only; zero/stale/out-of-range fails closed. No original prepass.
        local v=b.RenderTransform.Translation
        local ip,is=icon_slot:GetPosition(),icon_slot:GetSize()
        log("LAYOUT_INPUT","cached_text="..tostring(desired.X)..","..tostring(desired.Y)
            .." key_slot="..tostring(ip.X)..","..tostring(ip.Y)..","..tostring(is.X)..","..tostring(is.Y))
        local layout=Layout.plan(desired,position,alignment,ip,is,{X=v.X,Y=v.Y})
        log("COMPOSITION_GEOMETRY","text_width="..desired.X.." text_height="..desired.Y
            .." center_x="..layout.x.." line_y="..layout.line_y.." lower_translation="..layout.lower_y)
        local name = "IIP_AphesText_" .. tostring(os.time())
        local text_class = StaticFindObject("/Script/UMG.TextBlock")
        assert(valid(text_class) and text_class:type() == "UClass", "TextBlock class NOT_LOADED")
        local image_class = StaticFindObject("/Script/UMG.Image")
        assert(valid(image_class) and image_class:type() == "UClass", "Image class NOT_LOADED")
        owner, panel, tree = remember(w), remember(c), remember(t)
        local label = create(text_class,t,name .. "_OPEN","label")
        assert(cls(label) == "/Script/UMG.TextBlock", "unexpected label class")
        label:SetFont(b.Font) -- Typed struct copy, used synchronously; original untouched.
        assert(label.Font:GetStructAddress() ~= b.Font:GetStructAddress(), "FontInfo storage alias")
        font_identity = configure_font(label)
        label:SetText(FText("OPEN"))
        assert(label.Text:ToString() == "OPEN", "OPEN readback differs")
        label.Font.Size=32 -- Temporary 32/22 ratio; original FontInfo remains untouched.
        label.Font.OutlineSettings.OutlineSize=1
        label.Font.OutlineSettings.OutlineColor={R=0,G=0,B=0,A=0.75}
        label:SetFont(label.Font)
        label:SetColorAndOpacity({SpecifiedColor={R=1,G=1,B=1,A=1},ColorUseRule=0})
        label:SetJustification(1) -- Center on localized text, excluding the key.
        attach(c,label,"label",layout.x,layout.label_y,layout.label_width,layout.label_height,1)
        local line = create(image_class,t,name .. "_Divider","divider")
        assert(cls(line) == "/Script/UMG.Image", "unexpected divider class")
        configure_line(line,w)
        attach(c,line,"divider",layout.x,layout.line_y,layout.width,layout.height,0.5)
        -- Record primitives BEFORE the one stock write, including a partially successful setter.
        shifted={ref=remember(b),old_x=v.X,old_y=v.Y,x=v.X,y=v.Y+layout.lower_y}
        b:SetRenderTranslation({X=shifted.x,Y=shifted.y})
        local moved=b.RenderTransform.Translation
        assert(moved.X==shifted.x and moved.Y==shifted.y,"lower move readback differs")
        log("LOWER_SHIFTED","slot_font_text_unchanged=true")
        label:SetVisibility(3) -- Neither child can receive input; show only after pair configured.
        line:SetVisibility(3)
        phase = "attached"
        log("ATTACHED", "own_children=2 font=Aphes-private word=OPEN divider=local-stock-PNG duration_max=30s")
    end)
    -- No return override, no wrapper/Font/slot retained across callbacks.
end
local function control()
    if phase == "attached" and word == "OPEN" then
        guarded(function()
            if os.time() >= deadline then cleanup("timeout"); return end
            local w, label, font = resolve(owner), resolve(owned[1]), resolve(font_identity)
            assert(valid(w) and eligible(w,w.TextBlock_89), "target state changed before READ")
            assert(valid(label) and valid(font) and same(label.Font.FontObject,font)
                and path(font:GetOuter()) == "/Game/Fonts/EBGaramond-SemiBold_Font", "own font/label identity changed")
            label:SetText(FText("READ"))
            assert(label.Text:ToString() == "READ", "READ readback differs")
            word = "READ"
            log("TEXT_CHANGED","word=READ same_element=true")
        end)
        return
    end
    if phase ~= "armed" then cleanup("user"); return end
    guarded(function()
        local fn = StaticFindObject(PATH)
        assert(valid(fn) and fn:type() == "UFunction" and fn:GetFullName() == "Function " .. PATH, "CanShow NOT_LOADED")
        assert((fn:GetFunctionFlags() & 0x400) == 0, "CanShow is native")
        phase, deadline = "waiting", os.time()+30
        local pre, post = RegisterHook(PATH, observe)
        assert(type(pre) == "number" and pre > 0 and pre == post, "unexpected hook IDs")
        ExecuteInGameThreadWithDelay(30000, function()
            if phase ~= "stopped" and phase ~= "cleanup_failed" then cleanup("timeout") end
        end)
        log("WAITING", "target=Open one_attempt=true")
    end)
end
local ok, err = pcall(function()
    local config = require("IIPCompositionConfig")
    assert(type(config) == "table" and type(config.filename) == "string", "missing local Aphes config")
    png_filename=config.separator_filename
    assert(type(png_filename)=="string" and #png_filename<=1024
        and png_filename:match("^[A-Za-z]:[/\\]") and png_filename:lower():match("%.png$")
        and not png_filename:find("[%z\r\n\128-\255]"),"expected absolute ASCII ornament PNG path")
    ttf_filename = config.filename
    assert(#ttf_filename <= 1024 and ttf_filename:match("^[A-Za-z]:[/\\]")
        and ttf_filename:lower():match("%.ttf$") and not ttf_filename:find("[%z\r\n\128-\255]"), "expected absolute ASCII TTF filename")
    assert(type(io.open) == "function", "missing file-read API")
    for _, key in ipairs({"StaticFindObject","StaticConstructObject","RegisterHook","RegisterKeyBind",
                          "IsKeyBindRegistered","ExecuteInGameThread","ExecuteInGameThreadWithDelay"}) do
        assert(type(_G[key]) == "function", "missing API: " .. key)
    end
    assert(FName ~= nil and FText ~= nil and type(EObjectFlags) == "table"
           and type(EObjectFlags.RF_Transient) == "number", "missing constructors/flags")
    assert(EngineTickAvailable == true and type(EGameThreadMethod) == "table", "missing game-thread dispatch")
    local modifiers = {ModifierKey.CONTROL,ModifierKey.ALT}
    assert(not IsKeyBindRegistered(Key.F6,modifiers), "Ctrl+Alt+F6 collision")
    RegisterKeyBind(Key.F6,modifiers,function()
        local queued, problem = pcall(ExecuteInGameThread,control,EGameThreadMethod.EngineTick)
        if not queued then log("DISPATCH_FAILED", tostring(problem):sub(1,240)) end
    end)
end)
if ok then log("ARMED", "key=Ctrl+Alt+F6 one_session=true divider=local-stock-PNG")
else phase="stopped"; log("UNAVAILABLE", tostring(err):sub(1,240)) end
