(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[6692],{6692:function(t,e,i){"use strict";i.r(e),i.d(e,{default:function(){return c}});var n=i(6252),s=i(3577);function a(t,e,i,a,o,l){return(0,n.wg)(),(0,n.iD)("div",{class:(0,s.C_)(["row item entity-container",{blink:o.justUpdated}])},[((0,n.wg)(),(0,n.j4)((0,n.LL)(o.component),{value:t.value,loading:t.loading,error:t.error||0==t.value?.reachable,onInput:e[0]||(e[0]=e=>t.$emit("input",e)),onLoading:e[1]||(e[1]=e=>t.$emit("loading",e))},null,8,["value","loading","error"]))],2)}var o=i(7909),l={name:"Entity",mixins:[o["default"]],emits:["input","loading"],data(){return{component:null,justUpdated:!1}},methods:{valuesEqual(t,e){return t={...t},e={...e},delete t.updated_at,delete e.updated_at,this.objectsEqual(t,e)}},mounted(){if("Entity"!==this.type){const t=this.type.split("_").map((t=>t[0].toUpperCase()+t.slice(1))).join("");this.$watch((()=>this.value),((t,e)=>{if(this.valuesEqual(e,t))return!1;this.justUpdated=!0;const i=this;setTimeout((()=>i.justUpdated=!1),1e3)})),this.component=(0,n.RC)((()=>i(7243)(`./${t}`)))}}},r=i(3744);const u=(0,r.Z)(l,[["render",a],["__scopeId","data-v-5ec27be3"]]);var c=u},7909:function(t,e,i){"use strict";i.r(e),i.d(e,{default:function(){return o}});var n=i(6813),s={name:"EntityMixin",mixins:[n.Z],emits:["input"],props:{loading:{type:Boolean,default:!1},error:{type:Boolean,default:!1},value:{type:Object,required:!0}},data(){return{modalVisible:!1}},computed:{type(){let t=this.value.type||"";return t.split("_").map((t=>t.charAt(0).toUpperCase()+t.slice(1))).join("")}}};const a=s;var o=a},5993:function(t,e,i){"use strict";i.r(e),i.d(e,{default:function(){return W}});var n=i(6252),s=i(3577);const a=t=>((0,n.dD)("data-v-0f6918ce"),t=t(),(0,n.Cn)(),t),o={class:"row plugin entities-container"},l={class:"col-11 left"},r={class:"col-1 right"},u=a((()=>(0,n._)("i",{class:"fa fa-sync-alt"},null,-1))),c=[u],d={class:"groups-canvas"},p=(0,n.Uk)("No entities found"),m={key:2,class:"groups-container"},y={class:"frame"},h={class:"header"},g={class:"section left"},f={class:"section center"},v=["textContent"],_={class:"section right"},w=["onClick"],b=a((()=>(0,n._)("i",{class:"fa fa-sync-alt"},null,-1))),E=[b],k={class:"body"},C=["onClick"];function S(t,e,i,a,u,b){const S=(0,n.up)("Loading"),I=(0,n.up)("Selector"),x=(0,n.up)("EntityModal"),D=(0,n.up)("NoItems"),G=(0,n.up)("Icon"),T=(0,n.up)("Entity");return(0,n.wg)(),(0,n.iD)("div",o,[u.loading?((0,n.wg)(),(0,n.j4)(S,{key:0})):(0,n.kq)("",!0),(0,n._)("header",null,[(0,n._)("div",l,[(0,n.Wm)(I,{"entity-groups":b.entityGroups,value:u.selector,onInput:e[0]||(e[0]=t=>u.selector=t)},null,8,["entity-groups","value"])]),(0,n._)("div",r,[(0,n._)("button",{title:"Refresh",onClick:e[1]||(e[1]=t=>b.refresh(null))},c)])]),(0,n._)("div",d,[u.modalEntityId?((0,n.wg)(),(0,n.j4)(x,{key:0,entity:u.entities[u.modalEntityId],visible:u.modalVisible,onClose:e[2]||(e[2]=t=>b.onEntityModal(null))},null,8,["entity","visible"])):(0,n.kq)("",!0),Object.keys(b.displayGroups||{})?.length?((0,n.wg)(),(0,n.iD)("div",m,[((0,n.wg)(!0),(0,n.iD)(n.HY,null,(0,n.Ko)(b.displayGroups,(t=>((0,n.wg)(),(0,n.iD)("div",{class:"group fade-in",key:t.name},[(0,n._)("div",y,[(0,n._)("div",h,[(0,n._)("span",g,["category"===u.selector.grouping&&b.entitiesMeta[b.typesByCategory[t.name]]?((0,n.wg)(),(0,n.j4)(G,(0,s.vs)((0,n.dG)({key:0},b.entitiesMeta[b.typesByCategory[t.name]].icon||{})),null,16)):"plugin"===u.selector.grouping&&b.pluginIcons[t.name]?((0,n.wg)(),(0,n.j4)(G,{key:1,class:(0,s.C_)(b.pluginIcons[t.name]?.class),url:b.pluginIcons[t.name]?.imgUrl},null,8,["class","url"])):(0,n.kq)("",!0)]),(0,n._)("span",f,[(0,n._)("div",{class:"title",textContent:(0,s.zw)(t.name)},null,8,v)]),(0,n._)("span",_,[(0,n._)("button",{title:"Refresh",onClick:e=>b.refresh(t)},E,8,w)])]),(0,n._)("div",k,[((0,n.wg)(!0),(0,n.iD)(n.HY,null,(0,n.Ko)(t.entities,(t=>((0,n.wg)(),(0,n.iD)("div",{class:"entity-frame",onClick:e=>b.onEntityModal(t.id),key:t.id},[(0,n.Wm)(T,{value:t,onInput:b.onEntityInput,error:!!u.errorEntities[t.id],loading:!!u.loadingEntities[t.id],onLoading:e=>u.loadingEntities[t.id]=e},null,8,["value","onInput","error","loading","onLoading"])],8,C)))),128))])])])))),128))])):((0,n.wg)(),(0,n.j4)(D,{key:1},{default:(0,n.w5)((()=>[p])),_:1}))])])}var I=i(6813),x=i(1232),D=i(1478);const G={class:"no-items-container"},T={class:"no-items fade-in"};function j(t,e,i,s,a,o){return(0,n.wg)(),(0,n.iD)("div",G,[(0,n._)("div",T,[(0,n.WI)(t.$slots,"default",{},void 0,!0)])])}var q={name:"NoItems"},O=i(3744);const U=(0,O.Z)(q,[["render",j],["__scopeId","data-v-6fec32b5"]]);var $=U,M=i(6692),N=i(6382),L=i(6243),Z=i(1359),z=i(7369),B={name:"Entities",components:{Loading:x.Z,Icon:D.Z,Entity:M["default"],Selector:N["default"],NoItems:$,EntityModal:L["default"]},mixins:[I.Z],props:{entityScanTimeout:{type:Number,default:30}},data(){return{loading:!1,loadingEntities:{},errorEntities:{},entityTimeouts:{},entities:{},modalEntityId:null,modalVisible:!1,selector:{grouping:"category",selectedEntities:{}}}},computed:{entitiesMeta(){return z},pluginIcons(){return Z},entityTypes(){return this.groupEntities("type")},typesByCategory(){return Object.entries(z).reduce(((t,[e,i])=>(t[i.name_plural]=e,t)),{})},entityGroups(){return{id:Object.entries(this.groupEntities("id")).reduce(((t,[e,i])=>(t[e]=i[0],t)),{}),category:this.groupEntities("category"),plugin:this.groupEntities("plugin")}},displayGroups(){return Object.entries(this.entityGroups[this.selector.grouping]).filter((t=>t[1].filter((t=>!!this.selector.selectedEntities[t.id])).length>0)).sort(((t,e)=>t[0].localeCompare(e[0]))).map((([t,e])=>({name:t,entities:e.filter((t=>t.id in this.selector.selectedEntities))})))}},methods:{groupEntities(t){return Object.values(this.entities).reduce(((e,i)=>{const n=e[i[t]]||{};return n[i.id]=i,e[i[t]]=Object.values(n).sort(((t,e)=>t.name.localeCompare(e.name))),e}),{})},async refresh(t){const e=(t?t.entities:this.entities)||{},i={};t&&(i.plugins=Object.keys(e.reduce(((t,e)=>(t[e.plugin]=!0,t)),{}))),this.loadingEntities=Object.values(e).reduce(((t,e)=>{if(e.is_query_disabled||e.is_write_only)return t;const i=this,n=e.id;return this.entityTimeouts[n]&&clearTimeout(this.entityTimeouts[n]),this.entityTimeouts[n]=setTimeout((()=>{i.loadingEntities[n]&&delete i.loadingEntities[n],i.entityTimeouts[n]&&delete i.entityTimeouts[n],i.errorEntities[n]=e,console.warn(`Scan timeout for ${e.name}`)}),1e3*this.entityScanTimeout),t[n]=!0,t}),{}),await this.request("entities.scan",i)},async sync(){this.loading=!0;try{this.entities=(await this.request("entities.get")).reduce(((t,e)=>(e.name=e?.meta?.name_override||e.name,e.category=z[e.type].name_plural,e.meta={...z[e.type]||{},...e.meta||{}},t[e.id]=e,t)),{}),this.selector.selectedEntities=this.entityGroups.id}finally{this.loading=!1}},clearEntityTimeouts(t){this.errorEntities[t]&&delete this.errorEntities[t],this.loadingEntities[t]&&delete this.loadingEntities[t],this.entityTimeouts[t]&&(clearTimeout(this.entityTimeouts[t]),delete this.entityTimeouts[t])},onEntityInput(t){t.category=z[t.type].name_plural,this.entities[t.id]=t,this.clearEntityTimeouts(t.id),this.loadingEntities[t.id]&&delete this.loadingEntities[t.id]},onEntityUpdate(t){const e=t.entity.id;if(null==e)return;this.clearEntityTimeouts(e);const i={...t.entity};null==t.entity?.state&&(i.state=this.entities[e]?.state),i.meta?.name_override?.length?i.name=i.meta.name_override:this.entities[e]?.meta?.name_override?.length?i.name=this.entities[e].meta.name_override:i.name=t.entity?.name||this.entities[e]?.name,i.category=z[i.type].name_plural,i.meta={...z[t.entity.type]||{},...this.entities[e]?.meta||{},...t.entity?.meta||{}},this.entities[e]=i},onEntityDelete(t){const e=t.entity?.id;null!=e&&(e===this.modalEntityId&&(this.modalEntityId=null),this.entities[e]&&delete this.entities[e])},onEntityModal(t){t?(this.modalEntityId=t,this.modalVisible=!0):(this.modalEntityId=null,this.modalVisible=!1)}},async mounted(){this.subscribe(this.onEntityUpdate,"on-entity-update","platypush.message.event.entities.EntityUpdateEvent"),this.subscribe(this.onEntityDelete,"on-entity-delete","platypush.message.event.entities.EntityDeleteEvent"),await this.sync(),await this.refresh()}};const F=(0,O.Z)(B,[["render",S],["__scopeId","data-v-0f6918ce"]]);var W=F},6243:function(t,e,i){"use strict";i.r(e),i.d(e,{default:function(){return Zt}});var n=i(6252),s=i(3577);const a=t=>((0,n.dD)("data-v-628ff73f"),t=t(),(0,n.Cn)(),t),o=(0,n.Uk)(" Are you "),l=a((()=>(0,n._)("b",null,"sure",-1))),r=(0,n.Uk)(" that you want to delete this entity? "),u=a((()=>(0,n._)("br",null,null,-1))),c=a((()=>(0,n._)("br",null,null,-1))),d=(0,n.Uk)(" Note: you should only delete an entity if its plugin has been disabled or the entity is no longer reachable."),p=a((()=>(0,n._)("br",null,null,-1))),m=a((()=>(0,n._)("br",null,null,-1))),y=(0,n.Uk)(" Otherwise, the entity will simply be created again upon the next scan. "),h={class:"table-row"},g={class:"title"},f=(0,n.Uk)(" Name "),v={class:"value"},_=["textContent"],w={class:"table-row"},b={class:"title"},E=(0,n.Uk)(" Icon "),k={class:"value icon-canvas"},C={key:0,class:"icon-editor"},S=a((()=>(0,n._)("i",{class:"fas fa-rotate-left"},null,-1))),I=[S],x=a((()=>(0,n._)("span",{class:"help"},[(0,n.Uk)(" Supported: image URLs or "),(0,n._)("a",{href:"https://fontawesome.com/icons",target:"_blank"},"FontAwesome icon classes"),(0,n.Uk)(". ")],-1))),D={class:"table-row"},G=a((()=>(0,n._)("div",{class:"title"}," Icon color ",-1))),T={class:"value icon-color-picker"},j=["value"],q=a((()=>(0,n._)("i",{class:"fas fa-rotate-left"},null,-1))),O=[q],U={class:"table-row"},$=a((()=>(0,n._)("div",{class:"title"},"Plugin",-1))),M=["textContent"],N={class:"table-row"},L=a((()=>(0,n._)("div",{class:"title"},"Internal ID",-1))),Z=["textContent"],z={key:0,class:"table-row"},B=a((()=>(0,n._)("div",{class:"title"},"External ID",-1))),F=["textContent"],W={key:1,class:"table-row"},R=a((()=>(0,n._)("div",{class:"title"},"Description",-1))),V=["textContent"],H={key:0,class:"table-row"},K=["textContent"],A=["textContent"],P={key:2,class:"table-row"},Y=a((()=>(0,n._)("div",{class:"title"},"Created at",-1))),Q=["textContent"],J={key:3,class:"table-row"},X=a((()=>(0,n._)("div",{class:"title"},"Updated at",-1))),tt=["textContent"],et={class:"table-row delete-entity-container"},it=a((()=>(0,n._)("div",{class:"title"},"Delete Entity",-1))),nt={class:"value"},st=a((()=>(0,n._)("i",{class:"fas fa-trash"},null,-1))),at=[st];function ot(t,e,i,a,S,q){const st=(0,n.up)("ConfirmDialog"),ot=(0,n.up)("EditButton"),lt=(0,n.up)("NameEditor"),rt=(0,n.up)("Icon"),ut=(0,n.up)("Modal",!0);return(0,n.wg)(),(0,n.j4)(ut,{visible:i.visible,class:"entity-modal",title:i.entity.name||i.entity.external_id},{default:(0,n.w5)((()=>[(0,n.Wm)(st,{ref:"deleteConfirmDiag",title:"Confirm entity deletion",onInput:q.onDelete},{default:(0,n.w5)((()=>[o,l,r,u,c,d,p,m,y])),_:1},8,["onInput"]),(0,n._)("div",h,[(0,n._)("div",g,[f,S.editName?(0,n.kq)("",!0):((0,n.wg)(),(0,n.j4)(ot,{key:0,onClick:e[0]||(e[0]=t=>S.editName=!0)}))]),(0,n._)("div",v,[S.editName?((0,n.wg)(),(0,n.j4)(lt,{key:0,value:i.entity.name,onInput:q.onRename,onCancel:e[1]||(e[1]=t=>S.editName=!1),disabled:S.loading},null,8,["value","onInput","disabled"])):((0,n.wg)(),(0,n.iD)("span",{key:1,textContent:(0,s.zw)(i.entity.name)},null,8,_))])]),(0,n._)("div",w,[(0,n._)("div",b,[E,S.editIcon?(0,n.kq)("",!0):((0,n.wg)(),(0,n.j4)(ot,{key:0,onClick:e[2]||(e[2]=t=>S.editIcon=!0)}))]),(0,n._)("div",k,[S.editIcon?((0,n.wg)(),(0,n.iD)("span",C,[(0,n.Wm)(lt,{value:i.entity.meta?.icon?.class||i.entity.meta?.icon?.url,onInput:q.onIconEdit,onCancel:e[5]||(e[5]=t=>S.editIcon=!1),disabled:S.loading},{default:(0,n.w5)((()=>[(0,n._)("button",{type:"button",title:"Reset",onClick:e[3]||(e[3]=t=>q.onIconEdit(null)),onTouch:e[4]||(e[4]=t=>q.onIconEdit(null))},I,32)])),_:1},8,["value","onInput","disabled"]),x])):((0,n.wg)(),(0,n.j4)(rt,(0,s.vs)((0,n.dG)({key:1},i.entity?.meta?.icon||{})),null,16))])]),(0,n._)("div",D,[G,(0,n._)("div",T,[(0,n._)("input",{type:"color",value:i.entity.meta?.icon?.color,onChange:e[6]||(e[6]=(...t)=>q.onIconColorEdit&&q.onIconColorEdit(...t))},null,40,j),(0,n._)("button",{type:"button",title:"Reset",onClick:e[7]||(e[7]=t=>q.onIconColorEdit(null)),onTouch:e[8]||(e[8]=t=>q.onIconColorEdit(null))},O,32)])]),(0,n._)("div",U,[$,(0,n._)("div",{class:"value",textContent:(0,s.zw)(i.entity.plugin)},null,8,M)]),(0,n._)("div",N,[L,(0,n._)("div",{class:"value",textContent:(0,s.zw)(i.entity.id)},null,8,Z)]),i.entity.external_id?((0,n.wg)(),(0,n.iD)("div",z,[B,(0,n._)("div",{class:"value",textContent:(0,s.zw)(i.entity.external_id)},null,8,F)])):(0,n.kq)("",!0),i.entity.description?((0,n.wg)(),(0,n.iD)("div",W,[R,(0,n._)("div",{class:"value",textContent:(0,s.zw)(i.entity.description)},null,8,V)])):(0,n.kq)("",!0),((0,n.wg)(!0),(0,n.iD)(n.HY,null,(0,n.Ko)(i.entity.data||{},((e,i)=>((0,n.wg)(),(0,n.iD)("div",{key:i},[null!=e?((0,n.wg)(),(0,n.iD)("div",H,[(0,n._)("div",{class:"title",textContent:(0,s.zw)(t.prettify(i))},null,8,K),(0,n._)("div",{class:"value",textContent:(0,s.zw)(""+e)},null,8,A)])):(0,n.kq)("",!0)])))),128)),i.entity.created_at?((0,n.wg)(),(0,n.iD)("div",P,[Y,(0,n._)("div",{class:"value",textContent:(0,s.zw)(t.formatDateTime(i.entity.created_at))},null,8,Q)])):(0,n.kq)("",!0),i.entity.updated_at?((0,n.wg)(),(0,n.iD)("div",J,[X,(0,n._)("div",{class:"value",textContent:(0,s.zw)(t.formatDateTime(i.entity.updated_at))},null,8,tt)])):(0,n.kq)("",!0),(0,n._)("div",et,[it,(0,n._)("div",nt,[(0,n._)("button",{onClick:e[9]||(e[9]=e=>t.$refs.deleteConfirmDiag.show())},at)])])])),_:1},8,["visible","title"])}var lt=i(8453),rt=i(1478),ut=i(9963);const ct=t=>((0,n.dD)("data-v-d543b3e4"),t=t(),(0,n.Cn)(),t),dt={class:"dialog-content"},pt=ct((()=>(0,n._)("i",{class:"fas fa-check"},null,-1))),mt=ct((()=>(0,n._)("i",{class:"fas fa-xmark"},null,-1)));function yt(t,e,i,a,o,l){const r=(0,n.up)("Modal");return(0,n.wg)(),(0,n.j4)(r,{ref:"modal",title:i.title},{default:(0,n.w5)((()=>[(0,n._)("div",dt,[(0,n.WI)(t.$slots,"default",{},void 0,!0)]),(0,n._)("form",{class:"buttons",onSubmit:e[4]||(e[4]=(0,ut.iM)(((...t)=>l.onConfirm&&l.onConfirm(...t)),["prevent"]))},[(0,n._)("button",{type:"submit",class:"ok-btn",onClick:e[0]||(e[0]=(...t)=>l.onConfirm&&l.onConfirm(...t)),onTouch:e[1]||(e[1]=(...t)=>l.onConfirm&&l.onConfirm(...t))},[pt,(0,n.Uk)("   "+(0,s.zw)(i.confirmText),1)],32),(0,n._)("button",{type:"button",class:"cancel-btn",onClick:e[2]||(e[2]=(...t)=>l.close&&l.close(...t)),onTouch:e[3]||(e[3]=(...t)=>l.close&&l.close(...t))},[mt,(0,n.Uk)("   "+(0,s.zw)(i.cancelText),1)],32)],32)])),_:3},8,["title"])}var ht={emits:["input","click","touch"],components:{Modal:lt.Z},props:{title:{type:String},confirmText:{type:String,default:"OK"},cancelText:{type:String,default:"Cancel"}},methods:{onConfirm(){this.$emit("input"),this.close()},show(){this.$refs.modal.show()},close(){this.$refs.modal.hide()}}},gt=i(3744);const ft=(0,gt.Z)(ht,[["render",yt],["__scopeId","data-v-d543b3e4"]]);var vt=ft;const _t=t=>((0,n.dD)("data-v-3344f2bf"),t=t(),(0,n.Cn)(),t),wt=_t((()=>(0,n._)("i",{class:"fas fa-pen-to-square"},null,-1))),bt=[wt];function Et(t,e,i,s,a,o){return(0,n.wg)(),(0,n.iD)("button",{class:"edit-btn",onClick:e[0]||(e[0]=t=>o.proxy(t)),onTouch:e[1]||(e[1]=t=>o.proxy(t)),onInput:e[2]||(e[2]=t=>o.proxy(t))},bt,32)}var kt={emits:["input","click","touch"],methods:{proxy(t){this.$emit(t.type,t)}}};const Ct=(0,gt.Z)(kt,[["render",Et],["__scopeId","data-v-3344f2bf"]]);var St=Ct;const It=t=>((0,n.dD)("data-v-1405d90f"),t=t(),(0,n.Cn)(),t),xt=["disabled"],Dt=It((()=>(0,n._)("button",{type:"submit"},[(0,n._)("i",{class:"fas fa-circle-check"})],-1))),Gt=It((()=>(0,n._)("i",{class:"fas fa-ban"},null,-1))),Tt=[Gt];function jt(t,e,i,s,a,o){return(0,n.wg)(),(0,n.iD)("form",{onSubmit:e[3]||(e[3]=(0,ut.iM)(((...t)=>o.submit&&o.submit(...t)),["prevent"])),class:"name-editor"},[(0,n.wy)((0,n._)("input",{type:"text","onUpdate:modelValue":e[0]||(e[0]=t=>a.text=t),disabled:i.disabled},null,8,xt),[[ut.nr,a.text]]),Dt,(0,n._)("button",{class:"cancel",onClick:e[1]||(e[1]=e=>t.$emit("cancel")),onTouch:e[2]||(e[2]=e=>t.$emit("cancel"))},Tt,32),(0,n.WI)(t.$slots,"default",{},void 0,!0)],32)}var qt={emits:["input","cancel"],props:{value:{type:String},disabled:{type:Boolean,deafult:!1}},data(){return{text:null}},methods:{proxy(t){this.$emit(t.type,t)},submit(){return this.$emit("input",this.text),!1}},mounted(){this.text=this.value}};const Ot=(0,gt.Z)(qt,[["render",jt],["__scopeId","data-v-1405d90f"]]);var Ut=Ot,$t=i(6813),Mt=i(7369),Nt={name:"Entity",components:{Modal:lt.Z,EditButton:St,NameEditor:Ut,Icon:rt.Z,ConfirmDialog:vt},mixins:[$t.Z],emits:["input","loading"],props:{entity:{type:Object,required:!0},visible:{type:Boolean,default:!1}},data(){return{loading:!1,editName:!1,editIcon:!1}},methods:{async onRename(t){this.loading=!0;try{const e={};e[this.entity.id]=t,await this.request("entities.rename",e)}finally{this.loading=!1,this.editName=!1}},async onDelete(){this.loading=!0;try{await this.request("entities.delete",[this.entity.id])}finally{this.loading=!1}},async onIconEdit(t){this.loading=!0;try{const e={url:null,class:null};t?.length?t.startsWith("http")?e.url=t:e.class=t:(e.url=(Mt[this.entity.type]||{})?.icon?.url,e.class=(Mt[this.entity.type]||{})?.icon?.["class"]);const i={};i[this.entity.id]={icon:e},await this.request("entities.set_meta",i)}finally{this.loading=!1,this.editIcon=!1}},async onIconColorEdit(t){this.loading=!0;try{const e=this.entity.meta?.icon||{};e.color=t?t.target.value:null;const i={};i[this.entity.id]={icon:e},await this.request("entities.set_meta",i)}finally{this.loading=!1,this.editIcon=!1}}}};const Lt=(0,gt.Z)(Nt,[["render",ot],["__scopeId","data-v-628ff73f"]]);var Zt=Lt},6382:function(t,e,i){"use strict";i.r(e),i.d(e,{default:function(){return v}});var n=i(6252),s=i(3577),a=i(9963);const o={class:"entities-selectors-container"},l={class:"selector"},r={key:1,class:"selector"};function u(t,e,i,u,c,d){const p=(0,n.up)("DropdownItem"),m=(0,n.up)("Dropdown");return(0,n.wg)(),(0,n.iD)("div",o,[(0,n._)("div",l,[(0,n.Wm)(m,{title:"Group by","icon-class":"fas fa-eye",ref:"groupingSelector"},{default:(0,n.w5)((()=>[((0,n.wg)(!0),(0,n.iD)(n.HY,null,(0,n.Ko)(d.visibleGroupings,(t=>((0,n.wg)(),(0,n.j4)(p,{key:t,text:d.prettifyGroupingName(t),"item-class":{selected:i.value?.grouping===t},onClick:e=>d.onGroupingChanged(t)},null,8,["text","item-class","onClick"])))),128))])),_:1},512)]),i.value?.grouping?((0,n.wg)(),(0,n.iD)("div",{key:0,class:(0,s.C_)(["selector",{active:d.isGroupFilterActive}])},[(0,n.Wm)(m,{title:"Filter by","icon-class":"fas fa-filter",ref:"groupSelector","keep-open-on-item-click":""},{default:(0,n.w5)((()=>[((0,n.wg)(!0),(0,n.iD)(n.HY,null,(0,n.Ko)(d.sortedGroups,(t=>((0,n.wg)(),(0,n.j4)(p,(0,n.dG)({key:t,text:t},d.iconForGroup(t),{"item-class":{selected:!!c.selectedGroups[t]},onClick:(0,a.iM)((e=>d.toggleGroup(t)),["stop"])}),null,16,["text","item-class","onClick"])))),128))])),_:1},512)],2)):(0,n.kq)("",!0),Object.keys(i.entityGroups.id||{}).length?((0,n.wg)(),(0,n.iD)("div",r,[(0,n.wy)((0,n._)("input",{ref:"search",type:"text",class:"search-bar",placeholder:"🔎","onUpdate:modelValue":e[0]||(e[0]=t=>c.searchTerm=t)},null,512),[[a.nr,c.searchTerm]])])):(0,n.kq)("",!0)])}var c=i(6813),d=i(5771),p=i(9015),m=i(7369),y=i(1359),h={name:"Selector",emits:["input"],mixins:[c.Z],components:{Dropdown:d.Z,DropdownItem:p.Z},props:{entityGroups:{type:Object,required:!0},value:{type:Object,required:!0}},data(){return{selectedGroups:{},searchTerm:""}},computed:{visibleGroupings(){return Object.keys(this.entityGroups).filter((t=>"id"!==t))},sortedGroups(){return Object.keys(this.entityGroups[this.value?.grouping]||{}).sort()},typesMeta(){return m},isGroupFilterActive(){return Object.keys(this.selectedGroups).length!==this.sortedGroups.length},selectedEntities(){return Object.values(this.entityGroups.id).filter((t=>{if(!this.selectedGroups[t[this.value?.grouping]])return!1;if(this.searchTerm?.length){const e=this.searchTerm.toLowerCase();return(t.name||"").toLowerCase().indexOf(e)>=0||(t.plugin||"").toLowerCase().indexOf(e)>=0||(t.external_id||"").toLowerCase().indexOf(e)>=0||(t.id||0).toString()==e}return!0})).reduce(((t,e)=>(t[e.id]=e,t)),{})}},methods:{prettifyGroupingName(t){return t?(t=this.prettify(t),t.endsWith("y")&&(t=t.slice(0,t.length-1)+"ie"),t+="s",t):""},iconForGroup(t){if("plugin"===this.value.grouping&&y[t]){const e=y[t];return{"icon-class":e["class"]?.length||!e.imgUrl?.length?e["class"]:"fas fa-gears","icon-url":e.imgUrl}}return{}},synchronizeSelectedEntities(){const t={...this.value};t.selectedEntities=this.selectedEntities,this.$emit("input",t)},updateSearchTerm(){const t={...this.value};t.searchTerm=this.searchTerm,t.selectedEntities=this.selectedEntities,this.$emit("input",t)},refreshGroupFilter(t){if(t)this.selectedGroups=Object.keys(this.entityGroups[this.value?.grouping]||{}).reduce(((t,e)=>(t[e]=!0,t)),{});else for(const e of Object.keys(this.entityGroups[this.value?.grouping]))null==this.selectedGroups[e]&&(this.selectedGroups[e]=!0);this.synchronizeSelectedEntities()},toggleGroup(t){this.selectedGroups[t]=!this.selectedGroups[t],this.synchronizeSelectedEntities()},onGroupingChanged(t){if(!this.entityGroups[t]||t===this.value?.grouping)return!1;const e={...this.value};e.grouping=t,this.$emit("input",e)}},mounted(){this.refreshGroupFilter(!0),this.$watch((()=>this.value?.grouping),(()=>{this.refreshGroupFilter(!0)})),this.$watch((()=>this.searchTerm),this.updateSearchTerm),this.$watch((()=>this.entityGroups),(()=>{this.refreshGroupFilter(!1)}))}},g=i(3744);const f=(0,g.Z)(h,[["render",u],["__scopeId","data-v-c5a17b82"]]);var v=f},7243:function(t,e,i){var n={"./Battery":[8990,9,6869,8990],"./Battery.vue":[8990,9,6869,8990],"./BinarySensor":[9496,9,3490,6869,9496],"./BinarySensor.vue":[9496,9,3490,6869,9496],"./CurrentSensor":[2072,9,6869,2072],"./CurrentSensor.vue":[2072,9,6869,2072],"./Dimmer":[6365,9,9974,6869,6365],"./Dimmer.vue":[6365,9,9974,6869,6365],"./EnergySensor":[2072,9,6869,2072],"./EnergySensor.vue":[2072,9,6869,2072],"./Entity":[6692,9],"./Entity.vue":[6692,9],"./EntityIcon":[3673,9,6869,3673],"./EntityIcon.vue":[3673,9,6869,3673],"./EntityMixin":[7909,9],"./EntityMixin.vue":[7909,9],"./EnumSwitch":[818,9,6869,818],"./EnumSwitch.vue":[818,9,6869,818],"./HumiditySensor":[2072,9,6869,2072],"./HumiditySensor.vue":[2072,9,6869,2072],"./Index":[5993,9],"./Index.vue":[5993,9],"./Light":[1155,9,3490,9974,6869,1155],"./Light.vue":[1155,9,3490,9974,6869,1155],"./LinkQuality":[2235,9,6869,2235],"./LinkQuality.vue":[2235,9,6869,2235],"./Modal":[6243,9],"./Modal.vue":[6243,9],"./NumericSensor":[2072,9,6869,2072],"./NumericSensor.vue":[2072,9,6869,2072],"./PowerSensor":[2072,9,6869,2072],"./PowerSensor.vue":[2072,9,6869,2072],"./RawSensor":[2072,9,6869,2072],"./RawSensor.vue":[2072,9,6869,2072],"./Selector":[6382,9],"./Selector.vue":[6382,9],"./Sensor":[2072,9,6869,2072],"./Sensor.vue":[2072,9,6869,2072],"./Switch":[4024,9,3490,6869,4024],"./Switch.vue":[4024,9,3490,6869,4024],"./TemperatureSensor":[2072,9,6869,2072],"./TemperatureSensor.vue":[2072,9,6869,2072],"./VoltageSensor":[2072,9,6869,2072],"./VoltageSensor.vue":[2072,9,6869,2072],"./common.scss":[65,9,4981,65],"./meta":[7369,3],"./meta.json":[7369,3],"./vars.scss":[5207,9,4981,5207]};function s(t){if(!i.o(n,t))return Promise.resolve().then((function(){var e=new Error("Cannot find module '"+t+"'");throw e.code="MODULE_NOT_FOUND",e}));var e=n[t],s=e[0];return Promise.all(e.slice(2).map(i.e)).then((function(){return i.t(s,16|e[1])}))}s.keys=function(){return Object.keys(n)},s.id=7243,t.exports=s},7369:function(t){"use strict";t.exports=JSON.parse('{"battery":{"name":"Battery","name_plural":"Batteries","icon":{"class":"fas fa-battery-full"}},"current_sensor":{"name":"Sensor","name_plural":"Sensors","icon":{"class":"fas fa-bolt"}},"device":{"name":"Device","name_plural":"Devices","icon":{"class":"fas fa-gear"}},"dimmer":{"name":"Dimmer","name_plural":"Dimmers","icon":{"class":"fas fa-gauge"}},"energy_sensor":{"name":"Sensor","name_plural":"Sensors","icon":{"class":"fas fa-plug"}},"entity":{"name":"Entity","name_plural":"Entities","icon":{"class":"fas fa-circle-question"}},"humidity_sensor":{"name":"Sensor","name_plural":"Sensors","icon":{"class":"fas fa-droplet"}},"light":{"name":"Light","name_plural":"Lights","icon":{"class":"fas fa-lightbulb"}},"link_quality":{"name":"Link Quality","name_plural":"Link Qualities","icon":{"class":"fas fa-tower-broadcast"}},"power_sensor":{"name":"Sensor","name_plural":"Sensors","icon":{"class":"fas fa-plug"}},"temperature_sensor":{"name":"Sensor","name_plural":"Sensors","icon":{"class":"fas fa-temperature-half"}},"enum_switch":{"name":"Switch","name_plural":"Switches","icon":{"class":"fas fa-gauge"}},"switch":{"name":"Switch","name_plural":"Switches","icon":{"class":"fas fa-toggle-on"}},"voltage_sensor":{"name":"Sensor","name_plural":"Sensors","icon":{"class":"fas fa-car-battery"}},"binary_sensor":{"name":"Sensor","name_plural":"Sensors","icon":{"class":"fas fa-thermometer"}},"numeric_sensor":{"name":"Sensor","name_plural":"Sensors","icon":{"class":"fas fa-thermometer"}},"sensor":{"name":"Sensor","name_plural":"Sensors","icon":{"class":"fas fa-thermometer"}}}')}}]);
//# sourceMappingURL=6692.15999a09.js.map