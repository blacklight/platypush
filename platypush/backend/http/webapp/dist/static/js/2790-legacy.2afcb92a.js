(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[2790],{7556:function(e,t,n){var s=n(7293);e.exports=s((function(){if("function"==typeof ArrayBuffer){var e=new ArrayBuffer(8);Object.isExtensible(e)&&Object.defineProperty(e,"a",{value:8})}}))},5631:function(e,t,n){"use strict";var s=n(3070).f,o=n(30),r=n(9190),i=n(9974),l=n(5787),a=n(408),u=n(654),c=n(6340),d=n(9781),v=n(2423).fastKey,p=n(9909),m=p.set,f=p.getterFor;e.exports={getConstructor:function(e,t,n,u){var c=e((function(e,s){l(e,p),m(e,{type:t,index:o(null),first:void 0,last:void 0,size:0}),d||(e.size=0),void 0!=s&&a(s,e[u],{that:e,AS_ENTRIES:n})})),p=c.prototype,h=f(t),g=function(e,t,n){var s,o,r=h(e),i=w(e,t);return i?i.value=n:(r.last=i={index:o=v(t,!0),key:t,value:n,previous:s=r.last,next:void 0,removed:!1},r.first||(r.first=i),s&&(s.next=i),d?r.size++:e.size++,"F"!==o&&(r.index[o]=i)),e},w=function(e,t){var n,s=h(e),o=v(t);if("F"!==o)return s.index[o];for(n=s.first;n;n=n.next)if(n.key==t)return n};return r(p,{clear:function(){var e=this,t=h(e),n=t.index,s=t.first;while(s)s.removed=!0,s.previous&&(s.previous=s.previous.next=void 0),delete n[s.index],s=s.next;t.first=t.last=void 0,d?t.size=0:e.size=0},delete:function(e){var t=this,n=h(t),s=w(t,e);if(s){var o=s.next,r=s.previous;delete n.index[s.index],s.removed=!0,r&&(r.next=o),o&&(o.previous=r),n.first==s&&(n.first=o),n.last==s&&(n.last=r),d?n.size--:t.size--}return!!s},forEach:function(e){var t,n=h(this),s=i(e,arguments.length>1?arguments[1]:void 0);while(t=t?t.next:n.first){s(t.value,t.key,this);while(t&&t.removed)t=t.previous}},has:function(e){return!!w(this,e)}}),r(p,n?{get:function(e){var t=w(this,e);return t&&t.value},set:function(e,t){return g(this,0===e?0:e,t)}}:{add:function(e){return g(this,e=0===e?0:e,e)}}),d&&s(p,"size",{get:function(){return h(this).size}}),c},setStrong:function(e,t,n){var s=t+" Iterator",o=f(t),r=f(s);u(e,t,(function(e,t){m(this,{type:s,target:e,state:o(e),kind:t,last:void 0})}),(function(){var e=r(this),t=e.kind,n=e.last;while(n&&n.removed)n=n.previous;return e.target&&(e.last=n=n?n.next:e.state.first)?"keys"==t?{value:n.key,done:!1}:"values"==t?{value:n.value,done:!1}:{value:[n.key,n.value],done:!1}:(e.target=void 0,{value:void 0,done:!0})}),n?"entries":"values",!n,!0),c(t)}}},7710:function(e,t,n){"use strict";var s=n(2109),o=n(7854),r=n(1702),i=n(4705),l=n(8052),a=n(2423),u=n(408),c=n(5787),d=n(614),v=n(111),p=n(7293),m=n(7072),f=n(8003),h=n(9587);e.exports=function(e,t,n){var g=-1!==e.indexOf("Map"),w=-1!==e.indexOf("Weak"),_=g?"set":"add",C=o[e],y=C&&C.prototype,b=C,x={},k=function(e){var t=r(y[e]);l(y,e,"add"==e?function(e){return t(this,0===e?0:e),this}:"delete"==e?function(e){return!(w&&!v(e))&&t(this,0===e?0:e)}:"get"==e?function(e){return w&&!v(e)?void 0:t(this,0===e?0:e)}:"has"==e?function(e){return!(w&&!v(e))&&t(this,0===e?0:e)}:function(e,n){return t(this,0===e?0:e,n),this})},H=i(e,!d(C)||!(w||y.forEach&&!p((function(){(new C).entries().next()}))));if(H)b=n.getConstructor(t,e,g,_),a.enable();else if(i(e,!0)){var S=new b,D=S[_](w?{}:-0,1)!=S,q=p((function(){S.has(1)})),z=m((function(e){new C(e)})),M=!w&&p((function(){var e=new C,t=5;while(t--)e[_](t,t);return!e.has(-0)}));z||(b=t((function(e,t){c(e,y);var n=h(new C,e,b);return void 0!=t&&u(t,n[_],{that:n,AS_ENTRIES:g}),n})),b.prototype=y,y.constructor=b),(q||M)&&(k("delete"),k("has"),g&&k("get")),(M||D)&&k(_),w&&y.clear&&delete y.clear}return x[e]=b,s({global:!0,constructor:!0,forced:b!=C},x),f(b,e),w||n.setStrong(b,e,g),b}},9190:function(e,t,n){var s=n(8052);e.exports=function(e,t,n){for(var o in t)s(e,o,t[o],n);return e}},6677:function(e,t,n){var s=n(7293);e.exports=!s((function(){return Object.isExtensible(Object.preventExtensions({}))}))},2423:function(e,t,n){var s=n(2109),o=n(1702),r=n(3501),i=n(111),l=n(2597),a=n(3070).f,u=n(8006),c=n(1156),d=n(2050),v=n(9711),p=n(6677),m=!1,f=v("meta"),h=0,g=function(e){a(e,f,{value:{objectID:"O"+h++,weakData:{}}})},w=function(e,t){if(!i(e))return"symbol"==typeof e?e:("string"==typeof e?"S":"P")+e;if(!l(e,f)){if(!d(e))return"F";if(!t)return"E";g(e)}return e[f].objectID},_=function(e,t){if(!l(e,f)){if(!d(e))return!0;if(!t)return!1;g(e)}return e[f].weakData},C=function(e){return p&&m&&d(e)&&!l(e,f)&&g(e),e},y=function(){b.enable=function(){},m=!0;var e=u.f,t=o([].splice),n={};n[f]=1,e(n).length&&(u.f=function(n){for(var s=e(n),o=0,r=s.length;o<r;o++)if(s[o]===f){t(s,o,1);break}return s},s({target:"Object",stat:!0,forced:!0},{getOwnPropertyNames:c.f}))},b=e.exports={enable:y,fastKey:w,getWeakData:_,onFreeze:C};r[f]=!0},2050:function(e,t,n){var s=n(7293),o=n(111),r=n(4326),i=n(7556),l=Object.isExtensible,a=s((function(){l(1)}));e.exports=a||i?function(e){return!!o(e)&&((!i||"ArrayBuffer"!=r(e))&&(!l||l(e)))}:l},6091:function(e,t,n){var s=n(6530).PROPER,o=n(7293),r=n(1361),i="​᠎";e.exports=function(e){return o((function(){return!!r[e]()||i[e]()!==i||s&&r[e].name!==e}))}},7227:function(e,t,n){"use strict";var s=n(7710),o=n(5631);s("Set",(function(e){return function(){return e(this,arguments.length?arguments[0]:void 0)}}),o)},189:function(e,t,n){n(7227)},3210:function(e,t,n){"use strict";var s=n(2109),o=n(3111).trim,r=n(6091);s({target:"String",proto:!0,forced:r("trim")},{trim:function(){return o(this)}})},376:function(e,t,n){"use strict";n.d(t,{Z:function(){return g}});var s=n(6252),o=n(9963),r=n(3577),i={class:"slider-wrapper"},l=["min","max","step","disabled","value"],a={class:"track"},u={class:"track-inner",ref:"track"},c={class:"thumb",ref:"thumb"},d=["textContent"];function v(e,t,n,v,p,m){return(0,s.wg)(),(0,s.iD)("label",i,[(0,s._)("input",{class:"slider",type:"range",ref:"range",min:n.range[0],max:n.range[1],step:n.step,disabled:n.disabled,value:n.value,onInput:t[0]||(t[0]=(0,o.iM)((function(){return m.onUpdate&&m.onUpdate.apply(m,arguments)}),["stop"])),onChange:t[1]||(t[1]=(0,o.iM)((function(){return m.onUpdate&&m.onUpdate.apply(m,arguments)}),["stop"])),onMouseup:t[2]||(t[2]=(0,o.iM)((function(){return m.onUpdate&&m.onUpdate.apply(m,arguments)}),["stop"])),onMousedown:t[3]||(t[3]=(0,o.iM)((function(){return m.onUpdate&&m.onUpdate.apply(m,arguments)}),["stop"])),onTouchstart:t[4]||(t[4]=(0,o.iM)((function(){return m.onUpdate&&m.onUpdate.apply(m,arguments)}),["stop"])),onTouchend:t[5]||(t[5]=(0,o.iM)((function(){return m.onUpdate&&m.onUpdate.apply(m,arguments)}),["stop"])),onKeyup:t[6]||(t[6]=(0,o.iM)((function(){return m.onUpdate&&m.onUpdate.apply(m,arguments)}),["stop"])),onKeydown:t[7]||(t[7]=(0,o.iM)((function(){return m.onUpdate&&m.onUpdate.apply(m,arguments)}),["stop"]))},null,40,l),(0,s._)("div",a,[(0,s._)("div",u,null,512)]),(0,s._)("div",c,null,512),n.withLabel?((0,s.wg)(),(0,s.iD)("span",{key:0,class:"label",textContent:(0,r.zw)(n.value)},null,8,d)):(0,s.kq)("",!0)])}var p=n(4648),m=(n(9653),{name:"Slider",emits:["input","change","mouseup","mousedown","touchstart","touchend","keyup","keydown"],props:{value:{type:Number},disabled:{type:Boolean,default:!1},range:{type:Array,default:function(){return[0,100]}},step:{type:Number,default:1},withLabel:{type:Boolean,default:!1}},methods:{onUpdate:function(e){this.update(e.target.value),this.$emit(e.type,(0,p.Z)((0,p.Z)({},e),{},{target:(0,p.Z)((0,p.Z)({},e.target),{},{value:this.$refs.range.value})}))},update:function(e){var t=100*(e-this.range[0])/(this.range[1]-this.range[0]);this.$refs.thumb.style.left="".concat(t,"%"),this.$refs.thumb.style.transform="translate(-".concat(t,"%, -50%)"),this.$refs.track.style.width="".concat(t,"%")}},mounted:function(){null!=this.value&&this.update(this.value)}}),f=n(3744);const h=(0,f.Z)(m,[["render",v],["__scopeId","data-v-95edc28a"]]);var g=h},6:function(e,t,n){"use strict";n.d(t,{Z:function(){return m}});var s=n(6252),o=n(3577),r=n(9963),i=function(e){return(0,s.dD)("data-v-a6396ae8"),e=e(),(0,s.Cn)(),e},l=["checked"],a=i((function(){return(0,s._)("div",{class:"switch"},[(0,s._)("div",{class:"dot"})],-1)})),u={class:"label"};function c(e,t,n,i,c,d){return(0,s.wg)(),(0,s.iD)("div",{class:(0,o.C_)(["power-switch",{disabled:n.disabled}]),onClick:t[0]||(t[0]=(0,r.iM)((function(){return d.onInput&&d.onInput.apply(d,arguments)}),["stop"]))},[(0,s._)("input",{type:"checkbox",checked:n.value},null,8,l),(0,s._)("label",null,[a,(0,s._)("span",u,[(0,s.WI)(e.$slots,"default",{},void 0,!0)])])],2)}var d={name:"ToggleSwitch",emits:["input"],props:{value:{type:Boolean,default:!1},disabled:{type:Boolean,default:!1}},methods:{onInput:function(e){if(this.disabled)return!1;this.$emit("input",e)}}},v=n(3744);const p=(0,v.Z)(d,[["render",c],["__scopeId","data-v-a6396ae8"]]);var m=p},2790:function(e,t,n){"use strict";n.r(t),n.d(t,{default:function(){return vn}});var s=n(6252),o={class:"music-snapcast-container"},r={class:"info"},i={class:"info"},l={class:"info"};function a(e,t,n,a,u,c){var d=(0,s.up)("Loading"),v=(0,s.up)("ModalHost"),p=(0,s.up)("Modal"),m=(0,s.up)("ModalGroup"),f=(0,s.up)("ModalClient"),h=(0,s.up)("Host");return(0,s.wg)(),(0,s.iD)("div",o,[e.loading?((0,s.wg)(),(0,s.j4)(d,{key:0})):(0,s.kq)("",!0),(0,s._)("div",r,[(0,s.Wm)(p,{title:"Server info",ref:"modalHost"},{default:(0,s.w5)((function(){return[e.selectedHost?((0,s.wg)(),(0,s.j4)(v,{key:0,info:e.hosts[e.selectedHost]},null,8,["info"])):(0,s.kq)("",!0)]})),_:1},512)]),(0,s._)("div",i,[(0,s.Wm)(p,{title:"Group info",ref:"modalGroup"},{default:(0,s.w5)((function(){return[e.selectedGroup?((0,s.wg)(),(0,s.j4)(m,{key:0,group:e.hosts[e.selectedHost].groups[e.selectedGroup],streams:e.hosts[e.selectedHost].streams,clients:c.clientsByHost[e.selectedHost],loading:e.loading,onAddClient:c.addClientToGroup,onRemoveClient:c.removeClientFromGroup,onStreamChange:c.streamChange,onRenameGroup:t[0]||(t[0]=function(e){return c.renameGroup(e)})},null,8,["group","streams","clients","loading","onAddClient","onRemoveClient","onStreamChange"])):(0,s.kq)("",!0)]})),_:1},512)]),(0,s._)("div",l,[(0,s.Wm)(p,{title:"Client info",ref:"modalClient"},{default:(0,s.w5)((function(){return[e.selectedClient?((0,s.wg)(),(0,s.j4)(f,{key:0,client:e.hosts[e.selectedHost].groups[e.selectedGroup].clients[e.selectedClient],loading:e.loading,onRemoveClient:c.removeClient,onRenameClient:t[1]||(t[1]=function(e){return c.renameClient(e)})},null,8,["client","loading","onRemoveClient"])):(0,s.kq)("",!0)]})),_:1},512)]),((0,s.wg)(!0),(0,s.iD)(s.HY,null,(0,s.Ko)(e.hosts,(function(e,n){return(0,s.wg)(),(0,s.j4)(h,{key:n,server:e.server,streams:e.streams,groups:e.groups,onGroupMuteToggle:t[2]||(t[2]=function(e){return c.groupMute(e)}),onClientMuteToggle:t[3]||(t[3]=function(e){return c.clientMute(e)}),onClientVolumeChange:t[4]||(t[4]=function(e){return c.clientSetVolume(e)}),onModalShow:t[5]||(t[5]=function(e){return c.onModalShow(e)})},null,8,["server","streams","groups"])})),128))])}var u=n(9584),c=n(8534),d=n(4648),v=n(6084),p=(n(5666),n(1539),n(9720),n(4747),n(2479),n(8309),n(1249),n(8783),n(3948),n(7941),n(189),n(2222),n(8453)),m=n(6813),f=n(3577),h=function(e){return(0,s.dD)("data-v-7bce419a"),e=e(),(0,s.Cn)(),e},g={class:"host"},w={class:"header"},_=h((function(){return(0,s._)("i",{class:"icon fa fa-server"},null,-1)})),C={class:"col-2 buttons pull-right"},y={key:0,class:"group-container"};function b(e,t,n,o,r,i){var l=(0,s.up)("Group");return(0,s.wg)(),(0,s.iD)("div",g,[(0,s._)("div",w,[(0,s._)("div",{class:"col-10 name",onClick:t[0]||(t[0]=function(t){return e.$emit("modal-show",{type:"host",host:n.server.host.name})})},[_,(0,s.Uk)(" "+(0,f.zw)(n.server.host.name),1)]),(0,s._)("div",C,[(0,s._)("button",{type:"button",onClick:t[1]||(t[1]=function(e){return r.collapsed=!r.collapsed})},[(0,s._)("i",{class:(0,f.C_)(["icon fa",{"fa-chevron-up":!r.collapsed,"fa-chevron-down":r.collapsed}])},null,2)])])]),r.collapsed?(0,s.kq)("",!0):((0,s.wg)(),(0,s.iD)("div",y,[((0,s.wg)(!0),(0,s.iD)(s.HY,null,(0,s.Ko)(n.groups,(function(o,r){return(0,s.wg)(),(0,s.j4)(l,{key:r,id:o.id,name:o.name,server:n.server.host,muted:o.muted,clients:o.clients,stream:n.streams[o.stream_id],onModalShow:t[2]||(t[2]=function(t){return e.$emit("modal-show",t)}),onGroupMuteToggle:t[3]||(t[3]=function(t){return e.$emit("group-mute-toggle",t)}),onClientMuteToggle:t[4]||(t[4]=function(t){return e.$emit("client-mute-toggle",t)}),onClientVolumeChange:t[5]||(t[5]=function(t){return e.$emit("client-volume-change",t)})},null,8,["id","name","server","muted","clients","stream"])})),128))]))])}var x={class:"group"},k={class:"head"},H={class:"col-2 switch pull-right"},S={class:"body"};function D(e,t,n,o,r,i){var l=(0,s.up)("ToggleSwitch"),a=(0,s.up)("Client");return(0,s.wg)(),(0,s.iD)("div",x,[(0,s._)("div",k,[(0,s._)("div",{class:"col-10 name",onClick:t[0]||(t[0]=function(t){return e.$emit("modal-show",{type:"group",group:n.id,host:n.server.name})})},[(0,s._)("i",{class:(0,f.C_)(["icon fa",{"fa-play":"playing"===n.stream.status,"fa-stop":"playing"!==n.stream.status}])},null,2),(0,s.Uk)(" "+(0,f.zw)(n.name||n.stream.id||n.id),1)]),(0,s._)("div",H,[(0,s.Wm)(l,{value:!n.muted,onInput:t[1]||(t[1]=function(t){return e.$emit("group-mute-toggle",{host:n.server.name,group:n.id,muted:!n.muted})})},null,8,["value"])])]),(0,s._)("div",S,[((0,s.wg)(!0),(0,s.iD)(s.HY,null,(0,s.Ko)(n.clients,(function(o){return(0,s.wg)(),(0,s.j4)(a,{key:o.id,config:o.config,connected:o.connected,server:n.server,host:o.host,groupId:n.id,id:o.id,lastSeen:o.lastSeen,snapclient:o.snapclient,onModalShow:t[2]||(t[2]=function(t){return e.$emit("modal-show",t)}),onVolumeChange:t[3]||(t[3]=function(t){return e.$emit("client-volume-change",t)}),onMuteToggle:t[4]||(t[4]=function(t){return e.$emit("client-mute-toggle",t)})},null,8,["config","connected","server","host","groupId","id","lastSeen","snapclient"])})),128))])])}var q=n(6),z=["textContent"],M={class:"col-s-12 col-m-9 controls"},Z={class:"col-10 slider-container"},j={class:"col-2 switch pull-right"};function G(e,t,n,o,r,i){var l,a=(0,s.up)("Slider"),u=(0,s.up)("ToggleSwitch");return(0,s.wg)(),(0,s.iD)("div",{class:(0,f.C_)(["row client",{offline:!n.connected}])},[(0,s._)("div",{class:"col-s-12 col-m-3 name",textContent:(0,f.zw)(null!==(l=n.config.name)&&void 0!==l&&l.length?n.config.name:n.host.name),onClick:t[0]||(t[0]=function(t){return e.$emit("modal-show",{type:"client",client:n.id,group:n.groupId,host:n.server.name})})},null,8,z),(0,s._)("div",M,[(0,s._)("div",Z,[(0,s.Wm)(a,{range:[0,100],value:n.config.volume.percent,onMouseup:t[1]||(t[1]=function(t){return e.$emit("volume-change",{host:n.server.name,client:n.id,volume:t.target.value})})},null,8,["value"])]),(0,s._)("div",j,[(0,s.Wm)(u,{value:!n.config.volume.muted,onInput:t[2]||(t[2]=function(t){return e.$emit("mute-toggle",{host:n.server.name,client:n.id,muted:!n.config.volume.muted})})},null,8,["value"])])])],2)}var O=n(376),R={name:"Client",components:{Slider:O.Z,ToggleSwitch:q.Z},emits:["volume-change","mute-toggle","modal-show"],props:{config:{type:Object,required:!0},connected:{type:Boolean,default:!1},host:{type:Object,required:!0},id:{type:String,required:!0},groupId:{type:String,required:!0},lastSeen:{type:Object,default:function(){}},snapclient:{type:Object,required:!0},server:{type:Object,required:!0}}},I=n(3744);const U=(0,I.Z)(R,[["render",G],["__scopeId","data-v-12b0e65b"]]);var $=U,E={name:"Group",components:{Client:$,ToggleSwitch:q.Z},emits:["group-mute-toggle","modal-show","client-volume-change","client-mute-toggle"],props:{id:{type:String},clients:{type:Object,default:function(){}},muted:{type:Boolean},name:{type:String},stream:{type:Object},server:{type:Object}}};const A=(0,I.Z)(E,[["render",D],["__scopeId","data-v-748fccb4"]]);var T=A,B={name:"Host",emits:["modal-show","group-mute-toggle","client-mute-toggle","client-volume-change"],components:{Group:T},props:{groups:{type:Object,default:function(){}},server:{type:Object,default:function(){}},streams:{type:Object,default:function(){}}},data:function(){return{collapsed:!1}}};const P=(0,I.Z)(B,[["render",b],["__scopeId","data-v-7bce419a"]]);var V=P,N={class:"info"},K={key:0,class:"row"},W=(0,s._)("div",{class:"label col-3"},"IP Address",-1),F=["textContent"],L={key:1,class:"row"},Y=(0,s._)("div",{class:"label col-3"},"MAC Address",-1),J=["textContent"],Q={key:2,class:"row"},X=(0,s._)("div",{class:"label col-3"},"Name",-1),ee=["textContent"],te={key:3,class:"row"},ne=(0,s._)("div",{class:"label col-3"},"Port",-1),se=["textContent"],oe={key:4,class:"row"},re=(0,s._)("div",{class:"label col-3"},"OS",-1),ie=["textContent"],le={key:5,class:"row"},ae=(0,s._)("div",{class:"label col-3"},"Architecture",-1),ue=["textContent"],ce={key:6,class:"row"},de=(0,s._)("div",{class:"label col-3"},"Server name",-1),ve=["textContent"],pe={key:7,class:"row"},me=(0,s._)("div",{class:"label col-3"},"Server version",-1),fe=["textContent"],he={key:8,class:"row"},ge=(0,s._)("div",{class:"label col-3"},"Protocol version",-1),we=["textContent"],_e={key:9,class:"row"},Ce=(0,s._)("div",{class:"label col-3"},"Control protocol version",-1),ye=["textContent"];function be(e,t,n,o,r,i){var l,a,u,c,d,v,p,m,h,g,w,_,C,y,b,x,k,H,S,D,q,z,M,Z,j,G,O,R,I,U,$,E,A,T,B,P,V;return(0,s.wg)(),(0,s.iD)("div",N,[null!==(l=n.info)&&void 0!==l&&null!==(a=l.server)&&void 0!==a&&null!==(u=a.host)&&void 0!==u&&null!==(c=u.ip)&&void 0!==c&&c.length?((0,s.wg)(),(0,s.iD)("div",K,[W,(0,s._)("div",{class:"value col-9",textContent:(0,f.zw)(n.info.server.host.ip)},null,8,F)])):(0,s.kq)("",!0),null!==(d=n.info)&&void 0!==d&&null!==(v=d.server)&&void 0!==v&&null!==(p=v.host)&&void 0!==p&&null!==(m=p.mac)&&void 0!==m&&m.length?((0,s.wg)(),(0,s.iD)("div",L,[Y,(0,s._)("div",{class:"value col-9",textContent:(0,f.zw)(n.info.server.host.mac)},null,8,J)])):(0,s.kq)("",!0),null!==(h=n.info)&&void 0!==h&&null!==(g=h.server)&&void 0!==g&&null!==(w=g.host)&&void 0!==w&&null!==(_=w.name)&&void 0!==_&&_.length?((0,s.wg)(),(0,s.iD)("div",Q,[X,(0,s._)("div",{class:"value col-9",textContent:(0,f.zw)(n.info.server.host.name)},null,8,ee)])):(0,s.kq)("",!0),null!==(C=n.info)&&void 0!==C&&null!==(y=C.server)&&void 0!==y&&null!==(b=y.host)&&void 0!==b&&b.port?((0,s.wg)(),(0,s.iD)("div",te,[ne,(0,s._)("div",{class:"value col-9",textContent:(0,f.zw)(n.info.server.host.port)},null,8,se)])):(0,s.kq)("",!0),null!==(x=n.info)&&void 0!==x&&null!==(k=x.server)&&void 0!==k&&null!==(H=k.host)&&void 0!==H&&null!==(S=H.os)&&void 0!==S&&S.length?((0,s.wg)(),(0,s.iD)("div",oe,[re,(0,s._)("div",{class:"value col-9",textContent:(0,f.zw)(n.info.server.host.os)},null,8,ie)])):(0,s.kq)("",!0),null!==(D=n.info)&&void 0!==D&&null!==(q=D.server)&&void 0!==q&&null!==(z=q.host)&&void 0!==z&&null!==(M=z.arch)&&void 0!==M&&M.length?((0,s.wg)(),(0,s.iD)("div",le,[ae,(0,s._)("div",{class:"value col-9",textContent:(0,f.zw)(n.info.server.host.arch)},null,8,ue)])):(0,s.kq)("",!0),null!==(Z=n.info)&&void 0!==Z&&null!==(j=Z.server)&&void 0!==j&&null!==(G=j.snapserver)&&void 0!==G&&null!==(O=G.name)&&void 0!==O&&O.length?((0,s.wg)(),(0,s.iD)("div",ce,[de,(0,s._)("div",{class:"value col-9",textContent:(0,f.zw)(n.info.server.snapserver.name)},null,8,ve)])):(0,s.kq)("",!0),null!==(R=n.info)&&void 0!==R&&null!==(I=R.server)&&void 0!==I&&null!==(U=I.snapserver)&&void 0!==U&&null!==($=U.version)&&void 0!==$&&$.length?((0,s.wg)(),(0,s.iD)("div",pe,[me,(0,s._)("div",{class:"value col-9",textContent:(0,f.zw)(n.info.server.snapserver.version)},null,8,fe)])):(0,s.kq)("",!0),null!==(E=n.info)&&void 0!==E&&null!==(A=E.server)&&void 0!==A&&null!==(T=A.snapserver)&&void 0!==T&&T.protocolVersion?((0,s.wg)(),(0,s.iD)("div",he,[ge,(0,s._)("div",{class:"value col-9",textContent:(0,f.zw)(n.info.server.snapserver.protocolVersion)},null,8,we)])):(0,s.kq)("",!0),null!==(B=n.info)&&void 0!==B&&null!==(P=B.server)&&void 0!==P&&null!==(V=P.snapserver)&&void 0!==V&&V.controlProtocolVersion?((0,s.wg)(),(0,s.iD)("div",_e,[Ce,(0,s._)("div",{class:"value col-9",textContent:(0,f.zw)(n.info.server.snapserver.controlProtocolVersion)},null,8,ye)])):(0,s.kq)("",!0)])}var xe={name:"HostModal",props:{info:{type:Object,default:function(){}}}};const ke=(0,I.Z)(xe,[["render",be]]);var He=ke,Se=function(e){return(0,s.dD)("data-v-353ffa58"),e=e(),(0,s.Cn)(),e},De={class:"info"},qe={class:"section name"},ze=Se((function(){return(0,s._)("div",{class:"title"},"Name",-1)})),Me={class:"row"},Ze={class:"name-value"},je=["textContent"],Ge=Se((function(){return(0,s._)("i",{class:"fa fa-edit"},null,-1)})),Oe=[Ge],Re={key:0,class:"section clients"},Ie=Se((function(){return(0,s._)("div",{class:"title"},"Clients",-1)})),Ue=["for"],$e=["id","value","checked","disabled","onInput"],Ee={key:1,class:"section streams"},Ae=Se((function(){return(0,s._)("div",{class:"title"},"Stream",-1)})),Te={class:"row"},Be=Se((function(){return(0,s._)("div",{class:"label col-3"},"ID",-1)})),Pe={class:"value col-9"},Ve=["textContent","name","value","disabled","selected"],Ne={key:0,class:"row"},Ke=Se((function(){return(0,s._)("div",{class:"label col-m-3"},"Status",-1)})),We=["textContent"],Fe={key:1,class:"row"},Le=Se((function(){return(0,s._)("div",{class:"label col-s-12 col-m-3"},"Host",-1)})),Ye=["textContent"],Je={key:2,class:"row"},Qe=Se((function(){return(0,s._)("div",{class:"label col-s-12 col-m-3"},"Path",-1)})),Xe=["textContent"],et={key:3,class:"row"},tt=Se((function(){return(0,s._)("div",{class:"label col-s-12 col-m-3"},"URI",-1)})),nt=["textContent"];function st(e,t,n,o,r,i){var l,a,u,c,d,v,p,m,h,g,w,_,C,y,b,x,k;return(0,s.wg)(),(0,s.iD)("div",De,[(0,s._)("div",qe,[ze,(0,s._)("div",Me,[(0,s._)("div",Ze,[(0,s._)("span",{class:"name",textContent:(0,f.zw)(null!==(l=n.group.name)&&void 0!==l&&l.length?n.group.name:"default")},null,8,je),(0,s._)("button",{class:"pull-right",title:"Rename",onClick:t[0]||(t[0]=function(){return i.renameGroup&&i.renameGroup.apply(i,arguments)})},Oe)])])]),Object.keys((null===(a=n.group)||void 0===a?void 0:a.clients)||{}).length>0?((0,s.wg)(),(0,s.iD)("div",Re,[Ie,((0,s.wg)(!0),(0,s.iD)(s.HY,null,(0,s.Ko)(n.clients||{},(function(t,o){return(0,s.wg)(),(0,s.iD)("div",{class:"row",ref_for:!0,ref:"groupClients",key:o},[(0,s._)("label",{class:"client",for:"snapcast-client-"+t.id},[(0,s._)("input",{type:"checkbox",class:"client",id:"snapcast-client-".concat(t.id),value:t.id,checked:t.id in n.group.clients,disabled:n.loading,onInput:function(n){return e.$emit(n.target.checked?"add-client":"remove-client",t.id)}},null,40,$e),(0,s.Uk)(" "+(0,f.zw)(t.host.name),1)],8,Ue)])})),128))])):(0,s.kq)("",!0),null!==(u=n.group)&&void 0!==u&&u.stream_id?((0,s.wg)(),(0,s.iD)("div",Ee,[Ae,(0,s._)("div",Te,[Be,(0,s._)("div",Pe,[(0,s._)("label",null,[(0,s._)("select",{ref:"streamSelect",onChange:t[1]||(t[1]=function(t){return e.$emit("stream-change",t.target.value)})},[((0,s.wg)(!0),(0,s.iD)(s.HY,null,(0,s.Ko)(n.streams,(function(e,t){return(0,s.wg)(),(0,s.iD)("option",{key:t,textContent:(0,f.zw)(n.streams[n.group.stream_id].id),name:e.id,value:e.id,disabled:n.loading,selected:e.id===n.group.stream_id},null,8,Ve)})),128))],544)])])]),null!==(c=n.streams)&&void 0!==c&&null!==(d=c[n.group.stream_id])&&void 0!==d&&d.status?((0,s.wg)(),(0,s.iD)("div",Ne,[Ke,(0,s._)("div",{class:"value col-m-9",textContent:(0,f.zw)(n.streams[n.group.stream_id].status)},null,8,We)])):(0,s.kq)("",!0),null!==(v=n.streams)&&void 0!==v&&null!==(p=v[null===(h=n.group)||void 0===h?void 0:h.stream_id])&&void 0!==p&&null!==(m=p.uri)&&void 0!==m&&m.host?((0,s.wg)(),(0,s.iD)("div",Fe,[Le,(0,s._)("div",{class:"value col-s-12 col-m-9",textContent:(0,f.zw)(n.streams[n.group.stream_id].uri.host)},null,8,Ye)])):(0,s.kq)("",!0),null!==(g=n.streams)&&void 0!==g&&null!==(w=g[null===(C=n.group)||void 0===C?void 0:C.stream_id])&&void 0!==w&&null!==(_=w.uri)&&void 0!==_&&_.path?((0,s.wg)(),(0,s.iD)("div",Je,[Qe,(0,s._)("div",{class:"value col-s-12 col-m-9",textContent:(0,f.zw)(n.streams[n.group.stream_id].uri.path)},null,8,Xe)])):(0,s.kq)("",!0),null!==(y=n.streams)&&void 0!==y&&null!==(b=y[null===(k=n.group)||void 0===k?void 0:k.stream_id])&&void 0!==b&&null!==(x=b.uri)&&void 0!==x&&x.raw?((0,s.wg)(),(0,s.iD)("div",et,[tt,(0,s._)("div",{class:"value col-s-12 col-m-9",textContent:(0,f.zw)(n.streams[n.group.stream_id].uri.raw)},null,8,nt)])):(0,s.kq)("",!0)])):(0,s.kq)("",!0)])}n(3210);var ot={name:"GroupModal",emits:["add-client","remove-client","stream-change","rename-group"],props:{loading:{type:Boolean,default:!1},group:{type:Object},clients:{type:Object},streams:{type:Object}},methods:{renameGroup:function(){var e=(prompt("New group name",this.group.name)||"").trim();null!==e&&void 0!==e&&e.length&&this.$emit("rename-group",e)}}};const rt=(0,I.Z)(ot,[["render",st],["__scopeId","data-v-353ffa58"]]);var it=rt,lt=function(e){return(0,s.dD)("data-v-0e55ac54"),e=e(),(0,s.Cn)(),e},at={class:"client-modal"},ut={key:0,class:"info"},ct={class:"row"},dt=lt((function(){return(0,s._)("div",{class:"label col-s-12 col-m-3"},"ID",-1)})),vt=["textContent"],pt={key:0,class:"row"},mt=lt((function(){return(0,s._)("div",{class:"label col-s-12 col-m-3"},"Name",-1)})),ft={class:"value col-s-12 col-m-9"},ht=["textContent"],gt=lt((function(){return(0,s._)("i",{class:"fa fa-edit"},null,-1)})),wt=[gt],_t={class:"row"},Ct=lt((function(){return(0,s._)("div",{class:"label col-s-12 col-m-3"},"Connected",-1)})),yt=["textContent"],bt={class:"row"},xt=lt((function(){return(0,s._)("div",{class:"label col-s-12 col-m-3"},"Volume",-1)})),kt={class:"value col-s-12 col-m-9"},Ht={class:"row"},St=lt((function(){return(0,s._)("div",{class:"label col-s-12 col-m-3"},"Muted",-1)})),Dt=["textContent"],qt={class:"row"},zt=lt((function(){return(0,s._)("div",{class:"label col-s-12 col-m-3"},"Latency",-1)})),Mt=["textContent"],Zt={key:1,class:"row"},jt=lt((function(){return(0,s._)("div",{class:"label col-s-12 col-m-3"},"IP Address",-1)})),Gt=["textContent"],Ot={key:2,class:"row"},Rt=lt((function(){return(0,s._)("div",{class:"label col-s-12 col-m-3"},"MAC Address",-1)})),It=["textContent"],Ut={key:3,class:"row"},$t=lt((function(){return(0,s._)("div",{class:"label col-s-12 col-m-3"},"OS",-1)})),Et=["textContent"],At={key:4,class:"row"},Tt=lt((function(){return(0,s._)("div",{class:"label col-s-12 col-m-3"},"Architecture",-1)})),Bt=["textContent"],Pt={class:"row"},Vt=lt((function(){return(0,s._)("div",{class:"label col-s-12 col-m-3"},"Client name",-1)})),Nt=["textContent"],Kt={class:"row"},Wt=lt((function(){return(0,s._)("div",{class:"label col-s-12 col-m-3"},"Client version",-1)})),Ft=["textContent"],Lt={class:"row"},Yt=lt((function(){return(0,s._)("div",{class:"label col-s-12 col-m-3"},"Protocol version",-1)})),Jt=["textContent"],Qt={class:"buttons"},Xt={class:"row"},en=["disabled"],tn=lt((function(){return(0,s._)("i",{class:"fas fa-trash"},null,-1)})),nn=lt((function(){return(0,s._)("span",{class:"name"},"Remove client",-1)})),sn=[tn,nn];function on(e,t,n,o,r,i){var l,a,u,c,d;return(0,s.wg)(),(0,s.iD)("div",at,[n.client?((0,s.wg)(),(0,s.iD)("div",ut,[(0,s._)("div",ct,[dt,(0,s._)("div",{class:"value col-s-12 col-m-9",textContent:(0,f.zw)(n.client.id)},null,8,vt)]),null!==(l=n.client.config)&&void 0!==l&&null!==(a=l.name)&&void 0!==a&&a.length||null!==(u=n.client.host)&&void 0!==u&&u.name?((0,s.wg)(),(0,s.iD)("div",pt,[mt,(0,s._)("div",ft,[(0,s._)("span",{class:"name",textContent:(0,f.zw)((null===(c=n.client.config)||void 0===c?void 0:c.name)||(null===(d=n.client.host)||void 0===d?void 0:d.name))},null,8,ht),(0,s._)("button",{title:"Rename",onClick:t[0]||(t[0]=function(){return i.renameClient&&i.renameClient.apply(i,arguments)})},wt)])])):(0,s.kq)("",!0),(0,s._)("div",_t,[Ct,(0,s._)("div",{class:"value col-s-12 col-m-9",textContent:(0,f.zw)(n.client.connected)},null,8,yt)]),(0,s._)("div",bt,[xt,(0,s._)("div",kt,(0,f.zw)(n.client.config.volume.percent)+"%",1)]),(0,s._)("div",Ht,[St,(0,s._)("div",{class:"value col-s-12 col-m-9",textContent:(0,f.zw)(n.client.config.volume.muted)},null,8,Dt)]),(0,s._)("div",qt,[zt,(0,s._)("div",{class:"value col-s-12 col-m-9",textContent:(0,f.zw)(n.client.config.latency)},null,8,Mt)]),n.client.host.ip&&n.client.host.ip.length?((0,s.wg)(),(0,s.iD)("div",Zt,[jt,(0,s._)("div",{class:"value col-s-12 col-m-9",textContent:(0,f.zw)(n.client.host.ip)},null,8,Gt)])):(0,s.kq)("",!0),n.client.host.mac&&n.client.host.mac.length?((0,s.wg)(),(0,s.iD)("div",Ot,[Rt,(0,s._)("div",{class:"value col-s-12 col-m-9",textContent:(0,f.zw)(n.client.host.mac)},null,8,It)])):(0,s.kq)("",!0),n.client.host.os&&n.client.host.os.length?((0,s.wg)(),(0,s.iD)("div",Ut,[$t,(0,s._)("div",{class:"value col-s-12 col-m-9",textContent:(0,f.zw)(n.client.host.os)},null,8,Et)])):(0,s.kq)("",!0),n.client.host.arch&&n.client.host.arch.length?((0,s.wg)(),(0,s.iD)("div",At,[Tt,(0,s._)("div",{class:"value col-s-12 col-m-9",textContent:(0,f.zw)(n.client.host.arch)},null,8,Bt)])):(0,s.kq)("",!0),(0,s._)("div",Pt,[Vt,(0,s._)("div",{class:"value col-s-12 col-m-9",textContent:(0,f.zw)(n.client.snapclient.name)},null,8,Nt)]),(0,s._)("div",Kt,[Wt,(0,s._)("div",{class:"value col-s-12 col-m-9",textContent:(0,f.zw)(n.client.snapclient.version)},null,8,Ft)]),(0,s._)("div",Lt,[Yt,(0,s._)("div",{class:"value col-s-12 col-m-9",textContent:(0,f.zw)(n.client.snapclient.protocolVersion)},null,8,Jt)])])):(0,s.kq)("",!0),(0,s._)("div",Qt,[(0,s._)("div",Xt,[(0,s._)("button",{type:"button",disabled:n.loading,onClick:t[1]||(t[1]=function(){return i.removeClient&&i.removeClient.apply(i,arguments)})},sn,8,en)])])])}var rn={name:"ClientModal",emits:["remove-client","rename-client"],props:{loading:{type:Boolean,default:!1},client:{type:Object}},methods:{removeClient:function(){window.confirm("Are you sure that you want to remove this client?")&&this.$emit("remove-client")},renameClient:function(){var e,t=(window.prompt("New client name",null!==(e=this.client.config.name)&&void 0!==e&&e.length?this.client.config.name:this.client.host.name)||"").trim();t.length&&this.$emit("rename-client",t)}}};const ln=(0,I.Z)(rn,[["render",on],["__scopeId","data-v-0e55ac54"]]);var an=ln,un=n(1232),cn={name:"MusicSnapcast",mixins:[m.Z],components:{Loading:un.Z,Modal:p.Z,Host:V,ModalHost:He,ModalGroup:it,ModalClient:an},data:function(){return{loading:!1,hosts:{},ports:{},selectedHost:null,selectedGroup:null,selectedClient:null}},computed:{clientsByHost:function(){return Object.entries(this.hosts).reduce((function(e,t){var n=(0,v.Z)(t,2),s=n[0],o=n[1];return e[s]={},Object.values(o.groups).forEach((function(t){Object.entries(t.clients).forEach((function(t){var n=(0,v.Z)(t,2),o=n[0],r=n[1];e[s][o]=r}))})),e}),{})}},methods:{parseServerStatus:function(e){e.server.host.port=this.ports[e.server.host.name],this.hosts[e.server.host.name]=(0,d.Z)((0,d.Z)({},e),{},{groups:e.groups.map((function(e){return(0,d.Z)((0,d.Z)({},e),{},{clients:e.clients.reduce((function(e,t){return e[t.id]=t,e}),{})})})).reduce((function(e,t){return e[t.id]=t,e}),{}),streams:e.streams.reduce((function(e,t){return e[t.id]=t,e}),{})})},refresh:function(){var e=this;return(0,c.Z)(regeneratorRuntime.mark((function t(){var n,s;return regeneratorRuntime.wrap((function(t){while(1)switch(t.prev=t.next){case 0:return e.loading=!0,t.prev=1,t.next=4,e.request("music.snapcast.get_backend_hosts");case 4:return n=t.sent,t.next=7,Promise.all(Object.keys(n).map(function(){var t=(0,c.Z)(regeneratorRuntime.mark((function t(s){return regeneratorRuntime.wrap((function(t){while(1)switch(t.prev=t.next){case 0:return t.abrupt("return",e.request("music.snapcast.status",{host:s,port:n[s]}));case 1:case"end":return t.stop()}}),t)})));return function(e){return t.apply(this,arguments)}}()));case 7:s=t.sent,e.hosts={},s.forEach((function(t){e.ports[t.server.host.name]=n[t.server.host.name],e.parseServerStatus(t)}));case 10:return t.prev=10,e.loading=!1,t.finish(10);case 13:case"end":return t.stop()}}),t,null,[[1,,10,13]])})))()},refreshHost:function(e){var t=this;return(0,c.Z)(regeneratorRuntime.mark((function n(){return regeneratorRuntime.wrap((function(n){while(1)switch(n.prev=n.next){case 0:if(e in t.hosts){n.next=2;break}return n.abrupt("return");case 2:return n.t0=t,n.next=5,t.request("music.snapcast.status",{host:e,port:t.ports[e]});case 5:n.t1=n.sent,n.t0.parseServerStatus.call(n.t0,n.t1);case 7:case"end":return n.stop()}}),n)})))()},addClientToGroup:function(e){var t=this;return(0,c.Z)(regeneratorRuntime.mark((function n(){var s;return regeneratorRuntime.wrap((function(n){while(1)switch(n.prev=n.next){case 0:if(t.loading=!0,n.prev=1,t.selectedHost&&t.selectedGroup&&e in t.clientsByHost[t.selectedHost]){n.next=4;break}return n.abrupt("return");case 4:return s=(0,u.Z)(new Set([e].concat((0,u.Z)(Object.keys(t.hosts[t.selectedHost].groups[t.selectedGroup].clients))))),n.next=7,t.request("music.snapcast.group_set_clients",{host:t.selectedHost,port:t.ports[t.selectedHost],group:t.selectedGroup,clients:s});case 7:return n.next=9,t.refreshHost(t.selectedHost);case 9:return n.prev=9,t.loading=!1,n.finish(9);case 12:case"end":return n.stop()}}),n,null,[[1,,9,12]])})))()},removeClientFromGroup:function(e){var t=this;return(0,c.Z)(regeneratorRuntime.mark((function n(){var s;return regeneratorRuntime.wrap((function(n){while(1)switch(n.prev=n.next){case 0:if(t.loading=!0,n.prev=1,t.selectedHost&&t.selectedGroup&&e in t.clientsByHost[t.selectedHost]){n.next=4;break}return n.abrupt("return");case 4:if(s=new Set((0,u.Z)(Object.keys(t.hosts[t.selectedHost].groups[t.selectedGroup].clients))),s.has(e)){n.next=7;break}return n.abrupt("return");case 7:return s.delete(e),n.next=10,t.request("music.snapcast.group_set_clients",{host:t.selectedHost,port:t.ports[t.selectedHost],group:t.selectedGroup,clients:(0,u.Z)(s)});case 10:return n.next=12,t.refreshHost(t.selectedHost);case 12:return n.prev=12,t.loading=!1,n.finish(12);case 15:case"end":return n.stop()}}),n,null,[[1,,12,15]])})))()},renameGroup:function(e){var t=this;return(0,c.Z)(regeneratorRuntime.mark((function n(){return regeneratorRuntime.wrap((function(n){while(1)switch(n.prev=n.next){case 0:if(t.loading=!0,n.prev=1,t.selectedHost&&t.selectedGroup){n.next=4;break}return n.abrupt("return");case 4:return n.next=6,t.request("music.snapcast.set_group_name",{host:t.selectedHost,port:t.ports[t.selectedHost],group:t.selectedGroup,name:e});case 6:return n.next=8,t.refreshHost(t.selectedHost);case 8:return n.prev=8,t.loading=!1,n.finish(8);case 11:case"end":return n.stop()}}),n,null,[[1,,8,11]])})))()},renameClient:function(e){var t=this;return(0,c.Z)(regeneratorRuntime.mark((function n(){return regeneratorRuntime.wrap((function(n){while(1)switch(n.prev=n.next){case 0:if(t.loading=!0,n.prev=1,t.selectedHost&&t.selectedClient){n.next=4;break}return n.abrupt("return");case 4:return n.next=6,t.request("music.snapcast.set_client_name",{host:t.selectedHost,port:t.ports[t.selectedHost],client:t.selectedClient,name:e});case 6:return n.next=8,t.refreshHost(t.selectedHost);case 8:return n.prev=8,t.loading=!1,n.finish(8);case 11:case"end":return n.stop()}}),n,null,[[1,,8,11]])})))()},removeClient:function(){var e=this;return(0,c.Z)(regeneratorRuntime.mark((function t(){return regeneratorRuntime.wrap((function(t){while(1)switch(t.prev=t.next){case 0:if(e.loading=!0,t.prev=1,e.selectedHost&&e.selectedClient){t.next=4;break}return t.abrupt("return");case 4:return t.next=6,e.request("music.snapcast.delete_client",{host:e.selectedHost,port:e.ports[e.selectedHost],client:e.selectedClient});case 6:return e.$refs.modalClient.close(),t.next=9,e.refreshHost(e.selectedHost);case 9:return t.prev=9,e.loading=!1,t.finish(9);case 12:case"end":return t.stop()}}),t,null,[[1,,9,12]])})))()},streamChange:function(e){var t=this;return(0,c.Z)(regeneratorRuntime.mark((function n(){return regeneratorRuntime.wrap((function(n){while(1)switch(n.prev=n.next){case 0:return t.loading=!0,n.prev=1,n.next=4,t.request("music.snapcast.group_set_stream",{host:t.selectedHost,port:t.ports[t.selectedHost],group:t.selectedGroup,stream_id:e});case 4:return n.next=6,t.refreshHost(t.selectedHost);case 6:return n.prev=6,t.loading=!1,n.finish(6);case 9:case"end":return n.stop()}}),n,null,[[1,,6,9]])})))()},onClientUpdate:function(e){var t=this;Object.keys(this.hosts[e.host].groups).forEach((function(n){e.client.id in t.hosts[e.host].groups[n].clients&&(t.hosts[e.host].groups[n].clients[e.client.id]=e.client)}))},onGroupStreamChange:function(e){this.hosts[e.host].groups[e.group].stream_id=e.stream},onServerUpdate:function(e){this.parseServerStatus(e.server)},onStreamUpdate:function(e){this.hosts[e.host].streams[e.stream.id]=e.stream},onClientVolumeChange:function(e){var t=this;Object.keys(this.hosts[e.host].groups).forEach((function(n){e.client in t.hosts[e.host].groups[n].clients&&(null!=e.volume&&(t.hosts[e.host].groups[n].clients[e.client].config.volume.percent=e.volume),null!=e.muted&&(t.hosts[e.host].groups[n].clients[e.client].config.volume.muted=e.muted))}))},onGroupMuteChange:function(e){this.hosts[e.host].groups[e.group].muted=e.muted},modalShow:function(e){switch(e.type){case"host":this.modal[e.type].info=this.hosts[e.host];break;case"group":this.modal[e.type].info.server=this.hosts[e.host].server,this.modal[e.type].info.group=this.hosts[e.host].groups[e.group],this.modal[e.type].info.streams=this.hosts[e.host].streams,this.modal[e.type].info.clients={};for(var t=0,n=Object.values(this.hosts[e.host].groups);t<n.length;t++)for(var s=n[t],o=0,r=Object.values(s.clients);o<r.length;o++){var i=r[o];this.modal[e.type].info.clients[i.id]=i}break;case"client":this.modal[e.type].info=this.hosts[e.host].groups[e.group].clients[e.client],this.modal[e.type].info.server=this.hosts[e.host].server;break}this.modal[e.type].visible=!0},groupMute:function(e){var t=this;return(0,c.Z)(regeneratorRuntime.mark((function n(){return regeneratorRuntime.wrap((function(n){while(1)switch(n.prev=n.next){case 0:return n.next=2,t.request("music.snapcast.mute",{group:e.group,host:e.host,port:t.ports[e.host],mute:e.muted});case 2:return n.next=4,t.refreshHost(e.host);case 4:case"end":return n.stop()}}),n)})))()},clientMute:function(e){var t=this;return(0,c.Z)(regeneratorRuntime.mark((function n(){return regeneratorRuntime.wrap((function(n){while(1)switch(n.prev=n.next){case 0:return n.next=2,t.request("music.snapcast.mute",{client:e.client,host:e.host,port:t.ports[e.host],mute:e.muted});case 2:return n.next=4,t.refreshHost(e.host);case 4:case"end":return n.stop()}}),n)})))()},clientSetVolume:function(e){var t=this;return(0,c.Z)(regeneratorRuntime.mark((function n(){return regeneratorRuntime.wrap((function(n){while(1)switch(n.prev=n.next){case 0:return n.next=2,t.request("music.snapcast.volume",{client:e.client,host:e.host,port:t.ports[e.host],volume:e.volume});case 2:return n.next=4,t.refreshHost(e.host);case 4:case"end":return n.stop()}}),n)})))()},onModalShow:function(e){switch(e.type){case"host":this.selectedHost=e.host,this.$refs.modalHost.show();break;case"group":this.selectedHost=e.host,this.selectedGroup=e.group,this.$refs.modalGroup.show();break;case"client":this.selectedHost=e.host,this.selectedGroup=e.group,this.selectedClient=e.client,this.$refs.modalClient.show();break}}},mounted:function(){this.refresh(),this.subscribe(this.onClientUpdate,null,"platypush.message.event.music.snapcast.ClientConnectedEvent","platypush.message.event.music.snapcast.ClientDisconnectedEvent","platypush.message.event.music.snapcast.ClientNameChangeEvent"),this.subscribe(this.onGroupStreamChange,null,"platypush.message.event.music.snapcast.GroupStreamChangeEvent"),this.subscribe(this.onServerUpdate,null,"platypush.message.event.music.snapcast.ServerUpdateEvent"),this.subscribe(this.onStreamUpdate,null,"platypush.message.event.music.snapcast.StreamUpdateEvent"),this.subscribe(this.onClientVolumeChange,null,"platypush.message.event.music.snapcast.ClientVolumeChangeEvent"),this.subscribe(this.onGroupMuteChange,null,"platypush.message.event.music.snapcast.GroupMuteChangeEvent")}};const dn=(0,I.Z)(cn,[["render",a],["__scopeId","data-v-40841f5a"]]);var vn=dn}}]);
//# sourceMappingURL=2790-legacy.2afcb92a.js.map