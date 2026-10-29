# SPDX-License-Identifier: MPL-2.0
"""Own World component policy/failure tests. No engine rendering/occlusion proof."""
import unittest
from test_beginplay_join import FIXTURE
from test_ui_child import LuaRuntime, ROOT

DIR=ROOT/'research/interaction-prompts-owner/world-space/probe/Scripts'
MAIN=(DIR/'main.lua').read_text(encoding='utf8')
MODULE=(DIR/'IIPWorldChild.lua').read_text(encoding='utf8')
EXTRA=r'''
EObjectFlags.RF_Transient=64
-- Real constructors are callable userdata; non-function callables catch false type guards.
FName=setmetatable({},{__call=function(_,s)return s end});FText=FName
function ExecuteInGameThreadWithDelay(ms,fn)
 assert(S.game and (ms==120000 or ms==45000));S.timers[#S.timers+1]={ms=ms,fn=fn}
end
function owned(p,k,outer)
 local o=make(p,k);setmetatable(o,{__index=S.fields[o],__newindex=function(_,key,v)S.fields[o][key]=v end})
 o.outer=outer;o.GetOuter=function()return outer end;o.GetParent=function()return o.parent end
 o.SetVisibility=function(_,v)o.Visibility=v end
 return o
end
local function class(p,super)
 local c=make(p,'Class');set(c,'type',function()return 'UClass'end)
 set(c,'GetSuperStruct',function()return super end);return c
end
HOST='/Game/MainContent/Template/UMG/Debug/PostionItemUMG_BP.PostionItemUMG_BP_C'
MASK='/Engine/EngineMaterials/Widget3DPassThrough_Masked.Widget3DPassThrough_Masked'
BASEMAT='/Engine/EngineMaterials/Widget3DPassThrough.Widget3DPassThrough'
class(HOST,class('/Script/UMG.UserWidget'));class('/Script/UMG.WidgetComponent');class('/Script/UMG.TextBlock')
local base=owned(BASEMAT,'/Script/Engine.Material');base.bDisableDepthTest=false
local stock=owned(MASK,'/Script/Engine.MaterialInstanceConstant');stock.Parent=base
stock.BasePropertyOverrides={bOverride_BlendMode=true,BlendMode=1,bOverride_TwoSided=true,TwoSided=true}
S.stock=stock;S.base=base
local function static(p,fn)
 local f=make(p,'Function');set(f,'type',function()return 'UFunction'end)
 setmetatable(f,{__index=S.fields[f],__call=function(_,cdo,...)assert(S.game and cdo);return fn(...)end})
end
for _,library in ipairs({'KismetSystemLibrary','KismetMathLibrary'})do
 make('/Script/Engine.Default__'..library,'/Script/Engine.'..library)
end
static('/Script/Engine.KismetSystemLibrary:IsValid',function(o)return o and o.live and not o.pending or false end)
static('/Script/Engine.KismetMathLibrary:FindLookAtRotation',function(a,b)return {Pitch=0,Yaw=90,Roll=0}end)
static('/Script/Engine.KismetMathLibrary:MakeTransform',function(p,r,s)return {position=p,rotation=r,scale=s}end)
make('/Script/UMG.Default__WidgetBlueprintLibrary','/Script/UMG.WidgetBlueprintLibrary')
function font(size,id)return {Size=size,GetStructAddress=function()return id end}end
local function slot(ch,pa)
 local o=owned(ch.p..'.Slot','/Script/UMG.CanvasPanelSlot',pa);o.Parent=pa;o.Content=ch;ch.Slot=o;ch.parent=pa
 for _,name in ipairs({'SetAnchors','SetAlignment','SetPosition','SetSize','SetAutoSize'})do o[name]=function()end end
 return o
end
local function canvas(p,t)
 local o=owned(p,'/Script/UMG.CanvasPanel',t);o.children={}
 o.GetChildrenCount=function()return #o.children end;o.GetChildAt=function(_,i)return o.children[i+1]end
 o.AddChildToCanvas=function(_,ch)o.children[#o.children+1]=ch;return slot(ch,o)end
 o.RemoveChild=function(_,ch)
  for i,v in ipairs(o.children)do if v==ch then table.remove(o.children,i);ch.parent=nil;return true end end
  return false
 end;return o
end
static('/Script/UMG.WidgetBlueprintLibrary:Create',function(ctx,k)
 S.created=(S.created or 0)+1
 local w=owned('/Transient.OwnHost',HOST);S.host=w;w.Visibility=4
 local t=owned(w.p..'.Tree','/Script/UMG.WidgetTree',w);local r=canvas(t.p..'.Root',t)
 local m=canvas(t.p..'.Main',t);local v=owned(t.p..'.Value','/Script/UMG.TextBlock',t)
 local im=owned(t.p..'.Image','/Script/UMG.Image',t)
 r.children={m};m.children={v,im};slot(m,r);slot(v,m);slot(im,m)
 v.Font=font(14,100);t.RootWidget=r;w.WidgetTree=t;w.Value_Text=v;w.Bg_Image=im
 if S.bad_tree then m.children={}end
 w.IsInViewport=function()return false end;w.RemoveFromParent=function()S.host_removed=true end
 return w
end)
function LoadAsset()error('unexpected load: all exact assets present in fixture')end
function StaticConstructObject(k,outer,name,flags)
 assert(S.game and flags==64)
 local p=k:GetFullName():match('^[^ ]+ (.+)$')
 local o=owned(outer.p..'.'..name,p,outer);o.flags=flags
 if p=='/Script/UMG.WidgetComponent'then
  S.comp=o;S.owned=true;o.CreationMethod=0;o.BlendMode=1;o.GeometryMode=0;o.bVisible=true;o.bHiddenInGame=false
  o.GetOwner=function()return outer end;o.GetWidget=function()return o.widget end
  o.SetWidget=function(_,w)
   if S.detach_fail and not w then error('detach failed')end
   o.widget=w;if w then w.Visibility=S.no_construct and 4 or 2 end
  end
  o.SetWidgetSpace=function(_,v)assert(not o.registered);o.space=v end;o.GetWidgetSpace=function()return o.space end
  o.SetTwoSided=function(_,v)assert(not o.registered);o.twosided=v end
  o.SetDrawSize=function(_,v)assert(not o.registered);o.draw=v end;o.GetDrawSize=function()return o.draw end
  o.GetCurrentDrawSize=function()return o.draw end;o.SetPivot=function(_,v)assert(not o.registered);o.pivot=v end
  o.SetCollisionEnabled=function(_,v)assert(not o.registered);o.collision=v end;o.GetCollisionEnabled=function()return o.collision end
  o.SetGenerateOverlapEvents=function(_,v)assert(not o.registered);o.overlaps=v end;o.GetGenerateOverlapEvents=function()return o.overlaps end
  o.SetWindowFocusable=function(_,v)assert(not o.registered);o.focus=v end;o.GetWindowFocusable=function()return o.focus end
  o.SetTickWhenOffscreen=function(_,v)assert(not o.registered);o.tickoff=v end
  o.SetMaterial=function(_,i,m)
   assert(not o.registered and i==0);o.mat=m
   o.mid=owned(o.p..'.MID','/Script/Engine.MaterialInstanceDynamic',o);o.mid.Parent=m
  end
  o.GetMaterial=function()return o.mat end;o.GetMaterialInstance=function()return o.mid end
  o.GetRenderTarget=function()return o.rt end;o.GetAttachParent=function()return nil end
  o.K2_GetComponentLocation=function()return o.transform.position end
  o.K2_GetComponentRotation=function()return o.transform.rotation end
  o.K2_GetComponentScale=function()return o.transform.scale end
  o.K2_DestroyComponent=function(_,caller)
   assert(caller==o);S.destroys=(S.destroys or 0)+1
   if not S.destroy_fail then o.pending=true;S.owned=false;o.registered=false end
  end
 else
  assert(p=='/Script/UMG.TextBlock');S.label=o
  o.SetFont=function(_,v)o.Font=font(v.Size,200)end;o.SetJustification=function()end
  o.SetText=function(_,v)o.Text=v end;o.SetColorAndOpacity=function(_,v)o.color=v end
 end
 return o
end
set(P.actor,'RootComponent',make(P.actor.p..'.Root','/Script/Engine.SceneComponent'))
set(P.widget,'WidgetTree',make(P.widget.p..'.Tree','/Script/UMG.WidgetTree'))
local cam=make('/World.Camera','/Script/Engine.PlayerCameraManager')
set(cam,'GetCameraLocation',function()return {X=100,Y=200,Z=300}end)
set(P.widget,'GetOwningPlayerCameraManager',function()return cam end)
set(P.actor,'FinishAddComponent',function(_,c,manual,t)
 assert(c==S.comp and manual and not c.registered and c.space==0 and c.collision==0 and not c.overlaps)
 assert(not c.bReceiveHardwareInput and not c.focus and c.twosided and c.draw.X==512 and c.draw.Y==128)
 assert(c.mat==S.stock and c.widget==S.host and S.host.Visibility==3 and S.label.Text=='WORLD TEST')
 assert(t.position.Z==62 and t.scale.X==0.25);c.transform=t;c.registered=true
 if S.finish_fail then error('partial native registration')end
end)
function frame()
 S.game=true;S.comp.rt=owned(S.comp.p..'.RT','/Script/Engine.TextureRenderTarget2D',S.comp)
 S.comp.rt.SizeX=512;S.comp.rt.SizeY=128;S.game=false
end
function start()key();begin();show()end
function timeout(ms)S.game=true;for _,t in ipairs(S.timers)do if t.ms==ms then t.fn()end end;S.game=false end
'''

