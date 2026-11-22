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
 iir(v,svg,out){const fs=8000,fc=v*fs/100,O=2*fs*Math.tan(PI*fc/fs),a=(2*fs-O)/(2*fs+O),b=O/(2*fs+O),s=Array.from({length:121},(_,i)=>{const w=PI*i/120,cr=Math.cos(w),si=Math.sin(w),nr=b*(1+cr),ni=-b*si,dr=1-a*cr,di=a*si;return Math.hypot(nr,ni)/Math.hypot(dr,di)});chart(svg,s,{color:"#d06d4d",labels:"ω：0 → π"});out.textContent="指定截止 f_c="+Math.round(fc)+" Hz，预畸变 Ω_c="+O.toFixed(1)+" rad/s，数字极点 a="+a.toFixed(4)+"；截止点增益为 1/√2。";}
};
document.querySelectorAll('[data-spectrum-lab]').forEach(el=>{const kind=el.dataset.spectrumLab,run=registry[kind],slider=el.querySelector('input[type="range"]'),svg=el.querySelector("svg"),out=el.querySelector("output");if(!run||!slider||!svg||!out)return;const paint=()=>run(Number(slider.value),svg,out);slider.addEventListener("input",paint);paint();});
})();