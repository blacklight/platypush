"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[5778],{5778:function(e,t,l){l.r(t),l.d(t,{default:function(){return g}});var i=l(6252);const o={class:"videos index"},s={key:1,class:"wrapper music-wrapper"},n={key:3,class:"wrapper items-wrapper"};function c(e,t,l,c,a,d){const r=(0,i.up)("Loading"),m=(0,i.up)("Music"),p=(0,i.up)("NoItems"),u=(0,i.up)("Collections"),h=(0,i.up)("Results");return(0,i.wg)(),(0,i.iD)("div",o,[e.isLoading?((0,i.wg)(),(0,i.j4)(r,{key:0})):"music"===e.collection?.collection_type?((0,i.wg)(),(0,i.iD)("div",s,[(0,i.Wm)(m,{collection:e.collection,filter:e.filter,loading:e.isLoading,path:e.path,onPlay:t[0]||(t[0]=t=>e.$emit("play",t)),onPlayWithOpts:t[1]||(t[1]=t=>e.$emit("play-with-opts",t)),onSelect:t[2]||(t[2]=t=>{e.selectedResult=t,e.$emit("select",t)}),onSelectCollection:d.selectCollection},null,8,["collection","filter","loading","path","onSelectCollection"])])):e.items?.length?((0,i.wg)(),(0,i.iD)("div",n,[d.collections.length>0?((0,i.wg)(),(0,i.j4)(u,{key:0,collection:e.collection,filter:e.filter,items:d.collections,loading:e.isLoading,"parent-id":e.collection?.id,onSelect:d.selectCollection},null,8,["collection","filter","items","loading","parent-id","onSelect"])):(0,i.kq)("",!0),d.mediaItems.length>0?((0,i.wg)(),(0,i.j4)(h,{key:1,results:d.mediaItems,sources:{jellyfin:!0},filter:e.filter,"selected-result":e.selectedResult,onAddToPlaylist:t[3]||(t[3]=t=>e.$emit("add-to-playlist",t)),onDownload:t[4]||(t[4]=t=>e.$emit("download",t)),onPlay:t[5]||(t[5]=t=>e.$emit("play",t)),onPlayWithOpts:t[6]||(t[6]=t=>e.$emit("play-with-opts",t)),onRemoveFromPlaylist:t[7]||(t[7]=t=>e.$emit("remove-from-playlist",t)),onSelect:t[8]||(t[8]=t=>e.selectedResult=t)},null,8,["results","filter","selected-result"])):(0,i.kq)("",!0)])):((0,i.wg)(),(0,i.j4)(p,{key:2,"with-shadow":!1},{default:(0,i.w5)((()=>[(0,i.Uk)(" No videos found. ")])),_:1}))])}var a=l(1112),d=l(6791),r=l(8113),m=l(33),p=l(3222),u=l(5167),h={mixins:[r["default"]],emits:["select","select-collection"],components:{Collections:a["default"],Loading:d.Z,Music:m["default"],NoItems:p.Z,Results:u.Z},computed:{collections(){return this.sortedItems?.filter((e=>"collection"===e.item_type))??[]},mediaItems(){return this.sortedItems?.filter((e=>"collection"!==e.item_type))??[]}},methods:{selectCollection(e){this.$emit("select-collection",{type:"homevideos",...e})},async init(){const e=this.getUrlArgs();let t=e?.collection;if(t){this.loading_=!0;try{t=await this.request("media.jellyfin.info",{item_id:t}),t&&this.selectCollection(t)}finally{this.loading_=!1}}},async refresh(){if("music"!==this.collection?.collection_type){this.loading_=!0;try{"tvshows"===this.collection?.collection_type?this.items=(await this.request("media.jellyfin.get_collections",{parent_id:this.collection.id})).map((e=>({...e,item_type:"collection"}))):this.items=this.collection?.id?await this.request("media.jellyfin.get_items",{parent_id:this.collection.id,limit:5e3}):(await this.request("media.jellyfin.get_collections")).map((e=>({...e,item_type:"collection"})))}finally{this.loading_=!1}}}},async mounted(){this.init(),await this.refresh()}},y=l(3744);const f=(0,y.Z)(h,[["render",c],["__scopeId","data-v-6d38243d"]]);var g=f}}]);
//# sourceMappingURL=5778.2dcf8606.js.map