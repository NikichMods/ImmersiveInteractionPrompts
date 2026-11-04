-- SPDX-License-Identifier: MPL-2.0
-- Nonpersistent research controls. Units are UMG layout units, never screen pixels.
local M={width=1024,height=512,reference_height=128}
M.fields={
 {"upper_size","Aphes font",52,20,96,1,4},
 {"lower_size","Action font",30,16,64,1,4},
 {"tracking","Aphes tracking (1/1000 em)",400,0,400,10,50},
 {"outline","Aphes outline",0,0,3,1,1},
 {"gap","Vertical gaps",7,2,48,1,4},
 {"divider_y","Divider offset (+down)",0,-32,32,1,4},
 {"divider_width","Divider length",300,100,640,2,20},
 {"divider_thickness","Divider thickness x",1,0.5,6,0.25,0.5},
 {"divider_alpha","Divider opacity",1,0,1,0.05,0.2},
 {"hint_size","Button height",54,24,128,1,8},
 {"hint_gap","Button gap from text / line",64,2,128,1,4},
 {"hint_y","Button Y from divider (+down)",0,-100,180,1,4},
 {"upper_brightness","Aphes brightness",1,0.2,1,0.05,0.1},
 {"lower_brightness","Action brightness",1,0.2,1,0.05,0.1},
 {"divider_brightness","Divider brightness",1,0.2,1,0.05,0.1},
 {"hint_brightness","Button brightness",1,0.2,1,0.05,0.1},
 {"lower_outline","Action outline (readability)",0,0,3,1,1},
}
function M.new()
 local s={selected=1,coarse=false,open=false,seed=true,held={},dirty=true}
 for _,f in ipairs(M.fields)do s[f[1]]=f[3]end
 return s
end
function M.snapshot(s)
 local t={}
 for _,f in ipairs(M.fields)do t[#t+1]=f[1].."="..string.format("%.6g",s[f[1]])end
 return table.concat(t," ")
end
function M.text(s)
 local lines={"IIP / WORLD PROMPT - research", "Session only / no automatic save", "Close HildaSoftLight editor first", s.note or ""}
 local first=math.max(1,math.min(s.selected-4,#M.fields-8))
 local last=math.min(#M.fields,first+8)
 lines[#lines+1]="Parameters "..first.."-"..last.." / "..#M.fields
 for i=first,last do
  local f=M.fields[i]
  lines[#lines+1]=(i==s.selected and "> " or "  ")..f[2]..": "..string.format("%.6g",s[f[1]])
 end
 lines[#lines+1]=""
 lines[#lines+1]="Step: "..(s.coarse and "coarse" or "fine")
 lines[#lines+1]="Num8/2 select | Num4/6 adjust | Num5 step"
 lines[#lines+1]="Num7 reset selected | Num9 log values"
 lines[#lines+1]="Num0 / Ctrl+Alt+F11 close | Num* STOP"
 lines[#lines+1]="Num1/3 reserved | NumLock ON"
 return table.concat(lines,"\n")
end
function M.action(s,key)
 if not s.open then return nil end
 if key=="Multiply"then return "stop"end
 if key=="NumPadZero"then return "close"end
 if key=="NumPadNine"then return "log"end
 if key=="NumPadEight"then s.selected=(s.selected-2)%#M.fields+1
 elseif key=="NumPadTwo"then s.selected=s.selected%#M.fields+1
 elseif key=="NumPadFive"then s.coarse=not s.coarse
 elseif key=="NumPadFour" or key=="NumPadSix" or key=="NumPadSeven"then
  local f=M.fields[s.selected];local v=f[3]
  if key~="NumPadSeven"then v=s[f[1]]+(key=="NumPadSix"and 1 or -1)*f[s.coarse and 7 or 6]end
  s[f[1]]=math.max(f[4],math.min(f[5],math.floor(v*1000+0.5)/1000));s.dirty=true;s.edit_pending=true;s.note=nil
 else return nil end
 return "refresh"
end
M.keys={"Multiply","NumPadZero","NumPadOne","NumPadTwo","NumPadThree","NumPadFour",
 "NumPadFive","NumPadSix","NumPadSeven","NumPadEight","NumPadNine"}
function M.poll(s,pc)
 if not s.open then return nil end
 local function down(k)
  local b=pc:IsInputKeyDown({KeyName=FName(k)})
  assert(type(b)=="boolean","native key result is not bool");return b
 end
 local modified=down("LeftControl") or down("RightControl")
 modified=down("LeftAlt") or down("RightAlt") or down("LeftShift") or down("RightShift") or modified
 local command
 for _,k in ipairs(M.keys)do
  local d=down(k)
  if d and not s.seed and not s.held[k] and not modified then
   -- STOP has priority; otherwise one deterministic command per frame, no repeat.
   if not command or k=="Multiply"then command=k end
  end
  s.held[k]=d
 end
 s.seed=false
 return command
end
function M.values(s)
 local v={};for _,f in ipairs(M.fields)do v[f[1]]=s[f[1]]end;return v
end
function M.restore(s,v)
 for _,f in ipairs(M.fields)do s[f[1]]=assert(v[f[1]],"missing prior setting")end
end
function M.plan(s,upper,lower,hint)
 for _,v in ipairs({upper.X,upper.Y,lower.X,lower.Y,hint.X,hint.Y})do
  assert(type(v)=="number" and v==v and v>0 and v<10000,"unmeasured/unsupported own extent")
 end
 local margin=4;local center=M.width/2
 -- Preserve original world-space baseline at identical settings despite a larger RT.
 local origin=(M.height-M.reference_height)/2
 local upper_width=M.width-2*margin
 if upper.X+2*s.outline>upper_width then return nil,"Upper text is too wide"end
 local hh=s.hint_size;local hw=hh*hint.X/hint.Y
 if hw>M.width-2*margin then return nil,"Button is too wide"end
 -- Full PNG envelope reserves safe gaps; alpha occupies only rows8..23.
 -- 1x preserves the authored aspect; live thickness intentionally scales Y only.
 local lineh=s.divider_width*32/256*s.divider_thickness
 local upperh=upper.Y+2*s.outline
 local liney=origin+margin+upperh+s.gap+lineh/2+s.divider_y
 local rowy=liney+lineh/2+s.gap+lower.Y/2
 if liney-lineh/2<origin+margin+upperh then return nil,"Divider overlaps upper text"end
 if rowy+lower.Y/2>M.height-margin then return nil,"Text and spacing are too tall"end
 local x=center-math.max(lower.X,s.divider_width)/2-s.hint_gap-hw/2
 local hy=liney+s.hint_y
 if hy-hh/2<margin or hy+hh/2>M.height-margin then return nil,"Button is outside the vertical work area"end
 if x-hw/2<margin or center+lower.X/2>M.width-margin then return nil,"Action and button are too wide"end
 return {upper={center,origin+margin+upperh/2,upper_width,upperh},divider={center,liney,s.divider_width,lineh},
  lower={center,rowy,lower.X,lower.Y},hint={x,hy,hw,hh}}
end
return M
