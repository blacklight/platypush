(function(){"use strict";var e={5250:function(e,t,n){n.d(t,{$:function(){return s}});var i=n(9652);const s=(0,i.Z)();s.publishEntity=e=>{s.emit("entity-update",e)},s.onEntity=e=>{s.on("entity-update",e)},s.publishNotification=e=>{s.emit("notification-create",e)},s.onNotification=e=>{s.on("notification-create",e)}},2520:function(e,t,n){var i=n(9963),s=n(6252);function o(e,t,n,i,o,a){const r=(0,s.up)("Events"),c=(0,s.up)("Notifications"),l=(0,s.up)("VoiceAssistant"),d=(0,s.up)("Pushbullet"),u=(0,s.up)("Ntfy"),h=(0,s.up)("ConfirmDialog"),f=(0,s.up)("DropdownContainer"),p=(0,s.up)("router-view");return(0,s.wg)(),(0,s.iD)(s.HY,null,[a.hasWebsocket?((0,s.wg)(),(0,s.j4)(r,{key:0,ref:"events"},null,512)):(0,s.kq)("",!0),(0,s.Wm)(c,{ref:"notifications"},null,512),a.hasAssistant?((0,s.wg)(),(0,s.j4)(l,{key:1,ref:"voice-assistant"},null,512)):(0,s.kq)("",!0),a.hasPushbullet?((0,s.wg)(),(0,s.j4)(d,{key:2,ref:"pushbullet"},null,512)):(0,s.kq)("",!0),a.hasNtfy?((0,s.wg)(),(0,s.j4)(u,{key:3,ref:"ntfy"},null,512)):(0,s.kq)("",!0),(0,s.Wm)(h,{ref:"pwaDialog",onInput:a.installPWA},{default:(0,s.w5)((()=>[(0,s.Uk)(" Would you like to install this application locally? ")])),_:1},8,["onInput"]),(0,s.Wm)(f),(0,s.Wm)(p)],64)}var a=n(7833);const r={class:"dropdown-container"};function c(e,t,n,i,o,a){return(0,s.wg)(),(0,s.iD)("div",r)}var l=n(5250),d={methods:{onOpen(e){e?.$el&&(e.keepOpenOnItemClick||this.onClose(),this.$el.appendChild(e.$el))},onClose(){this.$el.innerHTML=""}},mounted(){l.$.on("dropdown-open",this.onOpen),l.$.on("dropdown-close",this.onClose)}},u=n(3744);const h=(0,u.Z)(d,[["render",c],["__scopeId","data-v-c190f656"]]);var f=h;const p={class:"notifications"};function m(e,t,n,i,o,a){const r=(0,s.up)("Notification");return(0,s.wg)(),(0,s.iD)("div",p,[((0,s.wg)(!0),(0,s.iD)(s.HY,null,(0,s.Ko)(e.notifications,((e,t,n)=>((0,s.wg)(),(0,s.j4)(r,{key:n,id:t,text:e.text,html:e.html,title:e.title,link:e.link,image:e.image,warning:e.warning,error:e.error,onClicked:a.destroy},null,8,["id","text","html","title","link","image","warning","error","onClicked"])))),128))])}var b=n(3577);const g=["textContent"],v={class:"body"},y={key:0,class:"image col-3"},w={class:"row"},k=["src"],C={key:3,class:"fa fa-exclamation"},x={key:4,class:"fa fa-times"},$=["textContent"],T=["innerHTML"],D=["textContent"],E=["innerHTML"];function _(e,t,n,i,o,a){return(0,s.wg)(),(0,s.iD)("div",{class:(0,b.C_)(["notification fade-in",{warning:n.warning,error:n.error}]),onClick:t[0]||(t[0]=(...e)=>a.clicked&&a.clicked(...e))},[n.title?((0,s.wg)(),(0,s.iD)("div",{key:0,class:"title",textContent:(0,b.zw)(n.title)},null,8,g)):(0,s.kq)("",!0),(0,s._)("div",v,[n.image||n.warning||n.error?((0,s.wg)(),(0,s.iD)("div",y,[(0,s._)("div",w,[n.image&&n.image.src?((0,s.wg)(),(0,s.iD)("img",{key:0,src:n.image.src,alt:""},null,8,k)):n.image&&n.image.icon?((0,s.wg)(),(0,s.iD)("i",{key:1,class:(0,b.C_)(["fa","fa-"+n.image.icon]),style:(0,b.j5)(n.image.color?"--color: "+n.image.color:"")},null,6)):n.image&&n.image.iconClass?((0,s.wg)(),(0,s.iD)("i",{key:2,class:(0,b.C_)(n.image.iconClass),style:(0,b.j5)(n.image.color?"--color: "+n.image.color:"")},null,6)):n.warning?((0,s.wg)(),(0,s.iD)("i",C)):n.error?((0,s.wg)(),(0,s.iD)("i",x)):(0,s.kq)("",!0)])])):(0,s.kq)("",!0),n.text&&n.image?((0,s.wg)(),(0,s.iD)("div",{key:1,class:"text col-9",textContent:(0,b.zw)(n.text)},null,8,$)):(0,s.kq)("",!0),n.html&&n.image?((0,s.wg)(),(0,s.iD)("div",{key:2,class:"text col-9",innerHTML:n.html},null,8,T)):(0,s.kq)("",!0),n.text&&!n.image?((0,s.wg)(),(0,s.iD)("div",{key:3,class:"text row horizontal-center",textContent:(0,b.zw)(n.text)},null,8,D)):(0,s.kq)("",!0),n.html&&!n.image?((0,s.wg)(),(0,s.iD)("div",{key:4,class:"text row horizontal-center",innerHTML:n.html},null,8,E)):(0,s.kq)("",!0)])],2)}var M={name:"Notification",props:["id","text","html","title","image","link","error","warning"],methods:{clicked(){this.link&&window.open(this.link,"_blank"),this.$emit("clicked",this.id)}}};const N=(0,u.Z)(M,[["render",_],["__scopeId","data-v-7646705e"]]);var O=N,j={name:"Notifications",components:{Notification:O},props:{duration:{type:Number,default:1e4}},data:function(){return{index:0,notifications:{},timeouts:{}}},methods:{create:function(e){const t=this.index++;this.notifications[t]=e,null==e.duration&&(e.duration=this.duration);const n=e.duration?parseInt(e.duration):0;n&&(this.timeouts[t]=setTimeout(this.destroy.bind(null,t),n))},destroy:function(e){delete this.notifications[e],delete this.timeouts[e]}}};const S=(0,u.Z)(j,[["render",m],["__scopeId","data-v-6dc8bebc"]]);var A=S,I=n(8637);function z(e,t,n,i,o,a){return(0,s.wg)(),(0,s.iD)("div")}n(560);var P={name:"Events",data(){return{ws:null,initialized:!1,pending:!1,opened:!1,timeout:null,reconnectMsecs:1e3,minReconnectMsecs:1e3,maxReconnectMsecs:3e4,handlers:{},handlerNameToEventTypes:{}}},methods:{onWebsocketTimeout(){console.log("Websocket reconnection timed out, retrying"),this.reconnectMsecs=Math.min(2*this.reconnectMsecs,this.maxReconnectMsecs),this.pending=!1,this.ws&&this.ws.close(),this.onClose()},onMessage(e){const t=[];if(e=e.data,"string"===typeof e)try{e=JSON.parse(e)}catch(n){console.warn("Received invalid non-JSON event"),console.warn(e)}if(console.debug(e),"event"===e.type){null in this.handlers&&t.push(this.handlers[null]),e.args.type in this.handlers&&t.push(...Object.values(this.handlers[e.args.type]));for(let n of t)n&&(n instanceof Array?n=n[0]:n instanceof Object&&!(n instanceof Function)&&(n=Object.values(n)[0]),n(e.args))}},onOpen(){this.opened&&(console.log("There's already an opened websocket connection, closing the newly opened one"),this.ws&&(this.ws.onclose=()=>{},this.ws.close())),console.log("Websocket connection successful"),this.opened=!0,this.reconnectMsecs=this.minReconnectMsecs,this.pending&&(this.pending=!1),this.timeout&&(clearTimeout(this.timeout),this.timeout=void 0)},onError(e){console.error("Websocket error"),console.error(e)},onClose(e){e&&console.log(`Websocket closed - code: ${e.code} - reason: ${e.reason}. Retrying in ${this.reconnectMsecs/1e3}s`),this.opened=!1,this.pending||(this.pending=!0,this.init())},init(){try{const e="https:"===location.protocol?"wss":"ws",t=`${e}://${location.host}/ws/events`;this.ws=new WebSocket(t)}catch(e){return console.error("Websocket initialization error"),void console.error(e)}this.pending=!0,this.timeout=setTimeout(this.onWebsocketTimeout,this.reconnectMsecs),this.ws.onmessage=this.onMessage,this.ws.onopen=this.onOpen,this.ws.onerror=this.onError,this.ws.onclose=this.onClose,this.initialized=!0},subscribe(e){const t=e.handler,n=e.events.length?e.events:[null],i=e.handlerName;for(const s of n)s in this.handlers||(this.handlers[s]={}),i in this.handlerNameToEventTypes||(this.handlerNameToEventTypes[i]=n),this.handlers[s][i]=t;return()=>{this.unsubscribe(i)}},unsubscribe(e){const t=this.handlerNameToEventTypes[e];if(t){for(const n of t)this.handlers[n]?.[e]&&(delete this.handlers[n][e],Object.keys(this.handlers[n]).length||delete this.handlers[n]);delete this.handlerNameToEventTypes[e]}}},created(){l.$.on("subscribe",this.subscribe),l.$.on("unsubscribe",this.unsubscribe),this.$watch("opened",(e=>{l.$.emit(e?"connect":"disconnect")})),this.init()}};const q=(0,u.Z)(P,[["render",z]]);var V=q;const W={class:"assistant-modal"},R={class:"icon"},Z={key:0,class:"fa fa-bell"},U={key:1,class:"fa fa-volume-up"},L={key:2,class:"fa fa-comment-dots"},F={key:3,class:"fa fa-microphone"},B={class:"text"},H={key:0,class:"listening"},K=(0,s._)("span",null,"Assistant listening",-1),J=[K],Y={key:1,class:"speech-recognized"},G=["textContent"],Q={key:2,class:"responding"},X=["textContent"];function ee(e,t,n,i,o,a){const r=(0,s.up)("Modal");return(0,s.wg)(),(0,s.iD)("div",W,[(0,s.Wm)(r,{ref:"assistantModal"},{default:(0,s.w5)((()=>[(0,s._)("div",R,[o.state.alerting?((0,s.wg)(),(0,s.iD)("i",Z)):o.state.responding?((0,s.wg)(),(0,s.iD)("i",U)):o.state.speechRecognized?((0,s.wg)(),(0,s.iD)("i",L)):((0,s.wg)(),(0,s.iD)("i",F))]),(0,s._)("div",B,[o.state.listening?((0,s.wg)(),(0,s.iD)("div",H,J)):o.state.speechRecognized?((0,s.wg)(),(0,s.iD)("div",Y,[(0,s._)("span",{textContent:(0,b.zw)(o.phrase)},null,8,G)])):o.state.responding?((0,s.wg)(),(0,s.iD)("div",Q,[(0,s._)("span",{textContent:(0,b.zw)(o.responseText)},null,8,X)])):(0,s.kq)("",!0)])])),_:1},512)])}var te=n(3493),ne={name:"VoiceAssistant",components:{Modal:te.Z},mixins:[I.Z],data(){return{responseText:"",phrase:"",hideTimeout:void 0,state:{listening:!1,speechRecognized:!1,responding:!1,alerting:!1}}},methods:{reset(){this.state.listening=!1,this.state.speechRecognized=!1,this.state.responding=!1,this.state.alerting=!1,this.phrase="",this.responseText=""},conversationStart(){this.reset(),this.state.listening=!0,this.$refs.assistantModal.show(),this.hideTimeout&&(clearTimeout(this.hideTimeout),this.hideTimeout=void 0)},conversationEnd(){const e=this;this.hideTimeout=setTimeout((()=>{this.reset(),e.$refs.assistantModal.close(),e.hideTimeout=void 0}),4e3)},speechRecognized(e){this.reset(),this.state.speechRecognized=!0,this.phrase=e.phrase,this.$refs.assistantModal.show()},response(e){this.reset(),this.state.responding=!0,this.responseText=e.response_text,this.$refs.assistantModal.show()},alertOn(){this.reset(),this.state.alerting=!0,this.$refs.assistantModal.show()},alertOff(){this.reset(),this.state.alerting=!1,this.$refs.assistantModal.close()},registerHandlers(){this.subscribe(this.conversationStart,null,"platypush.message.event.assistant.ConversationStartEvent"),this.subscribe(this.alertOn,null,"platypush.message.event.assistant.AlertStartedEvent"),this.subscribe(this.alertOff,null,"platypush.message.event.assistant.AlertEndEvent"),this.subscribe(this.speechRecognized,null,"platypush.message.event.assistant.SpeechRecognizedEvent"),this.subscribe(this.response,null,"platypush.message.event.assistant.ResponseEvent"),this.subscribe(this.conversationEnd,null,"platypush.message.event.assistant.ConversationEndEvent","platypush.message.event.assistant.ResponseEndEvent","platypush.message.event.assistant.NoResponseEvent","platypush.message.event.assistant.ConversationTimeoutEvent")}},mounted(){this.registerHandlers()}};const ie=(0,u.Z)(ne,[["render",ee]]);var se=ie;function oe(e,t,n,i,o,a){return(0,s.wg)(),(0,s.iD)("div")}var ae={name:"Ntfy",mixins:[I.Z],methods:{onMessage(e){this.notify({title:e.title,text:e.message,image:{icon:"bell"}})}},mounted(){this.subscribe(this.onMessage,null,"platypush.message.event.ntfy.NotificationEvent")}};const re=(0,u.Z)(ae,[["render",oe]]);var ce=re;function le(e,t,n,i,o,a){return(0,s.wg)(),(0,s.iD)("div")}var de={mixins:[I.Z],methods:{onMessage(e){this.notify({title:e.title,text:e.body,image:{src:e.icon?"data:image/png;base64, "+e.icon:void 0,icon:e.icon?void 0:"bell"}})}},mounted(){this.subscribe(this.onMessage,null,"platypush.message.event.pushbullet.PushbulletNotificationEvent")}};const ue=(0,u.Z)(de,[["render",le]]);var he=ue,fe={mixins:[I.Z],components:{ConfirmDialog:a.Z,DropdownContainer:f,Events:V,Notifications:A,Ntfy:ce,Pushbullet:he,VoiceAssistant:se},data(){return{config:{},userAuthenticated:!1,connected:!1,pwaInstallEvent:null}},computed:{hasWebsocket(){return this.userAuthenticated&&"backend.http"in this.config},hasAssistant(){return this.hasWebsocket},hasPushbullet(){return this.hasWebsocket&&("pushbullet"in this.config||"backend.pushbullet"in this.config)},hasNtfy(){return this.hasWebsocket&&"ntfy"in this.config}},methods:{onNotification(e){this.$refs.notifications.create(e)},async initConfig(){this.config=await this.request("config.get",{},6e4,!1),this.userAuthenticated=!0},installPWA(){this.pwaInstallEvent&&this.pwaInstallEvent.prompt(),this.$refs.pwaDialog.close()}},created(){this.initConfig()},beforeMount(){this.getCookie("pwa-dialog-shown")?.length||window.addEventListener("beforeinstallprompt",(e=>{e.preventDefault(),this.pwaInstallEvent=e,this.$refs.pwaDialog.show(),this.setCookie("pwa-dialog-shown","1",{expires:new Date((new Date).getTime()+31536e6)})}))},mounted(){l.$.onNotification(this.onNotification),l.$.on("connect",(()=>this.connected=!0)),l.$.on("disconnect",(()=>this.connected=!1))}};const pe=(0,u.Z)(fe,[["render",o]]);var me=pe,be=n(2201);const ge=[{path:"/",name:"Panel",component:()=>Promise.all([n.e(5933),n.e(9549),n.e(735),n.e(6281),n.e(58),n.e(2924),n.e(4084),n.e(6096),n.e(6217),n.e(2018),n.e(3393),n.e(7401)]).then(n.bind(n,8665))},{path:"/dashboard/:name",name:"Dashboard",component:()=>Promise.all([n.e(6096),n.e(9966)]).then(n.bind(n,8332))},{path:"/plugin/:plugin",name:"Plugin",component:()=>Promise.all([n.e(5933),n.e(9549),n.e(6281),n.e(2924),n.e(4084),n.e(6096),n.e(6217),n.e(3393),n.e(9975)]).then(n.bind(n,2354))},{path:"/login",name:"Login",component:()=>Promise.all([n.e(8590),n.e(4535)]).then(n.bind(n,1918))},{path:"/register",name:"Register",component:()=>Promise.all([n.e(8590),n.e(685)]).then(n.bind(n,9780))},{path:"/:catchAll(.*)",component:()=>n.e(2245).then(n.bind(n,2751))}],ve=(0,be.p7)({history:(0,be.PO)(),routes:ge});var ye=ve,we=n(5205);(0,we.z)("/service-worker.js",{ready(){console.log("App is being served from cache by a service worker.\nFor more details, visit https://goo.gl/AFskqB")},registered(){console.log("Service worker has been registered.")},cached(){console.log("Content has been cached for offline use.")},updatefound(){console.log("New content is downloading.")},updated(){console.log("New content is available; please refresh.")},offline(){console.log("No internet connection found. App is running in offline mode.")},error(e){console.error("Error during service worker registration:",e)}});const ke=(0,i.ri)(me);ke.config.globalProperties._config=window.config,ke.use(ye).mount("#app")},8637:function(e,t,n){n.d(t,{Z:function(){return W}});var i=n(5121),s={name:"Api",methods:{execute(e,t=6e4,n=!0){const s={};return"target"in e&&e["target"]||(e["target"]="localhost"),"type"in e&&e["type"]||(e["type"]="request"),t&&(s.timeout=t),new Promise(((t,o)=>{i.Z.post("/execute",e,s).then((e=>{if(e=e.data.response,e.errors?.length){const t=e.errors?.[0]||e;this.notify({text:t,error:!0}),o(t)}else t(e.output)})).catch((e=>{412===e?.response?.data?.code&&window.location.href.indexOf("/register")<0?window.location.href="/register?redirect="+window.location.href:401===e?.response?.data?.code&&window.location.href.indexOf("/login")<0?window.location.href="/login?redirect="+window.location.href:(console.log(e),n&&this.notify({text:e,error:!0}),o(e))}))}))},request(e,t={},n=6e4,i=!0){return this.execute({type:"request",action:e,args:t},n,i)},timeout(e){return new Promise((t=>setTimeout(t,e)))}}};const o=s;var a=o,r={name:"Clipboard",methods:{async copyToClipboard(e){await navigator.clipboard.writeText(e),this.notify({text:"Copied to the clipboard",image:{icon:"clipboard"}})}}};const c=r;var l=c,d={name:"Cookies",methods:{getCookies(){return document.cookie.split(/;\s*/).reduce(((e,t)=>{const[n,i]=t.split("=");return e[n]=i,e}),{})},getCookie(e){return this.getCookies()[e]},setCookie(e,t,n){document.cookie=`${e}=${t}; path=${n?.path||"/"}`+(n?.expires?`; expires=${n?.expires.toISOString()}`:"")},deleteCookie(e){document.cookie=`${e}=; expires=1970-01-01T00:00:00Z`}}};const u=d;var h=u,f={name:"DateTime",methods:{formatDate(e,t=!1){return"number"===typeof e?e=new Date(1e3*e):"string"===typeof e&&(e=new Date(Date.parse(e))),e.toDateString().substring(0,t?15:10)},formatTime(e,t=!0){return"number"===typeof e&&(e=new Date(1e3*e)),"string"===typeof e&&(e=new Date(Date.parse(e))),e.toTimeString().substring(0,t?8:5)},formatDateTime(e,t=!1,n=!0,i=!1){return"number"===typeof e&&(e=new Date(1e3*e)),"string"===typeof e&&(e=new Date(Date.parse(e))),i&&0===e.getHours()&&0===e.getMinutes()&&0===e.getSeconds()?this.formatDate(e,t):`${this.formatDate(e,t)}, ${this.formatTime(e,n)}`}}};const p=f;var m=p,b=(n(3429),n(5250)),g={name:"Events",computed:{_eventsReady(){return this.$root.$refs.events?.initialized}},methods:{subscribe(e,t,...n){const i=()=>{b.$.emit("subscribe",{events:n,handler:e,handlerName:t||this.generateId()})};if(this._eventsReady)return void i();const s=this,o=this.$watch((()=>s._eventsReady),(e=>{e&&(i(),o())}));return o},unsubscribe(e){b.$.emit("unsubscribe",e)},generateId(){return btoa([...Array(11).keys()].map((()=>String.fromCharCode(Math.round(255*Math.random())))))}}};const v=g;var y=v,w={name:"Extensions",methods:{pluginDisplayName(e){const t=e.split(".");return t.forEach(((e,n)=>{t[n]=e.charAt(0).toUpperCase()+e.slice(1)})),t.length>1&&(t[0]=`[${t[0]}]`),t.join(" ")}}};const k=w;var C=k,x={name:"Notification",methods:{notify(e){b.$.publishNotification(e)},notifyWarning(e){this.notify({text:e,warning:!0})},notifyError(e){throw this.notify({text:e,error:!0}),e}}};const $=x;var T=$,D={name:"Screen",methods:{isMobile(){return window.matchMedia("only screen and (max-width: 768px)").matches},isTablet(){return!this.isMobile()&&window.matchMedia("only screen and (max-width: 1023px)").matches},isDesktop(){return window.matchMedia("only screen and (min-width: 1024px)").matches}}};const E=D;var _=E,M={name:"Text",methods:{capitalize(e){return e?.length?e.charAt(0).toUpperCase()+e.slice(1):e},prettify(e){return e.split("_").map((e=>this.capitalize(e))).join(" ")},indent(e,t=2){return e.split("\n").map((e=>`${" ".repeat(t)}${e}`)).join("\n")}}};const N=M;var O=N,j=(n(560),{name:"Types",methods:{parseBoolean(e){return"string"===typeof e?(e=e.toLowerCase(),"true"===e||"false"!==e&&!!parseInt(e)):!!e},convertSize(e){"string"===typeof e&&(e=parseInt(e));let t=null;const n=["B","KB","MB","GB","TB"];return n.forEach(((i,s)=>{e<=1024&&null==t?t=i:e>1024&&(s===n.length-1?t=i:e/=1024)})),`${e.toFixed(2)} ${t}`},convertTime(e){const t={},n=[];if(e=parseFloat(e),t.d=Math.round(e/86400),t.h=Math.round(e/3600-24*t.d),t.m=Math.round(e/60-(24*t.d+60*t.h)),t.s=Math.round(e-(24*t.d+3600*t.h+60*t.m),1),parseInt(t.d)){let e=t.d+" day";t.d>1&&(e+="s"),n.push(e)}if(parseInt(t.h)){let e=t.h+" hour";t.h>1&&(e+="s"),n.push(e)}if(parseInt(t.m)){let e=t.m+" minute";t.m>1&&(e+="s"),n.push(e)}let i=t.s+" second";return t.s>1&&(i+="s"),n.push(i),n.join(" ")},objectsEqual(e,t){if("object"!==typeof e||"object"!==typeof t)return!1;if(null==e||null==t)return null==e&&null==t;for(const n of Object.keys(e||{}))switch(typeof e[n]){case"object":if(!this.objectsEqual(e[n],t[n]))return!1;break;case"function":if(e[n].toString()!=t[n]?.toString())return!1;break;default:if(e[n]!=t[n])return!1;break}for(const n of Object.keys(t||{}))if(null==e[n]&&null!=t[n])return!1;return!0},round(e,t){return Number(Math.round(e+"e"+t)+"e-"+t)}}});const S=j;var A=S,I={name:"Url",methods:{parseUrlFragment(){return window.location.hash.replace(/^#/,"").replace(/\?.*/,"")},getUrlArgs(){const e=window.location.hash.split("?").slice(1);return e.length?e[0].split(/[&;]/).reduce(((e,t)=>{const n=t.split("=");return n[0]?.length&&(e[n[0]]=decodeURIComponent(n[1])),e}),{}):{}},setUrlArgs(e){const t=this.getUrlArgs();e=Object.entries(e).reduce(((e,[n,i])=>(null!=i?e[n]=i:null!=t[n]&&delete t[n],e)),{}),e={...t,...e};let n=`${window.location.pathname}#${this.parseUrlFragment()}`;Object.keys(e).length&&(n+=`?${this.fragmentFromArgs(e)}`),window.location.href=n},encodeValue(e){return e?.length&&"null"!==e&&"undefined"!==e?e.match(/%[0-9A-F]{2}/i)?e:encodeURIComponent(e):""},fragmentFromArgs(e){return Object.entries(e).filter((([e,t])=>this.encodeValue(e)?.length&&this.encodeValue(t)?.length)).map((([e,t])=>`${this.encodeValue(e)}=${this.encodeValue(t)}`)).join("&")}}};const z=I;var P=z,q={name:"Utils",mixins:[a,l,h,m,y,T,C,_,O,A,P]};const V=q;var W=V},3493:function(e,t,n){n.d(t,{Z:function(){return b}});var i=n(6252),s=n(3577);const o=e=>((0,i.dD)("data-v-09bd997a"),e=e(),(0,i.Cn)(),e),a=["id"],r={key:0,class:"header"},c=["textContent"],l=o((()=>(0,i._)("i",{class:"fas fa-xmark"},null,-1))),d=[l],u={class:"body"};function h(e,t,n,o,l,h){return(0,i.wg)(),(0,i.iD)("div",{class:(0,s.C_)(["modal-container fade-in",{hidden:!l.isVisible}]),id:n.id,style:(0,s.j5)({"--z-index":h.zIndex}),onClick:t[3]||(t[3]=(...e)=>h.close&&h.close(...e))},[(0,i._)("div",{class:(0,s.C_)(["modal",e.$attrs.class])},[(0,i._)("div",{class:"content",style:(0,s.j5)({"--width":n.width,"--height":n.height}),onClick:t[2]||(t[2]=e=>e.stopPropagation())},[n.title?((0,i.wg)(),(0,i.iD)("div",r,[n.title?((0,i.wg)(),(0,i.iD)("div",{key:0,class:"title",textContent:(0,s.zw)(n.title)},null,8,c)):(0,i.kq)("",!0),(0,i._)("button",{title:"Close",alt:"Close",onClick:t[0]||(t[0]=(...e)=>h.close&&h.close(...e))},d)])):(0,i.kq)("",!0),(0,i._)("div",u,[(0,i.WI)(e.$slots,"default",{onModalClose:t[1]||(t[1]=(...e)=>h.close&&h.close(...e))},void 0,!0)])],4)],2)],14,a)}n(560);var f={name:"Modal",emits:["close","open"],props:{id:{type:String},title:{type:String},width:{type:[Number,String]},height:{type:[Number,String]},visible:{type:Boolean,default:!1},timeout:{type:[Number,String]},level:{type:Number,default:1}},data(){return{timeoutId:void 0,prevVisible:this.visible,isVisible:this.visible}},computed:{zIndex(){return 500+this.level}},methods:{close(){this.prevVisible=this.isVisible,this.isVisible=!1},hide(){this.close()},show(){this.prevVisible=this.isVisible,this.isVisible=!0},toggle(){this.isVisible?this.close():this.show()},onKeyUp(e){e.stopPropagation(),"Escape"===e.key&&this.close()}},mounted(){const e=this,t=t=>{t?e.$emit("open"):e.$emit("close"),e.isVisible=t};document.body.addEventListener("keyup",this.onKeyUp),this.$watch((()=>this.visible),t),this.$watch((()=>this.isVisible),t)},unmounted(){document.body.removeEventListener("keyup",this.onKeyUp)},updated(){if(this.prevVisible=this.isVisible,this.isVisible){let e=parseInt(getComputedStyle(this.$el).zIndex),t=[];for(const n of document.querySelectorAll(".modal-container:not(.hidden)")){const i=parseInt(getComputedStyle(n).zIndex);i>e?(e=i,t=[n]):i===e&&t.push(n)}(t.indexOf(this.$el)<0||t.length>1)&&(this.$el.style.zIndex=e+1)}if(this.isVisible&&this.timeout&&!this.timeoutId){const e=e=>()=>{e.close(),e.timeoutId=void 0};this.timeoutId=setTimeout(e(this),0+this.timeout)}}},p=n(3744);const m=(0,p.Z)(f,[["render",h],["__scopeId","data-v-09bd997a"]]);var b=m},7833:function(e,t,n){n.d(t,{Z:function(){return m}});var i=n(6252),s=n(9963),o=n(3577);const a=e=>((0,i.dD)("data-v-06d2f237"),e=e(),(0,i.Cn)(),e),r={class:"dialog-content"},c=a((()=>(0,i._)("i",{class:"fas fa-check"},null,-1))),l=a((()=>(0,i._)("i",{class:"fas fa-xmark"},null,-1)));function d(e,t,n,a,d,u){const h=(0,i.up)("Modal");return(0,i.wg)(),(0,i.j4)(h,{ref:"modal",title:n.title,onClose:u.close},{default:(0,i.w5)((()=>[(0,i._)("div",r,[(0,i.WI)(e.$slots,"default",{},void 0,!0)]),(0,i._)("form",{class:"buttons",onSubmit:t[4]||(t[4]=(0,s.iM)(((...e)=>u.onConfirm&&u.onConfirm(...e)),["prevent"]))},[(0,i._)("button",{type:"submit",class:"ok-btn",onClick:t[0]||(t[0]=(...e)=>u.onConfirm&&u.onConfirm(...e)),onTouch:t[1]||(t[1]=(...e)=>u.onConfirm&&u.onConfirm(...e))},[c,(0,i.Uk)("   "+(0,o.zw)(n.confirmText),1)],32),(0,i._)("button",{type:"button",class:"cancel-btn",onClick:t[2]||(t[2]=(...e)=>u.close&&u.close(...e)),onTouch:t[3]||(t[3]=(...e)=>u.close&&u.close(...e))},[l,(0,i.Uk)("   "+(0,o.zw)(n.cancelText),1)],32)],32)])),_:3},8,["title","onClose"])}var u=n(3493),h={emits:["input","click","close","touch"],components:{Modal:u.Z},props:{title:{type:String},confirmText:{type:String,default:"OK"},cancelText:{type:String,default:"Cancel"}},methods:{onConfirm(){this.$emit("input"),this.close()},open(){this.$refs.modal.show()},close(){this.$refs.modal.hide(),this.$emit("close")},show(){this.open()},hide(){this.close()}}},f=n(3744);const p=(0,f.Z)(h,[["render",d],["__scopeId","data-v-06d2f237"]]);var m=p}},t={};function n(i){var s=t[i];if(void 0!==s)return s.exports;var o=t[i]={exports:{}};return e[i].call(o.exports,o,o.exports,n),o.exports}n.m=e,function(){var e=[];n.O=function(t,i,s,o){if(!i){var a=1/0;for(d=0;d<e.length;d++){i=e[d][0],s=e[d][1],o=e[d][2];for(var r=!0,c=0;c<i.length;c++)(!1&o||a>=o)&&Object.keys(n.O).every((function(e){return n.O[e](i[c])}))?i.splice(c--,1):(r=!1,o<a&&(a=o));if(r){e.splice(d--,1);var l=s();void 0!==l&&(t=l)}}return t}o=o||0;for(var d=e.length;d>0&&e[d-1][2]>o;d--)e[d]=e[d-1];e[d]=[i,s,o]}}(),function(){n.n=function(e){var t=e&&e.__esModule?function(){return e["default"]}:function(){return e};return n.d(t,{a:t}),t}}(),function(){var e,t=Object.getPrototypeOf?function(e){return Object.getPrototypeOf(e)}:function(e){return e.__proto__};n.t=function(i,s){if(1&s&&(i=this(i)),8&s)return i;if("object"===typeof i&&i){if(4&s&&i.__esModule)return i;if(16&s&&"function"===typeof i.then)return i}var o=Object.create(null);n.r(o);var a={};e=e||[null,t({}),t([]),t(t)];for(var r=2&s&&i;"object"==typeof r&&!~e.indexOf(r);r=t(r))Object.getOwnPropertyNames(r).forEach((function(e){a[e]=function(){return i[e]}}));return a["default"]=function(){return i},n.d(o,a),o}}(),function(){n.d=function(e,t){for(var i in t)n.o(t,i)&&!n.o(e,i)&&Object.defineProperty(e,i,{enumerable:!0,get:t[i]})}}(),function(){n.f={},n.e=function(e){return Promise.all(Object.keys(n.f).reduce((function(t,i){return n.f[i](e,t),t}),[]))}}(),function(){n.u=function(e){return"static/js/"+({685:"register",2245:"notfound",4535:"login",7401:"panel",9966:"dashboard",9975:"plugin"}[e]||e)+"."+{34:"4c59fb03",58:"e14719bf",65:"ae7df477",169:"92c1a438",182:"0d7f4276",281:"0844207b",288:"ae1aea67",446:"cdd8637e",472:"1405415c",667:"3adea503",669:"67b2777b",685:"64e266ad",729:"81683ae6",735:"09e06f2a",746:"9a199f8f",813:"3ec855c4",844:"1cd89eec",906:"38a51fd1",980:"ee52bc55",984:"50a15617",1088:"f184400f",1259:"04c161c9",1327:"a10148a0",1391:"a76844c2",1449:"a5b4b2d2",1485:"501472f0",1512:"b686fb87",1558:"6fb75764",1706:"1a5248ba",1807:"564d1fef",1931:"fb0bd778",1949:"aa522c80",2018:"797df628",2106:"50dde272",2140:"d72a32d8",2154:"81668bf2",2183:"f8766c50",2200:"a7bc2894",2217:"d60fbb58",2245:"46477842",2460:"2a8400ba",2577:"f8b97d09",2582:"737d98fa",2614:"d8f2af9e",2732:"2b76d899",2844:"288f7727",2853:"99de82eb",2892:"96883d80",2893:"c9d72a7c",2924:"46a45250",2951:"82ed7dd0",2976:"e3dbc1e6",2992:"efd583f8",3033:"0d3aca76",3083:"b7c37603",3211:"542ae3e8",3322:"dadc23cc",3368:"8c968129",3369:"cb38d432",3393:"aeccb0ec",3400:"6966f10e",3518:"b56228c9",3559:"61ebd182",3732:"d6584e8e",3826:"cc264dd1",3835:"2db962db",3862:"0ca0e08c",3924:"0fd0a3c0",4053:"3890f446",4084:"5484e219",4109:"9ac9490e",4364:"771a5068",4535:"98ae4df8",4619:"b038c54a",4765:"cd86a538",4790:"7514123b",5197:"1a8603ef",5207:"7f241e21",5285:"4efb90e2",5329:"1dc4e553",5505:"35fbb782",5638:"d0047a11",5906:"5eaf69b5",5933:"e31ea3c0",6016:"ce3c3d44",6096:"bb407c5d",6148:"6a799072",6217:"e038c85c",6281:"38bbe6a9",6324:"93ea59d2",6362:"4870392f",6429:"20981cdf",6523:"426200f5",6561:"fc5ef77b",6640:"49b4564c",7089:"8779e12e",7381:"16a4edaa",7401:"9affcb8a",7528:"e54955c4",7590:"be3564f1",7651:"e7da8dba",7819:"5b29d1a3",7841:"580c6097",7878:"cb30e975",7880:"11b2f479",8069:"51c1e8b1",8179:"31c08ee9",8224:"fd608bb1",8391:"c04e1c3a",8498:"e34e99e5",8590:"034c423a",8621:"edd395ad",8752:"5e3dcc20",8769:"52fe04f5",8784:"5892bf2a",8825:"f5386513",8895:"c5e5490a",8930:"5354086d",8989:"d29a4bdb",9091:"b9371c68",9092:"89f920f0",9211:"e190626a",9334:"043959f5",9381:"a729807d",9461:"1b6014d3",9472:"8ac332bd",9549:"11496765",9751:"9e425e19",9962:"76f7d059",9966:"3b1ddc55",9975:"fc4b329b"}[e]+".js"}}(),function(){n.miniCssF=function(e){return"static/css/"+({7401:"panel",9966:"dashboard",9975:"plugin"}[e]||e)+"."+{34:"111a0e1a",58:"ecf614b3",65:"712466ff",169:"4e61bddf",182:"76b6eb09",281:"b8d8c407",288:"ceaf4d40",446:"ced514f5",472:"9c3bb868",669:"dd1b6ede",729:"5b54aac4",735:"93ff4770",746:"215dc404",906:"0c794836",980:"96973824",984:"04a4e901",1259:"705b87de",1327:"a8aa3d69",1391:"3a28e845",1449:"48f369df",1485:"ec7d392e",1558:"e4c74cc7",1706:"0cce53c8",1807:"414ba229",1931:"576454a1",1949:"09946541",2018:"8146b7c4",2140:"ccb2903f",2154:"9e4d2b2d",2217:"3d5833a8",2460:"c47d3d8a",2577:"52c4ebcb",2582:"0d7f9f2c",2844:"31199f56",2892:"0d765211",2893:"9ed78d28",2924:"23b041bd",2976:"0e5bc2d3",2992:"07a12488",3033:"1471fa39",3211:"ebc6e651",3368:"545f822b",3369:"8baddf78",3393:"eca14a3e",3559:"84280be4",3826:"6a236247",3835:"9eceb93e",3924:"548d44ae",4084:"0a0db151",4109:"e6d6b3d3",4364:"502178be",4790:"3b639ae0",5197:"a543b091",5207:"e08afd93",5285:"faa6ed68",5329:"3bb336f9",5638:"245c2ace",5906:"832a3a02",5933:"949d7b2b",6016:"558de04b",6096:"a3036d52",6217:"54339076",6281:"cdb5d498",6324:"0166f2db",6429:"79156821",6523:"9f1785cc",6561:"93704195",7401:"2a411b59",7528:"258d2865",7590:"db11c095",7651:"a7141db8",7841:"634d37da",7878:"ff3f31c5",7880:"bec7de73",8069:"6bdb62a5",8179:"cf2ba7d1",8224:"f72887fc",8391:"af187453",8498:"194ed9cc",8590:"88d3487c",8621:"dd386ad4",8769:"212a4f94",8825:"596c01e1",8989:"fd366c78",9092:"5de40234",9211:"c21e860e",9381:"b88ad779",9461:"e2d5774b",9549:"c4059cb5",9751:"f1de86a4",9962:"b2a51ef8",9966:"ce0fe60f",9975:"7646c315"}[e]+".css"}}(),function(){n.g=function(){if("object"===typeof globalThis)return globalThis;try{return this||new Function("return this")()}catch(e){if("object"===typeof window)return window}}()}(),function(){n.o=function(e,t){return Object.prototype.hasOwnProperty.call(e,t)}}(),function(){var e={},t="platypush:";n.l=function(i,s,o,a){if(e[i])e[i].push(s);else{var r,c;if(void 0!==o)for(var l=document.getElementsByTagName("script"),d=0;d<l.length;d++){var u=l[d];if(u.getAttribute("src")==i||u.getAttribute("data-webpack")==t+o){r=u;break}}r||(c=!0,r=document.createElement("script"),r.charset="utf-8",r.timeout=120,n.nc&&r.setAttribute("nonce",n.nc),r.setAttribute("data-webpack",t+o),r.src=i),e[i]=[s];var h=function(t,n){r.onerror=r.onload=null,clearTimeout(f);var s=e[i];if(delete e[i],r.parentNode&&r.parentNode.removeChild(r),s&&s.forEach((function(e){return e(n)})),t)return t(n)},f=setTimeout(h.bind(null,void 0,{type:"timeout",target:r}),12e4);r.onerror=h.bind(null,r.onerror),r.onload=h.bind(null,r.onload),c&&document.head.appendChild(r)}}}(),function(){n.r=function(e){"undefined"!==typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})}}(),function(){n.p="/"}(),function(){if("undefined"!==typeof document){var e=function(e,t,n,i,s){var o=document.createElement("link");o.rel="stylesheet",o.type="text/css";var a=function(n){if(o.onerror=o.onload=null,"load"===n.type)i();else{var a=n&&("load"===n.type?"missing":n.type),r=n&&n.target&&n.target.href||t,c=new Error("Loading CSS chunk "+e+" failed.\n("+r+")");c.code="CSS_CHUNK_LOAD_FAILED",c.type=a,c.request=r,o.parentNode&&o.parentNode.removeChild(o),s(c)}};return o.onerror=o.onload=a,o.href=t,n?n.parentNode.insertBefore(o,n.nextSibling):document.head.appendChild(o),o},t=function(e,t){for(var n=document.getElementsByTagName("link"),i=0;i<n.length;i++){var s=n[i],o=s.getAttribute("data-href")||s.getAttribute("href");if("stylesheet"===s.rel&&(o===e||o===t))return s}var a=document.getElementsByTagName("style");for(i=0;i<a.length;i++){s=a[i],o=s.getAttribute("data-href");if(o===e||o===t)return s}},i=function(i){return new Promise((function(s,o){var a=n.miniCssF(i),r=n.p+a;if(t(a,r))return s();e(i,r,null,s,o)}))},s={2143:0};n.f.miniCss=function(e,t){var n={34:1,58:1,65:1,169:1,182:1,281:1,288:1,446:1,472:1,669:1,729:1,735:1,746:1,906:1,980:1,984:1,1259:1,1327:1,1391:1,1449:1,1485:1,1558:1,1706:1,1807:1,1931:1,1949:1,2018:1,2140:1,2154:1,2217:1,2460:1,2577:1,2582:1,2844:1,2892:1,2893:1,2924:1,2976:1,2992:1,3033:1,3211:1,3368:1,3369:1,3393:1,3559:1,3826:1,3835:1,3924:1,4084:1,4109:1,4364:1,4790:1,5197:1,5207:1,5285:1,5329:1,5638:1,5906:1,5933:1,6016:1,6096:1,6217:1,6281:1,6324:1,6429:1,6523:1,6561:1,7401:1,7528:1,7590:1,7651:1,7841:1,7878:1,7880:1,8069:1,8179:1,8224:1,8391:1,8498:1,8590:1,8621:1,8769:1,8825:1,8989:1,9092:1,9211:1,9381:1,9461:1,9549:1,9751:1,9962:1,9966:1,9975:1};s[e]?t.push(s[e]):0!==s[e]&&n[e]&&t.push(s[e]=i(e).then((function(){s[e]=0}),(function(t){throw delete s[e],t})))}}}(),function(){var e={2143:0};n.f.j=function(t,i){var s=n.o(e,t)?e[t]:void 0;if(0!==s)if(s)i.push(s[2]);else if(/^(1(327|391|558|82|931)|2((15|84|92)4|577|992)|4(109|364|790)|5(8|906|933)|6(016|096|217|281|561|69)|8(069|590|989)|3393|3826|7651|906|9549)$/.test(t))e[t]=0;else{var o=new Promise((function(n,i){s=e[t]=[n,i]}));i.push(s[2]=o);var a=n.p+n.u(t),r=new Error,c=function(i){if(n.o(e,t)&&(s=e[t],0!==s&&(e[t]=void 0),s)){var o=i&&("load"===i.type?"missing":i.type),a=i&&i.target&&i.target.src;r.message="Loading chunk "+t+" failed.\n("+o+": "+a+")",r.name="ChunkLoadError",r.type=o,r.request=a,s[1](r)}};n.l(a,c,"chunk-"+t,t)}},n.O.j=function(t){return 0===e[t]};var t=function(t,i){var s,o,a=i[0],r=i[1],c=i[2],l=0;if(a.some((function(t){return 0!==e[t]}))){for(s in r)n.o(r,s)&&(n.m[s]=r[s]);if(c)var d=c(n)}for(t&&t(i);l<a.length;l++)o=a[l],n.o(e,o)&&e[o]&&e[o][0](),e[o]=0;return n.O(d)},i=self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[];i.forEach(t.bind(null,0)),i.push=t.bind(null,i.push.bind(i))}();var i=n.O(void 0,[4998],(function(){return n(2520)}));i=n.O(i)})();
//# sourceMappingURL=app.e68dae80.js.map