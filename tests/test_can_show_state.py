# SPDX-License-Identifier: MPL-2.0
"""Offline policy/read-only checks with Lua 5.4 mocks; not UE4SS runtime proof."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
try:
    from lupa.lua54 import LuaRuntime
except ModuleNotFoundError:
    config = ROOT / '.local/environment.json'
    if config.exists():
        library_path = json.loads(config.read_text(encoding='utf-8-sig')).get('testLibraries')
        if library_path:
            sys.path.insert(0, library_path)
    from lupa.lua54 import LuaRuntime

SOURCE = (ROOT / 'research/interaction-prompts-owner/can-show-state/Scripts/main.lua').read_text()
PATH = '/Game/MainContent/Template/UMG/TipHUD.TipHUD_C:CanShow'
FIXTURE = r'''
S = {now=1000, text="Взять", opacity=1.0, visibility=0, enabled=true,
     address=101, block_address=201, loaded=true, block_valid=true, valid=true,
     flags=0x0c420800, reads=0, writes=0, registrations=0, keybinds=0, queued=0,
     game=false, logs={}, timers={}, controls={}}
local classpath = "/Game/MainContent/Template/UMG/TipHUD.TipHUD_C"
local path = classpath .. ":CanShow"
os.time = function() return S.now end
print = function(line) S.logs[#S.logs+1] = line end
local function write_forbidden() S.writes=S.writes+1; error("host write") end
local function readonly(getter) return setmetatable({}, {__index=getter, __newindex=write_forbidden}) end
local function class(name)
    return readonly(function(_, key)
        if key=="IsValid" then return function() return true end end
        if key=="GetFullName" then return function() return "Class " .. name end end
        error("unexpected class access: "..key)
    end)
end
local text = readonly(function(_, key)
    assert(S.game, "text accessed off game thread")
    if key=="ToString" then return function() return S.text end end
    error("unexpected text access: "..key)
end)
local block = readonly(function(_, key)
    assert(S.game, "block accessed off game thread")
    if key=="IsValid" then return function() return S.block_valid end end
    if key=="GetClass" then return function() return class("/Script/UMG.TextBlock") end end
    if key=="GetAddress" then return function() return S.block_address end end
    if key=="Text" then S.reads=S.reads+1; return text end
    error("unexpected block access: "..key)
end)
local widget = readonly(function(_, key)
    assert(S.game, "widget accessed off game thread")
    if key=="IsValid" then return function() return S.valid end end
    if key=="GetClass" then return function() return class(S.class or classpath) end end
    if key=="GetFullName" then return function() return "TipHUD_C /Engine/Transient.Tip" .. S.address end end
    if key=="GetAddress" then return function() return S.address end end
    if key=="Visibility" then S.reads=S.reads+1; return S.visibility end
    if key=="RenderOpacity" then S.reads=S.reads+1; return S.opacity end
    if key=="bIsEnabled" then S.reads=S.reads+1; return S.enabled end
    if key=="TextBlock_89" then S.reads=S.reads+1; return block end
    error("unexpected widget access: "..key)
end)
local fn = readonly(function(_, key)
    assert(S.game, "metadata accessed off game thread")
    if key=="IsValid" then return function() return S.loaded end end
    if key=="type" then return function() return "UFunction" end end
    if key=="GetFullName" then return function() return "Function " .. path end end
    if key=="GetFunctionFlags" then return function() return S.flags end end
    error("unexpected function access: "..key)
end)
StaticFindObject = function(p) assert(S.game and p==path); return fn end
RegisterHook = function(p, callback, ...)
    assert(S.game and p==path and select('#',...)==0)
    S.registrations=S.registrations+1
    if S.register_error then error("registration failed") end
    S.hook=callback; return 12,12
end
Key={F10=121}; ModifierKey={CONTROL=17,ALT=18}
EngineTickAvailable=true; EGameThreadMethod={EngineTick=0}
IsKeyBindRegistered=function(key,modifiers)
    assert(key==121 and modifiers[1]==17 and modifiers[2]==18)
    return S.chord_busy or false
end
RegisterKeyBind=function(key,modifiers,callback)
    assert(key==121 and modifiers[1]==17 and modifiers[2]==18)
    S.keybinds=S.keybinds+1; S.key=callback
end
ExecuteInGameThread=function(callback,method)
    assert(method==0)
    if S.schedule_error then error("dispatch failed") end
    S.queued=S.queued+1; S.controls[#S.controls+1]=callback
end
ExecuteInGameThreadWithDelay=function(ms,callback)
    assert(S.game and ms==600000)
    if S.timer_error then error("timer unavailable") end
    S.timers[#S.timers+1]=callback
end
function press()
    S.key()
    while #S.controls>0 do
        local cb=table.remove(S.controls,1)
        S.game=true; cb(); S.game=false
    end
end
function call(...)
    S.game=true
    local context=readonly(function(_,key)
        if key=="get" then return function() return widget end end
        error("unexpected parameter operation")
    end)
    local result=table.pack(S.hook(context,...))
    S.game=false
    assert(result.n==0, "callback returned an override")
end
function expiry()
    S.game=true; S.timers[1](); S.game=false
end
'''


class ObserverTests(unittest.TestCase):
    def make(self, setup=''):
        lua = LuaRuntime(unpack_returned_tuples=True)
        lua.execute(FIXTURE)
        lua.execute(setup)
        lua.execute(SOURCE)
        return lua, lua.globals().S

    def logs(self, state):
        return list(state.logs.values())

    def test_state_changes_throttle_and_no_return_override(self):
        lua, s = self.make()
        self.assertEqual(s.registrations, 0)
        lua.eval('press')()
        self.assertEqual(s.registrations, 1)
        lua.eval('call')()
        reads = s.reads
        for _ in range(100):
            lua.eval('call')()
        self.assertEqual(s.reads, reads)
        s.now += 1
        lua.eval('call')()
        self.assertEqual(sum('event=SNAPSHOT' in line for line in self.logs(s)), 1)
        s.now += 1; s.text = 'Открыть'; s.opacity = 0.0; s.enabled = False; s.visibility = 2
        lua.eval('call')()
        last = self.logs(s)[-1]
        self.assertIn('Открыть', last)
        self.assertIn('enabled=false', last)
        self.assertIn('visibility_raw=2', last)
        self.assertEqual(s.writes, 0)

    def test_missing_child_is_unavailable_then_recovers(self):
        lua, s = self.make('S.block_valid=false')
        lua.eval('press')(); lua.eval('call')()
        self.assertIn('text_state=unavailable', self.logs(s)[-1])
        s.block_valid = True; s.now += 1
        lua.eval('call')()
        self.assertIn('text_state=available', self.logs(s)[-1])

    def test_expiry_without_calls_and_user_stop_are_inert(self):
        for mode in ('expiry', 'user'):
            with self.subTest(mode=mode):
                lua, s = self.make(); lua.eval('press')()
                if mode=='expiry': lua.eval('expiry')()
                else: lua.eval('press')()
                count, reads, queued = len(self.logs(s)), s.reads, s.queued
                lua.eval('call')(); lua.eval('press')(); lua.eval('expiry')()
                self.assertEqual((len(self.logs(s)),s.reads,s.queued), (count,reads,queued))
                self.assertIn('event=TIMEOUT' if mode=='expiry' else 'event=STOP', self.logs(s)[-1])

    def test_fail_closed_at_start_or_registration(self):
        for setup in ('S.loaded=false', 'S.flags=0x400', 'S.chord_busy=true',
                      'RegisterHook=nil', 'EngineTickAvailable=false',
                      'S.register_error=true', 'S.timer_error=true', 'S.schedule_error=true'):
            with self.subTest(setup=setup):
                lua, s = self.make(setup)
                if s.key: lua.eval('press')()
                self.assertIn('event=FAILED', self.logs(s)[-1])
                reads = s.reads
                if s.hook: lua.eval('call')()
                self.assertEqual(s.reads, reads)
                self.assertEqual(s.writes, 0)

    def test_contract_failures_stop_future_access(self):
        for setup in ('S.valid=false', 'S.class="/Game/Other.Other_C"',
                      'S.enabled=1', 'S.opacity=0/0', 'S.text=string.rep("x",1025)'):
            with self.subTest(setup=setup):
                lua, s = self.make(setup); lua.eval('press')(); lua.eval('call')()
                self.assertIn('event=FAILED', self.logs(s)[-1])
                reads = s.reads; s.now += 1; lua.eval('call')()
                self.assertEqual(s.reads, reads)
        lua, s = self.make(); lua.eval('press')(); lua.eval('call')(True)
        self.assertIn('unexpected CanShow input arguments', self.logs(s)[-1])
        self.assertEqual(s.reads, 0)

    def test_limits_and_control_escaping(self):
        lua, s = self.make(); lua.eval('press')()
        for i in range(9):
            s.now = 1000+i; s.address = 101+i; lua.eval('call')()
        self.assertIn('widget identity limit', self.logs(s)[-1])
        lua, s = self.make(); lua.eval('press')()
        for i in range(599):
            s.now = 1000+i; s.text = str(i); lua.eval('call')()
        self.assertEqual(len(self.logs(s)), 600)
        self.assertIn('line-limit', self.logs(s)[-1])
        lua, s = self.make(); lua.eval('press')()
        s.text = 'Взять\n"\\\t'; lua.eval('call')()
        self.assertTrue(all(line.count('\n')==1 for line in self.logs(s)))
        s.now=1600; reads=s.reads; lua.eval('call')()
        self.assertEqual(s.reads, reads)
        self.assertIn('TIMEOUT', self.logs(s)[-1])

    def test_no_broader_surface_in_source(self):
        for forbidden in ('SetupTipMessage2', 'SetupTipMessage_Proxy', 'TArray', 'ForEach',
                          'SetText', 'SetPropertyValue', 'ProcessEvent', 'FindAllOf',
                          'RetainerBox', 'LoopAsync', 'ExecuteWithDelay', ':set('):
            self.assertNotIn(forbidden, SOURCE)


if __name__ == '__main__':
    unittest.main()
