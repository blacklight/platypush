"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[5638],{5638:function(e,t,n){n.r(t),n.d(t,{default:function(){return C}});var s=n(6252),a=n(3577);const i={class:"calendar"},r={key:1,class:"no-events"},d={key:2,class:"event upcoming-event"},l=["textContent"],o=["textContent"],u={class:"time"},c={key:3,class:"event-list"},v=["textContent"],m=["textContent"],f=["textContent"];function h(e,t,n,h,g,w){const p=(0,s.up)("Loading");return(0,s.wg)(),(0,s.iD)("div",i,[e.loading?((0,s.wg)(),(0,s.j4)(p,{key:0})):e.events.length?e.events.length>0?((0,s.wg)(),(0,s.iD)("div",d,[(0,s._)("div",{class:"date",textContent:(0,a.zw)(e.formatDate(e.events[0].start))},null,8,l),(0,s._)("div",{class:"summary",textContent:(0,a.zw)(e.events[0].summary)},null,8,o),(0,s._)("div",u,(0,a.zw)(e.formatTime(e.events[0].start,!1))+" - "+(0,a.zw)(e.formatTime(e.events[0].end,!1)),1)])):(0,s.kq)("",!0):((0,s.wg)(),(0,s.iD)("div",r," No events found ")),e.events.length>1?((0,s.wg)(),(0,s.iD)("div",c,[((0,s.wg)(!0),(0,s.iD)(s.HY,null,(0,s.Ko)(e.events.slice(1,n.maxEvents),(t=>((0,s.wg)(),(0,s.iD)("div",{class:"event",key:t.id},[(0,s._)("div",{class:"date col-2",textContent:(0,a.zw)(e.formatDate(t.start))},null,8,v),(0,s._)("div",{class:"time col-2",textContent:(0,a.zw)(e.formatTime(t.start,!1))},null,8,m),(0,s._)("div",{class:"summary col-8",textContent:(0,a.zw)(t.summary)},null,8,f)])))),128))])):(0,s.kq)("",!0)])}var g=n(5576),w=n(6791),p={name:"Calendar",components:{Loading:w.Z},mixins:[g.Z],props:{maxEvents:{type:Number,required:!1,default:10},refreshSeconds:{type:Number,required:!1,default:600}},data:function(){return{events:[],loading:!1}},methods:{refresh:async function(){this.loading=!0;try{this.events=(await this.request("calendar.get_upcoming_events")).map((e=>(e.start&&(e.start=new Date(e.start.dateTime||e.start.date)),e.end&&(e.end=new Date(e.end.dateTime||e.end.date)),e)))}finally{this.loading=!1}}},mounted:function(){this.refresh(),setInterval(this.refresh,parseInt((1e3*this.refreshSeconds).toFixed(0)))}},y=n(3744);const x=(0,y.Z)(p,[["render",h],["__scopeId","data-v-44a3b988"]]);var C=x}}]);
//# sourceMappingURL=5638.2cef8bcb.js.map