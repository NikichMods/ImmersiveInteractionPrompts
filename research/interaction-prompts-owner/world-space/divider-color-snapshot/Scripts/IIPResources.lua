-- SPDX-License-Identifier: MPL-2.0
-- Reused private font/ornament seams; no shared font mutation; authored divider PNG is distributed.
local M={}
local ttf_filename,png_filename,import_attempted
local FONT="/Script/Engine.Font"
local DONOR="/Game/Fonts/EBGaramond-SemiBold_Font.EBGaramond-SemiBold_Font"
local function log(e,s)print("IIP_COMPOSITION_RESOURCE event="..e.." "..(s or "").."\n")end
local function valid(o)return o~=nil and o:IsValid()end
local function path(o)return assert(o:GetFullName():match("^[^ ]+ (.+)$"))end
local function cls(o)return path(o:GetClass())end
local function same(a,b)return valid(a) and valid(b) and a:GetAddress()==b:GetAddress()end
local function remember(o)return {path=path(o),class=cls(o),address=o:GetAddress()}end
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
    log("IMPORT_BEGIN", "size=256x32 once=true")
    -- StaticFindObject yields an unbound UFunction. First argument is its explicit calling CDO.
    local texture = fn(cdo,widget,png_filename)
    assert(valid(texture) and cls(texture) == "/Script/Engine.Texture2D", "import returned no Texture2D")
    assert(texture:HasAnyFlags(EObjectFlags.RF_Transient), "imported texture is not transient")
    assert(texture:Blueprint_GetSizeX() == 256 and texture:Blueprint_GetSizeY() == 32,
           "imported dimensions mismatch")
    image:SetColorAndOpacity({R=1,G=1,B=1,A=1})
    image:SetBrushFromTexture(texture,false) -- Own fixed slot, authored PNG aspect ratio.
    assert(same(image.Brush.ResourceObject,texture) and image.Brush.DrawAs == 3
        and image.Brush.TintColor.ColorUseRule == 0 and image.Brush.TintColor.SpecifiedColor.A == 1,
           "texture brush reference not established")
    log("TEXTURE_BOUND", "size=256x32 brush_ref=true transient=true")
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


function M.prepare()
 local c=require("IIPLiveConfig")
 for _,k in ipairs({"filename","separator_filename"})do
  assert(type(c[k])=="string" and #c[k]>0 and #c[k]<=1024,"missing local resource path: "..k)
 end
 ttf_filename,png_filename=c.filename,c.separator_filename
 check_file();validate_png()
end
M.font=configure_font
M.ornament=configure_line
return M
