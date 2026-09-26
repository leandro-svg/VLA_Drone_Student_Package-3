from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, math, html, os

ROOT=Path(__file__).resolve().parent.parent
OUT=Path(__file__).resolve().parent
BLUE='#003399'; ORANGE='#D85A00'; LIGHT='#EEF3FB'; GREY='#626B76'; GREEN='#27735B'; INK='#111820'; GRID='#D4DAE2'
def font_path(variable, candidates):
 value=os.environ.get(variable)
 if value and Path(value).is_file():return value
 for candidate in candidates:
  if Path(candidate).is_file():return candidate
 raise RuntimeError(f'Set {variable} to a TrueType font file path.')
REG=font_path('LITTER_FIGURE_FONT', ['/System/Library/Fonts/Supplemental/Arial.ttf', 'C:/Windows/Fonts/arial.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'])
BOLD=font_path('LITTER_FIGURE_BOLD', ['/System/Library/Fonts/Supplemental/Arial Bold.ttf', 'C:/Windows/Fonts/arialbd.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'])
class Figure:
 def __init__(self,name,height=1000):
  self.name=name;self.w=1600;self.h=height;self.im=Image.new('RGB',(self.w,self.h),'white');self.d=ImageDraw.Draw(self.im);self.svg=[]
 def line(self,pts,color=BLUE,width=4,dash=False):
  self.d.line(pts,fill=color,width=width)
  self.svg.append(f'<polyline points="'+ ' '.join(f'{x},{y}' for x,y in pts)+f'" fill="none" stroke="{color}" stroke-width="{width}"'+(' stroke-dasharray="10 8"' if dash else '')+'/>')
 def rect(self,x,y,w,h,fill='white',stroke=GRID,width=3):
  self.d.rectangle((x,y,x+w,y+h),fill=fill,outline=stroke,width=width)
  self.svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')
 def circle(self,x,y,r,fill=BLUE,stroke=None,width=3):
  self.d.ellipse((x-r,y-r,x+r,y+r),fill=fill,outline=stroke,width=width)
  self.svg.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill or "none"}" stroke="{stroke or fill}" stroke-width="{width}"/>')
 def arrow(self,pts,color=ORANGE,width=5):
  self.line(pts,color,width);x,y=pts[-1];a,b=pts[-2];ang=math.atan2(y-b,x-a);p=[(x,y),(x-18*math.cos(ang-.45),y-18*math.sin(ang-.45)),(x-18*math.cos(ang+.45),y-18*math.sin(ang+.45))];self.d.polygon(p,fill=color)
  self.svg.append('<polygon points="'+' '.join(f'{x},{y}' for x,y in p)+f'" fill="{color}"/>')
 def text(self,x,y,s,size=32,color=INK,bold=False,align='left',maxwidth=None):
  font=ImageFont.truetype(BOLD if bold else REG,size)
  lines=[]
  for part in str(s).split('\n'):
   if maxwidth:
    line=''
    for word in part.split():
     trial=(line+' '+word).strip()
     if line and self.d.textlength(trial,font=font)>maxwidth:lines.append(line);line=word
     else:line=trial
    lines.append(line)
   else:lines.append(part)
  for i,line in enumerate(lines):
   yy=y+i*size*1.22;ww=self.d.textlength(line,font=font);xx=x-ww/2 if align=='center' else x-ww if align=='right' else x
   self.d.text((xx,yy),line,fill=color,font=font)
   self.svg.append(f'<text x="{xx}" y="{yy+size*.92}" font-family="Arial, sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="{color}">{html.escape(line)}</text>')
  return len(lines)*size*1.22
 def box(self,x,y,w,h,title,body='',fill=LIGHT,size=31):
  self.rect(x,y,w,h,fill,BLUE)
  z=self.text(x+22,y+18,title,size+2,bold=True,maxwidth=w-44)
  if body:self.text(x+22,y+28+z,body,size,color=BLUE,maxwidth=w-44)
 def save(self):
  self.im.save(OUT/(self.name+'.png'))
  (OUT/(self.name+'.svg')).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="{self.h}" viewBox="0 0 1600 {self.h}"><rect width="1600" height="{self.h}" fill="white"/>'+''.join(self.svg)+'</svg>')

