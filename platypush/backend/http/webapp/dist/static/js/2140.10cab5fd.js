"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[2140,4619],{4619:function(e,t,s){s.r(t),s.d(t,{default:function(){return w}});var o=s(6252),i=s(3577);const a={class:"date-time"},r=["textContent"],h=["textContent"];function n(e,t,s,n,m,u){return(0,o.wg)(),(0,o.iD)("div",a,[u._showDate?((0,o.wg)(),(0,o.iD)("div",{key:0,class:"date",textContent:(0,i.zw)(e.formatDate(e.now))},null,8,r)):(0,o.kq)("",!0),u._showTime?((0,o.wg)(),(0,o.iD)("div",{key:1,class:"time",textContent:(0,i.zw)(e.formatTime(e.now,u._showSeconds))},null,8,h)):(0,o.kq)("",!0)])}var m=s(8637),u={name:"DateTime",mixins:[m.Z],props:{showDate:{required:!1,default:!0},showTime:{required:!1,default:!0},showSeconds:{required:!1,default:!0}},computed:{_showTime(){return this.parseBoolean(this.showTime)},_showDate(){return this.parseBoolean(this.showDate)},_showSeconds(){return this.parseBoolean(this.showSeconds)}},data:function(){return{now:new Date}},methods:{refreshTime(){this.now=new Date}},mounted:function(){this.refreshTime(),setInterval(this.refreshTime,1e3)}},c=s(3744);const l=(0,c.Z)(u,[["render",n],["__scopeId","data-v-ca42eb9c"]]);var w=l},2140:function(e,t,s){s.r(t),s.d(t,{default:function(){return k}});var o=s(6252),i=s(3577);const a={class:"image-carousel"},r={ref:"background",class:"background"},h=["src"],n={key:1,class:"row info-container"},m={class:"col-6 weather-container"},u={key:0},c={class:"col-6 date-time-container"};function l(e,t,s,l,w,d){const g=(0,o.up)("Loading"),f=(0,o.up)("Weather"),p=(0,o.up)("DateTime");return(0,o.wg)(),(0,o.iD)("div",a,[w.images.length?(0,o.kq)("",!0):((0,o.wg)(),(0,o.j4)(g,{key:0})),(0,o._)("div",r,null,512),(0,o._)("img",{ref:"img",src:d.imgURL,alt:"Your carousel images",style:(0,i.j5)({display:w.images.length?"block":"none"})},null,12,h),d._showDate||d._showTime?((0,o.wg)(),(0,o.iD)("div",n,[(0,o._)("div",m,[d._showWeather?((0,o.wg)(),(0,o.j4)(f,{key:1,"show-icon":d._showWeatherIcon,"show-summary":d._showWeatherSummary,"show-temperature":d._showTemperature,"icon-color":s.weatherIconColor,"icon-size":s.weatherIconSize,animate:d._animateWeatherIcon},null,8,["show-icon","show-summary","show-temperature","icon-color","icon-size","animate"])):((0,o.wg)(),(0,o.iD)("span",u," "))]),(0,o._)("div",c,[d._showTime||d._showDate?((0,o.wg)(),(0,o.j4)(p,{key:0,"show-date":d._showDate,"show-time":d._showTime,"show-seconds":d._showSeconds},null,8,["show-date","show-time","show-seconds"])):(0,o.kq)("",!0)])])):(0,o.kq)("",!0)])}var w=s(8637),d=s(6791),g=s(4619),f=s(9211),p={name:"ImageCarousel",components:{Weather:f["default"],DateTime:g["default"],Loading:d.Z},mixins:[w.Z],props:{imgDir:{type:String,required:!0},refreshSeconds:{type:Number,default:15},showDate:{default:!1},showTime:{default:!1},showSeconds:{default:!1},showWeather:{default:!1},showTemperature:{default:!0},showWeatherIcon:{default:!0},showWeatherSummary:{default:!0},weatherIconColor:{type:String,default:"white"},weatherIconSize:{type:Number,default:70},animateWeatherIcon:{default:!0}},data(){return{images:[],currentImage:void 0,loading:!1}},computed:{imgURL(){let e=8008;return"backend.http"in this.$root.config&&"port"in this.$root.config["backend.http"]&&(e=this.$root.config["backend.http"].port),"//"+window.location.hostname+":"+e+this.currentImage},_showDate(){return this.parseBoolean(this.showDate)},_showTime(){return this.parseBoolean(this.showTime)},_showSeconds(){return this.parseBoolean(this.showSeconds)},_showTemperature(){return this.parseBoolean(this.showTemperature)},_showWeather(){return this.parseBoolean(this.showWeather)},_showWeatherIcon(){return this.parseBoolean(this.showWeatherIcon)},_showWeatherSummary(){return this.parseBoolean(this.showWeatherSummary)},_animateWeatherIcon(){return this.parseBoolean(this.animateWeatherIcon)}},methods:{async refresh(){if(!this.images.length){this.loading=!0;try{this.images=await this.request("utils.search_web_directory",{directory:this.imgDir,extensions:[".jpg",".jpeg",".png"]}),this.shuffleImages()}finally{this.loading=!1}}this.images.length&&(this.currentImage=this.images.pop())},onNewImage(){if(this.$refs.img&&(this.$refs.background.style["background-image"]="url("+this.imgURL+")",this.$refs.img.style.width="auto",this.$refs.img.width>this.$refs.img.height)){const e=this.$refs.img.width/this.$refs.img.height;e>=4/3&&e<=16/9?this.$refs.img.style.width="100%":e<=4/3&&(this.$refs.img.style.height="100%")}},shuffleImages(){for(let e=this.images.length-1;e>0;e--){let t=Math.floor(Math.random()*(e+1)),s=this.images[e];this.images[e]=this.images[t],this.images[t]=s}}},mounted(){this.$refs.img.addEventListener("load",this.onNewImage),this.$refs.img.addEventListener("error",this.refresh),this.refresh(),setInterval(this.refresh,Math.round(1e3*this.refreshSeconds))}},_=s(3744);const y=(0,_.Z)(p,[["render",l],["__scopeId","data-v-7b09a273"]]);var k=y}}]);
//# sourceMappingURL=2140.10cab5fd.js.map