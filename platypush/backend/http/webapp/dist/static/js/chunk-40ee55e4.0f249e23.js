(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-40ee55e4"],{"7b41":function(e,t,n){"use strict";n("98e8")},"98e8":function(e,t,n){},dbf7:function(e,t,n){"use strict";n.r(t);var r=n("7a23"),c=Object(r["K"])("data-v-30d09191");Object(r["u"])("data-v-30d09191");var o={class:"sound"},a={class:"sound-container"},s={key:0,autoplay:"",preload:"none",ref:"player"},i=Object(r["g"])(" Your browser does not support audio elements "),u={class:"controls"},d=Object(r["h"])("i",{class:"fa fa-play"},null,-1),b=Object(r["g"])("  Start streaming audio "),p=Object(r["h"])("i",{class:"fa fa-stop"},null,-1),l=Object(r["g"])("  Stop streaming audio ");Object(r["s"])();var j=c((function(e,t,n,c,j,O){return Object(r["r"])(),Object(r["e"])("div",o,[Object(r["h"])("div",a,[j.recording?(Object(r["r"])(),Object(r["e"])("audio",s,[Object(r["h"])("source",{src:"/sound/stream?t=".concat((new Date).getTime()),type:"audio/x-wav;codec=pcm"},null,8,["src"]),i],512)):Object(r["f"])("",!0)]),Object(r["h"])("div",u,[j.recording?(Object(r["r"])(),Object(r["e"])("button",{key:1,type:"button",onClick:t[2]||(t[2]=function(){return O.stopRecording.apply(O,arguments)})},[p,l])):(Object(r["r"])(),Object(r["e"])("button",{key:0,type:"button",onClick:t[1]||(t[1]=function(){return O.startRecording.apply(O,arguments)})},[d,b]))])])})),O=(n("96cf"),n("1da1")),f=n("3e54"),g={name:"Sound",mixins:[f["a"]],data:function(){return{recording:!1}},methods:{startRecording:function(){this.recording=!0},stopRecording:function(){var e=this;return Object(O["a"])(regeneratorRuntime.mark((function t(){return regeneratorRuntime.wrap((function(t){while(1)switch(t.prev=t.next){case 0:return e.recording=!1,t.next=3,e.request("sound.stop_recording");case 3:case"end":return t.stop()}}),t)})))()}}};n("7b41");g.render=j,g.__scopeId="data-v-30d09191";t["default"]=g}}]);
//# sourceMappingURL=chunk-40ee55e4.0f249e23.js.map