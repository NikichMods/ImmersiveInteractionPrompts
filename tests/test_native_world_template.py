# SPDX-License-Identifier: MPL-2.0
"""Source-only mock for shared SCS template trial; no native inheritance is simulated."""
import unittest
from lupa import LuaRuntime
from test_ui_child import ROOT

SRC=(ROOT/"research/interaction-prompts-owner/world-space/native-world-template/Scripts/main.lua").read_text(encoding="utf8")
FIXTURE=r"""
S={logs={},objects={},coll=1,keys={},queue={},load=0}
EngineTickAvailable=true; EGameThreadMethod={EngineTick=1};Key={F5=5}
PACKAGE="/Game/MainContent/Template/BaseBlueprint/BaseGameEventObject_BP"
GENERATED_CLASS=PACKAGE..".BaseGameEventObject_BP_C"
TEMPLATE=GENERATED_CLASS..":ExtendedWidget_GEN_VARIABLE"
local level="/Game/MainContent/Maps/sublevel_plot/0-1/0-1_plot_outerRimA_interact1.0-1_plot_outerRimA_interact1:PersistentLevel."
OPEN=level.."0-1_lootbox_01_mat_ST001"
TAKE=level.."0-1_item_loot_bag_03_AP1_3"
local function obj(path,class,id)
    local x={p=path,c=class,id=id,Space=1}
    function x:IsValid()return true end
    function x:GetFullName()return "Object "..self.p end
    function x:GetAddress()return self.id end
    function x:GetClass()return {IsValid=function()return true end,
        GetFullName=function()return "Class "..self.c end}end
    return x
end
S.make=obj
COMP="/Script/Genesis.ExtendedWidgetComponent"
S.template=obj(TEMPLATE,COMP,1)
function S.template:GetCollisionEnabled()return S.coll end
function S.template:SetCollisionEnabled(v)if not S.reject then S.coll=v end end
S.actor=obj(OPEN,"/Game/MainContent/Act/Discoveries_BP/common/item_lootbox02.item_lootbox02_C",2)
S.comp=obj(OPEN..".ExtendedWidget",COMP,3)
S.actor.ExtendedWidget=S.comp
function S.comp:GetOwner()return S.actor end
function S.comp:GetCollisionEnabled()return 1 end
function S.comp:GetUserWidgetObject()return S.widget end
function S.comp:GetRenderTarget()return S.rt end
S.comp.bAddedToScreen=true
S.widget=obj("/Transient.TipHUD","/Game/MainContent/Template/UMG/TipHUD.TipHUD_C",4)
S.objects[TEMPLATE]=S.template;S.objects[OPEN]=nil
function StaticFindObject(p)return S.objects[p]end
function LoadAsset(p)
    S.load=S.load+1
    if p~=GENERATED_CLASS then return nil,false,false end
    S.objects[TEMPLATE]=S.template
    return S.template,true,true
end
function print(x)table.insert(S.logs,x)end
function has(s)for _,l in ipairs(S.logs)do if l:find(s,1,true)then return true end end return false end
function RegisterBeginPlayPostHook(fn)S.begin=fn end
function ExecuteInGameThread(fn,m)assert(m==1);table.insert(S.queue,fn)end
function IsKeyBindRegistered(k)return false end
function RegisterKeyBind(k,fn)S.keys[k]=fn end
function flush()
    while #S.queue>0 do local q=S.queue;S.queue={}
        for _,fn in ipairs(q)do fn()end end
end
"""
class TemplateWorldTrial(unittest.TestCase):
    def run_case(self,s,source=SRC):
        lua=LuaRuntime()
        lua.execute(FIXTURE)
        lua.execute(s.replace("{{LOAD_SOURCE}}",source))
    def test_single_template_write_and_subsequent_sampling_no_actor_write(self):
        self.run_case("""
        S.objects[TEMPLATE]=nil
        {{LOAD_SOURCE}}
        flush()
        assert(S.load==1 and S.template.Space==0 and S.coll==0)
        assert(S.comp.Space==1)
        assert(has("TEMPLATE_WORLD"))
        S.objects[OPEN]=S.actor
        S.begin({get=function()return S.actor end})
        assert(has("PLACED_BEGIN action=Open template_status=WRITTEN space=1"))
        S.keys[5]();flush()
        assert(has("PLACED_SAMPLE action=Open template_status=WRITTEN space=1"))
        """)
    def test_existing_shared_template_does_not_load_asset_again(self):
        self.run_case("""
        {{LOAD_SOURCE}}
        flush()
        assert(S.load==0 and S.template.Space==0 and S.coll==0)
        assert(has("TEMPLATE_WORLD"))
        """)

    def test_styling_accepts_native_world_outside_diagnostic_allowlist(self):
        case="""
        local npc=S.make("/Game/Test.Level:NPC","{{CLASS}}",9)
        local native=S.make(npc.p..".ExtendedWidget",COMP,10)
        local argument=S.make(npc.p..".TipHUDArgument","/Script/Genesis.TipHUDArgumentComponent",11)
        local tag="Interact"
        argument.msgTag={ToString=function()return tag end}
        function argument:GetOwner()return npc end
        npc.ExtendedWidget=native
        npc.TipHUDArgument=argument
        function native:GetOwner()return npc end
        function native:GetOuter()return npc end
        function native:GetCollisionEnabled()return 0 end
        function native:GetUserWidgetObject()return S.widget end
        S.objects[native.p]=native
        local can_show=S.widget.c..":CanShow"
        S.objects[can_show]={IsValid=function()return true end,type=function()return "UFunction" end}
        local starts,hooks,facings=0,0,0
        function RegisterHook(path,callback)
            assert(path==can_show)
            hooks=hooks+1
            S.can_show=callback
            return 1,1
        end
        package.preload.IIPTemplateResources=function()return {prepare=function()end} end
        package.preload.IIPTemplateProbe=function()return {} end
        package.preload.IIPTemplateStyle=function()return {
            RGB=.50,
            start=function(component,widget,_,_,_,action)
                assert(component==native and widget==S.widget and action=="Interact")
                starts=starts+1
                return {decorated=true}
            end,
            face_camera=function(component,widget)
                assert(component==native and widget==S.widget and component.bVisible and tag=="Talk")
                facings=facings+1
                return true
            end,
            can_show=function(component,widget,_,_,_,action)
                assert(component==native and widget==S.widget and action==tag)
                S.refreshed=action
            end}
        end
        {{LOAD_SOURCE}}
        flush()
        assert(S.template.Space==0 and native.Space==1)
        local context={get=function()return npc end}
        S.begin(context)
        assert(starts==0 and hooks==0)
        native.Space=0 -- Simulates the original World component created by the host.
        S.begin(context)
        S.begin(context)
        assert(starts==1 and hooks==1 and not has("PLACED_BEGIN"))
        local widget_context={get=function()return S.widget end}
        native.bVisible=true
        S.can_show(widget_context)
        assert(facings==0)
        tag="Talk"
        native.bVisible=false
        S.can_show(widget_context)
        assert(facings==0)
        native.bVisible=true
        assert(S.can_show(widget_context)==nil)
        S.can_show({get=function()return S.widget end})
        assert(facings=={{FACINGS}} and S.refreshed=="Talk")
        assert(argument.msgTag:ToString()=="Talk" and S.comp.Space==1)
        """
        for actor_class, facings in (
            ("/Game/MainContent/Template/BaseBlueprint/NPCInteract_Bp.NPCInteract_Bp_C", 1),
            ("/Game/Test.NonNPC_C", 0),
        ):
            with self.subTest(actor_class=actor_class):
                self.run_case(case.replace("{{CLASS}}", actor_class)
                                  .replace("{{FACINGS}}", str(facings)))

    def test_cold_load_rejects_package_name_and_leaves_template_untouched(self):
        self.run_case("""
        S.objects[TEMPLATE]=nil
        {{LOAD_SOURCE}}
        flush()
        assert(S.load==1 and S.objects[TEMPLATE]==nil)
        assert(S.template.Space==1 and S.coll==1 and S.comp.Space==1)
        assert(has("SKIP reason=template_unavailable_or_identity") and not has("TEMPLATE_WORLD"))
        """,source=SRC.replace("pcall(LoadAsset, GENERATED_CLASS)", "pcall(LoadAsset, PACKAGE)"))

    def test_preexisting_target_never_writes_template(self):
        self.run_case("""
        S.objects[OPEN]=S.actor
        {{LOAD_SOURCE}}
        flush()
        assert(S.load==0 and S.template.Space==1 and S.coll==1)
        assert(has("SKIP reason=target_already_loaded"))
        """)
    def test_failure_is_local_and_keeps_other_components_untouched(self):
        self.run_case("""
        S.reject=true
        {{LOAD_SOURCE}}
        flush()
        assert(S.template.Space==1 and S.coll==1)
        assert(has("REJECTED") and not has("TEMPLATE_WORLD"))
        assert(S.comp.Space==1)
        """)
    def test_missing_or_wrong_template_fails_closed(self):
        self.run_case("""
        S.template.c="/Script/Engine.ActorComponent"
        {{LOAD_SOURCE}}
        flush()
        assert(S.template.Space==1 and S.coll==1)
        assert(has("SKIP reason=template_unavailable_or_identity"))
        """)
    def test_unchanged_during_no_game_thread(self):
        self.run_case("""
        EngineTickAvailable=false
        {{LOAD_SOURCE}}
        assert(S.load==0 and S.template.Space==1 and S.coll==1)
        assert(has("SKIP reason=engine_thread_unavailable"))
        """)
if __name__=="__main__": unittest.main()
