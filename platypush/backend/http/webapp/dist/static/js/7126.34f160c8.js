"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[7126],{4358:function(e,t,s){s.d(t,{Z:function(){return f}});var l=s(6252),o=s(3577),n=s(9963);const i={class:"slider-wrapper"},a=["textContent"],c=["textContent"],r={class:"slider-container"},u=["min","max","step","disabled","value"],d={class:"track-inner",ref:"track"},h={class:"thumb",ref:"thumb"},p=["textContent"];function m(e,t,s,m,v,g){return(0,l.wg)(),(0,l.iD)("label",i,[s.withRange?((0,l.wg)(),(0,l.iD)("span",{key:0,class:(0,o.C_)(["range-labels",{"with-label":s.withLabel}])},[s.withRange?((0,l.wg)(),(0,l.iD)("span",{key:0,class:"label left",textContent:(0,o.zw)(s.range[0])},null,8,a)):(0,l.kq)("",!0),s.withRange?((0,l.wg)(),(0,l.iD)("span",{key:1,class:"label right",textContent:(0,o.zw)(s.range[1])},null,8,c)):(0,l.kq)("",!0)],2)):(0,l.kq)("",!0),(0,l._)("span",r,[(0,l._)("input",{class:(0,o.C_)(["slider",{"with-label":s.withLabel}]),type:"range",min:s.range[0],max:s.range[1],step:s.step,disabled:s.disabled,value:s.value,ref:"range",onInput:t[0]||(t[0]=(0,n.iM)(((...e)=>g.onUpdate&&g.onUpdate(...e)),["stop"])),onChange:t[1]||(t[1]=(0,n.iM)(((...e)=>g.onUpdate&&g.onUpdate(...e)),["stop"]))},null,42,u),(0,l._)("div",{class:(0,o.C_)(["track",{"with-label":s.withLabel}])},[(0,l._)("div",d,null,512)],2),(0,l._)("div",h,null,512),s.withLabel?((0,l.wg)(),(0,l.iD)("span",{key:0,class:"label",textContent:(0,o.zw)(s.value),ref:"label"},null,8,p)):(0,l.kq)("",!0)])])}var v={name:"Slider",emits:["input","change","mouseup","mousedown","touchstart","touchend","keyup","keydown"],props:{value:{type:Number},disabled:{type:Boolean,default:!1},range:{type:Array,default:()=>[0,100]},step:{type:Number,default:1},withLabel:{type:Boolean,default:!1},withRange:{type:Boolean,default:!1}},methods:{onUpdate(e){this.update(e.target.value),this.$emit(e.type,{...e,target:{...e.target,value:this.$refs.range.value}})},update(e){const t=this.$refs.range.clientWidth,s=(e-this.range[0])/(this.range[1]-this.range[0]),l=s*t,o=this.$refs.thumb;o.style.left=l-o.clientWidth/2+"px",this.$refs.thumb.style.transform=`translate(-${s}%, -50%)`,this.$refs.track.style.width=`${l}px`}},mounted(){null!=this.value&&this.update(this.value),this.$watch((()=>this.value),(e=>this.update(e)))}},g=s(3744);const w=(0,g.Z)(v,[["render",m],["__scopeId","data-v-4b38623f"]]);var f=w},3405:function(e,t,s){s.d(t,{Z:function(){return m}});var l=s(6252),o=s(3577),n=s(9963);const i=e=>((0,l.dD)("data-v-a6396ae8"),e=e(),(0,l.Cn)(),e),a=["checked"],c=i((()=>(0,l._)("div",{class:"switch"},[(0,l._)("div",{class:"dot"})],-1))),r={class:"label"};function u(e,t,s,i,u,d){return(0,l.wg)(),(0,l.iD)("div",{class:(0,o.C_)(["power-switch",{disabled:s.disabled}]),onClick:t[0]||(t[0]=(0,n.iM)(((...e)=>d.onInput&&d.onInput(...e)),["stop"]))},[(0,l._)("input",{type:"checkbox",checked:s.value},null,8,a),(0,l._)("label",null,[c,(0,l._)("span",r,[(0,l.WI)(e.$slots,"default",{},void 0,!0)])])],2)}var d={name:"ToggleSwitch",emits:["input"],props:{value:{type:Boolean,default:!1},disabled:{type:Boolean,default:!1}},methods:{onInput(e){if(this.disabled)return!1;this.$emit("input",e)}}},h=s(3744);const p=(0,h.Z)(d,[["render",u],["__scopeId","data-v-a6396ae8"]]);var m=p},7126:function(e,t,s){s.r(t),s.d(t,{default:function(){return as}});var l=s(6252);const o={class:"music-snapcast-container"},n={class:"info"},i={class:"info"},a={class:"info"};function c(e,t,s,c,r,u){const d=(0,l.up)("Loading"),h=(0,l.up)("ModalHost"),p=(0,l.up)("Modal"),m=(0,l.up)("ModalGroup"),v=(0,l.up)("ModalClient"),g=(0,l.up)("Host");return(0,l.wg)(),(0,l.iD)("div",o,[e.loading?((0,l.wg)(),(0,l.j4)(d,{key:0})):(0,l.kq)("",!0),(0,l._)("div",n,[(0,l.Wm)(p,{title:"Server info",ref:"modalHost"},{default:(0,l.w5)((()=>[e.selectedHost?((0,l.wg)(),(0,l.j4)(h,{key:0,info:e.hosts[e.selectedHost]},null,8,["info"])):(0,l.kq)("",!0)])),_:1},512)]),(0,l._)("div",i,[(0,l.Wm)(p,{title:"Group info",ref:"modalGroup"},{default:(0,l.w5)((()=>[e.selectedGroup?((0,l.wg)(),(0,l.j4)(m,{key:0,group:e.hosts[e.selectedHost].groups[e.selectedGroup],streams:e.hosts[e.selectedHost].streams,clients:u.clientsByHost[e.selectedHost],loading:e.loading,onAddClient:u.addClientToGroup,onRemoveClient:u.removeClientFromGroup,onStreamChange:u.streamChange,onRenameGroup:t[0]||(t[0]=e=>u.renameGroup(e))},null,8,["group","streams","clients","loading","onAddClient","onRemoveClient","onStreamChange"])):(0,l.kq)("",!0)])),_:1},512)]),(0,l._)("div",a,[(0,l.Wm)(p,{title:"Client info",ref:"modalClient"},{default:(0,l.w5)((()=>[e.selectedClient?((0,l.wg)(),(0,l.j4)(v,{key:0,client:e.hosts[e.selectedHost].groups[e.selectedGroup].clients[e.selectedClient],loading:e.loading,onRemoveClient:u.removeClient,onRenameClient:t[1]||(t[1]=e=>u.renameClient(e))},null,8,["client","loading","onRemoveClient"])):(0,l.kq)("",!0)])),_:1},512)]),((0,l.wg)(!0),(0,l.iD)(l.HY,null,(0,l.Ko)(e.hosts,((e,s)=>((0,l.wg)(),(0,l.j4)(g,{key:s,server:e.server,streams:e.streams,groups:e.groups,onGroupMuteToggle:t[2]||(t[2]=e=>u.groupMute(e)),onClientMuteToggle:t[3]||(t[3]=e=>u.clientMute(e)),onClientVolumeChange:t[4]||(t[4]=e=>u.clientSetVolume(e)),onModalShow:t[5]||(t[5]=e=>u.onModalShow(e))},null,8,["server","streams","groups"])))),128))])}var r=s(9417),u=s(5576),d=s(3577);const h=e=>((0,l.dD)("data-v-7bce419a"),e=e(),(0,l.Cn)(),e),p={class:"host"},m={class:"header"},v=h((()=>(0,l._)("i",{class:"icon fa fa-server"},null,-1))),g={class:"col-2 buttons pull-right"},w={key:0,class:"group-container"};function f(e,t,s,o,n,i){const a=(0,l.up)("Group");return(0,l.wg)(),(0,l.iD)("div",p,[(0,l._)("div",m,[(0,l._)("div",{class:"col-10 name",onClick:t[0]||(t[0]=t=>e.$emit("modal-show",{type:"host",host:s.server.host.name}))},[v,(0,l.Uk)(" "+(0,d.zw)(s.server.host.name),1)]),(0,l._)("div",g,[(0,l._)("button",{type:"button",onClick:t[1]||(t[1]=e=>n.collapsed=!n.collapsed)},[(0,l._)("i",{class:(0,d.C_)(["icon fa",{"fa-chevron-up":!n.collapsed,"fa-chevron-down":n.collapsed}])},null,2)])])]),n.collapsed?(0,l.kq)("",!0):((0,l.wg)(),(0,l.iD)("div",w,[((0,l.wg)(!0),(0,l.iD)(l.HY,null,(0,l.Ko)(s.groups,((o,n)=>((0,l.wg)(),(0,l.j4)(a,{key:n,id:o.id,name:o.name,server:s.server.host,muted:o.muted,clients:o.clients,stream:s.streams[o.stream_id],onModalShow:t[2]||(t[2]=t=>e.$emit("modal-show",t)),onGroupMuteToggle:t[3]||(t[3]=t=>e.$emit("group-mute-toggle",t)),onClientMuteToggle:t[4]||(t[4]=t=>e.$emit("client-mute-toggle",t)),onClientVolumeChange:t[5]||(t[5]=t=>e.$emit("client-volume-change",t))},null,8,["id","name","server","muted","clients","stream"])))),128))]))])}const _={class:"group"},C={class:"head"},y={class:"col-2 switch pull-right"},b={class:"body"};function k(e,t,s,o,n,i){const a=(0,l.up)("ToggleSwitch"),c=(0,l.up)("Client");return(0,l.wg)(),(0,l.iD)("div",_,[(0,l._)("div",C,[(0,l._)("div",{class:"col-10 name",onClick:t[0]||(t[0]=t=>e.$emit("modal-show",{type:"group",group:s.id,host:s.server.name}))},[(0,l._)("i",{class:(0,d.C_)(["icon fa",{"fa-play":"playing"===s.stream.status,"fa-stop":"playing"!==s.stream.status}])},null,2),(0,l.Uk)(" "+(0,d.zw)(s.name||s.stream.id||s.id),1)]),(0,l._)("div",y,[(0,l.Wm)(a,{value:!s.muted,onInput:t[1]||(t[1]=t=>e.$emit("group-mute-toggle",{host:s.server.name,group:s.id,muted:!s.muted}))},null,8,["value"])])]),(0,l._)("div",b,[((0,l.wg)(!0),(0,l.iD)(l.HY,null,(0,l.Ko)(s.clients,(o=>((0,l.wg)(),(0,l.j4)(c,{key:o.id,config:o.config,connected:o.connected,server:s.server,host:o.host,groupId:s.id,id:o.id,lastSeen:o.lastSeen,snapclient:o.snapclient,onModalShow:t[2]||(t[2]=t=>e.$emit("modal-show",t)),onVolumeChange:t[3]||(t[3]=t=>e.$emit("client-volume-change",t)),onMuteToggle:t[4]||(t[4]=t=>e.$emit("client-mute-toggle",t))},null,8,["config","connected","server","host","groupId","id","lastSeen","snapclient"])))),128))])])}var x=s(3405);const H=["textContent"],S={class:"col-s-12 col-m-9 controls"},D={class:"col-10 slider-container"},q={class:"col-2 switch pull-right"};function G(e,t,s,o,n,i){const a=(0,l.up)("Slider"),c=(0,l.up)("ToggleSwitch");return(0,l.wg)(),(0,l.iD)("div",{class:(0,d.C_)(["row client",{offline:!s.connected}])},[(0,l._)("div",{class:"col-s-12 col-m-3 name",textContent:(0,d.zw)(s.config.name?.length?s.config.name:s.host.name),onClick:t[0]||(t[0]=t=>e.$emit("modal-show",{type:"client",client:s.id,group:s.groupId,host:s.server.name}))},null,8,H),(0,l._)("div",S,[(0,l._)("div",D,[(0,l.Wm)(a,{range:[0,100],value:s.config.volume.percent,onMouseup:t[1]||(t[1]=t=>e.$emit("volume-change",{host:s.server.name,client:s.id,volume:t.target.value}))},null,8,["value"])]),(0,l._)("div",q,[(0,l.Wm)(c,{value:!s.config.volume.muted,onInput:t[2]||(t[2]=t=>e.$emit("mute-toggle",{host:s.server.name,client:s.id,muted:!s.config.volume.muted}))},null,8,["value"])])])],2)}var z=s(4358),M={name:"Client",components:{Slider:z.Z,ToggleSwitch:x.Z},emits:["volume-change","mute-toggle","modal-show"],props:{config:{type:Object,required:!0},connected:{type:Boolean,default:!1},host:{type:Object,required:!0},id:{type:String,required:!0},groupId:{type:String,required:!0},lastSeen:{type:Object,default:()=>{}},snapclient:{type:Object,required:!0},server:{type:Object,required:!0}}},j=s(3744);const $=(0,j.Z)(M,[["render",G],["__scopeId","data-v-12b0e65b"]]);var O=$,I={name:"Group",components:{Client:O,ToggleSwitch:x.Z},emits:["group-mute-toggle","modal-show","client-volume-change","client-mute-toggle"],props:{id:{type:String},clients:{type:Object,default:()=>{}},muted:{type:Boolean},name:{type:String},stream:{type:Object},server:{type:Object}}};const U=(0,j.Z)(I,[["render",k],["__scopeId","data-v-748fccb4"]]);var Z=U,R={name:"Host",emits:["modal-show","group-mute-toggle","client-mute-toggle","client-volume-change"],components:{Group:Z},props:{groups:{type:Object,default:()=>{}},server:{type:Object,default:()=>{}},streams:{type:Object,default:()=>{}}},data(){return{collapsed:!1}}};const V=(0,j.Z)(R,[["render",f],["__scopeId","data-v-7bce419a"]]);var B=V;const E={class:"info"},A={key:0,class:"row"},T=(0,l._)("div",{class:"label col-3"},"IP Address",-1),P=["textContent"],W={key:1,class:"row"},L=(0,l._)("div",{class:"label col-3"},"MAC Address",-1),N=["textContent"],K={key:2,class:"row"},Y=(0,l._)("div",{class:"label col-3"},"Name",-1),F=["textContent"],J={key:3,class:"row"},Q=(0,l._)("div",{class:"label col-3"},"Port",-1),X=["textContent"],ee={key:4,class:"row"},te=(0,l._)("div",{class:"label col-3"},"OS",-1),se=["textContent"],le={key:5,class:"row"},oe=(0,l._)("div",{class:"label col-3"},"Architecture",-1),ne=["textContent"],ie={key:6,class:"row"},ae=(0,l._)("div",{class:"label col-3"},"Server name",-1),ce=["textContent"],re={key:7,class:"row"},ue=(0,l._)("div",{class:"label col-3"},"Server version",-1),de=["textContent"],he={key:8,class:"row"},pe=(0,l._)("div",{class:"label col-3"},"Protocol version",-1),me=["textContent"],ve={key:9,class:"row"},ge=(0,l._)("div",{class:"label col-3"},"Control protocol version",-1),we=["textContent"];function fe(e,t,s,o,n,i){return(0,l.wg)(),(0,l.iD)("div",E,[s.info?.server?.host?.ip?.length?((0,l.wg)(),(0,l.iD)("div",A,[T,(0,l._)("div",{class:"value col-9",textContent:(0,d.zw)(s.info.server.host.ip)},null,8,P)])):(0,l.kq)("",!0),s.info?.server?.host?.mac?.length?((0,l.wg)(),(0,l.iD)("div",W,[L,(0,l._)("div",{class:"value col-9",textContent:(0,d.zw)(s.info.server.host.mac)},null,8,N)])):(0,l.kq)("",!0),s.info?.server?.host?.name?.length?((0,l.wg)(),(0,l.iD)("div",K,[Y,(0,l._)("div",{class:"value col-9",textContent:(0,d.zw)(s.info.server.host.name)},null,8,F)])):(0,l.kq)("",!0),s.info?.server?.host?.port?((0,l.wg)(),(0,l.iD)("div",J,[Q,(0,l._)("div",{class:"value col-9",textContent:(0,d.zw)(s.info.server.host.port)},null,8,X)])):(0,l.kq)("",!0),s.info?.server?.host?.os?.length?((0,l.wg)(),(0,l.iD)("div",ee,[te,(0,l._)("div",{class:"value col-9",textContent:(0,d.zw)(s.info.server.host.os)},null,8,se)])):(0,l.kq)("",!0),s.info?.server?.host?.arch?.length?((0,l.wg)(),(0,l.iD)("div",le,[oe,(0,l._)("div",{class:"value col-9",textContent:(0,d.zw)(s.info.server.host.arch)},null,8,ne)])):(0,l.kq)("",!0),s.info?.server?.snapserver?.name?.length?((0,l.wg)(),(0,l.iD)("div",ie,[ae,(0,l._)("div",{class:"value col-9",textContent:(0,d.zw)(s.info.server.snapserver.name)},null,8,ce)])):(0,l.kq)("",!0),s.info?.server?.snapserver?.version?.length?((0,l.wg)(),(0,l.iD)("div",re,[ue,(0,l._)("div",{class:"value col-9",textContent:(0,d.zw)(s.info.server.snapserver.version)},null,8,de)])):(0,l.kq)("",!0),s.info?.server?.snapserver?.protocolVersion?((0,l.wg)(),(0,l.iD)("div",he,[pe,(0,l._)("div",{class:"value col-9",textContent:(0,d.zw)(s.info.server.snapserver.protocolVersion)},null,8,me)])):(0,l.kq)("",!0),s.info?.server?.snapserver?.controlProtocolVersion?((0,l.wg)(),(0,l.iD)("div",ve,[ge,(0,l._)("div",{class:"value col-9",textContent:(0,d.zw)(s.info.server.snapserver.controlProtocolVersion)},null,8,we)])):(0,l.kq)("",!0)])}var _e={name:"HostModal",props:{info:{type:Object,default:()=>{}}}};const Ce=(0,j.Z)(_e,[["render",fe]]);var ye=Ce;const be=e=>((0,l.dD)("data-v-353ffa58"),e=e(),(0,l.Cn)(),e),ke={class:"info"},xe={class:"section name"},He=be((()=>(0,l._)("div",{class:"title"},"Name",-1))),Se={class:"row"},De={class:"name-value"},qe=["textContent"],Ge=be((()=>(0,l._)("i",{class:"fa fa-edit"},null,-1))),ze=[Ge],Me={key:0,class:"section clients"},je=be((()=>(0,l._)("div",{class:"title"},"Clients",-1))),$e=["for"],Oe=["id","value","checked","disabled","onInput"],Ie={key:1,class:"section streams"},Ue=be((()=>(0,l._)("div",{class:"title"},"Stream",-1))),Ze={class:"row"},Re=be((()=>(0,l._)("div",{class:"label col-3"},"ID",-1))),Ve={class:"value col-9"},Be=["textContent","name","value","disabled","selected"],Ee={key:0,class:"row"},Ae=be((()=>(0,l._)("div",{class:"label col-m-3"},"Status",-1))),Te=["textContent"],Pe={key:1,class:"row"},We=be((()=>(0,l._)("div",{class:"label col-s-12 col-m-3"},"Host",-1))),Le=["textContent"],Ne={key:2,class:"row"},Ke=be((()=>(0,l._)("div",{class:"label col-s-12 col-m-3"},"Path",-1))),Ye=["textContent"],Fe={key:3,class:"row"},Je=be((()=>(0,l._)("div",{class:"label col-s-12 col-m-3"},"URI",-1))),Qe=["textContent"];function Xe(e,t,s,o,n,i){return(0,l.wg)(),(0,l.iD)("div",ke,[(0,l._)("div",xe,[He,(0,l._)("div",Se,[(0,l._)("div",De,[(0,l._)("span",{class:"name",textContent:(0,d.zw)(s.group.name?.length?s.group.name:"default")},null,8,qe),(0,l._)("button",{class:"pull-right",title:"Rename",onClick:t[0]||(t[0]=(...e)=>i.renameGroup&&i.renameGroup(...e))},ze)])])]),Object.keys(s.group?.clients||{}).length>0?((0,l.wg)(),(0,l.iD)("div",Me,[je,((0,l.wg)(!0),(0,l.iD)(l.HY,null,(0,l.Ko)(s.clients||{},((t,o)=>((0,l.wg)(),(0,l.iD)("div",{class:"row",ref_for:!0,ref:"groupClients",key:o},[(0,l._)("label",{class:"client",for:"snapcast-client-"+t.id},[(0,l._)("input",{type:"checkbox",class:"client",id:`snapcast-client-${t.id}`,value:t.id,checked:t.id in s.group.clients,disabled:s.loading,onInput:s=>e.$emit(s.target.checked?"add-client":"remove-client",t.id)},null,40,Oe),(0,l.Uk)(" "+(0,d.zw)(t.host.name),1)],8,$e)])))),128))])):(0,l.kq)("",!0),s.group?.stream_id?((0,l.wg)(),(0,l.iD)("div",Ie,[Ue,(0,l._)("div",Ze,[Re,(0,l._)("div",Ve,[(0,l._)("label",null,[(0,l._)("select",{ref:"streamSelect",onChange:t[1]||(t[1]=t=>e.$emit("stream-change",t.target.value))},[((0,l.wg)(!0),(0,l.iD)(l.HY,null,(0,l.Ko)(s.streams,((e,t)=>((0,l.wg)(),(0,l.iD)("option",{key:t,textContent:(0,d.zw)(s.streams[s.group.stream_id].id),name:e.id,value:e.id,disabled:s.loading,selected:e.id===s.group.stream_id},null,8,Be)))),128))],544)])])]),s.streams?.[s.group.stream_id]?.status?((0,l.wg)(),(0,l.iD)("div",Ee,[Ae,(0,l._)("div",{class:"value col-m-9",textContent:(0,d.zw)(s.streams[s.group.stream_id].status)},null,8,Te)])):(0,l.kq)("",!0),s.streams?.[s.group?.stream_id]?.uri?.host?((0,l.wg)(),(0,l.iD)("div",Pe,[We,(0,l._)("div",{class:"value col-s-12 col-m-9",textContent:(0,d.zw)(s.streams[s.group.stream_id].uri.host)},null,8,Le)])):(0,l.kq)("",!0),s.streams?.[s.group?.stream_id]?.uri?.path?((0,l.wg)(),(0,l.iD)("div",Ne,[Ke,(0,l._)("div",{class:"value col-s-12 col-m-9",textContent:(0,d.zw)(s.streams[s.group.stream_id].uri.path)},null,8,Ye)])):(0,l.kq)("",!0),s.streams?.[s.group?.stream_id]?.uri?.raw?((0,l.wg)(),(0,l.iD)("div",Fe,[Je,(0,l._)("div",{class:"value col-s-12 col-m-9",textContent:(0,d.zw)(s.streams[s.group.stream_id].uri.raw)},null,8,Qe)])):(0,l.kq)("",!0)])):(0,l.kq)("",!0)])}var et={name:"GroupModal",emits:["add-client","remove-client","stream-change","rename-group"],props:{loading:{type:Boolean,default:!1},group:{type:Object},clients:{type:Object},streams:{type:Object}},methods:{renameGroup(){const e=(prompt("New group name",this.group.name)||"").trim();e?.length&&this.$emit("rename-group",e)}}};const tt=(0,j.Z)(et,[["render",Xe],["__scopeId","data-v-353ffa58"]]);var st=tt;const lt=e=>((0,l.dD)("data-v-0e55ac54"),e=e(),(0,l.Cn)(),e),ot={class:"client-modal"},nt={key:0,class:"info"},it={class:"row"},at=lt((()=>(0,l._)("div",{class:"label col-s-12 col-m-3"},"ID",-1))),ct=["textContent"],rt={key:0,class:"row"},ut=lt((()=>(0,l._)("div",{class:"label col-s-12 col-m-3"},"Name",-1))),dt={class:"value col-s-12 col-m-9"},ht=["textContent"],pt=lt((()=>(0,l._)("i",{class:"fa fa-edit"},null,-1))),mt=[pt],vt={class:"row"},gt=lt((()=>(0,l._)("div",{class:"label col-s-12 col-m-3"},"Connected",-1))),wt=["textContent"],ft={class:"row"},_t=lt((()=>(0,l._)("div",{class:"label col-s-12 col-m-3"},"Volume",-1))),Ct={class:"value col-s-12 col-m-9"},yt={class:"row"},bt=lt((()=>(0,l._)("div",{class:"label col-s-12 col-m-3"},"Muted",-1))),kt=["textContent"],xt={class:"row"},Ht=lt((()=>(0,l._)("div",{class:"label col-s-12 col-m-3"},"Latency",-1))),St=["textContent"],Dt={key:1,class:"row"},qt=lt((()=>(0,l._)("div",{class:"label col-s-12 col-m-3"},"IP Address",-1))),Gt=["textContent"],zt={key:2,class:"row"},Mt=lt((()=>(0,l._)("div",{class:"label col-s-12 col-m-3"},"MAC Address",-1))),jt=["textContent"],$t={key:3,class:"row"},Ot=lt((()=>(0,l._)("div",{class:"label col-s-12 col-m-3"},"OS",-1))),It=["textContent"],Ut={key:4,class:"row"},Zt=lt((()=>(0,l._)("div",{class:"label col-s-12 col-m-3"},"Architecture",-1))),Rt=["textContent"],Vt={class:"row"},Bt=lt((()=>(0,l._)("div",{class:"label col-s-12 col-m-3"},"Client name",-1))),Et=["textContent"],At={class:"row"},Tt=lt((()=>(0,l._)("div",{class:"label col-s-12 col-m-3"},"Client version",-1))),Pt=["textContent"],Wt={class:"row"},Lt=lt((()=>(0,l._)("div",{class:"label col-s-12 col-m-3"},"Protocol version",-1))),Nt=["textContent"],Kt={class:"buttons"},Yt={class:"row"},Ft=["disabled"],Jt=lt((()=>(0,l._)("i",{class:"fas fa-trash"},null,-1))),Qt=lt((()=>(0,l._)("span",{class:"name"},"Remove client",-1))),Xt=[Jt,Qt];function es(e,t,s,o,n,i){return(0,l.wg)(),(0,l.iD)("div",ot,[s.client?((0,l.wg)(),(0,l.iD)("div",nt,[(0,l._)("div",it,[at,(0,l._)("div",{class:"value col-s-12 col-m-9",textContent:(0,d.zw)(s.client.id)},null,8,ct)]),s.client.config?.name?.length||s.client.host?.name?((0,l.wg)(),(0,l.iD)("div",rt,[ut,(0,l._)("div",dt,[(0,l._)("span",{class:"name",textContent:(0,d.zw)(s.client.config?.name||s.client.host?.name)},null,8,ht),(0,l._)("button",{title:"Rename",onClick:t[0]||(t[0]=(...e)=>i.renameClient&&i.renameClient(...e))},mt)])])):(0,l.kq)("",!0),(0,l._)("div",vt,[gt,(0,l._)("div",{class:"value col-s-12 col-m-9",textContent:(0,d.zw)(s.client.connected)},null,8,wt)]),(0,l._)("div",ft,[_t,(0,l._)("div",Ct,(0,d.zw)(s.client.config.volume.percent)+"%",1)]),(0,l._)("div",yt,[bt,(0,l._)("div",{class:"value col-s-12 col-m-9",textContent:(0,d.zw)(s.client.config.volume.muted)},null,8,kt)]),(0,l._)("div",xt,[Ht,(0,l._)("div",{class:"value col-s-12 col-m-9",textContent:(0,d.zw)(s.client.config.latency)},null,8,St)]),s.client.host.ip&&s.client.host.ip.length?((0,l.wg)(),(0,l.iD)("div",Dt,[qt,(0,l._)("div",{class:"value col-s-12 col-m-9",textContent:(0,d.zw)(s.client.host.ip)},null,8,Gt)])):(0,l.kq)("",!0),s.client.host.mac&&s.client.host.mac.length?((0,l.wg)(),(0,l.iD)("div",zt,[Mt,(0,l._)("div",{class:"value col-s-12 col-m-9",textContent:(0,d.zw)(s.client.host.mac)},null,8,jt)])):(0,l.kq)("",!0),s.client.host.os&&s.client.host.os.length?((0,l.wg)(),(0,l.iD)("div",$t,[Ot,(0,l._)("div",{class:"value col-s-12 col-m-9",textContent:(0,d.zw)(s.client.host.os)},null,8,It)])):(0,l.kq)("",!0),s.client.host.arch&&s.client.host.arch.length?((0,l.wg)(),(0,l.iD)("div",Ut,[Zt,(0,l._)("div",{class:"value col-s-12 col-m-9",textContent:(0,d.zw)(s.client.host.arch)},null,8,Rt)])):(0,l.kq)("",!0),(0,l._)("div",Vt,[Bt,(0,l._)("div",{class:"value col-s-12 col-m-9",textContent:(0,d.zw)(s.client.snapclient.name)},null,8,Et)]),(0,l._)("div",At,[Tt,(0,l._)("div",{class:"value col-s-12 col-m-9",textContent:(0,d.zw)(s.client.snapclient.version)},null,8,Pt)]),(0,l._)("div",Wt,[Lt,(0,l._)("div",{class:"value col-s-12 col-m-9",textContent:(0,d.zw)(s.client.snapclient.protocolVersion)},null,8,Nt)])])):(0,l.kq)("",!0),(0,l._)("div",Kt,[(0,l._)("div",Yt,[(0,l._)("button",{type:"button",disabled:s.loading,onClick:t[1]||(t[1]=(...e)=>i.removeClient&&i.removeClient(...e))},Xt,8,Ft)])])])}var ts={name:"ClientModal",emits:["remove-client","rename-client"],props:{loading:{type:Boolean,default:!1},client:{type:Object}},methods:{removeClient(){window.confirm("Are you sure that you want to remove this client?")&&this.$emit("remove-client")},renameClient(){const e=(window.prompt("New client name",this.client.config.name?.length?this.client.config.name:this.client.host.name)||"").trim();e.length&&this.$emit("rename-client",e)}}};const ss=(0,j.Z)(ts,[["render",es],["__scopeId","data-v-0e55ac54"]]);var ls=ss,os=s(6791),ns={name:"MusicSnapcast",mixins:[u.Z],components:{Loading:os.Z,Modal:r.Z,Host:B,ModalHost:ye,ModalGroup:st,ModalClient:ls},data:function(){return{loading:!1,hosts:{},ports:{},selectedHost:null,selectedGroup:null,selectedClient:null}},computed:{clientsByHost(){return Object.entries(this.hosts).reduce(((e,[t,s])=>(e[t]={},Object.values(s.groups).forEach((s=>{Object.entries(s.clients).forEach((([s,l])=>{e[t][s]=l}))})),e)),{})}},methods:{parseServerStatus(e){e.server.host.port=this.ports[e.server.host.name],this.hosts[e.server.host.name]={...e,groups:e.groups.map((e=>({...e,clients:e.clients.reduce(((e,t)=>(e[t.id]=t,e)),{})}))).reduce(((e,t)=>(e[t.id]=t,e)),{}),streams:e.streams.reduce(((e,t)=>(e[t.id]=t,e)),{})}},async refresh(){this.loading=!0;try{const e=await this.request("music.snapcast.get_backend_hosts"),t=await Promise.all(Object.keys(e).map((async t=>this.request("music.snapcast.status",{host:t,port:e[t]}))));this.hosts={},t.forEach((t=>{this.ports[t.server.host.name]=e[t.server.host.name],this.parseServerStatus(t)}))}finally{this.loading=!1}},async refreshHost(e){e in this.hosts&&this.parseServerStatus(await this.request("music.snapcast.status",{host:e,port:this.ports[e]}))},async addClientToGroup(e){this.loading=!0;try{if(!this.selectedHost||!this.selectedGroup||!(e in this.clientsByHost[this.selectedHost]))return;const t=[...new Set([e,...Object.keys(this.hosts[this.selectedHost].groups[this.selectedGroup].clients)])];await this.request("music.snapcast.group_set_clients",{host:this.selectedHost,port:this.ports[this.selectedHost],group:this.selectedGroup,clients:t}),await this.refreshHost(this.selectedHost)}finally{this.loading=!1}},async removeClientFromGroup(e){this.loading=!0;try{if(!this.selectedHost||!this.selectedGroup||!(e in this.clientsByHost[this.selectedHost]))return;const t=new Set([...Object.keys(this.hosts[this.selectedHost].groups[this.selectedGroup].clients)]);if(!t.has(e))return;t.delete(e),await this.request("music.snapcast.group_set_clients",{host:this.selectedHost,port:this.ports[this.selectedHost],group:this.selectedGroup,clients:[...t]}),await this.refreshHost(this.selectedHost)}finally{this.loading=!1}},async renameGroup(e){this.loading=!0;try{if(!this.selectedHost||!this.selectedGroup)return;await this.request("music.snapcast.set_group_name",{host:this.selectedHost,port:this.ports[this.selectedHost],group:this.selectedGroup,name:e}),await this.refreshHost(this.selectedHost)}finally{this.loading=!1}},async renameClient(e){this.loading=!0;try{if(!this.selectedHost||!this.selectedClient)return;await this.request("music.snapcast.set_client_name",{host:this.selectedHost,port:this.ports[this.selectedHost],client:this.selectedClient,name:e}),await this.refreshHost(this.selectedHost)}finally{this.loading=!1}},async removeClient(){this.loading=!0;try{if(!this.selectedHost||!this.selectedClient)return;await this.request("music.snapcast.delete_client",{host:this.selectedHost,port:this.ports[this.selectedHost],client:this.selectedClient}),this.$refs.modalClient.close(),await this.refreshHost(this.selectedHost)}finally{this.loading=!1}},async streamChange(e){this.loading=!0;try{await this.request("music.snapcast.group_set_stream",{host:this.selectedHost,port:this.ports[this.selectedHost],group:this.selectedGroup,stream_id:e}),await this.refreshHost(this.selectedHost)}finally{this.loading=!1}},onClientUpdate(e){Object.keys(this.hosts[e.host].groups).forEach((t=>{e.client.id in this.hosts[e.host].groups[t].clients&&(this.hosts[e.host].groups[t].clients[e.client.id]=e.client)}))},onGroupStreamChange(e){this.hosts[e.host].groups[e.group].stream_id=e.stream},onServerUpdate(e){this.parseServerStatus(e.server)},onStreamUpdate(e){this.hosts[e.host].streams[e.stream.id]=e.stream},onClientVolumeChange(e){Object.keys(this.hosts[e.host].groups).forEach((t=>{e.client in this.hosts[e.host].groups[t].clients&&(null!=e.volume&&(this.hosts[e.host].groups[t].clients[e.client].config.volume.percent=e.volume),null!=e.muted&&(this.hosts[e.host].groups[t].clients[e.client].config.volume.muted=e.muted))}))},onGroupMuteChange(e){this.hosts[e.host].groups[e.group].muted=e.muted},modalShow(e){switch(e.type){case"host":this.modal[e.type].info=this.hosts[e.host];break;case"group":this.modal[e.type].info.server=this.hosts[e.host].server,this.modal[e.type].info.group=this.hosts[e.host].groups[e.group],this.modal[e.type].info.streams=this.hosts[e.host].streams,this.modal[e.type].info.clients={};for(const t of Object.values(this.hosts[e.host].groups))for(const s of Object.values(t.clients))this.modal[e.type].info.clients[s.id]=s;break;case"client":this.modal[e.type].info=this.hosts[e.host].groups[e.group].clients[e.client],this.modal[e.type].info.server=this.hosts[e.host].server;break}this.modal[e.type].visible=!0},async groupMute(e){await this.request("music.snapcast.mute",{group:e.group,host:e.host,port:this.ports[e.host],mute:e.muted}),await this.refreshHost(e.host)},async clientMute(e){await this.request("music.snapcast.mute",{client:e.client,host:e.host,port:this.ports[e.host],mute:e.muted}),await this.refreshHost(e.host)},async clientSetVolume(e){await this.request("music.snapcast.volume",{client:e.client,host:e.host,port:this.ports[e.host],volume:e.volume}),await this.refreshHost(e.host)},onModalShow(e){switch(e.type){case"host":this.selectedHost=e.host,this.$refs.modalHost.show();break;case"group":this.selectedHost=e.host,this.selectedGroup=e.group,this.$refs.modalGroup.show();break;case"client":this.selectedHost=e.host,this.selectedGroup=e.group,this.selectedClient=e.client,this.$refs.modalClient.show();break}}},mounted(){this.refresh(),this.subscribe(this.onClientUpdate,null,"platypush.message.event.music.snapcast.ClientConnectedEvent","platypush.message.event.music.snapcast.ClientDisconnectedEvent","platypush.message.event.music.snapcast.ClientNameChangeEvent"),this.subscribe(this.onGroupStreamChange,null,"platypush.message.event.music.snapcast.GroupStreamChangeEvent"),this.subscribe(this.onServerUpdate,null,"platypush.message.event.music.snapcast.ServerUpdateEvent"),this.subscribe(this.onStreamUpdate,null,"platypush.message.event.music.snapcast.StreamUpdateEvent"),this.subscribe(this.onClientVolumeChange,null,"platypush.message.event.music.snapcast.ClientVolumeChangeEvent"),this.subscribe(this.onGroupMuteChange,null,"platypush.message.event.music.snapcast.GroupMuteChangeEvent")}};const is=(0,j.Z)(ns,[["render",c],["__scopeId","data-v-40841f5a"]]);var as=is}}]);
//# sourceMappingURL=7126.34f160c8.js.map