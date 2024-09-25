"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[3924],{3924:function(a,e,t){t.r(e),t.d(e,{default:function(){return M}});var s=t(6252),i=t(3577);const r=a=>((0,s.dD)("data-v-1334f746"),a=a(),(0,s.Cn)(),a),n={class:"camera"},c={class:"camera-selector"},l={class:"left"},o={key:0,selected:"",disabled:""},d=["value","textContent"],u={class:"right"},m=["disabled"],p=r((()=>(0,s._)("i",{class:"fas fa-sync-alt",title:"Refresh cameras"},null,-1))),g=[p],f={class:"camera-container"},h={class:"frame-container",ref:"frameContainer"},b={key:0,class:"no-frame"},C={class:"frame",ref:"frame",alt:"",src:""},_={class:"controls"},y={class:"left"},v=["disabled"],k=r((()=>(0,s._)("i",{class:"fa fa-play",title:"Start video"},null,-1))),w=[k],S=["disabled"],D=r((()=>(0,s._)("i",{class:"fa fa-stop",title:"Stop video"},null,-1))),q=[D],L=["disabled"],$=r((()=>(0,s._)("i",{class:"fas fa-camera",title:"Take a picture"},null,-1))),x=[$],A={class:"right"},j=["disabled"],F=r((()=>(0,s._)("i",{class:"fas fa-retweet",title:"Flip camera"},null,-1))),T=[F],Z=["disabled"],I=r((()=>(0,s._)("i",{class:"fa fa-volume-mute",title:"Start audio"},null,-1))),O=[I],Y=["disabled"],z=r((()=>(0,s._)("i",{class:"fa fa-volume-up",title:"Stop audio"},null,-1))),E=[z],H={class:"sound-container"},K={key:0,autoplay:"",preload:"none",ref:"player"},N=["src"];function R(a,e,t,r,p,k){const D=(0,s.up)("Loading");return(0,s.wg)(),(0,s.iD)("div",n,[p.loading?((0,s.wg)(),(0,s.j4)(D,{key:0})):(0,s.kq)("",!0),(0,s._)("div",c,[(0,s._)("div",l,[(0,s._)("label",null,[(0,s._)("select",{ref:"cameraSelector",onChange:e[0]||(e[0]=(...a)=>k.onCameraSelected&&k.onCameraSelected(...a))},[Object.keys(p.cameras).length?(0,s.kq)("",!0):((0,s.wg)(),(0,s.iD)("option",o,"-- No cameras available")),((0,s.wg)(!0),(0,s.iD)(s.HY,null,(0,s.Ko)(Object.keys(p.cameras),(a=>((0,s.wg)(),(0,s.iD)("option",{key:a,value:a,textContent:(0,i.zw)(a)},null,8,d)))),128))],544)])]),(0,s._)("div",u,[(0,s._)("button",{type:"button",onClick:e[1]||(e[1]=(...a)=>k.updateCameraStatus&&k.updateCameraStatus(...a)),disabled:p.loading},g,8,m)])]),(0,s._)("div",f,[(0,s._)("div",h,[p.streaming||p.capturing||p.captured?(0,s.kq)("",!0):((0,s.wg)(),(0,s.iD)("div",b,"The camera is not active")),(0,s._)("img",C,null,512)],512),(0,s._)("div",_,[(0,s._)("div",y,[p.streaming?((0,s.wg)(),(0,s.iD)("button",{key:1,type:"button",onClick:e[3]||(e[3]=(...a)=>k.stopStreaming&&k.stopStreaming(...a)),disabled:p.capturing||p.loading},q,8,S)):((0,s.wg)(),(0,s.iD)("button",{key:0,type:"button",onClick:e[2]||(e[2]=(...a)=>k.startStreaming&&k.startStreaming(...a)),disabled:p.capturing||p.loading},w,8,v)),(0,s._)("button",{type:"button",onClick:e[4]||(e[4]=(...a)=>k.capture&&k.capture(...a)),disabled:p.streaming||p.capturing||p.loading},x,8,L)]),(0,s._)("div",A,[(0,s._)("button",{type:"button",onClick:e[5]||(e[5]=(...a)=>k.flipCamera&&k.flipCamera(...a)),disabled:p.loading},T,8,j),p.recording?((0,s.wg)(),(0,s.iD)("button",{key:1,type:"button",onClick:e[7]||(e[7]=a=>p.recording=!1),disabled:p.loading},E,8,Y)):((0,s.wg)(),(0,s.iD)("button",{key:0,type:"button",onClick:e[6]||(e[6]=a=>p.recording=!0),disabled:p.loading},O,8,Z))])])]),(0,s._)("div",H,[p.recording?((0,s.wg)(),(0,s.iD)("audio",K,[(0,s._)("source",{src:p.cameras[p.selectedCamera].audio_url,type:"audio/x-wav;codec=pcm"},null,8,N),(0,s.Uk)(" Your browser does not support audio elements ")],512)):(0,s.kq)("",!0)])])}var U=t(8637),W=t(6791),B={name:"CameraAndroidIpcam",components:{Loading:W.Z},mixins:[U.Z],data(){return{loading:!1,streaming:!1,capturing:!1,recording:!1,captured:!1,cameras:{},selectedCamera:void 0}},computed:{configuredCameras(){const a=this.$root.config["camera.android.ipcam"];let e=a.cameras||[];if(e.length)e=e.reduce(((a,e)=>{const t=e.name||e.host;return a[t]=e,a}),{});else{const t=a.name||a.host;e[t]={name:t,host:a.host,port:a.port,username:a.username,password:a.password,timeout:a.timeout,ssl:a.ssl}}return e}},methods:{startStreaming(){if(this.streaming)return;const a=this.cameras[this.selectedCamera];this.streaming=!0,this.capturing=!1,this.captured=!1,this.$refs.frame.setAttribute("src",a.stream_url)},stopStreaming(){this.streaming&&(this.streaming=!1,this.capturing=!1,this.$refs.frame.removeAttribute("src"))},capture(){if(this.capturing)return;const a=this.cameras[this.selectedCamera];this.streaming=!1,this.capturing=!0,this.captured=!0,this.$refs.frame.setAttribute("src",a.image_url+"?t="+(new Date).getTime())},onFrameLoaded(){this.capturing&&(this.capturing=!1)},onCameraSelected(a){this.selectedCamera=a.target.value},async flipCamera(){const a=this.cameras[this.selectedCamera];this.loading=!0;try{const e=!a.ffc;await this.request("camera.android.ipcam.set_front_facing_camera",{activate:e,camera:a.name}),this.cameras[this.selectedCamera].ffc=e}finally{this.loading=!1}},async updateCameraStatus(){this.loading=!0;try{const a=await this.request("camera.android.ipcam.status");this.cameras=a.reduce(((a,e)=>{for(const t of["stream_url","image_url","audio_url"])e[t].startsWith("https://")&&(e[t]=e[t].replace("https://","http://")),e.name in this.configuredCameras&&this.configuredCameras[e.name].username&&(e[t]="http://"+this.config.cameras[e.name].username+":"+this.config.cameras[e.name].password+"@"+e[t].substr(7));return a[e.name]=e,a}),{}),a.length&&(this.selectedCamera=a[0].name)}finally{this.loading=!1}}},mounted(){this.$refs.frame.addEventListener("load",this.onFrameLoaded),this.updateCameraStatus()}},G=t(3744);const J=(0,G.Z)(B,[["render",R],["__scopeId","data-v-1334f746"]]);var M=J}}]);
//# sourceMappingURL=3924.c0d2f3c0.js.map