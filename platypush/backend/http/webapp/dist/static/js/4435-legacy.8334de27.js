"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[4435,3459],{4435:function(t,e,n){n.r(e),n.d(e,{default:function(){return h}});n(8309);var o=n(6252),i=n(3577),l={class:"entity device-container"},r={class:"head"},c={class:"col-1 icon"},a={class:"col-12 label"},u=["textContent"];function s(t,e,n,s,d,p){var f=(0,o.up)("EntityIcon");return(0,o.wg)(),(0,o.iD)("div",l,[(0,o._)("div",r,[(0,o._)("div",c,[(0,o.Wm)(f,{entity:t.value,loading:t.loading,error:t.error},null,8,["entity","loading","error"])]),(0,o._)("div",a,[(0,o._)("div",{class:"name",textContent:(0,i.zw)(t.value.name)},null,8,u)])])])}var d=n(7909),p=n(3459),f={name:"Device",components:{EntityIcon:p["default"]},mixins:[d["default"]]},v=n(3744);const y=(0,v.Z)(f,[["render",s],["__scopeId","data-v-06440d28"]]);var h=y},3459:function(t,e,n){n.r(e),n.d(e,{default:function(){return v}});var o=n(6252),i=n(3577),l=n(3540),r={key:0,src:l,class:"loading"},c={key:1,class:"fas fa-circle-exclamation error"};function a(t,e,n,l,a,u){var s=(0,o.up)("Icon");return(0,o.wg)(),(0,o.iD)("div",{class:(0,i.C_)(["entity-icon-container",{"with-color-fill":!!u.colorFill}]),style:(0,i.j5)(u.colorFillStyle)},[n.loading?((0,o.wg)(),(0,o.iD)("img",r)):n.error?((0,o.wg)(),(0,o.iD)("i",c)):((0,o.wg)(),(0,o.j4)(s,(0,i.vs)((0,o.dG)({key:2},u.computedIconNormalized)),null,16))],6)}var u=n(4648),s=(n(7941),n(7042),n(1478)),d={name:"EntityIcon",components:{Icon:s.Z},props:{loading:{type:Boolean,default:!1},error:{type:Boolean,default:!1},entity:{type:Object,required:!0},icon:{type:Object,default:function(){}},hasColorFill:{type:Boolean,default:!1}},data:function(){return{component:null,modalVisible:!1}},computed:{computedIcon:function(){var t,e,n=(0,u.Z)({},(null===(t=this.entity)||void 0===t||null===(e=t.meta)||void 0===e?void 0:e.icon)||{});return Object.keys(this.icon||{}).length&&(n=this.icon),(0,u.Z)({},n)},colorFill:function(){return this.hasColorFill&&this.computedIcon.color},colorFillStyle:function(){return this.colorFill&&!this.error?{background:this.colorFill}:{}},computedIconNormalized:function(){var t=(0,u.Z)({},this.computedIcon);return this.colorFill&&delete t.color,t},type:function(){var t=this.entity.type||"";return t.charAt(0).toUpperCase()+t.slice(1)}}},p=n(3744);const f=(0,p.Z)(d,[["render",a],["__scopeId","data-v-4fad24e6"]]);var v=f},3540:function(t,e,n){t.exports=n.p+"static/img/spinner.c0bee445.gif"}}]);
//# sourceMappingURL=4435-legacy.8334de27.js.map