"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[6903],{9284:function(t,e,a){a.r(e),a.d(e,{default:function(){return mt}});var s=a(641),n=a(33),i=a(3751);const r={class:"camera",ref:"cameraRoot"},l={class:"frame-canvas",ref:"frameCanvas"},o={key:0,class:"no-frame"},c=["src"],u={class:"controls"},h={class:"left"},p=["disabled"],d=(0,s.Lk)("i",{class:"fa fa-play"},null,-1),m=[d],g=["disabled"],f=(0,s.Lk)("i",{class:"fa fa-stop"},null,-1),C=[f],k=["disabled"],b=(0,s.Lk)("i",{class:"fas fa-camera"},null,-1),y=[b],L={class:"right"},v=(0,s.Lk)("i",{class:"fas fa-volume-mute"},null,-1),_=[v],S=(0,s.Lk)("i",{class:"fas fa-volume-up"},null,-1),z=[S],w=(0,s.Lk)("i",{class:"fas fa-cog"},null,-1),x=[w],$=["title"],F={key:0,class:"fas fa-expand"},E={key:1,class:"fas fa-compress"},M={class:"audio-container"},U={key:0,autoplay:"",preload:"none",ref:"player"},V=["src"],X={key:0,class:"url"},O={class:"row"},R=(0,s.Lk)("span",{class:"name"},"Stream URL",-1),A=["value"],H={class:"params"},J={class:"row"},D=(0,s.Lk)("span",{class:"name"},"Device",-1),P={class:"row"},T=(0,s.Lk)("span",{class:"name"},"Width",-1),G={class:"row"},Q=(0,s.Lk)("span",{class:"name"},"Height",-1),j={class:"row"},I=(0,s.Lk)("span",{class:"name"},"Horizontal Flip",-1),W={class:"row"},q=(0,s.Lk)("span",{class:"name"},"Vertical Flip",-1),Y={class:"row"},B=(0,s.Lk)("span",{class:"name"},"Rotate",-1),K={class:"row"},N=(0,s.Lk)("span",{class:"name"},"Scale-X",-1),Z={class:"row"},tt=(0,s.Lk)("span",{class:"name"},"Scale-Y",-1),et={class:"row"},at=(0,s.Lk)("span",{class:"name"},"Frames per second",-1),st={class:"row"},nt=(0,s.Lk)("span",{class:"name"},"Grayscale",-1);function it(t,e,a,d,f,b){const v=(0,s.g2)("Modal");return(0,s.uX)(),(0,s.CE)("div",r,[(0,s.Lk)("div",{class:(0,n.C4)(["camera-container",{fullscreen:t.fullscreen_}]),ref:"cameraContainer"},[(0,s.Lk)("div",l,[(0,s.Lk)("div",{class:(0,n.C4)(["frame-container",{vertical:t.isCameraVertical,horizontal:!t.isCameraVertical}]),style:(0,n.Tr)({aspectRatio:t.aspectRatio}),ref:"frameContainer"},[t.streaming||t.capturing||t.captured?(0,s.Q3)("",!0):((0,s.uX)(),(0,s.CE)("div",o,"The camera is not active")),(0,s.Lk)("img",{class:"frame",src:t.url,ref:"frame",alt:""},null,8,c)],6)],512),(0,s.Lk)("div",u,[(0,s.Lk)("div",h,[t.streaming?((0,s.uX)(),(0,s.CE)("button",{key:1,type:"button",onClick:e[1]||(e[1]=(...e)=>t.stopStreaming&&t.stopStreaming(...e)),disabled:t.capturing,title:"Stop video"},C,8,g)):((0,s.uX)(),(0,s.CE)("button",{key:0,type:"button",onClick:e[0]||(e[0]=(...t)=>b.startStreaming&&b.startStreaming(...t)),disabled:t.capturing,title:"Start video"},m,8,p)),t.streaming?(0,s.Q3)("",!0):((0,s.uX)(),(0,s.CE)("button",{key:2,type:"button",onClick:e[2]||(e[2]=(...t)=>b.capture&&b.capture(...t)),disabled:t.streaming||t.capturing,title:"Take a picture"},y,8,k))]),(0,s.Lk)("div",L,[t.audioOn?((0,s.uX)(),(0,s.CE)("button",{key:1,type:"button",onClick:e[4]||(e[4]=(...e)=>t.stopAudio&&t.stopAudio(...e)),title:"Stop audio"},z)):((0,s.uX)(),(0,s.CE)("button",{key:0,type:"button",onClick:e[3]||(e[3]=(...e)=>t.startAudio&&t.startAudio(...e)),title:"Start audio"},_)),(0,s.Lk)("button",{type:"button",onClick:e[5]||(e[5]=e=>t.$refs.paramsModal.show()),title:"Settings"},x),t.fullscreen?(0,s.Q3)("",!0):((0,s.uX)(),(0,s.CE)("button",{key:2,type:"button",title:t.fullscreen_?"Exit fullscreen":"Fullscreen",onClick:e[6]||(e[6]=e=>t.fullscreen_=!t.fullscreen_)},[t.fullscreen_?((0,s.uX)(),(0,s.CE)("i",E)):((0,s.uX)(),(0,s.CE)("i",F))],8,$))])])],2),(0,s.Lk)("div",M,[t.audioOn?((0,s.uX)(),(0,s.CE)("audio",U,[(0,s.Lk)("source",{src:`/sound/stream.aac?t=${(new Date).getTime()}`},null,8,V),(0,s.eW)(" Your browser does not support audio elements ")],512)):(0,s.Q3)("",!0)]),t.url?.length?((0,s.uX)(),(0,s.CE)("div",X,[(0,s.Lk)("label",O,[R,(0,s.Lk)("input",{name:"url",type:"text",value:b.fullURL,disabled:"disabled"},null,8,A)])])):(0,s.Q3)("",!0),(0,s.bF)(v,{ref:"paramsModal",title:"Camera Parameters"},{default:(0,s.k6)((()=>[(0,s.Lk)("div",H,[(0,s.Lk)("label",J,[D,(0,s.bo)((0,s.Lk)("input",{name:"device",type:"text","onUpdate:modelValue":e[7]||(e[7]=e=>t.attrs.device=e),onChange:e[8]||(e[8]=(...e)=>t.onDeviceChanged&&t.onDeviceChanged(...e))},null,544),[[i.Jo,t.attrs.device]])]),(0,s.Lk)("label",P,[T,(0,s.bo)((0,s.Lk)("input",{name:"width",type:"text","onUpdate:modelValue":e[9]||(e[9]=e=>t.attrs.resolution[0]=e),onChange:e[10]||(e[10]=(...e)=>t.onSizeChanged&&t.onSizeChanged(...e))},null,544),[[i.Jo,t.attrs.resolution[0]]])]),(0,s.Lk)("label",G,[Q,(0,s.bo)((0,s.Lk)("input",{name:"height",type:"text","onUpdate:modelValue":e[11]||(e[11]=e=>t.attrs.resolution[1]=e),onChange:e[12]||(e[12]=(...e)=>t.onSizeChanged&&t.onSizeChanged(...e))},null,544),[[i.Jo,t.attrs.resolution[1]]])]),(0,s.Lk)("label",j,[I,(0,s.bo)((0,s.Lk)("input",{name:"horizontal_flip",type:"checkbox","onUpdate:modelValue":e[13]||(e[13]=e=>t.attrs.horizontal_flip=e),onChange:e[14]||(e[14]=(...e)=>t.onFlipChanged&&t.onFlipChanged(...e))},null,544),[[i.lH,t.attrs.horizontal_flip]])]),(0,s.Lk)("label",W,[q,(0,s.bo)((0,s.Lk)("input",{name:"vertical_flip",type:"checkbox","onUpdate:modelValue":e[15]||(e[15]=e=>t.attrs.vertical_flip=e),onChange:e[16]||(e[16]=(...e)=>t.onFlipChanged&&t.onFlipChanged(...e))},null,544),[[i.lH,t.attrs.vertical_flip]])]),(0,s.Lk)("label",Y,[B,(0,s.bo)((0,s.Lk)("input",{name:"rotate",type:"text","onUpdate:modelValue":e[17]||(e[17]=e=>t.attrs.rotate=e),onChange:e[18]||(e[18]=(...e)=>t.onSizeChanged&&t.onSizeChanged(...e))},null,544),[[i.Jo,t.attrs.rotate]])]),(0,s.Lk)("label",K,[N,(0,s.bo)((0,s.Lk)("input",{name:"scale_x",type:"text","onUpdate:modelValue":e[19]||(e[19]=e=>t.attrs.scale_x=e),onChange:e[20]||(e[20]=(...e)=>t.onSizeChanged&&t.onSizeChanged(...e))},null,544),[[i.Jo,t.attrs.scale_x]])]),(0,s.Lk)("label",Z,[tt,(0,s.bo)((0,s.Lk)("input",{name:"scale_y",type:"text","onUpdate:modelValue":e[21]||(e[21]=e=>t.attrs.scale_y=e),onChange:e[22]||(e[22]=(...e)=>t.onSizeChanged&&t.onSizeChanged(...e))},null,544),[[i.Jo,t.attrs.scale_y]])]),(0,s.Lk)("label",et,[at,(0,s.bo)((0,s.Lk)("input",{name:"fps",type:"text","onUpdate:modelValue":e[23]||(e[23]=e=>t.attrs.fps=e),onChange:e[24]||(e[24]=(...e)=>t.onFpsChanged&&t.onFpsChanged(...e))},null,544),[[i.Jo,t.attrs.fps]])]),(0,s.Lk)("label",st,[nt,(0,s.bo)((0,s.Lk)("input",{name:"grayscale",type:"checkbox","onUpdate:modelValue":e[25]||(e[25]=e=>t.attrs.grayscale=e),onChange:e[26]||(e[26]=(...e)=>t.onGrayscaleChanged&&t.onGrayscaleChanged(...e))},null,544),[[i.lH,t.attrs.grayscale]])]),(0,s.RG)(t.$slots,"default")])])),_:3},512)],512)}var rt=a(2002),lt={name:"CameraMixin",mixins:[rt.A],props:{fullscreen:{type:Boolean,default:!1},cameraPlugin:{type:String,required:!0}},data(){return{streaming:!1,capturing:!1,captured:!1,fullscreen_:!1,audioOn:!1,url:null,attrs:{},resizeObserver:null}},computed:{params(){return{resolution:this.attrs.resolution,device:this.attrs.device?.length?this.attrs.device:null,horizontal_flip:parseInt(0+this.attrs.horizontal_flip),vertical_flip:parseInt(0+this.attrs.vertical_flip),rotate:parseFloat(this.attrs.rotate),scale_x:parseFloat(this.attrs.scale_x),scale_y:parseFloat(this.attrs.scale_y),fps:parseFloat(this.attrs.fps),grayscale:parseInt(0+this.attrs.grayscale)}},aspectRatio(){return this.attrs?.resolution?`${this.attrs.resolution[0]}/${this.attrs.resolution[1]}`:1},isCameraVertical(){return!!this.attrs?.resolution&&this.attrs.resolution[1]>this.attrs.resolution[0]}},methods:{getUrl(t,e){return"/camera/"+t+"/"+e+"?"+Object.entries(this.params).filter((t=>null!=t[1]&&(""+t[1]).length>0)).map((([t,e])=>t+"="+e)).join("&")},_startStreaming(t){this.streaming||(this.streaming=!0,this.capturing=!1,this.captured=!1,this.url=this.getUrl(t,"video."+this.attrs.stream_format))},stopStreaming(){this.streaming&&(this.streaming=!1,this.capturing=!1,this.url=null)},_capture(t){this.capturing||(this.streaming=!1,this.capturing=!0,this.captured=!0,this.url=this.getUrl(t,"photo.jpg")+"&t="+(new Date).getTime())},onFrameLoaded(){this.capturing&&(this.capturing=!1)},onDeviceChanged(){},onFlipChanged(){this.onSizeChanged()},onSizeChanged(){const t=t=>t*Math.PI/180,e=t(this.params.rotate),a=this.$refs.frameContainer.parentElement.offsetWidth,s=this.$refs.frameContainer.parentElement.offsetHeight,n=this.$refs.cameraRoot?.offsetWidth||a,i=this.$refs.cameraRoot?.offsetHeight||s;let r="100%",l="100%";this.fullscreen_?this.params.resolution[0]>this.params.resolution[1]?(r="100%",l=s*(this.params.resolution[1]/this.params.resolution[0])+"px"):(l="100%",r=a*(this.params.resolution[0]/this.params.resolution[1])+"px"):(r=Math.min(n,Math.round(this.params.scale_x*Math.abs(this.params.resolution[0]*Math.cos(e)+this.params.resolution[1]*Math.sin(e))))+"px",l=Math.min(i,Math.round(this.params.scale_y*Math.abs(this.params.resolution[0]*Math.sin(e)+this.params.resolution[1]*Math.cos(e))))+"px"),this.$refs.frameContainer.style.width=r,this.$refs.frameContainer.style.height=l},onFpsChanged(){},onGrayscaleChanged(){},startAudio(){this.audioOn=!0},async stopAudio(){this.audioOn=!1,await this.request("sound.stop_recording")}},created(){const t=this.$root.config[`camera.${this.cameraPlugin}`]||{};this.attrs={resolution:t.resolution||[640,480],device:t.device,horizontal_flip:t.horizontal_flip||0,vertical_flip:t.vertical_flip||0,rotate:t.rotate||0,scale_x:t.scale_x||1,scale_y:t.scale_y||1,fps:t.fps||16,grayscale:t.grayscale||0,stream_format:t.stream_format||"mjpeg"}},mounted(){this.fullscreen_=this.fullscreen,this.$refs.frame.addEventListener("load",this.onFrameLoaded),this.onSizeChanged(),this.$watch((()=>this.attrs.resolution),this.onSizeChanged),this.$watch((()=>this.attrs.horizontal_flip),this.onSizeChanged),this.$watch((()=>this.attrs.vertical_flip),this.onSizeChanged),this.$watch((()=>this.attrs.rotate),this.onSizeChanged),this.$watch((()=>this.attrs.scale_x),this.onSizeChanged),this.$watch((()=>this.attrs.scale_y),this.onSizeChanged),screen.orientation.addEventListener("change",this.onSizeChanged);const t=()=>{this.onSizeChanged()};t(),this.$nextTick((()=>{this.resizeObserver=new ResizeObserver(t),this.resizeObserver.observe(document.body),this.resizeObserver.observe(this.$refs?.frameContainer?.parentElement)}))},unmouted(){this.resizeObserver?.disconnect()}};const ot=lt;var ct=ot,ut=a(9513),ht={name:"Camera",components:{Modal:ut.A},mixins:[ct],computed:{fullURL(){return`${window.location.protocol}//${window.location.host}${this.url}`}},methods:{startStreaming(){this._startStreaming(this.cameraPlugin)},capture(){this._capture(this.cameraPlugin)}}},pt=a(6262);const dt=(0,pt.A)(ht,[["render",it]]);var mt=dt}}]);
//# sourceMappingURL=6903.34f985a6.js.map