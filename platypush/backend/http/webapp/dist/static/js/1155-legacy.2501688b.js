"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[1155,3673],{634:function(e,t,n){n.d(t,{N:function(){return o}});var r=n(9584);n(1703);function a(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}function i(e,t){for(var n=0;n<t.length;n++){var r=t[n];r.enumerable=r.enumerable||!1,r.configurable=!0,"value"in r&&(r.writable=!0),Object.defineProperty(e,r.key,r)}}function l(e,t,n){return t&&i(e.prototype,t),n&&i(e,n),Object.defineProperty(e,"prototype",{writable:!1}),e}n(7941),n(6977),n(1249),n(2222),n(7042),n(9600),n(1539),n(9714);var o=function(){function e(t){if(a(this,e),this.ranges={hue:[0,360],sat:[0,100],bri:[0,100],ct:[154,500]},t)for(var n=0,r=Object.keys(this.ranges);n<r.length;n++){var i=r[n];t[i]&&(this.ranges[i]=t[i])}}return l(e,[{key:"normalize",value:function(e,t,n){return n[0]+(e-t[0])*(n[1]-n[0])/(t[1]-t[0])}},{key:"hslToRgb",value:function(e,t,n){var r=[this.normalize(e,this.ranges.hue,[0,360]),this.normalize(t,this.ranges.sat,[0,100]),this.normalize(n,this.ranges.bri,[0,100])];e=r[0],t=r[1],n=r[2],n/=100;var a=t*Math.min(n,1-n)/100,i=function(t){var r=(t+e/30)%12,i=n-a*Math.max(Math.min(r-3,9-r,1),-1);return Math.round(255*i)};return[i(0),i(8),i(4)]}},{key:"rgbToHsl",value:function(e,t,n){e/=255,t/=255,n/=255;var r,a,i=Math.max(e,t,n),l=Math.min(e,t,n),o=(i+l)/2;if(i===l)r=a=0;else{var u=i-l;switch(a=o>.5?u/(2-i-l):u/(i+l),i){case e:r=(t-n)/u+(t<n?6:0);break;case t:r=(n-e)/u+2;break;case n:r=(e-t)/u+4;break}r/=6}return[parseInt(this.normalize(r,[0,1],this.ranges.hue)),parseInt(this.normalize(a,[0,1],this.ranges.sat)),parseInt(this.normalize(o,[0,1],this.ranges.bri))]}},{key:"xyToRgb",value:function(e,t,n){null==n&&(n=this.ranges.bri[1]);var r=1-e-t,a=(n/(this.ranges.bri[1]-1)).toFixed(2),i=a/t*e,l=a/t*r,o=1.656492*i-.354851*a-.255038*l,u=.707196*-i+1.655397*a+.036152*l,s=.051713*i-.121364*a+1.01153*l;return o>s&&o>u&&o>1?(u/=o,s/=o,o=1):u>s&&u>o&&u>1?(o/=u,s/=u,u=1):s>o&&s>u&&s>1&&(o/=s,u/=s,s=1),o=o<=.0031308?12.92*o:1.055*Math.pow(o,1/2.4)-.055,u=u<=.0031308?12.92*u:1.055*Math.pow(u,1/2.4)-.055,s=s<=.0031308?12.92*s:1.055*Math.pow(s,1/2.4)-.055,o=Math.round(255*o),u=Math.round(255*u),s=Math.round(255*s),isNaN(o)&&(o=0),isNaN(u)&&(u=0),isNaN(s)&&(s=0),[o,u,s].map((function(e){return Math.min(Math.max(0,e),255)}))}},{key:"rgbToXY",value:function(e,t,n){e>1&&(e/=255),t>1&&(t/=255),n>1&&(n/=255),e=e>.04045?Math.pow((e+.055)/1.055,2.4):e/12.92,t=t>.04045?Math.pow((t+.055)/1.055,2.4):t/12.92,n=n>.04045?Math.pow((n+.055)/1.055,2.4):n/12.92;var r=.664511*e+.154324*t+.162028*n,a=.283881*e+.668433*t+.047685*n,i=88e-6*e+.07231*t+.986039*n,l=parseFloat((r/(r+a+i)).toFixed(4)),o=parseFloat((a/(r+a+i)).toFixed(4));return isNaN(l)&&(l=0),isNaN(o)&&(o=0),[l,o]}},{key:"rgbToBri",value:function(e,t,n){return Math.min(2*this.rgbToHsl(e,t,n)[2],this.ranges.bri[1])}},{key:"getRGB",value:function(e){return null!=e.red&&null!=e.green&&null!=e.blue?[e.red,e.green,e.blue]:null!=e.r&&null!=e.g&&null!=e.b?[e.r,e.g,e.b]:e.rgb?e.rgb:void 0}},{key:"getXY",value:function(e){return null!=e.x&&null!=e.y?[e.x,e.y]:e.xy?e.xy:void 0}},{key:"toRGB",value:function(e){var t=this.getRGB(e);if(t)return t;var n=this.getXY(e);return n&&e.bri?this.xyToRgb.apply(this,(0,r.Z)(n).concat([e.bri])):e.hue&&e.sat&&e.bri?this.hslToRgb(e.hue,e.sat,e.bri):(console.debug("Could not determine color space"),void console.debug(e))}},{key:"toXY",value:function(e){var t=this.getXY(e);if(t&&e.bri)return[t[0],t[1],e.bri];var n=this.getRGB(e);if(n)return this.rgbToXY.apply(this,(0,r.Z)(n));if(e.hue&&e.sat&&e.bri){var a=this.hslToRgb(e.hue,e.sat,e.bri);return this.rgbToXY.apply(this,(0,r.Z)(a))}console.debug("Could not determine color space"),console.debug(e)}},{key:"toHSL",value:function(e){if(e.hue&&e.sat&&e.bri)return[e.hue,e.sat,e.bri];var t=this.getRGB(e);if(t)return this.rgbToHsl.apply(this,(0,r.Z)(t));var n=this.getXY(e);if(n&&e.bri){var a=this.xyToRgb.apply(this,(0,r.Z)(n).concat([e.bri]));return this.rgbToHsl.apply(this,(0,r.Z)(a))}console.debug("Could not determine color space"),console.debug(e)}},{key:"hexToRgb",value:function(e){return[e.slice(1,3),e.slice(3,5),e.slice(5,7)].map((function(e){return parseInt(e,16)}))}},{key:"rgbToHex",value:function(e){return"#"+e.map((function(e){var t=e.toString(16);return t.length<2&&(t="0"+t),t})).join("")}}]),e}()},6237:function(e,t,n){n.d(t,{Z:function(){return f}});var r=n(6252),a=n(3577),i=n(9963),l={class:"slider-wrapper"},o=["min","max","step","disabled","value"],u={class:"track-inner",ref:"track"},s={class:"thumb",ref:"thumb"},c=["textContent"];function h(e,t,n,h,d,v){return(0,r.wg)(),(0,r.iD)("label",l,[(0,r._)("input",{class:(0,a.C_)(["slider",{"with-label":n.withLabel}]),type:"range",min:n.range[0],max:n.range[1],step:n.step,disabled:n.disabled,value:n.value,ref:"range",onInput:t[0]||(t[0]=(0,i.iM)((function(){return v.onUpdate&&v.onUpdate.apply(v,arguments)}),["stop"])),onChange:t[1]||(t[1]=(0,i.iM)((function(){return v.onUpdate&&v.onUpdate.apply(v,arguments)}),["stop"]))},null,42,o),(0,r._)("div",{class:(0,a.C_)(["track",{"with-label":n.withLabel}])},[(0,r._)("div",u,null,512)],2),(0,r._)("div",s,null,512),n.withLabel?((0,r.wg)(),(0,r.iD)("span",{key:0,class:"label",textContent:(0,a.zw)(n.value),ref:"label"},null,8,c)):(0,r.kq)("",!0)])}var d=n(4648),v=(n(9653),{name:"Slider",emits:["input","change","mouseup","mousedown","touchstart","touchend","keyup","keydown"],props:{value:{type:Number},disabled:{type:Boolean,default:!1},range:{type:Array,default:function(){return[0,100]}},step:{type:Number,default:1},withLabel:{type:Boolean,default:!1}},methods:{onUpdate:function(e){this.update(e.target.value),this.$emit(e.type,(0,d.Z)((0,d.Z)({},e),{},{target:(0,d.Z)((0,d.Z)({},e.target),{},{value:this.$refs.range.value})}))},update:function(e){var t=this.$refs.range.clientWidth,n=(e-this.range[0])/(this.range[1]-this.range[0]),r=n*t,a=this.$refs.thumb;a.style.left="".concat(r-a.clientWidth/2,"px"),this.$refs.thumb.style.transform="translate(-".concat(n,"%, -50%)"),this.$refs.track.style.width="".concat(r,"px")}},mounted:function(){null!=this.value&&this.update(this.value)}}),p=n(3744);const g=(0,p.Z)(v,[["render",h],["__scopeId","data-v-15d8c6c5"]]);var f=g},6:function(e,t,n){n.d(t,{Z:function(){return p}});var r=n(6252),a=n(3577),i=n(9963),l=function(e){return(0,r.dD)("data-v-a6396ae8"),e=e(),(0,r.Cn)(),e},o=["checked"],u=l((function(){return(0,r._)("div",{class:"switch"},[(0,r._)("div",{class:"dot"})],-1)})),s={class:"label"};function c(e,t,n,l,c,h){return(0,r.wg)(),(0,r.iD)("div",{class:(0,a.C_)(["power-switch",{disabled:n.disabled}]),onClick:t[0]||(t[0]=(0,i.iM)((function(){return h.onInput&&h.onInput.apply(h,arguments)}),["stop"]))},[(0,r._)("input",{type:"checkbox",checked:n.value},null,8,o),(0,r._)("label",null,[u,(0,r._)("span",s,[(0,r.WI)(e.$slots,"default",{},void 0,!0)])])],2)}var h={name:"ToggleSwitch",emits:["input"],props:{value:{type:Boolean,default:!1},disabled:{type:Boolean,default:!1}},methods:{onInput:function(e){if(this.disabled)return!1;this.$emit("input",e)}}},d=n(3744);const v=(0,d.Z)(h,[["render",c],["__scopeId","data-v-a6396ae8"]]);var p=v},3673:function(e,t,n){n.r(t),n.d(t,{default:function(){return p}});var r=n(6252),a=n(3577),i=n(3540),l={key:0,src:i,class:"loading"},o={key:1,class:"fas fa-circle-exclamation error"};function u(e,t,n,i,u,s){var c=(0,r.up)("Icon");return(0,r.wg)(),(0,r.iD)("div",{class:(0,a.C_)(["entity-icon-container",{"with-color-fill":!!s.colorFill}]),style:(0,a.j5)(s.colorFillStyle)},[n.loading?((0,r.wg)(),(0,r.iD)("img",l)):n.error?((0,r.wg)(),(0,r.iD)("i",o)):((0,r.wg)(),(0,r.j4)(c,(0,a.vs)((0,r.dG)({key:2},s.computedIcon)),null,16))],6)}var s=n(4648),c=(n(7042),n(1478)),h={name:"EntityIcon",components:{Icon:c.Z},props:{loading:{type:Boolean,default:!1},error:{type:Boolean,default:!1},icon:{type:Object,required:!0},hasColorFill:{type:Boolean,default:!1}},data:function(){return{component:null,modalVisible:!1}},computed:{colorFill:function(){return this.hasColorFill&&this.icon.color?this.icon.color:null},colorFillStyle:function(){return this.colorFill&&!this.error?{background:this.colorFill}:{}},computedIcon:function(){var e=(0,s.Z)({},this.icon);return this.colorFill&&delete e.color,e},type:function(){var e=this.entity.type||"";return e.charAt(0).toUpperCase()+e.slice(1)}}},d=n(3744);const v=(0,d.Z)(h,[["render",u],["__scopeId","data-v-e4043550"]]);var p=v},1155:function(e,t,n){n.r(t),n.d(t,{default:function(){return z}});n(8309);var r=n(6252),a=n(3577),i=n(9963),l=function(e){return(0,r.dD)("data-v-18a5dc7b"),e=e(),(0,r.Cn)(),e},o={class:"entity light-container"},u={class:"col-1 icon"},s={class:"col-s-8 col-m-9 label"},c=["textContent"],h={class:"col-s-3 col-m-2 buttons pull-right"},d={key:0,class:"row"},v=l((function(){return(0,r._)("div",{class:"icon"},[(0,r._)("i",{class:"fas fa-palette"})],-1)})),p={class:"input"},g=["value"],f={key:1,class:"row"},b=l((function(){return(0,r._)("div",{class:"icon"},[(0,r._)("i",{class:"fas fa-sun"})],-1)})),m={class:"input"},y={key:2,class:"row"},_=l((function(){return(0,r._)("div",{class:"icon"},[(0,r._)("i",{class:"fas fa-droplet"})],-1)})),w={class:"input"},x={key:3,class:"row"},k=l((function(){return(0,r._)("div",{class:"icon"},[(0,r._)("i",{class:"fas fa-temperature-half"})],-1)})),C={class:"input"};function Z(e,t,n,l,Z,T){var I=(0,r.up)("EntityIcon"),M=(0,r.up)("ToggleSwitch"),R=(0,r.up)("Slider");return(0,r.wg)(),(0,r.iD)("div",o,[(0,r._)("div",{class:(0,a.C_)(["head",{expanded:Z.expanded}])},[(0,r._)("div",u,[(0,r.Wm)(I,{icon:T.icon,hasColorFill:!0,loading:e.loading,error:e.error},null,8,["icon","loading","error"])]),(0,r._)("div",s,[(0,r._)("div",{class:"name",textContent:(0,a.zw)(e.value.name)},null,8,c)]),(0,r._)("div",h,[(0,r.Wm)(M,{value:e.value.on,onInput:T.toggle,onClick:t[0]||(t[0]=(0,i.iM)((function(){}),["stop"])),disabled:e.loading||e.value.is_read_only},null,8,["value","onInput","disabled"]),(0,r._)("button",{onClick:t[1]||(t[1]=(0,i.iM)((function(e){return Z.expanded=!Z.expanded}),["stop"]))},[(0,r._)("i",{class:(0,a.C_)(["fas",{"fa-angle-up":Z.expanded,"fa-angle-down":!Z.expanded}])},null,2)])])],2),Z.expanded?((0,r.wg)(),(0,r.iD)("div",{key:0,class:"body",onClick:t[6]||(t[6]=(0,i.iM)((function(){return T.prevent&&T.prevent.apply(T,arguments)}),["stop"]))},[T.cssColor?((0,r.wg)(),(0,r.iD)("div",d,[v,(0,r._)("div",p,[(0,r._)("input",{type:"color",value:T.cssColor,onChange:t[2]||(t[2]=function(e){return T.setLight({color:e.target.value})})},null,40,g)])])):(0,r.kq)("",!0),e.value.brightness?((0,r.wg)(),(0,r.iD)("div",f,[b,(0,r._)("div",m,[(0,r.Wm)(R,{range:[e.value.brightness_min,e.value.brightness_max],value:e.value.brightness,onInput:t[3]||(t[3]=function(e){return T.setLight({brightness:e.target.value})})},null,8,["range","value"])])])):(0,r.kq)("",!0),e.value.saturation?((0,r.wg)(),(0,r.iD)("div",y,[_,(0,r._)("div",w,[(0,r.Wm)(R,{range:[e.value.saturation_min,e.value.saturation_max],value:e.value.saturation,onInput:t[4]||(t[4]=function(e){return T.setLight({saturation:e.target.value})})},null,8,["range","value"])])])):(0,r.kq)("",!0),e.value.temperature?((0,r.wg)(),(0,r.iD)("div",x,[k,(0,r._)("div",C,[(0,r.Wm)(R,{range:[e.value.temperature_min,e.value.temperature_max],value:e.value.temperature,onInput:t[5]||(t[5]=function(e){return T.setLight({temperature:e.target.value})})},null,8,["range","value"])])])):(0,r.kq)("",!0)])):(0,r.kq)("",!0)])}var T=n(6084),I=n(9584),M=n(8534),R=n(4648),F=(n(5666),n(6237)),D=n(6),N=n(7909),B=n(3673),L=n(634),S={name:"Light",components:{ToggleSwitch:D.Z,Slider:F.Z,EntityIcon:B["default"]},mixins:[N["default"]],data:function(){return{expanded:!1,colorConverter:null}},computed:{rgbColor:function(){var e,t;return null!==(e=this.value.meta)&&void 0!==e&&null!==(t=e.icon)&&void 0!==t&&t.color?this.value.meta.icon.color:this.colorConverter&&(null!=this.value.hue||null!=this.value.x&&null!=this.value.y)?this.value.x&&this.value.y?this.colorConverter.xyToRgb(this.value.x,this.value.y,this.value.brightness):this.colorConverter.hslToRgb(this.value.hue,this.value.saturation,this.value.brightness):void 0},cssColor:function(){var e=this.rgbColor;return e?this.colorConverter.rgbToHex(e):null},icon:function(){var e,t=(0,R.Z)({},(null===(e=this.value.meta)||void 0===e?void 0:e.icon)||{});return!t.color&&this.cssColor&&(t.color=this.cssColor),t}},methods:{prevent:function(e){return e.stopPropagation(),!1},toggle:function(e){var t=this;return(0,M.Z)(regeneratorRuntime.mark((function n(){return regeneratorRuntime.wrap((function(n){while(1)switch(n.prev=n.next){case 0:return e.stopPropagation(),t.$emit("loading",!0),n.prev=2,n.next=5,t.request("entities.execute",{id:t.value.id,action:"toggle"});case 5:return n.prev=5,t.$emit("loading",!1),n.finish(5);case 8:case"end":return n.stop()}}),n,null,[[2,,5,8]])})))()},setLight:function(e){var t=this;return(0,M.Z)(regeneratorRuntime.mark((function n(){var r,a,i,l,o;return regeneratorRuntime.wrap((function(n){while(1)switch(n.prev=n.next){case 0:e.color&&(r=t.colorConverter.hexToRgb(e.color),null!=t.value.x&&null!=t.value.y?(e.xy=(a=t.colorConverter).rgbToXY.apply(a,(0,I.Z)(r)),delete e.color):null!=t.value.hue&&(l=(i=t.colorConverter).rgbToHsl.apply(i,(0,I.Z)(r)),o=(0,T.Z)(l,3),e.hue=o[0],e.saturation=o[1],e.brightness=o[2],delete e.color)),t.execute({type:"request",action:t.value.plugin+".set_lights",args:(0,R.Z)({lights:[t.value.external_id]},e)});case 2:case"end":return n.stop()}}),n)})))()}},mounted:function(){var e={};this.value.hue&&(e.hue=[this.value.hue_min,this.value.hue_max]),this.value.saturation&&(e.sat=[this.value.saturation_min,this.value.saturation_max]),this.value.brightness&&(e.bri=[this.value.brightness_min,this.value.brightness_max]),this.value.temperature&&(e.ct=[this.value.temperature_min,this.value.temperature_max]),this.colorConverter=new L.N(e)}},$=n(3744);const q=(0,$.Z)(S,[["render",Z],["__scopeId","data-v-18a5dc7b"]]);var z=q},3540:function(e,t,n){e.exports=n.p+"static/img/spinner.c0bee445.gif"}}]);
//# sourceMappingURL=1155-legacy.2501688b.js.map