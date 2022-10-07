"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[9694],{6:function(e,t,n){n.d(t,{Z:function(){return v}});var s=n(6252),i=n(3577),o=n(9963);const a=e=>((0,s.dD)("data-v-a6396ae8"),e=e(),(0,s.Cn)(),e),l=["checked"],c=a((()=>(0,s._)("div",{class:"switch"},[(0,s._)("div",{class:"dot"})],-1))),d={class:"label"};function u(e,t,n,a,u,r){return(0,s.wg)(),(0,s.iD)("div",{class:(0,i.C_)(["power-switch",{disabled:n.disabled}]),onClick:t[0]||(t[0]=(0,o.iM)(((...e)=>r.onInput&&r.onInput(...e)),["stop"]))},[(0,s._)("input",{type:"checkbox",checked:n.value},null,8,l),(0,s._)("label",null,[c,(0,s._)("span",d,[(0,s.WI)(e.$slots,"default",{},void 0,!0)])])],2)}var r={name:"ToggleSwitch",emits:["input"],props:{value:{type:Boolean,default:!1},disabled:{type:Boolean,default:!1}},methods:{onInput(e){if(this.disabled)return!1;this.$emit("input",e)}}},h=n(3744);const g=(0,h.Z)(r,[["render",u],["__scopeId","data-v-a6396ae8"]]);var v=g},4004:function(e,t,n){n.d(t,{Z:function(){return a}});var s=n(6813),i={name:"SwitchesMixin",mixins:[s.Z],props:{pluginName:{type:String,required:!0},bus:{type:Object,required:!0},config:{type:Object,default:()=>({})},selected:{type:Boolean,default:!1}},data(){return{loading:!1,initialized:!1,selectedDevice:null,devices:{}}},methods:{onRefreshEvent(e){e===this.pluginName&&this.refresh()},async toggle(e,t){null==t&&(t=e);const n=await this.request(`${this.pluginName}.toggle`,{device:t});this.devices[e].on=n.on},async refresh(){this.loading=!0;try{this.devices=(await this.request(`${this.pluginName}.switch_status`)).reduce(((e,t)=>{const n=t.name?.length?t.name:t.id;return e[n]=t,e}),{})}finally{this.loading=!1}}},mounted(){this.$watch((()=>this.selected),(e=>{e&&!this.initialized&&(this.refresh(),this.initialized=!0)})),this.bus.on("refresh",this.onRefreshEvent)},unmounted(){this.bus.off("refresh",this.onRefreshEvent)}};const o=i;var a=o},8671:function(e,t,n){n.d(t,{Z:function(){return m}});var s=n(6252),i=n(9963),o=n(3577);const a=e=>((0,s.dD)("data-v-38eb9831"),e=e(),(0,s.Cn)(),e),l={class:"name col-l-10 col-m-9 col-s-8"},c=a((()=>(0,s._)("i",{class:"fa fa-info"},null,-1))),d=[c],u=["textContent"],r={class:"toggler col-l-2 col-m-3 col-s-4"};function h(e,t,n,a,c,h){const g=(0,s.up)("Loading"),v=(0,s.up)("ToggleSwitch");return(0,s.wg)(),(0,s.iD)("div",{class:"switch",onClick:t[1]||(t[1]=(0,i.iM)(((...e)=>h.onToggle&&h.onToggle(...e)),["stop"]))},[n.loading?((0,s.wg)(),(0,s.j4)(g,{key:0})):(0,s.kq)("",!0),(0,s._)("div",l,[n.hasInfo?((0,s.wg)(),(0,s.iD)("button",{key:0,onClick:t[0]||(t[0]=(0,i.iM)(((...e)=>h.onInfo&&h.onInfo(...e)),["prevent"]))},d)):(0,s.kq)("",!0),(0,s._)("span",{class:"name-content",textContent:(0,o.zw)(n.name)},null,8,u)]),(0,s._)("div",r,[(0,s.Wm)(v,{disabled:n.loading,value:n.state,onInput:h.onToggle},null,8,["disabled","value","onInput"])])])}var g=n(6),v=n(1232),f={name:"Switch",components:{Loading:v.Z,ToggleSwitch:g.Z},emits:["toggle","info"],props:{name:{type:String,required:!0},state:{type:Boolean,default:!1},loading:{type:Boolean,default:!1},hasInfo:{type:Boolean,default:!1},id:{type:String}},methods:{onInfo(e){return e.stopPropagation(),this.$emit("info"),!1},onToggle(e){return e.stopPropagation(),this.$emit("toggle"),!1}}},p=n(3744);const w=(0,p.Z)(f,[["render",h],["__scopeId","data-v-38eb9831"]]);var m=w},9694:function(e,t,n){n.r(t),n.d(t,{default:function(){return Z}});var s=n(6252),i=n(3577);const o=e=>((0,s.dD)("data-v-7c8cf1b7"),e=e(),(0,s.Cn)(),e),a={class:"switches switchbot-switches"},l={key:1,class:"no-content"},c={key:0,class:"switch-info"},d={class:"row"},u=o((()=>(0,s._)("div",{class:"name"},"Name",-1))),r=["textContent"],h={class:"row"},g=o((()=>(0,s._)("div",{class:"name"},"On",-1))),v=["textContent"],f={class:"row"},p=o((()=>(0,s._)("div",{class:"name"},"Address",-1))),w=["textContent"];function m(e,t,n,o,m,_){const y=(0,s.up)("Loading"),b=(0,s.up)("Switch"),k=(0,s.up)("Modal");return(0,s.wg)(),(0,s.iD)("div",a,[e.loading?((0,s.wg)(),(0,s.j4)(y,{key:0})):Object.keys(e.devices).length?(0,s.kq)("",!0):((0,s.wg)(),(0,s.iD)("div",l,"No SwitchBot switches found.")),((0,s.wg)(!0),(0,s.iD)(s.HY,null,(0,s.Ko)(e.devices,((t,n)=>((0,s.wg)(),(0,s.j4)(b,{loading:e.loading,name:n,state:t.on,onToggle:t=>e.toggle(n),key:n,"has-info":!0,onInfo:t=>{e.selectedDevice=n,e.$refs.switchInfoModal.show()}},null,8,["loading","name","state","onToggle","onInfo"])))),128)),(0,s.Wm)(k,{title:"Device Info",ref:"switchInfoModal"},{default:(0,s.w5)((()=>[e.selectedDevice?((0,s.wg)(),(0,s.iD)("div",c,[(0,s._)("div",d,[u,(0,s._)("div",{class:"value",textContent:(0,i.zw)(e.devices[e.selectedDevice].name)},null,8,r)]),(0,s._)("div",h,[g,(0,s._)("div",{class:"value",textContent:(0,i.zw)(e.devices[e.selectedDevice].on)},null,8,v)]),(0,s._)("div",f,[p,(0,s._)("div",{class:"value",textContent:(0,i.zw)(e.devices[e.selectedDevice].address)},null,8,w)])])):(0,s.kq)("",!0)])),_:1},512)])}var _=n(1232),y=n(4004),b=n(8671),k=n(9642),I={name:"SwitchbotBluetooth",components:{Modal:k.Z,Switch:b.Z,Loading:_.Z},mixins:[y.Z]},C=n(3744);const D=(0,C.Z)(I,[["render",m],["__scopeId","data-v-7c8cf1b7"]]);var Z=D}}]);
//# sourceMappingURL=9694.18f23891.js.map