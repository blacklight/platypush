"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[9651],{9651:function(e,t,l){l.r(t),l.d(t,{default:function(){return b}});var n=l(6252),a=l(3577);const o={class:"entity battery-container"},s={class:"head"},c={class:"col-1 icon"},r={class:"col-s-8 col-m-9 label"},u=["textContent"],i={class:"col-s-3 col-m-2 buttons pull-right"},v=["textContent"];function d(e,t,l,d,p,f){const C=(0,n.up)("EntityIcon");return(0,n.wg)(),(0,n.iD)("div",o,[(0,n._)("div",s,[(0,n._)("div",c,[(0,n.Wm)(C,{entity:e.value,icon:f.icon,loading:e.loading,error:e.error},null,8,["entity","icon","loading","error"])]),(0,n._)("div",r,[(0,n._)("div",{class:"name",textContent:(0,a.zw)(e.value.name)},null,8,u)]),(0,n._)("div",i,[null!=f.valuePercent?((0,n.wg)(),(0,n.iD)("span",{key:0,class:"value-percent",textContent:(0,a.zw)(f.valuePercent+"%")},null,8,v)):(0,n.kq)("",!0)])])])}var p=l(7909),f=l(3459);const C=[{iconClass:"full",color:"#157145",value:.9},{iconClass:"three-quarters",color:"#94C595",value:.825},{iconClass:"half",color:"#F0B67F",value:.625},{iconClass:"quarter",color:"#FE5F55",value:.375},{iconClass:"low",color:"#CC444B",value:.15},{iconClass:"empty",color:"#EC0B43",value:.05}];var h={name:"Battery",components:{EntityIcon:f["default"]},mixins:[p["default"]],computed:{valuePercent(){if(null==this.value?.value)return null;const e=this.value.min||0,t=this.value.max||100;return(100*this.value.value/(t-e)).toFixed(0)},icon(){const e={...this.value.meta?.icon||{}};let t=this.valuePercent,l=C[0];if(null!=t){t=parseFloat(t)/100;for(const e of C){if(t>e.value)break;l=e}}return e["class"]=`fas fa-battery-${l.iconClass}`,e["color"]=l.color,e}},methods:{prevent(e){return e.stopPropagation(),!1}}},m=l(3744);const y=(0,m.Z)(h,[["render",d],["__scopeId","data-v-fb9c9926"]]);var b=y}}]);
//# sourceMappingURL=9651.5535826c.js.map