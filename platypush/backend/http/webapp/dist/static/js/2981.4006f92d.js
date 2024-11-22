"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[2981],{2981:function(e,a,t){t.r(a),t.d(a,{default:function(){return T}});var s=t(641),r=t(33);const i={class:"camera"},n={class:"camera-selector"},c={class:"left"},l={key:0,selected:"",disabled:""},o=["value","textContent"],d={class:"right"},u=["disabled"],m={class:"camera-container"},p={class:"frame-container",ref:"frameContainer"},g={key:0,class:"no-frame"},h={class:"frame",ref:"frame",alt:"",src:""},f={class:"controls"},k={class:"left"},C=["disabled"],b=["disabled"],v=["disabled"],y={class:"right"},L=["disabled"],S=["disabled"],_=["disabled"],w={class:"sound-container"},E={key:0,autoplay:"",preload:"none",ref:"player"},X=["src"];function A(e,a,t,A,$,x){const F=(0,s.g2)("Loading");return(0,s.uX)(),(0,s.CE)("div",i,[$.loading?((0,s.uX)(),(0,s.Wv)(F,{key:0})):(0,s.Q3)("",!0),(0,s.Lk)("div",n,[(0,s.Lk)("div",c,[(0,s.Lk)("label",null,[(0,s.Lk)("select",{ref:"cameraSelector",onChange:a[0]||(a[0]=(...e)=>x.onCameraSelected&&x.onCameraSelected(...e))},[Object.keys($.cameras).length?(0,s.Q3)("",!0):((0,s.uX)(),(0,s.CE)("option",l,"-- No cameras available")),((0,s.uX)(!0),(0,s.CE)(s.FK,null,(0,s.pI)(Object.keys($.cameras),(e=>((0,s.uX)(),(0,s.CE)("option",{key:e,value:e,textContent:(0,r.v_)(e)},null,8,o)))),128))],544)])]),(0,s.Lk)("div",d,[(0,s.Lk)("button",{type:"button",onClick:a[1]||(a[1]=(...e)=>x.updateCameraStatus&&x.updateCameraStatus(...e)),disabled:$.loading},a[8]||(a[8]=[(0,s.Lk)("i",{class:"fas fa-sync-alt",title:"Refresh cameras"},null,-1)]),8,u)])]),(0,s.Lk)("div",m,[(0,s.Lk)("div",p,[$.streaming||$.capturing||$.captured?(0,s.Q3)("",!0):((0,s.uX)(),(0,s.CE)("div",g,"The camera is not active")),(0,s.Lk)("img",h,null,512)],512),(0,s.Lk)("div",f,[(0,s.Lk)("div",k,[$.streaming?((0,s.uX)(),(0,s.CE)("button",{key:1,type:"button",onClick:a[3]||(a[3]=(...e)=>x.stopStreaming&&x.stopStreaming(...e)),disabled:$.capturing||$.loading},a[10]||(a[10]=[(0,s.Lk)("i",{class:"fa fa-stop",title:"Stop video"},null,-1)]),8,b)):((0,s.uX)(),(0,s.CE)("button",{key:0,type:"button",onClick:a[2]||(a[2]=(...e)=>x.startStreaming&&x.startStreaming(...e)),disabled:$.capturing||$.loading},a[9]||(a[9]=[(0,s.Lk)("i",{class:"fa fa-play",title:"Start video"},null,-1)]),8,C)),(0,s.Lk)("button",{type:"button",onClick:a[4]||(a[4]=(...e)=>x.capture&&x.capture(...e)),disabled:$.streaming||$.capturing||$.loading},a[11]||(a[11]=[(0,s.Lk)("i",{class:"fas fa-camera",title:"Take a picture"},null,-1)]),8,v)]),(0,s.Lk)("div",y,[(0,s.Lk)("button",{type:"button",onClick:a[5]||(a[5]=(...e)=>x.flipCamera&&x.flipCamera(...e)),disabled:$.loading},a[12]||(a[12]=[(0,s.Lk)("i",{class:"fas fa-retweet",title:"Flip camera"},null,-1)]),8,L),$.recording?((0,s.uX)(),(0,s.CE)("button",{key:1,type:"button",onClick:a[7]||(a[7]=e=>$.recording=!1),disabled:$.loading},a[14]||(a[14]=[(0,s.Lk)("i",{class:"fa fa-volume-up",title:"Stop audio"},null,-1)]),8,_)):((0,s.uX)(),(0,s.CE)("button",{key:0,type:"button",onClick:a[6]||(a[6]=e=>$.recording=!0),disabled:$.loading},a[13]||(a[13]=[(0,s.Lk)("i",{class:"fa fa-volume-mute",title:"Start audio"},null,-1)]),8,S))])])]),(0,s.Lk)("div",w,[$.recording?((0,s.uX)(),(0,s.CE)("audio",E,[(0,s.Lk)("source",{src:$.cameras[$.selectedCamera].audio_url,type:"audio/x-wav;codec=pcm"},null,8,X),a[15]||(a[15]=(0,s.eW)(" Your browser does not support audio elements "))],512)):(0,s.Q3)("",!0)])])}var $=t(2002),x=t(9828),F={name:"CameraAndroidIpcam",components:{Loading:x.A},mixins:[$.A],data(){return{loading:!1,streaming:!1,capturing:!1,recording:!1,captured:!1,cameras:{},selectedCamera:void 0}},computed:{configuredCameras(){const e=this.$root.config["camera.android.ipcam"];let a=e.cameras||[];if(a.length)a=a.reduce(((e,a)=>{const t=a.name||a.host;return e[t]=a,e}),{});else{const t=e.name||e.host;a[t]={name:t,host:e.host,port:e.port,username:e.username,password:e.password,timeout:e.timeout,ssl:e.ssl}}return a}},methods:{startStreaming(){if(this.streaming)return;const e=this.cameras[this.selectedCamera];this.streaming=!0,this.capturing=!1,this.captured=!1,this.$refs.frame.setAttribute("src",e.stream_url)},stopStreaming(){this.streaming&&(this.streaming=!1,this.capturing=!1,this.$refs.frame.removeAttribute("src"))},capture(){if(this.capturing)return;const e=this.cameras[this.selectedCamera];this.streaming=!1,this.capturing=!0,this.captured=!0,this.$refs.frame.setAttribute("src",e.image_url+"?t="+(new Date).getTime())},onFrameLoaded(){this.capturing&&(this.capturing=!1)},onCameraSelected(e){this.selectedCamera=e.target.value},async flipCamera(){const e=this.cameras[this.selectedCamera];this.loading=!0;try{const a=!e.ffc;await this.request("camera.android.ipcam.set_front_facing_camera",{activate:a,camera:e.name}),this.cameras[this.selectedCamera].ffc=a}finally{this.loading=!1}},async updateCameraStatus(){this.loading=!0;try{const e=await this.request("camera.android.ipcam.status");this.cameras=e.reduce(((e,a)=>{for(const t of["stream_url","image_url","audio_url"])a[t].startsWith("https://")&&(a[t]=a[t].replace("https://","http://")),a.name in this.configuredCameras&&this.configuredCameras[a.name].username&&(a[t]="http://"+this.config.cameras[a.name].username+":"+this.config.cameras[a.name].password+"@"+a[t].substr(7));return e[a.name]=a,e}),{}),e.length&&(this.selectedCamera=e[0].name)}finally{this.loading=!1}}},mounted(){this.$refs.frame.addEventListener("load",this.onFrameLoaded),this.updateCameraStatus()}},Q=t(6262);const I=(0,Q.A)(F,[["render",A],["__scopeId","data-v-1334f746"]]);var T=I}}]);
//# sourceMappingURL=2981.4006f92d.js.map