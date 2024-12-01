"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[6923],{5829:function(e,t,a){a.d(t,{A:function(){return pe}});var s=a(641);const l={class:"procedure-editor-modal-container"};function n(e,t,a,n,o,i){const r=(0,s.g2)("ProcedureEditor"),u=(0,s.g2)("Modal");return(0,s.uX)(),(0,s.CE)("div",l,[(0,s.bF)(u,{title:e.title||e.value.name,visible:e.visible,uppercase:!e.value.name,"before-close":()=>e.$refs.editor?.checkCanClose(),ref:"editorModal",onClose:t[1]||(t[1]=t=>e.$emit("close"))},{default:(0,s.k6)((()=>[(0,s.bF)(r,{procedure:e.value,"read-only":i.isReadOnly,"with-name":!i.isReadOnly,"with-save":!i.isReadOnly,value:e.value,modal:i.isReadOnly?null:()=>e.$refs.editorModal,ref:"editor",onInput:t[0]||(t[0]=t=>e.$emit("input",t))},null,8,["procedure","read-only","with-name","with-save","value","modal"])])),_:1},8,["title","visible","uppercase","before-close"])])}var o=a(9513),i=a(3751),r=a(33);const u={class:"procedure-editor-container"},d={class:"procedure-editor"},c={key:0,class:"name-editor-container"},h={class:"row item"},p={class:"value"},g=["disabled"],m={key:1,class:"icon-editor-container"},f={key:2,class:"args-editor-container"},v={class:"args",ref:"args"},y=["value","disabled","onInput","onBlur"],w={key:0,class:"row item new-arg"},k={class:"actions-container"},A={key:0},C={key:3,class:"response-container"},b={key:0,class:"args-modal-container",ref:"argsModalContainer"},L={class:"arg-name"},E={key:0},x={key:1},V=["value","onInput"],$={class:"arg-value"},_=["onUpdate:modelValue"],I={class:"row item new-arg"},N={class:"arg-name"},O={class:"arg-value"},R={class:"confirm-dialog-container"},F={class:"confirm-dialog-container"},X={class:"floating-buttons"},S={class:"buttons left"},P={class:"buttons right"},M={key:0,class:"duplicate-editor-container"},W={key:1,class:"dump-modal-container"};function D(e,t,a,l,n,o){const D=(0,s.g2)("IconEditor"),B=(0,s.g2)("ActionsList"),Q=(0,s.g2)("Response"),J=(0,s.g2)("FloatingButton"),T=(0,s.g2)("Modal"),U=(0,s.g2)("ConfirmDialog"),q=(0,s.g2)("FloatingButtons"),Y=(0,s.g2)("ProcedureEditor",!0),j=(0,s.g2)("ProcedureDump");return(0,s.uX)(),(0,s.CE)("div",u,[(0,s.Lk)("main",null,[(0,s.Lk)("div",d,[(0,s.Lk)("form",{class:"procedure-edit-form",autocomplete:"off",onSubmit:t[3]||(t[3]=(0,i.D$)(((...e)=>o.executeAction&&o.executeAction(...e)),["prevent"]))},[t[15]||(t[15]=(0,s.Lk)("input",{type:"submit",style:{display:"none"}},null,-1)),a.withName?((0,s.uX)(),(0,s.CE)("div",c,[(0,s.Lk)("div",h,[t[12]||(t[12]=(0,s.Lk)("div",{class:"name"},[(0,s.Lk)("label",null,[(0,s.Lk)("i",{class:"icon fas fa-pen-to-square"}),(0,s.eW)(" Name ")])],-1)),(0,s.Lk)("div",p,[(0,s.bo)((0,s.Lk)("input",{type:"text","onUpdate:modelValue":t[0]||(t[0]=e=>n.newValue.name=e),ref:"nameInput",disabled:a.readOnly},null,8,g),[[i.Jo,n.newValue.name]])])])])):(0,s.Q3)("",!0),Object.keys(n.newValue?.meta?.icon||{}).length?((0,s.uX)(),(0,s.CE)("div",m,[(0,s.bF)(D,{entity:n.newValue,onInput:o.onIconChange,onChange:o.onIconChange},null,8,["entity","onInput","onChange"])])):(0,s.Q3)("",!0),o.showArgs?((0,s.uX)(),(0,s.CE)("div",f,[t[13]||(t[13]=(0,s.Lk)("h3",null,[(0,s.Lk)("i",{class:"icon fas fa-code"}),(0,s.eW)("  Arguments ")],-1)),(0,s.Lk)("div",v,[((0,s.uX)(!0),(0,s.CE)(s.FK,null,(0,s.pI)(n.newValue.args,((e,t)=>((0,s.uX)(),(0,s.CE)("div",{class:"row item",key:t},[(0,s.Lk)("input",{type:"text",placeholder:"Argument Name",value:e,disabled:a.readOnly,onInput:e=>o.onArgInput(e.target.value?.trim(),t),onBlur:a=>o.onArgEdit(e,t)},null,40,y)])))),128)),a.readOnly?(0,s.Q3)("",!0):((0,s.uX)(),(0,s.CE)("div",w,[(0,s.bo)((0,s.Lk)("input",{type:"text",placeholder:"New Argument",ref:"newArgInput","onUpdate:modelValue":t[1]||(t[1]=e=>n.newArg=e),onBlur:t[2]||(t[2]=(...e)=>o.onNewArg&&o.onNewArg(...e))},null,544),[[i.Jo,n.newArg]])]))],512)])):(0,s.Q3)("",!0),(0,s.Lk)("div",k,[o.showArgs?((0,s.uX)(),(0,s.CE)("h3",A,t[14]||(t[14]=[(0,s.Lk)("i",{class:"icon fas fa-play"},null,-1),(0,s.eW)("  Actions ")]))):(0,s.Q3)("",!0),(0,s.bF)(B,{value:n.newValue.actions,context:o.context,"read-only":a.readOnly,onInput:o.onActionsEdit},null,8,["value","context","read-only","onInput"])]),n.response||n.error?((0,s.uX)(),(0,s.CE)("div",C,[(0,s.bF)(Q,{response:n.response,error:n.error},null,8,["response","error"])])):(0,s.Q3)("",!0)],32)]),n.showArgsModal?((0,s.uX)(),(0,s.CE)("div",b,[(0,s.bF)(T,{title:"Run Arguments",visible:!0,ref:"argsModal",onClose:o.onRunArgsModalClose},{default:(0,s.k6)((()=>[(0,s.Lk)("form",{class:"args",onSubmit:t[7]||(t[7]=(0,i.D$)(((...e)=>o.executeWithArgs&&o.executeWithArgs(...e)),["prevent"]))},[((0,s.uX)(!0),(0,s.CE)(s.FK,null,(0,s.pI)(n.runArgs,((e,a)=>((0,s.uX)(),(0,s.CE)("div",{class:"row item",key:a},[(0,s.Lk)("span",L,[n.newValue.args?.includes(a)?((0,s.uX)(),(0,s.CE)("span",E,(0,r.v_)(a),1)):((0,s.uX)(),(0,s.CE)("span",x,[(0,s.Lk)("input",{type:"text",placeholder:"New Argument",value:a,onInput:e=>o.onEditRunArgName(e,a)},null,40,V)])),t[16]||(t[16]=(0,s.Lk)("span",{class:"mobile"},"  =  ",-1))]),(0,s.Lk)("span",$,[t[17]||(t[17]=(0,s.Lk)("span",{class:"from tablet"},"  =  ",-1)),(0,s.bo)((0,s.Lk)("input",{type:"text",placeholder:"Argument Value",ref_for:!0,ref:`run-arg-value-${a}`,"onUpdate:modelValue":e=>n.runArgs[a]=e},null,8,_),[[i.Jo,n.runArgs[a]]])])])))),128)),(0,s.Lk)("div",I,[(0,s.Lk)("span",N,[(0,s.bo)((0,s.Lk)("input",{type:"text",placeholder:"New Argument",ref:"newRunArgName","onUpdate:modelValue":t[4]||(t[4]=e=>n.newRunArg[0]=e),onBlur:t[5]||(t[5]=(...e)=>o.onNewRunArgName&&o.onNewRunArgName(...e))},null,544),[[i.Jo,n.newRunArg[0]]]),t[18]||(t[18]=(0,s.Lk)("span",{class:"mobile"},"  =  ",-1))]),(0,s.Lk)("span",O,[t[19]||(t[19]=(0,s.Lk)("span",{class:"from tablet"},"  =  ",-1)),(0,s.bo)((0,s.Lk)("input",{type:"text",placeholder:"Argument Value","onUpdate:modelValue":t[6]||(t[6]=e=>n.newRunArg[1]=e)},null,512),[[i.Jo,n.newRunArg[1]]])])]),t[20]||(t[20]=(0,s.Lk)("input",{type:"submit",style:{display:"none"}},null,-1)),(0,s.bF)(J,{"icon-class":"fa fa-play",title:"Run Procedure",disabled:0===n.newValue.actions?.length||n.running,onClick:o.executeWithArgs},null,8,["disabled","onClick"])],32)])),_:1},8,["onClose"])],512)):(0,s.Q3)("",!0),(0,s.Lk)("div",R,[(0,s.bF)(U,{ref:"confirmClose",onInput:o.forceClose},{default:(0,s.k6)((()=>t[21]||(t[21]=[(0,s.eW)(" This procedure has unsaved changes. Are you sure you want to close it? ")]))),_:1},8,["onInput"])]),(0,s.Lk)("div",F,[(0,s.bF)(U,{ref:"confirmOverwrite",onInput:o.forceSave},{default:(0,s.k6)((()=>t[22]||(t[22]=[(0,s.eW)(" A procedure with the same name already exists. Do you want to overwrite it? ")]))),_:1},8,["onInput"])]),t[23]||(t[23]=(0,s.Lk)("div",{class:"spacer"},null,-1)),(0,s.Lk)("div",X,[(0,s.Lk)("div",S,[(0,s.bF)(q,{direction:"row"},{default:(0,s.k6)((()=>[(0,s.bF)(J,{"icon-class":"fa fa-code",left:"",glow:"",title:"Export to YAML",onClick:t[8]||(t[8]=e=>n.showYAML=!0)}),n.newValue.name?.length&&n.newValue.actions?.length?((0,s.uX)(),(0,s.Wv)(J,{key:0,"icon-class":"fa fa-copy",left:"",glow:"",title:"Duplicate Procedure",onClick:o.duplicate},null,8,["onClick"])):(0,s.Q3)("",!0)])),_:1})]),(0,s.Lk)("div",P,[(0,s.bF)(q,{direction:"row"},{default:(0,s.k6)((()=>[o.showSave?((0,s.uX)(),(0,s.Wv)(J,{key:0,"icon-class":"fa fa-save",right:"",glow:"",title:"Save Procedure",disabled:!o.canSave,onClick:o.save},null,8,["disabled","onClick"])):(0,s.Q3)("",!0),(0,s.bF)(J,{"icon-class":"fa fa-play",right:"",glow:"",title:"Run Procedure",disabled:0===n.newValue.actions?.length||n.running,onClick:o.executeAction},null,8,["disabled","onClick"])])),_:1})])])]),null!=n.duplicateValue?((0,s.uX)(),(0,s.CE)("div",M,[(0,s.bF)(T,{title:"Duplicate Procedure",ref:"duplicateModal",visible:!0,"before-close":()=>e.$refs.duplicateEditor?.checkCanClose(),onClose:t[10]||(t[10]=e=>n.duplicateValue=null)},{default:(0,s.k6)((()=>[(0,s.bF)(Y,{value:n.duplicateValue,"with-name":!0,"with-save":!0,modal:()=>e.$refs.duplicateModal,ref:"duplicateEditor",onInput:t[9]||(t[9]=e=>n.duplicateValue=null)},null,8,["value","modal"])])),_:1},8,["before-close"])])):(0,s.Q3)("",!0),n.showYAML?((0,s.uX)(),(0,s.CE)("div",W,[(0,s.bF)(T,{title:"Procedure Dump",visible:!0,onClose:t[11]||(t[11]=e=>n.showYAML=!1)},{default:(0,s.k6)((()=>[(0,s.bF)(j,{procedure:n.newValue},null,8,["procedure"])])),_:1})])):(0,s.Q3)("",!0)])}a(4114);var B=a(5707),Q=a(3538),J=a(7998);function T(e,t,a,l,n,o){return(0,s.uX)(),(0,s.CE)("div",{class:(0,r.C4)(["floating-btns",{direction:a.direction}])},[(0,s.RG)(e.$slots,"default")],2)}var U={emits:["click"],props:{direction:{type:String,default:"row"},size:{type:String,default:"4em"}},computed:{buttons(){return this.$el.querySelectorAll(".floating-btn")}},mounted(){const e=Array.from(this.buttons);let t=0;e.forEach(((e,a)=>{const s=e.offsetWidth,l=`calc(${t}px + (${a} * 1em))`;"row"===this.direction?parseFloat(getComputedStyle(e).left)?e.style.right=l:e.style.left=l:parseFloat(getComputedStyle(e).top)?e.style.bottom=l:e.style.top=l,t+=s}))}},q=a(6262);const Y=(0,q.A)(U,[["render",T]]);var j=Y,H=a(4219);const z={class:"procedure-dump"},K={key:1,class:"dump-container"},G=["innerHTML"];function Z(e,t,a,l,n,o){const i=(0,s.g2)("Loading"),r=(0,s.g2)("CopyButton");return(0,s.uX)(),(0,s.CE)("div",z,[n.loading?((0,s.uX)(),(0,s.Wv)(i,{key:0})):((0,s.uX)(),(0,s.CE)("div",K,[(0,s.bF)(r,{text:n.yaml?.trim()},null,8,["text"]),(0,s.Lk)("pre",null,[(0,s.Lk)("code",{innerHTML:o.highlightedYAML},null,8,G)])]))])}a(1545),a(7907);var ee=a(9878),te=a(1087),ae=a(9828),se=a(2002),le={mixins:[se.A],components:{CopyButton:te.A,Loading:ae.A},props:{procedure:{type:Object,required:!0}},data(){return{loading:!1,yaml:null}},computed:{highlightedYAML(){return ee.A.highlight("# You can copy this code in a YAML configuration file\n# if you prefer to store this procedure in a file.\n"+this.yaml||0,{language:"yaml"}).value}},methods:{async refresh(){this.loading=!0;try{this.yaml=await this.request("procedures.to_yaml",{procedure:this.procedure})}finally{this.loading=!1}}},mounted(){this.refresh()}};const ne=(0,q.A)(le,[["render",Z],["__scopeId","data-v-b22aac3c"]]);var oe=ne,ie=a(9954),re={mixins:[se.A],emits:["input"],components:{ActionsList:B["default"],ConfirmDialog:Q.A,FloatingButton:J.A,FloatingButtons:j,IconEditor:H["default"],Modal:o.A,ProcedureDump:oe,Response:ie.A},props:{withName:{type:Boolean,default:!1},withSave:{type:Boolean,default:!1},value:{type:Object,default:()=>({name:void 0,actions:[]})},readOnly:{type:Boolean,default:!1},modal:{type:[Object,Function]}},data(){return{confirmOverwrite:!1,duplicateValue:null,error:void 0,loading:!1,newAction:{},newArg:null,newRunArg:[null,null],newValue:{},response:void 0,running:!1,runArgs:{},shouldForceClose:!1,showArgsModal:!1,showYAML:!1}},computed:{floatingButtons(){return this.$el.querySelector(".floating-btns")},canSave(){return!(!this.withSave||this.readOnly||!this.newValue?.name?.length||!this.newValue?.actions?.length)&&this.valueString!==this.newValueString},valueString(){return JSON.stringify(this.value)},newValueString(){return JSON.stringify(this.newValue)},context(){return this.newValue?.args?.reduce(((e,t)=>(e[t]={source:"args"},e)),{})},modal_(){return this.readOnly?null:"function"===typeof this.modal?this.modal():this.modal},shouldConfirmClose(){return this.canSave&&!this.shouldForceClose},showArgs(){return!this.readOnly||this.newValue.args?.length},showSave(){return this.withSave&&!this.readOnly}},methods:{async save(){if(this.canSave){this.loading=!0;try{const e=await this.overwriteOk();if(!e)return;const t=this.newValue.actions.map((e=>{const t={...e};return"name"in t&&(t.action=t.name,delete t.name),t})),a={...this.newValue,actions:t};this.value?.name?.length&&this.value.name!==this.newValue.name&&(a.old_name=this.value.name),await this.request("procedures.save",a),this.$emit("input",this.newValue),this.notify({text:"Procedure saved successfully",image:{icon:"check"}})}finally{this.loading=!1}}},async forceSave(){this.confirmOverwrite=!0,await this.save()},async overwriteOk(){if(this.confirmOverwrite)return this.confirmOverwrite=!1,!0;const e=await this.request("procedures.status",{publish:!1});return!this.value.name?.length||this.value.name===this.newValue.name||!e[this.newValue.name]||(this.$refs.confirmOverwrite?.open(),!1)},onResponse(e){this.response=("string"===typeof e?e:JSON.stringify(e,null,2)).trim(),this.error=void 0},onError(e){e.message&&(e=e.message),this.response=void 0,this.error=e},onDone(){this.running=!1,this.runArgs={}},async executeAction(){if(this.newValue.actions?.length)if(!this.newValue.args?.length||Object.keys(this.runArgs).length){this.running=!0;try{const e={actions:this.newValue.actions.map((e=>{const t={...e};return"name"in t&&(t.action=t.name,delete t.name),t})),args:this.runArgs},t=await this.request("procedures.exec",{procedure:e});this.onResponse(t)}catch(e){console.error(e),this.onError(e)}finally{this.onDone()}}else this.showArgsModal=!0;else this.notify({text:"No actions to execute",warning:!0,image:{icon:"exclamation-triangle"}})},async executeWithArgs(){this.$refs.argsModal?.close(),Object.entries(this.runArgs).forEach((([e,t])=>{t?.length||(this.runArgs[e]=null);try{this.runArgs[e]=JSON.parse(t)}catch(a){}})),await this.executeAction()},duplicate(){const e=`${this.newValue.name||""}__copy`,t=JSON.parse(JSON.stringify(this.newValue));this.duplicateValue={...t,meta:{...t.meta||{},icon:{...t.meta?.icon||{}}},id:null,external_id:e,name:e}},onActionsEdit(e){this.newValue.actions=e},onArgInput(e,t){this.newValue.args[t]=e},onArgEdit(e,t){e=e?.trim();const a=!!this.newValue.args?.filter(((a,s)=>a===e&&s!==t)).length;if(!e?.length||a)if(this.newValue.args.splice(t,1),t===this.newValue.args.length)setTimeout((()=>this.$refs.newArgInput?.focus()),50);else{const e=this.$refs.args.children[t]?.querySelector("input[type=text]");setTimeout((()=>{e?.focus(),e?.select()}),50)}},onNewArg(e){const t=e.target.value?.trim();t?.length&&(this.newValue.args||(this.newValue.args=[]),this.newValue.args.includes(t)||this.newValue.args.push(t),this.newArg=null,setTimeout((()=>this.$refs.newArgInput?.focus()),50))},onNewRunArgName(){const e=this.newRunArg[0]?.trim(),t=this.newRunArg[1]?.trim();e?.length&&(this.runArgs[e]=t,this.newRunArg=[null,null],this.$nextTick((()=>this.$refs[`run-arg-value-${e}`]?.[0]?.focus())))},onEditRunArgName(e,t){const a=e.target.value?.trim();a!==t&&(a?.length&&(this.runArgs[a]=this.runArgs[t]),delete this.runArgs[t],this.$nextTick((()=>this.$el.querySelector(`.args-modal-container .args input[type=text][value="${a}"]`)?.focus())))},onIconChange(e){this.newValue.meta.icon=e},onRunArgsModalClose(){this.showArgsModal=!1,this.$nextTick((()=>{this.runArgs={}}))},checkCanClose(){return!this.shouldConfirmClose||(this.$refs.confirmClose?.open(),!1)},forceClose(){this.shouldForceClose=!0,this.$nextTick((()=>{if(!this.modal_)return;let e=this.modal_;"function"===typeof e&&(e=e());try{e?.close()}catch(t){console.warn("Failed to close modal",t)}this.reset()}))},beforeUnload(e){this.shouldConfirmClose&&(e.preventDefault(),e.returnValue="")},addBeforeUnload(){window.addEventListener("beforeunload",this.beforeUnload)},removeBeforeUnload(){window.removeEventListener("beforeunload",this.beforeUnload)},reset(){this.removeBeforeUnload()},syncValue(){if(!this.value)return;const e=JSON.parse(JSON.stringify(this.value));this.newValue={...e,actions:e.actions?.map((e=>({...e}))),args:[...e?.args||[]],meta:{...e?.meta||{}}}}},watch:{value:{immediate:!0,deep:!0,handler(){this.syncValue()}},newValue:{deep:!0,handler(e){this.withSave||this.$emit("input",e)}},showArgsModal(e){e&&(this.runArgs=this.newValue.args?.reduce(((e,t)=>(e[t]=null,e)),{}),this.$nextTick((()=>{this.$el.querySelector(".args-modal-container .args input[type=text]")?.focus()})))}},mounted(){this.addBeforeUnload(),this.syncValue(),this.$nextTick((()=>{this.withName&&this.$refs.nameInput?.focus()}))},unmouted(){this.reset()}};const ue=(0,q.A)(re,[["render",D],["__scopeId","data-v-e159c110"]]);var de=ue,ce={mixins:[o.A,de],emits:["close","input"],components:{Modal:o.A,ProcedureEditor:de},data:function(){return{args:{},defaultIconClass:"fas fa-cogs",extraArgs:{},collapsed_:!0,infoCollapsed:!1,lastError:null,lastResponse:null,newArgName:"",newArgValue:"",runCollapsed:!1,showConfirmDelete:!1,showFileEditor:!1,showProcedureEditor:!1}},computed:{isReadOnly(){return this.value.procedure_type&&"db"!==this.value.procedure_type}},methods:{open(){this.$refs.editorModal.open()},close(){this.$refs.editorModal.close()},show(){this.$refs.editorModal.show()},hide(){this.$refs.editorModal.hide()},toggle(){this.$refs.editorModal.toggle()}},watch:{collapsed:{immediate:!0,handler(e){this.collapsed_=e}},selected:{immediate:!0,handler(e){this.collapsed_=e}},showProcedureEditor(e){e||this.$refs.editor?.reset()}},mounted(){this.collapsed_=!this.selected}};const he=(0,q.A)(ce,[["render",n],["__scopeId","data-v-66039a54"]]);var pe=he},6923:function(e,t,a){a.r(t),a.d(t,{default:function(){return ie}});var s=a(641),l=a(33),n=a(3751);const o={class:"entity procedure-container"},i={class:"icon"},r={class:"label"},u=["textContent"],d={class:"value-and-toggler"},c={class:"value"},h=["disabled"],p={class:"run"},g={class:"col-2 buttons"},m=["disabled","title"],f={key:0,class:"run-body"},v={key:0,class:"args"},y=["value"],w=["disabled","onInput"],k={class:"extra args"},A=["value","disabled","onBlur"],C=["value","disabled"],b={class:"row add-arg"},L=["disabled"],E=["disabled"],x={class:"row run-container"},V=["disabled"],$={key:0,class:"response-container"},_={class:"info"},I={class:"col-2 buttons"},N=["disabled","title"],O={key:0,class:"info-body"},R={class:"item"},F={class:"value"},X={class:"item"},S={key:0,class:"item actions"},P={class:"value"},M={class:"item"},W=["disabled"],D={key:0},B={key:1},Q={key:2},J={key:0,class:"item delete"},T=["disabled"],U={key:1,class:"item"},q={class:"value"},Y=["href"],j={key:1,class:"file-editor-container"},H={class:"confirm-delete-container"};function z(e,t,a,z,K,G){const Z=(0,s.g2)("EntityIcon"),ee=(0,s.g2)("Response"),te=(0,s.g2)("IconEditor"),ae=(0,s.g2)("FileEditor"),se=(0,s.g2)("ProcedureEditor"),le=(0,s.g2)("ConfirmDialog");return(0,s.uX)(),(0,s.CE)("div",o,[(0,s.Lk)("div",{class:(0,l.C4)(["head",{collapsed:e.collapsed_}]),onClick:t[2]||(t[2]=(...e)=>G.onHeaderClick&&G.onHeaderClick(...e))},[(0,s.Lk)("div",i,[(0,s.bF)(Z,{entity:e.value,icon:G.icon,loading:e.loading},null,8,["entity","icon","loading"])]),(0,s.Lk)("div",r,[(0,s.Lk)("div",{class:"name",textContent:(0,l.v_)(e.value.name)},null,8,u)]),(0,s.Lk)("div",d,[(0,s.Lk)("div",c,[e.collapsed_?((0,s.uX)(),(0,s.CE)("button",{key:0,class:"btn btn-primary head-run-btn",title:"Run Procedure",disabled:e.loading,onClick:t[0]||(t[0]=(0,n.D$)(((...e)=>G.run&&G.run(...e)),["stop"]))},t[18]||(t[18]=[(0,s.Lk)("i",{class:"fas fa-play"},null,-1)]),8,h)):(0,s.Q3)("",!0)]),(0,s.Lk)("div",{class:"collapse-toggler",onClick:t[1]||(t[1]=(0,n.D$)((t=>e.collapsed_=!e.collapsed_),["stop"]))},[(0,s.Lk)("i",{class:(0,l.C4)(["fas",{"fa-chevron-down":e.collapsed_,"fa-chevron-up":!e.collapsed_}])},null,2)])])],2),e.collapsed_?(0,s.Q3)("",!0):((0,s.uX)(),(0,s.CE)("div",{key:0,class:"body",onClick:t[14]||(t[14]=(0,n.D$)((()=>{}),["stop"]))},[(0,s.Lk)("section",p,[(0,s.Lk)("header",{class:(0,l.C4)({collapsed:e.runCollapsed}),onClick:t[3]||(t[3]=t=>e.runCollapsed=!e.runCollapsed)},[t[19]||(t[19]=(0,s.Lk)("span",{class:"col-10"},[(0,s.Lk)("i",{class:"fas fa-play"}),(0,s.eW)("  Run ")],-1)),(0,s.Lk)("span",g,[(0,s.Lk)("button",{type:"button",class:"btn btn-primary",disabled:e.loading,title:e.runCollapsed?"Expand":"Collapse"},[(0,s.Lk)("i",{class:(0,l.C4)(["fas",{"fa-chevron-down":e.runCollapsed,"fa-chevron-up":!e.runCollapsed}])},null,2)],8,m)])],2),e.runCollapsed?(0,s.Q3)("",!0):((0,s.uX)(),(0,s.CE)("div",f,[(0,s.Lk)("form",{onSubmit:t[9]||(t[9]=(0,n.D$)(((...e)=>G.run&&G.run(...e)),["prevent"]))},[e.value.args?.length?((0,s.uX)(),(0,s.CE)("div",v,[t[21]||(t[21]=(0,s.eW)(" Arguments ")),((0,s.uX)(!0),(0,s.CE)(s.FK,null,(0,s.pI)(e.value.args||[],((a,l)=>((0,s.uX)(),(0,s.CE)("div",{class:"row arg",key:l},[(0,s.Lk)("input",{type:"text",class:"argname",value:a,disabled:!0},null,8,y),t[20]||(t[20]=(0,s.eW)(" = ")),(0,s.Lk)("input",{type:"text",class:"argvalue",placeholder:"Value",disabled:e.loading,onInput:e=>G.updateArg(a,e)},null,40,w)])))),128))])):(0,s.Q3)("",!0),(0,s.Lk)("div",k,[t[24]||(t[24]=(0,s.eW)(" Extra Arguments ")),((0,s.uX)(!0),(0,s.CE)(s.FK,null,(0,s.pI)(e.extraArgs,((a,l)=>((0,s.uX)(),(0,s.CE)("div",{class:"row arg",key:l},[(0,s.Lk)("input",{type:"text",class:"argname",placeholder:"Name",value:l,disabled:e.loading,onBlur:e=>G.updateExtraArgName(l,e)},null,40,A),t[22]||(t[22]=(0,s.eW)(" = ")),(0,s.Lk)("input",{type:"text",placeholder:"Value",class:"argvalue",value:a,disabled:e.loading,onInput:t[4]||(t[4]=t=>G.updateExtraArgValue(e.arg,t))},null,40,C)])))),128)),(0,s.Lk)("div",b,[(0,s.bo)((0,s.Lk)("input",{type:"text",class:"argname",placeholder:"Name","onUpdate:modelValue":t[5]||(t[5]=t=>e.newArgName=t),disabled:e.loading,ref:"newArgName",onBlur:t[6]||(t[6]=(...e)=>G.addExtraArg&&G.addExtraArg(...e))},null,40,L),[[n.Jo,e.newArgName]]),t[23]||(t[23]=(0,s.eW)(" = ")),(0,s.bo)((0,s.Lk)("input",{type:"text",class:"argvalue",placeholder:"Value","onUpdate:modelValue":t[7]||(t[7]=t=>e.newArgValue=t),disabled:e.loading,onBlur:t[8]||(t[8]=(...e)=>G.addExtraArg&&G.addExtraArg(...e))},null,40,E),[[n.Jo,e.newArgValue]])])]),(0,s.Lk)("div",x,[(0,s.Lk)("button",{type:"submit",class:"btn btn-primary",disabled:e.loading,title:"Run Procedure"},t[25]||(t[25]=[(0,s.Lk)("i",{class:"fas fa-play"},null,-1)]),8,V)])],32),e.lastResponse||e.lastError?((0,s.uX)(),(0,s.CE)("div",$,[(0,s.bF)(ee,{response:e.lastResponse,error:e.lastError},null,8,["response","error"])])):(0,s.Q3)("",!0)]))]),(0,s.Lk)("section",_,[(0,s.Lk)("header",{class:(0,l.C4)({collapsed:e.infoCollapsed}),onClick:t[10]||(t[10]=t=>e.infoCollapsed=!e.infoCollapsed)},[t[26]||(t[26]=(0,s.Lk)("span",{class:"col-10"},[(0,s.Lk)("i",{class:"fas fa-info-circle"}),(0,s.eW)("  Info ")],-1)),(0,s.Lk)("span",I,[(0,s.Lk)("button",{type:"button",class:"btn btn-primary",disabled:e.loading,title:e.infoCollapsed?"Expand":"Collapse"},[(0,s.Lk)("i",{class:(0,l.C4)(["fas",{"fa-chevron-down":e.infoCollapsed,"fa-chevron-up":!e.infoCollapsed}])},null,2)],8,N)])],2),e.infoCollapsed?(0,s.Q3)("",!0):((0,s.uX)(),(0,s.CE)("div",O,[(0,s.Lk)("div",R,[t[27]||(t[27]=(0,s.Lk)("div",{class:"label"},"Source",-1)),(0,s.Lk)("div",F,[(0,s.Lk)("i",{class:(0,l.C4)(G.procedureTypeIconClass)},null,2),(0,s.eW)("  "+(0,l.v_)(e.value.procedure_type),1)])]),(0,s.Lk)("div",X,[(0,s.bF)(te,{entity:e.value},null,8,["entity"])]),e.value?.actions?.length?((0,s.uX)(),(0,s.CE)("div",S,[t[32]||(t[32]=(0,s.Lk)("div",{class:"label"},"Actions",-1)),(0,s.Lk)("div",P,[(0,s.Lk)("div",M,[(0,s.Lk)("button",{type:"button",class:"btn btn-primary",title:"Edit Actions",disabled:e.loading,onClick:t[11]||(t[11]=t=>e.showProcedureEditor=!e.showProcedureEditor)},[G.isReadOnly&&!e.showProcedureEditor?((0,s.uX)(),(0,s.CE)("span",D,t[28]||(t[28]=[(0,s.Lk)("i",{class:"fas fa-eye"},null,-1),(0,s.eW)("  View ")]))):G.isReadOnly||e.showProcedureEditor?((0,s.uX)(),(0,s.CE)("span",Q,t[30]||(t[30]=[(0,s.Lk)("i",{class:"fas fa-times"},null,-1),(0,s.eW)("  Close ")]))):((0,s.uX)(),(0,s.CE)("span",B,t[29]||(t[29]=[(0,s.Lk)("i",{class:"fas fa-edit"},null,-1),(0,s.eW)("  Edit ")])))],8,W)]),G.isReadOnly?(0,s.Q3)("",!0):((0,s.uX)(),(0,s.CE)("div",J,[(0,s.Lk)("button",{type:"button",title:"Delete Procedure",disabled:e.loading,onClick:t[12]||(t[12]=t=>e.showConfirmDelete=!0)},t[31]||(t[31]=[(0,s.Lk)("i",{class:"fas fa-trash"},null,-1),(0,s.eW)("  Delete ")]),8,T)]))])])):(0,s.Q3)("",!0),e.value.source?((0,s.uX)(),(0,s.CE)("div",U,[t[33]||(t[33]=(0,s.Lk)("div",{class:"label"},"Path",-1)),(0,s.Lk)("div",q,[(0,s.Lk)("a",{href:e.$route.path,onClick:t[13]||(t[13]=(0,n.D$)((t=>e.showFileEditor=!0),["prevent"]))},(0,l.v_)(G.displayPath),9,Y)])])):(0,s.Q3)("",!0)]))])])),e.showFileEditor&&e.value.source?((0,s.uX)(),(0,s.CE)("div",j,[(0,s.bF)(ae,{file:e.value.source,line:e.value.line,visible:!0,uppercase:!1,onClose:t[15]||(t[15]=t=>e.showFileEditor=!1)},null,8,["file","line"])])):(0,s.Q3)("",!0),e.value?.actions?.length&&e.showProcedureEditor?((0,s.uX)(),(0,s.Wv)(se,{key:2,procedure:e.value,"read-only":G.isReadOnly,"with-name":!G.isReadOnly,"with-save":!G.isReadOnly,value:e.value,visible:e.showProcedureEditor,onInput:G.onUpdate,onClose:t[16]||(t[16]=t=>e.showProcedureEditor=!1),ref:"editor"},null,8,["procedure","read-only","with-name","with-save","value","visible","onInput"])):(0,s.Q3)("",!0),(0,s.Lk)("div",H,[e.showConfirmDelete?((0,s.uX)(),(0,s.Wv)(le,{key:0,visible:!0,onInput:G.remove,onClose:t[17]||(t[17]=t=>e.showConfirmDelete=!1)},{default:(0,s.k6)((()=>[t[34]||(t[34]=(0,s.eW)(" Are you sure you want to delete the procedure ")),(0,s.Lk)("b",null,(0,l.v_)(e.value.name),1),t[35]||(t[35]=(0,s.eW)("? "))])),_:1},8,["onInput"])):(0,s.Q3)("",!0)])])}var K=a(3538),G=a(4897),Z=a(1029),ee=a(1367),te=a(4219),ae=a(5829),se=a(9954),le={components:{ConfirmDialog:K.A,EntityIcon:Z["default"],FileEditor:ee.A,IconEditor:te["default"],ProcedureEditor:ae.A,Response:se.A},mixins:[G["default"]],emits:["delete","input","loading"],props:{collapseOnHeaderClick:{type:Boolean,default:!1},selected:{type:Boolean,default:!1}},data:function(){return{args:{},defaultIconClass:"fas fa-cogs",extraArgs:{},collapsed_:!0,infoCollapsed:!1,lastError:null,lastResponse:null,newArgName:"",newArgValue:"",runCollapsed:!1,showConfirmDelete:!1,showFileEditor:!1,showProcedureEditor:!1}},computed:{icon(){const e=this.defaultIconClass,t=this.value.meta?.icon?.["class"];let a=t;return t&&t!==e||(a=this.procedureTypeIconClass||e),{...this.value.meta?.icon||{},class:a}},isReadOnly(){return"db"!==this.value.procedure_type},allArgs(){return Object.entries({...this.args,...this.extraArgs}).map((([e,t])=>[e?.trim(),t])).filter((([e,t])=>e?.length&&null!=t&&("string"!==typeof t||t?.trim()?.length>0))).reduce(((e,[t,a])=>(e[t]=a,e)),{})},displayPath(){let e=this.value.source;if(!e?.length)return null;const t=this.$root.configDir;t&&(e=e.replace(new RegExp(`^${t}/`),""));const a=parseInt(this.value.line);return isNaN(a)||(e+=`:${a}`),e},procedureTypeIconClass(){return"python"===this.value.procedure_type?"fab fa-python":"config"===this.value.procedure_type?"fas fa-file":"db"===this.value.procedure_type?"fas fa-database":this.defaultIconClass}},methods:{async run(){this.$emit("loading",!0);try{this.lastResponse=await this.request(`procedure.${this.value.name}`,this.allArgs),this.lastError=null,this.notify({text:"Procedure executed successfully",image:{icon:"play"}})}catch(e){this.lastResponse=null,this.lastError=e,this.notify({text:"Failed to execute procedure",error:!0,image:{icon:"exclamation-triangle"}})}finally{this.$emit("loading",!1)}},async remove(){this.$emit("loading",!0);try{await this.request("procedures.delete",{name:this.value.name}),this.$emit("loading",!1),this.$emit("delete"),this.notify({text:"Procedure deleted successfully",image:{icon:"trash"}})}finally{this.$emit("loading",!1)}},onHeaderClick(e){this.collapseOnHeaderClick&&(e.stopPropagation(),this.collapsed_=!this.collapsed_)},onUpdate(e){this.isReadOnly||(this.$emit("input",e),this.$nextTick((()=>this.$refs.editor?.close())))},updateArg(e,t){let a=t.target.value;a?.length||delete this.args[e];try{a=JSON.parse(a)}catch(s){}this.args[e]=a},updateExtraArgName(e,t){let a=t.target.value?.trim();a!==e&&(a?.length?this.extraArgs[a]=e?this.extraArgs[e]:"":this.focusNewArgName(),e&&delete this.extraArgs[e])},updateExtraArgValue(e,t){let a=t.target.value;a?.length?this.extraArgs[e]=this.deserializeValue(a):delete this.extraArgs[e]},addExtraArg(){let e=this.newArgName?.trim(),t=this.newArgValue;e?.length&&t?.length&&(this.extraArgs[e]=this.deserializeValue(t),this.newArgName="",this.newArgValue="",this.focusNewArgName())},deserializeValue(e){try{return JSON.parse(e)}catch(t){return e}},focusNewArgName(){this.$nextTick((()=>this.$refs.newArgName.focus()))}},watch:{collapsed:{immediate:!0,handler(e){this.collapsed_=e}},selected:{immediate:!0,handler(e){this.collapsed_=e}},showProcedureEditor(e){e||this.$refs.editor?.reset()}},mounted(){this.collapsed_=!this.selected}},ne=a(6262);const oe=(0,ne.A)(le,[["render",z],["__scopeId","data-v-9744c022"]]);var ie=oe}}]);
//# sourceMappingURL=6923.12f5a8a3.js.map