"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[8031],{4660:function(t,e,i){i.d(e,{Z:function(){return v}});var n=i(6252),o=i(9963),s=i(3577);const l={class:"dropdown-container"},r=["title"],a=["textContent"],d={class:"body-container hidden",ref:"dropdownContainer"};function c(t,e,i,c,p,u){const h=(0,n.up)("DropdownBody");return(0,n.wg)(),(0,n.iD)("div",l,[(0,n._)("button",{title:i.title,ref:"button",onClick:e[0]||(e[0]=(0,o.iM)((t=>u.toggle(t)),["stop"]))},[i.iconClass?((0,n.wg)(),(0,n.iD)("i",{key:0,class:(0,s.C_)(["icon",i.iconClass])},null,2)):(0,n.kq)("",!0),i.text?((0,n.wg)(),(0,n.iD)("span",{key:1,class:"text",textContent:(0,s.zw)(i.text)},null,8,a)):(0,n.kq)("",!0)],8,r),(0,n._)("div",d,[(0,n.Wm)(h,{id:i.id,keepOpenOnItemClick:i.keepOpenOnItemClick,style:(0,s.j5)(i.style),ref:"dropdown",onClick:u.onClick},{default:(0,n.w5)((()=>[(0,n.WI)(t.$slots,"default",{},void 0,!0)])),_:3},8,["id","keepOpenOnItemClick","style","onClick"])],512)])}const p=["id"];function u(t,e,i,o,l,r){return(0,n.wg)(),(0,n.iD)("div",{class:"dropdown",id:i.id,style:(0,s.j5)(i.style),onClick:e[0]||(e[0]=e=>t.$emit("click",e))},[(0,n.WI)(t.$slots,"default",{},void 0,!0)],12,p)}var h={emits:["click"],props:{id:{type:String},keepOpenOnItemClick:{type:Boolean,default:!1},style:{type:Object,default:()=>({})}}},f=i(3744);const g=(0,f.Z)(h,[["render",u],["__scopeId","data-v-24c5aa28"]]);var m=g,k=i(5250),w={components:{DropdownBody:m},emits:["click"],props:{id:{type:String},iconClass:{default:"fa fa-ellipsis-h"},text:{type:String},title:{type:String},keepOpenOnItemClick:{type:Boolean,default:!1},style:{type:Object,default:()=>({})}},data(){return{visible:!1}},computed:{buttonStyle(){return this.$refs.button?getComputedStyle(this.$refs.button):{}},buttonWidth(){return parseFloat(this.buttonStyle.width||0)},buttonHeight(){return parseFloat(this.buttonStyle.height||0)}},methods:{documentClickHndl(t){if(!this.visible)return;let e=t.target;while(e){if(e.classList.contains("dropdown"))return;e=e.parentElement}this.close()},getDropdownWidth(){const t=this.$refs.dropdown?.$el;return t?parseFloat(getComputedStyle(t).width):0},getDropdownHeight(){const t=this.$refs.dropdown?.$el;return t?parseFloat(getComputedStyle(t).height):0},onClick(t){return this.keepOpenOnItemClick||this.close(),"A"===t.target.tagName?(t.preventDefault(),!1):t.defaultPrevented?(t.stopPropagation(),!1):void 0},close(){this.visible=!1,document.removeEventListener("click",this.documentClickHndl),k.$.emit("dropdown-close")},open(){document.addEventListener("click",this.documentClickHndl);const t=this.$refs.dropdown?.$el;t.parentElement||this.$el.appendChild(t),this.visible=!0,this.$refs.dropdownContainer.classList.remove("hidden"),this.$nextTick(this.adjustDropdownPos)},adjustDropdownPos(){const t=this.$refs.button.getBoundingClientRect(),e={left:t.left+window.scrollX,top:t.top+window.scrollY},i={left:e.left,top:e.top+this.buttonHeight},n=this.getDropdownWidth(),o=this.getDropdownHeight();if(i.left+n>(window.innerWidth+window.scrollX)/2&&(i.left-=n-this.buttonWidth),i.top+o>(window.innerHeight+window.scrollY)/2){let t=i.top-(o+this.buttonHeight-10);t<0&&(t=0),i.top=t}const s=this.$refs.dropdown.$el;s.classList.add("fade-in"),s.style.top=`${i.top}px`,s.style.left=`${i.left}px`,k.$.emit("dropdown-open",this.$refs.dropdown),this.$refs.dropdownContainer.classList.add("hidden")},toggle(t){t.stopPropagation(),this.$emit("click",t),this.visible?this.close():this.open()},onKeyUp(t){t.stopPropagation(),"Escape"===t.key&&this.close()}},mounted(){document.body.addEventListener("keyup",this.onKeyUp)},unmounted(){document.body.removeEventListener("keyup",this.onKeyUp)}};const y=(0,f.Z)(w,[["render",c],["__scopeId","data-v-9d2b1bfc"]]);var v=y},7597:function(t,e,i){i.d(e,{Z:function(){return f}});var n=i(6252),o=i(3577);const s=["title"],l={key:0,class:"col-2 icon"},r=["textContent"];function a(t,e,i,a,d,c){const p=(0,n.up)("Icon");return(0,n.wg)(),(0,n.iD)("div",{class:(0,o.C_)(["row item",{...c.itemClass_,disabled:i.disabled}]),title:i.hoverText,onClick:e[0]||(e[0]=(...t)=>c.clicked&&c.clicked(...t))},[i.iconClass?.length||i.iconUrl?.length?((0,n.wg)(),(0,n.iD)("div",l,[(0,n.Wm)(p,{class:(0,o.C_)(i.iconClass),url:i.iconUrl},null,8,["class","url"])])):(0,n.kq)("",!0),(0,n._)("div",{class:(0,o.C_)(["text",{"col-10":null!=i.iconClass}]),textContent:(0,o.zw)(i.text)},null,10,r)],10,s)}var d=i(657),c=i(5250),p={components:{Icon:d.Z},emits:["click","input"],props:{iconClass:{type:String},iconUrl:{type:String},text:{type:String},hoverText:{type:String,default:null},disabled:{type:Boolean,default:!1},itemClass:{}},computed:{itemClass_(){return"string"===typeof this.itemClass?{[this.itemClass]:!0}:this.itemClass}},methods:{clicked(t){if(this.$parent.keepOpenOnItemClick||c.$.emit("dropdown-close"),this.disabled)return t.stopPropagation(),t.preventDefault(),!1;this.$emit("input",t)}}},u=i(3744);const h=(0,u.Z)(p,[["render",a],["__scopeId","data-v-2babe09c"]]);var f=h},657:function(t,e,i){i.d(e,{Z:function(){return p}});var n=i(6252),o=i(3577);const s={class:"icon-container"},l=["src","alt"];function r(t,e,i,r,a,d){return(0,n.wg)(),(0,n.iD)("div",s,[i.url?.length?((0,n.wg)(),(0,n.iD)("img",{key:0,class:"icon",src:i.url,alt:i.alt},null,8,l)):d.className?.length?((0,n.wg)(),(0,n.iD)("i",{key:1,class:(0,o.C_)(["icon",d.className]),style:(0,o.j5)({color:i.color})},null,6)):(0,n.kq)("",!0)])}var a={props:{class:{type:String},url:{type:String},color:{type:String,default:""},alt:{type:String,default:""}},computed:{className(){return this.class}}},d=i(3744);const c=(0,d.Z)(a,[["render",r],["__scopeId","data-v-706a3bd1"]]);var p=c},2496:function(t,e,i){i.r(e),i.d(e,{default:function(){return b}});var n=i(6252);const o={class:"row plugin file-container"},s={key:1,class:"file-browser"};function l(t,e,i,l,r,a){const d=(0,n.up)("Loading"),c=(0,n.up)("Header"),p=(0,n.up)("Browser");return(0,n.wg)(),(0,n.iD)("div",o,[r.loading?((0,n.wg)(),(0,n.j4)(d,{key:0})):((0,n.wg)(),(0,n.iD)("div",s,[(0,n.Wm)(c,{filter:r.filter,onFilter:e[0]||(e[0]=t=>r.filter=t)},null,8,["filter"]),(0,n.Wm)(p,{"initial-path":null,filter:r.filter,homepage:a.displayedBookmarks},null,8,["filter","homepage"])]))])}var r=i(8409),a=i(9963);const d={class:"header"},c={class:"row"},p={class:"col-s-8 col-m-7 left side"},u={class:"search-box"};function h(t,e,i,o,s,l){return(0,n.wg)(),(0,n.iD)("div",d,[(0,n._)("div",c,[(0,n._)("div",p,[(0,n._)("label",u,[(0,n.wy)((0,n._)("input",{type:"search",placeholder:"Filter","onUpdate:modelValue":e[0]||(e[0]=t=>s.filter=t),onChange:e[1]||(e[1]=e=>t.$emit("filter",e.target.value)),onKeyup:e[2]||(e[2]=e=>t.$emit("filter",e.target.value))},null,544),[[a.nr,s.filter]])])])])])}var f=i(8637),g={mixins:[f.Z],emits:["filter"],data(){return{filter:""}}},m=i(3744);const k=(0,m.Z)(g,[["render",h],["__scopeId","data-v-76d6af7b"]]);var w=k,y=i(6791),v={mixins:[f.Z],components:{Browser:r.Z,Header:w,Loading:y.Z},data(){return{bookmarks:{},configDir:null,filter:"",homeDir:null,loading:!1}},computed:{displayedBookmarks(){const t={Root:{name:"Root",path:"/",icon:{class:"fas fa-hard-drive"}}};return this.homeDir&&(t.Home={name:"Home",path:this.homeDir,icon:{class:"fas fa-home"}}),this.configDir&&(t.Configuration={name:"Configuration",path:this.configDir,icon:{class:"fas fa-cogs"}}),{...t,...this.bookmarks}}},methods:{async getConfig(){this.loading=!0;try{let t=null;[this.homeDir,this.bookmarks,t]=await Promise.all([this.request("file.get_user_home"),this.request("file.get_bookmarks"),this.request("config.get_config_file")]),t&&(this.configDir=t.split("/").slice(0,-1).join("/"))}finally{this.loading=!1}}},mounted(){this.getConfig()}};const C=(0,m.Z)(v,[["render",l],["__scopeId","data-v-ac6ee662"]]);var b=C}}]);
//# sourceMappingURL=8031.1080086d.js.map