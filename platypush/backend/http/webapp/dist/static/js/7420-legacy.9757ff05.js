"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[7420],{7420:function(e,t,r){r.r(t),r.d(t,{default:function(){return m}});var n=r(6252),s=r(3577),i={class:"rss-news"},u={key:0,class:"article"},c=["textContent"],l=["textContent"],a=["textContent"];function h(e,t,r,h,o,d){return(0,n.wg)(),(0,n.iD)("div",i,[e.currentArticle?((0,n.wg)(),(0,n.iD)("div",u,[(0,n._)("div",{class:"source",textContent:(0,s.zw)(e.currentArticle.feed_title||e.currentArticle.feed_url)},null,8,c),(0,n._)("div",{class:"title",textContent:(0,s.zw)(e.currentArticle.title)},null,8,l),(0,n._)("div",{class:"published",textContent:(0,s.zw)(new Date(e.currentArticle.published).toDateString()+", "+new Date(e.currentArticle.published).toTimeString().substring(0,5))},null,8,a)])):(0,n.kq)("",!0)])}var o=r(9584),d=r(8534),p=(r(5666),r(9653),r(6977),r(2628)),f={name:"RssNews",mixins:[p.Z],props:{limit:{type:Number,required:!1,default:25},refreshSeconds:{type:Number,required:!1,default:15}},data:function(){return{articles:[],queue:[],currentArticle:void 0}},methods:{refresh:function(){var e=(0,d.Z)(regeneratorRuntime.mark((function e(){return regeneratorRuntime.wrap((function(e){while(1)switch(e.prev=e.next){case 0:if(this.queue.length){e.next=5;break}return e.next=3,this.request("rss.get_latest_entries",{limit:this.limit});case 3:this.articles=e.sent,this.queue=(0,o.Z)(this.articles).reverse();case 5:if(this.queue.length){e.next=7;break}return e.abrupt("return");case 7:this.currentArticle=this.queue.pop();case 8:case"end":return e.stop()}}),e,this)})));function t(){return e.apply(this,arguments)}return t}()},mounted:function(){this.refresh(),setInterval(this.refresh,parseInt((1e3*this.refreshSeconds).toFixed(0)))}},v=r(3744);const w=(0,v.Z)(f,[["render",h],["__scopeId","data-v-24745ce0"]]);var m=w}}]);
//# sourceMappingURL=7420-legacy.9757ff05.js.map