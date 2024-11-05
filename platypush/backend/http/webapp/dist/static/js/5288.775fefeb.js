"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[5288,9064,5766,5150],{5288:function(t,e,i){i.r(e),i.d(e,{default:function(){return f}});var l=i(641);const o={class:"media-jellyfin-container browser"},n={class:"media-jellyfin-browser"};function s(t,e,i,s,a,c){const r=(0,l.g2)("MediaNav"),d=(0,l.g2)("Loading"),u=(0,l.g2)("Movies"),h=(0,l.g2)("Media");return(0,l.uX)(),(0,l.CE)("div",o,[(0,l.bF)(r,{path:a.path,onBack:e[0]||(e[0]=e=>t.$emit("back")),onSelect:c.select},null,8,["path","onSelect"]),(0,l.Lk)("div",n,[c.isLoading?((0,l.uX)(),(0,l.Wv)(d,{key:0})):"movies"===c.currentView?((0,l.uX)(),(0,l.Wv)(u,(0,l.v6)({key:1},c.componentData.props,(0,l.Tb)(c.componentData.on),{collection:a.collection,onSelect:c.select,onView:e[1]||(e[1]=e=>t.$emit("view",e))}),null,16,["collection","onSelect"])):((0,l.uX)(),(0,l.Wv)(h,(0,l.v6)({key:2},c.componentData.props,(0,l.Tb)(c.componentData.on),{collection:a.collection,onSelect:c.select,onSelectCollection:c.selectCollection,onView:e[2]||(e[2]=e=>t.$emit("view",e))}),null,16,["collection","onSelect","onSelectCollection"]))])])}i(4114);var a=i(9828),c=i(5150),r=i(47),d=i(5766),u=i(2436),h={mixins:[r["default"]],components:{Loading:a.A,MediaNav:c["default"],Media:d["default"],Movies:u["default"]},emits:["add-to-playlist","back","download","path-change","play","play-with-opts","view"],data(){return{collection:null,loading_:!1,path:[]}},computed:{componentData(){return{props:{collection:this.collection,filter:this.filter,loading:this.isLoading,path:this.path},on:{"add-to-playlist":t=>this.$emit("add-to-playlist",t),download:t=>this.$emit("download",t),play:t=>this.$emit("play",t),"play-with-opts":t=>this.$emit("play-with-opts",t)}}},currentView(){if(!this.collection)return"index";switch(this.collection.collection_type){case"movies":return"movies";case"homevideos":return"videos";case"music":return"music";default:return"index"}},isLoading(){return this.loading_||this.loading},rootItem(){const t={id:"",title:"Jellyfin",type:"index",icon:{class:"fas fa-server"}};return t.click=()=>{this.collection=null,this.select(t)},t}},methods:{select(t){if(t){if(this.path.length>0&&this.path[this.path.length-1].id===t.id)return;if("index"===t.type)this.path=[this.rootItem];else{const e=this.path.findIndex((e=>e.id===t.id));e>=0?this.path=this.path.slice(0,e+1):this.path.push({title:t.name,click:()=>this.selectCollection(t),...t})}}else this.path=[];this.$emit("path-change",this.path)},selectCollection(t){this.collection=t,this.select(t)}},watch:{collection(){this.setUrlArgs({collection:this.collection?.id})}},mounted(){this.path=[this.rootItem]},unmounted(){this.setUrlArgs({collection:null})}},p=i(6262);const m=(0,p.A)(h,[["render",s],["__scopeId","data-v-5c4d8ddd"]]);var f=m},9064:function(t,e,i){i.r(e),i.d(e,{default:function(){return A}});var l=i(641);const o={class:"sort-buttons"},n={class:"sort-buttons-dropdown-body"},s=(0,l.Lk)("div",{class:"title"},"Sort Direction",-1),a=(0,l.Lk)("div",{class:"title"},"Sort By",-1);function c(t,e,i,c,r,d){const u=(0,l.g2)("DropdownItem"),h=(0,l.g2)("Dropdown");return(0,l.uX)(),(0,l.CE)("div",o,[(0,l.bF)(h,{"icon-class":d.btnIconClass,glow:"",right:"",title:d.title},{default:(0,l.k6)((()=>[(0,l.Lk)("div",n,[s,(0,l.bF)(u,{text:"Ascending","icon-class":"fa fa-arrow-up-short-wide","item-class":{active:!i.value?.desc},onInput:e[0]||(e[0]=t=>d.onDescChange(!1))},null,8,["item-class"]),(0,l.bF)(u,{text:"Descending","icon-class":"fa fa-arrow-down-wide-short","item-class":{active:i.value?.desc},onInput:e[1]||(e[1]=t=>d.onDescChange(!0))},null,8,["item-class"]),a,(0,l.bF)(u,{text:"Name","icon-class":"fa fa-font","item-class":{active:"title"===i.value?.attr},onInput:e[2]||(e[2]=t=>d.onAttrChange("title"))},null,8,["item-class"]),i.withReleaseDate?((0,l.uX)(),(0,l.Wv)(u,{key:0,text:"Release Date","icon-class":"fa fa-calendar","item-class":{active:"year"===i.value?.attr},onInput:e[3]||(e[3]=t=>d.onAttrChange("year"))},null,8,["item-class"])):(0,l.Q3)("",!0),i.withCriticRating?((0,l.uX)(),(0,l.Wv)(u,{key:1,text:"Critics Rating","icon-class":"fa fa-star","item-class":{active:"critic_rating"===i.value?.attr},onInput:e[4]||(e[4]=t=>d.onAttrChange("critic_rating"))},null,8,["item-class"])):(0,l.Q3)("",!0),i.withCommunityRating?((0,l.uX)(),(0,l.Wv)(u,{key:2,text:"Community Rating","icon-class":"fa fa-users","item-class":{active:"community_rating"===i.value?.attr},onInput:e[5]||(e[5]=t=>d.onAttrChange("community_rating"))},null,8,["item-class"])):(0,l.Q3)("",!0)])])),_:1},8,["icon-class","title"])])}var r=i(3751),d=i(33);const u={class:"floating-dropdown-container"},h={class:"body-container hidden",ref:"dropdownContainer"};function p(t,e,i,o,n,s){const a=(0,l.g2)("FloatingButton"),c=(0,l.g2)("DropdownBody");return(0,l.uX)(),(0,l.CE)("div",u,[(0,l.bF)(a,{disabled:t.disabled,iconClass:t.iconClass,iconUrl:t.iconUrl,glow:t.glow,left:t.left,right:t.right,title:t.title,top:t.top,bottom:t.bottom,ref:"button",onClick:e[0]||(e[0]=(0,r.D$)((e=>t.toggle(e)),["stop"]))},null,8,["disabled","iconClass","iconUrl","glow","left","right","title","top","bottom"]),(0,l.Lk)("div",h,[(0,l.bF)(c,{id:t.id,keepOpenOnItemClick:t.keepOpenOnItemClick,style:(0,d.Tr)(t.style),ref:"dropdown",onClick:t.onClick},{default:(0,l.k6)((()=>[(0,l.RG)(t.$slots,"default",{},void 0,!0)])),_:3},8,["id","keepOpenOnItemClick","style","onClick"])],512)])}var m=i(9265),f=i(4200),v=i(7998),y={mixins:[m.A,v.A],emits:["click"],components:{DropdownBody:f.A,FloatingButton:v.A}},g=i(6262);const w=(0,g.A)(y,[["render",p],["__scopeId","data-v-2e3f2ab5"]]);var k=w,C=i(9612),_=i(2002),b={emits:["input"],mixins:[_.A],components:{Dropdown:k,DropdownItem:C.A},props:{value:{type:Object,required:!0},withReleaseDate:{type:Boolean,default:!1},withCriticRating:{type:Boolean,default:!1},withCommunityRating:{type:Boolean,default:!1}},computed:{btnIconClass(){return this.value?.desc?"fa fa-arrow-down-wide-short":"fa fa-arrow-up-short-wide"},title(){return"Sort By: "+(this.value?.attr??"[none]")+" "+(this.value?.desc?"descending":"ascending")}},methods:{onAttrChange(t){this.$emit("input",{attr:t,desc:!!this.value?.desc})},onDescChange(t){this.$emit("input",{attr:this.value?.attr,desc:t})}},watch:{value(){this.setUrlArgs({sort:this.value?.attr,desc:this.value?.desc})}},mounted(){const t=this.getUrlArgs(),e=t.sort,i="true"===t.desc?.toString();(e||i)&&this.$emit("input",{attr:e,desc:i})},unmounted(){this.setUrlArgs({sort:null,desc:null})}};const I=(0,g.A)(b,[["render",c]]);var A=I},5766:function(t,e,i){i.r(e),i.d(e,{default:function(){return y}});var l=i(641);const o={class:"videos index"},n={key:1,class:"wrapper music-wrapper"},s={key:3,class:"wrapper items-wrapper"};function a(t,e,i,a,c,r){const d=(0,l.g2)("Loading"),u=(0,l.g2)("Music"),h=(0,l.g2)("NoItems"),p=(0,l.g2)("Collections"),m=(0,l.g2)("Results");return(0,l.uX)(),(0,l.CE)("div",o,[t.isLoading?((0,l.uX)(),(0,l.Wv)(d,{key:0})):"music"===t.collection?.collection_type?((0,l.uX)(),(0,l.CE)("div",n,[(0,l.bF)(u,{collection:t.collection,filter:t.filter,loading:t.isLoading,path:t.path,onPlay:e[0]||(e[0]=e=>t.$emit("play",e)),onPlayWithOpts:e[1]||(e[1]=e=>t.$emit("play-with-opts",e)),onSelect:e[2]||(e[2]=e=>{t.selectedResult=e,t.$emit("select",e)}),onSelectCollection:r.selectCollection,onView:e[3]||(e[3]=e=>t.$emit("view",e))},null,8,["collection","filter","loading","path","onSelectCollection"])])):t.items?.length?((0,l.uX)(),(0,l.CE)("div",s,[r.collections.length>0?((0,l.uX)(),(0,l.Wv)(p,{key:0,collection:t.collection,filter:t.filter,items:r.collections,loading:t.isLoading,"parent-id":t.collection?.id,onSelect:r.selectCollection},null,8,["collection","filter","items","loading","parent-id","onSelect"])):(0,l.Q3)("",!0),r.mediaItems.length>0?((0,l.uX)(),(0,l.Wv)(m,{key:1,results:r.mediaItems,sources:{jellyfin:!0},filter:t.filter,"selected-result":t.selectedResult,onAddToPlaylist:e[4]||(e[4]=e=>t.$emit("add-to-playlist",e)),onDownload:e[5]||(e[5]=e=>t.$emit("download",e)),onPlay:e[6]||(e[6]=e=>t.$emit("play",e)),onPlayWithOpts:e[7]||(e[7]=e=>t.$emit("play-with-opts",e)),onRemoveFromPlaylist:e[8]||(e[8]=e=>t.$emit("remove-from-playlist",e)),onSelect:r.selectItem,onView:e[9]||(e[9]=e=>t.$emit("view",e))},null,8,["results","filter","selected-result","onSelect"])):(0,l.Q3)("",!0)])):((0,l.uX)(),(0,l.Wv)(h,{key:2,"with-shadow":!1},{default:(0,l.k6)((()=>[(0,l.eW)(" No videos found. ")])),_:1}))])}var c=i(3644),r=i(9828),d=i(2012),u=i(3006),h=i(6561),p=i(1101),m={mixins:[d["default"]],emits:["select","select-collection"],components:{Collections:c["default"],Loading:r.A,Music:u["default"],NoItems:h.A,Results:p.A},computed:{collections(){return this.sortedItems?.filter((t=>"collection"===t.item_type))??[]},mediaItems(){const t=this.sortedItems?.filter((t=>"collection"!==t.item_type))??[];return!this.collection||this.collection.collection_type&&"books"!==this.collection.collection_type?t:t.sort(((t,e)=>{if(t.created_at&&e.created_at)return new Date(t.created_at)<new Date(e.created_at);if(t.created_at)return-1;if(e.created_at)return 1;let i=[t.name||t.title||"",e.name||e.title||""];return i[0].localeCompare(i[1])}))}},methods:{selectCollection(t){this.$emit("select-collection",{type:"homevideos",...t})},selectItem(t){const e=this.items[t];"book"===e.item_type&&e.embed_url?window.open(e.embed_url,"_blank"):this.selectedResult=t},async init(){const t=this.getUrlArgs();let e=t?.collection;if(e){this.loading_=!0;try{e=await this.request("media.jellyfin.info",{item_id:e}),e&&this.selectCollection(e)}finally{this.loading_=!1}}},async refresh(){if("music"!==this.collection?.collection_type){this.loading_=!0;try{"tvshows"===this.collection?.collection_type?this.items=(await this.request("media.jellyfin.get_collections",{parent_id:this.collection.id})).map((t=>({...t,item_type:"collection"}))):this.items=this.collection?.id?await this.request("media.jellyfin.get_items",{parent_id:this.collection.id,limit:25e3}):(await this.request("media.jellyfin.get_collections")).map((t=>({...t,item_type:"collection"})))}finally{this.loading_=!1}}}},async mounted(){this.init(),await this.refresh()}},f=i(6262);const v=(0,f.A)(m,[["render",a],["__scopeId","data-v-46a825e6"]]);var y=v},2436:function(t,e,i){i.r(e),i.d(e,{default:function(){return m}});var l=i(641);const o={class:"movies index"};function n(t,e,i,n,s,a){const c=(0,l.g2)("Loading"),r=(0,l.g2)("NoItems"),d=(0,l.g2)("Results"),u=(0,l.g2)("SortButton");return(0,l.uX)(),(0,l.CE)("div",o,[t.isLoading?((0,l.uX)(),(0,l.Wv)(c,{key:0})):0===a.movies.length?((0,l.uX)(),(0,l.Wv)(r,{key:1,"with-shadow":!1},{default:(0,l.k6)((()=>[(0,l.eW)(" No movies found. ")])),_:1})):((0,l.uX)(),(0,l.Wv)(d,{key:2,results:a.movies,sources:{jellyfin:!0},filter:t.filter,"selected-result":t.selectedResult,onAddToPlaylist:e[0]||(e[0]=e=>t.$emit("add-to-playlist",e)),onDownload:e[1]||(e[1]=e=>t.$emit("download",e)),onPlay:e[2]||(e[2]=e=>t.$emit("play",e)),onPlayWithOpts:e[3]||(e[3]=e=>t.$emit("play-with-opts",e)),onRemoveFromPlaylist:e[4]||(e[4]=e=>t.$emit("remove-from-playlist",e)),onSelect:e[5]||(e[5]=e=>t.selectedResult=e),onView:e[6]||(e[6]=e=>t.$emit("view",e))},null,8,["results","filter","selected-result"])),a.movies.length>0?((0,l.uX)(),(0,l.Wv)(u,{key:3,value:t.sort,"with-release-date":!0,"with-critic-rating":!0,"with-community-rating":!0,onInput:e[7]||(e[7]=e=>t.sort=e)},null,8,["value"])):(0,l.Q3)("",!0)])}var s=i(9828),a=i(2012),c=i(6561),r=i(1101),d=i(9064),u={mixins:[a["default"]],components:{Loading:s.A,NoItems:c.A,Results:r.A,SortButton:d["default"]},computed:{movies(){return this.sortedItems?.filter((t=>"movie"===t.item_type))??[]}},async mounted(){await this.refresh()}},h=i(6262);const p=(0,h.A)(u,[["render",n],["__scopeId","data-v-5adf10b7"]]);var m=p},5150:function(t,e,i){i.r(e),i.d(e,{default:function(){return k}});var l=i(641),o=i(33);const n=t=>((0,l.Qi)("data-v-1e886630"),t=t(),(0,l.jt)(),t),s={class:"nav"},a={class:"path"},c=n((()=>(0,l.Lk)("i",{class:"fas fa-home"},null,-1))),r=[c],d=n((()=>(0,l.Lk)("span",{class:"separator"},[(0,l.Lk)("i",{class:"fas fa-chevron-right"})],-1))),u=["title","onClick"],h={key:1},p={key:0,class:"separator"},m=n((()=>(0,l.Lk)("i",{class:"fas fa-chevron-right"},null,-1))),f=[m];function v(t,e,i,n,c,m){return(0,l.uX)(),(0,l.CE)("div",s,[(0,l.Lk)("span",a,[(0,l.Lk)("span",{class:"back token",title:"Back",onClick:e[0]||(e[0]=e=>t.$emit("back"))},r),d]),((0,l.uX)(!0),(0,l.CE)(l.FK,null,(0,l.pI)(i.path,((e,n)=>((0,l.uX)(),(0,l.CE)("span",{class:"path",key:n},[(0,l.Lk)("span",{class:"token",title:e.title,onClick:t=>m.onClick(e)},[(t.icon=e.icon?.["class"])?((0,l.uX)(),(0,l.CE)("i",{key:0,class:(0,o.C4)(["icon",t.icon])},null,2)):(0,l.Q3)("",!0),e.title?((0,l.uX)(),(0,l.CE)("span",h,(0,o.v_)(e.title),1)):(0,l.Q3)("",!0)],8,u),(n>0||i.path.length>1)&&n<i.path.length-1?((0,l.uX)(),(0,l.CE)("span",p,f)):(0,l.Q3)("",!0)])))),128))])}var y={emits:["back","select"],props:{path:{type:Array,default:()=>[]}},methods:{onClick(t){t.click&&(t.click(),this.$emit("select",t))}}},g=i(6262);const w=(0,g.A)(y,[["render",v],["__scopeId","data-v-1e886630"]]);var k=w}}]);
//# sourceMappingURL=5288.775fefeb.js.map