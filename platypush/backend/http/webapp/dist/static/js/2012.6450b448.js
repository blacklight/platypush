"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[2012,47],{2012:function(t,e,l){l.r(e),l.d(e,{default:function(){return o}});var i=l(47),a={mixins:[i["default"]],emits:["add-to-playlist","back","download","play","play-with-opts","select","view"],props:{collection:{type:Object},path:{type:Array,default:()=>[]}},data(){return{items:[],loading_:!1,selectedResult:null,sort:{attr:"title",desc:!1}}},computed:{isLoading(){return this.loading_||this.loading},sortedItems(){return this.items?"playlist"===this.collection?.item_type?this.items:[...this.items].sort(((t,e)=>{const l=this.sort.attr,i=this.sort.desc;let a=t[l],s=e[l];return"number"===typeof a||"number"===typeof s?(a=a||0,s=s||0,i?s-a:a-s):(a=(a||"").toString().toLowerCase(),s=(s||"").toString().toLowerCase(),i?s.localeCompare(a):a.localeCompare(s))})).map((t=>({item_type:t.type,...t,type:"jellyfin"}))):[]}},methods:{async refresh(){const t=this.collection?.name;if(t?.length){this.loading_=!0;try{this.items=await this.request("media.jellyfin.search",{collection:t,limit:1e3})}finally{this.loading_=!1}}}},watch:{collection(){this.refresh()}}};const s=a;var o=s},47:function(t,e,l){l.r(e),l.d(e,{default:function(){return o}});var i=l(2002),a={mixins:[i.A],emits:["add-to-playlist","back","create-playlist","download","download-audio","path-change","play","remove-from-playlist","remove-playlist","rename-playlist"],props:{filter:{type:String,default:""},loading:{type:Boolean,default:!1},mediaPlugin:{type:String},selectedPlaylist:{default:null},selectedChannel:{default:null}},data(){return{loading_:!1}},computed:{isLoading(){return this.loading||this.loading_}}};const s=a;var o=s}}]);
//# sourceMappingURL=2012.6450b448.js.map