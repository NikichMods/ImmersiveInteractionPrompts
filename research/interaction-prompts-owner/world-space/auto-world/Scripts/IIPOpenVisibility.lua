-- SPDX-License-Identifier: MPL-2.0
-- Read-only native visibility seam adapted from the verified TipHUD hint chain.
-- No native CanShow result is synthesized and no source opacity is written.
local M={}
local function valid(o)return o~=nil and o:IsValid()end
local function path(o)return assert(o:GetFullName():match("^[^ ]+ (.+)$"))end
local function cls(o)return path(o:GetClass())end
local function same(a,b)
    return valid(a) and valid(b) and a:GetAddress()==b:GetAddress()
end
local function shown(o,alive)
    if not alive(o)then return false end
    return (o.Visibility==0 or o.Visibility==3 or o.Visibility==4)
        and o.RenderOpacity==1 and o.bIsEnabled==true
end
function M.visible(w,alive)
    assert(type(alive)=="function" and valid(w),"TipHUD visibility source unavailable")
    if not shown(w,alive)then return false end
    local text=w.TextBlock_89
    if not shown(text,alive)then return false end
    assert(cls(text)=="/Script/UMG.TextBlock","TipHUD localized label class changed")
    local tree=w.WidgetTree
    assert(alive(tree) and cls(tree)=="/Script/UMG.WidgetTree","TipHUD tree missing")
    local retainer=StaticFindObject(path(tree)..".RetainerBox_0")
    assert(alive(retainer) and cls(retainer)=="/Script/UMG.RetainerBox"
        and same(retainer:GetOuter(),tree),"native RetainerBox owner changed")
    local chain=retainer
    for i=1,8 do
        if not shown(chain,alive)then return false end
        local parent=chain:GetParent()
        if not valid(parent)then
            assert(same(chain,tree.RootWidget),"RetainerBox ancestry root mismatch")
            break
        end
        assert(i<8,"RetainerBox ancestry bound")
        chain=parent
    end
    assert(retainer:GetChildrenCount()==1,"native RetainerBox leaf count")
    local leaf=retainer:GetChildAt(0)
    assert(alive(leaf) and cls(leaf)=="/Script/UMG.Image"
        and same(leaf:GetParent(),retainer),"native hint leaf identity changed")
    return shown(leaf,alive)
end
return M
