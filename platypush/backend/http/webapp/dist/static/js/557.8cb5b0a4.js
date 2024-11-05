"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[557,9164,2106],{557:function(e,t,s){s.r(t),s.d(t,{default:function(){return T}});var i=s(6252),a=s(3577);const n={class:"row plugin entities-container"},l={class:"groups-canvas"},r={key:2,class:"groups-container"},o={class:"frame"},c={class:"header"},u={class:"section left"},d={class:"section center"},p=["textContent"],h={class:"section right"},m={key:0,class:"body"};function f(e,t,s,f,g,y){const v=(0,i.up)("Loading"),b=(0,i.up)("Selector"),w=(0,i.up)("EntityModal"),E=(0,i.up)("VariableModal"),_=(0,i.up)("NoItems"),G=(0,i.up)("Icon"),I=(0,i.up)("DropdownItem"),k=(0,i.up)("Dropdown"),x=(0,i.up)("Entity");return(0,i.wg)(),(0,i.iD)("div",n,[g.loading?((0,i.wg)(),(0,i.j4)(v,{key:0})):(0,i.kq)("",!0),(0,i._)("header",null,[(0,i.Wm)(b,{"entity-groups":g.entityGroups,value:g.selector,onInput:t[0]||(t[0]=e=>g.selector=e),onRefresh:y.refresh,onShowVariableModal:t[1]||(t[1]=e=>g.variableModalVisible=!0)},null,8,["entity-groups","value","onRefresh"])]),(0,i._)("div",l,[g.modalEntityId&&g.entities[g.modalEntityId]?((0,i.wg)(),(0,i.j4)(w,{key:0,entity:g.entities[g.modalEntityId],parent:g.entities[g.entities[g.modalEntityId].parent_id],children:y.childrenByParentId(g.modalEntityId),visible:g.modalVisible,"config-values":y.configValuesByParentId(g.modalEntityId),onClose:y.onEntityModal,onEntityUpdate:t[2]||(t[2]=e=>g.modalEntityId=e)},null,8,["entity","parent","children","visible","config-values","onClose"])):(0,i.kq)("",!0),(0,i.Wm)(E,{visible:g.variableModalVisible,onClose:t[3]||(t[3]=e=>g.variableModalVisible=!1)},null,8,["visible"]),Object.keys(y.displayGroups||{})?.length?((0,i.wg)(),(0,i.iD)("div",r,[((0,i.wg)(!0),(0,i.iD)(i.HY,null,(0,i.Ko)(y.displayGroups,(e=>((0,i.wg)(),(0,i.iD)("div",{class:"group fade-in",key:e.name,ref_for:!0,ref:`group-${e.name}`},[(0,i._)("div",o,[(0,i._)("div",c,[(0,i._)("span",u,["category"===g.selector.grouping&&y.entitiesMeta[y.typesByCategory[e.name]]?((0,i.wg)(),(0,i.j4)(G,(0,i.dG)({key:0,ref_for:!0},y.entitiesMeta[y.typesByCategory[e.name]].icon||{}),null,16)):"plugin"===g.selector.grouping&&y.pluginIcons[e.name]?((0,i.wg)(),(0,i.j4)(G,{key:1,class:(0,a.C_)(y.pluginIcons[e.name]?.class),url:y.pluginIcons[e.name]?.imgUrl},null,8,["class","url"])):(0,i.kq)("",!0)]),(0,i._)("span",d,[(0,i._)("div",{class:"title",textContent:(0,a.zw)(e.name)},null,8,p)]),(0,i._)("span",h,[(0,i.Wm)(k,{title:"Actions","icon-class":"fa fa-ellipsis-h"},{default:(0,i.w5)((()=>[(0,i.Wm)(I,{text:"Refresh","icon-class":"fa fa-sync-alt",onInput:t=>y.refresh(e)},null,8,["onInput"]),(0,i.Wm)(I,{text:"Hide","icon-class":"fa fa-eye-slash",onInput:t=>y.hideGroup(e)},null,8,["onInput"]),g.collapsedGroups[e.name]?((0,i.wg)(),(0,i.j4)(I,{key:1,text:"Expand","icon-class":"fa fa-caret-down",onInput:t=>g.collapsedGroups[e.name]=!1},null,8,["onInput"])):((0,i.wg)(),(0,i.j4)(I,{key:0,text:"Collapse","icon-class":"fa fa-caret-up",onInput:t=>g.collapsedGroups[e.name]=!0},null,8,["onInput"]))])),_:2},1024)])]),g.collapsedGroups[e.name]?(0,i.kq)("",!0):((0,i.wg)(),(0,i.iD)("div",m,[((0,i.wg)(!0),(0,i.iD)(i.HY,null,(0,i.Ko)(Object.values(e.entities).sort(((e,t)=>e.name.localeCompare(t.name))),(e=>((0,i.wg)(),(0,i.iD)("div",{class:"entity-frame",key:e.id},[e.parent_id?(0,i.kq)("",!0):((0,i.wg)(),(0,i.j4)(x,{value:e,children:y.childrenByParentId(e.id),"all-entities":g.entities,onShowModal:t[4]||(t[4]=e=>y.onEntityModal(e)),onInput:t=>y.onEntityInput(e),error:!!g.errorEntities[e.id],key:e.id,loading:!!g.loadingEntities[e.id],onLoading:t=>g.loadingEntities[e.id]=t},null,8,["value","children","all-entities","onInput","error","loading","onLoading"]))])))),128))]))])])))),128))])):((0,i.wg)(),(0,i.j4)(_,{key:1},{default:(0,i.w5)((()=>[(0,i.Uk)("No entities found")])),_:1}))])])}var g=s(8637),y=s(4642),v=s(7597),b=s(6791),w=s(657),E=s(3222),_=s(4558),G=s(9164),I=s(6365),k=s(2106),x=s(5250),V=s(1359),j=s(7369),C={name:"Entities",mixins:[g.Z],components:{Dropdown:y.Z,DropdownItem:v.Z,Entity:_["default"],EntityModal:I["default"],Icon:w.Z,Loading:b.Z,NoItems:E.Z,Selector:G["default"],VariableModal:k["default"]},props:{entityScanTimeout:{type:Number,default:30}},data(){return{loading:!1,loadingEntities:{},errorEntities:{},entityTimeouts:{},entities:{},entityGroups:{id:{},category:{},plugin:{},type:{}},modalEntityId:null,modalVisible:!1,variableModalVisible:!1,selector:{grouping:"plugin",selectedEntities:{},selectedGroups:{}},collapsedGroups:{}}},computed:{entitiesMeta(){return j},pluginIcons(){return V},typesByCategory(){return Object.entries(j).reduce(((e,[t,s])=>(e[s.name_plural]=t,e)),{})},displayGroups(){return Object.entries(this.entityGroups[this.selector.grouping]).filter((e=>this.selector.selectedGroups[e[0]])).map((([e,t])=>({name:e,entities:Object.values(t).filter((e=>e.id in this.selector.selectedEntities))}))).filter((e=>e.entities?.length>0)).sort(((e,t)=>e.name.localeCompare(t.name)))}},methods:{addEntity(e){this.entities[e.id]=e,null==e.parent_id&&["id","type","category","plugin"].forEach((t=>{null!=e[t]&&("id"==t?this.entityGroups[t][e[t]]=e:(this.entityGroups[t][e[t]]||(this.entityGroups[t][e[t]]={}),this.entityGroups[t][e[t]][e.id]=e))}))},removeEntity(e){null==e.parent_id&&(["id","type","category","plugin"].forEach((t=>{this.entityGroups[t][e[t]][e.id]&&delete this.entityGroups[t][e[t]][e.id]})),this.entities[e.id]&&delete this.entities[e.id])},_shouldSkipLoading(e){const t=Object.values(this.childrenByParentId(e.id)),s=t.filter((e=>!e.is_configuration&&!e.is_write_only&&!e.is_query_disabled)).length>0;return e.is_query_disabled||e.is_write_only||t.length&&!s},hideGroup(e){Object.keys(e.entities).forEach((e=>{this.selector.selectedEntities[e]&&delete this.selector.selectedEntities[e]})),delete this.selector.selectedGroups[e.name]},async refresh(e,t=!0){const s=(e?e.entities:this.entities)||{},i={};e&&(i.plugins=Object.values(s).reduce(((e,t)=>(e[t.plugin]=!0,e)),{})),t&&(this.loadingEntities=Object.values(s).reduce(((e,t)=>{if(this._shouldSkipLoading(t))return e;const s=this,i=t.id;return this.entityTimeouts[i]&&clearTimeout(this.entityTimeouts[i]),this.addEntity(t),this.entityTimeouts[i]=setTimeout((()=>{s.loadingEntities[i]&&delete s.loadingEntities[i],s.entityTimeouts[i]&&delete s.entityTimeouts[i],s.errorEntities[i]=t,console.warn(`Scan timeout for ${t.name}`)}),1e3*this.entityScanTimeout),e[i]=!0,e}),{})),this.request("entities.scan",i)},async sync(e=!0){e&&(this.loading=!0);try{this.entities=(await this.request("entities.get")).reduce(((e,t)=>(t.name=t?.meta?.name_override||t.name,t.category=j[t.type].name_plural,t.meta={...j[t.type]||{},...t.meta||{}},e[t.id]=t,this.addEntity(t),e)),{}),this.selector.selectedEntities=this.entityGroups.id,this.refreshEntitiesCache()}finally{e&&(this.loading=!1)}},childrenByParentId(e,t){const s=this.entities?.[e];return s?.children_ids?.length?s.children_ids.reduce(((e,s)=>{const i=this.entities[s];return i&&(!t&&!i.is_configuration||t&&i.is_configuration)&&(e[s]=this.entities[s]),e}),{}):{}},configValuesByParentId(e){return this.childrenByParentId(e,!0)},clearEntityTimeouts(e){this.errorEntities[e]&&delete this.errorEntities[e],this.loadingEntities[e]&&delete this.loadingEntities[e],this.entityTimeouts[e]&&(clearTimeout(this.entityTimeouts[e]),delete this.entityTimeouts[e])},onEntityInput(e){e.category=j[e.type].name_plural,this.entities[e.id]=e,this.clearEntityTimeouts(e.id),this.loadingEntities[e.id]&&delete this.loadingEntities[e.id]},onEntityUpdate(e){const t=e.entity.id;if(null==t)return;this.clearEntityTimeouts(t);const s={...e.entity};null==e.entity?.state&&(s.state=this.entities[t]?.state),s.meta?.name_override?.length?s.name=s.meta.name_override:this.entities[t]?.meta?.name_override?.length?s.name=this.entities[t].meta.name_override:s.name=e.entity?.name||this.entities[t]?.name,s.category=j[s.type].name_plural,s.meta={...j[e.entity.type]||{},...this.entities[t]?.meta||{},...e.entity?.meta||{}},this.addEntity(s),x.$.publishEntity(s)},onEntityDelete(e){const t=e.entity?.id;null!=t&&(t===this.modalEntityId&&(this.modalEntityId=null),this.entities[t]&&this.removeEntity(this.entities[t]))},onEntityModal(e){e?(this.modalEntityId=e,this.modalVisible=!0):(this.modalEntityId=null,this.modalVisible=!1)},onModalOpen(e){const t=this.getParentGroup(e.$el);t&&(t.style.zIndex=""+(parseInt(t.style.zIndex||0)+1))},onModalClose(e){const t=this.getParentGroup(e.$el);t&&(t.style.zIndex=""+Math.max(0,parseInt(t.style.zIndex||0)-1))},getParentGroup(e){let t=e;while(t&&!t.classList?.contains("group"))t=t.parentElement;return t},loadCachedEntities(){const e=window.localStorage.getItem("entities");if(e){try{if(this.entities=JSON.parse(e),!this.entities)throw Error("The list of cached entities is null")}catch(t){return console.warning("Could not parse cached entities",t),!1}return Object.values(this.entities).forEach((e=>this.onEntityUpdate({entity:e}))),this.selector.selectedEntities=this.entityGroups.id,!0}return!1},refreshEntitiesCache(){this.loading||window.localStorage.setItem("entities",JSON.stringify(this.entities))}},async mounted(){this.subscribe(this.onEntityUpdate,"on-entity-update","platypush.message.event.entities.EntityUpdateEvent"),this.subscribe(this.onEntityDelete,"on-entity-delete","platypush.message.event.entities.EntityDeleteEvent"),x.$.on("modal-open",this.onModalOpen),x.$.on("modal-close",this.onModalClose);const e=this.loadCachedEntities();await this.sync(!e),await this.refresh(null,!e),setInterval((()=>this.refreshEntitiesCache()),1e4)},unmounted(){this.unsubscribe("on-entity-update")}},O=s(3744);const M=(0,O.Z)(C,[["render",f],["__scopeId","data-v-5b7876c8"]]);var T=M},9164:function(e,t,s){s.r(t),s.d(t,{default:function(){return v}});var i=s(6252),a=s(9963);const n={class:"entities-selectors-container"},l={key:0,class:"selector search-container col-11"},r={class:"selector actions-container col-1 pull-right"};function o(e,t,s,o,c,u){const d=(0,i.up)("DropdownItem"),p=(0,i.up)("Dropdown");return(0,i.wg)(),(0,i.iD)("div",n,[Object.keys(s.entityGroups.id||{}).length?((0,i.wg)(),(0,i.iD)("div",l,[(0,i.wy)((0,i._)("input",{ref:"search",type:"text",class:"search-bar",title:"Filter by name, plugin or ID",placeholder:"🔎","onUpdate:modelValue":t[0]||(t[0]=e=>c.searchTerm=e)},null,512),[[a.nr,c.searchTerm]])])):(0,i.kq)("",!0),(0,i._)("div",r,[(0,i.Wm)(p,{title:"Actions","icon-class":"fas fa-ellipsis"},{default:(0,i.w5)((()=>[(0,i.Wm)(d,{"icon-class":"fas fa-sync-alt",text:"Refresh",onInput:t[1]||(t[1]=t=>e.$emit("refresh"))}),(0,i.Wm)(d,{"icon-class":"fas fa-square-root-variable",text:"Set Variable",onInput:t[2]||(t[2]=t=>e.$emit("show-variable-modal"))}),(0,i.Wm)(p,{title:"Group by",text:"Group by","icon-class":"fas fa-object-ungroup",ref:"groupingSelector"},{default:(0,i.w5)((()=>[((0,i.wg)(!0),(0,i.iD)(i.HY,null,(0,i.Ko)(u.visibleGroupings,(e=>((0,i.wg)(),(0,i.j4)(d,{key:e,text:u.prettifyGroupingName(e),"item-class":{selected:s.value?.grouping===e},onInput:t=>u.onGroupingChanged(e)},null,8,["text","item-class","onInput"])))),128))])),_:1},512),(0,i.Wm)(p,{title:"Filter groups",text:"Filter groups","icon-class":{fas:!0,"fa-filter":!0,active:u.hasActiveFilter},ref:"groupSelector","keep-open-on-item-click":""},{default:(0,i.w5)((()=>[((0,i.wg)(!0),(0,i.iD)(i.HY,null,(0,i.Ko)(u.sortedGroups,(e=>((0,i.wg)(),(0,i.j4)(d,(0,i.dG)({key:e,text:e,ref_for:!0},u.iconForGroup(e),{"item-class":{selected:!!c.selectedGroups[e]},onClick:(0,a.iM)((t=>u.toggleGroup(e)),["stop"])}),null,16,["text","item-class","onClick"])))),128))])),_:1},8,["icon-class"])])),_:1})])])}var c=s(8637),u=s(4642),d=s(7597),p=s(7369),h=s(1359),m=s(5250),f={name:"Selector",emits:["input","refresh","show-variable-modal"],mixins:[c.Z],components:{Dropdown:u.Z,DropdownItem:d.Z},props:{entityGroups:{type:Object,required:!0},value:{type:Object,required:!0}},data(){return{selectedGroups:{},searchTerm:""}},computed:{visibleGroupings(){return Object.keys(this.entityGroups).filter((e=>"id"!==e))},hasActiveFilter(){return Object.values(this.selectedGroups).filter((e=>!1===e)).length>0},sortedGroups(){return Object.keys(this.entityGroups[this.value?.grouping]||{}).sort()},typesMeta(){return p},isGroupFilterActive(){return Object.keys(this.selectedGroups).length!==this.sortedGroups.length},selectedEntities(){if(!this.searchTerm?.length)return this.entityGroups.id;const e=this.searchTerm.toLowerCase().trim();return Object.values(this.entityGroups.id).filter((t=>{if(!this.selectedGroups[t[this.value?.grouping]])return!1;if(!e?.length)return!0;for(const s of["id","external_id","name","plugin"]){if(!t[s])continue;const i=t[s].toString().toLowerCase();if(i.indexOf(e)>=0)return!0}return!1})).reduce(((e,t)=>(e[t.id]=t,e)),{})}},methods:{prettifyGroupingName(e){return e?(e=this.prettify(e),e.endsWith("y")&&(e=e.slice(0,e.length-1)+"ie"),e+="s",e):""},iconForGroup(e){if("plugin"===this.value.grouping&&h[e]){const t=h[e];return{"icon-class":t["class"]?.length||!t.imgUrl?.length?t["class"]:"fas fa-gears","icon-url":t.imgUrl}}return{}},sync(){const e={...this.value};e.searchTerm=this.searchTerm,e.selectedEntities=this.selectedEntities,e.selectedGroups=this.selectedGroups,this.$emit("input",e)},refreshGroupFilter(){this.selectedGroups=Object.keys(this.entityGroups[this.value?.grouping]||{}).reduce(((e,t)=>(e[t]=!0,e)),{}),this.sync()},toggleGroup(e){this.selectedGroups[e]=!this.selectedGroups[e],this.sync()},processEntityUpdate(e){const t=e[this.value?.grouping];t&&null==this.selectedGroups[t]&&(this.selectedGroups[t]=!0)},onGroupingChanged(e){if(!this.entityGroups[e]||e===this.value?.grouping)return!1;const t={...this.value};t.grouping=e,this.$emit("input",t)}},mounted(){this.refreshGroupFilter(),this.$watch((()=>this.value?.grouping),(()=>{this.refreshGroupFilter()})),this.$watch((()=>this.searchTerm),this.sync),m.$.onEntity(this.processEntityUpdate)}},g=s(3744);const y=(0,g.Z)(f,[["render",o],["__scopeId","data-v-d41c8404"]]);var v=y},2106:function(e,t,s){s.r(t),s.d(t,{default:function(){return k}});var i=s(6252),a=s(9963);const n=e=>((0,i.dD)("data-v-4e3d4a40"),e=e(),(0,i.Cn)(),e),l={class:"variable-modal-container"},r={class:"row"},o=n((()=>(0,i._)("div",{class:"col-s-12 col-m-4 label"},[(0,i._)("label",{for:"name"},"Variable Name")],-1))),c={class:"col-s-12 col-m-8 value"},u=["disabled"],d={class:"row"},p=n((()=>(0,i._)("div",{class:"col-s-12 col-m-4 label"},[(0,i._)("label",{for:"name"},"Variable Value")],-1))),h={class:"col-s-12 col-m-8 value"},m=["disabled"],f={class:"row button-container"},g=["disabled"],y=n((()=>(0,i._)("i",{class:"fas fa-check"},null,-1))),v=[y];function b(e,t,s,n,y,b){const w=(0,i.up)("Modal");return(0,i.wg)(),(0,i.j4)(w,{visible:s.visible,title:"Set Variable",ref:"modal",onOpen:b.onOpen,onClose:t[3]||(t[3]=t=>e.$emit("close",t))},{default:(0,i.w5)((()=>[(0,i._)("div",l,[(0,i._)("form",{onSubmit:t[2]||(t[2]=(0,a.iM)(((...e)=>b.setValue&&b.setValue(...e)),["prevent"]))},[(0,i._)("div",r,[o,(0,i._)("div",c,[(0,i.wy)((0,i._)("input",{type:"text",id:"variable-name","onUpdate:modelValue":t[0]||(t[0]=e=>y.varName=e),placeholder:"Variable Name",disabled:y.loading,ref:"varName"},null,8,u),[[a.nr,y.varName]])])]),(0,i._)("div",d,[p,(0,i._)("div",h,[(0,i.wy)((0,i._)("input",{type:"text",id:"variable-value","onUpdate:modelValue":t[1]||(t[1]=e=>y.varValue=e),ref:"varValue",placeholder:"Variable Value",disabled:y.loading},null,8,m),[[a.nr,y.varValue]])])]),(0,i._)("div",f,[(0,i._)("button",{type:"submit",title:"Set",disabled:y.loading},v,8,g)])],32)])])),_:1},8,["visible","onOpen"])}var w=s(2918),E=s(8637),_={name:"VariableModal",components:{Modal:w.Z},mixins:[E.Z],emits:["close"],props:{visible:{type:Boolean,default:!1}},data(){return{loading:!1,varName:null,varValue:null}},methods:{async clearValue(){this.loading=!0;try{await this.request("variable.unset",{name:this.varName.trim()})}finally{this.loading=!1}},async setValue(){const e=this.varName.trim();e?.length||this.notifyWarning("No variable name has been specified");const t=this.varValue;if(t?.length){this.loading=!0;try{const s={};s[e]=t,await this.request("variable.set",s)}finally{this.loading=!1}}else await this.clearValue();this.$refs.varName.value="",this.$refs.varValue.value="",this.$refs.modal.close()},onOpen(){this.$nextTick((()=>{this.$refs.varName.focus()}))}}},G=s(3744);const I=(0,G.Z)(_,[["render",b],["__scopeId","data-v-4e3d4a40"]]);var k=I},1359:function(e){e.exports=JSON.parse('{"alarm":{"class":"fas fa-stopwatch"},"arduino":{"class":"fas fa-microchip"},"assistant.google":{"class":"fas fa-microphone-lines"},"assistant.openai":{"class":"fas fa-microphone-lines"},"assistant.picovoice":{"class":"fas fa-microphone-lines"},"bluetooth":{"class":"fab fa-bluetooth"},"camera.android.ipcam":{"class":"fab fa-android"},"camera.cv":{"class":"fas fa-camera"},"camera.ffmpeg":{"class":"fas fa-camera"},"camera.gstreamer":{"class":"fas fa-camera"},"camera.ir.mlx90640":{"class":"fas fa-sun"},"camera.pi":{"class":"fas fa-camera"},"camera.pi.legacy":{"class":"fas fa-camera"},"entities":{"class":"fa fa-home"},"execute":{"class":"fa fa-play"},"file":{"class":"fas fa-folder"},"extensions":{"class":"fas fa-puzzle-piece"},"light.hue":{"class":"fas fa-lightbulb"},"linode":{"class":"fas fa-cloud"},"media.chromecast":{"class":"fab fa-chromecast"},"media.jellyfin":{"imgUrl":"/icons/jellyfin.svg"},"media.kodi":{"imgUrl":"/icons/kodi.svg"},"media.mplayer":{"class":"fa fa-film"},"media.mpv":{"class":"fa fa-film"},"media.plex":{"imgUrl":"/icons/plex.svg"},"media.vlc":{"class":"fa fa-film"},"music.mpd":{"class":"fas fa-music"},"music.snapcast":{"class":"fa fa-volume-up"},"music.spotify":{"class":"fab fa-spotify"},"ping":{"class":"fas fa-server"},"procedures":{"class":"fas fa-gears"},"torrent":{"class":"fa fa-magnet"},"rtorrent":{"class":"fa fa-magnet"},"sensor.bme280":{"class":"fas fa-microchip"},"sensor.dht":{"class":"fas fa-microchip"},"sensor.envirophat":{"class":"fas fa-microchip"},"sensor.ltr559":{"class":"fas fa-microchip"},"sensor.mcp3008":{"class":"fas fa-microchip"},"sensor.pmw3901":{"class":"fas fa-microchip"},"sensor.vl53l1x":{"class":"fas fa-microchip"},"serial":{"class":"fab fa-usb"},"smartthings":{"imgUrl":"/icons/smartthings.png"},"switches":{"class":"fas fa-toggle-on"},"switch.switchbot":{"class":"fas fa-toggle-on"},"switch.tplink":{"class":"fas fa-toggle-on"},"switchbot":{"class":"fas fa-toggle-on"},"sound":{"class":"fa fa-microphone"},"system":{"class":"fas fa-microchip"},"tts":{"class":"far fa-comment"},"tts.google":{"class":"fas fa-comment"},"tv.samsung.ws":{"class":"fas fa-tv"},"variable":{"class":"fas fa-square-root-variable"},"weather.buienradar":{"class":"fas fa-cloud-sun-rain"},"weather.openweathermap":{"class":"fas fa-cloud-sun-rain"},"zigbee.mqtt":{"imgUrl":"/icons/zigbee.svg"},"zwave":{"imgUrl":"/icons/z-wave.png"},"zwave.mqtt":{"imgUrl":"/icons/z-wave.png"}}')}}]);
//# sourceMappingURL=557.8cb5b0a4.js.map