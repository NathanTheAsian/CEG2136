from pathlib import Path
import re, bisect, csv
summary=[]
rows=[]
for filename,mode in [('Addition.sim.vcd',0),('Subtraction.sim.vcd',1)]:
 text=Path(filename).read_text(); names={m[0]:m[1] for m in re.findall(r'\$var reg 1 (\S+) (\S+) \$end',text)}
 states=[]; times=[]; state={}
 for block in re.split(r'(?m)^#',text)[1:]:
  lines=block.splitlines(); time=int(lines[0])
  for line in lines[1:]:
   if line and line[0] in '01xXzZ' and line[1:] in names: state[names[line[1:]]]=line[0]
  times.append(time); states.append(state.copy())
 errors=[]; seen=set(); overflow_count=0
 for step in range(256):
  t=step*25000+12500; s=states[bisect.bisect_right(times,t)-1]
  val=lambda prefix:sum(int(s[prefix+str(i)])<<i for i in range(4))
  a,b,r=val('A'),val('B'),val('SA'); m=int(s['M']); ov=int(s['OV']); seen.add((a,b,m))
  signed=lambda v:v if v<8 else v-16
  exact=signed(a)+signed(b) if m==0 else signed(a)-signed(b)
  expected=exact&15; expected_ov=int(not -8<=exact<=7)
  ok=m==mode and r==expected and ov==expected_ov
  if not ok:errors.append((t/1000,a,b,r,expected,ov,expected_ov))
  overflow_count+=ov
  rows.append([t/1000,m,a,b,r,expected,ov,expected_ov,ok])
 assert len(seen)==256
 summary.append(f'{filename}: 256 unique cases, {len(errors)} mismatches, {overflow_count} overflow cases. First failures: {errors[:8]}')
with open('verification.csv','w',newline='') as f:
 writer=csv.writer(f);writer.writerow(['time_ns','M','A_unsigned','B_unsigned','actual_result','expected_result','actual_OV','expected_OV','pass']);writer.writerows(rows)
Path('verification.txt').write_text('\n'.join(summary))
print('\n'.join(summary))
