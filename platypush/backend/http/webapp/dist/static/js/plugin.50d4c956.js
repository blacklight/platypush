(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[9975,5729,7136],{8285:function(e,s,n){"use strict";n.d(s,{Z:function(){return F}});var a=n(6252),t=n(3577);const i=e=>((0,a.dD)("data-v-6878f243"),e=e(),(0,a.Cn)(),e),c=i((()=>(0,a._)("i",{class:"fas fa-bars"},null,-1))),l=["textContent"],o=["title"],r={key:0,class:"plugins"},d={href:"/#"},f=i((()=>(0,a._)("i",{class:"fas fa-home"},null,-1))),p={key:0,class:"name"},u=["title","onClick"],m=["href"],g={class:"icon"},h=["src"],x={key:2,class:"fas fa-puzzle-piece"},k=["textContent"],y={key:1,class:"plugins"},v=["title","onClick"],w=["href"],C={class:"icon"},I=["textContent"],_={key:1,class:"expander"},b=["onClick"],D=i((()=>(0,a._)("i",{class:"fas fa-up-right-from-square"},null,-1))),N=[D],P={class:"footer"},U={href:"/#extensions"},$=i((()=>(0,a._)("span",{class:"icon"},[(0,a._)("i",{class:"fa fa-puzzle-piece"})],-1))),M={key:0,class:"name"},S={href:"/#settings"},q=i((()=>(0,a._)("span",{class:"icon"},[(0,a._)("i",{class:"fa fa-cog"})],-1))),z={key:0,class:"name"},Z={href:"/logout"},T=i((()=>(0,a._)("span",{class:"icon"},[(0,a._)("i",{class:"fas fa-sign-out-alt"})],-1))),L={key:0,class:"name"};function j(e,s,n,i,D,j){const E=(0,a.up)("ExtensionIcon");return(0,a.wg)(),(0,a.iD)("nav",{class:(0,t.C_)({collapsed:D.collapsed})},[(0,a._)("div",{class:"toggler",onClick:s[0]||(s[0]=e=>D.collapsed=!D.collapsed)},[c,n.hostname?((0,a.wg)(),(0,a.iD)("span",{key:0,class:"hostname",textContent:(0,t.zw)(n.hostname)},null,8,l)):(0,a.kq)("",!0),(0,a._)("i",{class:(0,t.C_)(["icon status fas fa-circle",{ok:D.connected,error:!D.connected}]),title:D.connected?"Connected":"Disconnected"},null,10,o)]),"settings"===n.selectedPanel?((0,a.wg)(),(0,a.iD)("ul",r,[(0,a._)("li",{class:"entry",title:"Home",onClick:s[1]||(s[1]=e=>j.onItemClick("entities"))},[(0,a._)("a",d,[f,D.collapsed?(0,a.kq)("",!0):((0,a.wg)(),(0,a.iD)("span",p,"Home"))])]),((0,a.wg)(!0),(0,a.iD)(a.HY,null,(0,a.Ko)(D.configSections,((s,i)=>((0,a.wg)(),(0,a.iD)("li",{key:i,class:(0,t.C_)(["entry",{selected:i===n.selectedConfigPanel}]),title:s.name,onClick:s=>e.$emit("select-config",i)},[(0,a._)("a",{href:`/#settings?page=${i}`},[(0,a._)("span",g,[s.icon?.["class"]?((0,a.wg)(),(0,a.iD)("i",{key:0,class:(0,t.C_)(s.icon["class"])},null,2)):s.icon?.imgUrl?((0,a.wg)(),(0,a.iD)("img",{key:1,src:s.icon?.imgUrl,alt:"name"},null,8,h)):((0,a.wg)(),(0,a.iD)("i",x))]),D.collapsed?(0,a.kq)("",!0):((0,a.wg)(),(0,a.iD)("span",{key:0,class:"name",textContent:(0,t.zw)(s.name)},null,8,k))],8,m)],10,u)))),128))])):((0,a.wg)(),(0,a.iD)("ul",y,[((0,a.wg)(!0),(0,a.iD)(a.HY,null,(0,a.Ko)(j.panelNames,(e=>((0,a.wg)(),(0,a.iD)("li",{key:e,class:(0,t.C_)(["entry",{selected:e===n.selectedPanel}]),title:e,onClick:s=>j.onItemClick(e)},[(0,a._)("a",{href:`/#${e}`},[(0,a._)("span",C,[j.specialPlugins.includes(e)?((0,a.wg)(),(0,a.iD)("i",{key:0,class:(0,t.C_)(D.icons[e].class)},null,2)):((0,a.wg)(),(0,a.j4)(E,{key:1,name:e,size:"1.5em"},null,8,["name"]))]),D.collapsed?(0,a.kq)("",!0):((0,a.wg)(),(0,a.iD)("span",{key:0,class:"name",textContent:(0,t.zw)(j.displayName(e))},null,8,I)),e!==n.selectedPanel||D.collapsed?(0,a.kq)("",!0):((0,a.wg)(),(0,a.iD)("span",_,[(0,a._)("button",{title:"Expanded view",onClick:s=>j.openPluginView(e)},N,8,b)]))],8,w)],10,v)))),128))])),(0,a._)("ul",P,[(0,a._)("li",{class:(0,t.C_)({selected:"extensions"===n.selectedPanel}),title:"Extensions",onClick:s[2]||(s[2]=e=>j.onItemClick("extensions"))},[(0,a._)("a",U,[$,D.collapsed?(0,a.kq)("",!0):((0,a.wg)(),(0,a.iD)("span",M,"Extensions"))])],2),(0,a._)("li",{class:(0,t.C_)({selected:"settings"===n.selectedPanel}),title:"Settings",onClick:s[3]||(s[3]=e=>j.onItemClick("settings"))},[(0,a._)("a",S,[q,D.collapsed?(0,a.kq)("",!0):((0,a.wg)(),(0,a.iD)("span",z,"Settings"))])],2),(0,a._)("li",{title:"Logout",onClick:s[4]||(s[4]=e=>j.onItemClick("logout"))},[(0,a._)("a",Z,[T,D.collapsed?(0,a.kq)("",!0):((0,a.wg)(),(0,a.iD)("span",L,"Logout"))])])])],2)}var E=n(1359),O=n(2126),H=n(8637),W=JSON.parse('{"users":{"name":"Users","icon":{"class":"fas fa-user"}},"tokens":{"name":"Tokens","icon":{"class":"fas fa-key"}},"application":{"name":"Application","icon":{"class":"fas fa-gears"}}}'),A=n(5250),V={name:"Nav",emits:["select","select-config"],mixins:[H.Z],components:{ExtensionIcon:O.Z},props:{panels:{type:Object,required:!0},selectedPanel:{type:String},selectedConfigPanel:{type:String},hostname:{type:String}},computed:{specialPlugins(){return["execute","entities"]},panelNames(){const e=(e,n)=>{const a=s.indexOf(n);return a>=0&&(e=[n].concat(e.slice(0,a).concat(e.slice(a+1)))),e};let s=Object.keys(this.panels).sort();return s=e(s,"execute"),s=e(s,"entities"),s},collapsedDefault(){return!(!this.isMobile()&&!this.isTablet())}},methods:{onItemClick(e){this.$emit("select",e),this.collapsed=!!this.isMobile()||this.collapsedDefault},displayName(e){return"entities"===e?"Home":"execute"===e?"Execute":e},setConnected(e){this.connected=e},openPluginView(e){window.open(`/plugin/${e}`,"_blank")}},data(){return{collapsed:!0,connected:!1,icons:E,host:null,configSections:W}},mounted(){this.collapsed=this.collapsedDefault,A.$.on("connect",(()=>this.setConnected(!0))),A.$.on("disconnect",(()=>this.setConnected(!1))),this.$watch((()=>this.$root.connected),(e=>this.setConnected(e))),this.setConnected(this.$root.connected)}},Y=n(3744);const B=(0,Y.Z)(V,[["render",j],["__scopeId","data-v-6878f243"]]);var F=B},2126:function(e,s,n){"use strict";n.d(s,{Z:function(){return p}});var a=n(6252),t=n(3577);const i=["href"],c=["src","alt","title"],l=["src","alt","title"];function o(e,s,n,o,r,d){return(0,a.wg)(),(0,a.iD)("div",{class:"extension-icon",style:(0,t.j5)({width:`${n.size}`,height:`${n.size}`})},[n.withDocsLink?((0,a.wg)(),(0,a.iD)("a",{key:0,href:d.docsUrl,target:"_blank"},[(0,a._)("img",{src:d.iconUrl,alt:d.extensionName,title:d.extensionName},null,8,c)],8,i)):((0,a.wg)(),(0,a.iD)("img",{key:1,src:d.iconUrl,alt:d.extensionName,title:d.extensionName},null,8,l))],4)}var r={props:{name:{type:String,required:!0},size:{type:String,default:"1.75em"},withDocsLink:{type:Boolean,default:!1}},computed:{iconUrl(){return`https://static.platypush.tech/icons/${this.extensionName}-64.png`},extensionType(){return"backend"==this.name.split(".")[0]?"backend":"plugin"},extensionName(){const e=this.name.split(".");return e.length<1?this.name:("backend"==e[0]&&e.shift(),e.join("."))},docsUrl(){return`https://docs.platypush.tech/platypush/${this.extensionType}s/${this.extensionName}.html`}}},d=n(3744);const f=(0,d.Z)(r,[["render",o],["__scopeId","data-v-0353c248"]]);var p=f},8735:function(e,s,n){"use strict";n.d(s,{Z:function(){return f}});var a=n(6252),t=n(3577);const i={key:0,class:"icon"};function c(e,s,n,c,l,o){const r=(0,a.up)("Icon");return(0,a.wg)(),(0,a.iD)("div",{class:(0,t.C_)(["tab",n.selected?"selected":""]),onClick:s[0]||(s[0]=s=>e.$emit("input"))},[n.iconClass?.length||n.iconUrl?.length?((0,a.wg)(),(0,a.iD)("span",i,[(0,a.Wm)(r,{class:(0,t.C_)(n.iconClass),url:n.iconUrl},null,8,["class","url"])])):(0,a.kq)("",!0),(0,a.Uk)("   "),(0,a.WI)(e.$slots,"default",{},void 0,!0)],2)}var l=n(657),o={name:"Tab",components:{Icon:l.Z},emits:["input"],props:{selected:{type:Boolean,default:!1},iconClass:{type:String},iconUrl:{type:String}}},r=n(3744);const d=(0,r.Z)(o,[["render",c],["__scopeId","data-v-f3217d34"]]);var f=d},3176:function(e,s,n){"use strict";n.d(s,{Z:function(){return r}});var a=n(6252);const t={class:"tabs"};function i(e,s,n,i,c,l){return(0,a.wg)(),(0,a.iD)("div",t,[(0,a.WI)(e.$slots,"default",{},void 0,!0)])}var c={name:"Tabs"},l=n(3744);const o=(0,l.Z)(c,[["render",i],["__scopeId","data-v-f4300bb0"]]);var r=o},2354:function(e,s,n){"use strict";n.r(s),n.d(s,{default:function(){return m}});var a=n(6252);const t={key:1,class:"canvas"};function i(e,s,n,i,c,l){const o=(0,a.up)("Loading");return(0,a.wg)(),(0,a.iD)("main",null,[c.loading?((0,a.wg)(),(0,a.j4)(o,{key:0})):((0,a.wg)(),(0,a.iD)("div",t,[((0,a.wg)(),(0,a.j4)((0,a.LL)(c.component),{config:c.config,"plugin-name":l.pluginName},null,8,["config","plugin-name"]))]))])}var c=n(2262),l=n(8637),o=n(6791),r=n(8285),d=n(293),f={name:"Panel",mixins:[l.Z],components:{Settings:d["default"],Nav:r.Z,Loading:o.Z},data(){return{loading:!1,config:{},plugins:{},backends:{},procedures:{},component:void 0,hostname:void 0,selectedPanel:void 0}},computed:{pluginName(){return this.$route.params.plugin}},methods:{async initPanel(){const e=this.pluginName.split(".").map((e=>e[0].toUpperCase()+e.slice(1))).join("");let s=null;try{s=await n(3379)(`./${e}/Index`)}catch(t){return console.error(t),void this.notify({error:!0,title:`Cannot load plugin ${this.pluginName}`,text:t.toString()})}this.component=(0,c.XI)((0,a.RC)((async()=>s))),this.$options.components[e]=this.component},async initConfig(){const e=await this.request("config.get");this.config=e[this.pluginName]||{},this.hostname=await this.request("config.get_device_id")}},async mounted(){this.loading=!0;try{await this.initConfig(),await this.initPanel()}finally{this.loading=!1}}},p=n(3744);const u=(0,p.Z)(f,[["render",i],["__scopeId","data-v-e339182c"]]);var m=u},3379:function(e,s,n){var a={"./Alarm/Index":[1949,7651,5933,7243,2844,2992,3248,2308,735,6281,8710,1807,9381,9732,1949],"./Camera/Index":[7528,7528],"./CameraAndroidIpcam/Index":[3924,3924],"./CameraCv/Index":[6148,7528,6148],"./CameraFfmpeg/Index":[9334,7528,9334],"./CameraGstreamer/Index":[813,7528,813],"./CameraIrMlx90640/Index":[7381,7528,7381],"./CameraPi/Index":[5214,7528,8895],"./CameraPiLegacy/Index":[1512,7528,1512],"./Entities/Index":[2948,5933,7243,2992,669,864,9732,2948],"./Execute/Index":[4221,5933,3248,735,1807,732],"./Extensions/Index":[2018,5933,3248,735,8710,2924,6217,2018,3862],"./Light/Index":[9751,7651,2844,9751],"./LightHue/Index":[2976,7651,2844,9751,2976],"./Media/Index":[7493,7651,5933,7243,906,1171,2308,7624,182,7493],"./Media/Providers/YouTube/Index":[2200,2200],"./MediaMplayer/Index":[3518,7651,5933,7243,906,1171,2308,7624,182,7493,3518],"./MediaMpv/Index":[4765,7651,5933,7243,906,1171,2308,7624,182,7493,4765],"./MediaOmxplayer/Index":[7819,7651,5933,7243,906,1171,2308,7624,182,7493,7819],"./MediaVlc/Index":[2614,7651,5933,7243,906,1171,2308,7624,182,7493,2614],"./Music/Index":[4015,7651,5933,7243,906,1171,4015],"./MusicMopidy/Index":[3400,7651,5933,7243,906,1171,4015,3400],"./MusicMpd/Index":[3083,7651,5933,7243,906,1171,4015,3083],"./MusicSnapcast/Index":[5285,7651,2844,5285],"./MusicSpotify/Index":[4053,7651,5933,7243,906,1171,4015,4053],"./Rtorrent/Index":[2183,5933,7243,7624,6429,2183],"./Settings/Index":[293,5933,7243,2844,2992,3248,6281,215,2924,293,5729],"./Settings/Tokens/Index":[215,5933,7243,2992,3248,215,7136],"./Sound/Index":[746,746],"./Torrent/Index":[8784,5933,7243,7624,6429,8784],"./Tts/Index":[3732,8069,3732],"./TtsGoogle/Index":[7605,8069,2853],"./TtsPicovoice/Index":[7089,8069,7089],"./TvSamsungWs/Index":[34,34],"./ZigbeeMqtt/Index":[6882,7651,5933,7243,2844,6882],"./Zwave/Index":[2732,7651,5933,7243,2844,2718,2732],"./ZwaveMqtt/Index":[1088,7651,5933,7243,2844,2718,1088]};function t(e){if(!n.o(a,e))return Promise.resolve().then((function(){var s=new Error("Cannot find module '"+e+"'");throw s.code="MODULE_NOT_FOUND",s}));var s=a[e],t=s[0];return Promise.all(s.slice(1).map(n.e)).then((function(){return n(t)}))}t.keys=function(){return Object.keys(a)},t.id=3379,e.exports=t},1359:function(e){"use strict";e.exports=JSON.parse('{"alarm":{"class":"fas fa-stopwatch"},"arduino":{"class":"fas fa-microchip"},"assistant.google":{"class":"fas fa-microphone-lines"},"assistant.openai":{"class":"fas fa-microphone-lines"},"assistant.picovoice":{"class":"fas fa-microphone-lines"},"bluetooth":{"class":"fab fa-bluetooth"},"camera.android.ipcam":{"class":"fab fa-android"},"camera.cv":{"class":"fas fa-camera"},"camera.ffmpeg":{"class":"fas fa-camera"},"camera.gstreamer":{"class":"fas fa-camera"},"camera.ir.mlx90640":{"class":"fas fa-sun"},"camera.pi":{"class":"fas fa-camera"},"camera.pi.legacy":{"class":"fas fa-camera"},"entities":{"class":"fa fa-home"},"execute":{"class":"fa fa-play"},"extensions":{"class":"fas fa-puzzle-piece"},"light.hue":{"class":"fas fa-lightbulb"},"linode":{"class":"fas fa-cloud"},"media.jellyfin":{"imgUrl":"/icons/jellyfin.svg"},"media.kodi":{"imgUrl":"/icons/kodi.svg"},"media.omxplayer":{"class":"fa fa-film"},"media.mplayer":{"class":"fa fa-film"},"media.mpv":{"class":"fa fa-film"},"media.plex":{"imgUrl":"/icons/plex.svg"},"media.vlc":{"class":"fa fa-film"},"music.mpd":{"class":"fas fa-music"},"music.snapcast":{"class":"fa fa-volume-up"},"music.spotify":{"class":"fab fa-spotify"},"ping":{"class":"fas fa-server"},"torrent":{"class":"fa fa-magnet"},"rtorrent":{"class":"fa fa-magnet"},"sensor.bme280":{"class":"fas fa-microchip"},"sensor.dht":{"class":"fas fa-microchip"},"sensor.envirophat":{"class":"fas fa-microchip"},"sensor.ltr559":{"class":"fas fa-microchip"},"sensor.mcp3008":{"class":"fas fa-microchip"},"sensor.pmw3901":{"class":"fas fa-microchip"},"sensor.vl53l1x":{"class":"fas fa-microchip"},"serial":{"class":"fab fa-usb"},"smartthings":{"imgUrl":"/icons/smartthings.png"},"switches":{"class":"fas fa-toggle-on"},"switch.switchbot":{"class":"fas fa-toggle-on"},"switch.tplink":{"class":"fas fa-toggle-on"},"switchbot":{"class":"fas fa-toggle-on"},"sound":{"class":"fa fa-microphone"},"system":{"class":"fas fa-microchip"},"tts":{"class":"far fa-comment"},"tts.google":{"class":"fas fa-comment"},"tv.samsung.ws":{"class":"fas fa-tv"},"variable":{"class":"fas fa-square-root-variable"},"weather.buienradar":{"class":"fas fa-cloud-sun-rain"},"weather.openweathermap":{"class":"fas fa-cloud-sun-rain"},"zigbee.mqtt":{"imgUrl":"/icons/zigbee.svg"},"zwave":{"imgUrl":"/icons/z-wave.png"},"zwave.mqtt":{"imgUrl":"/icons/z-wave.png"}}')}}]);
//# sourceMappingURL=plugin.50d4c956.js.map