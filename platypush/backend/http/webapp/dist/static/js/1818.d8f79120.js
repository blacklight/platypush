"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[1818],{1818:function(n,t,e){e.r(t),e.d(t,{default:function(){return g}});var o=e(6252);const i={class:"plugin"};function s(n,t,e,s,a,p){const c=(0,o.up)("Loading");return(0,o.wg)(),(0,o.iD)("div",i,[a.loading?((0,o.wg)(),(0,o.j4)(c,{key:0})):a.component?((0,o.wg)(),(0,o.j4)((0,o.LL)(a.component),{key:1,config:a.config},null,8,["config"])):(0,o.kq)("",!0)])}var a=e(6813),p=e(1232),c=e(2262),u={name:"Plugin",components:{Loading:p.Z},mixins:[a.Z],props:{pluginName:{type:String,required:!0}},data(){return{loading:!1,component:null,config:{}}},computed:{componentName(){return this.pluginName.split(".").map((n=>n[0].toUpperCase()+n.slice(1))).join("")}},methods:{refresh:async function(){this.loading=!0;try{this.component=(0,c.XI)((0,o.RC)((()=>e(3379)(`./${this.componentName}/Index`)))),this.$options.components[this.componentName]=this.component,this.config=(await this.request("config.get_plugins"))?.[this.pluginName]||{}}finally{this.loading=!1}}},mounted:function(){this.refresh()}},r=e(3744);const l=(0,r.Z)(u,[["render",s],["__scopeId","data-v-69b17daa"]]);var g=l}}]);
//# sourceMappingURL=1818.d8f79120.js.map