# 1 Mission overview, an illustrative plan rather than a claimed flight.
f=Figure('01_mission',1030)
f.text(55,15,'FIELD AND FLIGHT PATH',34,bold=True);f.text(900,15,'FROM OBSERVATION TO MAP',34,bold=True)
f.rect(80,120,650,650,'#F0F5EF','#9AAEA0')
for x in [80,242,405,567,730]:f.line([(x,120),(x,770)],'#D8E3D6',2)
for y in [120,282,445,607,770]:f.line([(80,y),(730,y)],'#D8E3D6',2)
pts=[(130,720),(130,175),(270,175),(270,700),(410,700),(410,175),(550,175),(550,700),(680,700),(680,175)]
f.arrow(pts,BLUE,6)
for x,y,label in [(320,330,'can'),(570,520,'bottle'),(190,575,'paper')]:
 f.circle(x,y,13,ORANGE);f.text(155 if label=='paper' else x+20,620 if label=='paper' else y-20,label,29,bold=True)
f.circle(320,330,58,fill=None,stroke=ORANGE,width=4)
f.arrow([(270,340),(309,332)],ORANGE)
f.text(80,905,'Orange: local inspection',28,color=ORANGE)
f.arrow([(80,860),(80,810)],INK,4);f.text(100,810,'North',29);f.arrow([(500,860),(660,860)],INK,4);f.text(500,888,'East',29)
f.text(80,940,'Illustrative 20 m × 20 m field; path not to scale.',28,color=GREY)
for y,title,body in [(105,'1  Search','Survey the field and retain candidate sightings.'),(300,'2  Inspect','Approach a candidate and centre it in view.'),(495,'3  Analyse','Save visible category, attributes and uncertainty.'),(690,'4  Map','Associate sightings with one object record.')]:
 f.box(880,y,660,145,title,body)
 if y<690:f.arrow([(1210,y+145),(1210,y+195)])
f.text(880,885,'Output example',32,bold=True);f.text(880,935,'track_17  |  can  |  position + evidence',30,color=BLUE)
f.save()

# 2 Pixel geometry.
f=Figure('02_coordinates',1010)
f.text(65,20,'IMAGE COORDINATES',34,bold=True);f.text(880,20,'GROUND OFFSETS',34,bold=True)
x0,y0,w=80,140,580
f.rect(x0,y0,w,w,LIGHT,GRID)
for v in [24,48,72]:
 f.line([(x0+w*v/96,y0),(x0+w*v/96,y0+w)],GRID,2);f.line([(x0,y0+w*v/96),(x0+w,y0+w*v/96)],GRID,2)
cx,cy=x0+w/2,y0+w/2;tx,ty=x0+w*60/96,y0+w*36/96
f.line([(cx-25,cy),(cx+25,cy)],BLUE,4);f.line([(cx,cy-25),(cx,cy+25)],BLUE,4)
f.circle(tx,ty,12,ORANGE);f.arrow([(cx,cy),(tx,ty)],ORANGE)
f.text(100,745,'Centre (48, 48)',31);f.text(100,790,'Target (60, 36)',31,color=ORANGE)
f.arrow([(80,95),(370,95)],INK,4);f.text(390,73,'u increases',29)
f.arrow([(30,145),(30,450)],INK,4);f.text(65,80,'0',27);f.text(70,865,'v increases down the image',29,color=GREY)
f.rect(860,140,640,580,'white',GRID)
ox,oy=925,640;scale=280
f.arrow([(ox,oy),(1460,oy)],INK,4);f.text(1410,670,'East',30)
f.arrow([(ox,oy),(ox,185)],INK,4);f.text(965,165,'North',30)
f.arrow([(ox,oy),(ox+1.25*scale,oy-1.25*scale)],GREY,4)
f.circle(ox+350,oy-350,12,ORANGE);f.text(1290,245,'Target',30,color=ORANGE)
f.arrow([(ox,oy),(ox+.354*scale,oy-.354*scale)],BLUE,9)
f.text(1050,550,'Bounded command',29,color=BLUE)
f.text(900,750,'Target offset  [1.25, 1.25] m',31)
f.text(900,800,'Command      [0.354, 0.354] m',31,color=BLUE)
f.text(900,845,'Vector length limited to 0.5 m',29,color=GREY)
f.text(65,945,'Ideal level camera only: 96 × 96 pixels, f = 48 pixels, height = 5 m, north at image top.',29)
f.save()

