"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[1155,3499],{634:function(e,t,n){n.d(t,{N:function(){return l}});var a=n(9584);n(1703);function r(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}function i(e,t){for(var n=0;n<t.length;n++){var a=t[n];a.enumerable=a.enumerable||!1,a.configurable=!0,"value"in a&&(a.writable=!0),Object.defineProperty(e,a.key,a)}}function o(e,t,n){return t&&i(e.prototype,t),n&&i(e,n),Object.defineProperty(e,"prototype",{writable:!1}),e}n(7941),n(6977),n(1249),n(2222),n(7042),n(9600),n(1539),n(9714);var l=function(){function e(t){if(r(this,e),this.ranges={hue:[0,360],sat:[0,100],bri:[0,100],ct:[154,500]},t)for(var n=0,a=Object.keys(this.ranges);n<a.length;n++){var i=a[n];t[i]&&(this.ranges[i]=t[i])}}return o(e,[{key:"normalize",value:function(e,t,n){return n[0]+(e-t[0])*(n[1]-n[0])/(t[1]-t[0])}},{key:"hslToRgb",value:function(e,t,n){var a=[this.normalize(e,this.ranges.hue,[0,360]),this.normalize(t,this.ranges.sat,[0,100]),this.normalize(n,this.ranges.bri,[0,100])];e=a[0],t=a[1],n=a[2],n/=100;var r=t*Math.min(n,1-n)/100,i=function(t){var a=(t+e/30)%12,i=n-r*Math.max(Math.min(a-3,9-a,1),-1);return Math.round(255*i)};return[i(0),i(8),i(4)]}},{key:"rgbToHsl",value:function(e,t,n){e/=255,t/=255,n/=255;var a,r,i=Math.max(e,t,n),o=Math.min(e,t,n),l=(i+o)/2;if(i===o)a=r=0;else{var u=i-o;switch(r=l>.5?u/(2-i-o):u/(i+o),i){case e:a=(t-n)/u+(t<n?6:0);break;case t:a=(n-e)/u+2;break;case n:a=(e-t)/u+4;break}a/=6}return[parseInt(this.normalize(a,[0,1],this.ranges.hue)),parseInt(this.normalize(r,[0,1],this.ranges.sat)),parseInt(this.normalize(l,[0,1],this.ranges.bri))]}},{key:"xyToRgb",value:function(e,t,n){null==n&&(n=this.ranges.bri[1]);var a=1-e-t,r=(n/(this.ranges.bri[1]-1)).toFixed(2),i=r/t*e,o=r/t*a,l=1.656492*i-.354851*r-.255038*o,u=.707196*-i+1.655397*r+.036152*o,s=.051713*i-.121364*r+1.01153*o;return l>s&&l>u&&l>1?(u/=l,s/=l,l=1):u>s&&u>l&&u>1?(l/=u,s/=u,u=1):s>l&&s>u&&s>1&&(l/=s,u/=s,s=1),l=l<=.0031308?12.92*l:1.055*Math.pow(l,1/2.4)-.055,u=u<=.0031308?12.92*u:1.055*Math.pow(u,1/2.4)-.055,s=s<=.0031308?12.92*s:1.055*Math.pow(s,1/2.4)-.055,l=Math.round(255*l),u=Math.round(255*u),s=Math.round(255*s),isNaN(l)&&(l=0),isNaN(u)&&(u=0),isNaN(s)&&(s=0),[l,u,s].map((function(e){return Math.min(Math.max(0,e),255)}))}},{key:"rgbToXY",value:function(e,t,n){e>1&&(e/=255),t>1&&(t/=255),n>1&&(n/=255),e=e>.04045?Math.pow((e+.055)/1.055,2.4):e/12.92,t=t>.04045?Math.pow((t+.055)/1.055,2.4):t/12.92,n=n>.04045?Math.pow((n+.055)/1.055,2.4):n/12.92;var a=.664511*e+.154324*t+.162028*n,r=.283881*e+.668433*t+.047685*n,i=88e-6*e+.07231*t+.986039*n,o=parseFloat((a/(a+r+i)).toFixed(4)),l=parseFloat((r/(a+r+i)).toFixed(4));return isNaN(o)&&(o=0),isNaN(l)&&(l=0),[o,l]}},{key:"rgbToBri",value:function(e,t,n){return Math.min(2*this.rgbToHsl(e,t,n)[2],this.ranges.bri[1])}},{key:"getRGB",value:function(e){return null!=e.red&&null!=e.green&&null!=e.blue?[e.red,e.green,e.blue]:null!=e.r&&null!=e.g&&null!=e.b?[e.r,e.g,e.b]:e.rgb?e.rgb:void 0}},{key:"getXY",value:function(e){return null!=e.x&&null!=e.y?[e.x,e.y]:e.xy?e.xy:void 0}},{key:"toRGB",value:function(e){var t=this.getRGB(e);if(t)return t;var n=this.getXY(e);return n&&e.bri?this.xyToRgb.apply(this,(0,a.Z)(n).concat([e.bri])):e.hue&&e.sat&&e.bri?this.hslToRgb(e.hue,e.sat,e.bri):(console.debug("Could not determine color space"),void console.debug(e))}},{key:"toXY",value:function(e){var t=this.getXY(e);if(t&&e.bri)return[t[0],t[1],e.bri];var n=this.getRGB(e);if(n)return this.rgbToXY.apply(this,(0,a.Z)(n));if(e.hue&&e.sat&&e.bri){var r=this.hslToRgb(e.hue,e.sat,e.bri);return this.rgbToXY.apply(this,(0,a.Z)(r))}console.debug("Could not determine color space"),console.debug(e)}},{key:"toHSL",value:function(e){if(e.hue&&e.sat&&e.bri)return[e.hue,e.sat,e.bri];var t=this.getRGB(e);if(t)return this.rgbToHsl.apply(this,(0,a.Z)(t));var n=this.getXY(e);if(n&&e.bri){var r=this.xyToRgb.apply(this,(0,a.Z)(n).concat([e.bri]));return this.rgbToHsl.apply(this,(0,a.Z)(r))}console.debug("Could not determine color space"),console.debug(e)}},{key:"hexToRgb",value:function(e){return[e.slice(1,3),e.slice(3,5),e.slice(5,7)].map((function(e){return parseInt(e,16)}))}},{key:"rgbToHex",value:function(e){return"#"+e.map((function(e){var t=e.toString(16);return t.length<2&&(t="0"+t),t})).join("")}}]),e}()},8070:function(e,t,n){n.d(t,{Z:function(){return f}});var a=n(6252),r=n(3577),i=n(9963),o={class:"slider-wrapper"},l=["min","max","step","disabled","value"],u={class:"track-inner",ref:"track"},s={class:"thumb",ref:"thumb"},c=["textContent"];function p(e,t,n,p,h,d){return(0,a.wg)(),(0,a.iD)("label",o,[(0,a._)("input",{class:(0,r.C_)(["slider",{"with-label":n.withLabel}]),type:"range",min:n.range[0],max:n.range[1],step:n.step,disabled:n.disabled,value:n.value,ref:"range",onInput:t[0]||(t[0]=(0,i.iM)((function(){return d.onUpdate&&d.onUpdate.apply(d,arguments)}),["stop"])),onChange:t[1]||(t[1]=(0,i.iM)((function(){return d.onUpdate&&d.onUpdate.apply(d,arguments)}),["stop"])),onMouseup:t[2]||(t[2]=(0,i.iM)((function(){return d.onUpdate&&d.onUpdate.apply(d,arguments)}),["stop"])),onMousedown:t[3]||(t[3]=(0,i.iM)((function(){return d.onUpdate&&d.onUpdate.apply(d,arguments)}),["stop"])),onTouchstart:t[4]||(t[4]=(0,i.iM)((function(){return d.onUpdate&&d.onUpdate.apply(d,arguments)}),["stop"])),onTouchend:t[5]||(t[5]=(0,i.iM)((function(){return d.onUpdate&&d.onUpdate.apply(d,arguments)}),["stop"])),onKeyup:t[6]||(t[6]=(0,i.iM)((function(){return d.onUpdate&&d.onUpdate.apply(d,arguments)}),["stop"])),onKeydown:t[7]||(t[7]=(0,i.iM)((function(){return d.onUpdate&&d.onUpdate.apply(d,arguments)}),["stop"]))},null,42,l),(0,a._)("div",{class:(0,r.C_)(["track",{"with-label":n.withLabel}])},[(0,a._)("div",u,null,512)],2),(0,a._)("div",s,null,512),n.withLabel?((0,a.wg)(),(0,a.iD)("span",{key:0,class:"label",textContent:(0,r.zw)(n.value),ref:"label"},null,8,c)):(0,a.kq)("",!0)])}var h=n(4648),d=(n(9653),{name:"Slider",emits:["input","change","mouseup","mousedown","touchstart","touchend","keyup","keydown"],props:{value:{type:Number},disabled:{type:Boolean,default:!1},range:{type:Array,default:function(){return[0,100]}},step:{type:Number,default:1},withLabel:{type:Boolean,default:!1}},methods:{onUpdate:function(e){this.update(e.target.value),this.$emit(e.type,(0,h.Z)((0,h.Z)({},e),{},{target:(0,h.Z)((0,h.Z)({},e.target),{},{value:this.$refs.range.value})}))},update:function(e){var t=this.$refs.range.clientWidth,n=(e-this.range[0])/(this.range[1]-this.range[0]),a=n*t,r=this.$refs.thumb;r.style.left="".concat(a-r.clientWidth/2,"px"),this.$refs.thumb.style.transform="translate(-".concat(n,"%, -50%)"),this.$refs.track.style.width="".concat(a,"px")}},mounted:function(){null!=this.value&&this.update(this.value)}}),v=n(3744);const g=(0,v.Z)(d,[["render",p],["__scopeId","data-v-0359812c"]]);var f=g},6:function(e,t,n){n.d(t,{Z:function(){return v}});var a=n(6252),r=n(3577),i=n(9963),o=function(e){return(0,a.dD)("data-v-a6396ae8"),e=e(),(0,a.Cn)(),e},l=["checked"],u=o((function(){return(0,a._)("div",{class:"switch"},[(0,a._)("div",{class:"dot"})],-1)})),s={class:"label"};function c(e,t,n,o,c,p){return(0,a.wg)(),(0,a.iD)("div",{class:(0,r.C_)(["power-switch",{disabled:n.disabled}]),onClick:t[0]||(t[0]=(0,i.iM)((function(){return p.onInput&&p.onInput.apply(p,arguments)}),["stop"]))},[(0,a._)("input",{type:"checkbox",checked:n.value},null,8,l),(0,a._)("label",null,[u,(0,a._)("span",s,[(0,a.WI)(e.$slots,"default",{},void 0,!0)])])],2)}var p={name:"ToggleSwitch",emits:["input"],props:{value:{type:Boolean,default:!1},disabled:{type:Boolean,default:!1}},methods:{onInput:function(e){if(this.disabled)return!1;this.$emit("input",e)}}},h=n(3744);const d=(0,h.Z)(p,[["render",c],["__scopeId","data-v-a6396ae8"]]);var v=d},3499:function(e,t,n){n.r(t),n.d(t,{default:function(){return v}});var a=n(6252),r=n(3577),i=n(3540),o={key:0,src:i,class:"loading"},l={key:1,class:"fas fa-circle-exclamation error"};function u(e,t,n,i,u,s){var c=(0,a.up)("Icon");return(0,a.wg)(),(0,a.iD)("div",{class:(0,r.C_)(["entity-icon-container",{"with-color-fill":!!s.colorFill}]),style:(0,r.j5)(s.colorFillStyle)},[n.loading?((0,a.wg)(),(0,a.iD)("img",o)):n.error?((0,a.wg)(),(0,a.iD)("i",l)):((0,a.wg)(),(0,a.j4)(c,(0,r.vs)((0,a.dG)({key:2},s.computedIcon)),null,16))],6)}var s=n(4648),c=(n(7042),n(1478)),p={name:"EntityIcon",components:{Icon:c.Z},props:{loading:{type:Boolean,default:!1},error:{type:Boolean,default:!1},icon:{type:Object,required:!0},hasColorFill:{type:Boolean,default:!1}},data:function(){return{component:null,modalVisible:!1}},computed:{colorFill:function(){return this.hasColorFill&&this.icon.color?this.icon.color:null},colorFillStyle:function(){return this.colorFill?{background:this.colorFill}:{}},computedIcon:function(){var e=(0,s.Z)({},this.icon);return this.colorFill&&delete e.color,e},type:function(){var e=this.entity.type||"";return e.charAt(0).toUpperCase()+e.slice(1)}}},h=n(3744);const d=(0,h.Z)(p,[["render",u],["__scopeId","data-v-6f83c443"]]);var v=d},1155:function(e,t,n){n.r(t),n.d(t,{default:function(){return q}});n(8309);var a=n(6252),r=n(3577),i=n(9963),o=function(e){return(0,a.dD)("data-v-18a5dc7b"),e=e(),(0,a.Cn)(),e},l={class:"entity light-container"},u={class:"col-1 icon"},s={class:"col-s-8 col-m-9 label"},c=["textContent"],p={class:"col-s-3 col-m-2 buttons pull-right"},h={key:0,class:"row"},d=o((function(){return(0,a._)("div",{class:"icon"},[(0,a._)("i",{class:"fas fa-palette"})],-1)})),v={class:"input"},g=["value"],f={key:1,class:"row"},b=o((function(){return(0,a._)("div",{class:"icon"},[(0,a._)("i",{class:"fas fa-sun"})],-1)})),m={class:"input"},y={key:2,class:"row"},_=o((function(){return(0,a._)("div",{class:"icon"},[(0,a._)("i",{class:"fas fa-droplet"})],-1)})),w={class:"input"},x={key:3,class:"row"},k=o((function(){return(0,a._)("div",{class:"icon"},[(0,a._)("i",{class:"fas fa-temperature-half"})],-1)})),C={class:"input"};function M(e,t,n,o,M,T){var Z=(0,a.up)("EntityIcon"),I=(0,a.up)("ToggleSwitch"),R=(0,a.up)("Slider");return(0,a.wg)(),(0,a.iD)("div",l,[(0,a._)("div",{class:(0,r.C_)(["head",{expanded:M.expanded}])},[(0,a._)("div",u,[(0,a.Wm)(Z,{icon:T.icon,hasColorFill:!0,loading:e.loading,error:e.error},null,8,["icon","loading","error"])]),(0,a._)("div",s,[(0,a._)("div",{class:"name",textContent:(0,r.zw)(e.value.name)},null,8,c)]),(0,a._)("div",p,[(0,a.Wm)(I,{value:e.value.on,onInput:T.toggle,onClick:t[0]||(t[0]=(0,i.iM)((function(){}),["stop"])),disabled:e.loading||e.value.is_read_only},null,8,["value","onInput","disabled"]),(0,a._)("button",{onClick:t[1]||(t[1]=(0,i.iM)((function(e){return M.expanded=!M.expanded}),["stop"]))},[(0,a._)("i",{class:(0,r.C_)(["fas",{"fa-angle-up":M.expanded,"fa-angle-down":!M.expanded}])},null,2)])])],2),M.expanded?((0,a.wg)(),(0,a.iD)("div",{key:0,class:"body",onClick:t[6]||(t[6]=(0,i.iM)((function(){return T.prevent&&T.prevent.apply(T,arguments)}),["stop"]))},[T.cssColor?((0,a.wg)(),(0,a.iD)("div",h,[d,(0,a._)("div",v,[(0,a._)("input",{type:"color",value:T.cssColor,onChange:t[2]||(t[2]=function(e){return T.setLight({color:e.target.value})})},null,40,g)])])):(0,a.kq)("",!0),e.value.brightness?((0,a.wg)(),(0,a.iD)("div",f,[b,(0,a._)("div",m,[(0,a.Wm)(R,{range:[e.value.brightness_min,e.value.brightness_max],value:e.value.brightness,onInput:t[3]||(t[3]=function(e){return T.setLight({brightness:e.target.value})})},null,8,["range","value"])])])):(0,a.kq)("",!0),e.value.saturation?((0,a.wg)(),(0,a.iD)("div",y,[_,(0,a._)("div",w,[(0,a.Wm)(R,{range:[e.value.saturation_min,e.value.saturation_max],value:e.value.saturation,onInput:t[4]||(t[4]=function(e){return T.setLight({saturation:e.target.value})})},null,8,["range","value"])])])):(0,a.kq)("",!0),e.value.temperature?((0,a.wg)(),(0,a.iD)("div",x,[k,(0,a._)("div",C,[(0,a.Wm)(R,{range:[e.value.temperature_min,e.value.temperature_max],value:e.value.temperature,onInput:t[5]||(t[5]=function(e){return T.setLight({temperature:e.target.value})})},null,8,["range","value"])])])):(0,a.kq)("",!0)])):(0,a.kq)("",!0)])}var T=n(6084),Z=n(9584),I=n(8534),R=n(4648),U=(n(5666),n(8070)),F=n(6),D=n(7909),N=n(3499),B=n(634),L={name:"Light",components:{ToggleSwitch:F.Z,Slider:U.Z,EntityIcon:N["default"]},mixins:[D["default"]],data:function(){return{expanded:!1,colorConverter:null}},computed:{rgbColor:function(){var e,t;return null!==(e=this.value.meta)&&void 0!==e&&null!==(t=e.icon)&&void 0!==t&&t.color?this.value.meta.icon.color:this.colorConverter&&(null!=this.value.hue||null!=this.value.x&&null!=this.value.y)?this.value.x&&this.value.y?this.colorConverter.xyToRgb(this.value.x,this.value.y,this.value.brightness):this.colorConverter.hslToRgb(this.value.hue,this.value.saturation,this.value.brightness):void 0},cssColor:function(){var e=this.rgbColor;return e?this.colorConverter.rgbToHex(e):null},icon:function(){var e,t=(0,R.Z)({},(null===(e=this.value.meta)||void 0===e?void 0:e.icon)||{});return!t.color&&this.cssColor&&(t.color=this.cssColor),t}},methods:{prevent:function(e){return e.stopPropagation(),!1},toggle:function(e){var t=this;return(0,I.Z)(regeneratorRuntime.mark((function n(){return regeneratorRuntime.wrap((function(n){while(1)switch(n.prev=n.next){case 0:return e.stopPropagation(),t.$emit("loading",!0),n.prev=2,n.next=5,t.request("entities.execute",{id:t.value.id,action:"toggle"});case 5:return n.prev=5,t.$emit("loading",!1),n.finish(5);case 8:case"end":return n.stop()}}),n,null,[[2,,5,8]])})))()},setLight:function(e){var t=this;return(0,I.Z)(regeneratorRuntime.mark((function n(){var a,r,i,o,l;return regeneratorRuntime.wrap((function(n){while(1)switch(n.prev=n.next){case 0:e.color&&(a=t.colorConverter.hexToRgb(e.color),null!=t.value.x&&null!=t.value.y?(e.xy=(r=t.colorConverter).rgbToXY.apply(r,(0,Z.Z)(a)),delete e.color):null!=t.value.hue&&(o=(i=t.colorConverter).rgbToHsl.apply(i,(0,Z.Z)(a)),l=(0,T.Z)(o,3),e.hue=l[0],e.saturation=l[1],e.brightness=l[2],delete e.color)),t.execute({type:"request",action:t.value.plugin+".set_lights",args:(0,R.Z)({lights:[t.value.external_id]},e)});case 2:case"end":return n.stop()}}),n)})))()}},mounted:function(){var e={};this.value.hue&&(e.hue=[this.value.hue_min,this.value.hue_max]),this.value.saturation&&(e.sat=[this.value.saturation_min,this.value.saturation_max]),this.value.brightness&&(e.bri=[this.value.brightness_min,this.value.brightness_max]),this.value.temperature&&(e.ct=[this.value.temperature_min,this.value.temperature_max]),this.colorConverter=new B.N(e)}},S=n(3744);const $=(0,S.Z)(L,[["render",M],["__scopeId","data-v-18a5dc7b"]]);var q=$},3540:function(e,t,n){e.exports=n.p+"static/img/spinner.c0bee445.gif"}}]);
//# sourceMappingURL=1155-legacy.3b386edd.js.map