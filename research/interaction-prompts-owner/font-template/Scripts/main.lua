-- SPDX-License-Identifier: MPL-2.0
-- Research only: one read-only inspection of one newly constructed UFont. No font/UI writes.
local FONT = "/Script/Engine.Font"
local DONOR = "/Game/Fonts/EBGaramond-SemiBold_Font.EBGaramond-SemiBold_Font"
local attempted = false
local function log(event, detail)
    print("IIP_FONT_TEMPLATE event=" .. event .. " " .. (detail or "") .. "\n")
end
local function valid(o) return o ~= nil and o:IsValid() end
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
    assert(valid(face) and class(face) == "Class /Script/Engine.FontFace", "expected FontFace")
    state.face = address(face:GetAddress()) -- Shared immutable reference is expected.
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
    return state
end
local function equal(a,b,keys)
    for _,key in ipairs(keys) do assert(a[key] == b[key], "mismatch: " .. key) end
end
local STORAGE = {"composite","typeface","array","data","entry","font_data",
                 "fallback","fallback_typeface","fallback_array","subtypes"}
local VALUES = {"face","filename","hinting","loading","subface"}
local function run()
    local donor, before, stage = nil, nil, "lookup"
    local ok, err = pcall(function()
        donor = StaticFindObject(DONOR)
        if not valid(donor) then log("NOT_LOADED","donor=true no_load_attempted=true"); return end
        assert(donor:GetFullName() == "Font " .. DONOR, "donor identity differs")
        before = snapshot(donor)
        local font_class, outer = StaticFindObject(FONT), donor:GetOuter()
        assert(valid(font_class) and font_class:type() == "UClass"
            and font_class:GetFullName() == "Class " .. FONT, "Font class NOT_LOADED")
        assert(valid(outer) and class(outer) == "Class /Script/CoreUObject.Package", "unexpected donor outer")
        local outer_path = assert(outer:GetFullName():match("^Package (.+)$"))
        local name = "IIP_FontTemplate_" .. tostring(os.time())
        local copy_path = outer_path .. "." .. name
        assert(not valid(StaticFindObject(copy_path)), "copy name collision")
        stage = "construct"
        log("CREATE_BEGIN","template_arg=8 once=true")
        -- Explicit optional arguments 5,6,7 are required to reach Template at position8.
        local copy = StaticConstructObject(font_class,outer,FName(name),EObjectFlags.RF_Transient,
                                          0,false,false,donor)
        assert(valid(copy) and address(copy:GetAddress()) ~= before.object, "copy is absent or donor alias")
        assert(copy:GetFullName() == "Font " .. copy_path and class(copy) == "Class " .. FONT,
               "copy identity/class differs")
        assert(copy:HasAnyFlags(EObjectFlags.RF_Transient), "copy is not transient")
        assert(copy:GetOuter():GetAddress() == outer:GetAddress(), "copy outer differs")
        log("CREATED","transient=true separate_object=true")
        stage = "isolation"
        local after = snapshot(copy)
        equal(before,after,VALUES)
        log("STORAGE_ADDRESSES", "header=" .. before.array .. "/" .. after.array
            .. " data=" .. before.data .. "/" .. after.data
            .. " entry=" .. before.entry .. "/" .. after.entry
            .. " font_data=" .. before.font_data .. "/" .. after.font_data)
        for _,key in ipairs(STORAGE) do
            assert(before[key] ~= after[key], "shared storage: " .. key)
        end
        log("STORAGE_DISTINCT", "array_header=true array_data=true entry=true font_data=true shared_face=true")
        -- Only scalar results survive this scope. No read/write of raw memory at any address.
    end)
    if not ok then log("FAILED","stage=" .. stage .. " " .. tostring(err):sub(1,200)) end
    local unchanged = true
    if before then
        unchanged = pcall(function()
            local current = snapshot(donor)
            equal(before,current,{"object"}); equal(before,current,STORAGE); equal(before,current,VALUES)
        end)
        log(unchanged and "DONOR_UNCHANGED" or "DONOR_CHECK_FAILED","observed_fields_only=true")
    end
    log("DONE","result=" .. (not before and (ok and "NOT_LOADED" or "FAILED")
        or (ok and unchanged and "STORAGE_CHECK_PASS" or "FAILED"))
        .. " font_data_writes=0 ui_writes=0 retained_objects=0 gc_forced=false")
    -- No roots, persistent UObject wrappers, FontInfo/UI attachment or manual Destroy/GC.
    -- The one unreferenced transient copy is left for normal engine GC, not claimed collected.
end
local ok, err = pcall(function()
    for _,key in ipairs({"StaticFindObject","StaticConstructObject","RegisterKeyBind",
                          "IsKeyBindRegistered","ExecuteInGameThread"}) do
        assert(type(_G[key]) == "function", "missing API: " .. key)
    end
    assert(FName ~= nil and type(EObjectFlags) == "table"
        and type(EObjectFlags.RF_Transient) == "number", "missing constructor/flags")
    assert(EngineTickAvailable == true and type(EGameThreadMethod) == "table", "game-thread dispatch unavailable")
    local modifiers = {ModifierKey.CONTROL,ModifierKey.ALT}
    assert(not IsKeyBindRegistered(Key.F7,modifiers), "Ctrl+Alt+F7 collision")
    RegisterKeyBind(Key.F7,modifiers,function()
        if attempted then return end
        attempted = true -- Before dispatch: rapid repeated keys cannot queue duplicate copies.
        local queued, problem = pcall(ExecuteInGameThread,run,EGameThreadMethod.EngineTick)
        if not queued then log("DISPATCH_FAILED",tostring(problem):sub(1,200)) end
    end)
end)
if ok then log("ARMED","key=Ctrl+Alt+F7 one_attempt=true no_ffontdata_writes=true")
else log("UNAVAILABLE",tostring(err):sub(1,200)) end
