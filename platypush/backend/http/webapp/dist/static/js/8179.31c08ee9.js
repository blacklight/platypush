(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[8179],{8179:function(e,n,t){"use strict";t.r(n),t.d(n,{default:function(){return x}});var i=t(6252);const o={class:"plugin"};function a(e,n,t,a,d,r){const s=(0,i.up)("Loading");return(0,i.wg)(),(0,i.iD)("div",o,[d.loading?((0,i.wg)(),(0,i.j4)(s,{key:0})):d.component?((0,i.wg)(),(0,i.j4)((0,i.LL)(d.component),{key:1,config:d.config},null,8,["config"])):(0,i.kq)("",!0)])}var d=t(8637),r=t(6791),s=t(2262),c={name:"Plugin",components:{Loading:r.Z},mixins:[d.Z],props:{pluginName:{type:String,required:!0}},data(){return{loading:!1,component:null,config:{}}},computed:{componentName(){return this.pluginName.split(".").map((e=>e[0].toUpperCase()+e.slice(1))).join("")}},methods:{refresh:async function(){this.loading=!0;try{this.component=(0,s.XI)((0,i.RC)((()=>t(3379)(`./${this.componentName}/Index`)))),this.$options.components[this.componentName]=this.component,this.config=(await this.request("config.get_plugins"))?.[this.pluginName]||{}}finally{this.loading=!1}}},mounted:function(){this.refresh()}},u=t(3744);const p=(0,u.Z)(c,[["render",a],["__scopeId","data-v-69b17daa"]]);var x=p},3379:function(e,n,t){var i={"./Alarm/Index":[1949,7651,5933,9549,2844,6016,2992,735,6281,58,1807,9381,8224,1949],"./Camera/Index":[7528,7528],"./CameraAndroidIpcam/Index":[3924,3924],"./CameraCv/Index":[6148,7528,6148],"./CameraFfmpeg/Index":[9334,7528,9334],"./CameraGstreamer/Index":[813,7528,813],"./CameraIrMlx90640/Index":[7381,7528,7381],"./CameraPi/Index":[5214,7528,8895],"./CameraPiLegacy/Index":[1512,7528,1512],"./Entities/Index":[7878,5933,9549,2992,669,2154,8224,7878],"./Execute/Index":[4221,5933,735,1807,5197],"./Extensions/Index":[2018,5933,735,58,2924,6217,2018,3862],"./Light/Index":[9751,7651,2844,9751],"./LightHue/Index":[2976,7651,2844,9751,2976],"./Media/Index":[3033,7651,5933,9549,906,2582,6016,2577,182,3033],"./Media/Providers/YouTube/Index":[2200,2200],"./MediaMplayer/Index":[3518,7651,5933,9549,906,2582,6016,2577,182,3033,3518],"./MediaMpv/Index":[4765,7651,5933,9549,906,2582,6016,2577,182,3033,4765],"./MediaOmxplayer/Index":[7819,7651,5933,9549,906,2582,6016,2577,182,3033,7819],"./MediaVlc/Index":[2614,7651,5933,9549,906,2582,6016,2577,182,3033,2614],"./Music/Index":[288,7651,5933,9549,906,2582,288],"./MusicMopidy/Index":[3400,7651,5933,9549,906,2582,288,3400],"./MusicMpd/Index":[3083,7651,5933,9549,906,2582,288,3083],"./MusicSnapcast/Index":[5285,7651,2844,5285],"./MusicSpotify/Index":[4053,7651,5933,9549,906,2582,288,4053],"./Rtorrent/Index":[2183,5933,9549,2577,6429,2183],"./Settings/Index":[4084,5933,9549,6281,2924,4084],"./Sound/Index":[746,746],"./Torrent/Index":[8784,5933,9549,2577,6429,8784],"./Tts/Index":[3732,8069,3732],"./TtsGoogle/Index":[7605,8069,2853],"./TtsPicovoice/Index":[7089,8069,7089],"./TvSamsungWs/Index":[34,34],"./ZigbeeMqtt/Index":[1259,7651,5933,9549,2844,1259],"./Zwave/Index":[2732,7651,5933,9549,2844,7880,2732],"./ZwaveMqtt/Index":[1088,7651,5933,9549,2844,7880,1088]};function o(e){if(!t.o(i,e))return Promise.resolve().then((function(){var n=new Error("Cannot find module '"+e+"'");throw n.code="MODULE_NOT_FOUND",n}));var n=i[e],o=n[0];return Promise.all(n.slice(1).map(t.e)).then((function(){return t(o)}))}o.keys=function(){return Object.keys(i)},o.id=3379,e.exports=o}}]);
//# sourceMappingURL=8179.31c08ee9.js.map