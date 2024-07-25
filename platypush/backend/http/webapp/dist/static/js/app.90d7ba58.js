(function(){"use strict";var e={5250:function(e,t,n){n.d(t,{$:function(){return s}});var i=n(9652);const s=(0,i.Z)();s.publishEntity=e=>{s.emit("entity-update",e)},s.onEntity=e=>{s.on("entity-update",e)},s.publishNotification=e=>{s.emit("notification-create",e)},s.onNotification=e=>{s.on("notification-create",e)}},5621:function(e,t,n){var i=n(9963),s=n(6252),o=n(3577);const a={key:0,id:"error"},r=(0,s._)("h1",null,"Initialization error",-1),c={key:2,id:"app-container"};function l(e,t,n,i,l,d){const u=(0,s.up)("Loading"),h=(0,s.up)("Events"),f=(0,s.up)("Notifications"),p=(0,s.up)("VoiceAssistant"),m=(0,s.up)("Pushbullet"),b=(0,s.up)("Ntfy"),g=(0,s.up)("ConfirmDialog"),v=(0,s.up)("DropdownContainer"),y=(0,s.up)("router-view");return l.initError?((0,s.wg)(),(0,s.iD)("div",a,[r,(0,s._)("p",null,(0,o.zw)(l.initError),1)])):l.initialized?((0,s.wg)(),(0,s.iD)("div",c,[d.hasWebsocket?((0,s.wg)(),(0,s.j4)(h,{key:0,ref:"events"},null,512)):(0,s.kq)("",!0),(0,s.Wm)(f,{ref:"notifications"},null,512),d.hasAssistant?((0,s.wg)(),(0,s.j4)(p,{key:1,ref:"voice-assistant"},null,512)):(0,s.kq)("",!0),d.hasPushbullet?((0,s.wg)(),(0,s.j4)(m,{key:2,ref:"pushbullet"},null,512)):(0,s.kq)("",!0),d.hasNtfy?((0,s.wg)(),(0,s.j4)(b,{key:3,ref:"ntfy"},null,512)):(0,s.kq)("",!0),(0,s.Wm)(g,{ref:"pwaDialog",onInput:d.installPWA},{default:(0,s.w5)((()=>[(0,s.Uk)(" Would you like to install this application locally? ")])),_:1},8,["onInput"]),(0,s.Wm)(v),(0,s.Wm)(y)])):((0,s.wg)(),(0,s.j4)(u,{key:1}))}var d=n(7833);const u={class:"dropdown-container"};function h(e,t,n,i,o,a){return(0,s.wg)(),(0,s.iD)("div",u)}var f=n(5250),p={methods:{onOpen(e){e?.$el&&(e.keepOpenOnItemClick||this.onClose(),this.$el.appendChild(e.$el))},onClose(){this.$el.innerHTML=""}},mounted(){f.$.on("dropdown-open",this.onOpen),f.$.on("dropdown-close",this.onClose)}},m=n(3744);const b=(0,m.Z)(p,[["render",h],["__scopeId","data-v-c190f656"]]);var g=b,v=n(6791);const y={class:"notifications"};function w(e,t,n,i,o,a){const r=(0,s.up)("Notification");return(0,s.wg)(),(0,s.iD)("div",y,[((0,s.wg)(!0),(0,s.iD)(s.HY,null,(0,s.Ko)(e.notifications,((e,t,n)=>((0,s.wg)(),(0,s.j4)(r,{key:n,id:t,text:e.text,html:e.html,title:e.title,link:e.link,image:e.image,warning:e.warning,error:e.error,onClicked:a.destroy},null,8,["id","text","html","title","link","image","warning","error","onClicked"])))),128))])}const k=["textContent"],C={class:"body"},x={key:0,class:"image col-3"},$={class:"row"},D=["src"],T={key:3,class:"fa fa-exclamation"},_={key:4,class:"fa fa-times"},E=["textContent"],M=["innerHTML"],j=["textContent"],N=["innerHTML"];function O(e,t,n,i,a,r){return(0,s.wg)(),(0,s.iD)("div",{class:(0,o.C_)(["notification fade-in",{warning:n.warning,error:n.error}]),onClick:t[0]||(t[0]=(...e)=>r.clicked&&r.clicked(...e))},[n.title?((0,s.wg)(),(0,s.iD)("div",{key:0,class:"title",textContent:(0,o.zw)(n.title)},null,8,k)):(0,s.kq)("",!0),(0,s._)("div",C,[n.image||n.warning||n.error?((0,s.wg)(),(0,s.iD)("div",x,[(0,s._)("div",$,[n.image&&n.image.src?((0,s.wg)(),(0,s.iD)("img",{key:0,src:n.image.src,alt:""},null,8,D)):n.image&&n.image.icon?((0,s.wg)(),(0,s.iD)("i",{key:1,class:(0,o.C_)(["fa","fa-"+n.image.icon]),style:(0,o.j5)(n.image.color?"--color: "+n.image.color:"")},null,6)):n.image&&n.image.iconClass?((0,s.wg)(),(0,s.iD)("i",{key:2,class:(0,o.C_)(n.image.iconClass),style:(0,o.j5)(n.image.color?"--color: "+n.image.color:"")},null,6)):n.warning?((0,s.wg)(),(0,s.iD)("i",T)):n.error?((0,s.wg)(),(0,s.iD)("i",_)):(0,s.kq)("",!0)])])):(0,s.kq)("",!0),n.text&&n.image?((0,s.wg)(),(0,s.iD)("div",{key:1,class:"text col-9",textContent:(0,o.zw)(n.text)},null,8,E)):(0,s.kq)("",!0),n.html&&n.image?((0,s.wg)(),(0,s.iD)("div",{key:2,class:"text col-9",innerHTML:n.html},null,8,M)):(0,s.kq)("",!0),n.text&&!n.image?((0,s.wg)(),(0,s.iD)("div",{key:3,class:"text row horizontal-center",textContent:(0,o.zw)(n.text)},null,8,j)):(0,s.kq)("",!0),n.html&&!n.image?((0,s.wg)(),(0,s.iD)("div",{key:4,class:"text row horizontal-center",innerHTML:n.html},null,8,N)):(0,s.kq)("",!0)])],2)}var S={name:"Notification",props:["id","text","html","title","image","link","error","warning"],methods:{clicked(){this.link&&window.open(this.link,"_blank"),this.$emit("clicked",this.id)}}};const I=(0,m.Z)(S,[["render",O],["__scopeId","data-v-7646705e"]]);var z=I,A={name:"Notifications",components:{Notification:z},props:{duration:{type:Number,default:1e4}},data:function(){return{index:0,notifications:{},timeouts:{}}},methods:{create:function(e){const t=this.index++;this.notifications[t]=e,null==e.duration&&(e.duration=this.duration);const n=e.duration?parseInt(e.duration):0;n&&(this.timeouts[t]=setTimeout(this.destroy.bind(null,t),n))},destroy:function(e){delete this.notifications[e],delete this.timeouts[e]}}};const P=(0,m.Z)(A,[["render",w],["__scopeId","data-v-6dc8bebc"]]);var Z=P,q=n(8637);function V(e,t,n,i,o,a){return(0,s.wg)(),(0,s.iD)("div")}n(560);var W={name:"Events",data(){return{ws:null,initialized:!1,pending:!1,opened:!1,timeout:null,reconnectMsecs:1e3,minReconnectMsecs:1e3,maxReconnectMsecs:3e4,handlers:{},handlerNameToEventTypes:{}}},methods:{onWebsocketTimeout(){console.log("Websocket reconnection timed out, retrying"),this.reconnectMsecs=Math.min(2*this.reconnectMsecs,this.maxReconnectMsecs),this.pending=!1,this.ws&&this.ws.close(),this.onClose()},onMessage(e){const t=[];if(e=e.data,"string"===typeof e)try{e=JSON.parse(e)}catch(n){console.warn("Received invalid non-JSON event"),console.warn(e)}if(console.debug(e),"event"===e.type){null in this.handlers&&t.push(this.handlers[null]),e.args.type in this.handlers&&t.push(...Object.values(this.handlers[e.args.type]));for(let n of t)n&&(n instanceof Array?n=n[0]:n instanceof Object&&!(n instanceof Function)&&(n=Object.values(n)[0]),n(e.args))}},onOpen(){this.opened&&(console.log("There's already an opened websocket connection, closing the newly opened one"),this.ws&&(this.ws.onclose=()=>{},this.ws.close())),console.log("Websocket connection successful"),this.opened=!0,this.reconnectMsecs=this.minReconnectMsecs,this.pending&&(this.pending=!1),this.timeout&&(clearTimeout(this.timeout),this.timeout=void 0)},onError(e){console.error("Websocket error"),console.error(e)},onClose(e){e&&console.log(`Websocket closed - code: ${e.code} - reason: ${e.reason}. Retrying in ${this.reconnectMsecs/1e3}s`),this.opened=!1,this.pending||(this.pending=!0,this.init())},init(){try{const e="https:"===location.protocol?"wss":"ws",t=`${e}://${location.host}/ws/events`;this.ws=new WebSocket(t)}catch(e){return console.error("Websocket initialization error"),void console.error(e)}this.pending=!0,this.timeout=setTimeout(this.onWebsocketTimeout,this.reconnectMsecs),this.ws.onmessage=this.onMessage,this.ws.onopen=this.onOpen,this.ws.onerror=this.onError,this.ws.onclose=this.onClose,this.initialized=!0},subscribe(e){const t=e.handler,n=e.events.length?e.events:[null],i=e.handlerName;for(const s of n)s in this.handlers||(this.handlers[s]={}),i in this.handlerNameToEventTypes||(this.handlerNameToEventTypes[i]=n),this.handlers[s][i]=t;return()=>{this.unsubscribe(i)}},unsubscribe(e){const t=this.handlerNameToEventTypes[e];if(t){for(const n of t)this.handlers[n]?.[e]&&(delete this.handlers[n][e],Object.keys(this.handlers[n]).length||delete this.handlers[n]);delete this.handlerNameToEventTypes[e]}}},created(){f.$.on("subscribe",this.subscribe),f.$.on("unsubscribe",this.unsubscribe),this.$watch("opened",(e=>{f.$.emit(e?"connect":"disconnect")})),this.init()}};const R=(0,m.Z)(W,[["render",V]]);var U=R;const L={class:"assistant-modal"},F={class:"icon"},B={key:0,class:"fa fa-bell"},H={key:1,class:"fa fa-volume-up"},K={key:2,class:"fa fa-comment-dots"},J={key:3,class:"fa fa-microphone"},Y={class:"text"},G={key:0,class:"listening"},Q=(0,s._)("span",null,"Assistant listening",-1),X=[Q],ee={key:1,class:"speech-recognized"},te=["textContent"],ne={key:2,class:"responding"},ie=["textContent"];function se(e,t,n,i,a,r){const c=(0,s.up)("Modal");return(0,s.wg)(),(0,s.iD)("div",L,[(0,s.Wm)(c,{ref:"assistantModal"},{default:(0,s.w5)((()=>[(0,s._)("div",F,[a.state.alerting?((0,s.wg)(),(0,s.iD)("i",B)):a.state.responding?((0,s.wg)(),(0,s.iD)("i",H)):a.state.speechRecognized?((0,s.wg)(),(0,s.iD)("i",K)):((0,s.wg)(),(0,s.iD)("i",J))]),(0,s._)("div",Y,[a.state.listening?((0,s.wg)(),(0,s.iD)("div",G,X)):a.state.speechRecognized?((0,s.wg)(),(0,s.iD)("div",ee,[(0,s._)("span",{textContent:(0,o.zw)(a.phrase)},null,8,te)])):a.state.responding?((0,s.wg)(),(0,s.iD)("div",ne,[(0,s._)("span",{textContent:(0,o.zw)(a.responseText)},null,8,ie)])):(0,s.kq)("",!0)])])),_:1},512)])}var oe=n(5166),ae={name:"VoiceAssistant",components:{Modal:oe.Z},mixins:[q.Z],data(){return{responseText:"",phrase:"",hideTimeout:void 0,state:{listening:!1,speechRecognized:!1,responding:!1,alerting:!1}}},methods:{reset(){this.state.listening=!1,this.state.speechRecognized=!1,this.state.responding=!1,this.state.alerting=!1,this.phrase="",this.responseText=""},conversationStart(){this.reset(),this.state.listening=!0,this.$refs.assistantModal.show(),this.hideTimeout&&(clearTimeout(this.hideTimeout),this.hideTimeout=void 0)},conversationEnd(){const e=this;this.hideTimeout=setTimeout((()=>{this.reset(),e.$refs.assistantModal.close(),e.hideTimeout=void 0}),4e3)},speechRecognized(e){this.reset(),this.state.speechRecognized=!0,this.phrase=e.phrase,this.$refs.assistantModal.show()},response(e){this.reset(),this.state.responding=!0,this.responseText=e.response_text,this.$refs.assistantModal.show()},alertOn(){this.reset(),this.state.alerting=!0,this.$refs.assistantModal.show()},alertOff(){this.reset(),this.state.alerting=!1,this.$refs.assistantModal.close()},registerHandlers(){this.subscribe(this.conversationStart,null,"platypush.message.event.assistant.ConversationStartEvent"),this.subscribe(this.alertOn,null,"platypush.message.event.assistant.AlertStartedEvent"),this.subscribe(this.alertOff,null,"platypush.message.event.assistant.AlertEndEvent"),this.subscribe(this.speechRecognized,null,"platypush.message.event.assistant.SpeechRecognizedEvent"),this.subscribe(this.response,null,"platypush.message.event.assistant.ResponseEvent"),this.subscribe(this.conversationEnd,null,"platypush.message.event.assistant.ConversationEndEvent","platypush.message.event.assistant.ResponseEndEvent","platypush.message.event.assistant.NoResponseEvent","platypush.message.event.assistant.ConversationTimeoutEvent")}},mounted(){this.registerHandlers()}};const re=(0,m.Z)(ae,[["render",se]]);var ce=re;function le(e,t,n,i,o,a){return(0,s.wg)(),(0,s.iD)("div")}var de={name:"Ntfy",mixins:[q.Z],methods:{onMessage(e){this.notify({title:e.title,text:e.message,image:{icon:"bell"}})}},mounted(){this.subscribe(this.onMessage,null,"platypush.message.event.ntfy.NotificationEvent")}};const ue=(0,m.Z)(de,[["render",le]]);var he=ue;function fe(e,t,n,i,o,a){return(0,s.wg)(),(0,s.iD)("div")}var pe={mixins:[q.Z],methods:{onMessage(e){this.notify({title:e.title,text:e.body,image:{src:e.icon?"data:image/png;base64, "+e.icon:void 0,icon:e.icon?void 0:"bell"}})}},mounted(){this.subscribe(this.onMessage,null,"platypush.message.event.pushbullet.PushbulletNotificationEvent")}};const me=(0,m.Z)(pe,[["render",fe]]);var be=me,ge={mixins:[q.Z],components:{ConfirmDialog:d.Z,DropdownContainer:g,Events:U,Loading:v.Z,Notifications:Z,Ntfy:he,Pushbullet:be,VoiceAssistant:ce},data(){return{config:{},userAuthenticated:!1,connected:!1,pwaInstallEvent:null,initialized:!1,initError:null}},computed:{hasWebsocket(){return this.userAuthenticated&&"backend.http"in this.config},hasAssistant(){return this.hasWebsocket},hasPushbullet(){return this.hasWebsocket&&("pushbullet"in this.config||"backend.pushbullet"in this.config)},hasNtfy(){return this.hasWebsocket&&"ntfy"in this.config}},methods:{onNotification(e){this.$refs.notifications.create(e)},async initConfig(){this.config=await this.request("config.get",{},6e4,!1),this.userAuthenticated=!0},installPWA(){this.pwaInstallEvent&&this.pwaInstallEvent.prompt(),this.$refs.pwaDialog.close()}},async created(){try{await this.initConfig()}catch(e){const t=e?.response?.data?.code;[401,403,412].includes(t)||(this.initError=e,console.error("Initialization error",e))}finally{this.initialized=!0}},beforeMount(){this.getCookie("pwa-dialog-shown")?.length||window.addEventListener("beforeinstallprompt",(e=>{e.preventDefault(),this.pwaInstallEvent=e,this.$refs.pwaDialog.show(),this.setCookie("pwa-dialog-shown","1",{expires:new Date((new Date).getTime()+31536e6)})}))},mounted(){f.$.onNotification(this.onNotification),f.$.on("connect",(()=>this.connected=!0)),f.$.on("disconnect",(()=>this.connected=!1))}};const ve=(0,m.Z)(ge,[["render",l]]);var ye=ve,we=n(2201);const ke=[{path:"/",name:"Panel",component:()=>Promise.all([n.e(5933),n.e(7243),n.e(2844),n.e(735),n.e(6281),n.e(58),n.e(2924),n.e(8010),n.e(6217),n.e(2018),n.e(3393),n.e(7401)]).then(n.bind(n,8665))},{path:"/dashboard/:name",name:"Dashboard",component:()=>n.e(9966).then(n.bind(n,8332))},{path:"/plugin/:plugin",name:"Plugin",component:()=>Promise.all([n.e(5933),n.e(7243),n.e(2844),n.e(6281),n.e(2924),n.e(8010),n.e(6217),n.e(3393),n.e(9975)]).then(n.bind(n,2354))},{path:"/login",name:"Login",component:()=>Promise.all([n.e(9122),n.e(4535)]).then(n.bind(n,8137))},{path:"/register",name:"Register",component:()=>Promise.all([n.e(9122),n.e(685)]).then(n.bind(n,9780))},{path:"/:catchAll(.*)",component:()=>n.e(2245).then(n.bind(n,2751))}],Ce=(0,we.p7)({history:(0,we.PO)(),routes:ke});var xe=Ce,$e=n(5205);(0,$e.z)("/service-worker.js",{ready(){console.log("App is being served from cache by a service worker.\nFor more details, visit https://goo.gl/AFskqB")},registered(){console.log("Service worker has been registered.")},cached(){console.log("Content has been cached for offline use.")},updatefound(){console.log("New content is downloading.")},updated(){console.log("New content is available; please refresh.")},offline(){console.log("No internet connection found. App is running in offline mode.")},error(e){console.error("Error during service worker registration:",e)}});const De=(0,i.ri)(ye);De.config.globalProperties._config=window.config,De.use(xe).mount("#app")},8637:function(e,t,n){n.d(t,{Z:function(){return V}});var i=n(7066),s={name:"Api",methods:{execute(e,t=6e4,n=!0){const s={};return"target"in e&&e["target"]||(e["target"]="localhost"),"type"in e&&e["type"]||(e["type"]="request"),t&&(s.timeout=t),new Promise(((t,o)=>{i.Z.post("/execute",e,s).then((e=>{if(e=e.data.response,e.errors?.length){const t=e.errors?.[0]||e;n&&this.notify({text:t,error:!0}),o(t)}else t(e.output)})).catch((e=>{412!==e?.response?.data?.code||"/register"===window.location.pathname?401!==e?.response?.data?.code||"/login"===window.location.pathname?(console.log(e),n&&this.notify({text:e,error:!0}),o(e)):window.location.href="/login?redirect="+window.location.href.split("/").slice(3).join("/"):window.location.href="/register?redirect="+window.location.href.split("/").slice(3).join("/")}))}))},request(e,t={},n=6e4,i=!0){return this.execute({type:"request",action:e,args:t},n,i)},timeout(e){return new Promise((t=>setTimeout(t,e)))}}};const o=s;var a=o,r={name:"Clipboard",methods:{async copyToClipboard(e){await navigator.clipboard.writeText(e),this.notify({text:"Copied to the clipboard",image:{icon:"clipboard"}})}}};const c=r;var l=c,d={name:"Cookies",methods:{getCookies(){return document.cookie.split(/;\s*/).reduce(((e,t)=>{const[n,i]=t.split("=");return e[n]=i,e}),{})},getCookie(e){return this.getCookies()[e]},setCookie(e,t,n){document.cookie=`${e}=${t}; path=${n?.path||"/"}`+(n?.expires?`; expires=${n?.expires.toISOString()}`:"")},deleteCookie(e){document.cookie=`${e}=; expires=1970-01-01T00:00:00Z`}}};const u=d;var h=u,f={name:"DateTime",methods:{formatDate(e,t=!1){return"number"===typeof e?e=new Date(1e3*e):"string"===typeof e&&(e=new Date(Date.parse(e))),e.toDateString().substring(0,t?15:10)},formatTime(e,t=!0){return"number"===typeof e&&(e=new Date(1e3*e)),"string"===typeof e&&(e=new Date(Date.parse(e))),e.toTimeString().substring(0,t?8:5)},formatDateTime(e,t=!1,n=!0,i=!1){return"number"===typeof e&&(e=new Date(1e3*e)),"string"===typeof e&&(e=new Date(Date.parse(e))),i&&0===e.getHours()&&0===e.getMinutes()&&0===e.getSeconds()?this.formatDate(e,t):`${this.formatDate(e,t)}, ${this.formatTime(e,n)}`}}};const p=f;var m=p,b=(n(3429),n(5250)),g={name:"Events",computed:{_eventsReady(){return this.$root.$refs.events?.initialized}},methods:{subscribe(e,t,...n){const i=()=>{b.$.emit("subscribe",{events:n,handler:e,handlerName:t||this.generateId()})};if(this._eventsReady)return void i();const s=this,o=this.$watch((()=>s._eventsReady),(e=>{e&&(i(),o())}));return o},unsubscribe(e){b.$.emit("unsubscribe",e)},generateId(){return btoa([...Array(11).keys()].map((()=>String.fromCharCode(Math.round(255*Math.random())))))}}};const v=g;var y=v,w={name:"Extensions",methods:{pluginDisplayName(e){const t=e.split(".");return t.forEach(((e,n)=>{t[n]=e.charAt(0).toUpperCase()+e.slice(1)})),t.length>1&&(t[0]=`[${t[0]}]`),t.join(" ")}}};const k=w;var C=k,x={name:"Notification",methods:{notify(e){b.$.publishNotification(e)},notifyWarning(e){this.notify({text:e,warning:!0})},notifyError(e){throw this.notify({text:e,error:!0}),e}}};const $=x;var D=$,T={name:"Screen",methods:{isMobile(){return window.matchMedia("only screen and (max-width: 768px)").matches},isTablet(){return!this.isMobile()&&window.matchMedia("only screen and (max-width: 1023px)").matches},isDesktop(){return window.matchMedia("only screen and (min-width: 1024px)").matches}}};const _=T;var E=_,M={name:"Text",methods:{capitalize(e){return e?.length?e.charAt(0).toUpperCase()+e.slice(1):e},prettify(e){return e.split("_").map((e=>this.capitalize(e))).join(" ")},indent(e,t=2){return e.split("\n").map((e=>`${" ".repeat(t)}${e}`)).join("\n")}}};const j=M;var N=j,O=(n(560),{name:"Types",methods:{parseBoolean(e){return"string"===typeof e?(e=e.toLowerCase(),"true"===e||"false"!==e&&!!parseInt(e)):!!e},convertSize(e){"string"===typeof e&&(e=parseInt(e));let t=null;const n=["B","KB","MB","GB","TB"];return n.forEach(((i,s)=>{e<=1024&&null==t?t=i:e>1024&&(s===n.length-1?t=i:e/=1024)})),`${e.toFixed(2)} ${t}`},convertTime(e){const t={},n=[];if(e=parseFloat(e),t.d=Math.round(e/86400),t.h=Math.round(e/3600-24*t.d),t.m=Math.round(e/60-(24*t.d+60*t.h)),t.s=Math.round(e-(24*t.d+3600*t.h+60*t.m),1),parseInt(t.d)){let e=t.d+" day";t.d>1&&(e+="s"),n.push(e)}if(parseInt(t.h)){let e=t.h+" hour";t.h>1&&(e+="s"),n.push(e)}if(parseInt(t.m)){let e=t.m+" minute";t.m>1&&(e+="s"),n.push(e)}let i=t.s+" second";return t.s>1&&(i+="s"),n.push(i),n.join(" ")},objectsEqual(e,t){if("object"!==typeof e||"object"!==typeof t)return!1;if(null==e||null==t)return null==e&&null==t;for(const n of Object.keys(e||{}))switch(typeof e[n]){case"object":if(!this.objectsEqual(e[n],t[n]))return!1;break;case"function":if(e[n].toString()!=t[n]?.toString())return!1;break;default:if(e[n]!=t[n])return!1;break}for(const n of Object.keys(t||{}))if(null==e[n]&&null!=t[n])return!1;return!0},round(e,t){return Number(Math.round(e+"e"+t)+"e-"+t)}}});const S=O;var I=S,z={name:"Url",methods:{parseUrlFragment(){return window.location.hash.replace(/^#/,"").replace(/\?.*/,"")},getUrlArgs(){const e=window.location.hash.split("?").slice(1);return e.length?e[0].split(/[&;]/).reduce(((e,t)=>{const n=t.split("=");return n[0]?.length&&(e[n[0]]=decodeURIComponent(n[1])),e}),{}):{}},setUrlArgs(e){const t=this.getUrlArgs();e=Object.entries(e).reduce(((e,[n,i])=>(null!=i?e[n]=i:null!=t[n]&&delete t[n],e)),{}),e={...t,...e};let n=`${window.location.pathname}#${this.parseUrlFragment()}`;Object.keys(e).length&&(n+=`?${this.fragmentFromArgs(e)}`),window.location.href=n},encodeValue(e){return e?.length&&"null"!==e&&"undefined"!==e?e.match(/%[0-9A-F]{2}/i)?e:encodeURIComponent(e):""},fragmentFromArgs(e){return Object.entries(e).filter((([e,t])=>this.encodeValue(e)?.length&&this.encodeValue(t)?.length)).map((([e,t])=>`${this.encodeValue(e)}=${this.encodeValue(t)}`)).join("&")}}};const A=z;var P=A,Z={name:"Utils",mixins:[a,l,h,m,y,D,C,E,N,I,P]};const q=Z;var V=q},6791:function(e,t,n){n.d(t,{Z:function(){return d}});var i=n(6252);const s={class:"loading"},o={class:"icon"};function a(e,t){return(0,i.wg)(),(0,i.iD)("div",s,[(0,i._)("div",o,[((0,i.wg)(),(0,i.iD)(i.HY,null,(0,i.Ko)(4,(e=>(0,i._)("div",{key:e}))),64))])])}var r=n(3744);const c={},l=(0,r.Z)(c,[["render",a],["__scopeId","data-v-4d9c871b"]]);var d=l},5166:function(e,t,n){n.d(t,{Z:function(){return b}});var i=n(6252),s=n(3577);const o=e=>((0,i.dD)("data-v-dc19db9c"),e=e(),(0,i.Cn)(),e),a=["id"],r={key:0,class:"header"},c=["textContent"],l=o((()=>(0,i._)("i",{class:"fas fa-xmark"},null,-1))),d=[l],u={class:"body"};function h(e,t,n,o,l,h){return(0,i.wg)(),(0,i.iD)("div",{class:(0,s.C_)(["modal-container fade-in",{hidden:!l.isVisible}]),id:n.id,style:(0,s.j5)({"--z-index":h.zIndex}),onClick:t[3]||(t[3]=(...e)=>h.close&&h.close(...e))},[(0,i._)("div",{class:(0,s.C_)(["modal",e.$attrs.class])},[(0,i._)("div",{class:"content",style:(0,s.j5)({"--width":n.width,"--height":n.height}),onClick:t[2]||(t[2]=e=>e.stopPropagation())},[n.title?((0,i.wg)(),(0,i.iD)("div",r,[n.title?((0,i.wg)(),(0,i.iD)("div",{key:0,class:"title",textContent:(0,s.zw)(n.title)},null,8,c)):(0,i.kq)("",!0),(0,i._)("button",{title:"Close",alt:"Close",onClick:t[0]||(t[0]=(...e)=>h.close&&h.close(...e))},d)])):(0,i.kq)("",!0),(0,i._)("div",u,[(0,i.WI)(e.$slots,"default",{onModalClose:t[1]||(t[1]=(...e)=>h.close&&h.close(...e))},void 0,!0)])],4)],2)],14,a)}n(560);var f={name:"Modal",emits:["close","open"],props:{id:{type:String},title:{type:String},width:{type:[Number,String]},height:{type:[Number,String]},visible:{type:Boolean,default:!1},timeout:{type:[Number,String]},level:{type:Number,default:1}},data(){return{timeoutId:void 0,prevVisible:this.visible,isVisible:this.visible}},computed:{zIndex(){return 500+this.level}},methods:{close(){this.prevVisible=this.isVisible,this.isVisible=!1},hide(){this.close()},show(){this.prevVisible=this.isVisible,this.isVisible=!0},open(){this.show()},toggle(){this.isVisible?this.close():this.show()},onKeyUp(e){e.stopPropagation(),"Escape"===e.key&&this.close()}},mounted(){const e=this,t=t=>{t?e.$emit("open"):e.$emit("close"),e.isVisible=t};document.body.addEventListener("keyup",this.onKeyUp),this.$watch((()=>this.visible),t),this.$watch((()=>this.isVisible),t)},unmounted(){document.body.removeEventListener("keyup",this.onKeyUp)},updated(){if(this.prevVisible=this.isVisible,this.isVisible){let e=parseInt(getComputedStyle(this.$el).zIndex),t=[];for(const n of document.querySelectorAll(".modal-container:not(.hidden)")){const i=parseInt(getComputedStyle(n).zIndex);i>e?(e=i,t=[n]):i===e&&t.push(n)}(t.indexOf(this.$el)<0||t.length>1)&&(this.$el.style.zIndex=e+1)}if(this.isVisible&&this.timeout&&!this.timeoutId){const e=e=>()=>{e.close(),e.timeoutId=void 0};this.timeoutId=setTimeout(e(this),0+this.timeout)}}},p=n(3744);const m=(0,p.Z)(f,[["render",h],["__scopeId","data-v-dc19db9c"]]);var b=m},7833:function(e,t,n){n.d(t,{Z:function(){return m}});var i=n(6252),s=n(9963),o=n(3577);const a=e=>((0,i.dD)("data-v-06d2f237"),e=e(),(0,i.Cn)(),e),r={class:"dialog-content"},c=a((()=>(0,i._)("i",{class:"fas fa-check"},null,-1))),l=a((()=>(0,i._)("i",{class:"fas fa-xmark"},null,-1)));function d(e,t,n,a,d,u){const h=(0,i.up)("Modal");return(0,i.wg)(),(0,i.j4)(h,{ref:"modal",title:n.title,onClose:u.close},{default:(0,i.w5)((()=>[(0,i._)("div",r,[(0,i.WI)(e.$slots,"default",{},void 0,!0)]),(0,i._)("form",{class:"buttons",onSubmit:t[4]||(t[4]=(0,s.iM)(((...e)=>u.onConfirm&&u.onConfirm(...e)),["prevent"]))},[(0,i._)("button",{type:"submit",class:"ok-btn",onClick:t[0]||(t[0]=(...e)=>u.onConfirm&&u.onConfirm(...e)),onTouch:t[1]||(t[1]=(...e)=>u.onConfirm&&u.onConfirm(...e))},[c,(0,i.Uk)("   "+(0,o.zw)(n.confirmText),1)],32),(0,i._)("button",{type:"button",class:"cancel-btn",onClick:t[2]||(t[2]=(...e)=>u.close&&u.close(...e)),onTouch:t[3]||(t[3]=(...e)=>u.close&&u.close(...e))},[l,(0,i.Uk)("   "+(0,o.zw)(n.cancelText),1)],32)],32)])),_:3},8,["title","onClose"])}var u=n(5166),h={emits:["input","click","close","touch"],components:{Modal:u.Z},props:{title:{type:String},confirmText:{type:String,default:"OK"},cancelText:{type:String,default:"Cancel"}},methods:{onConfirm(){this.$emit("input"),this.close()},open(){this.$refs.modal.show()},close(){this.$refs.modal.hide(),this.$emit("close")},show(){this.open()},hide(){this.close()}}},f=n(3744);const p=(0,f.Z)(h,[["render",d],["__scopeId","data-v-06d2f237"]]);var m=p}},t={};function n(i){var s=t[i];if(void 0!==s)return s.exports;var o=t[i]={exports:{}};return e[i].call(o.exports,o,o.exports,n),o.exports}n.m=e,function(){var e=[];n.O=function(t,i,s,o){if(!i){var a=1/0;for(d=0;d<e.length;d++){i=e[d][0],s=e[d][1],o=e[d][2];for(var r=!0,c=0;c<i.length;c++)(!1&o||a>=o)&&Object.keys(n.O).every((function(e){return n.O[e](i[c])}))?i.splice(c--,1):(r=!1,o<a&&(a=o));if(r){e.splice(d--,1);var l=s();void 0!==l&&(t=l)}}return t}o=o||0;for(var d=e.length;d>0&&e[d-1][2]>o;d--)e[d]=e[d-1];e[d]=[i,s,o]}}(),function(){n.n=function(e){var t=e&&e.__esModule?function(){return e["default"]}:function(){return e};return n.d(t,{a:t}),t}}(),function(){var e,t=Object.getPrototypeOf?function(e){return Object.getPrototypeOf(e)}:function(e){return e.__proto__};n.t=function(i,s){if(1&s&&(i=this(i)),8&s)return i;if("object"===typeof i&&i){if(4&s&&i.__esModule)return i;if(16&s&&"function"===typeof i.then)return i}var o=Object.create(null);n.r(o);var a={};e=e||[null,t({}),t([]),t(t)];for(var r=2&s&&i;"object"==typeof r&&!~e.indexOf(r);r=t(r))Object.getOwnPropertyNames(r).forEach((function(e){a[e]=function(){return i[e]}}));return a["default"]=function(){return i},n.d(o,a),o}}(),function(){n.d=function(e,t){for(var i in t)n.o(t,i)&&!n.o(e,i)&&Object.defineProperty(e,i,{enumerable:!0,get:t[i]})}}(),function(){n.f={},n.e=function(e){return Promise.all(Object.keys(n.f).reduce((function(t,i){return n.f[i](e,t),t}),[]))}}(),function(){n.u=function(e){return"static/js/"+({685:"register",2245:"notfound",4535:"login",7401:"panel",9966:"dashboard",9975:"plugin"}[e]||e)+"."+{34:"4c59fb03",58:"e14719bf",65:"ae7df477",169:"92c1a438",182:"0d7f4276",281:"1392234b",446:"cdd8637e",472:"bf7d503c",669:"67b2777b",685:"c6276a24",729:"81683ae6",735:"09e06f2a",746:"9a199f8f",813:"3ec855c4",844:"4b1a666d",864:"e3d97a4c",906:"38a51fd1",980:"ee52bc55",984:"50a15617",1088:"1c904e63",1171:"58632721",1327:"a10148a0",1391:"a76844c2",1449:"a5b4b2d2",1485:"ffaf2a68",1512:"b686fb87",1558:"6fb75764",1706:"1a5248ba",1807:"16b67ced",1931:"fb0bd778",1949:"3baca6d5",2018:"797df628",2106:"283a2018",2140:"d72a32d8",2183:"f8766c50",2200:"a7bc2894",2217:"d60fbb58",2245:"388a3a0b",2308:"5dbe514d",2460:"2a8400ba",2614:"c79ffd3c",2718:"1c9a0e20",2732:"93033fcd",2844:"288f7727",2853:"99de82eb",2892:"e9ab901f",2893:"c9d72a7c",2924:"46a45250",2948:"042c8d4e",2951:"d5589556",2976:"e3dbc1e6",2992:"efd583f8",3083:"f289e43a",3211:"da74a6a1",3322:"dadc23cc",3368:"8c968129",3369:"cb38d432",3393:"aeccb0ec",3400:"748068b2",3518:"6ca9dd02",3559:"61ebd182",3732:"d6584e8e",3826:"cc264dd1",3835:"2db962db",3862:"0ca0e08c",3924:"0fd0a3c0",4015:"d70ab847",4053:"0d63e56f",4109:"9ac9490e",4364:"771a5068",4535:"588012cf",4619:"b038c54a",4765:"f893461f",4790:"7514123b",5197:"1a8603ef",5207:"7f241e21",5285:"ec1a8894",5329:"1dc4e553",5505:"35fbb782",5638:"d0047a11",5906:"5eaf69b5",5933:"e31ea3c0",6148:"6a799072",6217:"e038c85c",6281:"38bbe6a9",6324:"93ea59d2",6362:"4870392f",6429:"36d3a644",6523:"426200f5",6561:"fc5ef77b",6640:"49b4564c",6882:"8515123f",7089:"8779e12e",7243:"5d565037",7381:"16a4edaa",7401:"8a0ee873",7493:"33a4fb27",7528:"dc0f0c8b",7590:"be3564f1",7624:"c638b411",7651:"e7da8dba",7819:"d1f61659",7841:"580c6097",8010:"c9b590a2",8069:"51c1e8b1",8179:"8cdc4214",8391:"c04e1c3a",8498:"e34e99e5",8621:"edd395ad",8752:"1ad15e4e",8769:"52fe04f5",8784:"5892bf2a",8825:"f5386513",8895:"c5e5490a",8930:"5354086d",8989:"d29a4bdb",9091:"b9371c68",9092:"89f920f0",9122:"bd27eb9c",9164:"0a6e4f74",9211:"e190626a",9334:"043959f5",9381:"fb6fbb64",9461:"1b6014d3",9472:"3664c2f1",9732:"d4c667fa",9751:"9e425e19",9962:"76f7d059",9966:"fd1a4743",9975:"9bdd8cab"}[e]+".js"}}(),function(){n.miniCssF=function(e){return"static/css/"+({7401:"panel",9966:"dashboard",9975:"plugin"}[e]||e)+"."+{34:"697bbb6c",58:"4e42bcd7",65:"f26c4c69",169:"e5f2ae64",182:"ceea8242",281:"59540c1e",446:"00260d6b",472:"34503f0a",669:"b79c5124",729:"57b57d7b",735:"826ef4a8",746:"950ba016",864:"78f08d0f",906:"ba484368",980:"3fc64539",984:"d1631b13",1171:"e994a915",1327:"1b87ccea",1391:"4c2a54af",1449:"aa6f3b13",1485:"affb1035",1558:"972e84ae",1706:"6d512c72",1807:"c0b8bd4e",1931:"4aa7fbb8",1949:"5bc4128f",2018:"423c85e4",2140:"ccffb19d",2217:"5d4af353",2308:"b500f3ef",2460:"23b03062",2718:"7330d755",2844:"f22570b6",2892:"29e6b46e",2893:"6ff6d2f5",2924:"f0edc749",2948:"a853dd34",2976:"e523133c",2992:"3ad12451",3211:"bb22df23",3368:"46202981",3369:"6e3c3961",3393:"916736c6",3559:"18cfd512",3826:"a3a30364",3835:"4397fb75",3924:"1e986b6a",4015:"92ad285d",4109:"5418ba6a",4364:"92fac5a6",4790:"03576fd8",5197:"aa8e547f",5207:"270e37eb",5285:"b0da7899",5329:"389efe5a",5638:"ddd3f9ab",5906:"68bca63a",5933:"bfa8eecd",6217:"199dcb8a",6281:"96662ea9",6324:"12908cb3",6429:"370bde85",6523:"2d62c484",6561:"723d0b72",6882:"0292b32b",7243:"b4062d54",7401:"d8b4a6d8",7493:"6a1875d9",7528:"4bf79319",7590:"e5788cc0",7624:"b51179b6",7651:"f63c0e66",7841:"fdeea133",8010:"c7bd209b",8069:"7f911c23",8179:"c703112d",8391:"bab12c47",8498:"8ac7dc79",8621:"1d643b83",8769:"9fc4ff4e",8825:"6bed1a5d",8989:"995028ce",9092:"a5a11002",9122:"910eaed1",9211:"6c8097ed",9381:"9ee3ac59",9461:"4d6142dc",9732:"75f88cfe",9751:"99faecb1",9962:"1bd519cb",9966:"c3db81e8",9975:"0537ff26"}[e]+".css"}}(),function(){n.g=function(){if("object"===typeof globalThis)return globalThis;try{return this||new Function("return this")()}catch(e){if("object"===typeof window)return window}}()}(),function(){n.o=function(e,t){return Object.prototype.hasOwnProperty.call(e,t)}}(),function(){var e={},t="platypush:";n.l=function(i,s,o,a){if(e[i])e[i].push(s);else{var r,c;if(void 0!==o)for(var l=document.getElementsByTagName("script"),d=0;d<l.length;d++){var u=l[d];if(u.getAttribute("src")==i||u.getAttribute("data-webpack")==t+o){r=u;break}}r||(c=!0,r=document.createElement("script"),r.charset="utf-8",r.timeout=120,n.nc&&r.setAttribute("nonce",n.nc),r.setAttribute("data-webpack",t+o),r.src=i),e[i]=[s];var h=function(t,n){r.onerror=r.onload=null,clearTimeout(f);var s=e[i];if(delete e[i],r.parentNode&&r.parentNode.removeChild(r),s&&s.forEach((function(e){return e(n)})),t)return t(n)},f=setTimeout(h.bind(null,void 0,{type:"timeout",target:r}),12e4);r.onerror=h.bind(null,r.onerror),r.onload=h.bind(null,r.onload),c&&document.head.appendChild(r)}}}(),function(){n.r=function(e){"undefined"!==typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})}}(),function(){n.p="/"}(),function(){if("undefined"!==typeof document){var e=function(e,t,n,i,s){var o=document.createElement("link");o.rel="stylesheet",o.type="text/css";var a=function(n){if(o.onerror=o.onload=null,"load"===n.type)i();else{var a=n&&("load"===n.type?"missing":n.type),r=n&&n.target&&n.target.href||t,c=new Error("Loading CSS chunk "+e+" failed.\n("+r+")");c.code="CSS_CHUNK_LOAD_FAILED",c.type=a,c.request=r,o.parentNode&&o.parentNode.removeChild(o),s(c)}};return o.onerror=o.onload=a,o.href=t,n?n.parentNode.insertBefore(o,n.nextSibling):document.head.appendChild(o),o},t=function(e,t){for(var n=document.getElementsByTagName("link"),i=0;i<n.length;i++){var s=n[i],o=s.getAttribute("data-href")||s.getAttribute("href");if("stylesheet"===s.rel&&(o===e||o===t))return s}var a=document.getElementsByTagName("style");for(i=0;i<a.length;i++){s=a[i],o=s.getAttribute("data-href");if(o===e||o===t)return s}},i=function(i){return new Promise((function(s,o){var a=n.miniCssF(i),r=n.p+a;if(t(a,r))return s();e(i,r,null,s,o)}))},s={2143:0};n.f.miniCss=function(e,t){var n={34:1,58:1,65:1,169:1,182:1,281:1,446:1,472:1,669:1,729:1,735:1,746:1,864:1,906:1,980:1,984:1,1171:1,1327:1,1391:1,1449:1,1485:1,1558:1,1706:1,1807:1,1931:1,1949:1,2018:1,2140:1,2217:1,2308:1,2460:1,2718:1,2844:1,2892:1,2893:1,2924:1,2948:1,2976:1,2992:1,3211:1,3368:1,3369:1,3393:1,3559:1,3826:1,3835:1,3924:1,4015:1,4109:1,4364:1,4790:1,5197:1,5207:1,5285:1,5329:1,5638:1,5906:1,5933:1,6217:1,6281:1,6324:1,6429:1,6523:1,6561:1,6882:1,7243:1,7401:1,7493:1,7528:1,7590:1,7624:1,7651:1,7841:1,8010:1,8069:1,8179:1,8391:1,8498:1,8621:1,8769:1,8825:1,8989:1,9092:1,9122:1,9211:1,9381:1,9461:1,9732:1,9751:1,9962:1,9966:1,9975:1};s[e]?t.push(s[e]):0!==s[e]&&n[e]&&t.push(s[e]=i(e).then((function(){s[e]=0}),(function(t){throw delete s[e],t})))}}}(),function(){var e={2143:0};n.f.j=function(t,i){var s=n.o(e,t)?e[t]:void 0;if(0!==s)if(s)i.push(s[2]);else if(/^(1(327|391|558|82|931)|2(308|844|924|992)|4(109|364|790)|5(8|906|933)|6(217|281|561|69)|7(243|624|651)|8(069|64|989)|3393|3826|906|9122)$/.test(t))e[t]=0;else{var o=new Promise((function(n,i){s=e[t]=[n,i]}));i.push(s[2]=o);var a=n.p+n.u(t),r=new Error,c=function(i){if(n.o(e,t)&&(s=e[t],0!==s&&(e[t]=void 0),s)){var o=i&&("load"===i.type?"missing":i.type),a=i&&i.target&&i.target.src;r.message="Loading chunk "+t+" failed.\n("+o+": "+a+")",r.name="ChunkLoadError",r.type=o,r.request=a,s[1](r)}};n.l(a,c,"chunk-"+t,t)}},n.O.j=function(t){return 0===e[t]};var t=function(t,i){var s,o,a=i[0],r=i[1],c=i[2],l=0;if(a.some((function(t){return 0!==e[t]}))){for(s in r)n.o(r,s)&&(n.m[s]=r[s]);if(c)var d=c(n)}for(t&&t(i);l<a.length;l++)o=a[l],n.o(e,o)&&e[o]&&e[o][0](),e[o]=0;return n.O(d)},i=self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[];i.forEach(t.bind(null,0)),i.push=t.bind(null,i.push.bind(i))}();var i=n.O(void 0,[4998],(function(){return n(5621)}));i=n.O(i)})();
//# sourceMappingURL=app.90d7ba58.js.map