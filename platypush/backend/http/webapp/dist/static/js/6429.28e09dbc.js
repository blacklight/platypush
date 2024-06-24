"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[6429],{1065:function(e,t,s){s.d(t,{Z:function(){return l}});s(560);var a=s(8637),n={name:"Utils",mixins:[a.Z],computed:{audioExtensions(){return new Set(["3gp","aa","aac","aax","act","aiff","amr","ape","au","awb","dct","dss","dvf","flac","gsm","iklax","ivs","m4a","m4b","m4p","mmf","mp3","mpc","msv","nmf","nsf","ogg,","opus","ra,","raw","sln","tta","vox","wav","wma","wv","webm","8svx"])},videoExtensions(){return new Set(["webm","mkv","flv","flv","vob","ogv","ogg","drc","gif","gifv","mng","avi","mts","m2ts","mov","qt","wmv","yuv","rm","rmvb","asf","amv","mp4","m4p","m4v","mpg","mp2","mpeg","mpe","mpv","mpg","mpeg","m2v","m4v","svi","3gp","3g2","mxf","roq","nsv","flv","f4v","f4p","f4a","f4b"])},mediaExtensions(){return new Set([...this.videoExtensions,...this.audioExtensions])}},methods:{convertTime(e){e=parseFloat(e);const t={};t.h=""+parseInt(e/3600),t.m=""+parseInt(e/60-60*t.h),t.s=""+parseInt(e-(3600*t.h+60*t.m));for(const a of["m","s"])parseInt(t[a])<10&&(t[a]="0"+t[a]);const s=[];return parseInt(t.h)&&s.push(t.h),s.push(t.m,t.s),s.join(":")},async startStreaming(e,t,s=!1){let a=e,n=null;e instanceof Object?(a=e.url,n=e.subtitles):e={url:a};const r=await this.request(`${t}.start_streaming`,{media:a,subtitles:n,download:s});return{...e,...r}},async stopStreaming(e,t){await this.request(`${t}.stop_streaming`,{media_id:e})}}};const r=n;var l=r},6429:function(e,t,s){s.d(t,{Z:function(){return st}});var a=s(6252),n=s(3577);const r={class:"torrent-container"},l={class:"nav-container"};function i(e,t,s,i,o,d){const c=(0,a.up)("Info"),u=(0,a.up)("Modal"),p=(0,a.up)("Header"),v=(0,a.up)("Transfers"),f=(0,a.up)("Results"),m=(0,a.up)("Nav");return(0,a.wg)(),(0,a.iD)("div",r,[d.infoItem?((0,a.wg)(),(0,a.j4)(u,{key:0,title:"Torrent info",visible:null!==d.infoItem,onClose:t[0]||(t[0]=e=>o.infoIndex=null)},{default:(0,a.w5)((()=>[(0,a.Wm)(c,{torrent:d.infoItem},null,8,["torrent"])])),_:1},8,["visible"])):(0,a.kq)("",!0),(0,a._)("div",{class:(0,n.C_)(["header-container",{"with-nav":!o.navCollapsed}])},[(0,a.Wm)(p,{"with-nav":!o.navCollapsed,"selected-view":o.selectedView,loading:o.loading,onSearch:t[1]||(t[1]=e=>d.search(e)),onTorrentAdd:t[2]||(t[2]=e=>d.download(e)),onToggle:t[3]||(t[3]=e=>o.navCollapsed=!o.navCollapsed)},null,8,["with-nav","selected-view","loading"])],2),(0,a._)("main",null,[(0,a._)("div",{class:(0,n.C_)(["view-container",{"with-nav":!o.navCollapsed}])},["transfers"===o.selectedView?((0,a.wg)(),(0,a.j4)(v,{key:0,transfers:o.transfers,onPause:t[4]||(t[4]=e=>d.pause(e)),onResume:t[5]||(t[5]=e=>d.resume(e)),onRemove:t[6]||(t[6]=e=>d.remove(e))},null,8,["transfers"])):"search"===o.selectedView?((0,a.wg)(),(0,a.j4)(f,{key:1,results:o.results,onDownload:t[7]||(t[7]=e=>d.download(e)),onInfo:t[8]||(t[8]=e=>o.infoIndex=e),onNextPage:t[9]||(t[9]=e=>d.search(o.query,o.page+1))},null,8,["results"])):(0,a.kq)("",!0)],2),(0,a._)("div",l,[o.navCollapsed?(0,a.kq)("",!0):((0,a.wg)(),(0,a.j4)(m,{key:0,"selected-view":o.selectedView,onToggle:t[10]||(t[10]=e=>o.navCollapsed=!o.navCollapsed),onInput:t[11]||(t[11]=e=>o.selectedView=e)},null,8,["selected-view"]))])])])}const o=e=>((0,a.dD)("data-v-8eed74b0"),e=e(),(0,a.Cn)(),e),d={class:"info"},c={class:"row"},u=o((()=>(0,a._)("div",{class:"label"},"Title",-1))),p={class:"value"},v={class:"row"},f=o((()=>(0,a._)("div",{class:"label"},"URL",-1))),m={class:"value"},h=o((()=>(0,a._)("i",{class:"fas fa-up-right-from-square"},null,-1))),w=[h],g=o((()=>(0,a._)("i",{class:"fas fa-clipboard"},null,-1))),_=[g],y={class:"row"},b=o((()=>(0,a._)("div",{class:"label"},"Size",-1))),C={class:"value"},k={class:"row"},I=o((()=>(0,a._)("div",{class:"label"},"Seeders",-1))),x={class:"value"},T={class:"row"},D=o((()=>(0,a._)("div",{class:"label"},"Leechers",-1))),S={class:"value"},q={class:"row"},z=o((()=>(0,a._)("div",{class:"label"},"Uploaded",-1))),$={class:"value"},N={key:0,class:"row"},R=o((()=>(0,a._)("div",{class:"label"},"Description",-1))),Z={class:"value"},U={key:1,class:"row"},V=o((()=>(0,a._)("div",{class:"label"},"Year",-1))),E={class:"value"};function L(e,t,s,r,l,i){return(0,a.wg)(),(0,a.iD)("div",d,[(0,a._)("div",c,[u,(0,a._)("div",p,(0,n.zw)(s.torrent.title),1)]),(0,a._)("div",v,[f,(0,a._)("div",m,[(0,a._)("button",{title:"Open",onClick:t[0]||(t[0]=e=>i.openInNewTab(s.torrent.url))},w),(0,a._)("button",{title:"Copy",onClick:t[1]||(t[1]=t=>e.copyToClipboard(s.torrent.url))},_)])]),(0,a._)("div",y,[b,(0,a._)("div",C,(0,n.zw)(e.convertSize(s.torrent.size)),1)]),(0,a._)("div",k,[I,(0,a._)("div",x,(0,n.zw)(s.torrent.seeds),1)]),(0,a._)("div",T,[D,(0,a._)("div",S,(0,n.zw)(s.torrent.peers),1)]),(0,a._)("div",q,[z,(0,a._)("div",$,(0,n.zw)(e.formatDate(s.torrent.created_at,!0)),1)]),s.torrent.description?((0,a.wg)(),(0,a.iD)("div",N,[R,(0,a._)("div",Z,(0,n.zw)(s.torrent.description),1)])):(0,a.kq)("",!0),s.torrent.year?((0,a.wg)(),(0,a.iD)("div",U,[V,(0,a._)("div",E,(0,n.zw)(s.torrent.year),1)])):(0,a.kq)("",!0)])}var j=s(8637),P={mixins:[j.Z],props:{torrent:{type:Object,default:()=>({})}},methods:{openInNewTab(e){window.open(e,"_blank")}}},W=s(3744);const H=(0,W.Z)(P,[["render",L],["__scopeId","data-v-8eed74b0"]]);var F=H,M=s(9963);const O=e=>((0,a.dD)("data-v-0ae4cd8d"),e=e(),(0,a.Cn)(),e),Y={class:"row"},A={class:"search-box"},K=["disabled","placeholder"],B=["placeholder","value"],Q={class:"button-container"},G={key:0,type:"submit",title:"Loading",disabled:""},J={key:1,type:"submit",title:"Add torrent URL"},X=O((()=>(0,a._)("i",{class:"fa fa-download"},null,-1))),ee=[X],te={key:2,type:"submit",title:"Search"},se=O((()=>(0,a._)("i",{class:"fa fa-search"},null,-1))),ae=[se],ne={key:0,class:"right side col-1"},re=O((()=>(0,a._)("i",{class:"fa fa-bars"},null,-1))),le=[re];function ie(e,t,s,r,l,i){const o=(0,a.up)("Loading");return(0,a.wg)(),(0,a.iD)("div",{class:(0,n.C_)(["header",{"with-nav":s.withNav}])},[(0,a._)("div",Y,[(0,a._)("div",{class:(0,n.C_)(["left side",i.leftSideClasses])},[(0,a._)("form",{onSubmit:t[1]||(t[1]=(0,M.iM)(((...e)=>i.submit&&i.submit(...e)),["prevent"]))},[(0,a._)("label",A,["transfers"===s.selectedView?(0,a.wy)(((0,a.wg)(),(0,a.iD)("input",{key:0,type:"search",disabled:s.loading,placeholder:i.placeholder,"onUpdate:modelValue":t[0]||(t[0]=e=>l.torrentURL=e)},null,8,K)),[[M.nr,l.torrentURL]]):"search"===s.selectedView?((0,a.wg)(),(0,a.iD)("input",{key:1,type:"search",placeholder:i.placeholder,value:s.query,ref:"search"},null,8,B)):(0,a.kq)("",!0)]),(0,a._)("span",Q,[s.loading?((0,a.wg)(),(0,a.iD)("button",G,[(0,a.Wm)(o)])):"transfers"===s.selectedView?((0,a.wg)(),(0,a.iD)("button",J,ee)):"search"===s.selectedView?((0,a.wg)(),(0,a.iD)("button",te,ae)):(0,a.kq)("",!0)])],32)],2),s.withNav?(0,a.kq)("",!0):((0,a.wg)(),(0,a.iD)("div",ne,[(0,a._)("button",{onClick:t[2]||(t[2]=t=>e.$emit("toggle")),title:"Toggle navigation"},le)]))])],2)}var oe=s(6791),de={name:"Header",emits:["torrent-add","search","toggle"],components:{Loading:oe.Z},props:{query:{type:String,default:""},loading:{type:Boolean,default:!1},withNav:{type:Boolean,default:!1},selectedView:{type:String,default:"transfers"}},data(){return{torrentURL:""}},computed:{placeholder(){return"transfers"===this.selectedView?"Add torrent URL":"Search torrents"},leftSideClasses(){return this.withNav?{"col-11":!0}:{"col-12":!0}}},methods:{submit(){const e=this.$refs?.search?.value?.trim();"transfers"===this.selectedView&&this.torrentURL?.length?this.$emit("torrent-add",this.torrentURL):"search"===this.selectedView&&e?.length&&this.$emit("search",e)}}};const ce=(0,W.Z)(de,[["render",ie],["__scopeId","data-v-0ae4cd8d"]]);var ue=ce,pe=s(3493);const ve=e=>((0,a.dD)("data-v-5185ff00"),e=e(),(0,a.Cn)(),e),fe=ve((()=>(0,a._)("i",{class:"fa fa-bars"},null,-1))),me=[fe],he=["title","onClick"];function we(e,t,s,r,l,i){return(0,a.wg)(),(0,a.iD)("nav",null,[(0,a._)("button",{class:"menu-button",onClick:t[0]||(t[0]=t=>e.$emit("toggle"))},me),((0,a.wg)(!0),(0,a.iD)(a.HY,null,(0,a.Ko)(s.views,((t,r)=>((0,a.wg)(),(0,a.iD)("li",{key:r,title:t.displayName,class:(0,n.C_)({selected:r===s.selectedView}),onClick:t=>e.$emit("input",r)},[(0,a._)("i",{class:(0,n.C_)(t.iconClass)},null,2)],10,he)))),128))])}var ge={emits:["input","toggle"],props:{selectedView:{type:String},collapsed:{type:Boolean,default:!1},views:{type:Object,default:()=>({search:{displayName:"Search",iconClass:"fa fa-search"},transfers:{displayName:"Transfers",iconClass:"fa fa-download"}})}}};const _e=(0,W.Z)(ge,[["render",we],["__scopeId","data-v-5185ff00"]]);var ye=_e;const be=e=>((0,a.dD)("data-v-52a230bc"),e=e(),(0,a.Cn)(),e),Ce={class:"results-container"},ke={key:0,class:"no-content"},Ie={class:"info"},xe={class:"title"},Te={class:"additional-info"},De={class:"info-pill size"},Se=be((()=>(0,a._)("span",{class:"label"},[(0,a._)("i",{class:"fa fa-hdd"})],-1))),qe=be((()=>(0,a._)("span",{class:"separator"},null,-1))),ze={class:"value"},$e=be((()=>(0,a._)("span",{class:"separator"}," | ",-1))),Ne={class:"info-pill seeds"},Re=be((()=>(0,a._)("span",{class:"label"},[(0,a._)("i",{class:"fa fa-users"})],-1))),Ze=be((()=>(0,a._)("span",{class:"separator"},null,-1))),Ue={class:"value"},Ve=be((()=>(0,a._)("span",{class:"separator"}," | ",-1))),Ee={class:"info-pill created-at"},Le=be((()=>(0,a._)("span",{class:"label"},[(0,a._)("i",{class:"fa fa-calendar"})],-1))),je=be((()=>(0,a._)("span",{class:"separator"},null,-1))),Pe={class:"value"},We=be((()=>(0,a._)("span",{class:"separator"}," | ",-1))),He={class:"actions"},Fe=["onClick"],Me=be((()=>(0,a._)("i",{class:"fa fa-info-circle"},null,-1))),Oe=[Me],Ye=["onClick"],Ae=be((()=>(0,a._)("i",{class:"fa fa-download"},null,-1))),Ke=[Ae];function Be(e,t,s,r,l,i){return(0,a.wg)(),(0,a.iD)("div",Ce,[s.results?.length?((0,a.wg)(),(0,a.iD)("div",{key:1,class:"results",ref:"body",onScroll:t[0]||(t[0]=(...e)=>i.onScroll&&i.onScroll(...e))},[((0,a.wg)(!0),(0,a.iD)(a.HY,null,(0,a.Ko)(s.results,((t,s)=>((0,a.wg)(),(0,a.iD)("div",{class:"result",key:s},[(0,a._)("div",Ie,[(0,a._)("div",xe,(0,n.zw)(t.title),1),(0,a._)("div",Te,[(0,a._)("span",De,[Se,qe,(0,a._)("span",ze,(0,n.zw)(e.convertSize(t.size)),1)]),$e,(0,a._)("span",Ne,[Re,Ze,(0,a._)("span",Ue,(0,n.zw)(t.seeds),1)]),Ve,(0,a._)("span",Ee,[Le,je,(0,a._)("span",Pe,(0,n.zw)(e.formatDate(t.created_at,!0)),1)]),We])]),(0,a._)("div",He,[(0,a._)("button",{title:"Torrent info",onClick:t=>e.$emit("info",s)},Oe,8,Fe),(0,a._)("button",{title:"Download",onClick:s=>e.$emit("download",t.url)},Ke,8,Ye)])])))),128))],544)):((0,a.wg)(),(0,a.iD)("div",ke,"No results"))])}var Qe={emits:["download","info","next-page"],mixins:[j.Z],props:{results:{type:Array,default:()=>[]},page:{type:Number,default:1}},data(){return{scrollTimeout:null}},methods:{onScroll(){const e=this.$refs.body.scrollTop,t=parseFloat(getComputedStyle(this.$refs.body).height),s=this.$refs.body.scrollHeight;if(e>=s-t-5){if(this.scrollTimeout||!this.results.length)return;this.scrollTimeout=setTimeout((()=>{this.scrollTimeout=null}),250),this.$emit("next-page",this.page+1)}}}};const Ge=(0,W.Z)(Qe,[["render",Be],["__scopeId","data-v-52a230bc"]]);var Je=Ge,Xe=s(8590),et={mixins:[j.Z],components:{Info:F,Header:ue,Modal:pe.Z,Nav:ye,Results:Je,Transfers:Xe.Z},props:{pluginName:{type:String,required:!0}},data(){return{loading:!1,transfers:{},results:[],selectedView:"transfers",navCollapsed:!1,query:"",page:1,infoIndex:null}},computed:{infoItem(){return null===this.infoIndex?null:this.results[this.infoIndex]}},methods:{torrentId(e){return e?.hash&&e.hash.length?e.hash:e.url},onTorrentUpdate(e){this.transfers[this.torrentId(e)]=e},onTorrentQueued(e){this.onTorrentUpdate(e),this.notify({text:"Torrent queued for download",image:{icon:"hourglass-start"}})},onTorrentStart(e){this.onTorrentUpdate(e),this.notify({html:`Torrent download started: <b>${e.name}</b>`,image:{icon:"play"}})},onTorrentResume(e){this.onTorrentUpdate(e),this.notify({html:`Torrent download resumed: <b>${e.name}</b>`,image:{icon:"play"}})},onTorrentPause(e){this.onTorrentUpdate(e),this.notify({html:`Torrent download paused: <b>${e.name}</b>`,image:{icon:"pause"}})},onTorrentCompleted(e){this.onTorrentUpdate(e),this.transfers[this.torrentId(e)].finish_date=(new Date).toISOString(),this.transfers[this.torrentId(e)].progress=100,this.notify({html:`Torrent download completed: <b>${e.name}</b>`,image:{icon:"check"}})},onTorrentRemove(e){const t=this.torrentId(e);t in this.transfers&&delete this.transfers[t]},async search(e,t=1){this.loading=!0,this.query=e;let s=[];try{s=await this.request(`${this.pluginName}.search`,{query:e,page:t})}finally{this.loading=!1}this.results=1===t?s:this.results.concat(s),s.length>0&&(this.page=t)},async download(e){await this.request(`${this.pluginName}.download`,{torrent:e})},async pause(e){await this.request(`${this.pluginName}.pause`,{torrent:e.url}),await this.refresh()},async resume(e){await this.request(`${this.pluginName}.resume`,{torrent:e.url}),await this.refresh()},async remove(e){await this.request(`${this.pluginName}.remove`,{torrent:e.url}),await this.refresh()},async refresh(){this.loading=!0;try{this.transfers=Object.values(await this.request(`${this.pluginName}.status`)||{}).reduce(((e,t)=>(e[this.torrentId(t)]=t,e)),{})}finally{this.loading=!1}}},mounted(){this.refresh(),this.selectedView=this.transfers.length?"transfers":"search",this.subscribe(this.onTorrentUpdate,"on-torrent-update","platypush.message.event.torrent.TorrentDownloadStartEvent","platypush.message.event.torrent.TorrentDownloadProgressEvent","platypush.message.event.torrent.TorrentSeedingStartEvent","platypush.message.event.torrent.TorrentStateChangeEvent"),this.subscribe(this.onTorrentQueued,"on-torrent-queued","platypush.message.event.torrent.TorrentQueuedEvent"),this.subscribe(this.onTorrentStart,"on-torrent-queued","platypush.message.event.torrent.TorrentDownloadedMetadataEvent"),this.subscribe(this.onTorrentResume,"on-torrent-resume","platypush.message.event.torrent.TorrentResumedEvent"),this.subscribe(this.onTorrentPause,"on-torrent-pause","platypush.message.event.torrent.TorrentPausedEvent"),this.subscribe(this.onTorrentStop,"on-torrent-stop","platypush.message.event.torrent.TorrentDownloadStopEvent"),this.subscribe(this.onTorrentCompleted,"on-torrent-completed","platypush.message.event.torrent.TorrentDownloadCompletedEvent"),this.subscribe(this.onTorrentRemove,"on-torrent-remove","platypush.message.event.torrent.TorrentRemovedEvent");const e=document.querySelector('.search-box input[type="search"]');e&&this.$nextTick((()=>e.focus()))},destroy(){this.unsubscribe("on-torrent-update"),this.unsubscribe("on-torrent-remove")}};const tt=(0,W.Z)(et,[["render",i],["__scopeId","data-v-250eee36"]]);var st=tt},8590:function(e,t,s){s.d(t,{Z:function(){return he}});var a=s(6252),n=s(3577);const r=e=>((0,a.dD)("data-v-90235a8e"),e=e(),(0,a.Cn)(),e),l={key:1,class:"torrent-transfers fade-in"},i={key:0,class:"no-content"},o=["onClick"],d={class:"col-8 left side"},c=["textContent"],u={class:"col-2 right side"},p=["textContent"],v={class:"col-2 right side"},f={key:0,class:"modal-body torrent-info"},m={key:0,class:"row"},h=r((()=>(0,a._)("div",{class:"attr"},"Name",-1))),w=["textContent"],g={key:1,class:"row"},_=r((()=>(0,a._)("div",{class:"attr"},"State",-1))),y=["textContent"],b={class:"row"},C=r((()=>(0,a._)("div",{class:"attr"},"Progress",-1))),k=["textContent"],I={class:"row"},x=r((()=>(0,a._)("div",{class:"attr"},"DL rate",-1))),T=["textContent"],D={class:"row"},S=r((()=>(0,a._)("div",{class:"attr"},"UL rate",-1))),q=["textContent"],z={class:"row"},$=r((()=>(0,a._)("div",{class:"attr"},"Size",-1))),N=["textContent"],R={key:2,class:"row"},Z=r((()=>(0,a._)("div",{class:"attr"},"Remaining",-1))),U=["textContent"],V={class:"row"},E=r((()=>(0,a._)("div",{class:"attr"},"URL",-1))),L={class:"value nowrap"},j=["href","textContent"],P={class:"row"},W=r((()=>(0,a._)("div",{class:"attr"},"Peers",-1))),H=["textContent"],F={key:3,class:"row"},M=r((()=>(0,a._)("div",{class:"attr"},"Started",-1))),O=["textContent"],Y={key:4,class:"row"},A=r((()=>(0,a._)("div",{class:"attr"},"Finished",-1))),K=["textContent"],B={key:5,class:"row"},Q=r((()=>(0,a._)("div",{class:"attr"},"Save path",-1))),G=["textContent"],J={key:6,class:"row"},X=r((()=>(0,a._)("div",{class:"attr"},"Files",-1))),ee={class:"value"},te=["href","textContent"],se={key:0,class:"modal-body torrent-files"},ae={class:"col-1 icon"},ne={key:1,class:"fa fa-file"},re=["textContent"];function le(e,t,s,r,le,ie){const oe=(0,a.up)("Loading"),de=(0,a.up)("DropdownItem"),ce=(0,a.up)("Dropdown"),ue=(0,a.up)("Modal");return le.loading?((0,a.wg)(),(0,a.j4)(oe,{key:0})):((0,a.wg)(),(0,a.iD)("div",l,[Object.keys(s.transfers).length?(0,a.kq)("",!0):((0,a.wg)(),(0,a.iD)("div",i,"No torrent transfers in progress")),((0,a.wg)(!0),(0,a.iD)(a.HY,null,(0,a.Ko)(s.transfers,((s,r)=>((0,a.wg)(),(0,a.iD)("div",{class:(0,n.C_)(["row item",{selected:le.selectedItem===r}]),key:r,onClick:e=>le.selectedItem=r},[(0,a._)("div",d,[(0,a._)("i",{class:(0,n.C_)(["icon fa",{"fa-check":null!=s.finish_date,"fa-play":!s.finish_date&&"downloading"===s.state&&!s.paused,"fa-pause":!s.finish_date&&"downloading"===s.state&&s.paused,"fa-stop":!s.finish_date&&"stopped"===s.state}])},null,2),(0,a._)("div",{class:"title",textContent:(0,n.zw)(s.name||s.hash||s.url)},null,8,c)]),(0,a._)("div",u,[(0,a._)("span",{textContent:(0,n.zw)(`${s.progress}%`)},null,8,p)]),(0,a._)("div",v,[(0,a.Wm)(ce,{title:"Actions","icon-class":"fa fa-ellipsis-h",onClick:e=>le.selectedItem=r},{default:(0,a.w5)((()=>["downloading"!==s.state||s.paused?(0,a.kq)("",!0):((0,a.wg)(),(0,a.j4)(de,{key:0,"icon-class":"fa fa-pause",text:"Pause transfer",onClick:t=>e.$emit("pause",s)},null,8,["onClick"])),"downloading"===s.state&&s.paused?((0,a.wg)(),(0,a.j4)(de,{key:1,"icon-class":"fa fa-play",text:"Resume transfer",onClick:t=>e.$emit("resume",s)},null,8,["onClick"])):(0,a.kq)("",!0),(0,a.Wm)(de,{"icon-class":"fa fa-trash",text:"Remove transfer",onClick:t=>e.$emit("remove",s)},null,8,["onClick"]),(0,a.Wm)(de,{"icon-class":"fa fa-folder",text:"View files",onClick:t[0]||(t[0]=t=>e.$refs.torrentFiles.isVisible=!0)}),(0,a.Wm)(de,{"icon-class":"fa fa-info",text:"Torrent info",onClick:t[1]||(t[1]=t=>e.$refs.torrentInfo.isVisible=!0)})])),_:2},1032,["onClick"])])],10,o)))),128)),(0,a.Wm)(ue,{ref:"torrentInfo",title:"Torrent info",width:"80%"},{default:(0,a.w5)((()=>[null!=le.selectedItem&&s.transfers[le.selectedItem]?((0,a.wg)(),(0,a.iD)("div",f,[s.transfers[le.selectedItem].name?((0,a.wg)(),(0,a.iD)("div",m,[h,(0,a._)("div",{class:"value",textContent:(0,n.zw)(s.transfers[le.selectedItem].name)},null,8,w)])):(0,a.kq)("",!0),s.transfers[le.selectedItem].state?((0,a.wg)(),(0,a.iD)("div",g,[_,(0,a._)("div",{class:"value",textContent:(0,n.zw)(s.transfers[le.selectedItem].state)},null,8,y)])):(0,a.kq)("",!0),(0,a._)("div",b,[C,(0,a._)("div",{class:"value",textContent:(0,n.zw)(`${s.transfers[le.selectedItem].progress||0}%`)},null,8,k)]),(0,a._)("div",I,[x,(0,a._)("div",{class:"value",textContent:(0,n.zw)(`${e.convertSize(s.transfers[le.selectedItem].download_rate||0)}/s`)},null,8,T)]),(0,a._)("div",D,[S,(0,a._)("div",{class:"value",textContent:(0,n.zw)(`${e.convertSize(s.transfers[le.selectedItem].upload_rate||0)}/s`)},null,8,q)]),(0,a._)("div",z,[$,(0,a._)("div",{class:"value",textContent:(0,n.zw)(e.convertSize(s.transfers[le.selectedItem].size||0))},null,8,N)]),s.transfers[le.selectedItem].remaining_bytes?((0,a.wg)(),(0,a.iD)("div",R,[Z,(0,a._)("div",{class:"value",textContent:(0,n.zw)(e.convertSize(s.transfers[le.selectedItem].remaining_bytes))},null,8,U)])):(0,a.kq)("",!0),(0,a._)("div",V,[E,(0,a._)("div",L,[(0,a._)("a",{href:s.transfers[le.selectedItem].url,target:"_blank",textContent:(0,n.zw)(s.transfers[le.selectedItem].url)},null,8,j)])]),(0,a._)("div",P,[W,(0,a._)("div",{class:"value",textContent:(0,n.zw)(s.transfers[le.selectedItem].peers||0)},null,8,H)]),s.transfers[le.selectedItem].start_date?((0,a.wg)(),(0,a.iD)("div",F,[M,(0,a._)("div",{class:"value",textContent:(0,n.zw)(e.formatDateTime(s.transfers[le.selectedItem].start_date))},null,8,O)])):(0,a.kq)("",!0),s.transfers[le.selectedItem].finish_date?((0,a.wg)(),(0,a.iD)("div",Y,[A,(0,a._)("div",{class:"value",textContent:(0,n.zw)(e.formatDateTime(s.transfers[le.selectedItem].finish_date))},null,8,K)])):(0,a.kq)("",!0),s.transfers[le.selectedItem].save_path?((0,a.wg)(),(0,a.iD)("div",B,[Q,(0,a._)("div",{class:"value",textContent:(0,n.zw)(s.transfers[le.selectedItem].save_path)},null,8,G)])):(0,a.kq)("",!0),s.transfers[le.selectedItem].files?((0,a.wg)(),(0,a.iD)("div",J,[X,(0,a._)("div",ee,[((0,a.wg)(!0),(0,a.iD)(a.HY,null,(0,a.Ko)(s.transfers[le.selectedItem].files,((e,t)=>((0,a.wg)(),(0,a.iD)("div",{class:"file",key:t},[(0,a._)("a",{href:`/file?path=${encodeURIComponent(e)}`,target:"_blank",textContent:(0,n.zw)(e)},null,8,te)])))),128))])])):(0,a.kq)("",!0)])):(0,a.kq)("",!0)])),_:1},512),(0,a.Wm)(ue,{ref:"torrentFiles",title:"Torrent files",width:"80%"},{default:(0,a.w5)((()=>[null!=le.selectedItem&&s.transfers[le.selectedItem]?((0,a.wg)(),(0,a.iD)("div",se,[((0,a.wg)(!0),(0,a.iD)(a.HY,null,(0,a.Ko)(ie.relativeFiles,((t,r)=>((0,a.wg)(),(0,a.iD)("div",{class:"row",key:t},[(0,a._)("div",ae,[s.isMedia&&e.mediaExtensions.has(t.split(".").pop())?((0,a.wg)(),(0,a.j4)(ce,{key:0},{default:(0,a.w5)((()=>[(0,a.Wm)(de,{"icon-class":"fa fa-play",text:"Play",onClick:t=>e.$emit("play",{url:`file://${s.transfers[le.selectedItem].files[r]}`,type:"file"})},null,8,["onClick"])])),_:2},1024)):((0,a.wg)(),(0,a.iD)("i",ne))]),(0,a._)("div",{class:"col-11 name",textContent:(0,n.zw)(t)},null,8,re)])))),128))])):(0,a.kq)("",!0)])),_:1},512)]))}var ie=s(6791),oe=s(8637),de=s(1065),ce=s(3493),ue=s(2787),pe=s(815),ve={emits:["pause","play","play-with-captions","refresh","remove","resume"],components:{Dropdown:ue.Z,DropdownItem:pe.Z,Loading:ie.Z,Modal:ce.Z},mixins:[oe.Z,de.Z],props:{isMedia:{type:Boolean,default:!1},transfers:{type:Object,default:()=>({})}},data(){return{loading:!1,selectedItem:null}},computed:{relativeFiles(){return null!=this.selectedItem&&this.transfers[this.selectedItem]?.files?.length?this.transfers[this.selectedItem].files.map((e=>e.split("/").pop())):[]}}},fe=s(3744);const me=(0,fe.Z)(ve,[["render",le],["__scopeId","data-v-90235a8e"]]);var he=me}}]);
//# sourceMappingURL=6429.28e09dbc.js.map