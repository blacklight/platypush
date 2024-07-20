(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[8224],{2787:function(e,t,n){"use strict";n.d(t,{Z:function(){return w}});var s=n(6252),a=n(9963),i=n(3577);const l={class:"dropdown-container"},o=["title"],r=["textContent"],c={class:"body-container hidden",ref:"dropdownContainer"};function u(e,t,n,u,d,p){const m=(0,s.up)("DropdownBody");return(0,s.wg)(),(0,s.iD)("div",l,[(0,s._)("button",{title:n.title,ref:"button",onClick:t[0]||(t[0]=(0,a.iM)((e=>p.toggle(e)),["stop"]))},[n.iconClass?((0,s.wg)(),(0,s.iD)("i",{key:0,class:(0,i.C_)(["icon",n.iconClass])},null,2)):(0,s.kq)("",!0),n.text?((0,s.wg)(),(0,s.iD)("span",{key:1,class:"text",textContent:(0,i.zw)(n.text)},null,8,r)):(0,s.kq)("",!0)],8,o),(0,s._)("div",c,[(0,s.Wm)(m,{id:n.id,keepOpenOnItemClick:n.keepOpenOnItemClick,ref:"dropdown",onClick:p.onClick},{default:(0,s.w5)((()=>[(0,s.WI)(e.$slots,"default",{},void 0,!0)])),_:3},8,["id","keepOpenOnItemClick","onClick"])],512)])}const d=["id"];function p(e,t,n,a,i,l){return(0,s.wg)(),(0,s.iD)("div",{class:"dropdown",id:n.id,onClick:t[0]||(t[0]=t=>e.$emit("click",t))},[(0,s.WI)(e.$slots,"default",{},void 0,!0)],8,d)}var m={emits:["click"],props:{id:{type:String},keepOpenOnItemClick:{type:Boolean,default:!1}}},f=n(3744);const h=(0,f.Z)(m,[["render",p],["__scopeId","data-v-14579c63"]]);var v=h,y=n(5250),_={components:{DropdownBody:v},emits:["click"],props:{id:{type:String},iconClass:{default:"fa fa-ellipsis-h"},text:{type:String},title:{type:String},keepOpenOnItemClick:{type:Boolean,default:!1}},data(){return{visible:!1}},computed:{buttonStyle(){return this.$refs.button?getComputedStyle(this.$refs.button):{}},buttonWidth(){return parseFloat(this.buttonStyle.width||0)},buttonHeight(){return parseFloat(this.buttonStyle.height||0)}},methods:{documentClickHndl(e){if(!this.visible)return;let t=e.target;while(t){if(t.classList.contains("dropdown"))return;t=t.parentElement}this.close()},getDropdownWidth(){const e=this.$refs.dropdown?.$el;return e?parseFloat(getComputedStyle(e).width):0},getDropdownHeight(){const e=this.$refs.dropdown?.$el;return e?parseFloat(getComputedStyle(e).height):0},onClick(){this.keepOpenOnItemClick||this.close()},close(){this.visible=!1,document.removeEventListener("click",this.documentClickHndl),y.$.emit("dropdown-close")},open(){document.addEventListener("click",this.documentClickHndl);const e=this.$refs.dropdown?.$el;e.parentElement||this.$el.appendChild(e),this.visible=!0,this.$refs.dropdownContainer.classList.remove("hidden"),this.$nextTick((()=>{const e=this.$refs.button.getBoundingClientRect(),t={left:e.left+window.scrollX,top:e.top+window.scrollY},n={left:t.left,top:t.top+this.buttonHeight},s=this.getDropdownWidth(),a=this.getDropdownHeight();n.left+s>(window.innerWidth+window.scrollX)/2&&(n.left-=s-this.buttonWidth),n.top+a>(window.innerHeight+window.scrollY)/2&&(n.top-=a+this.buttonHeight-10);const i=this.$refs.dropdown.$el;i.classList.add("fade-in"),i.style.top=`${n.top}px`,i.style.left=`${n.left}px`,y.$.emit("dropdown-open",this.$refs.dropdown),this.$refs.dropdownContainer.classList.add("hidden")}))},toggle(e){e.stopPropagation(),this.$emit("click"),this.visible?this.close():this.open()},onKeyUp(e){e.stopPropagation(),"Escape"===e.key&&this.close()}},mounted(){document.body.addEventListener("keyup",this.onKeyUp)},unmounted(){document.body.removeEventListener("keyup",this.onKeyUp)}};const g=(0,f.Z)(_,[["render",u],["__scopeId","data-v-3220f58b"]]);var w=g},815:function(e,t,n){"use strict";n.d(t,{Z:function(){return m}});var s=n(6252),a=n(3577);const i={key:0,class:"col-2 icon"},l=["textContent"];function o(e,t,n,o,r,c){const u=(0,s.up)("Icon");return(0,s.wg)(),(0,s.iD)("div",{class:(0,a.C_)(["row item",n.itemClass]),onClick:t[0]||(t[0]=(...e)=>c.clicked&&c.clicked(...e))},[n.iconClass?.length||n.iconUrl?.length?((0,s.wg)(),(0,s.iD)("div",i,[(0,s.Wm)(u,{class:(0,a.C_)(n.iconClass),url:n.iconUrl},null,8,["class","url"])])):(0,s.kq)("",!0),(0,s._)("div",{class:(0,a.C_)(["text",{"col-10":null!=n.iconClass}]),textContent:(0,a.zw)(n.text)},null,10,l)],2)}var r=n(657),c=n(5250),u={components:{Icon:r.Z},props:{iconClass:{type:String},iconUrl:{type:String},text:{type:String},disabled:{type:Boolean,default:!1},itemClass:{}},methods:{clicked(){if(this.disabled)return!1;this.$parent.keepOpenOnItemClick||c.$.emit("dropdown-close")}}},d=n(3744);const p=(0,d.Z)(u,[["render",o],["__scopeId","data-v-1311e9ab"]]);var m=p},657:function(e,t,n){"use strict";n.d(t,{Z:function(){return d}});var s=n(6252),a=n(3577);const i={class:"icon-container"},l=["src","alt"];function o(e,t,n,o,r,c){return(0,s.wg)(),(0,s.iD)("div",i,[n.url?.length?((0,s.wg)(),(0,s.iD)("img",{key:0,class:"icon",src:n.url,alt:n.alt},null,8,l)):c.className?.length?((0,s.wg)(),(0,s.iD)("i",{key:1,class:(0,a.C_)(["icon",c.className]),style:(0,a.j5)({color:n.color})},null,6)):(0,s.kq)("",!0)])}var r={props:{class:{type:String},url:{type:String},color:{type:String,default:""},alt:{type:String,default:""}},computed:{className(){return this.class}}},c=n(3744);const u=(0,c.Z)(r,[["render",o],["__scopeId","data-v-706a3bd1"]]);var d=u},3222:function(e,t,n){"use strict";n.d(t,{Z:function(){return u}});var s=n(6252),a=n(3577);const i={class:"no-items-container"};function l(e,t,n,l,o,r){return(0,s.wg)(),(0,s.iD)("div",i,[(0,s._)("div",{class:(0,a.C_)(["no-items fade-in",{shadow:n.withShadow}])},[(0,s.WI)(e.$slots,"default",{},void 0,!0)],2)])}var o={name:"NoItems",props:{withShadow:{type:Boolean,default:!0}}},r=n(3744);const c=(0,r.Z)(o,[["render",l],["__scopeId","data-v-4856c4d7"]]);var u=c},4558:function(e,t,n){"use strict";n.r(t),n.d(t,{default:function(){return f}});var s=n(6252),a=n(3577),i=n(9963);const l={key:0,class:"children fade-in"};function o(e,t,n,o,r,c){const u=(0,s.up)("Entity",!0);return(0,s.wg)(),(0,s.iD)("div",{class:(0,a.C_)(["entity-container-wrapper",{"with-children":c.hasChildren,collapsed:c.isCollapsed,hidden:!e.value?.name?.length}])},[(0,s._)("div",{class:(0,a.C_)(["row item entity-container",{"with-children":c.hasChildren,collapsed:c.isCollapsed,blink:r.justUpdated}])},[(0,s._)("div",{class:(0,a.C_)(["adjuster",{"with-children":c.hasChildren}])},[((0,s.wg)(),(0,s.j4)((0,s.LL)(r.component),{value:e.value,parent:e.parent,children:e.children,loading:e.loading,ref:"instance",error:e.error||0==e.value?.reachable,onClick:c.onClick,onInput:t[0]||(t[0]=t=>e.$emit("input",t)),onLoading:t[1]||(t[1]=t=>e.$emit("loading",t))},null,40,["value","parent","children","loading","error","onClick"]))],2),c.hasChildren?((0,s.wg)(),(0,s.iD)("div",{key:0,class:"col-1 collapse-toggler",onClick:t[2]||(t[2]=(0,i.iM)(((...e)=>c.toggleCollapsed&&c.toggleCollapsed(...e)),["stop"]))},[(0,s._)("i",{class:(0,a.C_)(["fas",{"fa-chevron-down":c.isCollapsed,"fa-chevron-up":!c.isCollapsed}])},null,2)])):(0,s.kq)("",!0)],2),c.hasChildren&&!c.isCollapsed?((0,s.wg)(),(0,s.iD)("div",l,[((0,s.wg)(!0),(0,s.iD)(s.HY,null,(0,s.Ko)(e.children,(n=>((0,s.wg)(),(0,s.iD)("div",{class:"child",key:n.id},[(0,s.Wm)(u,{value:n,parent:e.value,children:c.childrenByParentId(n.id),loading:e.loading,level:e.level+1,onShowModal:t[3]||(t[3]=t=>e.$emit("show-modal",t)),onInput:t=>e.$emit("input",n)},null,8,["value","parent","children","loading","level","onInput"])])))),128))])):(0,s.kq)("",!0)],2)}var r=n(2262),c=n(847),u=n(5250),d={name:"Entity",mixins:[c["default"]],emits:["input","loading","update","show-modal"],data(){return{component:null,justUpdated:!1}},computed:{hasChildren(){return!!Object.keys(this.children||{}).length},isCollapsed(){return!this.hasChildren||this.collapsed},instance(){return this.$refs.instance}},methods:{valuesEqual(e,t){e={...e},t={...t};for(const n of["updated_at","data"])delete e[n],delete t[n];return this.objectsEqual(e,t)},childrenByParentId(e){const t=this.allEntities?.[e];return t?(t.children_ids||[]).reduce(((e,t)=>{const n=this.allEntities[t];return n&&!n.is_configuration&&(e[n.id]=n),e}),{}):{}},onClick(e){e.stopPropagation(),e.target.classList.contains("label")||e.target.classList.contains("head")?this.toggleCollapsed():this.$emit("show-modal",this.value.id)},onEntityUpdate(e){const t=e?.id,n=null!=t&&this.children&&t in this.children;n&&this.notifyUpdate()},toggleCollapsed(){this.collapsed=!this.collapsed,this.instance&&(this.instance.collapsed=!this.instance.collapsed)},notifyUpdate(){this.justUpdated=!0;const e=this;setTimeout((()=>e.justUpdated=!1),1e3)}},mounted(){if("Entity"!==this.type){const e=this.type.split("_").map((e=>e[0].toUpperCase()+e.slice(1))).join("");this.$watch((()=>this.value),((e,t)=>{if(this.valuesEqual(t,e))return!1;this.notifyUpdate(),this.$emit("update",{value:e})})),this.component=(0,r.XI)((0,s.RC)((()=>n(7243)(`./${e}`))))}u.$.onEntity(this.onEntityUpdate)}},p=n(3744);const m=(0,p.Z)(d,[["render",o],["__scopeId","data-v-7b0732e4"]]);var f=m},4967:function(e,t,n){"use strict";n.r(t),n.d(t,{default:function(){return f}});var s=n(6252),a=n(3577);const i=["title"],l={key:0,class:"fas fa-spinner fa-spin loading"},o={key:1,class:"fas fa-circle-exclamation error"};function r(e,t,n,r,c,u){const d=(0,s.up)("Icon");return(0,s.wg)(),(0,s.iD)("div",{class:(0,a.C_)(["entity-icon-container",{"with-color-fill":!!u.colorFill}]),title:e.prettify(n.entity.type||""),style:(0,a.j5)(u.colorFillStyle)},[n.loading?((0,s.wg)(),(0,s.iD)("i",l)):n.error?((0,s.wg)(),(0,s.iD)("i",o)):((0,s.wg)(),(0,s.j4)(d,(0,a.vs)((0,s.dG)({key:2},u.computedIconNormalized)),null,16))],14,i)}var c=n(657),u=n(8637),d={name:"EntityIcon",components:{Icon:c.Z},mixins:[u.Z],props:{loading:{type:Boolean,default:!1},error:{type:Boolean,default:!1},entity:{type:Object,required:!0},icon:{type:Object,default:()=>{}},hasColorFill:{type:Boolean,default:!1}},data(){return{component:null,modalVisible:!1}},computed:{computedIcon(){let e={...this.entity?.meta?.icon||{}};return Object.keys(this.icon||{}).length&&(e=this.icon),{...e}},colorFill(){return this.hasColorFill&&this.computedIcon.color},colorFillStyle(){return this.colorFill&&!this.error?{background:this.colorFill}:{}},computedIconNormalized(){const e={...this.computedIcon};return this.colorFill&&delete e.color,e},type(){let e=this.entity.type||"";return e.charAt(0).toUpperCase()+e.slice(1)}}},p=n(3744);const m=(0,p.Z)(d,[["render",r],["__scopeId","data-v-49689016"]]);var f=m},847:function(e,t,n){"use strict";n.r(t),n.d(t,{default:function(){return l}});var s=n(8637),a={name:"EntityMixin",mixins:[s.Z],emits:["input","loading"],props:{loading:{type:Boolean,default:!1},error:{type:Boolean,default:!1},value:{type:Object,required:!0},parent:{type:Object,default:()=>{}},children:{type:Object,default:()=>{}},allEntities:{type:Object,default:()=>{}},level:{type:Number,default:0}},data(){return{modalVisible:!1,collapsed:!0}},computed:{type(){let e=this.value.type||"";return e.split("_").map((e=>e.charAt(0).toUpperCase()+e.slice(1))).join("")}}};const i=a;var l=i},1999:function(e,t,n){"use strict";n.r(t),n.d(t,{default:function(){return at}});var s=n(6252),a=n(3577),i=n(9963);const l=e=>((0,s.dD)("data-v-6fce01a8"),e=e(),(0,s.Cn)(),e),o=l((()=>(0,s._)("b",null,"sure",-1))),r=l((()=>(0,s._)("br",null,null,-1))),c=l((()=>(0,s._)("br",null,null,-1))),u=l((()=>(0,s._)("br",null,null,-1))),d=l((()=>(0,s._)("br",null,null,-1))),p={class:"table-row"},m={class:"title"},f={class:"value"},h=["textContent"],v={class:"table-row"},y={class:"title"},_={class:"value icon-canvas"},g={key:0,class:"icon-editor"},w=l((()=>(0,s._)("i",{class:"fas fa-rotate-left"},null,-1))),C=[w],S=l((()=>(0,s._)("span",{class:"help"},[(0,s.Uk)(" Supported: image URLs or "),(0,s._)("a",{href:"https://fontawesome.com/icons",target:"_blank"},"FontAwesome icon classes"),(0,s.Uk)(". ")],-1))),k={class:"table-row"},b=l((()=>(0,s._)("div",{class:"title"}," Icon color ",-1))),I={class:"value icon-color-picker"},x=["value"],D=l((()=>(0,s._)("i",{class:"fas fa-rotate-left"},null,-1))),E=[D],$={class:"table-row"},q=l((()=>(0,s._)("div",{class:"title"},"Plugin",-1))),O=["textContent"],U={class:"table-row"},j=l((()=>(0,s._)("div",{class:"title"},"Internal ID",-1))),B=["textContent"],W={key:0,class:"table-row"},N=l((()=>(0,s._)("div",{class:"title"},"External ID",-1))),L=["textContent"],M={key:1,class:"table-row"},F=l((()=>(0,s._)("div",{class:"title"},"Description",-1))),A=["textContent"],H={key:2,class:"table-row"},Z=l((()=>(0,s._)("div",{class:"title"},"External URL",-1))),P={class:"value url"},z=["href","text"],T={key:3,class:"table-row"},V=l((()=>(0,s._)("div",{class:"title"},"Image",-1))),R={class:"value"},K=["src"],Y={key:4,class:"table-row"},Q=l((()=>(0,s._)("div",{class:"title"},"Parent",-1))),X={class:"value"},G=["textContent"],J={key:5,class:"table-row"},ee=l((()=>(0,s._)("div",{class:"title"},"Created at",-1))),te=["textContent"],ne={key:6,class:"table-row"},se=l((()=>(0,s._)("div",{class:"title"},"Updated at",-1))),ae=["textContent"],ie=l((()=>(0,s._)("div",{class:"title"},"Delete Entity",-1))),le={class:"value"},oe=l((()=>(0,s._)("i",{class:"fas fa-trash"},null,-1))),re=[oe],ce={key:7,class:"section children-container"},ue=l((()=>(0,s._)("div",{class:"col-11"},[(0,s._)("i",{class:"fas fa-sitemap"}),(0,s.Uk)("   Children ")],-1))),de={class:"col-1 pull-right"},pe={key:0,class:"children-container-info"},me={class:"title"},fe={class:"value"},he=["onClick","textContent"],ve={class:"section extra-info-container"},ye=l((()=>(0,s._)("div",{class:"col-11"},[(0,s._)("i",{class:"fas fa-circle-info"}),(0,s.Uk)("   Extra Info ")],-1))),_e={class:"col-1 pull-right"},ge={key:0,class:"extra-info"},we={key:0,class:"table-row"},Ce=["textContent"],Se=["textContent"],ke={key:0,class:"table-row"},be=["textContent"],Ie=["textContent"],xe={key:8,class:"section config-container"},De=l((()=>(0,s._)("div",{class:"col-11"},[(0,s._)("i",{class:"fas fa-screwdriver-wrench"}),(0,s.Uk)("   Configuration ")],-1))),Ee={class:"col-1 pull-right"},$e={key:0,class:"entities"};function qe(e,t,n,l,w,D){const oe=(0,s.up)("ConfirmDialog"),qe=(0,s.up)("EditButton"),Oe=(0,s.up)("NameEditor"),Ue=(0,s.up)("Icon"),je=(0,s.up)("EntityIcon"),Be=(0,s.up)("Entity"),We=(0,s.up)("Modal",!0);return n.entity?((0,s.wg)(),(0,s.j4)(We,{key:0,visible:n.visible,class:"entity-modal",title:n.entity.name||n.entity.external_id},{default:(0,s.w5)((()=>[(0,s.Wm)(oe,{ref:"deleteConfirmDiag",title:"Confirm entity deletion",onInput:D.onDelete},{default:(0,s.w5)((()=>[(0,s.Uk)(" Are you "),o,(0,s.Uk)(" that you want to delete this entity? "),r,c,(0,s.Uk)(" Note: you should only delete an entity if its plugin has been disabled or the entity is no longer reachable."),u,d,(0,s.Uk)(" Otherwise, the entity will simply be created again upon the next scan. ")])),_:1},8,["onInput"]),(0,s._)("div",p,[(0,s._)("div",m,[(0,s.Uk)(" Name "),w.editName?(0,s.kq)("",!0):((0,s.wg)(),(0,s.j4)(qe,{key:0,onClick:t[0]||(t[0]=e=>w.editName=!0)}))]),(0,s._)("div",f,[w.editName?((0,s.wg)(),(0,s.j4)(Oe,{key:0,value:n.entity.name,onInput:D.onRename,onCancel:t[1]||(t[1]=e=>w.editName=!1),disabled:w.loading},null,8,["value","onInput","disabled"])):((0,s.wg)(),(0,s.iD)("span",{key:1,textContent:(0,a.zw)(n.entity.name)},null,8,h))])]),(0,s._)("div",v,[(0,s._)("div",y,[(0,s.Uk)(" Icon "),w.editIcon?(0,s.kq)("",!0):((0,s.wg)(),(0,s.j4)(qe,{key:0,onClick:t[2]||(t[2]=e=>w.editIcon=!0)}))]),(0,s._)("div",_,[w.editIcon?((0,s.wg)(),(0,s.iD)("span",g,[(0,s.Wm)(Oe,{value:n.entity.meta?.icon?.class||n.entity.meta?.icon?.url,onInput:D.onIconEdit,onCancel:t[5]||(t[5]=e=>w.editIcon=!1),disabled:w.loading},{default:(0,s.w5)((()=>[(0,s._)("button",{type:"button",title:"Reset",onClick:t[3]||(t[3]=e=>D.onIconEdit(null)),onTouch:t[4]||(t[4]=e=>D.onIconEdit(null))},C,32)])),_:1},8,["value","onInput","disabled"]),S])):((0,s.wg)(),(0,s.j4)(Ue,(0,a.vs)((0,s.dG)({key:1},n.entity?.meta?.icon||{})),null,16))])]),(0,s._)("div",k,[b,(0,s._)("div",I,[(0,s._)("input",{type:"color",value:n.entity.meta?.icon?.color,onChange:t[6]||(t[6]=(...e)=>D.onIconColorEdit&&D.onIconColorEdit(...e))},null,40,x),(0,s._)("button",{type:"button",title:"Reset",onClick:t[7]||(t[7]=e=>D.onIconColorEdit(null)),onTouch:t[8]||(t[8]=e=>D.onIconColorEdit(null))},E,32)])]),(0,s._)("div",$,[q,(0,s._)("div",{class:"value",textContent:(0,a.zw)(n.entity.plugin)},null,8,O)]),(0,s._)("div",U,[j,(0,s._)("div",{class:"value",textContent:(0,a.zw)(n.entity.id)},null,8,B)]),n.entity.external_id?((0,s.wg)(),(0,s.iD)("div",W,[N,(0,s._)("div",{class:"value",textContent:(0,a.zw)(n.entity.external_id)},null,8,L)])):(0,s.kq)("",!0),n.entity.description?((0,s.wg)(),(0,s.iD)("div",M,[F,(0,s._)("div",{class:"value",textContent:(0,a.zw)(n.entity.description)},null,8,A)])):(0,s.kq)("",!0),n.entity.external_url?((0,s.wg)(),(0,s.iD)("div",H,[Z,(0,s._)("div",P,[(0,s._)("a",{href:n.entity.external_url,target:"_blank",text:n.entity.external_url},null,8,z)])])):(0,s.kq)("",!0),n.entity.image_url?((0,s.wg)(),(0,s.iD)("div",T,[V,(0,s._)("div",R,[(0,s._)("img",{class:"entity-image",src:n.entity.image_url},null,8,K)])])):(0,s.kq)("",!0),n.parent?((0,s.wg)(),(0,s.iD)("div",Y,[Q,(0,s._)("div",X,[(0,s._)("a",{class:"url",onClick:t[9]||(t[9]=t=>e.$emit("entity-update",n.parent.id)),textContent:(0,a.zw)(n.parent.name)},null,8,G)])])):(0,s.kq)("",!0),n.entity.created_at?((0,s.wg)(),(0,s.iD)("div",J,[ee,(0,s._)("div",{class:"value",textContent:(0,a.zw)(e.formatDateTime(n.entity.created_at))},null,8,te)])):(0,s.kq)("",!0),n.entity.updated_at?((0,s.wg)(),(0,s.iD)("div",ne,[se,(0,s._)("div",{class:"value",textContent:(0,a.zw)(e.formatDateTime(n.entity.updated_at))},null,8,ae)])):(0,s.kq)("",!0),(0,s._)("div",{class:"table-row delete-entity-container",onClick:t[11]||(t[11]=t=>e.$refs.deleteConfirmDiag.show())},[ie,(0,s._)("div",le,[(0,s._)("button",{onClick:t[10]||(t[10]=(0,i.iM)((t=>e.$refs.deleteConfirmDiag.show()),["stop"]))},re)])]),Object.keys(n.children||{}).length?((0,s.wg)(),(0,s.iD)("div",ce,[(0,s._)("div",{class:"title section-title",onClick:t[12]||(t[12]=e=>w.childrenCollapsed=!w.childrenCollapsed)},[ue,(0,s._)("div",de,[(0,s._)("i",{class:(0,a.C_)(["fas",{"fa-chevron-down":w.childrenCollapsed,"fa-chevron-up":!w.childrenCollapsed}])},null,2)])]),w.childrenCollapsed?(0,s.kq)("",!0):((0,s.wg)(),(0,s.iD)("div",pe,[((0,s.wg)(!0),(0,s.iD)(s.HY,null,(0,s.Ko)(n.children,(t=>((0,s.wg)(),(0,s.iD)("div",{class:(0,a.C_)(["table-row",{hidden:!t.name?.length||t.is_configuration}]),key:t.id},[(0,s._)("div",me,[(0,s.Wm)(je,{entity:n.entity,icon:n.entity.meta?.icon},null,8,["entity","icon"]),(0,s.Uk)("   "+(0,a.zw)(e.prettify(t.type)),1)]),(0,s._)("div",fe,[(0,s._)("a",{class:"url",onClick:n=>e.$emit("entity-update",t.id),textContent:(0,a.zw)(t.name)},null,8,he)])],2)))),128))]))])):(0,s.kq)("",!0),(0,s._)("div",ve,[(0,s._)("div",{class:"title section-title",onClick:t[13]||(t[13]=e=>w.extraInfoCollapsed=!w.extraInfoCollapsed)},[ye,(0,s._)("div",_e,[(0,s._)("i",{class:(0,a.C_)(["fas",{"fa-chevron-down":w.extraInfoCollapsed,"fa-chevron-up":!w.extraInfoCollapsed}])},null,2)])]),w.extraInfoCollapsed?(0,s.kq)("",!0):((0,s.wg)(),(0,s.iD)("div",ge,[((0,s.wg)(!0),(0,s.iD)(s.HY,null,(0,s.Ko)(n.entity,((t,n)=>((0,s.wg)(),(0,s.iD)("div",{key:n},[null!=t&&w.specialFields.indexOf(n)<0?((0,s.wg)(),(0,s.iD)("div",we,[(0,s._)("div",{class:"title",textContent:(0,a.zw)(e.prettify(n))},null,8,Ce),(0,s._)("div",{class:"value",textContent:(0,a.zw)(D.stringify(t))},null,8,Se)])):(0,s.kq)("",!0)])))),128)),((0,s.wg)(!0),(0,s.iD)(s.HY,null,(0,s.Ko)(n.entity.data||{},((t,n)=>((0,s.wg)(),(0,s.iD)("div",{key:n},[null!=t?((0,s.wg)(),(0,s.iD)("div",ke,[(0,s._)("div",{class:"title",textContent:(0,a.zw)(e.prettify(n))},null,8,be),(0,s._)("div",{class:"value",textContent:(0,a.zw)(D.stringify(t))},null,8,Ie)])):(0,s.kq)("",!0)])))),128))]))]),D.computedConfig.length?((0,s.wg)(),(0,s.iD)("div",xe,[(0,s._)("div",{class:"title section-title",onClick:t[14]||(t[14]=e=>w.configCollapsed=!w.configCollapsed)},[De,(0,s._)("div",Ee,[(0,s._)("i",{class:(0,a.C_)(["fas",{"fa-chevron-down":w.configCollapsed,"fa-chevron-up":!w.configCollapsed}])},null,2)])]),w.configCollapsed?(0,s.kq)("",!0):((0,s.wg)(),(0,s.iD)("div",$e,[((0,s.wg)(!0),(0,s.iD)(s.HY,null,(0,s.Ko)(D.computedConfig,(t=>((0,s.wg)(),(0,s.j4)(Be,{key:t.id,value:t,onInput:n=>e.$emit("input",t)},null,8,["value","onInput"])))),128))]))])):(0,s.kq)("",!0)])),_:1},8,["visible","title"])):(0,s.kq)("",!0)}var Oe=n(3493),Ue=n(657),je=n(7833);const Be=e=>((0,s.dD)("data-v-3344f2bf"),e=e(),(0,s.Cn)(),e),We=Be((()=>(0,s._)("i",{class:"fas fa-pen-to-square"},null,-1))),Ne=[We];function Le(e,t,n,a,i,l){return(0,s.wg)(),(0,s.iD)("button",{class:"edit-btn",onClick:t[0]||(t[0]=e=>l.proxy(e)),onTouch:t[1]||(t[1]=e=>l.proxy(e)),onInput:t[2]||(t[2]=e=>l.proxy(e))},Ne,32)}var Me={emits:["input","click","touch"],methods:{proxy(e){this.$emit(e.type,e)}}},Fe=n(3744);const Ae=(0,Fe.Z)(Me,[["render",Le],["__scopeId","data-v-3344f2bf"]]);var He=Ae,Ze=n(4967);const Pe=e=>((0,s.dD)("data-v-600cb1a8"),e=e(),(0,s.Cn)(),e),ze=["disabled"],Te=Pe((()=>(0,s._)("button",{type:"submit"},[(0,s._)("i",{class:"fas fa-circle-check"})],-1))),Ve=Pe((()=>(0,s._)("i",{class:"fas fa-ban"},null,-1))),Re=[Ve];function Ke(e,t,n,a,l,o){return(0,s.wg)(),(0,s.iD)("form",{onSubmit:t[3]||(t[3]=(0,i.iM)(((...e)=>o.submit&&o.submit(...e)),["prevent"])),class:"name-editor"},[(0,s.wy)((0,s._)("input",{type:"text","onUpdate:modelValue":t[0]||(t[0]=e=>l.text=e),disabled:n.disabled,ref:"input"},null,8,ze),[[i.nr,l.text]]),Te,(0,s._)("button",{class:"cancel",onClick:t[1]||(t[1]=t=>e.$emit("cancel")),onTouch:t[2]||(t[2]=t=>e.$emit("cancel"))},Re,32),(0,s.WI)(e.$slots,"default",{},void 0,!0)],32)}var Ye={emits:["input","cancel"],props:{value:{type:String},disabled:{type:Boolean,default:!1}},data(){return{text:null}},methods:{proxy(e){this.$emit(e.type,e)},submit(){return this.$emit("input",this.text),!1}},mounted(){this.text=this.value,this.$refs.input.focus()}};const Qe=(0,Fe.Z)(Ye,[["render",Ke],["__scopeId","data-v-600cb1a8"]]);var Xe=Qe,Ge=n(8637),Je=n(4558),et=n(7369);const tt=["created_at","data","description","external_id","external_url","id","image_url","is_configuration","meta","name","plugin","updated_at","parent_id"];var nt={name:"EntityModal",components:{Entity:Je["default"],EntityIcon:Ze["default"],Modal:Oe.Z,EditButton:He,NameEditor:Xe,Icon:Ue.Z,ConfirmDialog:je.Z},mixins:[Ge.Z],emits:["input","loading","entity-update"],props:{entity:{type:Object,required:!0},parent:{type:Object},children:{type:Object},visible:{type:Boolean,default:!1},configValues:{type:Object,default:()=>{}}},computed:{computedConfig(){return Object.values(this.configValues).sort(((e,t)=>(e.name||"").localeCompare(t.name||"")))}},data(){return{loading:!1,editName:!1,editIcon:!1,configCollapsed:!0,childrenCollapsed:!0,extraInfoCollapsed:!0,specialFields:tt}},methods:{async onRename(e){this.loading=!0;try{const t={};t[this.entity.id]=e,await this.request("entities.rename",t)}finally{this.loading=!1,this.editName=!1}},async onDelete(){this.loading=!0;try{await this.request("entities.delete",[this.entity.id])}finally{this.loading=!1}},async onIconEdit(e){this.loading=!0;try{const t={url:null,class:null};e?.length?e.startsWith("http")?t.url=e:t.class=e:(t.url=(et[this.entity.type]||{})?.icon?.url,t.class=(et[this.entity.type]||{})?.icon?.["class"]);const n={};n[this.entity.id]={icon:t},await this.request("entities.set_meta",n)}finally{this.loading=!1,this.editIcon=!1}},async onIconColorEdit(e){this.loading=!0;try{const t=this.entity.meta?.icon||{};t.color=e?e.target.value:null;const n={};n[this.entity.id]={icon:t},await this.request("entities.set_meta",n)}finally{this.loading=!1,this.editIcon=!1}},stringify(e){return null==e?"":Array.isArray(e)||"object"===typeof e?JSON.stringify(e,null,2):""+e}}};const st=(0,Fe.Z)(nt,[["render",qe],["__scopeId","data-v-6fce01a8"]]);var at=st},7243:function(e,t,n){var s={"./Accelerometer":[6362,9,3826,6362],"./Accelerometer.vue":[6362,9,3826,6362],"./Alarm":[472,9,7651,2844,6016,735,58,1807,9381,472],"./Alarm.vue":[472,9,7651,2844,6016,735,58,1807,9381,472],"./Alarm/AlarmEditor":[9381,9,7651,2844,6016,735,58,1807,9381],"./Alarm/AlarmEditor.vue":[9381,9,7651,2844,6016,735,58,1807,9381],"./Assistant":[3211,9,2844,182,3211],"./Assistant.vue":[3211,9,2844,182,3211],"./Battery":[7590,9,7590],"./Battery.vue":[7590,9,7590],"./BinarySensor":[8621,9,2844,8621],"./BinarySensor.vue":[8621,9,2844,8621],"./BluetoothDevice":[3835,9,2844,3835],"./BluetoothDevice.vue":[3835,9,2844,3835],"./BluetoothService":[984,9,2844,984],"./BluetoothService.vue":[984,9,2844,984],"./Button":[2893,9,3826,2893],"./Button.vue":[2893,9,3826,2893],"./CloudInstance":[8769,9,8769],"./CloudInstance.vue":[8769,9,8769],"./CompositeSensor":[6362,9,3826,6362],"./CompositeSensor.vue":[6362,9,3826,6362],"./ContactSensor":[8621,9,2844,8621],"./ContactSensor.vue":[8621,9,2844,8621],"./Cpu":[2460,9,2460],"./Cpu.vue":[2460,9,2460],"./CpuInfo":[3369,9,3369],"./CpuInfo.vue":[3369,9,3369],"./CpuStats":[8769,9,8769],"./CpuStats.vue":[8769,9,8769],"./CpuTimes":[2217,9,2217],"./CpuTimes.vue":[2217,9,2217],"./CurrentSensor":[6362,9,3826,6362],"./CurrentSensor.vue":[6362,9,3826,6362],"./Device":[8769,9,8769],"./Device.vue":[8769,9,8769],"./DewPointSensor":[6362,9,3826,6362],"./DewPointSensor.vue":[6362,9,3826,6362],"./Dimmer":[9461,9,7651,9461],"./Dimmer.vue":[9461,9,7651,9461],"./Disk":[8825,9,8825],"./Disk.vue":[8825,9,8825],"./DistanceSensor":[6362,9,3826,6362],"./DistanceSensor.vue":[6362,9,3826,6362],"./EnergySensor":[6362,9,3826,6362],"./EnergySensor.vue":[6362,9,3826,6362],"./Entity":[4558,9],"./Entity.vue":[4558,9],"./EntityIcon":[4967,9],"./EntityIcon.vue":[4967,9],"./EntityMixin":[847,9],"./EntityMixin.vue":[847,9],"./EnumSensor":[2893,9,3826,2893],"./EnumSensor.vue":[2893,9,3826,2893],"./EnumSwitch":[3368,9,3368],"./EnumSwitch.vue":[3368,9,3368],"./HeartRateSensor":[6362,9,3826,6362],"./HeartRateSensor.vue":[6362,9,3826,6362],"./HumiditySensor":[6362,9,3826,6362],"./HumiditySensor.vue":[6362,9,3826,6362],"./IlluminanceSensor":[6362,9,3826,6362],"./IlluminanceSensor.vue":[6362,9,3826,6362],"./Index":[7878,9,669,2154,7878],"./Index.vue":[7878,9,669,2154,7878],"./Light":[980,9,7651,2844,980],"./Light.vue":[980,9,7651,2844,980],"./LinkQuality":[3559,9,3559],"./LinkQuality.vue":[3559,9,3559],"./Magnetometer":[6362,9,3826,6362],"./Magnetometer.vue":[6362,9,3826,6362],"./MemoryStats":[5329,9,5329],"./MemoryStats.vue":[5329,9,5329],"./Modal":[1999,9],"./Modal.vue":[1999,9],"./MotionSensor":[6362,9,3826,6362],"./MotionSensor.vue":[6362,9,3826,6362],"./Muted":[8391,9,2844,8391],"./Muted.vue":[8391,9,2844,8391],"./NetworkInterface":[457,9,729],"./NetworkInterface.vue":[457,9,729],"./NumericSensor":[6362,9,3826,6362],"./NumericSensor.vue":[6362,9,3826,6362],"./PercentSensor":[169,9,169],"./PercentSensor.vue":[169,9,169],"./PingHost":[1706,9,1706],"./PingHost.vue":[1706,9,1706],"./PowerSensor":[6362,9,3826,6362],"./PowerSensor.vue":[6362,9,3826,6362],"./PresenceSensor":[8621,9,2844,8621],"./PresenceSensor.vue":[8621,9,2844,8621],"./PressureSensor":[6362,9,3826,6362],"./PressureSensor.vue":[6362,9,3826,6362],"./RawSensor":[6362,9,3826,6362],"./RawSensor.vue":[6362,9,3826,6362],"./Selector":[667,9,2154,667],"./Selector.vue":[667,9,2154,667],"./Sensor":[6362,9,3826,6362],"./Sensor.vue":[6362,9,3826,6362],"./StepsSensor":[6362,9,3826,6362],"./StepsSensor.vue":[6362,9,3826,6362],"./SwapStats":[5329,9,5329],"./SwapStats.vue":[5329,9,5329],"./Switch":[8391,9,2844,8391],"./Switch.vue":[8391,9,2844,8391],"./SystemBattery":[7590,9,7590],"./SystemBattery.vue":[7590,9,7590],"./SystemFan":[6362,9,3826,6362],"./SystemFan.vue":[6362,9,3826,6362],"./SystemTemperature":[6362,9,3826,6362],"./SystemTemperature.vue":[6362,9,3826,6362],"./TemperatureSensor":[6362,9,3826,6362],"./TemperatureSensor.vue":[6362,9,3826,6362],"./ThreeAxisSensor":[6362,9,3826,6362],"./ThreeAxisSensor.vue":[6362,9,3826,6362],"./TimeDuration":[6362,9,3826,6362],"./TimeDuration.vue":[6362,9,3826,6362],"./Variable":[6324,9,6324],"./Variable.vue":[6324,9,6324],"./VariableModal":[2106,9,669,2106],"./VariableModal.vue":[2106,9,669,2106],"./VoltageSensor":[6362,9,3826,6362],"./VoltageSensor.vue":[6362,9,3826,6362],"./Volume":[9461,9,7651,9461],"./Volume.vue":[9461,9,7651,9461],"./Weather":[8930,9,5906,8989,8930],"./Weather.vue":[8930,9,5906,8989,8930],"./WeatherForecast":[8498,9,5906,8989,8498],"./WeatherForecast.vue":[8498,9,5906,8989,8498],"./WeatherIcon":[3322,9,5906,3322],"./WeatherIcon.vue":[3322,9,5906,3322],"./WeightSensor":[6362,9,3826,6362],"./WeightSensor.vue":[6362,9,3826,6362],"./common.scss":[65,9,6561,65],"./meta":[7369,3],"./meta.json":[7369,3],"./vars.scss":[5207,9,6561,5207]};function a(e){if(!n.o(s,e))return Promise.resolve().then((function(){var t=new Error("Cannot find module '"+e+"'");throw t.code="MODULE_NOT_FOUND",t}));var t=s[e],a=t[0];return Promise.all(t.slice(2).map(n.e)).then((function(){return n.t(a,16|t[1])}))}a.keys=function(){return Object.keys(s)},a.id=7243,e.exports=a},7369:function(e){"use strict";e.exports=JSON.parse('{"alarm":{"name":"Alarm","name_plural":"Alarms","icon":{"class":"fas fa-stopwatch"}},"assistant":{"name":"Assistant","name_plural":"Assistants","icon":{"class":"fas fa-microphone-lines"}},"battery":{"name":"Battery","name_plural":"Batteries","icon":{"class":"fas fa-battery-full"}},"weather":{"name":"Weather","name_plural":"Weather","icon":{"class":"fas fa-cloud-sun-rain"}},"weather_forecast":{"name":"Weather Forecast","name_plural":"Weather Forecast","icon":{"class":"fas fa-cloud-sun-rain"}},"button":{"name":"Button","name_plural":"Buttons","icon":{"class":"fas fa-circle-dot"}},"cpu_info":{"name":"System","name_plural":"System","icon":{"class":"fas fa-circle-info"}},"cpu_stats":{"name":"System","name_plural":"System","icon":{"class":"fas fa-gauge"}},"cpu_times":{"name":"System","name_plural":"System","icon":{"class":"fas fa-clock"}},"memory_stats":{"name":"System","name_plural":"System","icon":{"class":"fas fa-memory"}},"swap_stats":{"name":"System","name_plural":"System","icon":{"class":"fas fa-memory"}},"disk":{"name":"System","name_plural":"System","icon":{"class":"fas fa-hard-drive"}},"network_interface":{"name":"System","name_plural":"System","icon":{"class":"fas fa-ethernet"}},"system_temperature":{"name":"System","name_plural":"System","icon":{"class":"fas fa-temperature-half"}},"system_fan":{"name":"System","name_plural":"System","icon":{"class":"fas fa-fan"}},"system_battery":{"name":"System","name_plural":"System","icon":{"class":"fas fa-battery-full"}},"current_sensor":{"name":"Sensor","name_plural":"Sensors","icon":{"class":"fas fa-bolt"}},"cpu":{"name":"System","name_plural":"System","icon":{"class":"fas fa-microchip"}},"motion_sensor":{"name":"Sensor","name_plural":"Sensors","icon":{"class":"fas fa-person-running"}},"distance_sensor":{"name":"Sensor","name_plural":"Sensors","icon":{"class":"fas fa-ruler-horizontal"}},"bluetooth_device":{"name":"Device","name_plural":"Devices","icon":{"class":"fab fa-bluetooth-b"}},"cloud_instance":{"name":"Cloud Entity","name_plural":"Cloud Entities","icon":{"class":"fas fa-cloud"}},"bluetooth_service":{"name":"Service","name_plural":"Services","icon":{"class":"fas fa-satellite-dish"}},"accelerometer":{"name":"Sensor","name_plural":"Sensors","icon":{"class":"fas fa-up-down-left-right"}},"magnetometer":{"name":"Sensor","name_plural":"Sensors","icon":{"class":"fas fa-magnet"}},"device":{"name":"Device","name_plural":"Devices","icon":{"class":"fas fa-gear"}},"volume":{"name":"Dimmer","name_plural":"Dimmers","icon":{"class":"fas fa-volume-high"}},"dimmer":{"name":"Dimmer","name_plural":"Dimmers","icon":{"class":"fas fa-gauge"}},"energy_sensor":{"name":"Sensor","name_plural":"Sensors","icon":{"class":"fas fa-plug"}},"entity":{"name":"Entity","name_plural":"Entities","icon":{"class":"fas fa-circle-question"}},"humidity_sensor":{"name":"Sensor","name_plural":"Sensors","icon":{"class":"fas fa-droplet"}},"dew_point_sensor":{"name":"Sensor","name_plural":"Sensors","icon":{"class":"fas fa-hand-holding-droplet"}},"illuminance_sensor":{"name":"Sensor","name_plural":"Sensors","icon":{"class":"fas fa-sun"}},"light":{"name":"Light","name_plural":"Lights","icon":{"class":"fas fa-lightbulb"}},"contact_sensor":{"name":"Sensor","name_plural":"Sensors","icon":{"class":"far fa-hand"}},"presence_sensor":{"name":"Sensor","name_plural":"Sensors","icon":{"class":"fas fa-person"}},"weight_sensor":{"name":"Sensor","name_plural":"Sensors","icon":{"class":"fas fa-weight-scale"}},"link_quality":{"name":"Link Quality","name_plural":"Link Qualities","icon":{"class":"fas fa-tower-broadcast"}},"power_sensor":{"name":"Sensor","name_plural":"Sensors","icon":{"class":"fas fa-plug"}},"temperature_sensor":{"name":"Sensor","name_plural":"Sensors","icon":{"class":"fas fa-temperature-half"}},"steps_sensor":{"name":"Sensor","name_plural":"Sensors","icon":{"class":"fas fa-shoe-prints"}},"heart_rate_sensor":{"name":"Sensor","name_plural":"Sensors","icon":{"class":"fas fa-heart-pulse"}},"ping_host":{"name":"Host","name_plural":"Hosts","icon":{"class":"fas fa-server"}},"time_duration_sensor":{"name":"Sensor","name_plural":"Sensors","icon":{"class":"fas fa-clock"}},"pressure_sensor":{"name":"Sensor","name_plural":"Sensors","icon":{"class":"fas fa-gauge"}},"muted":{"name":"Switch","name_plural":"Switches","icon":{"class":"fas fa-volume-xmark"}},"enum_switch":{"name":"Switch","name_plural":"Switches","icon":{"class":"fas fa-gauge"}},"switch":{"name":"Switch","name_plural":"Switches","icon":{"class":"fas fa-toggle-on"}},"variable":{"name":"Variable","name_plural":"Variables","icon":{"class":"fas fa-square-root-variable"}},"voltage_sensor":{"name":"Sensor","name_plural":"Sensors","icon":{"class":"fas fa-car-battery"}},"composite_sensor":{"name":"Sensor","name_plural":"Sensors","icon":{"class":"fas fa-thermometer"}},"binary_sensor":{"name":"Sensor","name_plural":"Sensors","icon":{"class":"fas fa-thermometer"}},"numeric_sensor":{"name":"Sensor","name_plural":"Sensors","icon":{"class":"fas fa-thermometer"}},"percent_sensor":{"name":"Sensor","name_plural":"Sensors","icon":{"class":"fas fa-thermometer"}},"enum_sensor":{"name":"Sensor","name_plural":"Sensors","icon":{"class":"fas fa-thermometer"}},"raw_sensor":{"name":"Sensor","name_plural":"Sensors","icon":{"class":"fas fa-thermometer"}},"sensor":{"name":"Sensor","name_plural":"Sensors","icon":{"class":"fas fa-thermometer"}}}')}}]);
//# sourceMappingURL=8224.fd608bb1.js.map