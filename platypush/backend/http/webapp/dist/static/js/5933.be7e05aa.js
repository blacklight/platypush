(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[5933,2545],{9265:function(t,e,n){"use strict";n.d(e,{A:function(){return f}});var s=n(641),i=n(3751),o=n(33);const a={class:"dropdown-container"},r=["title"],l=["textContent"];function c(t,e,n,c,u,d){const p=(0,s.g2)("DropdownBody");return(0,s.uX)(),(0,s.CE)("div",a,[(0,s.Lk)("button",{title:n.title,ref:"button",onClick:e[0]||(e[0]=(0,i.D$)((t=>d.toggle(t)),["stop"]))},[n.iconClass?((0,s.uX)(),(0,s.CE)("i",{key:0,class:(0,o.C4)(["icon",n.iconClass])},null,2)):(0,s.Q3)("",!0),n.text?((0,s.uX)(),(0,s.CE)("span",{key:1,class:"text",textContent:(0,o.v_)(n.text)},null,8,l)):(0,s.Q3)("",!0)],8,r),(0,s.Lk)("div",{class:(0,o.C4)(["body-container",{hidden:!u.visible}]),ref:"dropdownContainer"},[(0,s.bF)(p,{id:n.id,keepOpenOnItemClick:n.keepOpenOnItemClick,style:(0,o.Tr)(n.style),ref:"dropdown",onClick:d.onClick},{default:(0,s.k6)((()=>[(0,s.RG)(t.$slots,"default",{},void 0,!0)])),_:3},8,["id","keepOpenOnItemClick","style","onClick"])],2)])}var u=n(4200),d=n(2537),p={components:{DropdownBody:u.A},emits:["click"],props:{id:{type:String},iconClass:{default:"fa fa-ellipsis-h"},text:{type:String},title:{type:String},keepOpenOnItemClick:{type:Boolean,default:!1},style:{type:Object,default:()=>({})}},data(){return{visible:!1}},computed:{button(){const t=this.$refs.button?.$el;return t?t.querySelector("button"):this.$refs.button},buttonStyle(){return this.button?getComputedStyle(this.button):{}},buttonWidth(){return parseFloat(this.buttonStyle.width||0)},buttonHeight(){return parseFloat(this.buttonStyle.height||0)}},methods:{documentClickHndl(t){if(!this.visible)return;let e=t.target;while(e){if(e.classList.contains("dropdown"))return;e=e.parentElement}this.close()},getDropdownWidth(){const t=this.$refs.dropdown?.$el;return t?parseFloat(getComputedStyle(t).width):0},getDropdownHeight(){const t=this.$refs.dropdown?.$el;return t?parseFloat(getComputedStyle(t).height):0},onClick(t){return this.keepOpenOnItemClick||this.close(),"A"===t.target.tagName?(t.preventDefault(),!1):t.defaultPrevented?(t.stopPropagation(),!1):void 0},close(){this.visible=!1,document.removeEventListener("click",this.documentClickHndl),d.j.emit("dropdown-close")},open(){document.addEventListener("click",this.documentClickHndl);const t=this.$refs.dropdown?.$el;t.parentElement||this.$el.appendChild(t),this.visible=!0,this.$nextTick(this.adjustDropdownPos)},adjustDropdownPos(){const t=this.button.getBoundingClientRect(),e={left:t.left+window.scrollX,top:t.top+window.scrollY},n={left:e.left,top:e.top+this.buttonHeight},s=this.getDropdownWidth(),i=this.getDropdownHeight();if(n.left+s>(window.innerWidth+window.scrollX)/2&&(n.left-=s-this.buttonWidth),n.top+i>(window.innerHeight+window.scrollY)/2){let t=n.top-(i+this.buttonHeight-10);t<0&&(t=0),n.top=t}const o=this.$refs.dropdown.$el;o.classList.add("fade-in"),o.style.top=`${n.top}px`,o.style.left=`${n.left}px`,d.j.emit("dropdown-open",this.$refs.dropdown)},toggle(t){t?.stopPropagation(),this.$emit("click",t),this.visible?this.close():this.open()},onKeyUp(t){t.stopPropagation(),"Escape"===t.key&&this.close()}},mounted(){document.body.addEventListener("keyup",this.onKeyUp)},unmounted(){document.body.removeEventListener("keyup",this.onKeyUp)}},g=n(6262);const h=(0,g.A)(p,[["render",c],["__scopeId","data-v-3f1ad726"]]);var f=h},4200:function(t,e,n){"use strict";n.d(e,{A:function(){return u}});var s=n(641),i=n(33);const o=["id"];function a(t,e,n,a,r,l){return(0,s.uX)(),(0,s.CE)("div",{class:"dropdown",id:n.id,style:(0,i.Tr)(n.style),onClick:e[0]||(e[0]=e=>t.$emit("click",e))},[(0,s.RG)(t.$slots,"default",{},void 0,!0)],12,o)}var r={emits:["click"],props:{id:{type:String},keepOpenOnItemClick:{type:Boolean,default:!1},style:{type:Object,default:()=>({})}}},l=n(6262);const c=(0,l.A)(r,[["render",a],["__scopeId","data-v-24c5aa28"]]);var u=c},9612:function(t,e,n){"use strict";n.d(e,{A:function(){return h}});var s=n(641),i=n(33);const o=["title"],a={key:0,class:"col-2 icon"},r=["textContent"];function l(t,e,n,l,c,u){const d=(0,s.g2)("Icon");return(0,s.uX)(),(0,s.CE)("div",{class:(0,i.C4)(["row item",{...u.itemClass_,disabled:n.disabled}]),title:n.hoverText,onClick:e[0]||(e[0]=(...t)=>u.clicked&&u.clicked(...t))},[n.iconClass?.length||n.iconUrl?.length?((0,s.uX)(),(0,s.CE)("div",a,[(0,s.bF)(d,{class:(0,i.C4)(n.iconClass),url:n.iconUrl},null,8,["class","url"])])):(0,s.Q3)("",!0),(0,s.Lk)("div",{class:(0,i.C4)(["text",{"col-10":null!=n.iconClass}]),textContent:(0,i.v_)(n.text)},null,10,r)],10,o)}var c=n(3778),u=n(2537),d={components:{Icon:c.A},emits:["click","input"],props:{iconClass:{type:String},iconUrl:{type:String},text:{type:String},hoverText:{type:String,default:null},disabled:{type:Boolean,default:!1},itemClass:{}},computed:{itemClass_(){return"string"===typeof this.itemClass?{[this.itemClass]:!0}:this.itemClass}},methods:{clicked(t){if(this.$parent.keepOpenOnItemClick||u.j.emit("dropdown-close"),this.disabled)return t.stopPropagation(),t.preventDefault(),!1;this.$emit("input",t)}}},p=n(6262);const g=(0,p.A)(d,[["render",l],["__scopeId","data-v-2babe09c"]]);var h=g},3778:function(t,e,n){"use strict";n.d(e,{A:function(){return d}});var s=n(641),i=n(33);const o={class:"icon-container"},a=["src","alt"];function r(t,e,n,r,l,c){return(0,s.uX)(),(0,s.CE)("div",o,[n.url?.length?((0,s.uX)(),(0,s.CE)("img",{key:0,class:"icon",src:n.url,alt:n.alt},null,8,a)):c.className?.length?((0,s.uX)(),(0,s.CE)("i",{key:1,class:(0,i.C4)(["icon",c.className]),style:(0,i.Tr)({color:n.color})},null,6)):(0,s.Q3)("",!0)])}var l={props:{class:{type:String},url:{type:String},color:{type:String,default:""},alt:{type:String,default:""}},computed:{className(){return this.class}}},c=n(6262);const u=(0,c.A)(l,[["render",r],["__scopeId","data-v-706a3bd1"]]);var d=u},1968:function(t,e,n){"use strict";n.d(e,{A:function(){return d}});var s=n(641);const i={class:"restart-btn-container"};function o(t,e,n,o,a,r){const l=(0,s.g2)("ConfirmDialog");return(0,s.uX)(),(0,s.CE)("div",i,[(0,s.bF)(l,{ref:"modal",onInput:r.restart},{default:(0,s.k6)((()=>e[2]||(e[2]=[(0,s.eW)(" Are you sure that you want to restart the application? ")]))),_:1},8,["onInput"]),(0,s.Lk)("button",{class:"btn btn-default restart-btn",onClick:e[0]||(e[0]=(...t)=>r.showDialog&&r.showDialog(...t)),onTouch:e[1]||(e[1]=(...t)=>r.showDialog&&r.showDialog(...t))},e[3]||(e[3]=[(0,s.Lk)("i",{class:"fas fa-redo-alt"},null,-1),(0,s.eW)("   Restart Application ")]),32)])}var a=n(3538),r=n(2002),l={name:"RestartButton",components:{ConfirmDialog:a.A},mixins:[r.A],methods:{showDialog(){this.$refs.modal.show()},async restart(){await this.request("application.restart")}}},c=n(6262);const u=(0,c.A)(l,[["render",o],["__scopeId","data-v-2edff8b7"]]);var d=u},5054:function(t,e,n){"use strict";n.d(e,{A:function(){return d}});var s=n(641),i=n(33);const o={key:0,class:"icon"};function a(t,e,n,a,r,l){const c=(0,s.g2)("Icon");return(0,s.uX)(),(0,s.CE)("div",{class:(0,i.C4)(["tab",n.selected?"selected":""]),onClick:e[0]||(e[0]=e=>t.$emit("input"))},[n.iconClass?.length||n.iconUrl?.length?((0,s.uX)(),(0,s.CE)("span",o,[(0,s.bF)(c,{class:(0,i.C4)(n.iconClass),url:n.iconUrl},null,8,["class","url"])])):(0,s.Q3)("",!0),e[1]||(e[1]=(0,s.eW)("   ")),(0,s.RG)(t.$slots,"default",{},void 0,!0)],2)}var r=n(3778),l={name:"Tab",components:{Icon:r.A},emits:["input"],props:{selected:{type:Boolean,default:!1},iconClass:{type:String},iconUrl:{type:String}}},c=n(6262);const u=(0,c.A)(l,[["render",a],["__scopeId","data-v-f3217d34"]]);var d=u},3556:function(t,e,n){"use strict";n.d(e,{A:function(){return c}});var s=n(641);const i={class:"tabs"};function o(t,e,n,o,a,r){return(0,s.uX)(),(0,s.CE)("div",i,[(0,s.RG)(t.$slots,"default",{},void 0,!0)])}var a={name:"Tabs"},r=n(6262);const l=(0,r.A)(a,[["render",o],["__scopeId","data-v-f4300bb0"]]);var c=l},5933:function(t,e,n){"use strict";n.r(e),n.d(e,{default:function(){return Xt}});var s=n(641);const i={class:"app-container"},o={class:"tabs"},a={class:"content"};function r(t,e,n,r,l,c){const u=(0,s.g2)("Tab"),d=(0,s.g2)("Tabs"),p=(0,s.g2)("Actions"),g=(0,s.g2)("Events");return(0,s.uX)(),(0,s.CE)("div",i,[(0,s.Lk)("div",o,[(0,s.bF)(d,null,{default:(0,s.k6)((()=>[(0,s.bF)(u,{selected:"actions"===l.selectedView,"icon-class":"fas fa-cogs",onInput:e[0]||(e[0]=t=>l.selectedView="actions")},{default:(0,s.k6)((()=>e[2]||(e[2]=[(0,s.eW)(" Actions ")]))),_:1},8,["selected"]),(0,s.bF)(u,{selected:"events"===l.selectedView,"icon-class":"fas fa-bolt",onInput:e[1]||(e[1]=t=>l.selectedView="events")},{default:(0,s.k6)((()=>e[3]||(e[3]=[(0,s.eW)(" Events ")]))),_:1},8,["selected"])])),_:1})]),(0,s.Lk)("div",a,["actions"===l.selectedView?((0,s.uX)(),(0,s.Wv)(p,{key:0})):"events"===l.selectedView?((0,s.uX)(),(0,s.Wv)(g,{key:1})):(0,s.Q3)("",!0)])])}const l={class:"app-container"},c={class:"btn-container"},u={class:"btn-container"};function d(t,e,n,i,o,a){const r=(0,s.g2)("RestartButton"),d=(0,s.g2)("StopButton");return(0,s.uX)(),(0,s.CE)("div",l,[(0,s.Lk)("div",c,[(0,s.bF)(r)]),(0,s.Lk)("div",u,[(0,s.bF)(d)])])}var p=n(1968);const g={class:"stop-btn-container"};function h(t,e,n,i,o,a){const r=(0,s.g2)("ConfirmDialog");return(0,s.uX)(),(0,s.CE)("div",g,[(0,s.bF)(r,{ref:"modal",onInput:a.stop},{default:(0,s.k6)((()=>e[2]||(e[2]=[(0,s.eW)(" Are you sure that you want to stop the application? "),(0,s.Lk)("br",null,null,-1),(0,s.Lk)("br",null,null,-1),(0,s.Lk)("span",{class:"text-danger"}," This will stop the application and you will not be able to restart it through the Web interface! ",-1)]))),_:1},8,["onInput"]),(0,s.Lk)("button",{class:"btn btn-default stop-btn",onClick:e[0]||(e[0]=(...t)=>a.showDialog&&a.showDialog(...t)),onTouch:e[1]||(e[1]=(...t)=>a.showDialog&&a.showDialog(...t))},e[3]||(e[3]=[(0,s.Lk)("i",{class:"fas fa-stop"},null,-1),(0,s.eW)("   Stop Application ")]),32)])}var f=n(3538),v=n(2002),k={name:"StopButton",components:{ConfirmDialog:f.A},mixins:[v.A],methods:{showDialog(){this.$refs.modal.show()},async stop(){await this.request("application.stop")}}},y=n(6262);const m=(0,y.A)(k,[["render",h],["__scopeId","data-v-1eab04fa"]]);var b=m,w={mixins:[v.A],components:{RestartButton:p.A,StopButton:b},mounted(){this.setUrlArgs({view:"actions"})}};const C=(0,y.A)(w,[["render",d],["__scopeId","data-v-34f6e73c"]]);var L=C,x=n(3751),A=n(33);const E={class:"events-container"},_={class:"header"},S={class:"filter-container"},I={class:"btn-container"},D=["title"],O={class:"body",ref:"body"},$={class:"footer"};function j(t,e,n,i,o,a){const r=(0,s.g2)("DropdownItem"),l=(0,s.g2)("Dropdown"),c=(0,s.g2)("EventRenderer"),u=(0,s.g2)("Loading");return(0,s.uX)(),(0,s.CE)("div",E,[(0,s.Lk)("div",_,[(0,s.Lk)("div",S,[(0,s.bo)((0,s.Lk)("input",{type:"text","onUpdate:modelValue":e[0]||(e[0]=t=>o.filter=t),placeholder:"Filter events"},null,512),[[x.Jo,o.filter]])]),(0,s.Lk)("div",I,[(0,s.Lk)("button",{onClick:e[1]||(e[1]=t=>o.running=!o.running),title:(o.running?"Pause":"Start")+" capturing"},[(0,s.Lk)("i",{class:(0,A.C4)(o.running?"fa fa-pause":"fa fa-play")},null,2)],8,D),(0,s.bF)(l,{title:"Actions","icon-class":"fa fa-ellipsis-h"},{default:(0,s.k6)((()=>[(0,s.bF)(r,{text:o.follow?"Unfollow":"Follow","icon-class":"fa fa-eye",onInput:e[2]||(e[2]=t=>o.follow=!o.follow)},null,8,["text"]),(0,s.bF)(r,{text:"Export Events","icon-class":"fa fa-download",onInput:a.download},null,8,["onInput"]),(0,s.bF)(r,{text:"Clear Events","icon-class":"fa fa-trash",onInput:a.clear},null,8,["onInput"])])),_:1})])]),(0,s.Lk)("div",O,[((0,s.uX)(!0),(0,s.CE)(s.FK,null,(0,s.pI)(a.filteredEvents,((t,e)=>((0,s.uX)(),(0,s.Wv)(c,{key:e,index:e,output:t},null,8,["index","output"])))),128))],512),(0,s.Lk)("div",$,[o.running?((0,s.uX)(),(0,s.Wv)(u,{key:0})):(0,s.Q3)("",!0)])])}n(4603),n(7566),n(1102),n(4114);var X=n(9265),F=n(9612);const T=["href"],U={class:"header"},W={class:"col-11 title"},R={class:"time-container"},B={class:"time"},H={class:"type-container"},V={class:"type"},P={class:"col-1 buttons"},N={class:"body"},J={class:"row time"},Q={class:"value scalar"},q={class:"row type"},z={class:"value scalar"},K=["href"],G={class:"row id"},Y={class:"value scalar"},M={class:"row origin"},Z={class:"value scalar"},tt={class:"row args"},et={class:"value object"},nt={key:0,class:"editor-container"};function st(t,e,n,i,o,a){const r=(0,s.g2)("DropdownItem"),l=(0,s.g2)("Dropdown"),c=(0,s.g2)("ObjectRenderer"),u=(0,s.g2)("FileEditor");return(0,s.uX)(),(0,s.CE)("a",{class:(0,A.C4)(["event renderer",{even:t.index%2===0,odd:t.index%2!==0,expanded:t.expanded}]),href:a.href,onClick:e[3]||(e[3]=(0,x.D$)(((...t)=>a.onClick&&a.onClick(...t)),["prevent","stop"]))},[(0,s.Lk)("div",U,[(0,s.Lk)("div",W,[(0,s.Lk)("div",R,[e[4]||(e[4]=(0,s.eW)(" [")),(0,s.Lk)("span",B,(0,A.v_)(a.time),1),e[5]||(e[5]=(0,s.eW)("]   "))]),(0,s.Lk)("div",H,[(0,s.Lk)("span",V,(0,A.v_)(a.type),1)])]),(0,s.Lk)("div",P,[(0,s.bF)(l,{title:"Actions","icon-class":"fa fa-ellipsis-h"},{default:(0,s.k6)((()=>[(0,s.bF)(r,{text:"Raw Event","icon-class":"fa fa-file-code",onInput:e[0]||(e[0]=t=>o.showEditor=!0)}),(0,s.bF)(r,{text:"Copy to Clipboard","icon-class":"fa fa-copy",onInput:a.copy},null,8,["onInput"])])),_:1})])]),(0,s.Lk)("div",N,[t.expanded?((0,s.uX)(),(0,s.CE)("div",{key:0,class:"expanded",onClick:e[1]||(e[1]=(0,x.D$)((()=>{}),["stop"]))},[(0,s.Lk)("div",J,[e[6]||(e[6]=(0,s.Lk)("span",{class:"key"},[(0,s.Lk)("i",{class:"fas fa-clock"}),(0,s.eW)(" Time")],-1)),(0,s.Lk)("span",Q,(0,A.v_)(a.datetime),1)]),(0,s.Lk)("div",q,[e[7]||(e[7]=(0,s.Lk)("span",{class:"key"},[(0,s.Lk)("i",{class:"fas fa-tag"}),(0,s.eW)(" Type")],-1)),(0,s.Lk)("span",z,[a.typeDocHref?((0,s.uX)(),(0,s.CE)("a",{key:0,href:a.typeDocHref,target:"_blank"},(0,A.v_)(a.type),9,K)):(0,s.Q3)("",!0)])]),(0,s.Lk)("div",G,[e[8]||(e[8]=(0,s.Lk)("span",{class:"key"},[(0,s.Lk)("i",{class:"fas fa-id-badge"}),(0,s.eW)(" ID")],-1)),(0,s.Lk)("span",Y,(0,A.v_)(t.output?.id),1)]),(0,s.Lk)("div",M,[e[9]||(e[9]=(0,s.Lk)("span",{class:"key"},[(0,s.Lk)("i",{class:"fas fa-map-marker-alt"}),(0,s.eW)(" Origin")],-1)),(0,s.Lk)("span",Z,(0,A.v_)(t.output?.origin),1)]),(0,s.Lk)("div",tt,[e[10]||(e[10]=(0,s.Lk)("span",{class:"key"},[(0,s.Lk)("i",{class:"fas fa-cogs"}),(0,s.eW)(" Args")],-1)),(0,s.Lk)("span",et,[(0,s.bF)(c,{output:t.output.args},null,8,["output"])])])])):(0,s.Q3)("",!0)]),o.showEditor?((0,s.uX)(),(0,s.CE)("div",nt,[(0,s.bF)(u,{file:a.type.split(".").pop(),text:a.indentedOutput,visible:!0,uppercase:!1,"with-save":!1,"content-type":"json",onClose:e[2]||(e[2]=t=>o.showEditor=!1)},null,8,["file","text"])])):(0,s.Q3)("",!0)],10,T)}var it=n(1367),ot=(n(1545),n(6669),n(9878)),at={mixins:[v.A],props:{output:{type:[Object,String],required:!0},filter:{type:String,default:""},index:{type:Number,default:0}},data(){return{expanded:!1}},computed:{highlightedText(){return ot.A.highlight(this.outputString,{language:this.isJson?"json":"plaintext"}).value},isJson(){if("object"===typeof this.output)return!0;try{return JSON.parse(this.output),!0}catch(t){return!1}},outputString(){if(!Object.keys(this.output||{})?.length)return"";try{return JSON.stringify(this.output,null,this.expanded?2:0)}catch(t){return this.output}}}};const rt=at;var lt=rt;const ct=["href"],ut={key:0,class:"compact"},dt=["textContent"],pt=["textContent"],gt={key:1,class:"expanded"},ht={class:"rows"},ft=["textContent"],vt=["textContent"],kt={key:1,class:"value object"};function yt(t,e,n,i,o,a){const r=(0,s.g2)("ObjectRenderer",!0);return(0,s.uX)(),(0,s.CE)("a",{class:"object renderer",href:t.$route.fullPath,onClick:e[0]||(e[0]=(0,x.D$)(((...t)=>a.onClick&&a.onClick(...t)),["prevent","stop"]))},[t.expanded?((0,s.uX)(),(0,s.CE)("div",gt,[e[3]||(e[3]=(0,s.Lk)("i",{class:"toggler fas fa-caret-down"},null,-1)),(0,s.Lk)("div",ht,[((0,s.uX)(!0),(0,s.CE)(s.FK,null,(0,s.pI)(t.output,((t,e,n)=>((0,s.uX)(),(0,s.CE)("div",{class:(0,A.C4)(["row",{even:n%2===0,odd:n%2!==0,args:t instanceof Object||Array.isArray(t)}]),key:e},[(0,s.Lk)("span",{class:"key",textContent:(0,A.v_)(e)},null,8,ft),t instanceof Object||Array.isArray(t)?((0,s.uX)(),(0,s.CE)("span",kt,[(0,s.bF)(r,{output:t},null,8,["output"])])):((0,s.uX)(),(0,s.CE)("span",{key:0,class:"value scalar",textContent:(0,A.v_)(t)},null,8,vt))],2)))),128))])])):((0,s.uX)(),(0,s.CE)("div",ut,[e[1]||(e[1]=(0,s.Lk)("i",{class:"toggler fas fa-caret-right"},null,-1)),(0,s.Lk)("span",{class:"delimiter",textContent:(0,A.v_)("object"===typeof t.output?"{":"[")},null,8,dt),e[2]||(e[2]=(0,s.Lk)("span",{class:"ellipsis"},"...",-1)),(0,s.Lk)("span",{class:"delimiter",textContent:(0,A.v_)("object"===typeof t.output?"}":"]")},null,8,pt)]))],8,ct)}var mt={name:"ObjectRenderer",mixins:[lt],methods:{onClick(){this.expanded=!this.expanded}}};const bt=(0,y.A)(mt,[["render",yt],["__scopeId","data-v-01df4175"]]);var wt=bt,Ct={mixins:[lt],components:{Dropdown:X.A,DropdownItem:F.A,FileEditor:it.A,ObjectRenderer:wt},data(){return{showEditor:!1}},computed:{datetime(){const t=this.output?.timestamp||this.output?._timestamp;return t?this.formatDateTime(t):""},indentedOutput(){if(!Object.keys(this.output||{})?.length)return"";try{return JSON.stringify(this.output,null,2)}catch(t){return this.output}},time(){const t=this.output?.timestamp||this.output?._timestamp;return t?this.formatTime(t):""},href(){const t=this.$route.fullPath;return t.match(/&index=\d+/)?t.replace(/&index=\d+/,`&index=${this.index}`):t+(null!=this.index?`&index=${this.index}`:"")},type(){return this.output?.args?.type},typeDocHref(){if(!this.type?.length)return"";const t=this.type.replace(/^platypush\.message\.event\./,"").split("."),e=t.splice(0,t.length-1).join(".");return`https://docs.platypush.tech/platypush/events/${e}.html#${this.type}`}},methods:{async copy(){await this.copyToClipboard(this.indentedOutput)},onClick(){this.expanded=!this.expanded,this.setUrlArgs({index:this.expanded&&null!=this.index?this.index:void 0})}},mounted(){const t=this.getUrlArgs();t.index==this.index?.toString()&&(this.expanded=!0)}};const Lt=(0,y.A)(Ct,[["render",st],["__scopeId","data-v-6cdb0134"]]);var xt=Lt,At=n(9828),Et=n(2537),_t={mixins:[v.A],components:{Dropdown:X.A,DropdownItem:F.A,EventRenderer:xt,Loading:At.A},data(){return{filter:"",follow:!0,output:[],running:!0,error:null}},computed:{filteredEvents(){const t=this.filter?.toLowerCase();return Object.keys(this.serializedEvents).filter((e=>!t?.length||this.serializedEvents[e].includes(t))).map((t=>this.outputObjects[t]))},outputString(){return this.outputStrings.join("\n")},outputObjects(){return this.output.map((t=>{try{return JSON.parse(t)}catch(e){return t}}))},outputStrings(){return this.output.map((t=>{try{return JSON.stringify(t)}catch(e){return t}}))},serializedEvents(){return this.outputObjects.map((t=>{try{return JSON.stringify(t).toLowerCase()}catch(e){return t}}))}},methods:{clear(){this.output=[]},download(){const t=new Blob([this.outputString],{type:"application/json"}),e=URL.createObjectURL(t),n=document.createElement("a");n.href=e,n.download=`events-${(new Date).toISOString()}.json`,n.click(),URL.revokeObjectURL(e)},onEvent(t){this.running&&this.output.push(t)}},watch:{output:{deep:!0,handler(){this.follow&&this.$nextTick((()=>{this.$refs.body.scrollTop=this.$refs.body.scrollHeight}))}}},mounted(){this.setUrlArgs({view:"events"}),Et.j.on("event",this.onEvent)}};const St=(0,y.A)(_t,[["render",j],["__scopeId","data-v-175e1222"]]);var It=St,Dt=n(3556),Ot=n(5054),$t={mixins:[v.A],components:{Actions:L,Events:It,Tab:Ot.A,Tabs:Dt.A},data(){return{selectedView:"actions"}},methods:{setView(t){if(!t?.length){const e=this.getUrlArgs();e.view?.length&&(t=e.view)}t?.length&&(this.selectedView=t)}},watch:{$route(){this.setView()},selectedView(){this.setUrlArgs({view:this.selectedView})}},created(){this.setView()}};const jt=(0,y.A)($t,[["render",r],["__scopeId","data-v-63d59e12"]]);var Xt=jt},2106:function(t,e,n){"use strict";var s=n(283),i=n(4913);t.exports=function(t,e,n){return n.get&&s(n.get,e,{getter:!0}),n.set&&s(n.set,e,{setter:!0}),i.f(t,e,n)}},2812:function(t){"use strict";var e=TypeError;t.exports=function(t,n){if(t<n)throw new e("Not enough arguments");return t}},4603:function(t,e,n){"use strict";var s=n(6840),i=n(9504),o=n(655),a=n(2812),r=URLSearchParams,l=r.prototype,c=i(l.append),u=i(l["delete"]),d=i(l.forEach),p=i([].push),g=new r("a=1&a=2&b=3");g["delete"]("a",1),g["delete"]("b",void 0),g+""!=="a=2"&&s(l,"delete",(function(t){var e=arguments.length,n=e<2?void 0:arguments[1];if(e&&void 0===n)return u(this,t);var s=[];d(this,(function(t,e){p(s,{key:e,value:t})})),a(e,1);var i,r=o(t),l=o(n),g=0,h=0,f=!1,v=s.length;while(g<v)i=s[g++],f||i.key===r?(f=!0,u(this,i.key)):h++;while(h<v)i=s[h++],i.key===r&&i.value===l||c(this,i.key,i.value)}),{enumerable:!0,unsafe:!0})},7566:function(t,e,n){"use strict";var s=n(6840),i=n(9504),o=n(655),a=n(2812),r=URLSearchParams,l=r.prototype,c=i(l.getAll),u=i(l.has),d=new r("a=1");!d.has("a",2)&&d.has("a",void 0)||s(l,"has",(function(t){var e=arguments.length,n=e<2?void 0:arguments[1];if(e&&void 0===n)return u(this,t);var s=c(this,t);a(e,1);var i=o(n),r=0;while(r<s.length)if(s[r++]===i)return!0;return!1}),{enumerable:!0,unsafe:!0})},1102:function(t,e,n){"use strict";var s=n(3724),i=n(9504),o=n(2106),a=URLSearchParams.prototype,r=i(a.forEach);s&&!("size"in a)&&o(a,"size",{get:function(){var t=0;return r(this,(function(){t++})),t},configurable:!0,enumerable:!0})},3094:function(t,e,n){var s=n(8416);s.registerLanguage("xml",n(114)),s.registerLanguage("bash",n(8641)),s.registerLanguage("c",n(722)),s.registerLanguage("cpp",n(6570)),s.registerLanguage("csharp",n(7120)),s.registerLanguage("css",n(8612)),s.registerLanguage("markdown",n(602)),s.registerLanguage("diff",n(8596)),s.registerLanguage("ruby",n(5015)),s.registerLanguage("go",n(9777)),s.registerLanguage("graphql",n(7474)),s.registerLanguage("ini",n(1533)),s.registerLanguage("java",n(4895)),s.registerLanguage("javascript",n(6035)),s.registerLanguage("json",n(621)),s.registerLanguage("kotlin",n(2838)),s.registerLanguage("less",n(8330)),s.registerLanguage("lua",n(3873)),s.registerLanguage("makefile",n(7667)),s.registerLanguage("perl",n(946)),s.registerLanguage("objectivec",n(943)),s.registerLanguage("php",n(3111)),s.registerLanguage("php-template",n(1726)),s.registerLanguage("plaintext",n(9040)),s.registerLanguage("python",n(1117)),s.registerLanguage("python-repl",n(2664)),s.registerLanguage("r",n(8129)),s.registerLanguage("rust",n(5409)),s.registerLanguage("scss",n(1611)),s.registerLanguage("shell",n(8813)),s.registerLanguage("sql",n(315)),s.registerLanguage("swift",n(1496)),s.registerLanguage("yaml",n(5588)),s.registerLanguage("typescript",n(8640)),s.registerLanguage("vbnet",n(8928)),s.registerLanguage("wasm",n(9351)),s.HighlightJS=s,s.default=s,t.exports=s},1545:function(t,e,n){"use strict";n(3094)}}]);
//# sourceMappingURL=5933.be7e05aa.js.map