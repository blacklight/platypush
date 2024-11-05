"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[2436,2012,9064,47],{6561:function(t,e,n){n.d(e,{A:function(){return d}});var i=n(641),o=n(33);const s={class:"no-items-container"};function a(t,e,n,a,l,r){return(0,i.uX)(),(0,i.CE)("div",s,[(0,i.Lk)("div",{class:(0,o.C4)(["no-items fade-in",{shadow:n.withShadow}])},[(0,i.RG)(t.$slots,"default",{},void 0,!0)],2)])}var l={name:"NoItems",props:{withShadow:{type:Boolean,default:!0}}},r=n(6262);const c=(0,r.A)(l,[["render",a],["__scopeId","data-v-4856c4d7"]]);var d=c},2012:function(t,e,n){n.r(e),n.d(e,{default:function(){return a}});var i=n(47),o={mixins:[i["default"]],emits:["add-to-playlist","back","download","play","play-with-opts","select","view"],props:{collection:{type:Object},path:{type:Array,default:()=>[]}},data(){return{items:[],loading_:!1,selectedResult:null,sort:{attr:"title",desc:!1}}},computed:{isLoading(){return this.loading_||this.loading},sortedItems(){return this.items?[...this.items].sort(((t,e)=>{const n=this.sort.attr,i=this.sort.desc;let o=t[n],s=e[n];return"number"===typeof o||"number"===typeof s?(o=o||0,s=s||0,i?s-o:o-s):(o=(o||"").toString().toLowerCase(),s=(s||"").toString().toLowerCase(),i?s.localeCompare(o):o.localeCompare(s))})).map((t=>({item_type:t.type,...t,type:"jellyfin"}))):[]}},methods:{async refresh(){const t=this.collection?.name;if(t?.length){this.loading_=!0;try{this.items=await this.request("media.jellyfin.search",{collection:t,limit:1e3})}finally{this.loading_=!1}}}},watch:{collection(){this.refresh()}}};const s=o;var a=s},9064:function(t,e,n){n.r(e),n.d(e,{default:function(){return _}});var i=n(641);const o={class:"sort-buttons"},s={class:"sort-buttons-dropdown-body"},a=(0,i.Lk)("div",{class:"title"},"Sort Direction",-1),l=(0,i.Lk)("div",{class:"title"},"Sort By",-1);function r(t,e,n,r,c,d){const u=(0,i.g2)("DropdownItem"),m=(0,i.g2)("Dropdown");return(0,i.uX)(),(0,i.CE)("div",o,[(0,i.bF)(m,{"icon-class":d.btnIconClass,glow:"",right:"",title:d.title},{default:(0,i.k6)((()=>[(0,i.Lk)("div",s,[a,(0,i.bF)(u,{text:"Ascending","icon-class":"fa fa-arrow-up-short-wide","item-class":{active:!n.value?.desc},onInput:e[0]||(e[0]=t=>d.onDescChange(!1))},null,8,["item-class"]),(0,i.bF)(u,{text:"Descending","icon-class":"fa fa-arrow-down-wide-short","item-class":{active:n.value?.desc},onInput:e[1]||(e[1]=t=>d.onDescChange(!0))},null,8,["item-class"]),l,(0,i.bF)(u,{text:"Name","icon-class":"fa fa-font","item-class":{active:"title"===n.value?.attr},onInput:e[2]||(e[2]=t=>d.onAttrChange("title"))},null,8,["item-class"]),n.withReleaseDate?((0,i.uX)(),(0,i.Wv)(u,{key:0,text:"Release Date","icon-class":"fa fa-calendar","item-class":{active:"year"===n.value?.attr},onInput:e[3]||(e[3]=t=>d.onAttrChange("year"))},null,8,["item-class"])):(0,i.Q3)("",!0),n.withCriticRating?((0,i.uX)(),(0,i.Wv)(u,{key:1,text:"Critics Rating","icon-class":"fa fa-star","item-class":{active:"critic_rating"===n.value?.attr},onInput:e[4]||(e[4]=t=>d.onAttrChange("critic_rating"))},null,8,["item-class"])):(0,i.Q3)("",!0),n.withCommunityRating?((0,i.uX)(),(0,i.Wv)(u,{key:2,text:"Community Rating","icon-class":"fa fa-users","item-class":{active:"community_rating"===n.value?.attr},onInput:e[5]||(e[5]=t=>d.onAttrChange("community_rating"))},null,8,["item-class"])):(0,i.Q3)("",!0)])])),_:1},8,["icon-class","title"])])}var c=n(3751),d=n(33);const u={class:"floating-dropdown-container"},m={class:"body-container hidden",ref:"dropdownContainer"};function p(t,e,n,o,s,a){const l=(0,i.g2)("FloatingButton"),r=(0,i.g2)("DropdownBody");return(0,i.uX)(),(0,i.CE)("div",u,[(0,i.bF)(l,{disabled:t.disabled,iconClass:t.iconClass,iconUrl:t.iconUrl,glow:t.glow,left:t.left,right:t.right,title:t.title,top:t.top,bottom:t.bottom,ref:"button",onClick:e[0]||(e[0]=(0,c.D$)((e=>t.toggle(e)),["stop"]))},null,8,["disabled","iconClass","iconUrl","glow","left","right","title","top","bottom"]),(0,i.Lk)("div",m,[(0,i.bF)(r,{id:t.id,keepOpenOnItemClick:t.keepOpenOnItemClick,style:(0,d.Tr)(t.style),ref:"dropdown",onClick:t.onClick},{default:(0,i.k6)((()=>[(0,i.RG)(t.$slots,"default",{},void 0,!0)])),_:3},8,["id","keepOpenOnItemClick","style","onClick"])],512)])}var h=n(9265),f=n(4200),g=n(7998),v={mixins:[h.A,g.A],emits:["click"],components:{DropdownBody:f.A,FloatingButton:g.A}},y=n(6262);const w=(0,y.A)(v,[["render",p],["__scopeId","data-v-2e3f2ab5"]]);var C=w,k=n(9612),b=n(2002),A={emits:["input"],mixins:[b.A],components:{Dropdown:C,DropdownItem:k.A},props:{value:{type:Object,required:!0},withReleaseDate:{type:Boolean,default:!1},withCriticRating:{type:Boolean,default:!1},withCommunityRating:{type:Boolean,default:!1}},computed:{btnIconClass(){return this.value?.desc?"fa fa-arrow-down-wide-short":"fa fa-arrow-up-short-wide"},title(){return"Sort By: "+(this.value?.attr??"[none]")+" "+(this.value?.desc?"descending":"ascending")}},methods:{onAttrChange(t){this.$emit("input",{attr:t,desc:!!this.value?.desc})},onDescChange(t){this.$emit("input",{attr:this.value?.attr,desc:t})}},watch:{value(){this.setUrlArgs({sort:this.value?.attr,desc:this.value?.desc})}},mounted(){const t=this.getUrlArgs(),e=t.sort,n="true"===t.desc?.toString();(e||n)&&this.$emit("input",{attr:e,desc:n})},unmounted(){this.setUrlArgs({sort:null,desc:null})}};const I=(0,y.A)(A,[["render",r]]);var _=I},2436:function(t,e,n){n.r(e),n.d(e,{default:function(){return h}});var i=n(641);const o={class:"movies index"};function s(t,e,n,s,a,l){const r=(0,i.g2)("Loading"),c=(0,i.g2)("NoItems"),d=(0,i.g2)("Results"),u=(0,i.g2)("SortButton");return(0,i.uX)(),(0,i.CE)("div",o,[t.isLoading?((0,i.uX)(),(0,i.Wv)(r,{key:0})):0===l.movies.length?((0,i.uX)(),(0,i.Wv)(c,{key:1,"with-shadow":!1},{default:(0,i.k6)((()=>[(0,i.eW)(" No movies found. ")])),_:1})):((0,i.uX)(),(0,i.Wv)(d,{key:2,results:l.movies,sources:{jellyfin:!0},filter:t.filter,"selected-result":t.selectedResult,onAddToPlaylist:e[0]||(e[0]=e=>t.$emit("add-to-playlist",e)),onDownload:e[1]||(e[1]=e=>t.$emit("download",e)),onPlay:e[2]||(e[2]=e=>t.$emit("play",e)),onPlayWithOpts:e[3]||(e[3]=e=>t.$emit("play-with-opts",e)),onRemoveFromPlaylist:e[4]||(e[4]=e=>t.$emit("remove-from-playlist",e)),onSelect:e[5]||(e[5]=e=>t.selectedResult=e),onView:e[6]||(e[6]=e=>t.$emit("view",e))},null,8,["results","filter","selected-result"])),l.movies.length>0?((0,i.uX)(),(0,i.Wv)(u,{key:3,value:t.sort,"with-release-date":!0,"with-critic-rating":!0,"with-community-rating":!0,onInput:e[7]||(e[7]=e=>t.sort=e)},null,8,["value"])):(0,i.Q3)("",!0)])}var a=n(9828),l=n(2012),r=n(6561),c=n(1101),d=n(9064),u={mixins:[l["default"]],components:{Loading:a.A,NoItems:r.A,Results:c.A,SortButton:d["default"]},computed:{movies(){return this.sortedItems?.filter((t=>"movie"===t.item_type))??[]}},async mounted(){await this.refresh()}},m=n(6262);const p=(0,m.A)(u,[["render",s],["__scopeId","data-v-5adf10b7"]]);var h=p},47:function(t,e,n){n.r(e),n.d(e,{default:function(){return a}});var i=n(2002),o={mixins:[i.A],emits:["add-to-playlist","back","create-playlist","download","download-audio","path-change","play","remove-from-playlist","remove-playlist","rename-playlist"],props:{filter:{type:String,default:""},loading:{type:Boolean,default:!1},mediaPlugin:{type:String},selectedPlaylist:{default:null},selectedChannel:{default:null}},data(){return{loading_:!1}},computed:{isLoading(){return this.loading||this.loading_}}};const s=o;var a=s}}]);
//# sourceMappingURL=2436.6c6745d9.js.map