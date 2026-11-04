-- SPDX-License-Identifier: MPL-2.0
-- Bounded collision check, not certification of all raw-input consumers.
local M={}
local Bindings=require("IIPKeyboardBindings")
local Tuning=require("IIPTuning")
local fields={Multiply="MULTIPLY",NumPadZero="NUM_ZERO",NumPadOne="NUM_ONE",NumPadTwo="NUM_TWO",
 NumPadThree="NUM_THREE",NumPadFour="NUM_FOUR",NumPadFive="NUM_FIVE",NumPadSix="NUM_SIX",
 NumPadSeven="NUM_SEVEN",NumPadEight="NUM_EIGHT",NumPadNine="NUM_NINE"}
local function valid(o)return o~=nil and o:IsValid()end
function M.check(w)
 local reserved={F11=true}
 for _,name in ipairs(Tuning.keys)do
  local key=Key[fields[name]]
  assert(type(key)=="number" and not IsKeyBindRegistered(key),"NumPad UE4SS conflict: "..name)
  reserved[name]=true
 end
 local f=StaticFindObject("/Script/Genesis.GameGlobal:GetKeyByVirtualKey")
 local cdo=StaticFindObject("/Script/Genesis.Default__GameGlobal")
 assert(valid(f) and f:type()=="UFunction" and f:GetFullName()=="Function /Script/Genesis.GameGlobal:GetKeyByVirtualKey"
  and valid(cdo) and cdo:GetFullName()=="GameGlobal /Script/Genesis.Default__GameGlobal","current-key resolver unavailable")
 for _,id in ipairs(Bindings)do
  local key=f(cdo,FName(id))
  assert(type(key)=="table" and key.KeyName~=nil,"current FKey result shape")
  assert(not reserved[key.KeyName:ToString()],"current game-key conflict: "..id)
 end
 local native=StaticFindObject("/Script/Engine.PlayerController:IsInputKeyDown")
 assert(valid(native) and native:type()=="UFunction","native polling unavailable")
 local pc=w:GetOwningPlayer();assert(valid(pc),"editor player unavailable")
 local down=pc:IsInputKeyDown({KeyName=FName("NumPadEight")})
 assert(type(down)=="boolean","native polling result shape")
 print("IIP_EDITOR_INPUT event=AUDIT_PASS current_keyboard_actions="..#Bindings
  .." raw_polling_conflicts_unobservable=true no_input_consumption=true\n")
end
return M
