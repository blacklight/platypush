"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[4842],{4842:function(e,t,n){n.r(t),n.d(t,{default:function(){return m}});var l=n(641),a=n(33);const o={class:"entity battery-container"},s={class:"head"},r={class:"icon"},c={class:"label"},u=["textContent"],i={class:"value-container"},v=["textContent"];function d(e,t,n,d,C,f){const p=(0,l.g2)("EntityIcon");return(0,l.uX)(),(0,l.CE)("div",o,[(0,l.Lk)("div",s,[(0,l.Lk)("div",r,[(0,l.bF)(p,{entity:e.value,icon:f.icon,loading:e.loading,error:e.error},null,8,["entity","icon","loading","error"])]),(0,l.Lk)("div",c,[(0,l.Lk)("div",{class:"name",textContent:(0,a.v_)(e.value.name)},null,8,u)]),(0,l.Lk)("div",i,[null!=f.valuePercent?((0,l.uX)(),(0,l.CE)("span",{key:0,class:"value",textContent:(0,a.v_)(f.valuePercent+"%")},null,8,v)):(0,l.Q3)("",!0)])])])}var C=n(4897),f=n(1029);const p=[{iconClass:"full",color:"#157145",value:.9},{iconClass:"three-quarters",color:"#94C595",value:.825},{iconClass:"half",color:"#F0B67F",value:.625},{iconClass:"quarter",color:"#FE5F55",value:.375},{iconClass:"low",color:"#CC444B",value:.15},{iconClass:"empty",color:"#EC0B43",value:.05}];var h={name:"Battery",components:{EntityIcon:f["default"]},mixins:[C["default"]],computed:{valuePercent(){if(null==this.value?.value)return null;const e=this.value.min||0,t=this.value.max||100;return(100*this.value.value/(t-e)).toFixed(0)},icon(){const e={...this.value.meta?.icon||{}};let t=this.valuePercent,n=p[0];if(null!=t){t=parseFloat(t)/100;for(const e of p){if(t>e.value)break;n=e}}return e["class"]=`fas fa-battery-${n.iconClass}`,e["color"]=n.color,e}},methods:{prevent(e){return e.stopPropagation(),!1}}},y=n(6262);const k=(0,y.A)(h,[["render",d],["__scopeId","data-v-4b2ced66"]]);var m=k}}]);
//# sourceMappingURL=4842.48cab2fd.js.map