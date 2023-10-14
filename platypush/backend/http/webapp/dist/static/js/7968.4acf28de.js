"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[7968],{1065:function(e,t,s){s.d(t,{Z:function(){return i}});s(7658);var n=s(4421),a={name:"Utils",mixins:[n.Z],computed:{audioExtensions(){return new Set(["3gp","aa","aac","aax","act","aiff","amr","ape","au","awb","dct","dss","dvf","flac","gsm","iklax","ivs","m4a","m4b","m4p","mmf","mp3","mpc","msv","nmf","nsf","ogg,","opus","ra,","raw","sln","tta","vox","wav","wma","wv","webm","8svx"])},videoExtensions(){return new Set(["webm","mkv","flv","flv","vob","ogv","ogg","drc","gif","gifv","mng","avi","mts","m2ts","mov","qt","wmv","yuv","rm","rmvb","asf","amv","mp4","m4p","m4v","mpg","mp2","mpeg","mpe","mpv","mpg","mpeg","m2v","m4v","svi","3gp","3g2","mxf","roq","nsv","flv","f4v","f4p","f4a","f4b"])},mediaExtensions(){return new Set([...this.videoExtensions,...this.audioExtensions])}},methods:{convertTime(e){e=parseFloat(e);const t={};t.h=""+parseInt(e/3600),t.m=""+parseInt(e/60-60*t.h),t.s=""+parseInt(e-(3600*t.h+60*t.m));for(const n of["m","s"])parseInt(t[n])<10&&(t[n]="0"+t[n]);const s=[];return parseInt(t.h)&&s.push(t.h),s.push(t.m,t.s),s.join(":")},async startStreaming(e,t=!1){let s=e,n=null;e instanceof Object?(s=e.url,n=e.subtitles):e={url:s};const a=await this.request("media.start_streaming",{media:s,subtitles:n,download:t});return{...e,...a}},async stopStreaming(e){await this.request("media.stop_streaming",{media_id:e})}}};const r=a;var i=r},7968:function(e,t,s){s.d(t,{Z:function(){return k}});var n=s(6252);const a={class:"torrent-container"},r={class:"header-container"},i={class:"view-container"};function l(e,t,s,l,o,d){const c=(0,n.up)("Header"),m=(0,n.up)("TorrentView");return(0,n.wg)(),(0,n.iD)("div",a,[(0,n._)("div",r,[(0,n.Wm)(c,{onTorrentAdd:t[0]||(t[0]=e=>d.download(e))})]),(0,n._)("div",i,[(0,n.Wm)(m,{"plugin-name":s.pluginName},null,8,["plugin-name"])])])}var o=s(3577),d=s(9963);const c={class:"row"},m={class:"col-s-12 col-m-9 col-l-7 left side"},u={class:"search-box"};function v(e,t,s,a,r,i){return(0,n.wg)(),(0,n.iD)("div",{class:(0,o.C_)(["header",{"with-filter":e.filterVisible}])},[(0,n._)("div",c,[(0,n._)("div",m,[(0,n._)("form",{onSubmit:t[1]||(t[1]=(0,d.iM)((t=>e.$emit("torrent-add",r.torrentURL)),["prevent"]))},[(0,n._)("label",u,[(0,n.wy)((0,n._)("input",{type:"search",placeholder:"Add torrent URL","onUpdate:modelValue":t[0]||(t[0]=e=>r.torrentURL=e)},null,512),[[d.nr,r.torrentURL]])])],32)])])],2)}var f={name:"Header",emits:["torrent-add"],data(){return{torrentURL:""}}},p=s(3744);const h=(0,p.Z)(f,[["render",v],["__scopeId","data-v-33115af0"]]);var w=h,g=s(562),_=s(4421),y={name:"Panel",components:{TorrentView:g.Z,Header:w},mixins:[_.Z],props:{pluginName:{type:String,required:!0}},methods:{async download(e){await this.request(`${this.pluginName}.download`,{torrent:e})}}};const C=(0,p.Z)(y,[["render",l],["__scopeId","data-v-1502d8a8"]]);var k=C},562:function(e,t,s){s.d(t,{Z:function(){return ue}});var n=s(6252),a=s(3577);const r=e=>((0,n.dD)("data-v-7351a8a4"),e=e(),(0,n.Cn)(),e),i={key:1,class:"torrent-transfers fade-in"},l={key:0,class:"no-content"},o=["onClick"],d={class:"col-8 left side"},c=["textContent"],m={class:"col-2 right side"},u=["textContent"],v={class:"col-2 right side"},f={key:0,class:"modal-body torrent-info"},p={key:0,class:"row"},h=r((()=>(0,n._)("div",{class:"attr"},"Name",-1))),w=["textContent"],g={key:1,class:"row"},_=r((()=>(0,n._)("div",{class:"attr"},"State",-1))),y=["textContent"],C={class:"row"},k=r((()=>(0,n._)("div",{class:"attr"},"Progress",-1))),x=["textContent"],I={class:"row"},b=r((()=>(0,n._)("div",{class:"attr"},"DL rate",-1))),D=["textContent"],T={class:"row"},q=r((()=>(0,n._)("div",{class:"attr"},"UL rate",-1))),z=["textContent"],S={class:"row"},E=r((()=>(0,n._)("div",{class:"attr"},"Size",-1))),Z=["textContent"],$={key:2,class:"row"},R=r((()=>(0,n._)("div",{class:"attr"},"Remaining",-1))),U=["textContent"],L={class:"row"},N=r((()=>(0,n._)("div",{class:"attr"},"URL",-1))),W={class:"value nowrap"},j=["href","textContent"],V={class:"row"},P=r((()=>(0,n._)("div",{class:"attr"},"Peers",-1))),F=["textContent"],M={key:3,class:"row"},H=r((()=>(0,n._)("div",{class:"attr"},"Started",-1))),A=["textContent"],O={key:4,class:"row"},K=r((()=>(0,n._)("div",{class:"attr"},"Finished",-1))),Y=["textContent"],B={key:5,class:"row"},Q=r((()=>(0,n._)("div",{class:"attr"},"Save path",-1))),G=["textContent"],J={key:0,class:"modal-body torrent-files"},X={class:"col-1 icon"},ee={key:1,class:"fa fa-file"},te=["textContent"];function se(e,t,s,r,se,ne){const ae=(0,n.up)("Loading"),re=(0,n.up)("DropdownItem"),ie=(0,n.up)("Dropdown"),le=(0,n.up)("Modal");return se.loading?((0,n.wg)(),(0,n.j4)(ae,{key:0})):((0,n.wg)(),(0,n.iD)("div",i,[Object.keys(se.transfers).length?(0,n.kq)("",!0):((0,n.wg)(),(0,n.iD)("div",l,"No torrent transfers in progress")),((0,n.wg)(!0),(0,n.iD)(n.HY,null,(0,n.Ko)(se.transfers,((s,r)=>((0,n.wg)(),(0,n.iD)("div",{class:(0,a.C_)(["row item",{selected:se.selectedItem===r}]),key:r,onClick:e=>se.selectedItem=r},[(0,n._)("div",d,[(0,n._)("i",{class:(0,a.C_)(["icon fa",{"fa-check":null!=s.finish_date,"fa-play":!s.finish_date&&"downloading"===s.state,"fa-pause":!s.finish_date&&"paused"===s.state,"fa-stop":!s.finish_date&&"stopped"===s.state}])},null,2),(0,n._)("div",{class:"title",textContent:(0,a.zw)(s.name||s.hash||s.url)},null,8,c)]),(0,n._)("div",m,[(0,n._)("span",{textContent:(0,a.zw)(`${s.progress}%`)},null,8,u)]),(0,n._)("div",v,[(0,n.Wm)(ie,{title:"Actions","icon-class":"fa fa-ellipsis-h",onClick:e=>se.selectedItem=r},{default:(0,n.w5)((()=>["downloading"===s.state?((0,n.wg)(),(0,n.j4)(re,{key:0,"icon-class":"fa fa-pause",text:"Pause transfer",onClick:e=>ne.pause(ne.torrentId(s))},null,8,["onClick"])):(0,n.kq)("",!0),"paused"===s.state?((0,n.wg)(),(0,n.j4)(re,{key:1,"icon-class":"fa fa-play",text:"Resume transfer",onClick:e=>ne.resume(ne.torrentId(s))},null,8,["onClick"])):(0,n.kq)("",!0),(0,n.Wm)(re,{"icon-class":"fa fa-trash",text:"Remove transfer",onClick:e=>ne.remove(ne.torrentId(s))},null,8,["onClick"]),(0,n.Wm)(re,{"icon-class":"fa fa-folder",text:"View files",onClick:t[0]||(t[0]=t=>e.$refs.torrentFiles.isVisible=!0)}),(0,n.Wm)(re,{"icon-class":"fa fa-info",text:"Torrent info",onClick:t[1]||(t[1]=t=>e.$refs.torrentInfo.isVisible=!0)})])),_:2},1032,["onClick"])])],10,o)))),128)),(0,n.Wm)(le,{ref:"torrentInfo",title:"Torrent info",width:"80%"},{default:(0,n.w5)((()=>[null!=se.selectedItem&&se.transfers[se.selectedItem]?((0,n.wg)(),(0,n.iD)("div",f,[se.transfers[se.selectedItem].name?((0,n.wg)(),(0,n.iD)("div",p,[h,(0,n._)("div",{class:"value",textContent:(0,a.zw)(se.transfers[se.selectedItem].name)},null,8,w)])):(0,n.kq)("",!0),se.transfers[se.selectedItem].state?((0,n.wg)(),(0,n.iD)("div",g,[_,(0,n._)("div",{class:"value",textContent:(0,a.zw)(se.transfers[se.selectedItem].state)},null,8,y)])):(0,n.kq)("",!0),(0,n._)("div",C,[k,(0,n._)("div",{class:"value",textContent:(0,a.zw)(`${se.transfers[se.selectedItem].progress||0}%`)},null,8,x)]),(0,n._)("div",I,[b,(0,n._)("div",{class:"value",textContent:(0,a.zw)(`${e.convertSize(se.transfers[se.selectedItem].download_rate||0)}/s`)},null,8,D)]),(0,n._)("div",T,[q,(0,n._)("div",{class:"value",textContent:(0,a.zw)(`${e.convertSize(se.transfers[se.selectedItem].upload_rate||0)}/s`)},null,8,z)]),(0,n._)("div",S,[E,(0,n._)("div",{class:"value",textContent:(0,a.zw)(e.convertSize(se.transfers[se.selectedItem].size||0))},null,8,Z)]),se.transfers[se.selectedItem].remaining_bytes?((0,n.wg)(),(0,n.iD)("div",$,[R,(0,n._)("div",{class:"value",textContent:(0,a.zw)(e.convertSize(se.transfers[se.selectedItem].remaining_bytes))},null,8,U)])):(0,n.kq)("",!0),(0,n._)("div",L,[N,(0,n._)("div",W,[(0,n._)("a",{href:se.transfers[se.selectedItem].url,target:"_blank",textContent:(0,a.zw)(se.transfers[se.selectedItem].url)},null,8,j)])]),(0,n._)("div",V,[P,(0,n._)("div",{class:"value",textContent:(0,a.zw)(se.transfers[se.selectedItem].peers||0)},null,8,F)]),se.transfers[se.selectedItem].start_date?((0,n.wg)(),(0,n.iD)("div",M,[H,(0,n._)("div",{class:"value",textContent:(0,a.zw)(e.formatDateTime(se.transfers[se.selectedItem].start_date))},null,8,A)])):(0,n.kq)("",!0),se.transfers[se.selectedItem].finish_date?((0,n.wg)(),(0,n.iD)("div",O,[K,(0,n._)("div",{class:"value",textContent:(0,a.zw)(e.formatDateTime(se.transfers[se.selectedItem].finish_date))},null,8,Y)])):(0,n.kq)("",!0),se.transfers[se.selectedItem].save_path?((0,n.wg)(),(0,n.iD)("div",B,[Q,(0,n._)("div",{class:"value",textContent:(0,a.zw)(se.transfers[se.selectedItem].save_path)},null,8,G)])):(0,n.kq)("",!0)])):(0,n.kq)("",!0)])),_:1},512),(0,n.Wm)(le,{ref:"torrentFiles",title:"Torrent files",width:"80%"},{default:(0,n.w5)((()=>[null!=se.selectedItem&&se.transfers[se.selectedItem]?((0,n.wg)(),(0,n.iD)("div",J,[((0,n.wg)(!0),(0,n.iD)(n.HY,null,(0,n.Ko)(ne.relativeFiles,((t,r)=>((0,n.wg)(),(0,n.iD)("div",{class:"row",key:t},[(0,n._)("div",X,[s.isMedia&&e.mediaExtensions.has(t.split(".").pop())?((0,n.wg)(),(0,n.j4)(ie,{key:0},{default:(0,n.w5)((()=>[(0,n.Wm)(re,{"icon-class":"fa fa-play",text:"Play",onClick:t=>e.$emit("play",{url:`file://${se.transfers[se.selectedItem].files[r]}`,type:"file"})},null,8,["onClick"])])),_:2},1024)):((0,n.wg)(),(0,n.iD)("i",ee))]),(0,n._)("div",{class:"col-11 name",textContent:(0,a.zw)(t)},null,8,te)])))),128))])):(0,n.kq)("",!0)])),_:1},512)]))}var ne=s(6791),ae=s(4421),re=s(1065),ie=s(9417),le=s(7261),oe=s(1950),de={name:"View",emits:["play","play-with-captions"],components:{Dropdown:le.Z,DropdownItem:oe.Z,Loading:ne.Z,Modal:ie.Z},mixins:[ae.Z,re.Z],props:{pluginName:{type:String,required:!0},isMedia:{type:Boolean,default:!1}},data(){return{loading:!1,transfers:{},selectedItem:null}},computed:{relativeFiles(){return null!=this.selectedItem&&this.transfers[this.selectedItem]?.files?.length?this.transfers[this.selectedItem].files.map((e=>e.split("/").pop())):[]}},methods:{torrentId(e){return e?.hash&&e.hash.length?e.hash:e.url},async refresh(){this.loading=!0;try{this.transfers=Object.values(await this.request(`${this.pluginName}.status`)||{}).reduce(((e,t)=>(e[this.torrentId(t)]=t,e)),{})}finally{this.loading=!1}},async pause(e){await this.request(`${this.pluginName}.pause`,{torrent:e}),await this.refresh()},async resume(e){await this.request(`${this.pluginName}.resume`,{torrent:e}),await this.refresh()},async remove(e){await this.request(`${this.pluginName}.remove`,{torrent:e}),await this.refresh()},onTorrentUpdate(e){this.transfers[this.torrentId(e)]=e},onTorrentRemove(e){const t=this.torrentId(e);t in this.transfers&&delete this.transfers[t]}},mounted(){this.refresh(),this.subscribe(this.onTorrentUpdate,"on-torrent-update","platypush.message.event.torrent.TorrentQueuedEvent","platypush.message.event.torrent.TorrentDownloadedMetadataEvent","platypush.message.event.torrent.TorrentDownloadStartEvent","platypush.message.event.torrent.TorrentDownloadProgressEvent","platypush.message.event.torrent.TorrentResumedEvent","platypush.message.event.torrent.TorrentPausedEvent","platypush.message.event.torrent.TorrentSeedingStartEvent","platypush.message.event.torrent.TorrentStateChangeEvent","platypush.message.event.torrent.TorrentDownloadStopEvent","platypush.message.event.torrent.TorrentDownloadCompletedEvent"),this.subscribe(this.onTorrentRemove,"on-torrent-remove","platypush.message.event.torrent.TorrentRemovedEvent")},destroy(){this.unsubscribe("on-torrent-update"),this.unsubscribe("on-torrent-remove")}},ce=s(3744);const me=(0,ce.Z)(de,[["render",se],["__scopeId","data-v-7351a8a4"]]);var ue=me}}]);
//# sourceMappingURL=7968.4acf28de.js.map