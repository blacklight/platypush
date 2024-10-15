"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[1039],{1039:function(e,t,l){l.r(t),l.d(t,{default:function(){return g}});var i=l(6252);const o={class:"videos index"},s={key:1,class:"wrapper music-wrapper"},c={key:3,class:"wrapper items-wrapper"};function n(e,t,l,n,a,r){const d=(0,i.up)("Loading"),m=(0,i.up)("Music"),p=(0,i.up)("NoItems"),u=(0,i.up)("Collections"),h=(0,i.up)("Results");return(0,i.wg)(),(0,i.iD)("div",o,[e.isLoading?((0,i.wg)(),(0,i.j4)(d,{key:0})):"music"===e.collection?.collection_type?((0,i.wg)(),(0,i.iD)("div",s,[(0,i.Wm)(m,{collection:e.collection,filter:e.filter,loading:e.isLoading,path:e.path,onPlay:t[0]||(t[0]=t=>e.$emit("play",t)),onPlayWithOpts:t[1]||(t[1]=t=>e.$emit("play-with-opts",t)),onSelect:t[2]||(t[2]=t=>{e.selectedResult=t,e.$emit("select",t)}),onSelectCollection:r.selectCollection},null,8,["collection","filter","loading","path","onSelectCollection"])])):e.items?.length?((0,i.wg)(),(0,i.iD)("div",c,[r.collections.length>0?((0,i.wg)(),(0,i.j4)(u,{key:0,collection:e.collection,filter:e.filter,items:r.collections,loading:e.isLoading,"parent-id":e.collection?.id,onSelect:r.selectCollection},null,8,["collection","filter","items","loading","parent-id","onSelect"])):(0,i.kq)("",!0),r.mediaItems.length>0?((0,i.wg)(),(0,i.j4)(h,{key:1,results:r.mediaItems,sources:{jellyfin:!0},filter:e.filter,"selected-result":e.selectedResult,onAddToPlaylist:t[3]||(t[3]=t=>e.$emit("add-to-playlist",t)),onDownload:t[4]||(t[4]=t=>e.$emit("download",t)),onPlay:t[5]||(t[5]=t=>e.$emit("play",t)),onPlayWithOpts:t[6]||(t[6]=t=>e.$emit("play-with-opts",t)),onRemoveFromPlaylist:t[7]||(t[7]=t=>e.$emit("remove-from-playlist",t)),onSelect:t[8]||(t[8]=t=>e.selectedResult=t)},null,8,["results","filter","selected-result"])):(0,i.kq)("",!0)])):((0,i.wg)(),(0,i.j4)(p,{key:2,"with-shadow":!1},{default:(0,i.w5)((()=>[(0,i.Uk)(" No videos found. ")])),_:1}))])}var a=l(1112),r=l(6791),d=l(8113),m=l(1137),p=l(3222),u=l(5167),h={mixins:[d["default"]],emits:["select","select-collection"],components:{Collections:a["default"],Loading:r.Z,Music:m["default"],NoItems:p.Z,Results:u.Z},computed:{collections(){return this.sortedItems?.filter((e=>"collection"===e.item_type))??[]},mediaItems(){const e=this.sortedItems?.filter((e=>"collection"!==e.item_type))??[];return this.collection&&!this.collection.collection_type?e.sort(((e,t)=>{if(e.created_at&&t.created_at)return new Date(e.created_at)<new Date(t.created_at);if(e.created_at)return-1;if(t.created_at)return 1;let l=[e.name||e.title||"",t.name||t.title||""];return l[0].localeCompare(l[1])})):e}},methods:{selectCollection(e){this.$emit("select-collection",{type:"homevideos",...e})},async init(){const e=this.getUrlArgs();let t=e?.collection;if(t){this.loading_=!0;try{t=await this.request("media.jellyfin.info",{item_id:t}),t&&this.selectCollection(t)}finally{this.loading_=!1}}},async refresh(){if("music"!==this.collection?.collection_type){this.loading_=!0;try{"tvshows"===this.collection?.collection_type?this.items=(await this.request("media.jellyfin.get_collections",{parent_id:this.collection.id})).map((e=>({...e,item_type:"collection"}))):this.items=this.collection?.id?await this.request("media.jellyfin.get_items",{parent_id:this.collection.id,limit:25e3}):(await this.request("media.jellyfin.get_collections")).map((e=>({...e,item_type:"collection"})))}finally{this.loading_=!1}}}},async mounted(){this.init(),await this.refresh()}},y=l(3744);const f=(0,y.Z)(h,[["render",n],["__scopeId","data-v-d3b1ee0c"]]);var g=f}}]);
//# sourceMappingURL=1039.740c8191.js.map