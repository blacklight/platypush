(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[8606],{4899:function(e,s,a){"use strict";a.d(s,{A:function(){return W}});var n=a(641),t=a(33);const i=e=>((0,n.Qi)("data-v-edd6404c"),e=e(),(0,n.jt)(),e),c=i((()=>(0,n.Lk)("i",{class:"fas fa-bars"},null,-1))),l=["textContent"],o=["title"],r={key:0,class:"plugins"},d={href:"/#"},f=i((()=>(0,n.Lk)("i",{class:"fas fa-home"},null,-1))),u={key:0,class:"name"},p=["title","onClick"],m=["href"],g={class:"icon"},h=["src"],x={key:2,class:"fas fa-puzzle-piece"},k=["textContent"],C={key:1,class:"plugins"},v=["title","onClick"],y=["href"],I={class:"icon"},w=["textContent"],b={key:1,class:"expander"},L=["onClick"],E=i((()=>(0,n.Lk)("i",{class:"fas fa-up-right-from-square"},null,-1))),M=[E],P={class:"footer"},X={href:"/#extensions"},N=i((()=>(0,n.Lk)("span",{class:"icon"},[(0,n.Lk)("i",{class:"fa fa-puzzle-piece"})],-1))),S={key:0,class:"name"},$={href:"/#settings"},U=i((()=>(0,n.Lk)("span",{class:"icon"},[(0,n.Lk)("i",{class:"fa fa-cog"})],-1))),z={key:0,class:"name"},_={href:"/logout"},A=i((()=>(0,n.Lk)("span",{class:"icon"},[(0,n.Lk)("i",{class:"fas fa-sign-out-alt"})],-1))),T={key:0,class:"name"};function j(e,s,a,i,E,j){const q=(0,n.g2)("ExtensionIcon");return(0,n.uX)(),(0,n.CE)("nav",{class:(0,t.C4)({collapsed:E.collapsed})},[(0,n.Lk)("div",{class:"toggler",onClick:s[0]||(s[0]=e=>E.collapsed=!E.collapsed)},[c,a.hostname?((0,n.uX)(),(0,n.CE)("span",{key:0,class:"hostname",textContent:(0,t.v_)(a.hostname)},null,8,l)):(0,n.Q3)("",!0),(0,n.Lk)("i",{class:(0,t.C4)(["icon status fas fa-circle",{ok:E.connected,error:!E.connected}]),title:E.connected?"Connected":"Disconnected"},null,10,o)]),"settings"===a.selectedPanel?((0,n.uX)(),(0,n.CE)("ul",r,[(0,n.Lk)("li",{class:"entry",title:"Home",onClick:s[1]||(s[1]=e=>j.onItemClick("entities"))},[(0,n.Lk)("a",d,[f,E.collapsed?(0,n.Q3)("",!0):((0,n.uX)(),(0,n.CE)("span",u,"Home"))])]),((0,n.uX)(!0),(0,n.CE)(n.FK,null,(0,n.pI)(E.configSections,((s,i)=>((0,n.uX)(),(0,n.CE)("li",{key:i,class:(0,t.C4)(["entry",{selected:i===a.selectedConfigPanel}]),title:s.name,onClick:s=>e.$emit("select-config",i)},[(0,n.Lk)("a",{href:`/#settings?page=${i}`},[(0,n.Lk)("span",g,[s.icon?.["class"]?((0,n.uX)(),(0,n.CE)("i",{key:0,class:(0,t.C4)(s.icon["class"])},null,2)):s.icon?.imgUrl?((0,n.uX)(),(0,n.CE)("img",{key:1,src:s.icon?.imgUrl,alt:"name"},null,8,h)):((0,n.uX)(),(0,n.CE)("i",x))]),E.collapsed?(0,n.Q3)("",!0):((0,n.uX)(),(0,n.CE)("span",{key:0,class:"name",textContent:(0,t.v_)(s.name)},null,8,k))],8,m)],10,p)))),128))])):((0,n.uX)(),(0,n.CE)("ul",C,[((0,n.uX)(!0),(0,n.CE)(n.FK,null,(0,n.pI)(j.panelNames,(e=>((0,n.uX)(),(0,n.CE)("li",{key:e,class:(0,t.C4)(["entry",{selected:e===a.selectedPanel}]),title:e,onClick:s=>j.onItemClick(e)},[(0,n.Lk)("a",{href:`/#${e}`},[(0,n.Lk)("span",I,[j.specialPlugins.includes(e)?((0,n.uX)(),(0,n.CE)("i",{key:0,class:(0,t.C4)(E.icons[e].class)},null,2)):((0,n.uX)(),(0,n.Wv)(q,{key:1,name:e,size:"1.5em"},null,8,["name"]))]),E.collapsed?(0,n.Q3)("",!0):((0,n.uX)(),(0,n.CE)("span",{key:0,class:"name",textContent:(0,t.v_)(j.displayName(e))},null,8,w)),e!==a.selectedPanel||E.collapsed?(0,n.Q3)("",!0):((0,n.uX)(),(0,n.CE)("span",b,[(0,n.Lk)("button",{title:"Expanded view",onClick:s=>j.openPluginView(e)},M,8,L)]))],8,y)],10,v)))),128))])),(0,n.Lk)("ul",P,[(0,n.Lk)("li",{class:(0,t.C4)({selected:"extensions"===a.selectedPanel}),title:"Extensions",onClick:s[2]||(s[2]=e=>j.onItemClick("extensions"))},[(0,n.Lk)("a",X,[N,E.collapsed?(0,n.Q3)("",!0):((0,n.uX)(),(0,n.CE)("span",S,"Extensions"))])],2),(0,n.Lk)("li",{class:(0,t.C4)({selected:"settings"===a.selectedPanel}),title:"Settings",onClick:s[3]||(s[3]=e=>j.onItemClick("settings"))},[(0,n.Lk)("a",$,[U,E.collapsed?(0,n.Q3)("",!0):((0,n.uX)(),(0,n.CE)("span",z,"Settings"))])],2),(0,n.Lk)("li",{title:"Logout",onClick:s[4]||(s[4]=e=>j.onItemClick("logout"))},[(0,n.Lk)("a",_,[A,E.collapsed?(0,n.Q3)("",!0):((0,n.uX)(),(0,n.CE)("span",T,"Logout"))])])])],2)}var q=a(1921),O=a(2573),Q=a(2002),D=JSON.parse('{"users":{"name":"Users","icon":{"class":"fas fa-user"}},"tokens":{"name":"Tokens","icon":{"class":"fas fa-key"}},"application":{"name":"Application","icon":{"class":"fas fa-gears"}}}'),F=a(2537),J={name:"Nav",emits:["select","select-config"],mixins:[Q.A],components:{ExtensionIcon:O.A},props:{panels:{type:Object,required:!0},selectedPanel:{type:String},selectedConfigPanel:{type:String},hostname:{type:String}},computed:{specialPlugins(){return["execute","entities","file","procedures"]},panelNames(){const e=(e,a)=>{const n=s.indexOf(a);return n>=0&&(e=[a].concat(e.slice(0,n).concat(e.slice(n+1)))),e};let s=Object.keys(this.panels).sort();return s=e(s,"file"),s=e(s,"procedures"),s=e(s,"execute"),s=e(s,"entities"),s},collapsedDefault(){return!(!this.isMobile()&&!this.isTablet())}},methods:{onItemClick(e){this.$emit("select",e),this.collapsed=!!this.isMobile()||this.collapsedDefault},displayName(e){return"entities"===e?"Home":"execute"===e?"Execute":"file"===e?"Files":"procedures"===e?"Procedures":e},setConnected(e){this.connected=e},openPluginView(e){window.open(`/plugin/${e}`,"_blank")}},data(){return{collapsed:!0,connected:!1,icons:q,host:null,configSections:D}},mounted(){this.collapsed=this.collapsedDefault,F.j.on("connect",(()=>this.setConnected(!0))),F.j.on("disconnect",(()=>this.setConnected(!1))),this.$watch((()=>this.$root.connected),(e=>this.setConnected(e))),this.setConnected(this.$root.connected)}},H=a(6262);const V=(0,H.A)(J,[["render",j],["__scopeId","data-v-edd6404c"]]);var W=V},2573:function(e,s,a){"use strict";a.d(s,{A:function(){return u}});var n=a(641),t=a(33);const i=["href"],c=["src","alt","title"],l=["src","alt","title"];function o(e,s,a,o,r,d){return(0,n.uX)(),(0,n.CE)("div",{class:"extension-icon",style:(0,t.Tr)({width:`${a.size}`,height:`${a.size}`})},[a.withDocsLink?((0,n.uX)(),(0,n.CE)("a",{key:0,href:d.docsUrl,target:"_blank"},[(0,n.Lk)("img",{src:d.iconUrl,alt:d.extensionName,title:d.extensionName},null,8,c)],8,i)):((0,n.uX)(),(0,n.CE)("img",{key:1,src:d.iconUrl,alt:d.extensionName,title:d.extensionName},null,8,l))],4)}var r={props:{name:{type:String,required:!0},size:{type:String,default:"1.75em"},withDocsLink:{type:Boolean,default:!1}},computed:{iconUrl(){return`https://static.platypush.tech/icons/${this.extensionName}-64.png`},extensionType(){return"backend"==this.name.split(".")[0]?"backend":"plugin"},extensionName(){const e=this.name.split(".");return e.length<1?this.name:("backend"==e[0]&&e.shift(),e.join("."))},docsUrl(){return`https://docs.platypush.tech/platypush/${this.extensionType}s/${this.extensionName}.html`}}},d=a(6262);const f=(0,d.A)(r,[["render",o],["__scopeId","data-v-0353c248"]]);var u=f},6010:function(e,s,a){"use strict";a.r(s),a.d(s,{default:function(){return m}});var n=a(641);const t={key:1,class:"canvas"};function i(e,s,a,i,c,l){const o=(0,n.g2)("Loading");return(0,n.uX)(),(0,n.CE)("main",null,[c.loading?((0,n.uX)(),(0,n.Wv)(o,{key:0})):((0,n.uX)(),(0,n.CE)("div",t,[((0,n.uX)(),(0,n.Wv)((0,n.$y)(c.component),{config:c.config,"plugin-name":l.pluginName},null,8,["config","plugin-name"]))]))])}var c=a(953),l=a(2002),o=a(9828),r=a(4899),d=a(4050),f={name:"Panel",mixins:[l.A],components:{Settings:d["default"],Nav:r.A,Loading:o.A},data(){return{loading:!1,config:{},plugins:{},backends:{},procedures:{},component:void 0,hostname:void 0,selectedPanel:void 0}},computed:{pluginName(){return this.$route.params.plugin}},methods:{async initPanel(){const e=this.pluginName.split(".").map((e=>e[0].toUpperCase()+e.slice(1))).join("");let s=null;try{s=await a(7672)(`./${e}/Index`)}catch(t){return console.error(t),void this.notify({error:!0,title:`Cannot load plugin ${this.pluginName}`,text:t.toString()})}this.component=(0,c.IJ)((0,n.$V)((async()=>s))),this.$options.components[e]=this.component},async initConfig(){const e=await this.request("config.get");this.config=e[this.pluginName]||{},this.hostname=await this.request("config.get_device_id")}},async mounted(){this.loading=!0;try{await this.initConfig(),await this.initPanel()}finally{this.loading=!1}}},u=a(6262);const p=(0,u.A)(f,[["render",i],["__scopeId","data-v-e339182c"]]);var m=p},7672:function(e,s,a){var n={"./Alarm/Index":[8597,9769,5184,3841,1146,1861,3162,9878,4280,933,2561,2716,648,572,6027,5928,7329,7594,343,3045,6360],"./Camera/Index":[9284,6903],"./CameraAndroidIpcam/Index":[2981,2981],"./CameraCv/Index":[2908,6903,2908],"./CameraFfmpeg/Index":[6973,6903,6973],"./CameraGstreamer/Index":[5783,6903,5783],"./CameraIrMlx90640/Index":[8636,6903,8636],"./CameraPi/Index":[3671,6903,3671],"./CameraPiLegacy/Index":[8357,6903,8357],"./Entities/Index":[1131,3841,1146,1861,5799,2486,343,1131,2256],"./Execute/Index":[8567,1146,9878,2561,5928,1381],"./Extensions/Index":[7908,1146,9878,2561,572,6027,6592,7908,6730],"./File/Index":[2061,1146,1861,3162,9878,933,2716,648,1562],"./Light/Index":[6298,9769,5184,6298],"./LightHue/Index":[9318,9769,5184,6298,9318],"./Media/Index":[4277,5184,1146,1861,3162,9878,4280,933,2716,648,6157,4787,3149,6777,4277],"./Media/Providers/Jellyfin/views/Media/Index":[6975,3841,1146,1861,3162,4280,2353,3149,1433,7619,1616],"./Media/Providers/Jellyfin/views/Movies/Index":[2436,3841,1146,1861,3162,4280,3149,1008,6556,4267],"./Media/Providers/Jellyfin/views/Music/Index":[1433,3841,1146,1861,3162,4280,2353,3149,1433,28],"./Media/Providers/YouTube/Index":[9476,9476],"./MediaChromecast/Index":[1684,5184,1146,1861,3162,9878,4280,933,2716,648,6157,4787,3149,6777,4277,1684],"./MediaGstreamer/Index":[9145,5184,1146,1861,3162,9878,4280,933,2716,648,6157,4787,3149,6777,4277,9145],"./MediaMplayer/Index":[7839,5184,1146,1861,3162,9878,4280,933,2716,648,6157,4787,3149,6777,4277,7839],"./MediaMpv/Index":[9388,5184,1146,1861,3162,9878,4280,933,2716,648,6157,4787,3149,6777,4277,9388],"./MediaVlc/Index":[6372,5184,1146,1861,3162,9878,4280,933,2716,648,6157,4787,3149,6777,4277,6372],"./Music/Index":[4834,5184,1146,1861,6157,4787,4834],"./MusicMopidy/Index":[7533,5184,1146,1861,6157,4787,4834,7533],"./MusicMpd/Index":[560,5184,1146,1861,6157,4787,4834,560],"./MusicSnapcast/Index":[6564,9769,5184,6564],"./MusicSpotify/Index":[7299,5184,1146,1861,6157,4787,4834,7299],"./Procedures/Index":[9636,3841,1146,3162,9878,4280,933,2561,572,6027,5928,7329,6923,343,9636],"./Rtorrent/Index":[8499,1146,1861,6777,9142,8499],"./Settings/Index":[4050,9769,3841,1146,1861,3162,2561,806,6592,4050],"./Settings/Tokens/Index":[806,3841,1146,1861,2561,806],"./Sound/Index":[7158,7158],"./Torrent/Index":[7098,1146,1861,6777,9142,7098],"./Tts/Index":[2392,8946,2392],"./TtsGoogle/Index":[1526,8946,1526],"./TtsPicovoice/Index":[8191,8946,8191],"./TvSamsungWs/Index":[4387,4387],"./ZigbeeMqtt/Index":[7630,9769,5184,1146,1861,7630],"./Zwave/Index":[9313,9769,5184,1146,1861,3290,9313],"./ZwaveMqtt/Index":[5145,9769,5184,1146,1861,3290,5145]};function t(e){if(!a.o(n,e))return Promise.resolve().then((function(){var s=new Error("Cannot find module '"+e+"'");throw s.code="MODULE_NOT_FOUND",s}));var s=n[e],t=s[0];return Promise.all(s.slice(1).map(a.e)).then((function(){return a(t)}))}t.keys=function(){return Object.keys(n)},t.id=7672,e.exports=t},1921:function(e){"use strict";e.exports=JSON.parse('{"alarm":{"class":"fas fa-stopwatch"},"arduino":{"class":"fas fa-microchip"},"assistant.google":{"class":"fas fa-microphone-lines"},"assistant.openai":{"class":"fas fa-microphone-lines"},"assistant.picovoice":{"class":"fas fa-microphone-lines"},"bluetooth":{"class":"fab fa-bluetooth"},"camera.android.ipcam":{"class":"fab fa-android"},"camera.cv":{"class":"fas fa-camera"},"camera.ffmpeg":{"class":"fas fa-camera"},"camera.gstreamer":{"class":"fas fa-camera"},"camera.ir.mlx90640":{"class":"fas fa-sun"},"camera.pi":{"class":"fas fa-camera"},"camera.pi.legacy":{"class":"fas fa-camera"},"entities":{"class":"fa fa-home"},"execute":{"class":"fa fa-play"},"file":{"class":"fas fa-folder"},"extensions":{"class":"fas fa-puzzle-piece"},"light.hue":{"class":"fas fa-lightbulb"},"linode":{"class":"fas fa-cloud"},"media.chromecast":{"class":"fab fa-chromecast"},"media.jellyfin":{"imgUrl":"/icons/jellyfin.svg"},"media.kodi":{"imgUrl":"/icons/kodi.svg"},"media.mplayer":{"class":"fa fa-film"},"media.mpv":{"class":"fa fa-film"},"media.plex":{"imgUrl":"/icons/plex.svg"},"media.vlc":{"class":"fa fa-film"},"music.mpd":{"class":"fas fa-music"},"music.snapcast":{"class":"fa fa-volume-up"},"music.spotify":{"class":"fab fa-spotify"},"ping":{"class":"fas fa-server"},"procedures":{"class":"fas fa-gears"},"torrent":{"class":"fa fa-magnet"},"rtorrent":{"class":"fa fa-magnet"},"sensor.bme280":{"class":"fas fa-microchip"},"sensor.dht":{"class":"fas fa-microchip"},"sensor.envirophat":{"class":"fas fa-microchip"},"sensor.ltr559":{"class":"fas fa-microchip"},"sensor.mcp3008":{"class":"fas fa-microchip"},"sensor.pmw3901":{"class":"fas fa-microchip"},"sensor.vl53l1x":{"class":"fas fa-microchip"},"serial":{"class":"fab fa-usb"},"smartthings":{"imgUrl":"/icons/smartthings.png"},"switches":{"class":"fas fa-toggle-on"},"switch.switchbot":{"class":"fas fa-toggle-on"},"switch.tplink":{"class":"fas fa-toggle-on"},"switchbot":{"class":"fas fa-toggle-on"},"sound":{"class":"fa fa-microphone"},"system":{"class":"fas fa-microchip"},"tts":{"class":"far fa-comment"},"tts.google":{"class":"fas fa-comment"},"tv.samsung.ws":{"class":"fas fa-tv"},"variable":{"class":"fas fa-square-root-variable"},"weather.buienradar":{"class":"fas fa-cloud-sun-rain"},"weather.openweathermap":{"class":"fas fa-cloud-sun-rain"},"zigbee.mqtt":{"imgUrl":"/icons/zigbee.svg"},"zwave":{"imgUrl":"/icons/z-wave.png"},"zwave.mqtt":{"imgUrl":"/icons/z-wave.png"}}')}}]);
//# sourceMappingURL=plugin.a571e03f.js.map