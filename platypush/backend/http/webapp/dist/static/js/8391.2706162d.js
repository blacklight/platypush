"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[8391],{7514:function(t,e,i){i.d(e,{Z:function(){return h}});var n=i(6252),a=i(3577),l=i(9963);const s=t=>((0,n.dD)("data-v-eff375b6"),t=t(),(0,n.Cn)(),t),o=["checked","id"],d=s((()=>(0,n._)("div",{class:"switch"},[(0,n._)("div",{class:"dot"})],-1))),u={class:"label"};function c(t,e,i,s,c,r){return(0,n.wg)(),(0,n.iD)("div",{class:(0,a.C_)(["power-switch",{disabled:i.disabled}]),onClick:e[0]||(e[0]=(0,l.iM)(((...t)=>r.onInput&&r.onInput(...t)),["stop"]))},[(0,n._)("input",{type:"checkbox",checked:i.value,id:i.id},null,8,o),(0,n._)("label",null,[d,(0,n._)("span",u,[(0,n.WI)(t.$slots,"default",{},void 0,!0)])])],2)}var r={name:"ToggleSwitch",emits:["input"],props:{id:{type:String},value:{type:Boolean,default:!1},disabled:{type:Boolean,default:!1}},methods:{onInput(t){if(this.disabled)return!1;this.$emit("input",t)}}},p=i(3744);const v=(0,p.Z)(r,[["render",c],["__scopeId","data-v-eff375b6"]]);var h=v},8391:function(t,e,i){i.r(e),i.d(e,{default:function(){return y}});var n=i(6252),a=i(3577),l=i(9963);const s={class:"entity switch-container"},o={class:"head"},d={class:"col-1 icon"},u={class:"col-9 label"},c=["textContent"],r={class:"col-2 switch pull-right"};function p(t,e,i,p,v,h){const g=(0,n.up)("EntityIcon"),f=(0,n.up)("ToggleSwitch");return(0,n.wg)(),(0,n.iD)("div",s,[(0,n._)("div",o,[(0,n._)("div",d,[(0,n.Wm)(g,{entity:t.value,loading:t.loading,error:t.error},null,8,["entity","loading","error"])]),(0,n._)("div",u,[(0,n._)("div",{class:"name",textContent:(0,a.zw)(t.value.name)},null,8,c)]),(0,n._)("div",r,[(0,n.Wm)(f,{value:!t.value.is_write_only&&t.value.state,disabled:t.loading||t.value.is_read_only,onInput:h.toggle,onClick:e[0]||(e[0]=(0,l.iM)((()=>{}),["stop"]))},null,8,["value","disabled","onInput"])])])])}var v=i(7514),h=i(4967),g=i(847),f={name:"Switch",components:{ToggleSwitch:v.Z,EntityIcon:h["default"]},mixins:[g["default"]],methods:{async toggle(t){t.stopPropagation(),this.$emit("loading",!0);try{if(await this.request("entities.execute",{id:this.value.id,action:"toggle"}),this.value.is_write_only){const t=this;t.value.state=!0,setTimeout((()=>t.value.state=!1),250)}}finally{this.$emit("loading",!1)}}}},_=i(3744);const w=(0,_.Z)(f,[["render",p],["__scopeId","data-v-2aaabd26"]]);var y=w}}]);
//# sourceMappingURL=8391.2706162d.js.map