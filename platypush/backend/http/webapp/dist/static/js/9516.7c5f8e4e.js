"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[9516],{3222:function(e,t,s){s.d(t,{Z:function(){return r}});var i=s(6252),l=s(3577);const n={class:"no-items-container"};function a(e,t,s,a,o,u){return(0,i.wg)(),(0,i.iD)("div",n,[(0,i._)("div",{class:(0,l.C_)(["no-items fade-in",{shadow:s.withShadow}])},[(0,i.WI)(e.$slots,"default",{},void 0,!0)],2)])}var o={name:"NoItems",props:{withShadow:{type:Boolean,default:!0}}},u=s(3744);const d=(0,u.Z)(o,[["render",a],["__scopeId","data-v-4856c4d7"]]);var r=d},9516:function(e,t,s){s.r(t),s.d(t,{default:function(){return f}});var i=s(6252);const l={class:"media-youtube-playlist"};function n(e,t,s,n,a,o){const u=(0,i.up)("Loading"),d=(0,i.up)("NoItems"),r=(0,i.up)("Results");return(0,i.wg)(),(0,i.iD)("div",l,[a.loading?((0,i.wg)(),(0,i.j4)(u,{key:0})):a.items?.length?((0,i.wg)(),(0,i.j4)(r,{key:2,results:a.items,sources:{youtube:!0},filter:s.filter,"selected-result":a.selectedResult,onSelect:t[0]||(t[0]=e=>a.selectedResult=e),onPlay:t[1]||(t[1]=t=>e.$emit("play",t))},null,8,["results","filter","selected-result"])):((0,i.wg)(),(0,i.j4)(d,{key:1,"with-shadow":!1},{default:(0,i.w5)((()=>[(0,i.Uk)(" No videos found. ")])),_:1}))])}var a=s(3222),o=s(6791),u=s(382),d=s(8637),r={emits:["play"],mixins:[d.Z],components:{Loading:o.Z,NoItems:a.Z,Results:u.Z},props:{id:{type:String,required:!0},filter:{type:String,default:null}},data(){return{items:[],loading:!1,selectedResult:null}},methods:{async loadItems(){this.loading=!0;try{this.items=(await this.request("youtube.get_playlist",{id:this.id})).map((e=>({...e,type:"youtube"})))}finally{this.loading=!1}}},mounted(){this.loadItems()}},c=s(3744);const p=(0,c.Z)(r,[["render",n],["__scopeId","data-v-f6d5d450"]]);var f=p}}]);
//# sourceMappingURL=9516.7c5f8e4e.js.map