"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[518,3499],{6:function(e,n,t){t.d(n,{Z:function(){return f}});var o=t(6252),i=t(3577),l=t(9963),a=function(e){return(0,o.dD)("data-v-a6396ae8"),e=e(),(0,o.Cn)(),e},r=["checked"],c=a((function(){return(0,o._)("div",{class:"switch"},[(0,o._)("div",{class:"dot"})],-1)})),u={class:"label"};function s(e,n,t,a,s,d){return(0,o.wg)(),(0,o.iD)("div",{class:(0,i.C_)(["power-switch",{disabled:t.disabled}]),onClick:n[0]||(n[0]=(0,l.iM)((function(){return d.onInput&&d.onInput.apply(d,arguments)}),["stop"]))},[(0,o._)("input",{type:"checkbox",checked:t.value},null,8,r),(0,o._)("label",null,[c,(0,o._)("span",u,[(0,o.WI)(e.$slots,"default",{},void 0,!0)])])],2)}var d={name:"ToggleSwitch",emits:["input"],props:{value:{type:Boolean,default:!1},disabled:{type:Boolean,default:!1}},methods:{onInput:function(e){if(this.disabled)return!1;this.$emit("input",e)}}},p=t(3744);const v=(0,p.Z)(d,[["render",s],["__scopeId","data-v-a6396ae8"]]);var f=v},3499:function(e,n,t){t.r(n),t.d(n,{default:function(){return f}});var o=t(6252),i=t(3577),l=t(3540),a={key:0,src:l,class:"loading"},r={key:1,class:"fas fa-circle-exclamation error"};function c(e,n,t,l,c,u){var s=(0,o.up)("Icon");return(0,o.wg)(),(0,o.iD)("div",{class:(0,i.C_)(["entity-icon-container",{"with-color-fill":!!u.colorFill}]),style:(0,i.j5)(u.colorFillStyle)},[t.loading?((0,o.wg)(),(0,o.iD)("img",a)):t.error?((0,o.wg)(),(0,o.iD)("i",r)):((0,o.wg)(),(0,o.j4)(s,(0,i.vs)((0,o.dG)({key:2},u.computedIcon)),null,16))],6)}var u=t(4648),s=(t(7042),t(1478)),d={name:"EntityIcon",components:{Icon:s.Z},props:{loading:{type:Boolean,default:!1},error:{type:Boolean,default:!1},icon:{type:Object,required:!0},hasColorFill:{type:Boolean,default:!1}},data:function(){return{component:null,modalVisible:!1}},computed:{colorFill:function(){return this.hasColorFill&&this.icon.color?this.icon.color:null},colorFillStyle:function(){return this.colorFill?{background:this.colorFill}:{}},computedIcon:function(){var e=(0,u.Z)({},this.icon);return this.colorFill&&delete e.color,e},type:function(){var e=this.entity.type||"";return e.charAt(0).toUpperCase()+e.slice(1)}}},p=t(3744);const v=(0,p.Z)(d,[["render",c],["__scopeId","data-v-6f83c443"]]);var f=v},518:function(e,n,t){t.r(n),t.d(n,{default:function(){return _}});t(8309);var o=t(6252),i=t(3577),l=t(9963),a={class:"entity switch-container"},r={class:"head"},c={class:"col-1 icon"},u={class:"col-9 label"},s=["textContent"],d={class:"col-2 switch pull-right"};function p(e,n,t,p,v,f){var h,g=(0,o.up)("EntityIcon"),m=(0,o.up)("ToggleSwitch");return(0,o.wg)(),(0,o.iD)("div",a,[(0,o._)("div",r,[(0,o._)("div",c,[(0,o.Wm)(g,{icon:(null===(h=e.value.meta)||void 0===h?void 0:h.icon)||{},loading:e.loading,error:e.error},null,8,["icon","loading","error"])]),(0,o._)("div",u,[(0,o._)("div",{class:"name",textContent:(0,i.zw)(e.value.name)},null,8,s)]),(0,o._)("div",d,[(0,o.Wm)(m,{value:e.value.state,onInput:f.toggle,onClick:n[0]||(n[0]=(0,l.iM)((function(){}),["stop"])),disabled:e.loading||e.value.is_read_only},null,8,["value","onInput","disabled"])])])])}var v=t(8534),f=(t(5666),t(6)),h=t(3499),g=t(7909),m={name:"Switch",components:{ToggleSwitch:f.Z,EntityIcon:h["default"]},mixins:[g["default"]],methods:{toggle:function(e){var n=this;return(0,v.Z)(regeneratorRuntime.mark((function t(){return regeneratorRuntime.wrap((function(t){while(1)switch(t.prev=t.next){case 0:return e.stopPropagation(),n.$emit("loading",!0),t.prev=2,t.next=5,n.request("entities.execute",{id:n.value.id,action:"toggle"});case 5:return t.prev=5,n.$emit("loading",!1),t.finish(5);case 8:case"end":return t.stop()}}),t,null,[[2,,5,8]])})))()}}},y=t(3744);const w=(0,y.Z)(m,[["render",p],["__scopeId","data-v-7feeaa4b"]]);var _=w},3540:function(e,n,t){e.exports=t.p+"static/img/spinner.c0bee445.gif"}}]);
//# sourceMappingURL=518-legacy.e665a841.js.map