# SPDX-License-Identifier: MPL-2.0
"""Native selected input preflight is read-only and fails closed."""
from pathlib import Path
import unittest
from lupa import LuaRuntime
MODULE = (Path(__file__).resolve().parents[1] /
          "research/interaction-prompts-owner/world-space/tiphud-render-suppression/IIPSelectedHintPreflight.lua")
RIG=r'''
local function obj(path,cls,id)
 local o={path=path,cls=cls,id=id}
 function o:IsValid()return true end
 function o:GetAddress()return self.id end
 function o:GetFullName()return "Object "..self.path end
 function o:GetClass()return {GetFullName=function()return "Class "..self.cls end}end
 return o
end
actor=obj("Actor","Npc",1)
source=obj("Extended","Component",2)
widget=obj("TipHUD","TipHUD",3)
actor.ExtendedWidget=source
function source:GetOwner()return actor end
function source:GetUserWidgetObject()return widget end
widget.CanHoldPress=false
widget.CanvasPanel_2=obj("Locked","CanvasPanel",4)
widget.CanvasPanel_2.Visibility=1
widget.player=obj("PC","Controller",5)
function widget:GetOwningPlayer()return self.player end
function widget.player:GetNowInputControllerType()return 1 end
local i=obj("Image","/Script/UMG.Image",6)
widget.ImageInteractAllowed=i
i.bFlipForRightToLeftFlowDirection=false
i.RenderTransform={Translation={X=0,Y=0},Scale={X=1,Y=1},Shear={X=0,Y=0},Angle=0}
i.ColorAndOpacity={R=1,G=1,B=1,A=1}
i.Brush={DrawAs=3,Tiling=0,Mirroring=0,ImageType=0,ImageSize={X=64,Y=64},
 UVRegion={bIsValid=0},Margin={Left=0,Top=0,Right=0,Bottom=0},
 TintColor={ColorUseRule=0,SpecifiedColor={R=1,G=1,B=1,A=1}},
 ResourceObject=obj("Input","/Script/Engine.Texture2D",7)}
row={refs={component={address=2},widget={address=3}},hint_state="visible"}
alive=function(o)return o~=nil and o:IsValid()end
'''
class HintPreflight(unittest.TestCase):
 def check(self,code):
  vm=LuaRuntime(unpack_returned_tuples=True)
  vm.execute(RIG)
  vm.globals().Preflight=vm.execute(MODULE.read_text(encoding="utf-8"))
  vm.execute(code)
 def test_direct_candidate_is_not_world_permission(self):
  self.check('''
local s=assert(Preflight.inspect(actor,row,alive))
assert(s:find("hint_gate=direct_brush_candidate",1,true))
assert(s:find("remap_equivalence=UNKNOWN",1,true))
assert(s:find("geometry_occlusion=UNKNOWN",1,true))
''')
 def test_all_non_direct_states_fail_closed(self):
  self.check('''
widget.CanHoldPress=true
assert(Preflight.inspect(actor,row,alive):find("hint_gate=hold",1,true))
widget.CanHoldPress=false;widget.CanvasPanel_2.Visibility=0
assert(Preflight.inspect(actor,row,alive):find("hint_gate=locked",1,true))
widget.CanvasPanel_2.Visibility=1
function widget.player:GetNowInputControllerType()return 3 end
assert(Preflight.inspect(actor,row,alive):find("hint_gate=unsupported_device",1,true))
function widget.player:GetNowInputControllerType()return 1 end
widget.ImageInteractAllowed.Brush.Margin.Left=1
assert(Preflight.inspect(actor,row,alive):find("hint_gate=brush_not_direct",1,true))
''')
 def test_unknowns_and_identity_change_unavailable(self):
  self.check('''
widget.CanHoldPress=nil
local s,why=Preflight.inspect(actor,row,alive)
assert(not s and why=="unavailable")
widget.CanHoldPress=false;source.id=999
s,why=Preflight.inspect(actor,row,alive)
assert(not s and why=="unavailable")
''')
if __name__=="__main__":
 unittest.main()
