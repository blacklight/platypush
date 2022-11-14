"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[6365,3673],{6237:function(e,t,n){n.d(t,{Z:function(){return m}});var a=n(6252),l=n(3577),i=n(9963),r={class:"slider-wrapper"},o=["min","max","step","disabled","value"],u={class:"track-inner",ref:"track"},s={class:"thumb",ref:"thumb"},c=["textContent"];function d(e,t,n,d,p,v){return(0,a.wg)(),(0,a.iD)("label",r,[(0,a._)("input",{class:(0,l.C_)(["slider",{"with-label":n.withLabel}]),type:"range",min:n.range[0],max:n.range[1],step:n.step,disabled:n.disabled,value:n.value,ref:"range",onInput:t[0]||(t[0]=(0,i.iM)((function(){return v.onUpdate&&v.onUpdate.apply(v,arguments)}),["stop"])),onChange:t[1]||(t[1]=(0,i.iM)((function(){return v.onUpdate&&v.onUpdate.apply(v,arguments)}),["stop"]))},null,42,o),(0,a._)("div",{class:(0,l.C_)(["track",{"with-label":n.withLabel}])},[(0,a._)("div",u,null,512)],2),(0,a._)("div",s,null,512),n.withLabel?((0,a.wg)(),(0,a.iD)("span",{key:0,class:"label",textContent:(0,l.zw)(n.value),ref:"label"},null,8,c)):(0,a.kq)("",!0)])}var p=n(4648),v=(n(9653),{name:"Slider",emits:["input","change","mouseup","mousedown","touchstart","touchend","keyup","keydown"],props:{value:{type:Number},disabled:{type:Boolean,default:!1},range:{type:Array,default:function(){return[0,100]}},step:{type:Number,default:1},withLabel:{type:Boolean,default:!1}},methods:{onUpdate:function(e){this.update(e.target.value),this.$emit(e.type,(0,p.Z)((0,p.Z)({},e),{},{target:(0,p.Z)((0,p.Z)({},e.target),{},{value:this.$refs.range.value})}))},update:function(e){var t=this.$refs.range.clientWidth,n=(e-this.range[0])/(this.range[1]-this.range[0]),a=n*t,l=this.$refs.thumb;l.style.left="".concat(a-l.clientWidth/2,"px"),this.$refs.thumb.style.transform="translate(-".concat(n,"%, -50%)"),this.$refs.track.style.width="".concat(a,"px")}},mounted:function(){null!=this.value&&this.update(this.value)}}),f=n(3744);const h=(0,f.Z)(v,[["render",d],["__scopeId","data-v-15d8c6c5"]]);var m=h},6365:function(e,t,n){n.r(t),n.d(t,{default:function(){return _}});n(8309),n(6977);var a=n(6252),l=n(3577),i=n(9963),r={class:"entity dimmer-container"},o={class:"col-1 icon"},u={class:"col-s-8 col-m-9 label"},s=["textContent"],c={class:"col-s-3 col-m-2 buttons pull-right"},d=["textContent"],p={class:"row"},v={class:"input"};function f(e,t,n,f,h,m){var g,y=(0,a.up)("EntityIcon"),w=(0,a.up)("Slider");return(0,a.wg)(),(0,a.iD)("div",r,[(0,a._)("div",{class:(0,l.C_)(["head",{expanded:h.expanded}])},[(0,a._)("div",o,[(0,a.Wm)(y,{icon:(null===(g=this.value.meta)||void 0===g?void 0:g.icon)||{},loading:e.loading,error:e.error},null,8,["icon","loading","error"])]),(0,a._)("div",u,[(0,a._)("div",{class:"name",textContent:(0,l.zw)(e.value.name)},null,8,s)]),(0,a._)("div",c,[(0,a._)("button",{onClick:t[0]||(t[0]=(0,i.iM)((function(e){return h.expanded=!h.expanded}),["stop"]))},[(0,a._)("i",{class:(0,l.C_)(["fas",{"fa-angle-up":h.expanded,"fa-angle-down":!h.expanded}])},null,2)]),null!=m.valuePercent?((0,a.wg)(),(0,a.iD)("span",{key:0,class:"value-percent",textContent:(0,l.zw)(m.valuePercent.toFixed(0)+"%")},null,8,d)):(0,a.kq)("",!0)])],2),h.expanded?((0,a.wg)(),(0,a.iD)("div",{key:0,class:"body",onClick:t[1]||(t[1]=(0,i.iM)((function(){return m.prevent&&m.prevent.apply(m,arguments)}),["stop"]))},[(0,a._)("div",p,[(0,a._)("div",v,[(0,a.Wm)(w,{range:[e.value.min,e.value.max],value:e.value.value,onInput:m.setValue},null,8,["range","value","onInput"])])])])):(0,a.kq)("",!0)])}var h=n(8534),m=(n(5666),n(6237)),g=n(7909),y=n(3673),w={name:"Dimmer",components:{Slider:m.Z,EntityIcon:y["default"]},mixins:[g["default"]],data:function(){return{expanded:!1}},computed:{valuePercent:function(){var e,t;if(null!==(e=this.value)&&void 0!==e&&e.is_write_only||null==(null===(t=this.value)||void 0===t?void 0:t.value))return null;var n=this.value.min||0,a=this.value.max||100;return 100*this.value.value/(a-n)}},methods:{prevent:function(e){return e.stopPropagation(),!1},setValue:function(e){var t=this;return(0,h.Z)(regeneratorRuntime.mark((function n(){return regeneratorRuntime.wrap((function(n){while(1)switch(n.prev=n.next){case 0:return t.$emit("loading",!0),n.prev=1,n.next=4,t.request("entities.execute",{id:t.value.id,action:"set_value",data:+e.target.value});case 4:return n.prev=4,t.$emit("loading",!1),n.finish(4);case 7:case"end":return n.stop()}}),n,null,[[1,,4,7]])})))()}}},b=n(3744);const x=(0,b.Z)(w,[["render",f],["__scopeId","data-v-162eb0f4"]]);var _=x},3673:function(e,t,n){n.r(t),n.d(t,{default:function(){return f}});var a=n(6252),l=n(3577),i=n(3540),r={key:0,src:i,class:"loading"},o={key:1,class:"fas fa-circle-exclamation error"};function u(e,t,n,i,u,s){var c=(0,a.up)("Icon");return(0,a.wg)(),(0,a.iD)("div",{class:(0,l.C_)(["entity-icon-container",{"with-color-fill":!!s.colorFill}]),style:(0,l.j5)(s.colorFillStyle)},[n.loading?((0,a.wg)(),(0,a.iD)("img",r)):n.error?((0,a.wg)(),(0,a.iD)("i",o)):((0,a.wg)(),(0,a.j4)(c,(0,l.vs)((0,a.dG)({key:2},s.computedIcon)),null,16))],6)}var s=n(4648),c=(n(7042),n(1478)),d={name:"EntityIcon",components:{Icon:c.Z},props:{loading:{type:Boolean,default:!1},error:{type:Boolean,default:!1},icon:{type:Object,required:!0},hasColorFill:{type:Boolean,default:!1}},data:function(){return{component:null,modalVisible:!1}},computed:{colorFill:function(){return this.hasColorFill&&this.icon.color?this.icon.color:null},colorFillStyle:function(){return this.colorFill&&!this.error?{background:this.colorFill}:{}},computedIcon:function(){var e=(0,s.Z)({},this.icon);return this.colorFill&&delete e.color,e},type:function(){var e=this.entity.type||"";return e.charAt(0).toUpperCase()+e.slice(1)}}},p=n(3744);const v=(0,p.Z)(d,[["render",u],["__scopeId","data-v-e4043550"]]);var f=v},3540:function(e,t,n){e.exports=n.p+"static/img/spinner.c0bee445.gif"}}]);
//# sourceMappingURL=6365-legacy.f0476e2f.js.map