"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[3194],{6:function(e,n,t){t.d(n,{Z:function(){return f}});var a=t(6252),i=t(3577),l=t(9963),o=function(e){return(0,a.dD)("data-v-a6396ae8"),e=e(),(0,a.Cn)(),e},u=["checked"],c=o((function(){return(0,a._)("div",{class:"switch"},[(0,a._)("div",{class:"dot"})],-1)})),r={class:"label"};function s(e,n,t,o,s,d){return(0,a.wg)(),(0,a.iD)("div",{class:(0,i.C_)(["power-switch",{disabled:t.disabled}]),onClick:n[0]||(n[0]=(0,l.iM)((function(){return d.onInput&&d.onInput.apply(d,arguments)}),["stop"]))},[(0,a._)("input",{type:"checkbox",checked:t.value},null,8,u),(0,a._)("label",null,[c,(0,a._)("span",r,[(0,a.WI)(e.$slots,"default",{},void 0,!0)])])],2)}var d={name:"ToggleSwitch",emits:["input"],props:{value:{type:Boolean,default:!1},disabled:{type:Boolean,default:!1}},methods:{onInput:function(e){if(this.disabled)return!1;this.$emit("input",e)}}},v=t(3744);const p=(0,v.Z)(d,[["render",s],["__scopeId","data-v-a6396ae8"]]);var f=p},3194:function(e,n,t){t.r(n),t.d(n,{default:function(){return w}});t(8309);var a=t(6252),i=t(3577),l=t(9963),o={class:"entity device-container"},u={class:"head"},c={class:"icon"},r={class:"label"},s=["textContent"];function d(e,n,t,d,v,p){var f,h,g=(0,a.up)("EntityIcon"),m=(0,a.up)("ToggleSwitch");return(0,a.wg)(),(0,a.iD)("div",o,[(0,a._)("div",u,[(0,a._)("div",c,[(0,a.Wm)(g,{entity:e.value,loading:e.loading,error:e.error},null,8,["entity","loading","error"])]),(0,a._)("div",r,[(0,a._)("div",{class:"name",textContent:(0,i.zw)(e.value.name)},null,8,s)]),(0,a._)("div",{class:(0,i.C_)(["value-container",{"with-children":null===(f=e.value)||void 0===f||null===(h=f.children_ids)||void 0===h?void 0:h.length}])},[(0,a.Wm)(m,{value:e.value.connected,disabled:e.loading,onInput:p.connect,onClick:n[0]||(n[0]=(0,l.iM)((function(){}),["stop"]))},null,8,["value","disabled","onInput"])],2)])])}var v=t(8534),p=(t(5666),t(7909)),f=t(1706),h=t(6),g={name:"BluetoothDevice",components:{EntityIcon:f["default"],ToggleSwitch:h.Z},mixins:[p["default"]],methods:{connect:function(e){var n=this;return(0,v.Z)(regeneratorRuntime.mark((function t(){var a;return regeneratorRuntime.wrap((function(t){while(1)switch(t.prev=t.next){case 0:return e.stopPropagation(),n.$emit("loading",!0),a="bluetooth."+(n.value.connected?"disconnect":"connect"),t.prev=3,t.next=6,n.request(a,{device:n.value.address});case 6:return t.prev=6,n.$emit("loading",!1),t.finish(6);case 9:case"end":return t.stop()}}),t,null,[[3,,6,9]])})))()}}},m=t(3744);const _=(0,m.Z)(g,[["render",d],["__scopeId","data-v-6aff1eff"]]);var w=_}}]);
//# sourceMappingURL=3194-legacy.8b9635f4.js.map