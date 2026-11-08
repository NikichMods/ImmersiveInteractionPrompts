-- SPDX-License-Identifier: MPL-2.0
-- One exact Open from the first-show video. Only primitive identities survive a callback.
local M={}
local TARGET="/Game/MainContent/Maps/sublevel_plot/0-1/0-1_plot_outerRimA_interact1.0-1_plot_outerRimA_interact1:PersistentLevel.0-1_lootbox_01_mat_ST001"

local function probe(read)
    local ok,value=pcall(read)
    return ok and value~=nil and tostring(value) or "unknown"
end

local function color(value)
    local result={}
    for _,k in ipairs({"R","G","B","A"}) do
        local v=value[k]
        assert(type(v)=="number" and v==v and math.abs(v)<math.huge)
        result[#result+1]=string.format("%.9g",v)
    end
    return table.concat(result,",")
end

function M.new(source,alive,path,key,hint_visible,emit)
    local early,episode,selected,screen_done,reads=nil,0,false,false,0
    local function id(o)
        return alive(o) and key(o) or "-"
    end
    local function capture(a,c)
        local result={actor=key(a),address=a:GetAddress(),component=id(c),widget="-",replacement="-",getter="-"}
        if not alive(c) then return result,"component_missing" end
        result.widget=id(c.Widget)
        result.replacement=id(c.NewUserWidget)
        local w=c:GetUserWidgetObject()
        result.getter=id(w)
        local ok,record,why=pcall(source.acquire,a)
        local pair=ok and record and record.widget==result.getter and record.component==result.component
        local fields={
            "action="..probe(function()return a.TipHUDArgument.msgTag:ToString() end),
            "visible="..tostring(c.bVisible),"added="..tostring(c.bAddedToScreen),
            "space="..probe(function()return c:GetWidgetSpace() end),
            "reciprocal="..tostring(pair==true),
        }
        if not pair then
            fields[#fields+1]="pair_reason="..string.format("%q",ok and tostring(why) or tostring(record):sub(1,125))
            return result,table.concat(fields," ")
        end
        fields[#fields+1]="hold="..probe(function()return w.CanHoldPress end)
        fields[#fields+1]="lock_panel="..probe(function()return w.CanvasPanel_2.Visibility end)
        fields[#fields+1]="allowed_leaf="..probe(function()return w.ImageInteractAllowed.Visibility end)
        fields[#fields+1]="device="..probe(function()return w:GetOwningPlayer():GetNowInputControllerType() end)
        fields[#fields+1]="brush="..probe(function()return string.format("%q",id(w.ImageInteractAllowed.Brush.ResourceObject)) end)
        fields[#fields+1]="brush_shape="..probe(function()
            local b=w.ImageInteractAllowed.Brush
            return table.concat({b.ImageSize.X,b.ImageSize.Y,b.DrawAs,b.TintColor.ColorUseRule},",")
        end)
        fields[#fields+1]="uv="..probe(function()
            local uv=w.ImageInteractAllowed.Brush.UVRegion
            if uv.bIsValid==0 then return "unset" end
            assert(uv.bIsValid==1)
            return table.concat({uv.Min.X,uv.Min.Y,uv.Max.X,uv.Max.Y},",")
        end)
        fields[#fields+1]="rgba="..probe(function()return color(w.ColorAndOpacity) end)
        fields[#fields+1]="binding="..probe(function()
            local d=w.ColorAndOpacityDelegate
            assert(type(d)=="table" and d.Object~=nil)
            local fn=d.FunctionName:ToString()
            return d.Object:IsValid()==false and d.Object:GetAddress()==0 and fn=="None" and "empty" or "present"
        end)
        return result,table.concat(fields," ")
    end
    local function snapshot(event,a,c)
        local result,fields=capture(a,c)
        local same=early and early.getter~="-" and result.actor==early.actor
            and result.component==early.component and result.getter==early.getter
            and result.widget==early.widget and result.replacement==early.replacement
        emit(event,"episode="..episode.." early_match="..(early and tostring(same==true) or "unknown")
            .." actor="..string.format("%q",result.actor).." component="..string.format("%q",result.component)
            .." widget="..string.format("%q",result.widget).." getter="..string.format("%q",result.getter)
            .." replacement="..string.format("%q",result.replacement).." "..fields)
        return result
    end
    local function guard(fn,...)
        local ok,err=pcall(fn,...)
        if not ok then
            screen_done=true
            emit("UNAVAILABLE","reason="..string.format("%q",tostring(err):sub(1,150)))
        end
    end
    return {
        begin=function(a)
            if path(a)~=TARGET then return end
            if early and early.address==a:GetAddress() then return end
            guard(function()early=snapshot("BEGIN",a,a.ExtendedWidget)end)
        end,
        reset=function()
            early,episode,selected,screen_done,reads=nil,0,false,false,0
        end,
        ended=function(address)
            if early and early.address==address then early=nil end
            if selected==address then selected,screen_done,reads=false,false,0 end
        end,
        read=function(a)
            if not a or path(a)~=TARGET then
                selected,screen_done,reads=false,false,0
                return
            end
            local address=a:GetAddress()
            if selected~=address then selected,screen_done,reads=false,false,0 end
            if episode>=2 and not selected then return end
            if screen_done then return end
            guard(function()
                local c=a.ExtendedWidget
                if not selected then
                    selected=address
                    episode=episode+1
                    snapshot("SELECTED",a,c)
                end
                if screen_done then return end
                reads=reads+1
                if reads>120 then
                    screen_done=true
                    emit("SCREEN_UNOBSERVED","episode="..episode)
                elseif alive(c) and c.bAddedToScreen==true and c.bVisible==true then
                    local ok,r=pcall(source.acquire,a)
                    local visible_ok,visible=false,false
                    if ok and r then visible_ok,visible=pcall(hint_visible,c:GetUserWidgetObject()) end
                    if visible_ok and visible==true then
                        screen_done=true
                        snapshot("SCREEN_READY",a,c)
                    end
                end
            end)
        end,
    }
end
return M