# 3 Complete architecture including direct image/state input to local policy.
f=Figure('03_architecture',980)
f.box(45,295,350,165,'Observe','RGB + state\nCapture time')
f.box(475,50,445,155,'Detect and remember','Candidate instances\nCoverage + evidence')
f.box(1040,50,510,155,'Slow VLM planner','Choose an allowed task\nAnalyse selected views')
f.box(620,335,410,175,'Local inspection','Image + task + state\nClassical policy OR VLA')
f.box(620,650,410,145,'Command supervisor','Validate age and bounds\nHold on expiry')
f.box(1130,650,420,145,'Flight controller','Existing autopilot\nPosition tracking')
f.box(45,650,400,145,'Map and evidence','One track per object\nExport positions + labels')
f.arrow([(395,360),(435,360),(435,125),(475,125)],BLUE)
f.arrow([(395,425),(620,425)],BLUE)
f.arrow([(920,125),(1040,125)],BLUE)
f.arrow([(1295,205),(1295,270),(825,270),(825,335)]);f.text(850,232,'task + expiry',29,color=ORANGE)
f.arrow([(825,510),(825,650)]);f.text(850,555,'bounded action',29,color=ORANGE)
f.arrow([(1030,722),(1130,722)]);f.text(1085,590,'position /\nvelocity',28,align='center')
f.arrow([(495,205),(495,570),(245,570),(245,650)],BLUE)
f.text(60,550,'tracks',27,color=BLUE)
f.arrow([(1340,795),(1340,900),(20,900),(20,375),(45,375)],BLUE)
f.text(580,918,'New measurements after motion',29,color=BLUE)
f.arrow([(1550,145),(1580,145),(1580,850),(470,850),(470,740),(445,740)],BLUE)
f.text(710,808,'analysis labels',28,color=BLUE)
f.save()

# 4 Action anchoring and timing.
f=Figure('04_command_timeline',970)
f.text(60,20,'ONE PREDICTION CREATES ONE ABSOLUTE TARGET',34,bold=True)
f.box(50,110,460,180,'Observation at capture','Anchor N,E\n[-0.4947, 0.3212] m')
f.box(580,110,410,180,'Policy prediction','Increment N,E\n[0.3743, -0.3315] m')
f.box(1060,110,490,180,'Accepted target','Anchor + increment\n[-0.1204, -0.0103] m')
f.arrow([(510,200),(580,200)]);f.arrow([(990,200),(1060,200)])
f.text(60,365,'WALL CLOCK EXAMPLE',33,bold=True);f.text(60,412,'Illustrative times; measure your own latency.',30,color=GREY)
f.arrow([(100,545),(1515,545)],INK,4)
for x,t,label in [(130,'0 ms','Capture'),(520,'120 ms','Inference ready'),(950,'180 ms','Send target'),(1370,'230 ms','Resend target')]:
 f.line([(x,525),(x,565)],BLUE,4);f.text(x,478,t,30,bold=True,align='center');f.text(x,590,label,28,align='center')
f.text(770,705,'Send the SAME absolute target while it remains valid.',34,bold=True,align='center')
f.text(80,810,'Do not add the increment again on every resend.',32,color=ORANGE)
f.text(80,866,'Reject stale observations or expired commands; use the tested hold response.',31,maxwidth=1440)
f.save()

# 6 Actual saved teaching results, not a synthetic improvement curve.
f=Figure('06_measured_results',1030)
history=json.loads((ROOT/'VLA_Drone_Starter_Kit/examples/tiny_model/history.json').read_text())
f.text(65,20,'RECORDED TRAINING HISTORY',33,bold=True);f.text(910,20,'HELD OUT TEACHING TRIALS',33,bold=True)
l,t,r,b=100,130,720,700
f.line([(l,t),(l,b),(r,b)],INK,3)
for v in [0,.05,.10,.15,.20]:
 y=b-v/.20*(b-t);f.line([(l,y),(r,y)],GRID,2);f.text(l-14,y-15,f'{v:.2f}',27,align='right')
for epoch in [1,50,100,150,200]:
 x=l+(epoch-1)/199*(r-l);f.text(x,b+20,str(epoch),27,align='center')
for key,col in [('train_mse_normalised',BLUE),('val_mse_normalised',ORANGE)]:
 pts=[(l+(row['epoch']-1)/199*(r-l),b-row[key]/.20*(b-t)) for row in history];f.line(pts,col,4)
