"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[7452],{7452:function(e,t,s){s.r(t),s.d(t,{default:function(){return y}});var u=s(6252);const l={class:"media-youtube-feed"};function d(e,t,s,d,n,a){const o=(0,u.up)("Loading"),i=(0,u.up)("NoItems"),c=(0,u.up)("Results");return(0,u.wg)(),(0,u.iD)("div",l,[n.loading?((0,u.wg)(),(0,u.j4)(o,{key:0})):n.feed?.length?((0,u.wg)(),(0,u.j4)(c,{key:2,results:n.feed,sources:{youtube:!0},"selected-result":n.selectedResult,onSelect:t[0]||(t[0]=e=>n.selectedResult=e),onPlay:t[1]||(t[1]=t=>e.$emit("play",t))},null,8,["results","selected-result"])):((0,u.wg)(),(0,u.j4)(i,{key:1,"with-shadow":!1},{default:(0,u.w5)((()=>[(0,u.Uk)(" No videos found. ")])),_:1}))])}var n=s(3222),a=s(6791),o=s(8804),i=s(8637),c={emits:["play"],mixins:[i.Z],components:{Loading:a.Z,NoItems:n.Z,Results:o.Z},data(){return{feed:[],loading:!1,selectedResult:null}},methods:{async loadFeed(){this.loading=!0;try{this.feed=(await this.request("youtube.get_feed")).map((e=>({...e,type:"youtube"})))}finally{this.loading=!1}}},mounted(){this.loadFeed()}},r=s(3744);const p=(0,r.Z)(c,[["render",d],["__scopeId","data-v-d9e6809e"]]);var y=p}}]);
//# sourceMappingURL=7452.511562c4.js.map