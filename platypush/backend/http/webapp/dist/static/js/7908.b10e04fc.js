(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[7908],{7907:function(){},9667:function(e,t,n){"use strict";n.d(t,{A:function(){return h}});var s=n(641),i=n(3751);const l=e=>((0,s.Qi)("data-v-0bc64e95"),e=e(),(0,s.jt)(),e),a=l((()=>(0,s.Lk)("i",{class:"fas fa-clipboard"},null,-1))),o=[a];function r(e,t,n,l,a,r){return(0,s.uX)(),(0,s.CE)("button",{class:"copy-button",ref:"copyButton",title:"Copy to clipboard",onClick:t[0]||(t[0]=(0,i.D$)(((...e)=>r.copy&&r.copy(...e)),["prevent"])),onInput:t[1]||(t[1]=(0,i.D$)(((...e)=>r.copy&&r.copy(...e)),["prevent"]))},o,544)}var c=n(2002),u={name:"CopyButton",emits:["input","click"],mixins:[c.A],props:{text:{type:String}},methods:{async copy(e){this.text?.length&&await this.copyToClipboard(this.text),this.$emit(e.type,e)}}},g=n(6262);const d=(0,g.A)(u,[["render",r],["__scopeId","data-v-0bc64e95"]]);var h=d},2573:function(e,t,n){"use strict";n.d(t,{A:function(){return d}});var s=n(641),i=n(33);const l=["href"],a=["src","alt","title"],o=["src","alt","title"];function r(e,t,n,r,c,u){return(0,s.uX)(),(0,s.CE)("div",{class:"extension-icon",style:(0,i.Tr)({width:`${n.size}`,height:`${n.size}`})},[n.withDocsLink?((0,s.uX)(),(0,s.CE)("a",{key:0,href:u.docsUrl,target:"_blank"},[(0,s.Lk)("img",{src:u.iconUrl,alt:u.extensionName,title:u.extensionName},null,8,a)],8,l)):((0,s.uX)(),(0,s.CE)("img",{key:1,src:u.iconUrl,alt:u.extensionName,title:u.extensionName},null,8,o))],4)}var c={props:{name:{type:String,required:!0},size:{type:String,default:"1.75em"},withDocsLink:{type:Boolean,default:!1}},computed:{iconUrl(){return`https://static.platypush.tech/icons/${this.extensionName}-64.png`},extensionType(){return"backend"==this.name.split(".")[0]?"backend":"plugin"},extensionName(){const e=this.name.split(".");return e.length<1?this.name:("backend"==e[0]&&e.shift(),e.join("."))},docsUrl(){return`https://docs.platypush.tech/platypush/${this.extensionType}s/${this.extensionName}.html`}}},u=n(6262);const g=(0,u.A)(c,[["render",r],["__scopeId","data-v-0353c248"]]);var d=g},7908:function(e,t,n){"use strict";n.r(t),n.d(t,{default:function(){return Xe}});var s=n(641),i=n(3751),l=n(33);const a={class:"row plugin extensions-container"},o={class:"filter-container"},r=["disabled"],c={class:"items"},u={key:0,class:"extension"},g=["data-name","onClick"],d={class:"name"},h={key:0,class:"enabled icon",title:"Enabled"},p={key:0,class:"enabled icon fas fa-circle-check"},f={key:0,class:"extension-body-container until tablet"},m={key:0,class:"extension-body-container from desktop"};function x(e,t,n,x,k,b){const C=(0,s.g2)("Loading"),y=(0,s.g2)("ExtensionIcon"),L=(0,s.g2)("Extension");return(0,s.uX)(),(0,s.CE)("div",a,[k.loading?((0,s.uX)(),(0,s.Wv)(C,{key:0})):(0,s.Q3)("",!0),(0,s.Lk)("header",null,[(0,s.Lk)("div",o,[(0,s.bo)((0,s.Lk)("input",{type:"text",ref:"filter",placeholder:"Extension name","onUpdate:modelValue":t[0]||(t[0]=e=>k.filter=e),disabled:k.loading},null,8,r),[[i.Jo,k.filter]])])]),(0,s.Lk)("main",null,[(0,s.Lk)("div",c,[((0,s.uX)(!0),(0,s.CE)(s.FK,null,(0,s.pI)(b.extensionNames,(e=>((0,s.uX)(),(0,s.CE)("div",{class:"extension-container",key:e},[b.matchesFilter(e)?((0,s.uX)(),(0,s.CE)("div",u,[(0,s.Lk)("div",{class:(0,l.C4)(["item",{selected:e===k.selectedExtension}]),"data-name":e,onClick:t=>b.onClick(e,!1)},[(0,s.bF)(y,{name:e,size:"1.75em"},null,8,["name"]),(0,s.Lk)("span",d,(0,l.v_)(b.extensions[e].name),1),b.enabledExtensions[e]?((0,s.uX)(),(0,s.CE)("span",h,[b.enabledExtensions[e]?((0,s.uX)(),(0,s.CE)("i",p)):(0,s.Q3)("",!0)])):(0,s.Q3)("",!0)],10,g),k.selectedExtension&&e===k.selectedExtension?((0,s.uX)(),(0,s.CE)("div",f,[(0,s.bF)(L,{extension:b.extensions[k.selectedExtension],config:b.enabledExtensions[k.selectedExtension],"config-file":k.configFile},null,8,["extension","config","config-file"])])):(0,s.Q3)("",!0)])):(0,s.Q3)("",!0)])))),128))]),k.selectedExtension?((0,s.uX)(),(0,s.CE)("div",m,[(0,s.bF)(L,{extension:b.extensions[k.selectedExtension],config:b.enabledExtensions[k.selectedExtension],"config-file":k.configFile},null,8,["extension","config","config-file"])])):(0,s.Q3)("",!0)])])}const k=e=>((0,s.Qi)("data-v-3fa6b036"),e=e(),(0,s.jt)(),e),b={class:"extension"},C=k((()=>(0,s.Lk)("span",{class:"from tablet"},"Documentation",-1))),y=k((()=>(0,s.Lk)("span",{class:"from tablet"},"Install",-1))),L=k((()=>(0,s.Lk)("span",{class:"from tablet"},"Configuration",-1))),v={class:"extension-body"};function E(e,t,n,i,l,a){const o=(0,s.g2)("Tab"),r=(0,s.g2)("Tabs"),c=(0,s.g2)("Doc"),u=(0,s.g2)("Config"),g=(0,s.g2)("Install");return(0,s.uX)(),(0,s.CE)("div",b,[(0,s.Lk)("header",null,[(0,s.bF)(r,null,{default:(0,s.k6)((()=>[(0,s.bF)(o,{selected:"doc"===l.selectedTab,"icon-class":"fas fa-book",onInput:t[0]||(t[0]=e=>l.selectedTab="doc")},{default:(0,s.k6)((()=>[C])),_:1},8,["selected"]),(0,s.bF)(o,{selected:"install"===l.selectedTab,"icon-class":"fas fa-download",onInput:t[1]||(t[1]=e=>l.selectedTab="install")},{default:(0,s.k6)((()=>[y])),_:1},8,["selected"]),(0,s.bF)(o,{selected:"config"===l.selectedTab,"icon-class":"fas fa-square-check",onInput:t[2]||(t[2]=e=>l.selectedTab="config")},{default:(0,s.k6)((()=>[L])),_:1},8,["selected"])])),_:1})]),(0,s.Lk)("div",v,["doc"===l.selectedTab?((0,s.uX)(),(0,s.Wv)(c,{key:0,extension:n.extension},null,8,["extension"])):"config"===l.selectedTab?((0,s.uX)(),(0,s.Wv)(u,{key:1,extension:n.extension,config:n.config,"config-file":n.configFile},null,8,["extension","config","config-file"])):"install"===l.selectedTab?((0,s.uX)(),(0,s.Wv)(g,{key:2,extension:n.extension},null,8,["extension"])):(0,s.Q3)("",!0)])])}var _=n(5054),w=n(3556);const $={key:0,class:"config-container current"},X=["innerHTML"],I=["innerHTML"];function A(e,t,n,i,a,o){const r=(0,s.g2)("CopyButton");return(0,s.uX)(),(0,s.CE)(s.FK,null,[o.highlightedCurrentConfig?((0,s.uX)(),(0,s.CE)("div",$,[(0,s.bF)(r,{text:a.curYamlConfig},null,8,["text"]),(0,s.Lk)("pre",null,[(0,s.Lk)("code",{class:"config-snippet",innerHTML:o.highlightedCurrentConfig},null,8,X)])])):(0,s.Q3)("",!0),(0,s.Lk)("div",{class:(0,l.C4)(["config-container snippet",{fullscreen:!o.highlightedCurrentConfig}])},[(0,s.bF)(r,{text:n.extension.config_snippet},null,8,["text"]),(0,s.Lk)("pre",null,[(0,s.Lk)("code",{class:"config-snippet",innerHTML:o.highlightedConfigSnippet},null,8,I)])],2)],64)}n(1545);var F=n(9878),T=n(9667),j=n(2002),O={name:"Extension",mixins:[j.A],components:{CopyButton:T.A},props:{extension:{type:Object,required:!0},config:{type:Object},configFile:{type:String}},data(){return{curYamlConfig:null}},computed:{highlightedConfigSnippet(){return F.A.highlight(`# Configuration template. You can add it to ${this.configFile}\n`+this.extension.config_snippet,{language:"yaml"}).value.trim()},highlightedCurrentConfig(){return this.curYamlConfig?F.A.highlight("# Currently loaded configuration\n"+this.curYamlConfig,{language:"yaml"}).value.trim():null}},methods:{async loadCurrentConfig(){this.config?this.curYamlConfig=await this.request("utils.to_yaml",{obj:{[this.extension.name]:this.config}}):this.curYamlConfig=null}},mounted(){this.loadCurrentConfig(),this.$watch("config",this.loadCurrentConfig)}},D=n(6262);const q=(0,D.A)(O,[["render",A],["__scopeId","data-v-325a3576"]]);var Q=q;const W=e=>((0,s.Qi)("data-v-49986d05"),e=e(),(0,s.jt)(),e),N={class:"doc"},R=["href"],B=["textContent"],S=["innerHTML"],U={key:0,class:"actions"},H=W((()=>(0,s.Lk)("h3",null,[(0,s.Lk)("i",{class:"icon fas fa-play"}),(0,s.eW)("   Actions ")],-1))),M=["href"],P={key:1,class:"events"},z=W((()=>(0,s.Lk)("h3",null,[(0,s.Lk)("i",{class:"icon fas fa-flag"}),(0,s.eW)("   Events ")],-1))),Y=["href"];function K(e,t,n,i,a,o){const r=(0,s.g2)("ExtensionIcon");return(0,s.uX)(),(0,s.CE)("section",N,[(0,s.Lk)("header",null,[(0,s.Lk)("h2",null,[(0,s.Lk)("a",{class:"title",href:n.extension.doc_url,target:"_blank"},[(0,s.bF)(r,{name:n.extension.name,size:"2em","with-docs-link":""},null,8,["name"]),(0,s.Lk)("span",{class:"name",textContent:(0,l.v_)(n.extension.name)},null,8,B)],8,R)])]),a.doc?((0,s.uX)(),(0,s.CE)("article",{key:0,onClick:t[0]||(t[0]=(...e)=>o.onDocClick&&o.onDocClick(...e))},[(0,s.Lk)("div",{class:"doc-content",innerHTML:a.doc},null,8,S),Object.keys(n.extension.actions||{}).length>0?((0,s.uX)(),(0,s.CE)("div",U,[H,(0,s.Lk)("ul",null,[((0,s.uX)(!0),(0,s.CE)(s.FK,null,(0,s.pI)(o.actionNames,(e=>((0,s.uX)(),(0,s.CE)("li",{class:"action",key:e},[(0,s.Lk)("a",{href:`/#execute?action=${n.extension.name}.${e}`},(0,l.v_)(n.extension.name)+"."+(0,l.v_)(e),9,M)])))),128))])])):(0,s.Q3)("",!0),Object.keys(n.extension.events||{}).length>0?((0,s.uX)(),(0,s.CE)("div",P,[z,(0,s.Lk)("ul",null,[((0,s.uX)(!0),(0,s.CE)(s.FK,null,(0,s.pI)(o.eventNames,(e=>((0,s.uX)(),(0,s.CE)("li",{class:"event",key:e},[(0,s.Lk)("a",{href:n.extension.events[e].doc_url,target:"_blank"},(0,l.v_)(e),9,Y)])))),128))])])):(0,s.Q3)("",!0)])):(0,s.Q3)("",!0)])}var J=n(2573),V=n(2537),G={name:"Doc",mixins:[j.A],components:{ExtensionIcon:J.A},props:{extension:{type:Object,required:!0}},data(){return{doc:null,localPageRegex:new RegExp("^/?#.*$")}},computed:{actionNames(){return Object.keys(this.extension.actions).sort()},eventNames(){return Object.keys(this.extension.events).sort()}},methods:{async parseDoc(){return this.extension.doc?.length?await this.request("utils.rst_to_html",{text:this.extension.doc}):null},refreshDoc(){this.parseDoc().then((e=>this.doc=e))},onDocClick(e){if("a"!==e.target.tagName.toLowerCase())return!0;e.preventDefault();const t=e.target.getAttribute("href");if(!t)return!0;if(t.match(this.localPageRegex))return window.location.href=t,!0;const n=t.match(/^https:\/\/docs\.platypush\.tech\/platypush\/(plugins|backend)\/([\w.]+)\.html#?.*$/);if(!n)return e.preventDefault(),window.open(t,"_blank"),!0;let[s,i]=n.slice(1);"backend"===s&&(i=`backend.${i}`),V.j.emit("update:extension",i),e.preventDefault()}},mounted(){this.refreshDoc(),this.$watch("extension.doc",this.refreshDoc)}};const Z=(0,D.A)(G,[["render",K],["__scopeId","data-v-49986d05"]]);var ee=Z;const te=e=>((0,s.Qi)("data-v-8b2323ae"),e=e(),(0,s.jt)(),e),ne={class:"install-container"},se={class:"top"},ie=te((()=>(0,s.Lk)("header",null,[(0,s.Lk)("h2",null,"Dependencies")],-1))),le={class:"body"},ae={class:"container install-cmd-container"},oe=["innerHTML"],re={key:0,class:"buttons install-btn"},ce=["disabled"],ue=te((()=>(0,s.Lk)("i",{class:"fas fa-download"},null,-1))),ge={key:0,class:"bottom"},de=te((()=>(0,s.Lk)("header",null,[(0,s.Lk)("h2",null,"Output")],-1))),he={class:"body"},pe={class:"container install-output",ref:"installOutput"},fe=["textContent"],me={key:0,class:"loading-container"};function xe(e,t,n,i,a,o){const r=(0,s.g2)("CopyButton"),c=(0,s.g2)("Loading"),u=(0,s.g2)("RestartButton");return(0,s.uX)(),(0,s.CE)("div",ne,[(0,s.Lk)("section",se,[ie,(0,s.Lk)("div",le,[(0,s.Lk)("div",ae,[o.installCmd?((0,s.uX)(),(0,s.Wv)(r,{key:0,text:o.installCmd},null,8,["text"])):(0,s.Q3)("",!0),(0,s.Lk)("pre",null,[a.loading?((0,s.uX)(),(0,s.Wv)(c,{key:0})):((0,s.uX)(),(0,s.CE)("code",{key:1,innerHTML:o.highlightedInstallCmd},null,8,oe))])]),o.installCmd?((0,s.uX)(),(0,s.CE)("div",re,[a.installDone?((0,s.uX)(),(0,s.Wv)(u,{key:0})):(0,s.Q3)("",!0),(0,s.Lk)("button",{type:"button",class:"btn btn-default",disabled:a.installRunning,onClick:t[0]||(t[0]=(...e)=>o.installExtension&&o.installExtension(...e))},[ue,(0,s.eW)(" Install ")],8,ce)])):(0,s.Q3)("",!0)])]),a.installRunning||a.installOutput?((0,s.uX)(),(0,s.CE)("section",ge,[de,(0,s.Lk)("div",he,[(0,s.Lk)("div",pe,[(0,s.bF)(r,{text:a.installOutput},null,8,["text"]),(0,s.Lk)("pre",null,[(0,s.Lk)("code",{textContent:(0,l.v_)(a.installOutput)},null,8,fe),a.installRunning?((0,s.uX)(),(0,s.CE)("div",me,[(0,s.eW)("\n            "),(0,s.bF)(c),(0,s.eW)("\n          ")])):(0,s.Q3)("",!0)])],512)])])):(0,s.Q3)("",!0)])}n(7907);var ke=n(9828),be=n(1968),Ce={name:"Install",mixins:[j.A],emits:["install-start","install-end"],components:{CopyButton:T.A,Loading:ke.A,RestartButton:be.A},props:{extension:{type:Object,required:!0}},data(){return{installRunning:!1,installDone:!1,installOutput:null,installCmds:[],pendingCommands:0,error:null,loading:!1}},computed:{installCmd(){return this.installCmds.length?this.installCmds.join("\n").trim():null},highlightedInstallCmd(){return F.A.highlight(this.installCmd?this.installCmds.map((e=>`$ ${e}`)).join("\n").trim():"# No extra installation steps required",{language:"bash"}).value}},methods:{wsProcess(e){try{const t="https:"===window.location.protocol?"wss":"ws",n=`${t}://${location.host}${e}`,s=new WebSocket(n);s.onmessage=this.onMessage,s.onerror=this.onError,s.onclose=this.onClose}catch(t){this.notify({error:!0,title:"Websocket initialization error",text:t.toString()}),console.error("Websocket initialization error"),console.error(t),this.error=t,this.installRunning=!1}},onMessage(e){this.installOutput||(this.installOutput=""),this.installOutput+=e.data},onClose(){this.installRunning=!1,this.$emit("install-end",this.extension),this.error||(this.installDone=!0),this.notify({title:"Extension installed",html:`Extension <b>${this.extension.name}</b> installed successfully`,image:{iconClass:"fas fa-check"}})},onError(e){this.notify({error:!0,title:"Websocket error",text:e.toString()}),console.error("Websocket error"),console.error(e),this.error=e,this.installRunning=!1},installExtension(){if(!this.installCmd)return;this.error=null,this.installRunning=!0,this.installOutput="",this.$emit("install-start",this.extension);const e=this.installCmds.join(";\n");this.request("shell.exec",{cmd:e,ws:!0}).then((e=>{this.wsProcess(e.ws_path)})).catch((e=>{this.error=e,this.installRunning=!1,this.$emit("install-end",this.extension)}))},async refreshInstallCmds(){this.loading=!0;try{this.installCmds=await this.request("application.get_install_commands",{extension:this.extension.name})}finally{this.loading=!1}}},mounted(){this.refreshInstallCmds(),this.$watch("extension.name",(()=>{this.refreshInstallCmds()})),this.$watch("installOutput",(()=>{this.$nextTick((()=>{this.$refs.installOutput.focus(),this.$refs.installOutput.scrollTop=this.$refs.installOutput.scrollHeight}))}))}};const ye=(0,D.A)(Ce,[["render",xe],["__scopeId","data-v-8b2323ae"]]);var Le=ye,ve={name:"Extension",components:{Config:Q,Doc:ee,Install:Le,Tab:_.A,Tabs:w.A},props:{extension:{type:Object,required:!0},config:{type:Object},configFile:{type:String}},data(){return{selectedTab:"doc"}}};const Ee=(0,D.A)(ve,[["render",E],["__scopeId","data-v-3fa6b036"]]);var _e=Ee,we={name:"Extensions",mixins:[j.A],components:{Extension:_e,ExtensionIcon:J.A,Loading:ke.A},data(){return{loading:!1,plugins:{},backends:{},enabledPlugins:{},enabledBackends:{},filter:"",selectedExtension:null,configFile:null,config:{}}},computed:{extensions(){const e={};return Object.entries(this.plugins).forEach((([t,n])=>{e[t]={...n,name:t}})),Object.entries(this.backends).forEach((([t,n])=>{t=`backend.${t}`,e[t]={...n,name:t}})),e},enabledExtensions(){return[this.enabledPlugins,this.enabledBackends].reduce(((e,t)=>(Object.entries(t).forEach((([t,n])=>{e[t]=n})),e)),{})},extensionNames(){return Object.keys(this.extensions).sort()}},methods:{onClick(e,t=!0,n=!0){this.selectedExtension===e?this.selectedExtension=null:this.onInput(e,t,n)},onInput(e,t=!0,n=!0){t&&(this.filter=e);const s=e?.toLowerCase()?.trim();if(s?.length&&this.extensions[s]){this.selectedExtension=s,n&&this.setUrlArgs({extension:s});const e=this.$el.querySelector(`.extensions-container .item[data-name="${s}"]`);e&&e.scrollIntoView({behavior:"smooth"})}else this.selectedExtension=null,n&&this.setUrlArgs({})},matchesFilter(e){return!this.filter||e.includes(this.filter.toLowerCase())},async loadExtensions(){this.loading=!0;let[e,t]=[[],[]];try{[this.plugins,this.backends,e,t,this.config]=await Promise.all([this.request("inspect.get_all_plugins"),this.request("inspect.get_all_backends"),this.request("inspect.get_enabled_plugins"),this.request("inspect.get_enabled_backends"),this.request("inspect.get_config")])}finally{this.loading=!1}this.enabledPlugins=e.reduce(((e,t)=>(e[t]=this.config[t]||{},e)),{}),this.enabledBackends=t.reduce(((e,t)=>(t=`backend.${t}`,e[t]=this.config[t]||{},e)),{}),this.loadExtensionFromUrl(),this.$watch("$route.hash",(()=>this.loadExtensionFromUrl()))},async loadConfigFile(){this.configFile=await this.request("config.get_config_file")},loadExtensionFromUrl(){const e=this.getUrlArgs().extension;e&&this.$nextTick((()=>this.onInput(e,!1,!1)))}},mounted(){this.loadConfigFile(),this.loadExtensions(),V.j.on("update:extension",(e=>this.onInput(e,!1))),this.$nextTick((()=>this.$refs.filter.focus()))}};const $e=(0,D.A)(we,[["render",x],["__scopeId","data-v-74d75ec7"]]);var Xe=$e},3094:function(e,t,n){var s=n(8416);s.registerLanguage("xml",n(114)),s.registerLanguage("bash",n(8641)),s.registerLanguage("c",n(722)),s.registerLanguage("cpp",n(6570)),s.registerLanguage("csharp",n(7120)),s.registerLanguage("css",n(8612)),s.registerLanguage("markdown",n(602)),s.registerLanguage("diff",n(8596)),s.registerLanguage("ruby",n(5015)),s.registerLanguage("go",n(9777)),s.registerLanguage("graphql",n(7474)),s.registerLanguage("ini",n(1533)),s.registerLanguage("java",n(4895)),s.registerLanguage("javascript",n(6035)),s.registerLanguage("json",n(621)),s.registerLanguage("kotlin",n(2838)),s.registerLanguage("less",n(8330)),s.registerLanguage("lua",n(3873)),s.registerLanguage("makefile",n(7667)),s.registerLanguage("perl",n(946)),s.registerLanguage("objectivec",n(943)),s.registerLanguage("php",n(3111)),s.registerLanguage("php-template",n(1726)),s.registerLanguage("plaintext",n(9040)),s.registerLanguage("python",n(1117)),s.registerLanguage("python-repl",n(2664)),s.registerLanguage("r",n(8129)),s.registerLanguage("rust",n(5409)),s.registerLanguage("scss",n(1611)),s.registerLanguage("shell",n(8813)),s.registerLanguage("sql",n(315)),s.registerLanguage("swift",n(1496)),s.registerLanguage("yaml",n(5588)),s.registerLanguage("typescript",n(8640)),s.registerLanguage("vbnet",n(8928)),s.registerLanguage("wasm",n(9351)),s.HighlightJS=s,s.default=s,e.exports=s},1545:function(e,t,n){"use strict";n(3094)}}]);
//# sourceMappingURL=7908.b10e04fc.js.map