f.text(100,82,'Normalised action MSE',29);f.text(400,768,'Epoch',30,align='center')
f.line([(115,855),(175,855)],BLUE,5);f.text(190,835,'Training',30);f.line([(410,855),(470,855)],ORANGE,5);f.text(485,835,'Validation',30)
labels=[('eval_baseline','Classical'),('eval_normal','Learned'),('eval_swapped','Changed task'),('eval_empty','No task')]
xl,xr=970,1450
for i,(path,label) in enumerate(labels):
 d=json.loads((ROOT/f'VLA_Drone_Starter_Kit/examples/{path}/summary.json').read_text());y=170+i*180
 f.text(920,y-52,label,30,bold=True)
 f.rect(xl,y,xr-xl,54,'#F4F5F7',GRID,1)
 if d['success_count']:f.rect(xl,y,(xr-xl)*d['success_rate'],54,BLUE,BLUE,1)
 else:f.line([(xl,y),(xl,y+54)],ORANGE,6)
 f.text(xr+15,y+4,f"{d['success_count']}/30",29)
f.text(920,887,'Each condition uses the same 30 starts.',28,color=GREY,maxwidth=640)
f.text(65,970,'Source: bundled examples/tiny_model/history.json and examples/eval_*/summary.json.',27,color=GREY)
f.save()

# 7 Simulator loop with explicit estimated-state and camera paths.
f=Figure('07_simulator',1070)
f.text(55,20,'THE FLIGHT SIMULATION LOOP',34,bold=True)
f.box(50,110,430,180,'Experiment runner','Layout + task\nReset, start, stop, score')
f.box(575,110,430,180,'Policy process','Image + task + state\nBounded action output')
f.box(1090,110,460,180,'Flight bridge','Time alignment\nValidate + send setpoint')
f.box(1090,610,460,180,'PX4 SITL','Estimated vehicle state\nExisting flight controller')
f.box(575,610,430,180,'Gazebo','Vehicle physics\nCamera + other sensors')
f.box(50,610,430,180,'Saved evidence','All processes log here\nImages, actions and poses')
f.arrow([(480,155),(575,155)])
f.arrow([(1005,160),(1090,160)]);f.text(860,65,'command',28,color=ORANGE)
f.arrow([(1090,255),(1005,255)],BLUE);f.text(585,315,'aligned image + state',28,color=BLUE)
f.arrow([(1460,290),(1460,610)]);f.text(1435,390,'setpoint',26,color=ORANGE,align='right')
f.arrow([(1300,610),(1300,290)],BLUE);f.text(1315,495,'estimated\nstate',27,color=BLUE)
f.arrow([(800,610),(800,440),(1150,440),(1150,290)],BLUE);f.text(880,385,'camera',28,color=BLUE)
f.arrow([(1005,735),(1090,735)],BLUE);f.text(940,826,'sensor readings',26,color=BLUE,align='center')
f.arrow([(1090,665),(1005,665)],ORANGE);f.text(1105,565,'actuation',26,color=ORANGE)
f.arrow([(480,230),(520,230),(520,515),(650,515),(650,610)],GREY,3);f.text(70,460,'reset / layout',28,color=GREY)
f.text(60,920,'The bridge pairs the camera with PX4 estimated state before delivering an observation.',30,maxwidth=1460)
f.text(60,980,'Privileged ground truth goes only to the evaluator or expert, never to the deployed policy.',29,maxwidth=1460)
f.save()

# 8 Mapping and instance association.
f=Figure('08_mapping',990)
f.text(60,20,'MULTIPLE VIEWS',34,bold=True);f.text(890,20,'ONE TRACK PER PHYSICAL ITEM',34,bold=True)
for y,label,p in [(115,'Frame 001','Can near image centre'),(335,'Frame 019','Same can seen again'),(555,'Frame 031','Two different cans')]:
 f.rect(60,y,280,160,LIGHT,BLUE)
 f.circle(185,y+80,15,ORANGE)
 if y==555:f.circle(245,y+115,15,ORANGE)
 f.text(365,y+12,label,32,bold=True);f.text(365,y+60,p,29,maxwidth=360)
f.arrow([(730,390),(835,390)],BLUE)
f.rect(875,120,640,595,'white',GRID)
f.arrow([(930,655),(1440,655)],INK,3);f.arrow([(930,655),(930,170)],INK,3)
f.text(1325,675,'East',29);f.text(958,153,'North',29)
f.circle(1120,390,72,fill=None,stroke=BLUE)
for x,y in [(1098,400),(1135,372),(1130,414)]:f.circle(x,y,9,ORANGE)
f.circle(1120,390,7,BLUE);f.text(1010,272,'track_17',32,bold=True)
f.circle(1350,430,60,fill=None,stroke=BLUE);f.circle(1350,430,9,ORANGE);f.text(1250,514,'track_18',32,bold=True)
f.text(60,805,'Image point + capture-time pose + calibration',32,bold=True)
f.text(60,850,'Project to the ground, then associate observations using position uncertainty and appearance.',31,maxwidth=1440)
f.text(60,934,'Illustrative uncertainty regions; same category does not mean the same object.',28,color=GREY)
f.save()

