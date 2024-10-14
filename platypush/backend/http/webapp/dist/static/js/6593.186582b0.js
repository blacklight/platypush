"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[6593,8113,4279,6640],{3222:function(t,e,i){i.d(e,{Z:function(){return d}});var n=i(6252),o=i(3577);const s={class:"no-items-container"};function a(t,e,i,a,l,r){return(0,n.wg)(),(0,n.iD)("div",s,[(0,n._)("div",{class:(0,o.C_)(["no-items fade-in",{shadow:i.withShadow}])},[(0,n.WI)(t.$slots,"default",{},void 0,!0)],2)])}var l={name:"NoItems",props:{withShadow:{type:Boolean,default:!0}}},r=i(3744);const c=(0,r.Z)(l,[["render",a],["__scopeId","data-v-4856c4d7"]]);var d=c},8113:function(t,e,i){i.r(e),i.d(e,{default:function(){return a}});var n=i(6640),o={mixins:[n["default"]],emits:["add-to-playlist","back","download","play","play-with-opts","select"],props:{collection:{type:Object},path:{type:Array,default:()=>[]}},data(){return{items:[],loading_:!1,selectedResult:null,sort:{attr:"title",desc:!1}}},computed:{isLoading(){return this.loading_||this.loading},sortedItems(){return this.items?[...this.items].sort(((t,e)=>{const i=this.sort.attr,n=this.sort.desc;let o=t[i],s=e[i];return"number"===typeof o||"number"===typeof s?(o=o||0,s=s||0,n?s-o:o-s):(o=(o||"").toString().toLowerCase(),s=(s||"").toString().toLowerCase(),n?s.localeCompare(o):o.localeCompare(s))})).map((t=>({item_type:t.type,...t,type:"jellyfin"}))):[]}},methods:{async refresh(){const t=this.collection?.name;if(t?.length){this.loading_=!0;try{this.items=await this.request("media.jellyfin.search",{collection:t,limit:1e3})}finally{this.loading_=!1}}}},watch:{collection(){this.refresh()}}};const s=o;var a=s},4279:function(t,e,i){i.r(e),i.d(e,{default:function(){return D}});var n=i(6252);const o={class:"sort-buttons"},s={class:"sort-buttons-dropdown-body"},a=(0,n._)("div",{class:"title"},"Sort Direction",-1),l=(0,n._)("div",{class:"title"},"Sort By",-1);function r(t,e,i,r,c,d){const u=(0,n.up)("DropdownItem"),m=(0,n.up)("Dropdown");return(0,n.wg)(),(0,n.iD)("div",o,[(0,n.Wm)(m,{"icon-class":d.btnIconClass,glow:"",right:"",title:d.title},{default:(0,n.w5)((()=>[(0,n._)("div",s,[a,(0,n.Wm)(u,{text:"Ascending","icon-class":"fa fa-arrow-up-short-wide","item-class":{active:!i.value?.desc},onInput:e[0]||(e[0]=t=>d.onDescChange(!1))},null,8,["item-class"]),(0,n.Wm)(u,{text:"Descending","icon-class":"fa fa-arrow-down-wide-short","item-class":{active:i.value?.desc},onInput:e[1]||(e[1]=t=>d.onDescChange(!0))},null,8,["item-class"]),l,(0,n.Wm)(u,{text:"Name","icon-class":"fa fa-font","item-class":{active:"title"===i.value?.attr},onInput:e[2]||(e[2]=t=>d.onAttrChange("title"))},null,8,["item-class"]),i.withReleaseDate?((0,n.wg)(),(0,n.j4)(u,{key:0,text:"Release Date","icon-class":"fa fa-calendar","item-class":{active:"year"===i.value?.attr},onInput:e[3]||(e[3]=t=>d.onAttrChange("year"))},null,8,["item-class"])):(0,n.kq)("",!0),i.withCriticRating?((0,n.wg)(),(0,n.j4)(u,{key:1,text:"Critics Rating","icon-class":"fa fa-star","item-class":{active:"critic_rating"===i.value?.attr},onInput:e[4]||(e[4]=t=>d.onAttrChange("critic_rating"))},null,8,["item-class"])):(0,n.kq)("",!0),i.withCommunityRating?((0,n.wg)(),(0,n.j4)(u,{key:2,text:"Community Rating","icon-class":"fa fa-users","item-class":{active:"community_rating"===i.value?.attr},onInput:e[5]||(e[5]=t=>d.onAttrChange("community_rating"))},null,8,["item-class"])):(0,n.kq)("",!0)])])),_:1},8,["icon-class","title"])])}var c=i(9963),d=i(3577);const u={class:"floating-dropdown-container"},m={class:"body-container hidden",ref:"dropdownContainer"};function p(t,e,i,o,s,a){const l=(0,n.up)("FloatingButton"),r=(0,n.up)("DropdownBody");return(0,n.wg)(),(0,n.iD)("div",u,[(0,n.Wm)(l,{disabled:t.disabled,iconClass:t.iconClass,iconUrl:t.iconUrl,glow:t.glow,left:t.left,right:t.right,title:t.title,top:t.top,bottom:t.bottom,ref:"button",onClick:e[0]||(e[0]=(0,c.iM)((e=>t.toggle(e)),["stop"]))},null,8,["disabled","iconClass","iconUrl","glow","left","right","title","top","bottom"]),(0,n._)("div",m,[(0,n.Wm)(r,{id:t.id,keepOpenOnItemClick:t.keepOpenOnItemClick,style:(0,d.j5)(t.style),ref:"dropdown",onClick:t.onClick},{default:(0,n.w5)((()=>[(0,n.WI)(t.$slots,"default",{},void 0,!0)])),_:3},8,["id","keepOpenOnItemClick","style","onClick"])],512)])}var h=i(1370),f=i(3218),g=i(3825),w={mixins:[h.Z,g.Z],emits:["click"],components:{DropdownBody:f.Z,FloatingButton:g.Z}},y=i(3744);const v=(0,y.Z)(w,[["render",p],["__scopeId","data-v-2e3f2ab5"]]);var C=v,k=i(7597),_=i(8637),I={emits:["input"],mixins:[_.Z],components:{Dropdown:C,DropdownItem:k.Z},props:{value:{type:Object,required:!0},withReleaseDate:{type:Boolean,default:!1},withCriticRating:{type:Boolean,default:!1},withCommunityRating:{type:Boolean,default:!1}},computed:{btnIconClass(){return this.value?.desc?"fa fa-arrow-down-wide-short":"fa fa-arrow-up-short-wide"},title(){return"Sort By: "+(this.value?.attr??"[none]")+" "+(this.value?.desc?"descending":"ascending")}},methods:{onAttrChange(t){this.$emit("input",{attr:t,desc:!!this.value?.desc})},onDescChange(t){this.$emit("input",{attr:this.value?.attr,desc:t})}},watch:{value(){this.setUrlArgs({sort:this.value?.attr,desc:this.value?.desc})}},mounted(){const t=this.getUrlArgs(),e=t.sort,i="true"===t.desc?.toString();(e||i)&&this.$emit("input",{attr:e,desc:i})},unmounted(){this.setUrlArgs({sort:null,desc:null})}};const b=(0,y.Z)(I,[["render",r]]);var D=b},6593:function(t,e,i){i.r(e),i.d(e,{default:function(){return h}});var n=i(6252);const o={class:"movies index"};function s(t,e,i,s,a,l){const r=(0,n.up)("Loading"),c=(0,n.up)("NoItems"),d=(0,n.up)("Results"),u=(0,n.up)("SortButton");return(0,n.wg)(),(0,n.iD)("div",o,[t.isLoading?((0,n.wg)(),(0,n.j4)(r,{key:0})):0===l.movies.length?((0,n.wg)(),(0,n.j4)(c,{key:1,"with-shadow":!1},{default:(0,n.w5)((()=>[(0,n.Uk)(" No movies found. ")])),_:1})):((0,n.wg)(),(0,n.j4)(d,{key:2,results:l.movies,sources:{jellyfin:!0},filter:t.filter,"selected-result":t.selectedResult,onAddToPlaylist:e[0]||(e[0]=e=>t.$emit("add-to-playlist",e)),onDownload:e[1]||(e[1]=e=>t.$emit("download",e)),onPlay:e[2]||(e[2]=e=>t.$emit("play",e)),onPlayWithOpts:e[3]||(e[3]=e=>t.$emit("play-with-opts",e)),onRemoveFromPlaylist:e[4]||(e[4]=e=>t.$emit("remove-from-playlist",e)),onSelect:e[5]||(e[5]=e=>t.selectedResult=e)},null,8,["results","filter","selected-result"])),l.movies.length>0?((0,n.wg)(),(0,n.j4)(u,{key:3,value:t.sort,"with-release-date":!0,"with-critic-rating":!0,"with-community-rating":!0,onInput:e[6]||(e[6]=e=>t.sort=e)},null,8,["value"])):(0,n.kq)("",!0)])}var a=i(6791),l=i(8113),r=i(3222),c=i(1602),d=i(4279),u={mixins:[l["default"]],components:{Loading:a.Z,NoItems:r.Z,Results:c.Z,SortButton:d["default"]},computed:{movies(){return this.sortedItems?.filter((t=>"movie"===t.item_type))??[]}},async mounted(){await this.refresh()}},m=i(3744);const p=(0,m.Z)(u,[["render",s],["__scopeId","data-v-f07087c4"]]);var h=p},6640:function(t,e,i){i.r(e),i.d(e,{default:function(){return a}});var n=i(8637),o={mixins:[n.Z],emits:["add-to-playlist","back","create-playlist","download","download-audio","path-change","play","remove-from-playlist","remove-playlist","rename-playlist"],props:{filter:{type:String,default:""},loading:{type:Boolean,default:!1},mediaPlugin:{type:String},selectedPlaylist:{default:null},selectedChannel:{default:null}},data(){return{loading_:!1}},computed:{isLoading(){return this.loading||this.loading_}}};const s=o;var a=s}}]);
//# sourceMappingURL=6593.186582b0.js.map