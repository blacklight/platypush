"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[3194],{6:function(e,t,n){n.d(t,{Z:function(){return h}});var a=n(6252),i=n(3577),l=n(9963);const o=e=>((0,a.dD)("data-v-a6396ae8"),e=e(),(0,a.Cn)(),e),s=["checked"],c=o((()=>(0,a._)("div",{class:"switch"},[(0,a._)("div",{class:"dot"})],-1))),d={class:"label"};function u(e,t,n,o,u,r){return(0,a.wg)(),(0,a.iD)("div",{class:(0,i.C_)(["power-switch",{disabled:n.disabled}]),onClick:t[0]||(t[0]=(0,l.iM)(((...e)=>r.onInput&&r.onInput(...e)),["stop"]))},[(0,a._)("input",{type:"checkbox",checked:n.value},null,8,s),(0,a._)("label",null,[c,(0,a._)("span",d,[(0,a.WI)(e.$slots,"default",{},void 0,!0)])])],2)}var r={name:"ToggleSwitch",emits:["input"],props:{value:{type:Boolean,default:!1},disabled:{type:Boolean,default:!1}},methods:{onInput(e){if(this.disabled)return!1;this.$emit("input",e)}}},v=n(3744);const p=(0,v.Z)(r,[["render",u],["__scopeId","data-v-a6396ae8"]]);var h=p},3194:function(e,t,n){n.r(t),n.d(t,{default:function(){return m}});var a=n(6252),i=n(3577),l=n(9963);const o={class:"entity device-container"},s={class:"head"},c={class:"icon"},d={class:"label"},u=["textContent"];function r(e,t,n,r,v,p){const h=(0,a.up)("EntityIcon"),f=(0,a.up)("ToggleSwitch");return(0,a.wg)(),(0,a.iD)("div",o,[(0,a._)("div",s,[(0,a._)("div",c,[(0,a.Wm)(h,{entity:e.value,loading:e.loading,error:e.error},null,8,["entity","loading","error"])]),(0,a._)("div",d,[(0,a._)("div",{class:"name",textContent:(0,i.zw)(e.value.name)},null,8,u)]),(0,a._)("div",{class:(0,i.C_)(["value-container",{"with-children":e.value?.children_ids?.length}])},[(0,a.Wm)(f,{value:e.value.connected,disabled:e.loading,onInput:p.connect,onClick:t[0]||(t[0]=(0,l.iM)((()=>{}),["stop"]))},null,8,["value","disabled","onInput"])],2)])])}var v=n(7909),p=n(1706),h=n(6),f={name:"BluetoothDevice",components:{EntityIcon:p["default"],ToggleSwitch:h.Z},mixins:[v["default"]],methods:{async connect(e){e.stopPropagation(),this.$emit("loading",!0);const t="bluetooth."+(this.value.connected?"disconnect":"connect");try{await this.request(t,{device:this.value.address})}finally{this.$emit("loading",!1)}}}},_=n(3744);const g=(0,_.Z)(f,[["render",r],["__scopeId","data-v-6aff1eff"]]);var m=g}}]);
//# sourceMappingURL=3194.256c2da8.js.map