# 9 Dataset schema and grouped splits.
f=Figure('09_dataset',1080)
f.box(60,50,1480,130,'One episode','episode_id  |  session  |  layout  |  instruction  |  calibration  |  split')
xs=[60,565,1070]
for x,title,body in [(60,'Observation','RGB frame\nEstimated state\nCapture time'),(565,'Action label','Position increment\nAccepted target\nCommand time'),(1070,'Evaluator only','True object positions\nSuccess / failure\nPrivileged state')]:f.box(x,250,470,220,title,body,fill=LIGHT if x<1070 else '#F5F5F5')
f.arrow([(430,180),(295,250)],BLUE);f.arrow([(800,180),(800,250)],BLUE);f.arrow([(1190,180),(1305,250)],GREY)
f.arrow([(295,470),(295,565),(760,565)],BLUE);f.arrow([(800,470),(800,565)],BLUE)
f.text(70,605,'Training loader reads observations and action labels only.',32,bold=True)
f.text(1090,510,'Never an input\nto the policy',30,color=ORANGE)
f.text(60,715,'SPLIT WHOLE GROUPS BEFORE TRAINING',33,bold=True)
for x,title,body in [(60,'Training','Fit model weights\n150 toy episodes'),(565,'Validation','Choose settings\n30 toy episodes'),(1070,'Test','Final comparison\n30 toy episodes')]:f.box(x,790,470,165,title,body)
f.text(60,1005,'For field work, group by session, layout and physical object instance as required by the question.',28,color=GREY)
f.save()

# 10 Training vs inference process.
f=Figure('10_training',1050)
f.text(55,15,'WORKSTATION TRAINING',35,bold=True)
f.box(50,90,450,170,'Demonstrations','Image + task + state\nExpert action label')
f.box(580,90,440,170,'Adapted SmolVLA','Drone projections\nPretrained backbone')
f.box(1100,90,450,170,'Supervised objective','Native flow-matching loss\nUpdate trainable parameters')
f.arrow([(500,175),(580,175)],BLUE);f.arrow([(1020,175),(1100,175)],BLUE)
f.arrow([(1330,260),(1330,340),(800,340),(800,260)])
f.text(1010,357,'Optimiser update',29,color=ORANGE)
f.box(580,430,440,155,'Validation and selection','Loss + closed-loop tests\nValidation scenes only')
f.arrow([(800,340),(800,430)],BLUE)
f.box(1100,430,450,155,'Saved deployment bundle','Weights + processors\nAction schema + versions')
f.arrow([(1020,510),(1100,510)],BLUE)
f.line([(50,675),(1550,675)],GRID,3)
f.text(55,715,'ONBOARD INFERENCE',35,bold=True)
f.box(50,790,450,155,'Newest observation','Image + task + state')
f.box(580,790,440,155,'Frozen policy','Predict position increment')
f.box(1100,790,450,155,'Command supervisor','Validate + send setpoint\nAutopilot executes')
f.arrow([(500,868),(580,868)],BLUE);f.arrow([(1020,868),(1100,868)])
f.text(55,995,'Episodes organise the data. This workflow uses imitation learning; no reward or online RL is required.',28,color=GREY)
f.save()

# 11 Scheduling with categorical phases, not fabricated benchmark values.
f=Figure('11_orin',1030)
f.text(60,15,'PROPOSED SCHEDULE TO BENCHMARK',34,bold=True)
f.text(60,65,'Phase widths are illustrative. Model durations must be measured.',29,color=GREY)
left,right=375,1530
phases=[(375,390,'Local inspection'),(765,380,'Validated hold'),(1145,385,'Resume inspection')]
for x,w,label in phases:
 f.text(x+w/2,150,label,30,bold=True,align='center');f.line([(x,205),(x,855)],GRID,2)
