"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[5465],{9021:function(t,a,n){n.r(a),n.d(a,{default:function(){return ft}});var e=n(6252),r=n(9963),i={class:"camera"},s={class:"camera-container"},o={class:"frame-container",ref:"frameContainer"},l={key:0,class:"no-frame"},u=["src"],c={class:"controls"},p={class:"left"},h=["disabled"],d=(0,e._)("i",{class:"fa fa-play"},null,-1),f=[d],m=["disabled"],g=(0,e._)("i",{class:"fa fa-stop"},null,-1),_=[g],y=["disabled"],C=(0,e._)("i",{class:"fas fa-camera"},null,-1),v=[C],w={class:"right"},b=(0,e._)("i",{class:"fas fa-volume-mute"},null,-1),S=[b],k=(0,e._)("i",{class:"fas fa-volume-up"},null,-1),x=[k],z=(0,e._)("i",{class:"fas fa-cog"},null,-1),F=[z],U={class:"audio-container"},D={key:0,autoplay:"",preload:"none",ref:"player"},M=["src"],V=(0,e.Uk)(" Your browser does not support audio elements "),$={key:0,class:"url"},q={class:"row"},P=(0,e._)("span",{class:"name"},"Stream URL",-1),A=["value"],L={class:"params"},O={class:"row"},R=(0,e._)("span",{class:"name"},"Device",-1),Z={class:"row"},j=(0,e._)("span",{class:"name"},"Width",-1),G={class:"row"},I=(0,e._)("span",{class:"name"},"Height",-1),T={class:"row"},W=(0,e._)("span",{class:"name"},"Horizontal Flip",-1),H={class:"row"},Y=(0,e._)("span",{class:"name"},"Vertical Flip",-1),E={class:"row"},X=(0,e._)("span",{class:"name"},"Rotate",-1),B={class:"row"},J=(0,e._)("span",{class:"name"},"Scale-X",-1),K={class:"row"},N=(0,e._)("span",{class:"name"},"Scale-Y",-1),Q={class:"row"},tt=(0,e._)("span",{class:"name"},"Frames per second",-1),at={class:"row"},nt=(0,e._)("span",{class:"name"},"Grayscale",-1);function et(t,a,n,d,g,C){var b,k=(0,e.up)("Slot"),z=(0,e.up)("Modal");return(0,e.wg)(),(0,e.iD)("div",i,[(0,e._)("div",s,[(0,e._)("div",o,[t.streaming||t.capturing||t.captured?(0,e.kq)("",!0):((0,e.wg)(),(0,e.iD)("div",l,"The camera is not active")),(0,e._)("img",{class:"frame",src:t.url,ref:"frame",alt:""},null,8,u)],512),(0,e._)("div",c,[(0,e._)("div",p,[t.streaming?((0,e.wg)(),(0,e.iD)("button",{key:1,type:"button",onClick:a[1]||(a[1]=function(){return t.stopStreaming&&t.stopStreaming.apply(t,arguments)}),disabled:t.capturing,title:"Stop video"},_,8,m)):((0,e.wg)(),(0,e.iD)("button",{key:0,type:"button",onClick:a[0]||(a[0]=function(){return C.startStreaming&&C.startStreaming.apply(C,arguments)}),disabled:t.capturing,title:"Start video"},f,8,h)),t.streaming?(0,e.kq)("",!0):((0,e.wg)(),(0,e.iD)("button",{key:2,type:"button",onClick:a[2]||(a[2]=function(){return C.capture&&C.capture.apply(C,arguments)}),disabled:t.streaming||t.capturing,title:"Take a picture"},v,8,y))]),(0,e._)("div",w,[t.audioOn?((0,e.wg)(),(0,e.iD)("button",{key:1,type:"button",onClick:a[4]||(a[4]=function(){return t.stopAudio&&t.stopAudio.apply(t,arguments)}),title:"Stop audio"},x)):((0,e.wg)(),(0,e.iD)("button",{key:0,type:"button",onClick:a[3]||(a[3]=function(){return t.startAudio&&t.startAudio.apply(t,arguments)}),title:"Start audio"},S)),(0,e._)("button",{type:"button",onClick:a[5]||(a[5]=function(a){return t.$refs.paramsModal.show()}),title:"Settings"},F)])])]),(0,e._)("div",U,[t.audioOn?((0,e.wg)(),(0,e.iD)("audio",D,[(0,e._)("source",{src:"/sound/stream.aac?t=".concat((new Date).getTime())},null,8,M),V],512)):(0,e.kq)("",!0)]),null!==(b=t.url)&&void 0!==b&&b.length?((0,e.wg)(),(0,e.iD)("div",$,[(0,e._)("label",q,[P,(0,e._)("input",{name:"url",type:"text",value:C.fullURL,disabled:"disabled"},null,8,A)])])):(0,e.kq)("",!0),(0,e.Wm)(z,{ref:"paramsModal",title:"Camera Parameters"},{default:(0,e.w5)((function(){return[(0,e._)("div",L,[(0,e._)("label",O,[R,(0,e.wy)((0,e._)("input",{name:"device",type:"text","onUpdate:modelValue":a[6]||(a[6]=function(a){return t.attrs.device=a}),onChange:a[7]||(a[7]=function(){return t.onDeviceChanged&&t.onDeviceChanged.apply(t,arguments)})},null,544),[[r.nr,t.attrs.device]])]),(0,e._)("label",Z,[j,(0,e.wy)((0,e._)("input",{name:"width",type:"text","onUpdate:modelValue":a[8]||(a[8]=function(a){return t.attrs.resolution[0]=a}),onChange:a[9]||(a[9]=function(){return t.onSizeChanged&&t.onSizeChanged.apply(t,arguments)})},null,544),[[r.nr,t.attrs.resolution[0]]])]),(0,e._)("label",G,[I,(0,e.wy)((0,e._)("input",{name:"height",type:"text","onUpdate:modelValue":a[10]||(a[10]=function(a){return t.attrs.resolution[1]=a}),onChange:a[11]||(a[11]=function(){return t.onSizeChanged&&t.onSizeChanged.apply(t,arguments)})},null,544),[[r.nr,t.attrs.resolution[1]]])]),(0,e._)("label",T,[W,(0,e.wy)((0,e._)("input",{name:"horizontal_flip",type:"checkbox","onUpdate:modelValue":a[12]||(a[12]=function(a){return t.attrs.horizontal_flip=a}),onChange:a[13]||(a[13]=function(){return t.onFlipChanged&&t.onFlipChanged.apply(t,arguments)})},null,544),[[r.e8,t.attrs.horizontal_flip]])]),(0,e._)("label",H,[Y,(0,e.wy)((0,e._)("input",{name:"vertical_flip",type:"checkbox","onUpdate:modelValue":a[14]||(a[14]=function(a){return t.attrs.vertical_flip=a}),onChange:a[15]||(a[15]=function(){return t.onFlipChanged&&t.onFlipChanged.apply(t,arguments)})},null,544),[[r.e8,t.attrs.vertical_flip]])]),(0,e._)("label",E,[X,(0,e.wy)((0,e._)("input",{name:"rotate",type:"text","onUpdate:modelValue":a[16]||(a[16]=function(a){return t.attrs.rotate=a}),onChange:a[17]||(a[17]=function(){return t.onSizeChanged&&t.onSizeChanged.apply(t,arguments)})},null,544),[[r.nr,t.attrs.rotate]])]),(0,e._)("label",B,[J,(0,e.wy)((0,e._)("input",{name:"scale_x",type:"text","onUpdate:modelValue":a[18]||(a[18]=function(a){return t.attrs.scale_x=a}),onChange:a[19]||(a[19]=function(){return t.onSizeChanged&&t.onSizeChanged.apply(t,arguments)})},null,544),[[r.nr,t.attrs.scale_x]])]),(0,e._)("label",K,[N,(0,e.wy)((0,e._)("input",{name:"scale_y",type:"text","onUpdate:modelValue":a[20]||(a[20]=function(a){return t.attrs.scale_y=a}),onChange:a[21]||(a[21]=function(){return t.onSizeChanged&&t.onSizeChanged.apply(t,arguments)})},null,544),[[r.nr,t.attrs.scale_y]])]),(0,e._)("label",Q,[tt,(0,e.wy)((0,e._)("input",{name:"fps",type:"text","onUpdate:modelValue":a[22]||(a[22]=function(a){return t.attrs.fps=a}),onChange:a[23]||(a[23]=function(){return t.onFpsChanged&&t.onFpsChanged.apply(t,arguments)})},null,544),[[r.nr,t.attrs.fps]])]),(0,e._)("label",at,[nt,(0,e.wy)((0,e._)("input",{name:"grayscale",type:"checkbox","onUpdate:modelValue":a[24]||(a[24]=function(a){return t.attrs.grayscale=a}),onChange:a[25]||(a[25]=function(){return t.onGrayscaleChanged&&t.onGrayscaleChanged.apply(t,arguments)})},null,544),[[r.e8,t.attrs.grayscale]])]),(0,e.Wm)(k)])]})),_:1},512)])}n(2222);var rt=n(8534),it=n(6084),st=(n(5666),n(9600),n(1249),n(7327),n(1539),n(9720),n(6813)),ot={name:"CameraMixin",mixins:[st.Z],props:{cameraPlugin:{type:String,required:!0}},data:function(){return{streaming:!1,capturing:!1,captured:!1,audioOn:!1,url:null,attrs:{}}},computed:{params:function(){var t;return{resolution:this.attrs.resolution,device:null!==(t=this.attrs.device)&&void 0!==t&&t.length?this.attrs.device:null,horizontal_flip:parseInt(0+this.attrs.horizontal_flip),vertical_flip:parseInt(0+this.attrs.vertical_flip),rotate:parseFloat(this.attrs.rotate),scale_x:parseFloat(this.attrs.scale_x),scale_y:parseFloat(this.attrs.scale_y),fps:parseFloat(this.attrs.fps),grayscale:parseInt(0+this.attrs.grayscale)}}},methods:{getUrl:function(t,a){return"/camera/"+t+"/"+a+"?"+Object.entries(this.params).filter((function(t){return null!=t[1]&&(""+t[1]).length>0})).map((function(t){var a=(0,it.Z)(t,2),n=a[0],e=a[1];return n+"="+e})).join("&")},_startStreaming:function(t){this.streaming||(this.streaming=!0,this.capturing=!1,this.captured=!1,this.url=this.getUrl(t,"video."+this.attrs.stream_format))},stopStreaming:function(){this.streaming&&(this.streaming=!1,this.capturing=!1,this.url=null)},_capture:function(t){this.capturing||(this.streaming=!1,this.capturing=!0,this.captured=!0,this.url=this.getUrl(t,"photo.jpg")+"&t="+(new Date).getTime())},onFrameLoaded:function(){this.capturing&&(this.capturing=!1)},onDeviceChanged:function(){},onFlipChanged:function(){},onSizeChanged:function(){var t=function(t){return t*Math.PI/180},a=t(this.params.rotate);this.$refs.frameContainer.style.width=Math.round(this.params.scale_x*Math.abs(this.params.resolution[0]*Math.cos(a)+this.params.resolution[1]*Math.sin(a)))+"px",this.$refs.frameContainer.style.height=Math.round(this.params.scale_y*Math.abs(this.params.resolution[0]*Math.sin(a)+this.params.resolution[1]*Math.cos(a)))+"px"},onFpsChanged:function(){},onGrayscaleChanged:function(){},startAudio:function(){this.audioOn=!0},stopAudio:function(){var t=this;return(0,rt.Z)(regeneratorRuntime.mark((function a(){return regeneratorRuntime.wrap((function(a){while(1)switch(a.prev=a.next){case 0:return t.audioOn=!1,a.next=3,t.request("sound.stop_recording");case 3:case"end":return a.stop()}}),a)})))()}},created:function(){var t=this.$root.config["camera.".concat(this.cameraPlugin)]||{};this.attrs={resolution:t.resolution||[640,480],device:t.device,horizontal_flip:t.horizontal_flip||0,vertical_flip:t.vertical_flip||0,rotate:t.rotate||0,scale_x:t.scale_x||1,scale_y:t.scale_y||1,fps:t.fps||16,grayscale:t.grayscale||0,stream_format:t.stream_format||"mjpeg"}},mounted:function(){var t=this;this.$refs.frame.addEventListener("load",this.onFrameLoaded),this.onSizeChanged(),this.$watch((function(){return t.attrs.resolution}),this.onSizeChanged),this.$watch((function(){return t.attrs.horizontal_flip}),this.onSizeChanged),this.$watch((function(){return t.attrs.vertical_flip}),this.onSizeChanged),this.$watch((function(){return t.attrs.rotate}),this.onSizeChanged),this.$watch((function(){return t.attrs.scale_x}),this.onSizeChanged),this.$watch((function(){return t.attrs.scale_y}),this.onSizeChanged)}};const lt=ot;var ut=lt,ct=n(1794),pt={name:"Camera",components:{Modal:ct.Z},mixins:[ut],props:{cameraPlugin:{type:String,required:!0}},computed:{fullURL:function(){return"".concat(window.location.protocol,"//").concat(window.location.host).concat(this.url)}},methods:{startStreaming:function(){this._startStreaming(this.cameraPlugin)},capture:function(){this._capture(this.cameraPlugin)}}},ht=n(3744);const dt=(0,ht.Z)(pt,[["render",et]]);var ft=dt}}]);
//# sourceMappingURL=5465-legacy.f819fef2.js.map