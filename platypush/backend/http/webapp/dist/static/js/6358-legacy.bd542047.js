"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[6358],{6358:function(e,t,n){n.r(t),n.d(t,{default:function(){return b}});n(8309),n(1539),n(3948);var l=n(6252),a=n(3577),u=n(9963),i={class:"entity switch-container"},s={class:"icon"},r={class:"label"},o=["textContent"],v={class:"value-container"},c=["textContent"],d={class:"row"},p={class:"input"},f=["disabled"],h={key:0,value:"",selected:""},g=["value","selected","textContent"];function w(e,t,n,w,y,k){var _,m=(0,l.up)("EntityIcon");return(0,l.wg)(),(0,l.iD)("div",i,[(0,l._)("div",{class:(0,a.C_)(["head",{collapsed:e.collapsed}])},[(0,l._)("div",s,[(0,l.Wm)(m,{entity:e.value,loading:e.loading,error:e.error},null,8,["entity","loading","error"])]),(0,l._)("div",r,[(0,l._)("div",{class:"name",textContent:(0,a.zw)(e.value.name)},null,8,o)]),(0,l._)("div",v,[null!=(null===(_=e.value)||void 0===_?void 0:_.value)?((0,l.wg)(),(0,l.iD)("span",{key:0,class:"value",textContent:(0,a.zw)(e.value.values[e.value.value]||e.value.value)},null,8,c)):(0,l.kq)("",!0),k.hasValues?((0,l.wg)(),(0,l.iD)("button",{key:1,onClick:t[0]||(t[0]=(0,u.iM)((function(t){return e.collapsed=!e.collapsed}),["stop"]))},[(0,l._)("i",{class:(0,a.C_)(["fas",{"fa-angle-up":!e.collapsed,"fa-angle-down":e.collapsed}])},null,2)])):(0,l.kq)("",!0)])],2),e.collapsed?(0,l.kq)("",!0):((0,l.wg)(),(0,l.iD)("div",{key:0,class:"body",onClick:t[2]||(t[2]=(0,u.iM)((function(){return k.prevent&&k.prevent.apply(k,arguments)}),["stop"]))},[(0,l._)("div",d,[(0,l._)("div",p,[(0,l._)("select",{onInput:t[1]||(t[1]=function(){return k.setValue&&k.setValue.apply(k,arguments)}),ref:"values",disabled:e.loading},[e.value.is_write_only?((0,l.wg)(),(0,l.iD)("option",h,"--")):(0,l.kq)("",!0),((0,l.wg)(!0),(0,l.iD)(l.HY,null,(0,l.Ko)(k.displayValues,(function(t,n){return(0,l.wg)(),(0,l.iD)("option",{value:n,selected:n==e.value.value,key:n,textContent:(0,a.zw)(t)},null,8,g)})),128))],40,f)])])]))])}var y=n(8534),k=(n(5666),n(2479),n(7909)),_=n(343),m={name:"EnumSwitch",components:{EntityIcon:_["default"]},mixins:[k["default"]],computed:{hasValues:function(){var e;return!!Object.values((null===this||void 0===this||null===(e=this.value)||void 0===e?void 0:e.values)||{}).length},displayValues:function(){var e,t;return(null===(e=this.value)||void 0===e?void 0:e.values)instanceof Array?this.value.values.reduce((function(e,t){return e[t]=t,e}),{}):(null===(t=this.value)||void 0===t?void 0:t.values)||{}}},methods:{prevent:function(e){return e.stopPropagation(),!1},setValue:function(e){var t=this;return(0,y.Z)(regeneratorRuntime.mark((function n(){var l,a;return regeneratorRuntime.wrap((function(n){while(1)switch(n.prev=n.next){case 0:if(null!==(l=e.target.value)&&void 0!==l&&l.length){n.next=2;break}return n.abrupt("return");case 2:return t.$emit("loading",!0),t.value.is_write_only&&(a=t,setTimeout((function(){a.$refs.values.value=""}),1e3)),n.prev=4,n.next=7,t.request("entities.execute",{id:t.value.id,action:"set",value:e.target.value});case 7:return n.prev=7,t.$emit("loading",!1),n.finish(7);case 10:case"end":return n.stop()}}),n,null,[[4,,7,10]])})))()}}},C=n(3744);const x=(0,C.Z)(m,[["render",w],["__scopeId","data-v-043593ec"]]);var b=x}}]);
//# sourceMappingURL=6358-legacy.bd542047.js.map