rows=[('Camera + logger',270),('CPU supervisor',410),('GPU inspection',550),('GPU slow planner',690),('Flight controller',830)]
for name,y in rows:f.text(60,y-25,name,29,bold=True);f.line([(left,y+50),(right,y+50)],GRID,2)
for y,label in [(250,'Acquire newest frames and save evidence'),(390,'Validate commands, state, expiry and task IDs'),(810,'Track bounded targets or the validated hold')]:
 f.rect(left,y,1155,60,LIGHT,BLUE);f.text(left+20,y+12,label,29,color=BLUE)
for x,w,label in [(375,390,'Policy + detector'),(1145,385,'Policy + detector')]:
 f.rect(x,530,w,65,LIGHT,BLUE);f.text(x+w/2,545,label,28,color=BLUE,align='center')
f.rect(765,670,380,65,'#FFF2E8',ORANGE);f.text(955,685,'VLM task / analysis',28,color=ORANGE,align='center')
f.text(805,537,'Hold; no stale\npolicy output',28,color=GREY)
f.text(60,946,'One initial option: serialise heavy GPU work while the independent supervisor keeps running.',29,maxwidth=1450)
f.save()

# 12 Transfer ladder.
f=Figure('12_transfer',1060)
f.text(60,15,'INCREASE THE STRENGTH OF THE EVIDENCE IN STAGES',33,bold=True)
rows=[('1','Real image replay','Perception and projection','No changed future views'),('2','Orin with real-time SITL','Device timing under simulated motion','No real vehicle dynamics'),('3','Scripted real flight','Tracking + camera + shadow actions','Policy has no flight authority'),('4','Restricted learned skill','Local inspection transfer','Only the tested envelope'),('5','Complete field mission','Search, analyse and map together','Only the tested conditions')]
for i,(n,a,b,c) in enumerate(rows):
 y=115+i*155
 f.circle(90,y+44,32,BLUE);f.text(90,y+22,n,34,color='white',bold=True,align='center')
 if i<4:f.arrow([(90,y+80),(90,y+123)],BLUE,4)
 f.text(160,y,a,32,bold=True);f.text(160,y+49,b,29,color=BLUE)
 f.text(1000,y+20,c,29,color=GREY,maxwidth=520)
f.text(60,940,'At every stage: record failures, interventions, conditions and the claim the evidence supports.',30,maxwidth=1450)
f.save()

# 13 Factorial design, relationships not scores.
f=Figure('13_experiments',1010)
f.text(650,15,'TASK PLANNING',34,bold=True)
f.text(700,100,'Deterministic rule',32,bold=True,align='center');f.text(1260,100,'VLM planner',32,bold=True,align='center')
f.text(65,305,'Classical\ninspection',32,bold=True)
f.text(65,595,'Learned\nVLA inspection',32,bold=True)
for x,y,title,body in [(400,205,'A  Complete baseline','Classical inspection\nDeterministic planning'),(960,205,'C  Planner comparison','Classical inspection\nVLM planning'),(400,505,'B  Policy comparison','Learned inspection\nDeterministic planning'),(960,505,'D  Combined system','Learned inspection\nVLM planning')]:f.box(x,y,500,205,title,body)
f.arrow([(650,410),(650,505)],ORANGE);f.arrow([(900,307),(960,307)],BLUE)
f.arrow([(1210,410),(1210,505)],ORANGE);f.arrow([(900,607),(960,607)],BLUE)
f.text(60,800,'A versus B isolates the local policy. A versus C isolates the planner.',32,bold=True,maxwidth=1450)
f.text(60,874,'Hold detector, mapping, budgets, starts and command limits fixed.',31)
f.text(60,930,'Then compare D and test whether combining both components adds a benefit.',30,color=GREY)
f.save()

# Figure 5 is retained as supplied; this script regenerates the other thirteen figures.


# Replacements for the single-model edition. Uses the Figure drawing primitives.
f=Figure('01_mission',1030)
f.text(50,15,'NORMAL SURVEY WITH ONE DETOUR',34,bold=True)
f.rect(65,130,660,660,'#F0F5EF','#9AAEA0')
for x in [65,230,395,560,725]:f.line([(x,130),(x,790)],'#D8E3D6',2)
for y in [130,295,460,625,790]:f.line([(65,y),(725,y)],'#D8E3D6',2)
route=[(130,735),(130,190),(295,190),(295,735),(460,735),(460,190),(645,190),(645,735)]
f.arrow(route,BLUE,6)
f.circle(435,420,15,ORANGE);f.text(465,385,'litter',29,color=ORANGE)
f.arrow([(295,440),(400,420)],ORANGE,6)
f.arrow([(420,445),(325,500),(295,500)],ORANGE,4)
f.circle(295,440,9,BLUE)
f.text(70,835,'Blue: survey route',31,color=BLUE)
f.text(70,885,'Orange: inspect and rejoin',31,color=ORANGE)
f.text(70,945,'Illustrative path; save coverage before detouring.',27,color=GREY)
for y,t,b in [(120,'1  Survey normally','One VLA monitors images and mission context.'),(315,'2  Decide to inspect','Save route progress; approach the visible candidate.'),(510,'3  Analyse and mark','Record a supported label, location and image.'),(705,'4  Resume the survey','Rejoin unfinished coverage; avoid duplicate objects.')]:
 f.box(865,y,685,145,t,b,size=29)
 if y<705:f.arrow([(1205,y+145),(1205,y+195)])