class WorldChildPolicy(unittest.TestCase):
    def case(self,code,setup=''):
        lua=LuaRuntime(unpack_returned_tuples=True)
        lua.execute(FIXTURE+EXTRA)
        lua.execute('package.preload["IIPWorldChild"]=function()\n'+MODULE+'\nend')
        lua.execute(setup);lua.execute(MAIN)
        try:lua.execute(code)
        except Exception:
            print(list(lua.globals().S.logs.values()));raise

    def test_owned_registration_render_pending_then_state_and_native_cleanup(self):
        self.case('''start();assert(S.created==1 and S.comp.registered and S.owned)
        assert(has('RENDER_PENDING') and not has('event=STATE'))
        frame();key();assert(has('event=STATE') and S.label.Font.Size==36)
        key(7);assert(has('CLEANED') and has('hooks_remaining=0') and not S.owned)
        S.game=true;assert(S.comp:IsValid() and S.comp.pending);S.game=false
        assert(S.destroys==1 and S.host_removed and not S.label.parent)
        timeout(45000);timeout(120000);show();assert(S.created==1 and S.destroys==1)''')

    def test_depth_override_rejected_before_allocation(self):
        self.case("start();assert(has('stock depth contract differs') and not S.comp)","S.base.bDisableDepthTest=true")

    def test_wrong_material_blend_rejected(self):
        self.case("start();assert(has('expected masked') and not S.comp)","S.stock.BasePropertyOverrides.BlendMode=2")

    def test_bad_tree_rolls_back_component_and_own_host(self):
        self.case("start();assert(has('host placeholder') and has('CLEANED') and S.host_removed and not S.owned)","S.bad_tree=true")

    def test_construct_mismatch_never_registers(self):
        self.case("start();assert(has('first own Slate') and has('CLEANED') and not S.comp.registered)","S.no_construct=true")

    def test_partial_registration_is_destroyed(self):
        self.case("start();assert(has('partial native registration') and has('CLEANED') and S.comp.pending)","S.finish_fail=true")

    def test_pending_kill_check_failure_retains_retry(self):
        self.case("start();key(7);assert(has('CLEANUP_PENDING') and S.owned);S.destroy_fail=false;key(7);assert(has('CLEANED') and not S.owned)","S.destroy_fail=true")

    def test_detach_failure_preserves_cleanup_retry(self):
        self.case("start();key(7);assert(has('CLEANUP_PENDING') and S.owned);S.detach_fail=false;key(7);assert(has('CLEANED') and not S.owned)","S.detach_fail=true")

    def test_source_disappears_cleanup_does_not_need_foreign_objects(self):
        self.case("start();set(P.actor,'live',false);show();assert(has('FAILED') and has('CLEANED') and not S.owned)")

    def test_anchor_movement_stops_fixed_pose_experiment(self):
        self.case("start();set(P.component,'x',11);show();assert(has('source anchor moved') and has('CLEANED'))")

    def test_natural_hide_cleans_up_without_native_prompt_write(self):
        self.case("start();set(P.widget,'Visibility',2);show();assert(has('reason=target_not_visible') and has('CLEANED'))")

    def test_no_matching_widget_never_allocates(self):
        self.case("key();show();timeout(120000);assert(not S.comp and has('hooks_remaining=0'))")

    def test_timeout_destroys_only_own_component(self):
        self.case("start();timeout(45000);assert(has('reason=world_timeout') and has('CLEANED') and not S.owned)")

    def test_hidden_own_component_is_failure_not_occlusion(self):
        self.case("start();S.comp.bHiddenInGame=true;key();assert(has('own visible state changed') and has('CLEANED'))")

    def test_inert_no_retarget_no_recreation_and_four_snapshot_cap(self):
        self.case("start();show();show();assert(S.created==1);frame();key();key();key();assert(has('reason=pose_budget'));key();assert(S.created==1)")

    def test_missing_factory_fails_before_allocation(self):
        self.case("start();assert(has('missing World API') and not S.comp)","StaticConstructObject=nil")

if __name__=='__main__':unittest.main()
