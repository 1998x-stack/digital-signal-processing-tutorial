(()=>{
"use strict";
const ns="http://www.w3.org/2000/svg",PI=Math.PI;
const E=(name,attrs={},text="")=>{const el=document.createElementNS(ns,name);for(const [k,v] of Object.entries(attrs))el.setAttribute(k,String(v));el.textContent=text;return el};
const add=(svg,name,attrs,text="")=>svg.append(E(name,attrs,text));
const line=(svg,x1,y1,x2,y2,color="#c5d6ce",w=1)=>add(svg,"line",{x1,y1,x2,y2,stroke:color,"stroke-width":w});
const text=(svg,x,y,value,color="#53676d")=>add(svg,"text",{x,y,fill:color,"font-size":12,"font-family":"system-ui,PingFang SC,sans-serif"},value);
function chart(svg,series,{color="#147f80",bars=false,labels=""}={}){
 svg.replaceChildren();svg.setAttribute("viewBox","0 0 560 215");
 const max=Math.max(1e-9,...series.map(Math.abs)),left=34,right=536,top=29,bottom=173;
 line(svg,left,bottom,right,bottom);line(svg,left,top,left,bottom);
 const points=[];
 series.forEach((v,i)=>{const x=left+i*(right-left)/Math.max(1,series.length-1),y=bottom-Math.abs(v)/max*132;points.push([x,y]);if(bars)line(svg,x,bottom,x,y,color,2.8);});
 if(!bars)add(svg,"path",{d:points.map(([x,y],i)=>(i?"L":"M")+x.toFixed(2)+" "+y.toFixed(2)).join(" "),fill:"none",stroke:color,"stroke-width":2.7});
 points.forEach(([x,y],i)=>{if(i%Math.max(1,Math.ceil(series.length/12))===0)add(svg,"circle",{cx:x,cy:y,r:3.6,fill:color})});
 text(svg,36,17,"相对幅度（动态缩放）");text(svg,451,200,labels||"频率索引 k →");
}
function dft(x){return x.map((_,k)=>x.reduce((z,v,n)=>({re:z.re+v*Math.cos(2*PI*k*n/x.length),im:z.im-v*Math.sin(2*PI*k*n/x.length)}),{re:0,im:0}))}
function hamming(M,wc){let h=Array.from({length:M},(_,n)=>{const m=n-(M-1)/2,ideal=Math.abs(m)<1e-12?wc/PI:Math.sin(wc*m)/(PI*m),window=.54-.46*Math.cos(2*PI*n/(M-1));return ideal*window});const dc=h.reduce((s,v)=>s+v,0);return h.map(v=>v/dc)}
function mag(h,w){let re=0,im=0;h.forEach((v,n)=>{re+=v*Math.cos(w*n);im-=v*Math.sin(w*n)});return Math.hypot(re,im)}
function stages(x){const N=x.length,bits=Math.log2(N),arr=x.map(v=>({re:v,im:0}));for(let i=0;i<N;i++){const rev=parseInt(i.toString(2).padStart(bits,"0").split("").reverse().join(""),2);if(rev>i)[arr[i],arr[rev]]=[arr[rev],arr[i]];}const result=[[...arr].map(v=>({...v}))];for(let len=2;len<=N;len*=2){for(let base=0;base<N;base+=len){for(let j=0;j<len/2;j++){const w=-2*PI*j/len,c=Math.cos(w),s=Math.sin(w),a=arr[base+j],q=arr[base+j+len/2],t={re:q.re*c-q.im*s,im:q.re*s+q.im*c};arr[base+j]={re:a.re+t.re,im:a.im+t.im};arr[base+j+len/2]={re:a.re-t.re,im:a.im-t.im};}}result.push(arr.map(v=>({...v})));}return result}
const registry={
 dtft(v,svg,out){const M=v,h=Array(M).fill(1/M),x=Array.from({length:121},(_,i)=>mag(h,PI*i/120));chart(svg,x,{labels:"ω：0 → π"});out.textContent="M="+M+" 点平均：DC 增益 1；首个零点 ω=2π/"+M+"；群延迟在非零频带为 "+((M-1)/2)+" 个样本。"},
 dft(v,svg,out){const f=v/10,N=16,x=Array.from({length:N},(_,i)=>Math.cos(2*PI*f*i/N)),X=dft(x).map(z=>Math.hypot(z.re,z.im));chart(svg,X,{bars:true,color:"#d06d4d",labels:"DFT 索引 k →"});out.textContent="N=16，频率="+f.toFixed(1)+" bins；非整频点的窗口边界不连续，谱会泄漏到更多 k。补零不会增加观察时长。"},
 fft(v,svg,out){const input=[1,2,0,0,0,0,0,0],states=stages(input),vals=states[v].map(z=>Math.hypot(z.re,z.im));chart(svg,vals,{bars:true,color:"#7461ba",labels:"蝶形存储位置 →"});out.textContent=v===0?"stage 0：位反转输入，尚未执行蝶形。":("stage "+v+"：已完成块长 "+(2**v)+" 的迭代，stage 3 才是自然顺序 DFT 输出。");},
 fir(v,svg,out){const M=v,h=hamming(M,.35*PI),s=Array.from({length:121},(_,i)=>mag(h,PI*i/120));chart(svg,s,{color:"#147f80",labels:"ω：0 → π"});out.textContent="Hamming 窗，长度 M="+M+"，对称且 DC 增益为 1，理论线性相位群延迟 "+((M-1)/2)+" 个样本；Nyquist 增益约 "+mag(h,PI).toFixed(4)+"。"},
 iir(v,svg,out){const fs=8000,fc=v*fs/100,O=2*fs*Math.tan(PI*fc/fs),a=(2*fs-O)/(2*fs+O),b=O/(2*fs+O),s=Array.from({length:121},(_,i)=>{const w=PI*i/120,cr=Math.cos(w),si=Math.sin(w),nr=b*(1+cr),ni=-b*si,dr=1-a*cr,di=a*si;return Math.hypot(nr,ni)/Math.hypot(dr,di)});chart(svg,s,{color:"#d06d4d",labels:"ω：0 → π"});out.textContent="指定截止 f_c="+Math.round(fc)+" Hz，预畸变 Ω_c="+O.toFixed(1)+" rad/s，数字极点 a="+a.toFixed(4)+"；截止点增益为 1/√2。";},
 biquadpole(bits,svg,out){
 const r=.98,w0=.2*PI,a1=-2*r*Math.cos(w0),a2=r*r;
 const q=x=>{const s=2**bits;return Math.round(x*s)/s};
 const roots=(p,t)=>{const d=p*p-4*t;if(d>=0)return[[(-p+Math.sqrt(d))/2,0],[(-p-Math.sqrt(d))/2,0]];const re=-p/2,im=Math.sqrt(-d)/2;return[[re,im],[re,-im]]};
 const qa1=q(a1),qa2=q(a2),P=roots(a1,a2),Q=roots(qa1,qa2);
 svg.replaceChildren();svg.setAttribute("viewBox","0 0 560 215");
 const cx=250,cy=108,R=88,X=v=>cx+v*R,Y=v=>cy-v*R;
 add(svg,"circle",{cx,cy,r:R,fill:"none",stroke:"#c5d6ce","stroke-width":1.4});
 line(svg,cx-116,cy,cx+116,cy,"#e2ece8",1);line(svg,cx,cy-R-18,cx,cy+R+18,"#e2ece8",1);
 text(svg,cx+96,cy+15,"Re z");text(svg,cx+6,cy-R-8,"Im z");text(svg,cx+70,cy-R-8,"|z| = 1");
 Q.forEach(p=>add(svg,"circle",{cx:X(p[0]),cy:Y(p[1]),r:5.4,fill:"#d06d4d"}));
 P.forEach(p=>add(svg,"circle",{cx:X(p[0]),cy:Y(p[1]),r:5.4,fill:"#147f80"}));
 const rq=Math.hypot(Q[0][0],Q[0][1]),dth=Math.abs(Math.atan2(Q[0][1],Q[0][0])-w0)*180/PI;
 out.textContent="设计半径 0.9800；量化后半径 "+rq.toFixed(4)+"（"+bits+" bit）。"+(rq>=1?"极点已到或越过单位圆：不稳定。":"仍在单位圆内；幅角偏移约 "+dth.toFixed(2)+"°，半径偏移 "+(rq-0.98).toFixed(4)+"。");
 },
 decimate(M,svg,out){
 const N=64*M+1;
 const x=Array.from({length:N},(_,n)=>Math.cos(2*PI*.10*n)+.7*Math.cos(2*PI*.30*n));
 const h=hamming(31,PI/M);
 const conv=(a,b)=>{const y=new Array(a.length+b.length-1).fill(0);a.forEach((av,i)=>b.forEach((bv,j)=>{y[i+j]+=av*bv}));return y};
 const dec=a=>a.filter((_,i)=>i%M===0);
 const K=64,H=K/2;
 const sd=dft(dec(x).slice(0,K)).map(z=>Math.hypot(z.re,z.im));
 const sf=dft(dec(conv(x,h)).slice(0,K)).map(z=>Math.hypot(z.re,z.im));
 const max=Math.max(.0001,...sd.slice(0,H),...sf.slice(0,H)),left=34,right=536,top=29,bottom=173;
 svg.replaceChildren();svg.setAttribute("viewBox","0 0 560 215");
 line(svg,left,bottom,right,bottom);line(svg,left,top,left,bottom);
 const px=i=>left+i*(right-left)/(H-1),py=v=>bottom-v/max*132;
 const draw=(s,c)=>add(svg,"path",{d:s.slice(0,H).map((v,i)=>(i?"L":"M")+px(i).toFixed(1)+" "+py(v).toFixed(1)).join(" "),fill:"none",stroke:c,"stroke-width":2.4});
 draw(sd,"#d06d4d");draw(sf,"#147f80");
 text(svg,36,17,"相对幅度（两曲线同一缩放）");text(svg,404,200,"归一化频率（下采样后 0–0.5）→");
 const alias=(()=>{const f=.30%(1/M);return f>1/(2*M)?1/M-f:f})();
 out.textContent="M="+M+"：新采样率下 Nyquist=0.5；带内 0.10 分量出现在 "+(0.10*M).toFixed(2)+"，0.30 带外分量混叠到 "+alias.toFixed(3)+"（原始归一化轴）＝"+(alias*M).toFixed(2)+"（新采样率轴）。赭色峰即为混叠。";
 },
 cic(N,svg,out){
 const M=8,H=180,left=44,right=536,top=29,bottom=173;
 const db=w=>{const s=Math.abs(Math.sin(M*w/2)/Math.sin(w/2))**N;return 20*Math.log10(Math.max(s,1e-9))-N*20*Math.log10(M)};
 const pts=Array.from({length:H+1},(_,i)=>db(PI*i/H));
 svg.replaceChildren();svg.setAttribute("viewBox","0 0 560 215");
 line(svg,left,bottom,right,bottom);line(svg,left,top,left,bottom);
 const lo=-100,hi=10,py=v=>top+(hi-Math.max(lo,Math.min(hi,v)))/(hi-lo)*144;
 [0,-20,-40,-60,-80].forEach(g=>{const y=py(g);line(svg,left,y,right,y,"#eef3f1",1);text(svg,6,y+4,String(g))});
 text(svg,6,20,"dB（相对直流）");
 add(svg,"path",{d:pts.map((v,i)=>(i?"L":"M")+(left+i*(right-left)/H).toFixed(1)+" "+py(v).toFixed(1)).join(" "),fill:"none",stroke:"#7461ba","stroke-width":2.4});
 text(svg,300,200,"ω：0 → π");
 out.textContent="N="+N+" 级：直流增益 "+(N*20*Math.log10(M)).toFixed(1)+" dB（=M^N，M=8）；第一零点 ω=2π/8≈0.785 rad；第一旁瓣约 "+db(3*PI/M).toFixed(1)+" dB（相对直流）。N 越大阻带压得越低，但通带滚降也更明显。";
 },
 psd(K,svg,out){
 const N=1024;let seed=12345;const rnd=()=>{seed=(seed*16807)%2147483647;return seed/2147483647*2-1};
 const x=Array.from({length:N},rnd);
 const L=Math.floor(N/K);
 const win=Array.from({length:L},(_,n)=>.5-.5*Math.cos(2*PI*n/(L-1)));
 const psum=new Array(L).fill(0);
 for(let s=0;s<K;s++){const seg=x.slice(s*L,s*L+L).map((v,i)=>v*win[i]);const X=dft(seg).map(z=>z.re*z.re+z.im*z.im);for(let i=0;i<L;i++)psum[i]+=X[i]/K;}
 const H=Math.floor(L/2);
 const one=dft(x.slice(0,L).map((v,i)=>v*win[i])).map(z=>z.re*z.re+z.im*z.im);
 const norm=a=>{const m=a.slice(0,H).reduce((s,v)=>s+v,0)/H;return a.slice(0,H).map(v=>v/m)};
 const np=norm(psum),no=norm(one);
 const cv=Math.sqrt(np.reduce((s,v)=>s+(v-1)*(v-1),0)/np.length);
 svg.replaceChildren();svg.setAttribute("viewBox","0 0 560 215");
 const left=44,right=536,top=29,bottom=173,hi=3.5,py=v=>bottom-Math.max(0,Math.min(hi,v))/hi*144;
 line(svg,left,bottom,right,bottom);line(svg,left,top,left,bottom);
 [1,2,3].forEach(g=>{const y=py(g);line(svg,left,y,right,y,"#eef3f1",1);text(svg,6,y+4,String(g))});
 text(svg,4,20,"×均值");
 const draw=(a,c)=>{add(svg,"path",{d:a.map((v,i)=>(i?"L":"M")+(left+i*(right-left)/(a.length-1)).toFixed(1)+" "+py(v).toFixed(1)).join(" "),fill:"none",stroke:c,"stroke-width":2.2})};
 draw(no,"#d06d4d");draw(np,"#147f80");
 text(svg,330,200,"归一化频率（0–0.5）→");
 out.textContent="K="+K+"，每段 "+L+" 点：K 段平均估计的变异系数（跨频点 std/mean）≈ "+cv.toFixed(3)+"，理论约 1/√K = "+(1/Math.sqrt(K)).toFixed(3)+"。青线越平说明方差越小，代价是频率分辨率下降。";
 }
};
document.querySelectorAll('[data-spectrum-lab]').forEach(el=>{const kind=el.dataset.spectrumLab,run=registry[kind],slider=el.querySelector('input[type="range"]'),svg=el.querySelector("svg"),out=el.querySelector("output");if(!run||!slider||!svg||!out)return;const paint=()=>run(Number(slider.value),svg,out);slider.addEventListener("input",paint);paint();});
})();