f.save()

f=Figure('03_architecture',1030)
f.text(50,20,'ONE LEARNED MODEL ON THE ORIN',35,bold=True)
f.box(50,280,350,280,'Observation','Image + pose\nInstruction\nMission mode\nMap / coverage context',size=28)
f.rect(475,180,600,420,LIGHT,BLUE)
f.text(500,202,'ONE VLA',36,bold=True,color=BLUE)
f.text(500,264,'Shared vision + language backbone',29,bold=True)
for y,t in [(340,'Choose event + ground candidate'),(410,'Predict bounded inspection move'),(480,'Describe visible litter evidence')]:
 f.text(505,y,t,29,color=BLUE)
f.box(1160,180,390,420,'Mission manager','Follow survey route\nSave / restore progress\nValidate proposals\nProject and save map\n\nOrdinary software',size=28)
f.arrow([(400,420),(475,420)],BLUE)
f.arrow([(1075,390),(1160,390)],ORANGE)

f.box(475,765,600,165,'Litter map','One record per object\nLocation + label + image evidence',size=29)
f.box(1160,765,390,165,'Existing autopilot','Stable flight\nTrack accepted targets',size=29)
f.arrow([(1350,600),(1350,765)],ORANGE)
f.text(1380,644,'Position /\nvelocity',27,color=ORANGE)
f.arrow([(1210,600),(1210,685),(775,685),(775,765)],BLUE)
f.text(570,637,'Accepted evidence + geometric location',27,color=BLUE)
f.text(50,980,'The manager supplies mission context. New observations close the loop after movement.',28,color=GREY)
f.save()

f=Figure('09_dataset',1030)
f.box(50,30,1500,130,'One complete mission','Survey → inspect → analyse → resume; shared mission / layout / session IDs',size=30)
for x,t,b in [(50,'Deployable inputs','Image + estimated pose\nInstruction + current mode\nBudget + map / coverage'),(560,'Supervised outputs','Event + region + labels\nExpert inspection action\nValidity mask for each head'),(1070,'Evaluator only','True item positions\nFuture success / failure\nPrivileged simulator state')]:f.box(x,245,480,220,t,b,size=28)
for x in [290,800,1310]:f.arrow([(x,160),(x,245)],BLUE if x<1000 else GREY)
f.text(1085,498,'Never a deployed model input',27,color=ORANGE)
f.text(50,580,'VALID LABELS DEPEND ON THE MISSION MODE',32,bold=True)
for x,t,b in [(50,'SURVEY','Event + visible region\nNo inspection-action loss'),(560,'INSPECT','Event + bounded movement\nNo future evidence labels'),(1070,'ANALYSE','Category + attributes\nUnknown when unsupported')]:f.box(x,650,480,175,t,b,size=27)
f.text(50,890,'Split whole missions and field sessions before sampling frames.',31,bold=True)
f.text(50,950,'The bundled 150 / 30 / 30 episodes are local teaching skills, not complete missions.',28,color=GREY)
f.save()

