# SPDX-License-Identifier: MPL-2.0
"""Actual four-child/World/panel/input code against host mocks. No engine render claim."""
import hashlib
import json
import unittest
from test_ui_child import LuaRuntime, ROOT
from test_beginplay_join import FIXTURE
from test_world_child import EXTRA
from test_world_deferred import CONTEXT
from test_world_orientation import ORIENTATION
from test_vertical_yaw import FRAMES
from test_hint_mirror import HINT_FIXTURE

DIR=ROOT/'research/interaction-prompts-owner/world-space/live-editor/Scripts'
SOURCES={p.stem:p.read_text(encoding='utf8') for p in DIR.glob('*.lua')}
# Isolate already-proven local resource loading from this assembly test. The real
# extracted resource module is exercised separately in test_live_resources.py.
RESOURCES=r'''
return {prepare=function()end,font=function(o)
 if S.font_failure then error('font bind failure')end
 o.Font.FontObject=S.private_font
end,ornament=function(o)
 if S.ornament_failure then error('ornament import failure')end
 o.Brush.ResourceObject=S.raw;S.imports=(S.imports or 0)+1
end}
'''
LIVE=r'''
Key.F11=11
for i,k in ipairs({'MULTIPLY','NUM_ZERO','NUM_ONE','NUM_TWO','NUM_THREE','NUM_FOUR','NUM_FIVE',
 'NUM_SIX','NUM_SEVEN','NUM_EIGHT','NUM_NINE'})do Key[k]=100+i end
S.down={};S.actions={};S.original_font={Size=22,FontObject=S.raw,OutlineSettings={OutlineSize=0},GetStructAddress=function()return 800 end}
S.private_font=owned('/Private.Font','/Script/Engine.Font')
set(P.text,'Font',S.original_font);set(P.text,'GetText',function()return P.text.Text end)
set(S.pc,'IsInputKeyDown',function(_,k)
 if S.poll_failure then error('input lost')end
 return S.down[k.KeyName] or false
end)
local resolver=make('/Script/Genesis.GameGlobal:GetKeyByVirtualKey','Function')
set(resolver,'type',function()return 'UFunction'end)
setmetatable(resolver,{__index=S.fields[resolver],__call=function(_,_,name)
 return {KeyName={ToString=function()return S.actions[name] or 'F'end}}
end})
make('/Script/Genesis.Default__GameGlobal','GameGlobal')
local polling=make('/Script/Engine.PlayerController:IsInputKeyDown','Function')
set(polling,'type',function()return 'UFunction'end)
local fn=S.objects['/Script/UMG.WidgetBlueprintLibrary:Create'];local oldcreate=getmetatable(fn).__call
getmetatable(fn).__call=function(...)
 local world=S.host
 -- The factory returns distinct engine instances, even for the same WidgetClass.
 local w=oldcreate(...);local root=w.WidgetTree.RootWidget
 if S.created>=2 then
  local objects={w,w.WidgetTree,root,root.children[1],w.Value_Text,w.Bg_Image}
  for _,o in ipairs(objects)do
   local old=o.p;S.objects[old]=nil;o.p=old:gsub('OwnHost','EditorHost'..S.created);S.objects[o.p]=o
  end
  -- Reinstall the untouched World identities shadowed by the simplistic base factory.
  local t=world.WidgetTree;local r=t.RootWidget;local m=r.children[1]
  for _,o in ipairs({world,t,r,m,world.Value_Text,world.Bg_Image})do S.objects[o.p]=o end
  S.panel=w;S.host=world
 end
 local add=root.AddChildToCanvas
 root.AddChildToCanvas=function(_,o)
  local slot=add(root,o)
  slot.SetPosition=function(_,v)slot.position=v end;slot.GetPosition=function()return slot.position end
  slot.SetSize=function(_,v)
   if S.slot_failure then error('slot setter failure')end
   slot.size={X=v.X,Y=v.Y}
  end
  slot.GetSize=function()return slot.size end
  return slot
 end
 w.ForceLayoutPrepass=function()S.prepasses=(S.prepasses or 0)+1 end
 w.SetDesiredSizeInViewport=function()end;w.SetAnchorsInViewport=function()end
 w.SetAlignmentInViewport=function()end;w.SetPositionInViewport=function()end
 w.AddToViewport=function()w.viewport=true;w.Visibility=2 end
 w.IsInViewport=function()return w.viewport or false end
 w.RemoveFromParent=function()w.viewport=false;S.host_removed=true end
 return w
end
local construct=StaticConstructObject
function StaticConstructObject(c,outer,name,...)
 local o=construct(c,outer,name,...)
 if c.p=='/Script/UMG.TextBlock' then
  o.SetFont=function(_,f)
   if S.release_font_failure and f==S.lower.Font then error('font release failed')end
   local v={};for k,x in pairs(f)do v[k]=x end
   local outline={};for k,x in pairs(f.OutlineSettings or {})do outline[k]=x end
   v.OutlineSettings=outline;v.GetStructAddress=function()return o.id+900 end;o.Font=v
  end
  o.SetText=function(_,t)o.Text={ToString=function()return t end}end
  o.GetText=function()return o.Text end
  o.SetShadowOffset=function()end;o.SetShadowColorAndOpacity=function()end
  o.GetDesiredSize=function()
   if S.wide_text then return {X=500,Y=30}end
   return {X=name:find('_Aphes')and 140 or 120,Y=o.Font.Size+4}
  end
  if name:find('_Aphes')then S.upper=o elseif name:find('_Action')then S.lower=o end
 elseif c.p=='/Script/UMG.Image'then
  o.SetColorAndOpacity=function(_,v)o.ColorAndOpacity=v end
  if name:find('_Ornament')then S.divider=o else S.hint=o end
 end
 return o
end
set(P.actor,'FinishAddComponent',function(_,c,manual,t)
 assert(manual and c==S.comp and c.widget==S.host and c.draw.X==512 and c.draw.Y==128)
 c.transform=t;c.registered=true
end)
function key(k)S.keys[k or 11]();flush()end
function tap(k)S.down[k]=true;yawframe();S.down[k]=false;yawframe()end
function ready()start();settle();assert(has('event=LAYOUT') and has('AUDIT_PASS') and S.panel.viewport)end
'''

