"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[9978],{8337:function(t,e,s){s.d(e,{Z:function(){return o}});var a=s(6813),l={name:"Utils",mixins:[a.Z],computed:{audioExtensions(){return new Set(["3gp","aa","aac","aax","act","aiff","amr","ape","au","awb","dct","dss","dvf","flac","gsm","iklax","ivs","m4a","m4b","m4p","mmf","mp3","mpc","msv","nmf","nsf","ogg,","opus","ra,","raw","sln","tta","vox","wav","wma","wv","webm","8svx"])},videoExtensions(){return new Set(["webm","mkv","flv","flv","vob","ogv","ogg","drc","gif","gifv","mng","avi","mts","m2ts","mov","qt","wmv","yuv","rm","rmvb","asf","amv","mp4","m4p","m4v","mpg","mp2","mpeg","mpe","mpv","mpg","mpeg","m2v","m4v","svi","3gp","3g2","mxf","roq","nsv","flv","f4v","f4p","f4a","f4b"])},mediaExtensions(){return new Set([...this.videoExtensions,...this.audioExtensions])}},methods:{convertTime(t){t=parseFloat(t);const e={};e.h=""+parseInt(t/3600),e.m=""+parseInt(t/60-60*e.h),e.s=""+parseInt(t-(3600*e.h+60*e.m));for(const a of["m","s"])parseInt(e[a])<10&&(e[a]="0"+e[a]);const s=[];return parseInt(e.h)&&s.push(e.h),s.push(e.m,e.s),s.join(":")},async startStreaming(t,e=!1){let s=t,a=null;t instanceof Object?(s=t.url,a=t.subtitles):t={url:s};const l=await this.request("media.start_streaming",{media:s,subtitles:a,download:e});return{...t,...l}},async stopStreaming(t){await this.request("media.stop_streaming",{media_id:t})}}};const n=l;var o=n},9978:function(t,e,s){s.d(e,{Z:function(){return Bt}});var a=s(6252);const l={class:"media-container"},n={class:"view-container"},o={class:"controls-container"};function i(t,e,s,i,u,r){const c=(0,a.up)("Controls");return(0,a.wg)(),(0,a.iD)("div",l,[(0,a._)("div",n,[(0,a.WI)(t.$slots,"default",{},void 0,!0)]),(0,a._)("div",o,[(0,a.Wm)(c,{status:s.status,track:s.track,buttons:s.buttons,onPlay:e[0]||(e[0]=e=>t.$emit("play",e)),onPause:e[1]||(e[1]=e=>t.$emit("pause",e)),onStop:e[2]||(e[2]=e=>t.$emit("stop")),onPrevious:e[3]||(e[3]=e=>t.$emit("previous")),onNext:e[4]||(e[4]=e=>t.$emit("next")),onSeek:e[5]||(e[5]=e=>t.$emit("seek",e)),onSetVolume:e[6]||(e[6]=e=>t.$emit("set-volume",e)),onConsume:e[7]||(e[7]=e=>t.$emit("consume",e)),onRepeat:e[8]||(e[8]=e=>t.$emit("repeat",e)),onRandom:e[9]||(e[9]=e=>t.$emit("random",e)),onSearch:e[10]||(e[10]=e=>t.$emit("search",e))},null,8,["status","track","buttons"])])])}var u=s(3577),r=s(9963);const c=t=>((0,a.dD)("data-v-8db4988a"),t=t(),(0,a.Cn)(),t),d={class:"row"},p=c((()=>(0,a._)("div",{class:"col-3"},null,-1))),m={class:"col-6"},v={class:"buttons"},k=c((()=>(0,a._)("i",{class:"icon fa fa-step-backward"},null,-1))),b=[k],f=c((()=>(0,a._)("i",{class:"icon fa fa-stop"},null,-1))),g=[f],h=c((()=>(0,a._)("i",{class:"icon fa fa-step-forward"},null,-1))),_=[h],y=c((()=>(0,a._)("div",{class:"col-3"},null,-1))),w={class:"row"},C={class:"col-9 volume-container"},x={class:"col-1"},$=["disabled"],D=c((()=>(0,a._)("i",{class:"icon fa fa-volume-up"},null,-1))),q=[D],S={class:"col-11 volume-slider"},T={class:"col-3 list-controls"},P=c((()=>(0,a._)("i",{class:"icon fa fa-utensils"},null,-1))),I=[P],Z=c((()=>(0,a._)("i",{class:"icon fa fa-random"},null,-1))),j=[Z],z=c((()=>(0,a._)("i",{class:"icon fa fa-redo"},null,-1))),M=[z],O={class:"row"},W={class:"col-s-2 col-m-1 time"},N=["textContent"],U={class:"col-s-8 col-m-10 time-bar"},E={class:"col-s-2 col-m-1 time"},R=["textContent"],L={class:"controls"},A={class:"playback-controls mobile tablet col-2"},B=["title"],H={key:0,class:"icon play-pause fa fa-pause"},V={key:1,class:"icon play-pause fa fa-play"},F={class:"track-container col-s-8 col-m-8 col-l-3"},Y={key:0,class:"track-info"},G={key:0,class:"title"},J=["href","textContent"],K=["href","textContent"],Q=["textContent"],X={key:1,class:"artist"},tt=["href","textContent"],et={class:"playback-controls desktop col-6"},st={class:"row buttons"},at=c((()=>(0,a._)("i",{class:"icon fa fa-step-backward"},null,-1))),lt=[at],nt=["title"],ot={key:0,class:"icon play-pause fa fa-pause"},it={key:1,class:"icon play-pause fa fa-play"},ut=c((()=>(0,a._)("i",{class:"icon fa fa-stop"},null,-1))),rt=[ut],ct=c((()=>(0,a._)("i",{class:"icon fa fa-step-forward"},null,-1))),dt=[ct],pt={class:"row"},mt={class:"col-1 time"},vt=["textContent"],kt={class:"col-10"},bt={class:"col-1 time"},ft=["textContent"],gt={class:"col-2 pull-right mobile tablet right-buttons"},ht=["title"],_t={class:"col-3 pull-right desktop"},yt={class:"row list-controls"},wt=c((()=>(0,a._)("i",{class:"icon fa fa-utensils"},null,-1))),Ct=[wt],xt=c((()=>(0,a._)("i",{class:"icon fa fa-random"},null,-1))),$t=[xt],Dt=c((()=>(0,a._)("i",{class:"icon fa fa-redo"},null,-1))),qt=[Dt],St={class:"row volume-container"},Tt={class:"col-2"},Pt=["disabled"],It=c((()=>(0,a._)("i",{class:"icon fa fa-volume-up"},null,-1))),Zt=[It],jt={class:"col-10"};function zt(t,e,s,l,n,o){const i=(0,a.up)("Slider");return(0,a.wg)(),(0,a.iD)(a.HY,null,[(0,a._)("div",{class:(0,u.C_)(["extension fade-in",{hidden:!n.expanded}])},[(0,a._)("div",d,[p,(0,a._)("div",m,[(0,a._)("div",v,[n.buttons_.previous?((0,a.wg)(),(0,a.iD)("button",{key:0,onClick:e[0]||(e[0]=e=>t.$emit("previous")),title:"Play previous track"},b)):(0,a.kq)("",!0),n.buttons_.stop&&"stop"!==s.status.state?((0,a.wg)(),(0,a.iD)("button",{key:1,onClick:e[1]||(e[1]=e=>t.$emit("stop")),title:"Stop playback"},g)):(0,a.kq)("",!0),n.buttons_.next?((0,a.wg)(),(0,a.iD)("button",{key:2,onClick:e[2]||(e[2]=e=>t.$emit("next")),title:"Play next track"},_)):(0,a.kq)("",!0)])]),y]),(0,a._)("div",w,[(0,a._)("div",C,[(0,a._)("div",x,[(0,a._)("button",{disabled:null==s.status.muted,onClick:e[3]||(e[3]=e=>t.$emit(s.status.muted?"unmute":"mute"))},q,8,$)]),(0,a._)("div",S,[(0,a.Wm)(i,{value:s.status.volume,range:s.volumeRange,disabled:null==s.status.volume,onMouseup:e[4]||(e[4]=e=>t.$emit("set-volume",e.target.value))},null,8,["value","range","disabled"])])]),(0,a._)("div",T,[n.buttons_.consume?((0,a.wg)(),(0,a.iD)("button",{key:0,onClick:e[5]||(e[5]=e=>t.$emit("consume",!s.status.consume)),class:(0,u.C_)({enabled:s.status.consume}),title:"Toggle consume mode"},I,2)):(0,a.kq)("",!0),n.buttons_.random?((0,a.wg)(),(0,a.iD)("button",{key:1,onClick:e[6]||(e[6]=e=>t.$emit("random",!s.status.random)),class:(0,u.C_)({enabled:s.status.random}),title:"Toggle shuffle"},j,2)):(0,a.kq)("",!0),n.buttons_.repeat?((0,a.wg)(),(0,a.iD)("button",{key:2,onClick:e[7]||(e[7]=e=>t.$emit("repeat",!s.status.repeat)),class:(0,u.C_)({enabled:s.status.repeat}),title:"Toggle repeat"},M,2)):(0,a.kq)("",!0)])]),(0,a._)("div",O,[(0,a._)("div",W,[(0,a._)("span",{class:"elapsed-time",textContent:(0,u.zw)(null==n.elapsed||"play"!==s.status.state&&"pause"!==s.status.state?"-:--":t.convertTime(n.elapsed))},null,8,N)]),(0,a._)("div",U,[(0,a.Wm)(i,{value:n.elapsed,range:[0,o.duration],disabled:!o.duration||"stop"===s.status.state,onMouseup:e[8]||(e[8]=e=>t.$emit("seek",e.target.value))},null,8,["value","range","disabled"])]),(0,a._)("div",E,[(0,a._)("span",{class:"total-time",textContent:(0,u.zw)(o.duration&&"stop"!==s.status.state?t.convertTime(o.duration):"-:--")},null,8,R)])])],2),(0,a._)("div",L,[(0,a._)("div",A,[(0,a._)("button",{onClick:e[9]||(e[9]=e=>t.$emit("play"===s.status.state?"pause":"play")),title:"play"===s.status.state?"Pause":"Play"},["play"===s.status.state?((0,a.wg)(),(0,a.iD)("i",H)):((0,a.wg)(),(0,a.iD)("i",V))],8,B)]),(0,a._)("div",F,[s.track&&"stop"!==s.status?.state?((0,a.wg)(),(0,a.iD)("div",Y,["play"===s.status.state||"pause"===s.status.state?((0,a.wg)(),(0,a.iD)("div",G,[s.track.album?((0,a.wg)(),(0,a.iD)("a",{key:0,href:t.$route.fullPath,textContent:(0,u.zw)(s.track.title?.length?s.track.title:"[No Title]"),onClick:e[10]||(e[10]=(0,r.iM)((e=>t.$emit("search",{artist:s.track.artist,album:s.track.album})),["prevent"]))},null,8,J)):s.track.url?((0,a.wg)(),(0,a.iD)("a",{key:1,href:s.track.url,textContent:(0,u.zw)(s.track.title?.length?s.track.title:"[No Title]")},null,8,K)):((0,a.wg)(),(0,a.iD)("span",{key:2,textContent:(0,u.zw)(s.track.title?.length?s.track.title:"[No Title]")},null,8,Q))])):(0,a.kq)("",!0),!s.track.artist?.length||"play"!==s.status.state&&"pause"!==s.status.state?(0,a.kq)("",!0):((0,a.wg)(),(0,a.iD)("div",X,[(0,a._)("a",{href:t.$route.fullPath,textContent:(0,u.zw)(s.track.artist),onClick:e[11]||(e[11]=(0,r.iM)((e=>t.$emit("search",{artist:s.track.artist})),["prevent"]))},null,8,tt)]))])):(0,a.kq)("",!0)]),(0,a._)("div",et,[(0,a._)("div",st,[n.buttons_.previous?((0,a.wg)(),(0,a.iD)("button",{key:0,onClick:e[12]||(e[12]=e=>t.$emit("previous")),title:"Play previous track"},lt)):(0,a.kq)("",!0),(0,a._)("button",{onClick:e[13]||(e[13]=e=>t.$emit("play"===s.status.state?"pause":"play")),title:"play"===s.status.state?"Pause":"Play"},["play"===s.status.state?((0,a.wg)(),(0,a.iD)("i",ot)):((0,a.wg)(),(0,a.iD)("i",it))],8,nt),n.buttons_.stop&&"stop"!==s.status.state?((0,a.wg)(),(0,a.iD)("button",{key:1,onClick:e[14]||(e[14]=e=>t.$emit("stop")),title:"Stop playback"},rt)):(0,a.kq)("",!0),n.buttons_.next?((0,a.wg)(),(0,a.iD)("button",{key:2,onClick:e[15]||(e[15]=e=>t.$emit("next")),title:"Play next track"},dt)):(0,a.kq)("",!0)]),(0,a._)("div",pt,[(0,a._)("div",mt,[(0,a._)("span",{class:"elapsed-time",textContent:(0,u.zw)(null==n.elapsed||"play"!==s.status.state&&"pause"!==s.status.state?"-:--":t.convertTime(n.elapsed))},null,8,vt)]),(0,a._)("div",kt,[(0,a.Wm)(i,{value:n.elapsed,range:[0,o.duration],disabled:!o.duration||"stop"===s.status.state,onMouseup:e[16]||(e[16]=e=>t.$emit("seek",e.target.value))},null,8,["value","range","disabled"])]),(0,a._)("div",bt,[(0,a._)("span",{class:"total-time",textContent:(0,u.zw)(o.duration&&"stop"!==s.status.state?t.convertTime(o.duration):"-:--")},null,8,ft)])])]),(0,a._)("div",gt,[(0,a._)("button",{onClick:e[17]||(e[17]=t=>n.expanded=!n.expanded),title:n.expanded?"Show more controls":"Hide extra controls"},[(0,a._)("i",{class:(0,u.C_)(["fas",["fa-chevron-"+(n.expanded?"down":"up")]])},null,2)],8,ht)]),(0,a._)("div",_t,[(0,a._)("div",yt,[n.buttons_.consume?((0,a.wg)(),(0,a.iD)("button",{key:0,onClick:e[18]||(e[18]=e=>t.$emit("consume")),class:(0,u.C_)({enabled:s.status.consume}),title:"Toggle consume mode"},Ct,2)):(0,a.kq)("",!0),n.buttons_.random?((0,a.wg)(),(0,a.iD)("button",{key:1,onClick:e[19]||(e[19]=e=>t.$emit("random")),class:(0,u.C_)({enabled:s.status.random}),title:"Toggle shuffle"},$t,2)):(0,a.kq)("",!0),n.buttons_.repeat?((0,a.wg)(),(0,a.iD)("button",{key:2,onClick:e[20]||(e[20]=e=>t.$emit("repeat")),class:(0,u.C_)({enabled:s.status.repeat}),title:"Toggle repeat"},qt,2)):(0,a.kq)("",!0)]),(0,a._)("div",St,[(0,a._)("div",Tt,[(0,a._)("button",{disabled:null==s.status.muted,onClick:e[21]||(e[21]=e=>t.$emit(s.status.muted?"unmute":"mute"))},Zt,8,Pt)]),(0,a._)("div",jt,[(0,a.Wm)(i,{value:s.status.volume,range:s.volumeRange,disabled:null==s.status.volume,onMouseup:e[22]||(e[22]=e=>t.$emit("set-volume",e.target.value))},null,8,["value","range","disabled"])])])])])],64)}var Mt=s(6813),Ot=s(8337),Wt=s(6237),Nt={name:"Controls",components:{Slider:Wt.Z},mixins:[Mt.Z,Ot.Z],emits:["search","previous","next","play","pause","stop","seek","consume","random","repeat","set-volume","mute","unmute"],props:{track:{type:Object},status:{type:Object,default:()=>{}},buttons:{type:Object,default:()=>({previous:!0,next:!0,stop:!0,consume:!0,random:!0,repeat:!0})},volumeRange:{type:Array,default:()=>[0,100]}},data(){const t=Object.keys(this.buttons)?.length?this.buttons:{previous:!0,next:!0,stop:!0,consume:!0,random:!0,repeat:!0};return{expanded:!1,lastSync:0,elapsed:this.status?.elapsed||this.status?.position,buttons_:t}},computed:{duration(){return null!=this.status?.duration?this.status.duration:this.track?.duration}},methods:{getTime(){return(new Date).getTime()/1e3}},mounted(){const t=this;this.lastSync=this.getTime(),this.$watch((()=>this.track),(e=>{e&&"play"===t.status?.state||(t.lastSync=this.getTime())})),this.$watch((()=>this.status),(()=>{t.lastSync=this.getTime()})),setInterval((()=>{"stop"!==t.status?.state&&(t.elapsed=t.status?.elapsed||t.status?.position||0,"play"===t.status?.state&&(t.elapsed+=Math.round(this.getTime()-t.lastSync)))}),1e3)}},Ut=s(3744);const Et=(0,Ut.Z)(Nt,[["render",zt],["__scopeId","data-v-8db4988a"]]);var Rt=Et,Lt={name:"View",components:{Controls:Rt},emits:["play","pause","stop","next","previous","set-volume","seek","consume","random","repeat","search"],props:{pluginName:{type:String,required:!0},status:{type:Object,default:()=>{}},track:{type:Object},buttons:{type:Object}}};const At=(0,Ut.Z)(Lt,[["render",i],["__scopeId","data-v-70d7a7df"]]);var Bt=At},6237:function(t,e,s){s.d(e,{Z:function(){return k}});var a=s(6252),l=s(3577),n=s(9963);const o={class:"slider-wrapper"},i=["min","max","step","disabled","value"],u={class:"track-inner",ref:"track"},r={class:"thumb",ref:"thumb"},c=["textContent"];function d(t,e,s,d,p,m){return(0,a.wg)(),(0,a.iD)("label",o,[(0,a._)("input",{class:(0,l.C_)(["slider",{"with-label":s.withLabel}]),type:"range",min:s.range[0],max:s.range[1],step:s.step,disabled:s.disabled,value:s.value,ref:"range",onInput:e[0]||(e[0]=(0,n.iM)(((...t)=>m.onUpdate&&m.onUpdate(...t)),["stop"])),onChange:e[1]||(e[1]=(0,n.iM)(((...t)=>m.onUpdate&&m.onUpdate(...t)),["stop"]))},null,42,i),(0,a._)("div",{class:(0,l.C_)(["track",{"with-label":s.withLabel}])},[(0,a._)("div",u,null,512)],2),(0,a._)("div",r,null,512),s.withLabel?((0,a.wg)(),(0,a.iD)("span",{key:0,class:"label",textContent:(0,l.zw)(s.value),ref:"label"},null,8,c)):(0,a.kq)("",!0)])}var p={name:"Slider",emits:["input","change","mouseup","mousedown","touchstart","touchend","keyup","keydown"],props:{value:{type:Number},disabled:{type:Boolean,default:!1},range:{type:Array,default:()=>[0,100]},step:{type:Number,default:1},withLabel:{type:Boolean,default:!1}},methods:{onUpdate(t){this.update(t.target.value),this.$emit(t.type,{...t,target:{...t.target,value:this.$refs.range.value}})},update(t){const e=this.$refs.range.clientWidth,s=(t-this.range[0])/(this.range[1]-this.range[0]),a=s*e,l=this.$refs.thumb;l.style.left=a-l.clientWidth/2+"px",this.$refs.thumb.style.transform=`translate(-${s}%, -50%)`,this.$refs.track.style.width=`${a}px`}},mounted(){null!=this.value&&this.update(this.value)}},m=s(3744);const v=(0,m.Z)(p,[["render",d],["__scopeId","data-v-15d8c6c5"]]);var k=v}}]);
//# sourceMappingURL=9978.94898f2d.js.map