f=Figure('10_training',1020)
f.text(50,20,'WORKSTATION TRAINING',34,bold=True)
f.box(50,120,410,210,'Mixed demonstrations','Annotated images\nInspection actions\nMission events + context',size=29)
f.box(595,120,410,210,'One shared model','Image / language features\nMission and semantic heads\nFlow-matching action expert',size=27)
f.box(1130,120,420,210,'Masked supervised loss','Event + region + semantics\nValid inspection actions\nUpdate selected weights',size=27)
f.arrow([(460,225),(595,225)],BLUE);f.arrow([(1005,225),(1130,225)],BLUE)
f.box(595,445,955,160,'Validate complete missions and save one checkpoint','Check map quality, coverage, command validity and runtime; retain all interface versions.',size=29)
f.arrow([(1340,330),(1340,445)],BLUE)
f.line([(50,665),(1550,665)],GRID,3)
f.text(50,700,'ORIN INFERENCE',34,bold=True)
for x,t,b in [(50,'Newest input','Image + task + context'),(595,'Same frozen model','Mode selects active heads'),(1130,'Ordinary execution','Validate events and targets')]:f.box(x,790,420,140,t,b,size=28)
f.arrow([(470,860),(595,860)],BLUE);f.arrow([(1015,860),(1130,860)],ORANGE)
f.text(50,974,'Research design: the supplied trainer currently covers the movement pilot only.',28,color=GREY)
f.save()

f=Figure('11_orin',990)
f.text(50,20,'ONE MODEL ACROSS MISSION MODES',34,bold=True)
f.text(50,73,'Phases are schematic; durations and achievable rates must be measured.',28,color=GREY)
xs=[420,785,1150];ww=365
for x,t in zip(xs,['SURVEY','INSPECT','ANALYSE / RESUME']):
 f.text(x+ww/2,180,t,27,bold=True,align='center');f.line([(x,225),(x,840)],GRID,2)
for name,y in [('Camera and logger',295),('CPU manager',455),('ONE VLA on GPU',615),('Flight execution',790)]:
 f.text(50,y,name,29,bold=True)
for y,txt in [(270,'Acquire observations and save evidence'),(430,'Check context, events, command validity and route progress')]:
 f.rect(420,y,1095,85,LIGHT,BLUE);f.text(442,y+25,txt,28,color=BLUE)
for x,t in zip(xs,['Events + grounding','Events + actions','Labels + events']):
 f.rect(x,595,ww,85,LIGHT,BLUE);f.text(x+ww/2,620,t,26,color=BLUE,align='center')
for x,t in zip(xs,['Normal route','Bounded VLA moves','Hold then rejoin']):
 f.rect(x,770,ww,85,'#FFF2E8',ORANGE);f.text(x+ww/2,795,t,26,color=ORANGE,align='center')
f.text(50,930,'The model decides when to detour and resume. The manager preserves unfinished coverage.',29)
f.save()

f=Figure('13_experiments',1020)
f.text(50,20,'WHAT DOES THE UNIFIED POLICY CONTRIBUTE?',34,bold=True)
for y,t,b in [(135,'B0   Classical system','Detector + fixed decision rules + classical inspection'),(370,'B1   Same learned features and movements','Unified perception / semantic / action heads + fixed event rules'),(605,'U     Complete single VLA','Learned events + grounding + semantic labels + inspection actions')]:
 f.box(55,y,1490,155,t,b,size=30)
 if y<605:f.arrow([(800,y+155),(800,y+235)],BLUE)
f.text(55,820,'B0 versus U: complete system value',31,bold=True)
f.text(55,873,'B1 versus U: value of learned mission decisions',31,bold=True)
f.text(55,941,'Also remove mission context to test the contribution of history and coverage.',28,color=GREY)
f.save()

f=Figure('14_model',1040)
f.text(50,15,'ONE VLA CHECKPOINT',35,bold=True)
f.box(50,110,420,165,'V   Vision','Camera image\nSigLIP image encoder',size=30)
f.box(580,110,970,165,'L   Language and context','Instruction + projected drone / mission state\nSmolVLM2 shared backbone with SmolLM2 decoder',size=30)
f.arrow([(470,195),(580,195)],BLUE)
f.text(50,338,'Shared features condition all output heads',32,bold=True)
f.line([(260,430),(1340,430)],BLUE,4);f.line([(1065,275),(1065,430)],BLUE,4)
for x,t,b in [(50,'Mission decisions','Event + candidate region\nCategory + attributes\nEvent / region / label heads'),(865,'A   Continuous movement','Bounded north/east increment\nFlow-matching action expert\nInspection mode only')]:
 f.box(x,510,685,245,t,b,size=30)
f.arrow([(390,430),(390,510)],BLUE);f.arrow([(1210,430),(1210,510)],BLUE)
f.text(50,823,'Proposed additions: mission context, event, grounding and semantic heads.',30,bold=True)
f.text(50,885,'Flow matching generates movement; it does not supply mission events automatically.',29)
f.text(50,955,'Ordinary software stores the route, projects locations and validates execution.',29,color=GREY)
f.save()

print("Single VLA edition: 14 figures generated")