class WorldLiveEditor(unittest.TestCase):
    def case(self,code,setup=''):
        lua=LuaRuntime(unpack_returned_tuples=True)
        lua.execute(FIXTURE+EXTRA+CONTEXT+ORIENTATION+FRAMES+HINT_FIXTURE+LIVE)
        for name,source in SOURCES.items():
            if name!='main':
                lua.execute('package.preload["'+name+'"]=function()\n'+(RESOURCES if name=='IIPResources' else source)+'\nend')
        lua.execute(setup);lua.execute(SOURCES['main'])
        try:lua.execute(code)
        except Exception:
            print(list(lua.globals().S.logs.values())[-15:]);raise
        return lua

    def test_complete_creation_edit_and_stop(self):
        self.case('ready();assert(S.upper.Text:ToString()=="OPEN" and S.lower.Text:ToString()=="Открыть");'
                  'assert(S.upper.Font.OutlineSettings.OutlineSize==0 and S.imports==1);'
                  'tap("NumPadSix");assert(S.upper.Font.Size==33);tap("NumPadSeven");assert(S.upper.Font.Size==32);'
                  'tap("NumPadNine");assert(has("event=VALUES"));tap("Multiply");'
                  'assert(has("LOOP_CANCELLED") and has("CLEANED") and S.comp.pending and not S.panel.viewport);'
                  'assert(S.hint.Brush.ResourceObject==nil and S.divider.Brush.ResourceObject==nil and S.upper.Font.FontObject==S.raw)')

    def test_panel_close_reopen_seed_and_no_closed_input(self):
        self.case('ready();tap("NumPadZero");assert(not S.panel.viewport and not S.comp.pending);'
                  'tap("NumPadSix");assert(S.upper.Font.Size==32);S.down.NumPadSix=true;key();'
                  'yawframe();assert(S.upper.Font.Size==32);S.down.NumPadSix=false;yawframe();'
                  'tap("NumPadSix");assert(S.upper.Font.Size==33);key();assert(not S.panel.viewport);'
                  'tap("Multiply");assert(not S.comp.pending);key();yawframe();tap("Multiply");assert(has("CLEANED"))')

    def test_localized_value_and_native_hint_resource_refresh(self):
        self.case('ready();set(P.text,"value","Open chest");yawframe();assert(S.lower:GetText():ToString()=="Open chest");'
                  'for i=1,8 do tap("NumPadTwo")end;tap("NumPadSix");assert(S.hint.Slot.size.Y==39);'
                  'S.device=4;settle();assert(has("device=4") and S.hint.Brush.ResourceObject==S.hint_mid);'
                  'S.hint_mid=new_mid("/Hint.NewMID");settle();assert(S.hint.Brush.ResourceObject==S.hint_mid);'
                  'assert(S.hint.Slot.size.Y==39);tap("Multiply");assert(has("CLEANED"))')

    def test_all_parameters_steps_reset_and_bounds(self):
        self.case('ready();for i=1,10 do tap("NumPadFive");tap("NumPadSix");tap("NumPadSeven");'
                  'tap("NumPadTwo")end;assert(S.upper.Font.Size==32 and S.lower.Font.Size==22);'
                  'tap("NumPadEight");tap("NumPadFour");assert(S.hint.Slot.position.X>0);tap("Multiply")')

    def test_modifier_and_held_keys_do_not_repeat(self):
        self.case('ready();S.down.LeftControl=true;tap("NumPadSix");assert(S.upper.Font.Size==32);'
                  'S.down.LeftControl=false;S.down.NumPadSix=true;for i=1,8 do yawframe()end;'
                  'assert(S.upper.Font.Size==33);S.down.NumPadSix=false;yawframe();tap("Multiply")')

    def test_budgets_context_loss_and_text_overflow_clean(self):
        for setup in ['set(P.widget,"Visibility",2)', 'S.now=S.now+46',
                      'S.wide_text=true;set(P.text,"value","changed")',
                      'S.icon=nil', 'S.poll_failure=true']:
            self.case('ready();'+setup+';yawframe();assert(has("CLEANED") and S.comp.pending and not S.panel.viewport)')

    def test_partial_creation_failures_release_independent_parts(self):
        for setup in ['S.font_failure=true','S.ornament_failure=true','S.slot_failure=true']:
            self.case('start();assert(has("FAILED") and has("CLEANED") and S.comp.pending)',setup)

    def test_release_failure_retains_retryable_own_resources(self):
        self.case('ready();S.release_fail=true;tap("Multiply");assert(has("CLEANUP_PENDING") and not S.comp.pending);'
                  'S.release_fail=false;key();assert(has("CLEANED") and S.comp.pending)')

    def test_mapping_conflict_and_registry_error_fail_closed(self):
        self.case('start();assert(has("current game-key conflict") and has("CLEANED"))','S.actions["K-Interact"]="NumPadEight"')
        self.case('start();assert(has("CLEANED"))','IsKeyBindRegistered=function(k)return k==Key.NUM_EIGHT end')
        self.case('assert(has("UNAVAILABLE") and not S.comp)',
                  'IsKeyBindRegistered=function()error("registry failed")end')

    def test_invalid_action_and_cancelled_callbacks_cannot_leave_stale_ui(self):
        for value in ['', 'line1\nline2']:
            self.case('ready();set(P.text,"value",'+json.dumps(value)+');yawframe();assert(has("CLEANED"))')
        self.case('ready();local cb=S.loop.fn;tap("Multiply");local writes=S.sets;'
                  'S.game=true;cb();S.game=false;assert(S.sets==writes and S.destroys==1)')

    def test_source_manifest_matches_exact_files(self):
        manifest=json.loads((DIR.parent/'SOURCE_MANIFEST.json').read_text(encoding='utf8'))
        self.assertEqual(set(manifest['files']),{str(p.relative_to(DIR.parent)).replace('\\','/')
                         for p in DIR.glob('*.lua')} | {'IIPLiveConfig.example.lua'})
        for path,digest in manifest['files'].items():
            self.assertEqual(hashlib.sha256((DIR.parent/path).read_bytes()).hexdigest(),digest,path)

    def test_no_new_forbidden_keys_and_no_original_setters(self):
        self.assertNotIn('Key.F6',SOURCES['main'])
        self.assertNotIn('Key.F12',SOURCES['main'])
        self.assertNotIn('Key.F10',SOURCES['main'])
        self.assertNotIn('SetRenderTranslation',SOURCES['IIPComposition'])
        self.case('ready();tap("Multiply");assert(P.text.Font==S.original_font and S.hint_size.X==38)')

if __name__=='__main__':unittest.main()
