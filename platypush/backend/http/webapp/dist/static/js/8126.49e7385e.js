"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[8126],{8126:function(t,e,n){n.r(e),n.d(e,{default:function(){return k}});var l=n(6252),a=n(3577);const u={class:"entity link-quality-container"},i={class:"head"},s={class:"col-1 icon"},c={class:"col-s-8 col-m-9 label"},o=["textContent"],r={class:"col-s-3 col-m-2 buttons pull-right"},v=["textContent"];function d(t,e,n,d,p,h){const m=(0,l.up)("EntityIcon");return(0,l.wg)(),(0,l.iD)("div",u,[(0,l._)("div",i,[(0,l._)("div",s,[(0,l.Wm)(m,{entity:t.value,loading:t.loading,error:t.error},null,8,["entity","loading","error"])]),(0,l._)("div",c,[(0,l._)("div",{class:"name",textContent:(0,a.zw)(t.value.name)},null,8,o)]),(0,l._)("div",r,[null!=h.valuePercent?((0,l.wg)(),(0,l.iD)("span",{key:0,class:"value-percent",textContent:(0,a.zw)(h.valuePercent+"%")},null,8,v)):(0,l.kq)("",!0)])])])}var p=n(7909),h=n(3459),m={name:"LinkQuality",components:{EntityIcon:h["default"]},mixins:[p["default"]],computed:{valuePercent(){if(null==this.value?.value)return null;const t=this.value.min||0,e=this.value.max||100;return(100*this.value.value/(e-t)).toFixed(0)}}},f=n(3744);const y=(0,f.Z)(m,[["render",d],["__scopeId","data-v-4ca8847f"]]);var k=y}}]);
//# sourceMappingURL=8126.49e7385e.js.map