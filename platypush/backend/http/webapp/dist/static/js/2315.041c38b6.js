"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[2315,3459],{4212:function(e,t,l){l.d(t,{N:function(){return a}});class a{constructor(e){if(this.ranges={hue:[0,360],sat:[0,100],bri:[0,100],ct:[154,500]},e)for(const t of Object.keys(this.ranges))e[t]&&(this.ranges[t]=e[t])}normalize(e,t,l){return l[0]+(e-t[0])*(l[1]-l[0])/(t[1]-t[0])}hslToRgb(e,t,l){[e,t,l]=[this.normalize(e,this.ranges.hue,[0,360]),this.normalize(t,this.ranges.sat,[0,100]),this.normalize(l,this.ranges.bri,[0,100])],l/=100;const a=t*Math.min(l,1-l)/100,s=t=>{const s=(t+e/30)%12,n=l-a*Math.max(Math.min(s-3,9-s,1),-1);return Math.round(255*n)};return[s(0),s(8),s(4)]}rgbToHsl(e,t,l){e/=255,t/=255,l/=255;const a=Math.max(e,t,l),s=Math.min(e,t,l);let n,i,r=(a+s)/2;if(a===s)n=i=0;else{const o=a-s;switch(i=r>.5?o/(2-a-s):o/(a+s),a){case e:n=(t-l)/o+(t<l?6:0);break;case t:n=(l-e)/o+2;break;case l:n=(e-t)/o+4;break}n/=6}return[parseInt(this.normalize(n,[0,1],this.ranges.hue)),parseInt(this.normalize(i,[0,1],this.ranges.sat)),parseInt(this.normalize(r,[0,1],this.ranges.bri))]}xyToRgb(e,t,l){null==l&&(l=this.ranges.bri[1]);const a=1-e-t,s=(l/(this.ranges.bri[1]-1)).toFixed(2),n=s/t*e,i=s/t*a;let r=1.656492*n-.354851*s-.255038*i,o=.707196*-n+1.655397*s+.036152*i,u=.051713*n-.121364*s+1.01153*i;return r>u&&r>o&&r>1?(o/=r,u/=r,r=1):o>u&&o>r&&o>1?(r/=o,u/=o,o=1):u>r&&u>o&&u>1&&(r/=u,o/=u,u=1),r=r<=.0031308?12.92*r:1.055*Math.pow(r,1/2.4)-.055,o=o<=.0031308?12.92*o:1.055*Math.pow(o,1/2.4)-.055,u=u<=.0031308?12.92*u:1.055*Math.pow(u,1/2.4)-.055,r=Math.round(255*r),o=Math.round(255*o),u=Math.round(255*u),isNaN(r)&&(r=0),isNaN(o)&&(o=0),isNaN(u)&&(u=0),[r,o,u].map((e=>Math.min(Math.max(0,e),255)))}rgbToXY(e,t,l){e>1&&(e/=255),t>1&&(t/=255),l>1&&(l/=255),e=e>.04045?Math.pow((e+.055)/1.055,2.4):e/12.92,t=t>.04045?Math.pow((t+.055)/1.055,2.4):t/12.92,l=l>.04045?Math.pow((l+.055)/1.055,2.4):l/12.92;const a=.664511*e+.154324*t+.162028*l,s=.283881*e+.668433*t+.047685*l,n=88e-6*e+.07231*t+.986039*l;let i=parseFloat((a/(a+s+n)).toFixed(4)),r=parseFloat((s/(a+s+n)).toFixed(4));return isNaN(i)&&(i=0),isNaN(r)&&(r=0),[i,r]}rgbToBri(e,t,l){return Math.min(2*this.rgbToHsl(e,t,l)[2],this.ranges.bri[1])}getRGB(e){return null!=e.red&&null!=e.green&&null!=e.blue?[e.red,e.green,e.blue]:null!=e.r&&null!=e.g&&null!=e.b?[e.r,e.g,e.b]:e.rgb?e.rgb:void 0}getXY(e){return null!=e.x&&null!=e.y?[e.x,e.y]:e.xy?e.xy:void 0}toRGB(e){const t=this.getRGB(e);if(t)return t;const l=this.getXY(e);return l&&e.bri?this.xyToRgb(...l,e.bri):e.hue&&e.sat&&e.bri?this.hslToRgb(e.hue,e.sat,e.bri):(console.debug("Could not determine color space"),void console.debug(e))}toXY(e){const t=this.getXY(e);if(t&&e.bri)return[t[0],t[1],e.bri];const l=this.getRGB(e);if(l)return this.rgbToXY(...l);if(e.hue&&e.sat&&e.bri){const t=this.hslToRgb(e.hue,e.sat,e.bri);return this.rgbToXY(...t)}console.debug("Could not determine color space"),console.debug(e)}toHSL(e){if(e.hue&&e.sat&&e.bri)return[e.hue,e.sat,e.bri];const t=this.getRGB(e);if(t)return this.rgbToHsl(...t);const l=this.getXY(e);if(l&&e.bri){const t=this.xyToRgb(...l,e.bri);return this.rgbToHsl(...t)}console.debug("Could not determine color space"),console.debug(e)}hexToRgb(e){return[e.slice(1,3),e.slice(3,5),e.slice(5,7)].map((e=>parseInt(e,16)))}rgbToHex(e){return"#"+e.map((e=>{let t=e.toString(16);return t.length<2&&(t="0"+t),t})).join("")}}},1583:function(e,t,l){l.d(t,{Z:function(){return f}});var a=l(6252),s=l(3577),n=l(9963);const i={class:"slider-wrapper"},r=["textContent"],o=["textContent"],u={class:"slider-container"},c=["min","max","step","disabled","value"],h={class:"track-inner",ref:"track"},d={class:"thumb",ref:"thumb"},g=["textContent"];function p(e,t,l,p,v,b){return(0,a.wg)(),(0,a.iD)("label",i,[l.withRange?((0,a.wg)(),(0,a.iD)("span",{key:0,class:(0,s.C_)(["range-labels",{"with-label":l.withLabel}])},[l.withRange?((0,a.wg)(),(0,a.iD)("span",{key:0,class:"label left",textContent:(0,s.zw)(l.range[0])},null,8,r)):(0,a.kq)("",!0),l.withRange?((0,a.wg)(),(0,a.iD)("span",{key:1,class:"label right",textContent:(0,s.zw)(l.range[1])},null,8,o)):(0,a.kq)("",!0)],2)):(0,a.kq)("",!0),(0,a._)("span",u,[(0,a._)("input",{class:(0,s.C_)(["slider",{"with-label":l.withLabel}]),type:"range",min:l.range[0],max:l.range[1],step:l.step,disabled:l.disabled,value:l.value,ref:"range",onInput:t[0]||(t[0]=(0,n.iM)(((...e)=>b.onUpdate&&b.onUpdate(...e)),["stop"])),onChange:t[1]||(t[1]=(0,n.iM)(((...e)=>b.onUpdate&&b.onUpdate(...e)),["stop"]))},null,42,c),(0,a._)("div",{class:(0,s.C_)(["track",{"with-label":l.withLabel}])},[(0,a._)("div",h,null,512)],2),(0,a._)("div",d,null,512),l.withLabel?((0,a.wg)(),(0,a.iD)("span",{key:0,class:"label",textContent:(0,s.zw)(l.value),ref:"label"},null,8,g)):(0,a.kq)("",!0)])])}var v={name:"Slider",emits:["input","change","mouseup","mousedown","touchstart","touchend","keyup","keydown"],props:{value:{type:Number},disabled:{type:Boolean,default:!1},range:{type:Array,default:()=>[0,100]},step:{type:Number,default:1},withLabel:{type:Boolean,default:!1},withRange:{type:Boolean,default:!1}},methods:{onUpdate(e){this.update(e.target.value),this.$emit(e.type,{...e,target:{...e.target,value:this.$refs.range.value}})},update(e){const t=this.$refs.range.clientWidth,l=(e-this.range[0])/(this.range[1]-this.range[0]),a=l*t,s=this.$refs.thumb;s.style.left=a-s.clientWidth/2+"px",this.$refs.thumb.style.transform=`translate(-${l}%, -50%)`,this.$refs.track.style.width=`${a}px`}},mounted(){null!=this.value&&this.update(this.value),this.$watch((()=>this.value),(e=>this.update(e)))}},b=l(3744);const m=(0,b.Z)(v,[["render",p],["__scopeId","data-v-28d31846"]]);var f=m},6:function(e,t,l){l.d(t,{Z:function(){return p}});var a=l(6252),s=l(3577),n=l(9963);const i=e=>((0,a.dD)("data-v-a6396ae8"),e=e(),(0,a.Cn)(),e),r=["checked"],o=i((()=>(0,a._)("div",{class:"switch"},[(0,a._)("div",{class:"dot"})],-1))),u={class:"label"};function c(e,t,l,i,c,h){return(0,a.wg)(),(0,a.iD)("div",{class:(0,s.C_)(["power-switch",{disabled:l.disabled}]),onClick:t[0]||(t[0]=(0,n.iM)(((...e)=>h.onInput&&h.onInput(...e)),["stop"]))},[(0,a._)("input",{type:"checkbox",checked:l.value},null,8,r),(0,a._)("label",null,[o,(0,a._)("span",u,[(0,a.WI)(e.$slots,"default",{},void 0,!0)])])],2)}var h={name:"ToggleSwitch",emits:["input"],props:{value:{type:Boolean,default:!1},disabled:{type:Boolean,default:!1}},methods:{onInput(e){if(this.disabled)return!1;this.$emit("input",e)}}},d=l(3744);const g=(0,d.Z)(h,[["render",c],["__scopeId","data-v-a6396ae8"]]);var p=g},3459:function(e,t,l){l.r(t),l.d(t,{default:function(){return g}});var a=l(6252),s=l(3577),n=l(3540);const i={key:0,src:n,class:"loading"},r={key:1,class:"fas fa-circle-exclamation error"};function o(e,t,l,n,o,u){const c=(0,a.up)("Icon");return(0,a.wg)(),(0,a.iD)("div",{class:(0,s.C_)(["entity-icon-container",{"with-color-fill":!!u.colorFill}]),style:(0,s.j5)(u.colorFillStyle)},[l.loading?((0,a.wg)(),(0,a.iD)("img",i)):l.error?((0,a.wg)(),(0,a.iD)("i",r)):((0,a.wg)(),(0,a.j4)(c,(0,s.vs)((0,a.dG)({key:2},u.computedIconNormalized)),null,16))],6)}var u=l(1478),c={name:"EntityIcon",components:{Icon:u.Z},props:{loading:{type:Boolean,default:!1},error:{type:Boolean,default:!1},entity:{type:Object,required:!0},icon:{type:Object,default:()=>{}},hasColorFill:{type:Boolean,default:!1}},data(){return{component:null,modalVisible:!1}},computed:{computedIcon(){let e={...this.entity?.meta?.icon||{}};return Object.keys(this.icon||{}).length&&(e=this.icon),{...e}},colorFill(){return this.hasColorFill&&this.computedIcon.color},colorFillStyle(){return this.colorFill&&!this.error?{background:this.colorFill}:{}},computedIconNormalized(){const e={...this.computedIcon};return this.colorFill&&delete e.color,e},type(){let e=this.entity.type||"";return e.charAt(0).toUpperCase()+e.slice(1)}}},h=l(3744);const d=(0,h.Z)(c,[["render",o],["__scopeId","data-v-4fad24e6"]]);var g=d},2315:function(e,t,l){l.r(t),l.d(t,{default:function(){return $}});var a=l(6252),s=l(3577),n=l(9963);const i=e=>((0,a.dD)("data-v-5c39391e"),e=e(),(0,a.Cn)(),e),r={class:"entity light-container"},o={class:"col-1 icon"},u={class:"col-s-8 col-m-9 label"},c=["textContent"],h={class:"col-s-3 col-m-2 buttons pull-right"},d={key:0,class:"row"},g=i((()=>(0,a._)("div",{class:"icon"},[(0,a._)("i",{class:"fas fa-palette"})],-1))),p={class:"input"},v=["value"],b={key:1,class:"row"},m=i((()=>(0,a._)("div",{class:"icon"},[(0,a._)("i",{class:"fas fa-sun"})],-1))),f={class:"input"},y={key:2,class:"row"},_=i((()=>(0,a._)("div",{class:"icon"},[(0,a._)("i",{class:"fas fa-droplet"})],-1))),w={class:"input"},C={key:3,class:"row"},x=i((()=>(0,a._)("div",{class:"icon"},[(0,a._)("i",{class:"fas fa-temperature-half"})],-1))),k={class:"input"};function I(e,t,l,i,I,T){const M=(0,a.up)("EntityIcon"),R=(0,a.up)("ToggleSwitch"),D=(0,a.up)("Slider");return(0,a.wg)(),(0,a.iD)("div",r,[(0,a._)("div",{class:(0,s.C_)(["head",{collapsed:e.collapsed}])},[(0,a._)("div",o,[(0,a.Wm)(M,{entity:e.value,icon:T.icon,hasColorFill:!0,loading:e.loading,error:e.error},null,8,["entity","icon","loading","error"])]),(0,a._)("div",u,[(0,a._)("div",{class:"name",textContent:(0,s.zw)(e.value.name)},null,8,c)]),(0,a._)("div",h,[(0,a.Wm)(R,{value:e.value.on,onInput:T.toggle,onClick:t[0]||(t[0]=(0,n.iM)((()=>{}),["stop"])),disabled:e.loading||e.value.is_read_only},null,8,["value","onInput","disabled"]),(0,a._)("button",{onClick:t[1]||(t[1]=(0,n.iM)((t=>e.collapsed=!e.collapsed),["stop"]))},[(0,a._)("i",{class:(0,s.C_)(["fas",{"fa-angle-up":!e.collapsed,"fa-angle-down":e.collapsed}])},null,2)])])],2),e.collapsed?(0,a.kq)("",!0):((0,a.wg)(),(0,a.iD)("div",{key:0,class:"body",onClick:t[6]||(t[6]=(0,n.iM)(((...e)=>T.prevent&&T.prevent(...e)),["stop"]))},[T.cssColor?((0,a.wg)(),(0,a.iD)("div",d,[g,(0,a._)("div",p,[(0,a._)("input",{type:"color",value:T.cssColor,onChange:t[2]||(t[2]=e=>T.setLight({color:e.target.value}))},null,40,v)])])):(0,a.kq)("",!0),e.value.brightness?((0,a.wg)(),(0,a.iD)("div",b,[m,(0,a._)("div",f,[(0,a.Wm)(D,{range:[e.value.brightness_min,e.value.brightness_max],value:e.value.brightness,onInput:t[3]||(t[3]=e=>T.setLight({brightness:e.target.value}))},null,8,["range","value"])])])):(0,a.kq)("",!0),e.value.saturation?((0,a.wg)(),(0,a.iD)("div",y,[_,(0,a._)("div",w,[(0,a.Wm)(D,{range:[e.value.saturation_min,e.value.saturation_max],value:e.value.saturation,onInput:t[4]||(t[4]=e=>T.setLight({saturation:e.target.value}))},null,8,["range","value"])])])):(0,a.kq)("",!0),e.value.temperature?((0,a.wg)(),(0,a.iD)("div",C,[x,(0,a._)("div",k,[(0,a.Wm)(D,{range:[e.value.temperature_min,e.value.temperature_max],value:e.value.temperature,onInput:t[5]||(t[5]=e=>T.setLight({temperature:e.target.value}))},null,8,["range","value"])])])):(0,a.kq)("",!0)]))])}var T=l(1583),M=l(6),R=l(7909),D=l(3459),N=l(4212),F={name:"Light",components:{ToggleSwitch:M.Z,Slider:T.Z,EntityIcon:D["default"]},mixins:[R["default"]],data(){return{colorConverter:null}},computed:{rgbColor(){return this.value.meta?.icon?.color?this.value.meta.icon.color:this.value.red&&this.value.green&&this.value.blue?["red","green","blue"].map((e=>this.value[e])):this.colorConverter&&(null!=this.value.hue||null!=this.value.x&&null!=this.value.y)?this.value.x&&this.value.y?this.colorConverter.xyToRgb(this.value.x,this.value.y,this.value.brightness):this.colorConverter.hslToRgb(this.value.hue,this.value.saturation,this.value.brightness):void 0},cssColor(){const e=this.rgbColor;return e?this.colorConverter.rgbToHex(e):null},icon(){const e={...this.value.meta?.icon||{}};return!e.color&&this.cssColor&&(e.color=this.cssColor),e}},methods:{prevent(e){return e.stopPropagation(),!1},async toggle(e){e.stopPropagation(),this.$emit("loading",!0);try{await this.request("entities.execute",{id:this.value.id,action:"toggle"})}finally{this.$emit("loading",!1)}},async setLight(e){if(e.color){const t=this.colorConverter.hexToRgb(e.color);null!=this.value.x&&null!=this.value.y?e.xy=this.colorConverter.rgbToXY(...t):null!=this.value.hue?[e.hue,e.saturation,e.brightness]=this.colorConverter.rgbToHsl(...t):null!=this.value.red&&null!=this.value.green&&null!=this.value.blue?[e.red,e.green,e.blue]=[t.red,t.green,t.blue]:(console.warn("Unrecognized color format"),console.warn(e.color)),delete e.color}this.execute({type:"request",action:this.value.plugin+".set_lights",args:{lights:[this.value.external_id],...e}})}},mounted(){const e={};this.value.hue&&(e.hue=[this.value.hue_min,this.value.hue_max]),this.value.saturation&&(e.sat=[this.value.saturation_min,this.value.saturation_max]),this.value.brightness&&(e.bri=[this.value.brightness_min,this.value.brightness_max]),this.value.temperature&&(e.ct=[this.value.temperature_min,this.value.temperature_max]),this.colorConverter=new N.N(e)},unmounted(){this.colorConverter&&delete this.colorConverter}},z=l(3744);const B=(0,z.Z)(F,[["render",I],["__scopeId","data-v-5c39391e"]]);var $=B},3540:function(e,t,l){e.exports=l.p+"static/img/spinner.c0bee445.gif"}}]);
//# sourceMappingURL=2315.041c38b6.js.map