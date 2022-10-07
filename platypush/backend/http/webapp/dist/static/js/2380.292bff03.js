"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[2380],{6:function(e,t,n){n.d(t,{Z:function(){return p}});var i=n(6252),o=n(3577),s=n(9963);const a=e=>((0,i.dD)("data-v-a6396ae8"),e=e(),(0,i.Cn)(),e),l=["checked"],d=a((()=>(0,i._)("div",{class:"switch"},[(0,i._)("div",{class:"dot"})],-1))),c={class:"label"};function u(e,t,n,a,u,r){return(0,i.wg)(),(0,i.iD)("div",{class:(0,o.C_)(["power-switch",{disabled:n.disabled}]),onClick:t[0]||(t[0]=(0,s.iM)(((...e)=>r.onInput&&r.onInput(...e)),["stop"]))},[(0,i._)("input",{type:"checkbox",checked:n.value},null,8,l),(0,i._)("label",null,[d,(0,i._)("span",c,[(0,i.WI)(e.$slots,"default",{},void 0,!0)])])],2)}var r={name:"ToggleSwitch",emits:["input"],props:{value:{type:Boolean,default:!1},disabled:{type:Boolean,default:!1}},methods:{onInput(e){if(this.disabled)return!1;this.$emit("input",e)}}},g=n(3744);const h=(0,g.Z)(r,[["render",u],["__scopeId","data-v-a6396ae8"]]);var p=h},4004:function(e,t,n){n.d(t,{Z:function(){return a}});var i=n(6813),o={name:"SwitchesMixin",mixins:[i.Z],props:{pluginName:{type:String,required:!0},bus:{type:Object,required:!0},config:{type:Object,default:()=>({})},selected:{type:Boolean,default:!1}},data(){return{loading:!1,initialized:!1,selectedDevice:null,devices:{}}},methods:{onRefreshEvent(e){e===this.pluginName&&this.refresh()},async toggle(e,t){null==t&&(t=e);const n=await this.request(`${this.pluginName}.toggle`,{device:t});this.devices[e].on=n.on},async refresh(){this.loading=!0;try{this.devices=(await this.request(`${this.pluginName}.switch_status`)).reduce(((e,t)=>{const n=t.name?.length?t.name:t.id;return e[n]=t,e}),{})}finally{this.loading=!1}}},mounted(){this.$watch((()=>this.selected),(e=>{e&&!this.initialized&&(this.refresh(),this.initialized=!0)})),this.bus.on("refresh",this.onRefreshEvent)},unmounted(){this.bus.off("refresh",this.onRefreshEvent)}};const s=o;var a=s},8671:function(e,t,n){n.d(t,{Z:function(){return w}});var i=n(6252),o=n(9963),s=n(3577);const a=e=>((0,i.dD)("data-v-38eb9831"),e=e(),(0,i.Cn)(),e),l={class:"name col-l-10 col-m-9 col-s-8"},d=a((()=>(0,i._)("i",{class:"fa fa-info"},null,-1))),c=[d],u=["textContent"],r={class:"toggler col-l-2 col-m-3 col-s-4"};function g(e,t,n,a,d,g){const h=(0,i.up)("Loading"),p=(0,i.up)("ToggleSwitch");return(0,i.wg)(),(0,i.iD)("div",{class:"switch",onClick:t[1]||(t[1]=(0,o.iM)(((...e)=>g.onToggle&&g.onToggle(...e)),["stop"]))},[n.loading?((0,i.wg)(),(0,i.j4)(h,{key:0})):(0,i.kq)("",!0),(0,i._)("div",l,[n.hasInfo?((0,i.wg)(),(0,i.iD)("button",{key:0,onClick:t[0]||(t[0]=(0,o.iM)(((...e)=>g.onInfo&&g.onInfo(...e)),["prevent"]))},c)):(0,i.kq)("",!0),(0,i._)("span",{class:"name-content",textContent:(0,s.zw)(n.name)},null,8,u)]),(0,i._)("div",r,[(0,i.Wm)(p,{disabled:n.loading,value:n.state,onInput:g.onToggle},null,8,["disabled","value","onInput"])])])}var h=n(6),p=n(1232),f={name:"Switch",components:{Loading:p.Z,ToggleSwitch:h.Z},emits:["toggle","info"],props:{name:{type:String,required:!0},state:{type:Boolean,default:!1},loading:{type:Boolean,default:!1},hasInfo:{type:Boolean,default:!1},id:{type:String}},methods:{onInfo(e){return e.stopPropagation(),this.$emit("info"),!1},onToggle(e){return e.stopPropagation(),this.$emit("toggle"),!1}}},v=n(3744);const m=(0,v.Z)(f,[["render",g],["__scopeId","data-v-38eb9831"]]);var w=m},2380:function(e,t,n){n.r(t),n.d(t,{default:function(){return h}});var i=n(6252);const o={class:"switches zwave-mqtt-switches"},s={key:1,class:"no-content"};function a(e,t,n,a,l,d){const c=(0,i.up)("Loading"),u=(0,i.up)("Switch");return(0,i.wg)(),(0,i.iD)("div",o,[e.loading?((0,i.wg)(),(0,i.j4)(c,{key:0})):Object.keys(e.devices).length?(0,i.kq)("",!0):((0,i.wg)(),(0,i.iD)("div",s,"No Z-Wave switches found.")),((0,i.wg)(!0),(0,i.iD)(i.HY,null,(0,i.Ko)(e.devices,((t,n)=>((0,i.wg)(),(0,i.j4)(u,{loading:e.loading,name:n,state:t.on,id:t.id,onToggle:i=>e.toggle(n,t.id),key:n},null,8,["loading","name","state","id","onToggle"])))),128))])}var l=n(1232),d=n(4004),c=n(8671),u={name:"ZwaveMqtt",components:{Switch:c.Z,Loading:l.Z},mixins:[d.Z]},r=n(3744);const g=(0,r.Z)(u,[["render",a],["__scopeId","data-v-c92e52f8"]]);var h=g}}]);
//# sourceMappingURL=2380.292bff03.js.map