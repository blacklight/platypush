"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[28],{226:function(t,e,n){n.d(e,{A:function(){return l}});n(4114);var s=n(2002),o={name:"Utils",mixins:[s.A],computed:{audioExtensions(){return new Set(["3gp","aa","aac","aax","act","aiff","amr","ape","au","awb","dct","dss","dvf","flac","gsm","iklax","ivs","m4a","m4b","m4p","mmf","mp3","mpc","msv","nmf","nsf","ogg,","opus","ra,","raw","sln","tta","vox","wav","wma","wv","webm","8svx"])},videoExtensions(){return new Set(["webm","mkv","flv","flv","vob","ogv","ogg","drc","gif","gifv","mng","avi","mts","m2ts","mov","qt","wmv","yuv","rm","rmvb","asf","amv","mp4","m4p","m4v","mpg","mp2","mpeg","mpe","mpv","mpg","mpeg","m2v","m4v","svi","3gp","3g2","mxf","roq","nsv","flv","f4v","f4p","f4a","f4b"])},mediaExtensions(){return new Set([...this.videoExtensions,...this.audioExtensions])}},methods:{convertTime(t){t=parseFloat(t);const e={};e.h=""+parseInt(t/3600),e.m=""+parseInt(t/60-60*e.h),e.s=""+parseInt(t-(3600*e.h+60*e.m));for(const s of["m","s"])parseInt(e[s])<10&&(e[s]="0"+e[s]);const n=[];return parseInt(e.h)&&n.push(e.h),n.push(e.m,e.s),n.join(":")},async startStreaming(t,e,n=!1){let s=t,o=null;t instanceof Object?(s=t.url,o=t.subtitles):t={url:s};const i=await this.request(`${e}.start_streaming`,{media:s,subtitles:o,download:n});return{...t,...i}},async stopStreaming(t,e){await this.request(`${e}.stop_streaming`,{media_id:t})}}};const i=o;var l=i},9265:function(t,e,n){n.d(e,{A:function(){return f}});var s=n(641),o=n(3751),i=n(33);const l={class:"dropdown-container"},r=["title"],a=["textContent"];function c(t,e,n,c,d,p){const u=(0,s.g2)("DropdownBody");return(0,s.uX)(),(0,s.CE)("div",l,[(0,s.Lk)("button",{title:n.title,ref:"button",onClick:e[0]||(e[0]=(0,o.D$)((t=>p.toggle(t)),["stop"]))},[n.iconClass?((0,s.uX)(),(0,s.CE)("i",{key:0,class:(0,i.C4)(["icon",n.iconClass])},null,2)):(0,s.Q3)("",!0),n.text?((0,s.uX)(),(0,s.CE)("span",{key:1,class:"text",textContent:(0,i.v_)(n.text)},null,8,a)):(0,s.Q3)("",!0)],8,r),(0,s.Lk)("div",{class:(0,i.C4)(["body-container",{hidden:!d.visible}]),ref:"dropdownContainer"},[(0,s.bF)(u,{id:n.id,keepOpenOnItemClick:n.keepOpenOnItemClick,style:(0,i.Tr)(n.style),ref:"dropdown",onClick:p.onClick},{default:(0,s.k6)((()=>[(0,s.RG)(t.$slots,"default",{},void 0,!0)])),_:3},8,["id","keepOpenOnItemClick","style","onClick"])],2)])}var d=n(4200),p=n(2537),u={components:{DropdownBody:d.A},emits:["click"],props:{id:{type:String},iconClass:{default:"fa fa-ellipsis-h"},text:{type:String},title:{type:String},keepOpenOnItemClick:{type:Boolean,default:!1},style:{type:Object,default:()=>({})}},data(){return{visible:!1}},computed:{button(){const t=this.$refs.button?.$el;return t?t.querySelector("button"):this.$refs.button},buttonStyle(){return this.button?getComputedStyle(this.button):{}},buttonWidth(){return parseFloat(this.buttonStyle.width||0)},buttonHeight(){return parseFloat(this.buttonStyle.height||0)}},methods:{documentClickHndl(t){if(!this.visible)return;let e=t.target;while(e){if(e.classList.contains("dropdown"))return;e=e.parentElement}this.close()},getDropdownWidth(){const t=this.$refs.dropdown?.$el;return t?parseFloat(getComputedStyle(t).width):0},getDropdownHeight(){const t=this.$refs.dropdown?.$el;return t?parseFloat(getComputedStyle(t).height):0},onClick(t){return this.keepOpenOnItemClick||this.close(),"A"===t.target.tagName?(t.preventDefault(),!1):t.defaultPrevented?(t.stopPropagation(),!1):void 0},close(){this.visible=!1,document.removeEventListener("click",this.documentClickHndl),p.j.emit("dropdown-close")},open(){document.addEventListener("click",this.documentClickHndl);const t=this.$refs.dropdown?.$el;t.parentElement||this.$el.appendChild(t),this.visible=!0,this.$nextTick(this.adjustDropdownPos)},adjustDropdownPos(){const t=this.button.getBoundingClientRect(),e={left:t.left+window.scrollX,top:t.top+window.scrollY},n={left:e.left,top:e.top+this.buttonHeight},s=this.getDropdownWidth(),o=this.getDropdownHeight();if(n.left+s>(window.innerWidth+window.scrollX)/2&&(n.left-=s-this.buttonWidth),n.top+o>(window.innerHeight+window.scrollY)/2){let t=n.top-(o+this.buttonHeight-10);t<0&&(t=0),n.top=t}const i=this.$refs.dropdown.$el;i.classList.add("fade-in"),i.style.top=`${n.top}px`,i.style.left=`${n.left}px`,p.j.emit("dropdown-open",this.$refs.dropdown)},toggle(t){t?.stopPropagation(),this.$emit("click",t),this.visible?this.close():this.open()},onKeyUp(t){t.stopPropagation(),"Escape"===t.key&&this.close()}},mounted(){document.body.addEventListener("keyup",this.onKeyUp)},unmounted(){document.body.removeEventListener("keyup",this.onKeyUp)}},m=n(6262);const h=(0,m.A)(u,[["render",c],["__scopeId","data-v-3f1ad726"]]);var f=h},4200:function(t,e,n){n.d(e,{A:function(){return d}});var s=n(641),o=n(33);const i=["id"];function l(t,e,n,l,r,a){return(0,s.uX)(),(0,s.CE)("div",{class:"dropdown",id:n.id,style:(0,o.Tr)(n.style),onClick:e[0]||(e[0]=e=>t.$emit("click",e))},[(0,s.RG)(t.$slots,"default",{},void 0,!0)],12,i)}var r={emits:["click"],props:{id:{type:String},keepOpenOnItemClick:{type:Boolean,default:!1},style:{type:Object,default:()=>({})}}},a=n(6262);const c=(0,a.A)(r,[["render",l],["__scopeId","data-v-24c5aa28"]]);var d=c},9612:function(t,e,n){n.d(e,{A:function(){return h}});var s=n(641),o=n(33);const i=["title"],l={key:0,class:"col-2 icon"},r=["textContent"];function a(t,e,n,a,c,d){const p=(0,s.g2)("Icon");return(0,s.uX)(),(0,s.CE)("div",{class:(0,o.C4)(["row item",{...d.itemClass_,disabled:n.disabled}]),title:n.hoverText,onClick:e[0]||(e[0]=(...t)=>d.clicked&&d.clicked(...t))},[n.iconClass?.length||n.iconUrl?.length?((0,s.uX)(),(0,s.CE)("div",l,[(0,s.bF)(p,{class:(0,o.C4)(n.iconClass),url:n.iconUrl},null,8,["class","url"])])):(0,s.Q3)("",!0),(0,s.Lk)("div",{class:(0,o.C4)(["text",{"col-10":null!=n.iconClass}]),textContent:(0,o.v_)(n.text)},null,10,r)],10,i)}var c=n(3778),d=n(2537),p={components:{Icon:c.A},emits:["click","input"],props:{iconClass:{type:String},iconUrl:{type:String},text:{type:String},hoverText:{type:String,default:null},disabled:{type:Boolean,default:!1},itemClass:{}},computed:{itemClass_(){return"string"===typeof this.itemClass?{[this.itemClass]:!0}:this.itemClass}},methods:{clicked(t){if(this.$parent.keepOpenOnItemClick||d.j.emit("dropdown-close"),this.disabled)return t.stopPropagation(),t.preventDefault(),!1;this.$emit("input",t)}}},u=n(6262);const m=(0,u.A)(p,[["render",a],["__scopeId","data-v-2babe09c"]]);var h=m},7998:function(t,e,n){n.d(e,{A:function(){return p}});var s=n(641),o=n(33);const i=["disabled","title"];function l(t,e,n,l,r,a){const c=(0,s.g2)("Icon");return(0,s.uX)(),(0,s.CE)("div",{class:(0,o.C4)(["floating-btn",a.classes])},[(0,s.Lk)("button",{type:"button",class:(0,o.C4)(["btn btn-primary",n.glow?"with-glow":""]),disabled:n.disabled,title:n.title,onClick:e[0]||(e[0]=e=>t.$emit("click",e))},[(0,s.bF)(c,{class:(0,o.C4)(n.iconClass),url:n.iconUrl},null,8,["class","url"])],10,i)],2)}var r=n(3778),a={components:{Icon:r.A},emits:["click"],props:{disabled:{type:Boolean,default:!1},iconClass:{type:String},iconUrl:{type:String},class:{type:String},title:{type:String},left:{type:Boolean,default:!1},right:{type:Boolean,default:!0},top:{type:Boolean,default:!1},bottom:{type:Boolean,default:!0},glow:{type:Boolean,default:!1}},computed:{classes(){const t={};return this.left?t.left=!0:t.right=!0,this.top?t.top=!0:t.bottom=!0,this.class?.length&&(t[this.class]=!0),t}}},c=n(6262);const d=(0,c.A)(a,[["render",l],["__scopeId","data-v-544409fc"]]);var p=d},3778:function(t,e,n){n.d(e,{A:function(){return p}});var s=n(641),o=n(33);const i={class:"icon-container"},l=["src","alt"];function r(t,e,n,r,a,c){return(0,s.uX)(),(0,s.CE)("div",i,[n.url?.length?((0,s.uX)(),(0,s.CE)("img",{key:0,class:"icon",src:n.url,alt:n.alt},null,8,l)):c.className?.length?((0,s.uX)(),(0,s.CE)("i",{key:1,class:(0,o.C4)(["icon",c.className]),style:(0,o.Tr)({color:n.color})},null,6)):(0,s.Q3)("",!0)])}var a={props:{class:{type:String},url:{type:String},color:{type:String,default:""},alt:{type:String,default:""}},computed:{className(){return this.class}}},c=n(6262);const d=(0,c.A)(a,[["render",r],["__scopeId","data-v-706a3bd1"]]);var p=d}}]);
//# sourceMappingURL=28.a4a0a573.js.map