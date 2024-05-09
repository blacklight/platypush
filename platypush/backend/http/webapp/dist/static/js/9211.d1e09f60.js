"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[9211],{9211:function(t,e,i){i.r(e),i.d(e,{default:function(){return U}});var n=i(6252),a=i(3577);const o={class:"weather"},r={key:1},s=["src","alt","width","height"],h={key:2,class:"temperature"},l=["textContent"];function c(t,e,i,c,u,d){const g=(0,n.up)("Loading"),p=(0,n.up)("skycons");return(0,n.wg)(),(0,n.iD)("div",o,[t.loading?((0,n.wg)(),(0,n.j4)(g,{key:0})):((0,n.wg)(),(0,n.iD)("h1",r,[d._showIcon&&t.weatherIcon&&"weather.darksky"===t.weatherPlugin?((0,n.wg)(),(0,n.j4)(p,{key:0,condition:t.weatherIcon,paused:!i.animate,size:i.iconSize,color:i.iconColor},null,8,["condition","paused","size","color"])):d._showIcon&&t.weatherIcon&&"weather.openweathermap"===t.weatherPlugin?((0,n.wg)(),(0,n.iD)("img",{key:1,src:`/icons/openweathermap/${i.iconColor||"dark"}/${t.weatherIcon}.png`,alt:t.weather?.summary,width:1.5*i.iconSize,height:1.5*i.iconSize,class:"owm-icon"},null,8,s)):(0,n.kq)("",!0),d._showTemperature&&t.weather?((0,n.wg)(),(0,n.iD)("span",h,(0,a.zw)(Math.round(parseFloat(t.weather.temperature))+"°"),1)):(0,n.kq)("",!0)])),d._showSummary&&t.weather&&t.weather.summary?((0,n.wg)(),(0,n.iD)("div",{key:2,class:"summary",textContent:(0,a.zw)(t.weather.summary)},null,8,l)):(0,n.kq)("",!0)])}var u=i(8637);const d=["width","height","data-condition"];function g(t,e,i,a,o,r){return(0,n.wg)(),(0,n.iD)("canvas",{width:t.width,height:t.height,"data-condition":t.condition},null,8,d)}let p,m;{const t=i.g.requestAnimationFrame||i.g.webkitRequestAnimationFrame||i.g.mozRequestAnimationFrame||i.g.oRequestAnimationFrame||i.g.msRequestAnimationFrame,e=i.g.cancelAnimationFrame||i.g.webkitCancelAnimationFrame||i.g.mozCancelAnimationFrame||i.g.oCancelAnimationFrame||i.g.msCancelAnimationFrame;t&&e?(p=function(e){var i={value:null};function n(){i.value=t(n),e()}return n(),i},m=function(t){e(t.value)}):(p=setInterval,m=clearInterval)}let w=500,f=.08,v=2*Math.PI,y=2/Math.sqrt(2);function M(t,e,i,n){t.beginPath(),t.arc(e,i,n,0,v,!1),t.fill()}function C(t,e,i,n,a){t.beginPath(),t.moveTo(e,i),t.lineTo(n,a),t.stroke()}function k(t,e,i,n,a,o,r,s){var h=Math.cos(e*v),l=Math.sin(e*v);s-=r,M(t,i-l*a,n+h*o+.5*s,r+(1-.5*h)*s)}function b(t,e,i,n,a,o,r,s){var h;for(h=5;h--;)k(t,e+h/5,i,n,a,o,r,s)}function I(t,e,i,n,a,o,r){e/=3e4;var s=.21*a,h=.12*a,l=.24*a,c=.28*a;t.fillStyle=r,b(t,e,i,n,s,h,l,c),t.globalCompositeOperation="destination-out",b(t,e,i,n,s,h,l-o,c-o),t.globalCompositeOperation="source-over"}function S(t,e,i,n,a,o,r){e/=12e4;var s,h,l,c,u=.25*a-.5*o,d=.32*a+.5*o,g=.5*a-.5*o;for(t.strokeStyle=r,t.lineWidth=o,t.lineCap="round",t.lineJoin="round",t.beginPath(),t.arc(i,n,u,0,v,!1),t.stroke(),s=8;s--;)h=(e+s/8)*v,l=Math.cos(h),c=Math.sin(h),C(t,i+l*d,n+c*d,i+l*g,n+c*g)}function P(t,e,i,n,a,o,r){e/=15e3;var s=.29*a-.5*o,h=.05*a,l=Math.cos(e*v),c=l*v/-16;t.strokeStyle=r,t.lineWidth=o,t.lineCap="round",t.lineJoin="round",i+=l*h,t.beginPath(),t.arc(i,n,s,c+v/8,c+7*v/8,!1),t.arc(i+Math.cos(c)*s*y,n+Math.sin(c)*s*y,s,c+5*v/8,c+3*v/8,!0),t.closePath(),t.stroke()}function _(t,e,i,n,a,o,r){e/=1350;var s,h,l,c,u=.16*a,d=11*v/12,g=7*v/12;for(t.fillStyle=r,s=4;s--;)h=(e+s/4)%1,l=i+(s-1.5)/1.5*(1===s||2===s?-1:1)*u,c=n+h*h*a,t.beginPath(),t.moveTo(l,c-1.5*o),t.arc(l,c,.75*o,d,g,!1),t.fill()}function T(t,e,i,n,a,o,r){e/=750;var s,h,l,c,u=.1875*a;for(t.strokeStyle=r,t.lineWidth=.5*o,t.lineCap="round",t.lineJoin="round",s=4;s--;)h=(e+s/4)%1,l=Math.floor(i+(s-1.5)/1.5*(1===s||2===s?-1:1)*u)+.5,c=n+h*a,C(t,l,c-1.5*o,l,c+1.5*o)}function q(t,e,i,n,a,o,r){e/=3e3;var s,h,l,c,u=.16*a,d=.75*o,g=e*v*.7,p=Math.cos(g)*d,m=Math.sin(g)*d,w=g+v/3,f=Math.cos(w)*d,y=Math.sin(w)*d,M=g+2*v/3,k=Math.cos(M)*d,b=Math.sin(M)*d;for(t.strokeStyle=r,t.lineWidth=.5*o,t.lineCap="round",t.lineJoin="round",s=4;s--;)h=(e+s/4)%1,l=i+Math.sin((h+s/4)*v)*u,c=n+h*a,C(t,l-p,c-m,l+p,c+m),C(t,l-f,c-y,l+f,c+y),C(t,l-k,c-b,l+k,c+b)}function z(t,e,i,n,a,o,r){e/=3e4;var s=.21*a,h=.06*a,l=.21*a,c=.28*a;t.fillStyle=r,b(t,e,i,n,s,h,l,c),t.globalCompositeOperation="destination-out",b(t,e,i,n,s,h,l-o,c-o),t.globalCompositeOperation="source-over"}var A=[[-.75,-.18,-.7219,-.1527,-.6971,-.1225,-.6739,-.091,-.6516,-.0588,-.6298,-.0262,-.6083,.0065,-.5868,.0396,-.5643,.0731,-.5372,.1041,-.5033,.1259,-.4662,.1406,-.4275,.1493,-.3881,.153,-.3487,.1526,-.3095,.1488,-.2708,.1421,-.2319,.1342,-.1943,.1217,-.16,.1025,-.129,.0785,-.1012,.0509,-.0764,.0206,-.0547,-.012,-.0378,-.0472,-.0324,-.0857,-.0389,-.1241,-.0546,-.1599,-.0814,-.1876,-.1193,-.1964,-.1582,-.1935,-.1931,-.1769,-.2157,-.1453,-.229,-.1085,-.2327,-.0697,-.224,-.0317,-.2064,.0033,-.1853,.0362,-.1613,.0672,-.135,.0961,-.1051,.1213,-.0706,.1397,-.0332,.1512,.0053,.158,.0442,.1624,.0833,.1636,.1224,.1615,.1613,.1565,.1999,.15,.2378,.1402,.2749,.1279,.3118,.1147,.3487,.1015,.3858,.0892,.4236,.0787,.4621,.0715,.5012,.0702,.5398,.0766,.5768,.089,.6123,.1055,.6466,.1244,.6805,.144,.7147,.163,.75,.18],[-.75,0,-.7033,.0195,-.6569,.0399,-.6104,.06,-.5634,.0789,-.5155,.0954,-.4667,.1089,-.4174,.1206,-.3676,.1299,-.3174,.1365,-.2669,.1398,-.2162,.1391,-.1658,.1347,-.1157,.1271,-.0661,.1169,-.017,.1046,.0316,.0903,.0791,.0728,.1259,.0534,.1723,.0331,.2188,.0129,.2656,-.0064,.3122,-.0263,.3586,-.0466,.4052,-.0665,.4525,-.0847,.5007,-.1002,.5497,-.113,.5991,-.124,.6491,-.1325,.6994,-.138,.75,-.14]],D=[{start:.36,end:.11},{start:.56,end:.16}];function F(t,e,i,n,a,o,r){var s=a/8,h=s/3,l=2*h,c=e%1*v,u=Math.cos(c),d=Math.sin(c);t.fillStyle=r,t.strokeStyle=r,t.lineWidth=o,t.lineCap="round",t.lineJoin="round",t.beginPath(),t.arc(i,n,s,c,c+Math.PI,!1),t.arc(i-h*u,n-h*d,l,c+Math.PI,c,!1),t.arc(i+l*u,n+l*d,h,c+Math.PI,c,!0),t.globalCompositeOperation="destination-out",t.fill(),t.globalCompositeOperation="source-over",t.stroke()}function W(t,e,i,n,a,o,r,s,h){e/=2500;var l,c,u,d,g=A[r],p=(e+r-D[r].start)%s,m=(e+r-D[r].end)%s,w=(e+r)%s;if(t.strokeStyle=h,t.lineWidth=o,t.lineCap="round",t.lineJoin="round",p<1){if(t.beginPath(),p*=g.length/2-1,l=Math.floor(p),p-=l,l*=2,l+=2,t.moveTo(i+(g[l-2]*(1-p)+g[l]*p)*a,n+(g[l-1]*(1-p)+g[l+1]*p)*a),m<1){for(m*=g.length/2-1,c=Math.floor(m),m-=c,c*=2,c+=2,d=l;d!==c;d+=2)t.lineTo(i+g[d]*a,n+g[d+1]*a);t.lineTo(i+(g[c-2]*(1-m)+g[c]*m)*a,n+(g[c-1]*(1-m)+g[c+1]*m)*a)}else for(d=l;d!==g.length;d+=2)t.lineTo(i+g[d]*a,n+g[d+1]*a);t.stroke()}else if(m<1){for(t.beginPath(),m*=g.length/2-1,c=Math.floor(m),m-=c,c*=2,c+=2,t.moveTo(i+g[0]*a,n+g[1]*a),d=2;d!==c;d+=2)t.lineTo(i+g[d]*a,n+g[d+1]*a);t.lineTo(i+(g[c-2]*(1-m)+g[c]*m)*a,n+(g[c-1]*(1-m)+g[c+1]*m)*a),t.stroke()}w<1&&(w*=g.length/2-1,u=Math.floor(w),w-=u,u*=2,u+=2,F(t,e,i+(g[u-2]*(1-w)+g[u]*w)*a,n+(g[u-1]*(1-w)+g[u+1]*w)*a,a,o,h))}class N{constructor(t){this.list=[],this.interval=null,this.color=t&&t.color?t.color:"black",this.resizeClear=!(!t||!t.resizeClear),this.speed=Number(t&&t.speed)||1,this.speed<0&&(this.speed=1)}static CLEAR_DAY(t,e,i){const n=t.canvas.width,a=t.canvas.height,o=Math.min(n,a);S(t,e,.5*n,.5*a,o,o*f,i)}static CLEAR_NIGHT(t,e,i){const n=t.canvas.width,a=t.canvas.height,o=Math.min(n,a);P(t,e,.5*n,.5*a,o,o*f,i)}static PARTLY_CLOUDY_DAY(t,e,i){const n=t.canvas.width,a=t.canvas.height,o=Math.min(n,a);S(t,e,.625*n,.375*a,.75*o,o*f,i),I(t,e,.375*n,.625*a,.75*o,o*f,i)}static PARTLY_CLOUDY_NIGHT(t,e,i){const n=t.canvas.width,a=t.canvas.height,o=Math.min(n,a);P(t,e,.667*n,.375*a,.75*o,o*f,i),I(t,e,.375*n,.625*a,.75*o,o*f,i)}static CLOUDY(t,e,i){const n=t.canvas.width,a=t.canvas.height,o=Math.min(n,a);I(t,e,.5*n,.5*a,o,o*f,i)}static RAIN(t,e,i){const n=t.canvas.width,a=t.canvas.height,o=Math.min(n,a);_(t,e,.5*n,.37*a,.9*o,o*f,i),I(t,e,.5*n,.37*a,.9*o,o*f,i)}static SLEET(t,e,i){const n=t.canvas.width,a=t.canvas.height,o=Math.min(n,a);T(t,e,.5*n,.37*a,.9*o,o*f,i),I(t,e,.5*n,.37*a,.9*o,o*f,i)}static SNOW(t,e,i){const n=t.canvas.width,a=t.canvas.height,o=Math.min(n,a);q(t,e,.5*n,.37*a,.9*o,o*f,i),I(t,e,.5*n,.37*a,.9*o,o*f,i)}static WIND(t,e,i){const n=t.canvas.width,a=t.canvas.height,o=Math.min(n,a);W(t,e,.5*n,.5*a,o,o*f,0,2,i),W(t,e,.5*n,.5*a,o,o*f,1,2,i)}static FOG(t,e,i){const n=t.canvas.width,a=t.canvas.height,o=Math.min(n,a),r=o*f;z(t,e,.5*n,.32*a,.75*o,r,i),e/=5e3;const s=Math.cos(e*v)*o*.02,h=Math.cos((e+.25)*v)*o*.02,l=Math.cos((e+.5)*v)*o*.02,c=Math.cos((e+.75)*v)*o*.02,u=.936*a,d=Math.floor(u-.5*r)+.5,g=Math.floor(u-2.5*r)+.5;t.strokeStyle=i,t.lineWidth=r,t.lineCap="round",t.lineJoin="round",C(t,s+.2*n+.5*r,d,h+.8*n-.5*r,d),C(t,l+.2*n+.5*r,g,c+.8*n-.5*r,g)}#t=t=>("string"===typeof t&&(t=N[t.toUpperCase().replace(/-/g,"_")]||null),t);add(t,e){if("string"===typeof t&&(t=document.getElementById(t)),null===t||void 0===t)return;if(e=this.#t(e),"function"!==typeof e)return;const i={element:t,context:t.getContext("2d"),drawing:e};this.list.push(i),this.draw(i,w)}set(t,e){"string"===typeof t&&(t=document.getElementById(t));for(let i=this.list.length;i--;)if(this.list[i].element===t)return this.list[i].drawing=this.#t(e),void this.draw(this.list[i],w);this.add(t,e)}remove(t){"string"===typeof t&&(t=document.getElementById(t));for(let e=this.list.length;e--;)if(this.list[e].element===t)return void this.list.splice(e,1)}draw(t,e){const i=t.context.canvas;this.resizeClear?i.width=i.width:t.context.clearRect(0,0,i.width,i.height),t.drawing(t.context,e,this.color)}play(){this.pause(),this.interval=p((()=>{const t=Date.now()*this.speed;for(let e=this.list.length;e--;)this.draw(this.list[e],t)}),1e3/60)}pause(){this.interval&&(m(this.interval),this.interval=null)}}function O(t){const e={};return e.paused=!t.interval,e.play=()=>{t.play(),e.paused=!1},e.pause=()=>{t.pause(),e.paused=!0},e}var L=(0,n.aZ)({props:{condition:{type:String,required:!0},size:{type:[Number,String],default:64},color:{type:String,default:"black"},paused:{type:Boolean,default:!1},speed:{type:[Number,String],default:1}},computed:{width(){return""+this.size},height(){return""+this.size},icon(){return this.condition.toUpperCase().replace(/[\s.-]/g,"_")}},mounted(){const t=new N({color:this.color,speed:this.speed});t.set(this.$el,N[this.icon]),this.paused||t.play(),this.$emit("load",O(t))}}),R=i(3744);const x=(0,R.Z)(L,[["render",g]]);var E=x,$=E,B=i(6791),J={name:"Weather",mixins:[u.Z],components:{Loading:B.Z,Skycons:$},props:{animate:{required:!1,default:!0},iconSize:{type:Number,required:!1,default:50},iconColor:{type:String,required:!1},showIcon:{required:!1,default:!0},showSummary:{required:!1,default:!0},showTemperature:{required:!1,default:!0},refreshSeconds:{type:Number,required:!1,default:900}},data:function(){return{weather:void 0,weatherIcon:void 0,weatherPlugin:void 0,loading:!1,weatherPlugins:["weather.openweathermap","weather.darksky"]}},computed:{_showSummary(){return this.parseBoolean(this.showSummary)},_showIcon(){return this.parseBoolean(this.showIcon)},_showTemperature(){return this.parseBoolean(this.showTemperature)}},methods:{async refresh(){this.loading=!0;try{const t=await this.request(`${this.weatherPlugin}.get_current_weather`);this.onWeatherChange(t)}finally{this.loading=!1}},onWeatherChange(t){this.weather&&t&&this.weatherPlugins.includes(t.plugin_name)||(this.weather={}),this.weather={...this.weather,...t},this.weatherIcon=this.weather.icon},initWeatherPlugin(){for(const t of this.weatherPlugins)if(this.$root.config[t]){this.weatherPlugin=t,console.debug(`Initialized weather UI - plugin: ${t}`);break}this.weatherPlugin||console.warn(`No weather plugins configured. Compatible plugins: ${this.weatherPlugins}`)}},mounted:function(){this.initWeatherPlugin(),this.refresh(),this.subscribe(this.onWeatherChange,null,"platypush.message.event.weather.NewWeatherConditionEvent"),setInterval(this.refresh,parseInt((1e3*this.refreshSeconds).toFixed(0)))}};const Y=(0,R.Z)(J,[["render",c],["__scopeId","data-v-e45afcf6"]]);var U=Y}}]);
//# sourceMappingURL=9211.d1e09f60.js.map