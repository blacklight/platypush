"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[1807],{1807:function(e,t,n){n.d(t,{Z:function(){return We}});var s=n(6252),i=n(3577),a=n(9963);const o=e=>((0,s.dD)("data-v-48afe350"),e=e(),(0,s.Cn)(),e),r={class:"action-editor"},l={class:"curl-modal-container"},c=["innerHTML"],u={class:"header-container"},d={class:"tabs-container"},h={key:0,class:"buttons"},p=["disabled"],g=o((()=>(0,s._)("i",{class:"fas fa-save"},null,-1))),m=[g],v={key:0,class:"request structured"},b={class:"autocomplete-container"},y=["type","disabled"],k=o((()=>(0,s._)("i",{class:"fas fa-play"},null,-1))),f=[k],w={key:0,class:"args"},A=o((()=>(0,s._)("h2",null,[(0,s._)("i",{class:"fas fa-code"}),(0,s.Uk)("   Arguments ")],-1))),x={key:1,class:"request raw-request"},I={class:"first-row"},_=["placeholder"],D=["type","disabled"],q=o((()=>(0,s._)("i",{class:"fas fa-play"},null,-1))),C=[q];function S(e,t,n,o,g,k){const q=(0,s.up)("Loading"),S=(0,s.up)("Modal"),E=(0,s.up)("Tab"),R=(0,s.up)("Tabs"),O=(0,s.up)("Autocomplete"),$=(0,s.up)("ActionDoc"),j=(0,s.up)("ActionArgs"),T=(0,s.up)("Response");return(0,s.wg)(),(0,s.iD)("div",{class:(0,i.C_)(["action-editor-container",{"with-save":n.withSave}]),onClick:t[12]||(t[12]=(...e)=>k.onClick&&k.onClick(...e))},[g.loading?((0,s.wg)(),(0,s.j4)(q,{key:0})):(0,s.kq)("",!0),(0,s._)("div",r,[(0,s._)("div",l,[k.curlSnippet?.length?((0,s.wg)(),(0,s.j4)(S,{key:0,ref:"curlModal",title:"curl request"},{default:(0,s.w5)((()=>[(0,s._)("div",{class:"output curl-snippet",onClick:t[0]||(t[0]=t=>e.copyToClipboard(k.curlSnippet))},[(0,s._)("pre",null,[(0,s._)("code",{innerHTML:k.highlightedCurlSnippet},null,8,c)])])])),_:1},512)):(0,s.kq)("",!0)]),(0,s._)("div",u,[(0,s._)("div",d,[(0,s.Wm)(R,null,{default:(0,s.w5)((()=>[(0,s.Wm)(E,{selected:g.structuredInput,"icon-class":"fas fa-list",onInput:t[1]||(t[1]=e=>k.onInputTypeChange(!0))},{default:(0,s.w5)((()=>[(0,s.Uk)(" Structured ")])),_:1},8,["selected"]),(0,s.Wm)(E,{selected:!g.structuredInput,"icon-class":"fas fa-code",onInput:t[2]||(t[2]=e=>k.onInputTypeChange(!1))},{default:(0,s.w5)((()=>[(0,s.Uk)(" Raw ")])),_:1},8,["selected"])])),_:1})]),n.withSave?((0,s.wg)(),(0,s.iD)("div",h,[(0,s._)("button",{type:"submit",class:"save-btn btn-primary",disabled:g.running||!k.isValidAction,title:"Save",onClick:t[3]||(t[3]=(0,a.iM)(((...e)=>k.onSubmit&&k.onSubmit(...e)),["stop"]))},m,8,p)])):(0,s.kq)("",!0)]),(0,s._)("form",{ref:"actionForm",autocomplete:"off",onSubmit:t[11]||(t[11]=(0,a.iM)(((...e)=>k.onSubmit&&k.onSubmit(...e)),["prevent"]))},[g.structuredInput?((0,s.wg)(),(0,s.iD)("div",v,[(0,s._)("header",null,[(0,s._)("div",b,[(0,s.Wm)(O,{ref:"autocomplete",items:k.autocompleteItems,onInput:k.updateAction,placeholder:"Action","show-results-when-blank":"",autofocus:"",disabled:g.running,value:g.action.name},null,8,["items","onInput","disabled","value"]),(0,s._)("button",{type:n.withSave?"button":"submit",class:"run-btn btn-primary",disabled:g.running||!k.isValidAction,title:"Run",onClick:t[4]||(t[4]=(0,a.iM)(((...e)=>k.executeAction&&k.executeAction(...e)),["stop"]))},f,8,y)])]),(0,s.Wm)($,{action:g.action,"curl-snippet":k.curlSnippet,loading:g.docLoading,doc:g.selectedDoc,onCurlModal:t[5]||(t[5]=t=>e.$refs.curlModal.show())},null,8,["action","curl-snippet","loading","doc"]),g.action.name in g.actions&&(Object.keys(g.action.args).length||g.action.supportsExtraArgs)?((0,s.wg)(),(0,s.iD)("section",w,[A,(0,s.Wm)(j,{action:g.action,loading:g.loading,running:g.running,"selected-arg":g.selectedArg,"selected-argdoc":g.selectedArgdoc,onAdd:k.addArg,onSelect:k.selectArgdoc,onRemove:k.removeArg,onArgEdit:t[6]||(t[6]=e=>g.action.args[e.name].value=e.value),onExtraArgNameEdit:t[7]||(t[7]=e=>g.action.extraArgs[e.index].name=e.value),onExtraArgValueEdit:t[8]||(t[8]=e=>g.action.extraArgs[e.index].value=e.value)},null,8,["action","loading","running","selected-arg","selected-argdoc","onAdd","onSelect","onRemove"])])):(0,s.kq)("",!0),(0,s.Wm)(T,{response:g.response,error:g.error},null,8,["response","error"])])):(0,s.kq)("",!0),g.structuredInput?(0,s.kq)("",!0):((0,s.wg)(),(0,s.iD)("div",x,[(0,s._)("div",I,[(0,s._)("label",null,[(0,s.wy)((0,s._)("textarea",{"onUpdate:modelValue":t[9]||(t[9]=e=>g.rawRequest=e),ref:"rawAction",placeholder:g.rawRequestPlaceholder},null,8,_),[[a.nr,g.rawRequest]])]),(0,s._)("button",{type:n.withSave?"button":"submit",disabled:g.running,class:"raw-run-btn btn-primary",title:"Run",onClick:t[10]||(t[10]=(0,a.iM)(((...e)=>k.executeAction&&k.executeAction(...e)),["stop"]))},C,8,D)]),(0,s.Wm)(T,{response:g.response,error:g.error},null,8,["response","error"])]))],544)])],2)}n(560),n(8783),n(3465);var E=n(637);const R=e=>((0,s.dD)("data-v-1edf7bde"),e=e(),(0,s.Cn)(),e),O={class:"args-body"},$={key:0,class:"args-list"},j=["disabled","placeholder","value","onInput","onFocus"],T={key:0,class:"required-flag"},N={key:0,class:"extra-args"},L={class:"col-5"},M=["disabled","value","onInput"],U={class:"col-6"},Z=["disabled","value","onInput"],B={class:"col-1 buttons"},K=["onClick"],J=R((()=>(0,s._)("i",{class:"fas fa-trash"},null,-1))),V=[J],H={key:1,class:"add-arg"},z=R((()=>(0,s._)("i",{class:"fas fa-plus"},null,-1))),W=[z];function P(e,t,n,a,o,r){const l=(0,s.up)("Argdoc");return(0,s.wg)(),(0,s.iD)("div",O,[Object.keys(n.action.args).length||n.action.supportsExtraArgs?((0,s.wg)(),(0,s.iD)("div",$,[((0,s.wg)(!0),(0,s.iD)(s.HY,null,(0,s.Ko)(Object.keys(n.action.args),(e=>((0,s.wg)(),(0,s.iD)("div",{class:"arg",key:e},[(0,s._)("label",null,[(0,s._)("input",{type:"text",class:(0,i.C_)(["action-arg-value",{required:n.action.args[e].required}]),disabled:n.running,placeholder:e,value:n.action.args[e].value,onInput:t=>r.onArgEdit(e,t),onFocus:t=>r.onSelect(e)},null,42,j),n.action.args[e].required?((0,s.wg)(),(0,s.iD)("span",T,"*")):(0,s.kq)("",!0)]),n.selectedArgdoc&&n.selectedArg&&e===n.selectedArg?((0,s.wg)(),(0,s.j4)(l,{key:0,name:n.selectedArg,args:n.action.args[n.selectedArg],doc:n.selectedArgdoc,loading:n.loading,"is-mobile":""},null,8,["name","args","doc","loading"])):(0,s.kq)("",!0)])))),128)),Object.keys(n.action.extraArgs).length?((0,s.wg)(),(0,s.iD)("div",N,[((0,s.wg)(!0),(0,s.iD)(s.HY,null,(0,s.Ko)(n.action.extraArgs,((t,i)=>((0,s.wg)(),(0,s.iD)("div",{class:"arg extra-arg",key:i},[(0,s._)("label",L,[(0,s._)("input",{type:"text",class:"action-extra-arg-name",placeholder:"Name",disabled:n.running,value:t.name,onInput:e=>r.onExtraArgNameEdit(i,e.target.value)},null,40,M)]),(0,s._)("label",U,[(0,s._)("input",{type:"text",class:"action-extra-arg-value",placeholder:"Value",disabled:n.running,value:t.value,onInput:e=>r.onExtraArgValueEdit(i,e.target.value)},null,40,Z)]),(0,s._)("label",B,[(0,s._)("button",{type:"button",class:"action-extra-arg-del",title:"Remove argument",onClick:t=>e.$emit("remove",i)},V,8,K)])])))),128))])):(0,s.kq)("",!0),n.action.supportsExtraArgs?((0,s.wg)(),(0,s.iD)("div",H,[(0,s._)("button",{type:"button",title:"Add an argument",onClick:t[0]||(t[0]=(...e)=>r.onArgAdd&&r.onArgAdd(...e))},W)])):(0,s.kq)("",!0)])):(0,s.kq)("",!0),n.selectedArgdoc&&n.selectedArg?((0,s.wg)(),(0,s.j4)(l,{key:1,name:n.selectedArg,args:n.action.args[n.selectedArg],doc:n.selectedArgdoc,loading:n.loading},null,8,["name","args","doc","loading"])):(0,s.kq)("",!0)])}const F=e=>((0,s.dD)("data-v-2df98b7b"),e=e(),(0,s.Cn)(),e),Y=["textContent"],G={key:0,class:"flag required"},X={key:1,class:"flag optional"},Q={class:"doc html"},ee={key:1},te=["innerHTML"],ne={key:1,class:"type"},se=F((()=>(0,s._)("b",null,"Type:",-1)));function ie(e,t,n,a,o,r){const l=(0,s.up)("Loading");return(0,s.wg)(),(0,s.iD)("article",{class:(0,i.C_)(["argdoc-container",{mobile:n.isMobile,widescreen:!n.isMobile}])},[(0,s._)("h2",null,[(0,s.Uk)(" Argument: "),(0,s._)("div",{class:"argname",textContent:(0,i.zw)(n.name)},null,8,Y),n.args.required?((0,s.wg)(),(0,s.iD)("span",G,"[Required]")):((0,s.wg)(),(0,s.iD)("span",X,"[Optional]"))]),(0,s._)("div",Q,[n.loading?((0,s.wg)(),(0,s.j4)(l,{key:0})):((0,s.wg)(),(0,s.iD)("span",ee,[n.doc?.length?((0,s.wg)(),(0,s.iD)("span",{key:0,innerHTML:n.doc},null,8,te)):(0,s.kq)("",!0),n.args.type?((0,s.wg)(),(0,s.iD)("div",ne,[se,(0,s.Uk)("   "+(0,i.zw)(n.args.type),1)])):(0,s.kq)("",!0)]))])],2)}var ae=n(6791),oe={name:"Argdoc",components:{Loading:ae.Z},props:{args:{type:Object,default:()=>({})},name:{type:String,required:!0},doc:String,loading:Boolean,isMobile:Boolean}},re=n(3744);const le=(0,re.Z)(oe,[["render",ie],["__scopeId","data-v-2df98b7b"]]);var ce=le,ue={name:"ActionArgs",components:{Argdoc:ce},emits:["add","arg-edit","extra-arg-name-edit","extra-arg-value-edit","remove","select"],props:{action:Object,loading:Boolean,running:Boolean,selectedArg:String,selectedArgdoc:String},methods:{onArgAdd(){this.$emit("add"),this.$nextTick((()=>{const e=this.$el.querySelectorAll(".action-extra-arg-name");e.length&&e[e.length-1].focus()}))},onArgEdit(e,t){this.$emit("arg-edit",{name:e,value:t.target.value})},onExtraArgNameEdit(e,t){this.$emit("extra-arg-name-edit",{index:e,value:t})},onExtraArgValueEdit(e,t){this.$emit("extra-arg-value-edit",{index:e,value:t})},onSelect(e){this.$emit("select",e)}}};const de=(0,re.Z)(ue,[["render",P],["__scopeId","data-v-1edf7bde"]]);var he=de;const pe=e=>((0,s.dD)("data-v-105c186a"),e=e(),(0,s.Cn)(),e),ge={key:0,class:"doc-container"},me={class:"title"},ve=pe((()=>(0,s._)("i",{class:"fas fa-book"},null,-1))),be=["href"],ye={key:0,class:"buttons"},ke=pe((()=>(0,s._)("i",{class:"fas fa-puzzle-piece"},null,-1))),fe=[ke],we=pe((()=>(0,s._)("i",{class:"fas fa-terminal"},null,-1))),Ae=[we],xe={class:"doc html"},Ie=["innerHTML"];function _e(e,t,n,i,a,o){const r=(0,s.up)("Loading");return n.doc?.length?((0,s.wg)(),(0,s.iD)("section",ge,[(0,s._)("h2",null,[(0,s._)("div",me,[ve,(0,s.Uk)("   "),(0,s._)("a",{href:n.action?.doc_url},"Action documentation",8,be)]),n.action?.name?((0,s.wg)(),(0,s.iD)("div",ye,[o.pluginName?.length?((0,s.wg)(),(0,s.iD)("button",{key:0,type:"button",title:"Go to extension",onClick:t[0]||(t[0]=(...e)=>o.onExtClick&&o.onExtClick(...e))},fe)):(0,s.kq)("",!0),n.curlSnippet?.length?((0,s.wg)(),(0,s.iD)("button",{key:1,type:"button",title:"cURL command",onClick:t[1]||(t[1]=t=>e.$emit("curl-modal"))},Ae)):(0,s.kq)("",!0)])):(0,s.kq)("",!0)]),(0,s._)("div",xe,[n.loading?((0,s.wg)(),(0,s.j4)(r,{key:0})):((0,s.wg)(),(0,s.iD)("span",{key:1,innerHTML:n.doc},null,8,Ie))])])):(0,s.kq)("",!0)}var De={name:"ActionDoc",components:{Loading:ae.Z},emits:["curl-modal"],props:{action:Object,doc:String,curlSnippet:String,loading:Boolean},computed:{pluginName(){const e=(this.action?.name||"").split(".");return e.length>1?e.slice(0,-1).join("."):null}},methods:{onExtClick(){window.location.href=`/#extensions?extension=${this.pluginName}`}}};const qe=(0,re.Z)(De,[["render",_e],["__scopeId","data-v-105c186a"]]);var Ce=qe;const Se={class:"autocomplete"},Ee=["text"],Re=["placeholder","disabled","value"],Oe={key:0,class:"items"},$e=["data-item","onClick"],je={key:0,class:"matching"},Te={class:"normal"};function Ne(e,t,n,a,o,r){return(0,s.wg)(),(0,s.iD)("div",Se,[(0,s._)("label",{text:n.label},[(0,s._)("input",{type:"text",class:"input",ref:"input",placeholder:n.placeholder,disabled:n.disabled,value:n.value,onFocus:t[0]||(t[0]=(...e)=>r.onFocus&&r.onFocus(...e)),onInput:t[1]||(t[1]=(...e)=>r.onInput&&r.onInput(...e)),onBlur:t[2]||(t[2]=(...e)=>r.onBlur&&r.onBlur(...e)),onKeydown:t[3]||(t[3]=(...e)=>r.onInputKeyDown&&r.onInputKeyDown(...e)),onKeyup:t[4]||(t[4]=(...e)=>r.onInputKeyUp&&r.onInputKeyUp(...e))},null,40,Re)],8,Ee),r.showItems?((0,s.wg)(),(0,s.iD)("div",Oe,[((0,s.wg)(!0),(0,s.iD)(s.HY,null,(0,s.Ko)(r.visibleItems,((e,t)=>((0,s.wg)(),(0,s.iD)("div",{class:(0,i.C_)(["item",{active:t===o.curIndex}]),key:e,"data-item":e,onClick:t=>r.onItemSelect(e)},[n.value?.length?((0,s.wg)(),(0,s.iD)("span",je,(0,i.zw)(e.substr(0,n.value.length)),1)):(0,s.kq)("",!0),(0,s._)("span",Te,(0,i.zw)(e.substr(n.value?.length||0)),1)],10,$e)))),128))])):(0,s.kq)("",!0)])}var Le={name:"Autocomplete",emits:["input"],props:{items:{type:Array,required:!0},value:{type:String,default:""},disabled:{type:Boolean,default:!1},autofocus:{type:Boolean,default:!1},label:{type:String},placeholder:{type:String},showResultsWhenBlank:{type:Boolean,default:!1}},data(){return{visible:!1,curIndex:-1}},computed:{visibleItems(){if(!this.value?.length)return this.items;const e=this.value.toUpperCase();return e?.length?this.items.filter((t=>t.substr(0,e.length).toUpperCase()===e)):this.showResultsWhenBlank?this.items:[]},showItems(){return this.visible&&this.items?.length}},methods:{selectNextItem(){this.curIndex++,this.normalizeIndex()},selectPrevItem(){this.curIndex--,this.normalizeIndex()},normalizeIndex(){this.curIndex>=this.visibleItems.length&&(this.curIndex=0),this.curIndex<0&&(this.curIndex=this.visibleItems.length-1);const e=this.$el.querySelector("[data-item='"+this.visibleItems[this.curIndex]+"']");e&&e.scrollIntoView({block:"start",inline:"nearest",behavior:"smooth"})},valueIsInItems(){return!!this.value&&this.items.indexOf(this.value)>=0},onFocus(){(this.showResultsWhenBlank||this.value?.length)&&(this.visible=!0)},onInput(e){let t=e.target.value;this.valueIsInItems()&&(this.visible=!1),e.stopPropagation(),this.$emit("input",t),this.curIndex=-1,this.visible=!0},onBlur(e){this.onInput(e),this.$nextTick((()=>{this.valueIsInItems()&&(this.visible=!1)}))},onItemSelect(e){this.$emit("input",e),this.$nextTick((()=>{this.valueIsInItems()&&(this.visible=!1)}))},onInputKeyUp(e){["ArrowUp","ArrowDown","Tab","Enter","Escape"].indexOf(e.key)>=0&&e.stopPropagation(),"Enter"===e.key&&this.valueIsInItems()&&(this.$refs.input.blur(),this.visible=!1)},onInputKeyDown(e){"ArrowDown"===e.key||"Tab"===e.key&&!e.shiftKey||"j"===e.key&&e.ctrlKey?(this.selectNextItem(),e.preventDefault()):"ArrowUp"===e.key||"Tab"===e.key&&e.shiftKey||"k"===e.key&&e.ctrlKey?(this.selectPrevItem(),e.preventDefault()):"Enter"===e.key?this.curIndex>-1&&this.visible&&(e.preventDefault(),this.onItemSelect(this.visibleItems[this.curIndex]),this.$refs.input.focus()):"Escape"===e.key&&(this.visible=!1)},onDocumentClick(e){this.$el.contains(e.target)||e.target.classList.contains("item")||(this.visible=!1)}},mounted(){document.addEventListener("click",this.onDocumentClick),this.autofocus&&this.$refs.input.focus()}};const Me=(0,re.Z)(Le,[["render",Ne],["__scopeId","data-v-1f70dd66"]]);var Ue=Me,Ze=n(3493),Be=n(803),Ke=n(8735),Je=n(3176),Ve=n(8637),He={mixins:[Ve.Z],emits:["input"],components:{ActionArgs:he,ActionDoc:Ce,Autocomplete:Ue,Loading:ae.Z,Modal:Ze.Z,Response:Be.Z,Tab:Ke.Z,Tabs:Je.Z},props:{value:{type:Object},withSave:{type:Boolean,default:!1}},data(){return{loading:!1,running:!1,docLoading:!1,structuredInput:!0,selectedDoc:void 0,selectedArg:void 0,selectedArgdoc:void 0,response:void 0,error:void 0,rawRequest:void 0,rawRequestPlaceholder:'Raw JSON request. Example:\n\n{"type": "request", "action": "file.list", "args": {"path": "/"}}',actions:{},plugins:{},procedures:{},actionDocsCache:{},action:{name:void 0,args:{},extraArgs:[],supportsExtraArgs:!1}}},computed:{currentActionDocURL(){return this.action?.doc_url},isValidAction(){return this.action?.name?.length&&this.action.name in this.actions&&Object.values(this.action.args).every((e=>!e.required||e.value?.length))},autocompleteItems(){return this.getPluginName(this.action.name)in this.plugins?Object.keys(this.actions).sort():Object.keys(this.plugins).sort().map((e=>`${e}.`))},actionInput(){return this.$refs.autocomplete.$el.parentElement.querySelector("input[type=text]")},requestArgs(){return this.action.name?{...Object.entries(this.action.args).reduce(((e,t)=>{if(null!=t[1].value){let s=t[1].value;try{s=JSON.parse(s)}catch(n){console.debug("Not a valid JSON value"),console.debug(s)}e[t[0]]=s}return e}),{}),...(this.action.extraArgs||[]).reduce(((e,t)=>{let n=t.value;try{n=JSON.parse(n)}catch(s){console.debug("Not a valid JSON value"),console.debug(n)}return e[t.name]=n,e}),{})}:{}},curlURL(){return`${window.location.protocol}//${window.location.host}/execute`},curlSnippet(){if(!this.action.name)return"";const e={type:"request",action:this.action.name,args:this.requestArgs},t=JSON.stringify(e,null,2);return`curl -XPOST -H "Content-Type: application/json" \\\n  -H "Cookie: session_token=${this.getCookies()["session_token"]}" \\\n  -d '\n  {\n    `+this.indent(t.split("\n").slice(1,t.length-2).join("\n"),2).trim()+"' \\\n  "+`'${this.curlURL}'`},highlightedCurlSnippet(){return E.Z.highlight("# Note: Replace the cookie with a JWT token for production cases\n"+this.curlSnippet,{language:"bash"}).value}},methods:{async refresh(){this.loading=!0;try{[this.procedures,this.plugins]=await Promise.all([this.request("inspect.get_procedures"),this.request("inspect.get_all_plugins")])}finally{this.loading=!1}this.plugins.procedure={name:"procedure",actions:Object.entries(this.procedures||{}).reduce(((e,[t,n])=>(e[t]={name:t,args:(n.args||[]).reduce(((e,t)=>(e[t]={name:t,required:!1},e)),{}),supportsExtraArgs:!0},e)),{})};for(const n of Object.values(this.plugins))for(const e of Object.values(n.actions))e.name=n.name+"."+e.name,e.supportsExtraArgs=!!e.has_kwargs,delete e.has_kwargs,this.actions[e.name]=e;const e=this.getUrlArgs(),t=e?.action;t?.length&&t in this.actions&&t!==this.action.name&&this.updateAction(t)},async updateAction(e,t){let{force:n,args:s,extraArgs:i}=t||{};if(s||(s={}),i||(i=[]),e===this.action.name&&!n)return;if(this.action.name=e,!(this.action.name in this.actions))return this.selectedDoc=void 0,void this.resetArgdoc();this.resetArgdoc(),this.docLoading=!0;try{this.action={...this.actions[this.action.name],args:Object.entries(this.actions[this.action.name].args).reduce(((e,t)=>(e[t[0]]={...t[1],value:s?.[t[0]]??t[1].default},e)),{}),extraArgs:i||[]}}finally{this.docLoading=!1}this.selectedDoc=this.actionDocsCache[this.action.name]?.html||await this.parseDoc(this.action.doc),this.actionDocsCache[this.action.name]||(this.actionDocsCache[this.action.name]={}),this.actionDocsCache[this.action.name].html=this.selectedDoc,this.setUrlArgs({action:this.action.name});const a=this.$el.querySelector(".action-arg-value");a?a.focus():this.$nextTick((()=>{this.actionInput.focus()})),this.response=void 0,this.error=void 0},async parseDoc(e){return e?.length?await this.request("utils.rst_to_html",{text:e}):e},addArg(){this.action.extraArgs.push({name:void 0,value:void 0})},removeArg(e){this.action.extraArgs.pop(e)},async selectArgdoc(e){this.selectedArg=e,this.selectedArgdoc=this.actionDocsCache[this.action.name]?.[e]?.html||await this.parseDoc(this.action.args[e].doc),this.actionDocsCache[this.action.name]||(this.actionDocsCache[this.action.name]={}),this.actionDocsCache[this.action.name][e]={html:this.selectedArgdoc}},resetArgdoc(){this.selectedArg=void 0,this.selectedArgdoc=void 0},onInputTypeChange(e){this.structuredInput=e,this.response=void 0,this.error=void 0,this.$nextTick((()=>{e?this.actionInput.focus():(this.$refs.rawAction.focus(),this.isValidAction&&(this.rawRequest=JSON.stringify(this.toRequest(this.action),null,2)))}))},onResponse(e){this.response=("string"===typeof e?e:JSON.stringify(e,null,2)).trim(),this.error=void 0},onError(e){this.response=void 0,this.error=e},onDone(){this.running=!1},getPluginName(e){return e?.length?e.split(".").slice(0,-1).join("."):""},executeAction(){if((this.action.name||this.rawRequest)&&!this.running)if(this.running=!0,this.structuredInput)this.request(this.action.name,this.requestArgs).then(this.onResponse).catch(this.onError).finally(this.onDone);else try{const e=JSON.parse(this.rawRequest);this.execute(e).then(this.onResponse).catch(this.onError).finally(this.onDone)}catch(e){this.notify({error:!0,title:"Invalid JSON request",text:e.toString()})}},toRequest(e){return{type:"request",action:e.name,args:this.requestArgs}},emitInput(e){e=e||this.value,e&&this.$emit("input",this.toRequest(e))},onClick(e){"a"===e.target.tagName.toLowerCase()&&(e.stopPropagation(),e.preventDefault(),window.open(e.target.getAttribute("href","_blank")))},onValueChanged(e){if(e=e||this.value,!e)return;const t=e.name||e.action;this.$nextTick((()=>{this.updateAction(t,{force:!0,args:e.args||{},extraArgs:e.extraArgs||[]})}))},onSubmit(){this.isValidAction&&(this.withSave?this.emitInput(this.action):this.executeAction())}},watch:{value:{immediate:!0,handler(e){this.onValueChanged(e)}}},async mounted(){await this.refresh(),await this.onValueChanged()}};const ze=(0,re.Z)(He,[["render",S],["__scopeId","data-v-48afe350"]]);var We=ze},803:function(e,t,n){n.d(t,{Z:function(){return x}});var s=n(6252),i=n(3577);const a=e=>((0,s.dD)("data-v-801045b2"),e=e(),(0,s.Cn)(),e),o={class:"response"},r={key:0},l={class:"title"},c={class:"buttons"},u=a((()=>(0,s._)("i",{class:"fas fa-clipboard"},null,-1))),d=[u],h={key:1,class:"output response"},p=["innerHTML"],g=["textContent"],m={key:2,class:"output error"},v=["textContent"];function b(e,t,n,a,u,b){return(0,s.wg)(),(0,s.iD)("section",o,[null!=n.error||null!=n.response?((0,s.wg)(),(0,s.iD)("h2",r,[(0,s._)("span",l,(0,i.zw)(null!=n.error?"Error":"Output"),1),(0,s._)("span",c,[(0,s._)("button",{type:"button",title:"Copy to clipboard",onClick:t[0]||(t[0]=t=>e.copyToClipboard(n.response))},d)])])):(0,s.kq)("",!0),null!=n.response?((0,s.wg)(),(0,s.iD)("div",h,[(0,s._)("pre",null,[null!=b.jsonResponse?((0,s.wg)(),(0,s.iD)("code",{key:0,innerHTML:b.jsonResponse},null,8,p)):((0,s.wg)(),(0,s.iD)("code",{key:1,textContent:(0,i.zw)(n.response)},null,8,g))])])):null!=n.error?((0,s.wg)(),(0,s.iD)("div",m,[(0,s._)("pre",{textContent:(0,i.zw)(n.error)},null,8,v)])):(0,s.kq)("",!0)])}n(8783),n(3465);var y=n(637),k=n(8637),f={name:"Response",mixins:[k.Z],props:{response:String,error:String},computed:{isJSON(){try{return null!=JSON.parse(this.response)}catch(e){return!1}},jsonResponse(){return this.isJSON?y.Z.highlight(this.response,{language:"json"}).value:null}}},w=n(3744);const A=(0,w.Z)(f,[["render",b],["__scopeId","data-v-801045b2"]]);var x=A}}]);
//# sourceMappingURL=1807.564d1fef.js.map