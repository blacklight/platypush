"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[7841],{7191:function(t,s,e){e.d(s,{Z:function(){return v}});var a=e(6252),i=e(3577);const n={class:"progress-bar-container"},r={class:"col-s-2 col-m-1 time"},l=["textContent"],u={class:"col-s-8 col-m-10 time-bar"},o={class:"col-s-2 col-m-1 time"},c=["textContent"];function p(t,s,e,p,h,m){const g=(0,a.up)("Slider");return(0,a.wg)(),(0,a.iD)("div",n,[(0,a._)("div",r,[(0,a._)("span",{class:"elapsed-time",textContent:(0,i.zw)(null==e.elapsed||"play"!==e.status.state&&"pause"!==e.status.state?"-:--":t.convertTime(e.elapsed))},null,8,l)]),(0,a._)("div",u,[(0,a.Wm)(g,{value:e.elapsed,range:[0,e.duration],disabled:!e.duration||"stop"===e.status.state,onChange:s[0]||(s[0]=s=>t.$emit("seek",s.target.value))},null,8,["value","range","disabled"])]),(0,a._)("div",o,[(0,a._)("span",{class:"total-time",textContent:(0,i.zw)(e.duration&&"stop"!==e.status.state?t.convertTime(e.duration):"-:--")},null,8,c)])])}var h=e(1065),m=e(8140),g={components:{Slider:m.Z},emits:["seek"],mixins:[h.Z],props:{elapsed:{type:Number},duration:{type:Number},status:{type:Object,default:()=>({})}}},d=e(3744);const k=(0,d.Z)(g,[["render",p],["__scopeId","data-v-3894ad4d"]]);var v=k},1065:function(t,s,e){e.d(s,{Z:function(){return r}});e(560);var a=e(8637),i={name:"Utils",mixins:[a.Z],computed:{audioExtensions(){return new Set(["3gp","aa","aac","aax","act","aiff","amr","ape","au","awb","dct","dss","dvf","flac","gsm","iklax","ivs","m4a","m4b","m4p","mmf","mp3","mpc","msv","nmf","nsf","ogg,","opus","ra,","raw","sln","tta","vox","wav","wma","wv","webm","8svx"])},videoExtensions(){return new Set(["webm","mkv","flv","flv","vob","ogv","ogg","drc","gif","gifv","mng","avi","mts","m2ts","mov","qt","wmv","yuv","rm","rmvb","asf","amv","mp4","m4p","m4v","mpg","mp2","mpeg","mpe","mpv","mpg","mpeg","m2v","m4v","svi","3gp","3g2","mxf","roq","nsv","flv","f4v","f4p","f4a","f4b"])},mediaExtensions(){return new Set([...this.videoExtensions,...this.audioExtensions])}},methods:{convertTime(t){t=parseFloat(t);const s={};s.h=""+parseInt(t/3600),s.m=""+parseInt(t/60-60*s.h),s.s=""+parseInt(t-(3600*s.h+60*s.m));for(const a of["m","s"])parseInt(s[a])<10&&(s[a]="0"+s[a]);const e=[];return parseInt(s.h)&&e.push(s.h),e.push(s.m,s.s),e.join(":")},async startStreaming(t,s,e=!1){let a=t,i=null;t instanceof Object?(a=t.url,i=t.subtitles):t={url:a};const n=await this.request(`${s}.start_streaming`,{media:a,subtitles:i,download:e});return{...t,...n}},async stopStreaming(t,s){await this.request(`${s}.stop_streaming`,{media_id:t})}}};const n=i;var r=n},8140:function(t,s,e){e.d(s,{Z:function(){return k}});var a=e(6252),i=e(3577),n=e(9963);const r={class:"slider-wrapper"},l=["textContent"],u=["textContent"],o={class:"slider-container"},c=["min","max","step","disabled","value"],p=["textContent"];function h(t,s,e,h,m,g){return(0,a.wg)(),(0,a.iD)("label",r,[e.withRange?((0,a.wg)(),(0,a.iD)("span",{key:0,class:(0,i.C_)(["range-labels",{"with-label":e.withLabel}])},[e.withRange?((0,a.wg)(),(0,a.iD)("span",{key:0,class:"label left",textContent:(0,i.zw)(e.range[0])},null,8,l)):(0,a.kq)("",!0),e.withRange?((0,a.wg)(),(0,a.iD)("span",{key:1,class:"label right",textContent:(0,i.zw)(e.range[1])},null,8,u)):(0,a.kq)("",!0)],2)):(0,a.kq)("",!0),(0,a._)("span",o,[(0,a._)("input",{class:(0,i.C_)(["slider",{"with-label":e.withLabel}]),type:"range",min:e.range[0],max:e.range[1],step:e.step,disabled:e.disabled,value:e.value,ref:"range",onInput:s[0]||(s[0]=(0,n.iM)((s=>t.$emit("input",s)),["stop"])),onChange:s[1]||(s[1]=(0,n.iM)((s=>t.$emit("change",s)),["stop"]))},null,42,c),e.withLabel?((0,a.wg)(),(0,a.iD)("span",{key:0,class:"label",textContent:(0,i.zw)(e.value),ref:"label"},null,8,p)):(0,a.kq)("",!0)])])}var m={emits:["input","change"],props:{value:{type:Number},disabled:{type:Boolean,default:!1},range:{type:Array,default:()=>[0,100]},step:{type:Number,default:1},withLabel:{type:Boolean,default:!1},withRange:{type:Boolean,default:!1}}},g=e(3744);const d=(0,g.Z)(m,[["render",h],["__scopeId","data-v-d90e850c"]]);var k=d},7841:function(t,s,e){e.r(s),e.d(s,{default:function(){return A}});var a=e(6252),i=e(3577);const n=t=>((0,a.dD)("data-v-3f481e2d"),t=t(),(0,a.Cn)(),t),r={key:1,class:"music"},l={key:0,class:"background"},u={class:"foreground"},o={class:"top"},c={class:"track"},p={key:0,class:"unknown"},h={key:1,class:"no-track"},m=["textContent"],g=["textContent"],d={key:0,class:"progress-bar"},k={class:"row"},v={key:1,class:"controls"},y=n((()=>(0,a._)("i",{class:"fa fa-step-backward"},null,-1))),w=[y],f=["title"],b={key:0,class:"fa fa-pause"},_={key:1,class:"fa fa-play"},C=n((()=>(0,a._)("i",{class:"fa fa-stop"},null,-1))),S=[C],x=n((()=>(0,a._)("i",{class:"fa fa-step-forward"},null,-1))),T=[x],q={class:"bottom"},I={key:0,class:"status-property col-4 volume fade-in"},D=n((()=>(0,a._)("i",{class:"fa fa-volume-up"},null,-1))),P={key:1,class:"status-property col-4 volume fade-in"},$={class:"row"},N=n((()=>(0,a._)("i",{class:"fa fa-volume-up"},null,-1))),M={class:"status-property col-2"},E={class:"status-property col-2"},Z={class:"status-property col-2"},R={class:"status-property col-2"};function U(t,s,e,n,y,C){const x=(0,a.up)("Loading"),U=(0,a.up)("ProgressBar"),B=(0,a.up)("Slider");return y.loading?((0,a.wg)(),(0,a.j4)(x,{key:0})):((0,a.wg)(),(0,a.iD)("div",r,[C.image?((0,a.wg)(),(0,a.iD)("div",l,[(0,a._)("div",{class:"image",style:(0,i.j5)({backgroundImage:"url("+C.image+")"})},null,4)])):(0,a.kq)("",!0),(0,a._)("div",u,[(0,a._)("div",o,[(0,a._)("div",{class:(0,i.C_)(["section",{"has-image":!!C.image,"has-progress":"play"===y.status?.state}])},[(0,a._)("div",c,[y.status?(0,a.kq)("",!0):((0,a.wg)(),(0,a.iD)("div",p,"[Unknown state]")),y.status&&"stop"===y.status.state?((0,a.wg)(),(0,a.iD)("div",h,"No media is being played")):(0,a.kq)("",!0),y.status&&"stop"!==y.status.state&&y.track&&y.track.artist?((0,a.wg)(),(0,a.iD)("div",{key:2,class:"artist",textContent:(0,i.zw)(y.track.artist)},null,8,m)):(0,a.kq)("",!0),y.status&&"stop"!==y.status.state&&y.track&&y.track.title?((0,a.wg)(),(0,a.iD)("div",{key:3,class:"title",textContent:(0,i.zw)(y.track.title)},null,8,g)):(0,a.kq)("",!0)]),"play"===y.status?.state?((0,a.wg)(),(0,a.iD)("div",d,[(0,a._)("div",k,[(0,a.Wm)(U,{duration:y.track.time,elapsed:y.status.elapsed,status:y.status,onSeek:C.seek},null,8,["duration","elapsed","status","onSeek"])])])):(0,a.kq)("",!0),C._withControls&&y.status?((0,a.wg)(),(0,a.iD)("div",v,[(0,a._)("button",{title:"Previous",onClick:s[0]||(s[0]=(...t)=>C.prev&&C.prev(...t))},w),(0,a._)("button",{class:"play-pause",onClick:s[1]||(s[1]=(...t)=>C.playPause&&C.playPause(...t)),title:"play"===y.status.state?"Pause":"Play"},["play"===y.status.state?((0,a.wg)(),(0,a.iD)("i",b)):((0,a.wg)(),(0,a.iD)("i",_))],8,f),"stop"!==y.status.state?((0,a.wg)(),(0,a.iD)("button",{key:0,title:"Stop",onClick:s[2]||(s[2]=(...t)=>C.stop&&C.stop(...t))},S)):(0,a.kq)("",!0),(0,a._)("button",{title:"Next",onClick:s[3]||(s[3]=(...t)=>C.next&&C.next(...t))},T)])):(0,a.kq)("",!0)],2)]),(0,a._)("div",q,[y.status?((0,a.wg)(),(0,a.iD)("div",{key:0,class:(0,i.C_)(["playback-status section",{"has-image":!!C.image}])},[y.showVolumeBar?((0,a.wg)(),(0,a.iD)("div",P,[(0,a._)("div",$,[N,(0,a.Uk)("   "),(0,a.Wm)(B,{range:[0,100],value:y.status.volume,onChange:C.setVolume},null,8,["value","onChange"])])])):((0,a.wg)(),(0,a.iD)("div",I,[(0,a._)("button",{title:"Volume",onClick:s[4]||(s[4]=t=>y.showVolumeBar=!0)},[D,(0,a.Uk)("   "+(0,i.zw)(y.status.volume)+"% ",1)])])),(0,a._)("div",M,[(0,a._)("button",{title:"Random",onClick:s[5]||(s[5]=(...t)=>C.random&&C.random(...t))},[(0,a._)("i",{class:(0,i.C_)(["fas fa-random",{active:y.status.random}])},null,2)])]),(0,a._)("div",E,[(0,a._)("button",{title:"Repeat",onClick:s[6]||(s[6]=(...t)=>C.repeat&&C.repeat(...t))},[(0,a._)("i",{class:(0,i.C_)(["fas fa-redo",{active:y.status.repeat}])},null,2)])]),(0,a._)("div",Z,[(0,a._)("button",{title:"Single",onClick:s[7]||(s[7]=(...t)=>C.single&&C.single(...t))},[(0,a._)("i",{class:(0,i.C_)(["fa fa-bullseye",{active:y.status.single}])},null,2)])]),(0,a._)("div",R,[(0,a._)("button",{title:"Consume",onClick:s[8]||(s[8]=(...t)=>C.consume&&C.consume(...t))},[(0,a._)("i",{class:(0,i.C_)(["fa fa-utensils",{active:y.status.consume}])},null,2)])])],2)):(0,a.kq)("",!0)])])]))}var B=e(8637),j=e(6791),V=e(7303),z=e(7191),O=e(8140),F={name:"Music",components:{Loading:j.Z,ProgressBar:z.Z,Slider:O.Z},mixins:[V.Z,B.Z],props:{plugin:{type:String,default:"music.mopidy"},refreshSeconds:{type:Number,default:60},withControls:{type:Boolean,default:!0}},data(){return{track:null,status:{},timer:null,loading:!1,showVolumeBar:!1,images:{},maxImages:100,syncTime:{timestamp:null,elapsed:null}}},computed:{_withControls(){return this.parseBoolean(this.withControls)},_refreshSeconds(){return parseFloat(this.refreshSeconds)},trackUri(){return this.track?.uri||this.track?.file},image(){return"stop"===this.status?.state?null:this.images[this.trackUri]||this.track?.image||this.status?.image}},methods:{async refresh(){this.loading=!0;try{let t=await this.request(`${this.plugin}.status`)||{},s=await this.request(`${this.plugin}.current_track`);this._parseStatus(t),this._parseTrack(s),"play"!==t.state||this.timer?"play"!==t.state&&this.timer&&this.stopTimer():this.startTimer(),"stop"===t.state||this.image||await this.refreshImage()}finally{this.loading=!1}},async refreshImage(){if(this.trackUri){if(!this.images[this.trackUri]){const t=(await this.request(`${this.plugin}.get_images`,{resources:[this.trackUri]}))[this.trackUri];Object.keys(this.images).length>this.maxImages&&delete this.images[Object.keys(this.images)[0]],this.images[this.trackUri]=t}return this.images[this.trackUri]}},async _parseStatus(t){const s=t.pluginName;s&&this.plugin&&s!==this.plugin||(t&&0!==Object.keys(t).length||(t=await this.request(`${this.plugin}.status`)||{}),this.status||(this.status={}),this.status=this.parseStatus(t))},async _parseTrack(t){t&&0!==t.length||(t=await this.request(`${this.plugin}.current_track`)),this.track||(this.track={});for(const[s,e]of Object.entries(t))["id","pos","time","track","disc"].indexOf(s)>=0?this.track[s]=parseInt(e):this.track[s]=e},showNewTrackNotification(){this.notify({html:"<b>"+(this.track.artist||"[No Artist]")+"</b><br>"+(this.track.title||"[No Title]"),image:{icon:"play"}})},async seek(t){await this.request(`${this.plugin}.seek`,{position:t})},async setVolume(t){await this.request(`${this.plugin}.set_volume`,{volume:t.target.value}),this.showVolumeBar=!1},async random(){await this.request(`${this.plugin}.random`)},async repeat(){await this.request(`${this.plugin}.repeat`)},async consume(){await this.request(`${this.plugin}.consume`)},async single(){await this.request(`${this.plugin}.single`)},async onNewPlayingTrack(t){let s=null;this.track&&(s={file:this.track.file,artist:this.track.artist,title:this.track.title}),this.status.state="play",this.status.elapsed=0,this.track={},this._parseTrack(t.track);let e=t.status?t.status:await this.request(`${this.plugin}.status`);this._parseStatus(e),this.startTimer(),s&&this.track.file===s.file&&this.track.artist===s.artist&&this.track.title===s.title||this.showNewTrackNotification(),this.image||await this.refreshImage()},onMusicStop(t){this.status.state="stop",this.status.elapsed=0,this._parseStatus(t.status),this._parseTrack(t.track),this.stopTimer()},async onMusicPlay(t){this.status.state="play",this._parseStatus(t.status),this._parseTrack(t.track),this.startTimer(),this.image||await this.refreshImage()},async onMusicPause(t){this.status.state="pause",this._parseStatus(t.status),this._parseTrack(t.track),this.syncTime.timestamp=new Date,this.syncTime.elapsed=this.status.elapsed,this.image||await this.refreshImage()},onSeekChange(t){null!=t.position&&(this.status.elapsed=parseFloat(t.position)),t.status&&this._parseStatus(t.status),t.track&&this._parseTrack(t.track),this.syncTime.timestamp=new Date,this.syncTime.elapsed=this.status.elapsed},onVolumeChange(t){null!=t.volume&&(this.status.volume=parseFloat(t.volume)),t.status&&this._parseStatus(t.status),t.track&&this._parseTrack(t.track)},onRepeatChange(t){this.status.repeat=t.state},onRandomChange(t){this.status.random=t.state},onConsumeChange(t){this.status.consume=t.state},onSingleChange(t){this.status.single=t.state},startTimer(){null!=this.timer&&this.stopTimer(),this.syncTime.timestamp=new Date,this.syncTime.elapsed=this.status.elapsed,this.timer=setInterval(this.timerFunc,1e3)},stopTimer(){null==this.timer&&(clearInterval(this.timer),this.timer=null)},timerFunc(){"play"===this.status.state&&null!=this.status.elapsed&&(this.status.elapsed=this.syncTime.elapsed+(new Date).getTime()/1e3-this.syncTime.timestamp.getTime()/1e3)},async _run(t,s){s=s||{},await this.request(`music.mpd.${t}`,s),await this.refresh()},async playPause(){return await this._run("pause")},async stop(){return await this._run("stop")},async prev(){return await this._run("previous")},async next(){return await this._run("next")}},mounted(){this.refresh(),this._refreshSeconds&&setInterval(this.refresh,1e3*this._refreshSeconds),this.subscribe(this.onNewPlayingTrack,"widget-music-on-new-track","platypush.message.event.music.NewPlayingTrackEvent"),this.subscribe(this.onMusicStop,"widget-music-on-music-stop","platypush.message.event.music.MusicStopEvent"),this.subscribe(this.onMusicPlay,"widget-music-on-music-play","platypush.message.event.music.MusicPlayEvent"),this.subscribe(this.onMusicPause,"widget-music-on-music-pause","platypush.message.event.music.MusicPauseEvent"),this.subscribe(this.onSeekChange,"widget-music-on-music-seek","platypush.message.event.music.SeekChangeEvent"),this.subscribe(this.onVolumeChange,"widget-music-on-volume-change","platypush.message.event.music.VolumeChangeEvent"),this.subscribe(this.onRepeatChange,"widget-music-on-repeat-change","platypush.message.event.music.PlaybackRepeatModeChangeEvent"),this.subscribe(this.onRandomChange,"widget-music-on-random-change","platypush.message.event.music.PlaybackRandomModeChangeEvent"),this.subscribe(this.onConsumeChange,"widget-music-on-consume-change","platypush.message.event.music.PlaybackConsumeModeChangeEvent"),this.subscribe(this.onSingleChange,"widget-music-on-single-change","platypush.message.event.music.PlaybackSingleModeChangeEvent")}},L=e(3744);const W=(0,L.Z)(F,[["render",U],["__scopeId","data-v-3f481e2d"]]);var A=W},7303:function(t,s,e){e.d(s,{Z:function(){return n}});var a={methods:{parseStatus(t){return Object.entries(t).reduce(((t,[s,e])=>{switch(s){case"bitrate":case"volume":t[s]=parseInt(e);break;case"consume":case"random":case"repeat":case"single":t[s]=!!parseInt(+e);break;case"playing_pos":case"song":t.playingPos=parseInt(e);break;case"time":e.split?(e=e.split(":"),1===e.length?t.elapsed=parseInt(e[0]):(t.elapsed=parseInt(e[0]),t.duration=parseInt(e[1]))):t.elapsed=e;break;case"track":null!=e?.time&&(t.duration=e.time),null!=e?.playlistPos&&(t.playingPos=e.pos);break;case"duration":t.duration=parseInt(e);break;case"elapsed":break;default:t[s]=e;break}return t}),{})}}};const i=a;var n=i}}]);
//# sourceMappingURL=7841.580c6097.js.map