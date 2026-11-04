-- SPDX-License-Identifier: MPL-2.0
-- Nonpersistent research controls. Units are UMG layout units, never screen pixels.
local M={}
M.fields={
 {"upper_size","Aphes font",32,20,44,1,2},
 {"lower_size","Action font",22,16,30,1,2},
 {"tracking","Aphes tracking (1/1000 em)",150,0,400,10,50},
 {"outline","Aphes outline",0,0,3,1,1},
 {"gap","Vertical gaps",8,2,16,1,4},
 {"divider_y","Divider offset (+down)",0,-6,6,1,2},
 {"divider_width","Divider width",200,100,280,2,10},
 {"divider_alpha","Divider opacity",1,0,1,0.05,0.2},
 {"hint_size","Button height",38,24,64,1,4},
 {"hint_gap","Button-to-action gap",8,2,24,1,4},
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
 local lines={"IIP / WORLD PROMPT - research", "Session only / no automatic save", "Close HildaSoftLight editor first", ""}
 for i,f in ipairs(M.fields)do
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
  s[f[1]]=math.max(f[4],math.min(f[5],math.floor(v*1000+0.5)/1000));s.dirty=true
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
function M.plan(s,upper,lower,hint)
 for _,v in ipairs({upper.X,upper.Y,lower.X,lower.Y,hint.X,hint.Y})do
  assert(type(v)=="number" and v==v and v>0 and v<1000,"unmeasured/unsupported own extent")
 end
 assert(upper.X+2*s.outline<=440 and lower.X<=340,"text too wide; preserve original fallback")
 local hh=s.hint_size;local hw=hh*hint.X/hint.Y
 assert(hw<=96,"unsupported hint aspect")
 local lineh=s.divider_width*16/570
 local upperh=upper.Y+2*s.outline
 local liney=4+upperh+s.gap+s.divider_y
 local rowy=liney+lineh/2+s.gap+math.max(lower.Y,hh)/2
 assert(liney-lineh/2>=4+upperh and rowy+math.max(lower.Y,hh)/2<=124,"composition exceeds 512x128")
 local x=256-lower.X/2-s.hint_gap-hw/2
 assert(x-hw/2>=4,"button/action row exceeds canvas")
 return {upper={256,4+upperh/2,440,upperh},divider={256,liney,s.divider_width,lineh},
  lower={256,rowy,lower.X,lower.Y},hint={x,rowy,hw,hh}}
end
return M
