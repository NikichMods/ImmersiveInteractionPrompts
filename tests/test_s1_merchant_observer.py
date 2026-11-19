# SPDX-License-Identifier: MPL-2.0
"""Observer callback/identity tests with no UMG writes."""
import unittest

from test_native_tiphud_s1 import ADDITIONS, FIXTURE, LAYOUT, OVERRIDES, SRC, LuaRuntime

OBSERVER = (SRC / "IIPS1MerchantObserver.lua").read_text(encoding="utf-8")
ENTRY = 'local Layout = require("IIPS1Layout")'
PAYLOAD = OBSERVER.replace(ENTRY, "local Layout = (function()\n" + LAYOUT + "\nend)()")
NPC = r'''
local actor=make("/Game/MainContent/Template/BaseBlueprint/NPCInteract_Bp.NPCInteract_Bp_C","/NPC")
local component=make("/Script/Genesis.ExtendedWidgetComponent","/NPC.ExtendedWidget")
local argument=make("/Script/Genesis.TipHUDArgumentComponent","/NPC.TipHUDArgument")
actor.ExtendedWidget=component
actor.TipHUDArgument=argument
function component:GetOwner() return actor end
function argument:GetOwner() return actor end
argument.msgTag={ToString=function()return S.tag end}
S.tag="Talk"
function component:GetUserWidgetObject() if not S.missing then return w end end
function start_npc()
 S.game=true
 S.beginplay({get=function()return actor end})
 S.game=false
end
function show_npc()
 component.bVisible=true;component.bAddedToScreen=true
 trigger(1)
end
'''


class MerchantObserverTests(unittest.TestCase):
    def logs(self, operations):
        vm = LuaRuntime(unpack_returned_tuples=True)
        vm.execute(FIXTURE + ADDITIONS + OVERRIDES + NPC)
        vm.execute("S.game=true")
        vm.execute(PAYLOAD)
        vm.execute("S.game=false\n" + operations)
        self.assertTrue(vm.eval("original_safe() and S.created==0 and S.attached==0"))
        return list(vm.globals().S.logs.values())

    def test_same_widget_reports_first_failure_and_first_valid_once(self):
        log = self.logs("""
            S.tag="Interact"; S.bad_size=true; start_npc()
            S.tag="Talk"; show_npc(); show_npc()
            S.bad_size=false; show_npc(); show_npc()
        """)
        for event in ("BEGIN_MATCH", "CANSHOW_FIRST", "LAYOUT_FIRST_REJECT",
                      "LAYOUT_FIRST_VALID", "CANSHOW_ELIGIBLE"):
            self.assertEqual(sum(f"event={event} " in line for line in log), 1, log)
        self.assertTrue(any("check=desired_size desired=(0," in line for line in log), log)

    def test_missing_early_widget_cannot_be_claimed_later(self):
        log = self.logs("S.missing=true; start_npc(); S.missing=false; show_npc()")
        self.assertTrue(any("event=BEGIN_MISS " in line for line in log), log)
        self.assertFalse(any("event=CANSHOW_FIRST " in line for line in log), log)

    def test_map_reset_discards_old_identity(self):
        log = self.logs("start_npc(); travel(); show_npc()")
        self.assertFalse(any("event=CANSHOW_FIRST " in line for line in log), log)


if __name__ == "__main__":
    unittest.main()
