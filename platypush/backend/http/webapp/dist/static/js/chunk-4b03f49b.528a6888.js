(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-4b03f49b"],{"17dc":function(e,t,n){"use strict";n("b0c0");var i=n("7a23"),o=Object(i["K"])("data-v-755a3c5f");Object(i["u"])("data-v-755a3c5f");var a={class:"name col-l-10 col-m-9 col-s-8"},c=Object(i["h"])("i",{class:"fa fa-info"},null,-1),r={class:"toggler col-l-2 col-m-3 col-s-4"};Object(i["s"])();var s=o((function(e,t,n,o,s,u){var l=Object(i["z"])("Loading"),f=Object(i["z"])("ToggleSwitch");return Object(i["r"])(),Object(i["e"])("div",{class:"switch",onClick:t[2]||(t[2]=Object(i["J"])((function(){return u.onToggle.apply(u,arguments)}),["stop"]))},[n.loading?(Object(i["r"])(),Object(i["e"])(l,{key:0})):Object(i["f"])("",!0),Object(i["h"])("div",a,[n.hasInfo?(Object(i["r"])(),Object(i["e"])("button",{key:0,onClick:t[1]||(t[1]=Object(i["J"])((function(){return u.onInfo.apply(u,arguments)}),["prevent"]))},[c])):Object(i["f"])("",!0),Object(i["h"])("span",{class:"name-content",textContent:Object(i["C"])(n.name)},null,8,["textContent"])]),Object(i["h"])("div",r,[Object(i["h"])(f,{disabled:n.loading,value:n.state,onInput:u.onToggle},null,8,["disabled","value","onInput"])])])})),u=n("0279"),l=n("3a5e"),f={name:"Switch",components:{Loading:l["a"],ToggleSwitch:u["a"]},emits:["toggle","info"],props:{name:{type:String,required:!0},state:{type:Boolean,default:!1},loading:{type:Boolean,default:!1},hasInfo:{type:Boolean,default:!1}},methods:{onInfo:function(e){return e.stopPropagation(),this.$emit("info"),!1},onToggle:function(e){return e.stopPropagation(),this.$emit("toggle"),!1}}};n("21ae");f.render=s,f.__scopeId="data-v-755a3c5f";t["a"]=f},"21ae":function(e,t,n){"use strict";n("3386")},3386:function(e,t,n){},"487b":function(e,t,n){"use strict";n("13d5"),n("b0c0"),n("96cf");var i=n("1da1"),o=n("3e54"),a={name:"SwitchesMixin",mixins:[o["a"]],props:{pluginName:{type:String,required:!0},bus:{type:Object,required:!0},config:{type:Object,default:function(){return{}}},selected:{type:Boolean,default:!1}},data:function(){return{loading:!1,initialized:!1,selectedDevice:null,devices:{}}},methods:{onRefreshEvent:function(e){e===this.pluginName&&this.refresh()},toggle:function(e){var t=this;return Object(i["a"])(regeneratorRuntime.mark((function n(){var i;return regeneratorRuntime.wrap((function(n){while(1)switch(n.prev=n.next){case 0:return n.next=2,t.request("".concat(t.pluginName,".toggle"),{device:e});case 2:i=n.sent,t.devices[e].on=i.on;case 4:case"end":return n.stop()}}),n)})))()},refresh:function(){var e=this;return Object(i["a"])(regeneratorRuntime.mark((function t(){return regeneratorRuntime.wrap((function(t){while(1)switch(t.prev=t.next){case 0:return e.loading=!0,t.prev=1,t.next=4,e.request("".concat(e.pluginName,".status"));case 4:e.devices=t.sent.reduce((function(e,t){var n,i=(null===(n=t.name)||void 0===n?void 0:n.length)?t.name:t.id;return e[i]=t,e}),{});case 5:return t.prev=5,e.loading=!1,t.finish(5);case 8:case"end":return t.stop()}}),t,null,[[1,,5,8]])})))()}},mounted:function(){var e=this;this.$watch((function(){return e.selected}),(function(t){t&&!e.initialized&&(e.refresh(),e.initialized=!0)})),this.bus.on("refresh",this.onRefreshEvent)},unmounted:function(){this.bus.off("refresh",this.onRefreshEvent)}};t["a"]=a}}]);
//# sourceMappingURL=chunk-4b03f49b.528a6888.js.map