"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[1367],{6669:function(){},1367:function(e,t,s){s.d(t,{A:function(){return N}});var i=s(641),n=s(33);const o={class:"file-editor-root"},l={class:"modal-body"},a={class:"confirm-dialog-container"};function r(e,t,s,r,h,x){const p=(0,i.g2)("FileEditor"),c=(0,i.g2)("Modal"),d=(0,i.g2)("ConfirmDialog");return(0,i.uX)(),(0,i.CE)("div",o,[(0,i.Lk)("div",{class:(0,n.C4)(["file-editor-modal",{maximized:h.maximized}])},[(0,i.bF)(c,(0,i.v6)(x.proxiedProperties,{ref:"modal",onClose:x.onClose}),{default:(0,i.k6)((()=>[(0,i.Lk)("div",l,[s.file?((0,i.uX)(),(0,i.Wv)(p,{key:0,ref:"fileEditor",file:s.file,"is-new":s.isNew,line:s.line,text:s.text,"content-type":s.contentType,"with-save":s.withSave,onSave:t[0]||(t[0]=t=>e.$emit("save",t))},null,8,["file","is-new","line","text","content-type","with-save"])):(0,i.Q3)("",!0)])])),_:1},16,["onClose"]),(0,i.Lk)("div",a,[(0,i.bF)(d,{ref:"confirmClose",onInput:x.forceClose},{default:(0,i.k6)((()=>[(0,i.eW)(" This file has unsaved changes. Are you sure you want to close it? ")])),_:1},8,["onInput"])])],2)])}s(4114);var h=s(3538),x=s(3751);const p={class:"file-editor"},c={class:"editor-container"},d={key:0,class:"editor-highlight-loading"},y={class:"editor-body"},f={class:"line-numbers",ref:"lineNumbers"},g=["onClick","textContent"],u={ref:"pre"},m=["innerHTML"],v={key:0,class:"selected-line",ref:"selectedLine"};function b(e,t,s,o,l,a){const r=(0,i.g2)("Loading"),h=(0,i.g2)("FloatingButton");return(0,i.uX)(),(0,i.CE)("div",p,[l.loading?((0,i.uX)(),(0,i.Wv)(r,{key:0})):(0,i.Q3)("",!0),(0,i.Lk)("div",c,[a.isProcessing?((0,i.uX)(),(0,i.CE)("div",d,[(0,i.bF)(r)])):(0,i.Q3)("",!0),(0,i.Lk)("div",y,[(0,i.Lk)("div",f,[((0,i.uX)(!0),(0,i.CE)(i.FK,null,(0,i.pI)(a.lines,(e=>((0,i.uX)(),(0,i.CE)("span",{class:(0,n.C4)(["line-number",{selected:l.selectedLine===e}]),key:e,onClick:t=>l.selectedLine=l.selectedLine===e?null:e,textContent:(0,n.v_)(e)},null,10,g)))),128))],512),(0,i.Lk)("pre",u,[(0,i.Lk)("code",{ref:"content",innerHTML:a.displayedContent},null,8,m),null!=l.selectedLine?((0,i.uX)(),(0,i.CE)("div",v,null,512)):(0,i.Q3)("",!0)],512),(0,i.bo)((0,i.Lk)("textarea",{ref:"textarea","onUpdate:modelValue":t[0]||(t[0]=e=>l.content=e),onScroll:t[1]||(t[1]=(...e)=>a.syncScroll&&a.syncScroll(...e)),onInput:t[2]||(t[2]=(0,x.D$)((()=>{}),["stop"]))},null,544),[[x.Jo,l.content]])]),s.withSave?((0,i.uX)(),(0,i.Wv)(h,{key:1,"icon-class":"fa fa-save",title:"Save",disabled:!a.hasChanges||l.saving,onClick:a.saveFile},null,8,["disabled","onClick"])):(0,i.Q3)("",!0)])])}var C=s(4335),k=s(9878),w=(s(6669),s(7998));const L={actionscript:{extensions:[".as"],types:["text/x-actionscript"]},ada:{extensions:[".ada",".adb",".ads"],types:["text/x-ada"]},apache:{extensions:[".htaccess",".htpasswd"],types:["text/x-apache"]},arduino:{extensions:[".ino"],types:["text/x-arduino"]},autoit:{extensions:[".au3"],types:["text/x-autoit"]},awk:{extensions:[".awk"],types:["text/x-awk"]},bash:{extensions:[".sh",".bash"],types:["text/x-sh"]},basic:{extensions:[".bas",".basic"],types:["text/x-basic"]},bnf:{extensions:[".bnf"],types:["text/x-bnf"]},c:{extensions:[".c",".h"],types:["text/x-c"]},clojure:{extensions:[".clj",".cljc",".cljx",".cljs",".edn"],types:["text/x-clojure"]},cmake:{extensions:[".cmake",".cmake.in"],types:["text/x-cmake"]},coffeescript:{extensions:[".coffee"],types:["text/x-coffeescript"]},cpp:{extensions:[".cpp",".cc",".cxx",".c++",".h",".hh",".hpp",".hxx",".h++"],types:["text/x-c++src"]},crystal:{extensions:[".cr"],types:["text/x-crystal"]},css:{extensions:[".css"],types:["text/css"]},d:{extensions:[".d"],types:["text/x-d"]},dart:{extensions:[".dart"],types:["text/x-dart"]},delphi:{extensions:[".pas",".dpr",".dfm",".dpk",".dproj"],types:["text/x-pascal"]},diff:{extensions:[".diff",".patch"],types:["text/x-diff"]},dns:{extensions:[".zone",".arpa"],types:["text/x-dns"]},dockerfile:{extensions:["Dockerfile"],types:["text/x-dockerfile"]},dos:{extensions:[".bat",".cmd"],types:["text/x-dos"]},dsconfig:{extensions:[".dsconfig"],types:["text/x-dsconfig"]},dts:{extensions:[".dts",".dtsi"],types:["text/x-dts"]},dust:{extensions:[".dust"],types:["text/x-dust"]},ebnf:{extensions:[".ebnf"],types:["text/x-ebnf"]},elixir:{extensions:[".ex",".exs"],types:["text/x-elixir"]},elm:{extensions:[".elm"],types:["text/x-elm"]},erlang:{extensions:[".erl"],types:["text/x-erlang"]},excel:{extensions:[".xls",".xlsx"],types:["text/x-excel"]},fortran:{extensions:[".f",".f77",".f90",".f95"],types:["text/x-fortran"]},fsharp:{extensions:[".fs",".fsi",".fsx",".fsscript"],types:["text/x-fsharp"]},gherkin:{extensions:[".feature"],types:["text/x-feature"]},go:{extensions:[".go"],types:["text/x-go"]},gradle:{extensions:[".gradle"],types:["text/x-gradle"]},graphql:{extensions:[".graphql"],types:["text/x-graphql"]},groovy:{extensions:[".groovy",".gradle"],types:["text/x-groovy"]},handlebars:{extensions:[".hbs",".handlebars"],types:["text/x-handlebars-template"]},haskell:{extensions:[".hs",".lhs"],types:["text/x-haskell"]},http:{extensions:[".http"],types:["message/http"]},ini:{extensions:[".ini",".toml"],types:["text/x-ini"]},java:{extensions:[".java"],types:["text/x-java"]},html:{extensions:[".html",".htm"],types:["text/html"]},javascript:{extensions:[".js",".mjs"],types:["application/javascript"]},json:{extensions:[".json"],types:["application/json"]},julia:{extensions:[".jl"],types:["text/x-julia"]},kotlin:{extensions:[".kt",".kts"],types:["text/x-kotlin"]},latex:{extensions:[".tex"],types:["text/x-latex"]},less:{extensions:[".less"],types:["text/x-less"]},lisp:{extensions:[".lisp",".lsp"],types:["text/x-lisp"]},llvm:{extensions:[".ll"],types:["text/x-llvm"]},lua:{extensions:[".lua"],types:["text/x-lua"]},makefile:{extensions:["Makefile"],types:["text/x-makefile"]},markdown:{extensions:[".md",".markdown"],types:["text/markdown"]},mathematica:{extensions:[".m"],types:["text/x-mathematica"]},matlab:{extensions:[".m"],types:["text/x-matlab"]},nginx:{extensions:[".nginx","nginx.conf"],contains:["/sites-available/","/sites-enabled/"],types:["text/x-nginx-conf"]},nim:{extensions:[".nim",".nimble"],types:["text/x-nim"]},nix:{extensions:[".nix"],types:["text/x-nix"]},objectivec:{extensions:[".m"],types:["text/x-objectivec"]},ocaml:{extensions:[".ml",".mli"],types:["text/x-ocaml"]},perl:{extensions:[".pl",".pm"],types:["text/x-perl"]},pgsql:{extensions:[".pgsql"],types:["text/x-pgsql"]},php:{extensions:[".php"],types:["text/x-php"]},plaintext:{extensions:[".txt"]},powershell:{extensions:[".ps1",".psm1",".psd1"],types:["text/x-powershell"]},prolog:{extensions:[".pro",".prolog"],types:["text/x-prolog"]},protobuf:{extensions:[".proto"],types:["text/x-protobuf"]},puppet:{extensions:[".pp"],types:["text/x-puppet"]},python:{extensions:[".py"],types:["text/x-python"]},r:{extensions:[".r"],types:["text/x-r"]},ruby:{extensions:[".rb"],types:["text/x-ruby"]},rust:{extensions:[".rs"],types:["text/x-rust"]},scala:{extensions:[".scala"],types:["text/x-scala"]},scheme:{extensions:[".scm",".ss"],types:["text/x-scheme"]},scss:{extensions:[".scss"],types:["text/x-scss"]},smalltalk:{extensions:[".st"],types:["text/x-stsrc"]},sql:{extensions:[".sql"],types:["text/x-sql"]},swift:{extensions:[".swift"],types:["text/x-swift"]},tcl:{extensions:[".tcl"],types:["text/x-tcl"]},typescript:{extensions:[".ts"],types:["application/typescript"]},vbnet:{extensions:[".vb"],types:["text/x-vb"]},vbscript:{extensions:[".vbs"],types:["text/vbscript"]},vhdl:{extensions:[".vhd",".vhdl"],types:["text/x-vhdl"]},vim:{extensions:[".vim",".vimrc"],types:["text/x-vim"]},wasm:{extensions:[".wasm"],types:["application/wasm"]},x86asm:{extensions:[".asm",".s"],types:["text/x-asm"]},xml:{extensions:[".xml"],types:["application/xml"]},yaml:{extensions:[".yaml",".yml"],types:["text/x-yaml"]}};var T={methods:{getLanguageType(e){for(const[t,s]of Object.entries(L)){const i=s.extensions?.filter((t=>e.path.toLowerCase().endsWith(t)));if(i?.length)return t;const n=s.contains?.filter((t=>e.path.toLowerCase().includes(t)));if(n?.length)return t;const o=s.types?.filter((t=>e.type===t));if(o?.length)return t}return"plaintext"}}};const S=T;var $=S,j=s(9828),A=s(2002),F={mixins:[$,A.A],emits:["save"],components:{FloatingButton:w.A,Loading:j.A},props:{file:{type:String},text:{type:String,default:""},contentType:{type:String,default:"plaintext"},isNew:{type:Boolean,default:!1},line:{type:[String,Number],default:null},withSave:{type:Boolean,default:!0}},data(){return{content:"",currentContentHash:0,highlightedContent:"",highlighting:!1,highlightTimer:null,info:{},initialContentHash:0,loading:!1,saving:!1,selectedLine:null,type:null}},computed:{codeClass(){return this.type?.length?`language-${this.type}`:"language-plaintext"},displayedContent(){return this.highlightedContent?.length?this.highlightedContent:this.content},hasChanges(){return this.initialContentHash!==this.currentContentHash},isProcessing(){return this.highlighting||this.highlightTimer||this.saving},lines(){return this.content?.length?this.content.split("\n").length:1}},methods:{async loadFile(){if(!this.text?.length){if(this.setUrlArgs({file:this.file}),this.isNew)return this.content="",this.initialContentHash=0,this.highlightedContent="",this.info={},void(this.type=this.getLanguageType({path:this.file}));this.loading=!0;try{this.info=(await this.request("file.info",{files:[this.file]}))[this.file]||{},this.type=this.getLanguageType(this.info),this.content=(await C.A.get(`/file?path=${encodeURIComponent(this.file)}`)).data,"object"===typeof this.content&&(this.content=JSON.stringify(this.content,null,2)),this.initialContentHash=this.content.hashCode()}catch(e){this.notify({error:!0,text:e.message,title:"Failed to load file"})}finally{this.loading=!1}}this.selectedLine&&setTimeout((()=>{this.scrollToLine(this.selectedLine)}),1e3)},async saveFile(){if(this.hasChanges){this.saving=!0;try{await C.A.put(`/file?path=${encodeURIComponent(this.file)}`,this.content),this.initialContentHash=this.content.hashCode(),this.notify({title:"File saved",text:`${this.file} saved`,image:{icon:"check"}})}catch(e){this.notify({error:!0,text:e.message,title:"Failed to save file"})}finally{this.saving=!1}this.$emit("save")}},syncScroll(e){const[t,s]=[e.target.scrollTop,e.target.scrollLeft],i=Math.min(e.target.scrollHeight,this.$refs.pre.scrollHeight),n=Math.min(e.target.clientHeight,this.$refs.pre.clientHeight),o=i-n,l={top:Math.min(t,o),left:s,behavior:"auto"};e.target.scrollTo(l),this.$refs.pre.scrollTo(l),this.$refs.lineNumbers.scrollTo({top:l.top,behavior:"auto"})},scrollToLine(e){const t=(e-1)*parseFloat(getComputedStyle(this.$refs.pre).lineHeight);return this.$refs.textarea.scrollTo({top:t,left:0,behavior:"smooth"}),t},highlightContent(){this.highlighting=!0;try{clearTimeout(this.highlightTimer),this.highlightTimer=null,this.highlightedContent=k.A.highlight(this.content,{language:this.type||"plaintext"}).value}finally{this.highlighting=!1}},async keyListener(e){"s"===e.key&&(e.ctrlKey||e.metaKey)&&(e.preventDefault(),await this.saveFile())},addKeyListener(){window.addEventListener("keydown",(e=>{"s"===e.key&&(e.ctrlKey||e.metaKey)&&(e.preventDefault(),this.saveFile())}))},removeKeyListener(){window.removeEventListener("keydown",(e=>{"s"===e.key&&(e.ctrlKey||e.metaKey)&&(e.preventDefault(),this.saveFile())}))},beforeUnload(e){this.hasChanges&&(e.preventDefault(),e.returnValue="")},addBeforeUnload(){window.addEventListener("beforeunload",this.beforeUnload)},removeBeforeUnload(){window.removeEventListener("beforeunload",this.beforeUnload)},convertType(e){const t=e.split("/");return t[t.length-1]},reset(){this.setUrlArgs({file:null,line:null}),this.removeBeforeUnload(),this.removeKeyListener()}},watch:{contentType(){this.contentType?.length&&(this.type=this.convertType(this.contentType))},file(){this.loadFile()},content(){this.content?.length&&(this.currentContentHash=this.content.hashCode(),this.highlightedContent?.length?(this.highlightTimer&&clearTimeout(this.highlightTimer),this.highlightTimer=setTimeout(this.highlightContent,1e3),this.highlightedContent=this.content):this.highlightContent())},selectedLine(e){if(e=parseInt(e),isNaN(e))return;const t=this.$refs.textarea,s=this.content.split("\n"),i=s.slice(0,e-1).join("\n").length+1;t.setSelectionRange(i,i),t.focus(),this.setUrlArgs({line:e}),this.$nextTick((()=>{const t=this.scrollToLine(e);this.$refs.selectedLine.style.top=`${t}px`}))},text(){this.content=this.text}},mounted(){const e=this.getUrlArgs(),t=parseInt(this.line||e.line||0);t&&(isNaN(t)||(this.selectedLine=t)),this.content=this.text,this.type=this.convertType(this.contentType),this.loadFile(),this.addBeforeUnload(),this.addKeyListener(),this.$nextTick((()=>{this.$refs.textarea.focus()}))},unmouted(){this.reset()}},U=s(6262);const B=(0,U.A)(F,[["render",b],["__scopeId","data-v-622fc6dc"]]);var E=B,z=s(9513),H={emits:["close","open","save"],mixins:[z.A,A.A],components:{ConfirmDialog:h.A,FileEditor:E,Modal:z.A},props:{file:{type:String},text:{type:String,default:""},contentType:{type:String,default:"text/plain"},isNew:{type:Boolean,default:!1},line:{type:[String,Number],default:null},withSave:{type:Boolean,default:!0}},data(){return{confirmClose:!0,maximized:!1}},computed:{filename(){return this.file.split("/").pop()||"Untitled"},headerButtons(){const e=[];return this.maximized?e.push({title:"Restore",icon:"far fa-window-restore",action:()=>this.maximized=!1}):e.push({title:"Maximize",icon:"far fa-window-maximize",action:()=>this.maximized=!0}),e},proxiedProperties(){const e={...this.$props};return delete e.file,delete e.withSave,e.buttons=this.headerButtons,e.title=this.filename,e.beforeClose=this.checkClose,e}},methods:{checkClose(){return!(this.withSave&&this.confirmClose&&this.$refs.fileEditor.hasChanges)||(this.$refs.confirmClose.open(),!1)},forceClose(){this.confirmClose=!1,this.$refs.modal.close()},onClose(){this.$refs.fileEditor.reset(),this.setUrlArgs({maximized:null}),this.$emit("close")}},watch:{maximized(){this.setUrlArgs({maximized:this.maximized})}},mounted(){this.maximized=!!this.getUrlArgs().maximized}};const I=(0,U.A)(H,[["render",r],["__scopeId","data-v-85640964"]]);var N=I},7998:function(e,t,s){s.d(t,{A:function(){return p}});var i=s(641),n=s(33);const o=["disabled","title"];function l(e,t,s,l,a,r){const h=(0,i.g2)("Icon");return(0,i.uX)(),(0,i.CE)("div",{class:(0,n.C4)(["floating-btn",r.classes])},[(0,i.Lk)("button",{type:"button",class:(0,n.C4)(["btn btn-primary",s.glow?"with-glow":""]),disabled:s.disabled,title:s.title,onClick:t[0]||(t[0]=t=>e.$emit("click",t))},[(0,i.bF)(h,{class:(0,n.C4)(s.iconClass),url:s.iconUrl},null,8,["class","url"])],10,o)],2)}var a=s(3778),r={components:{Icon:a.A},emits:["click"],props:{disabled:{type:Boolean,default:!1},iconClass:{type:String},iconUrl:{type:String},class:{type:String},title:{type:String},left:{type:Boolean,default:!1},right:{type:Boolean,default:!0},top:{type:Boolean,default:!1},bottom:{type:Boolean,default:!0},glow:{type:Boolean,default:!1}},computed:{classes(){const e={};return this.left?e.left=!0:e.right=!0,this.top?e.top=!0:e.bottom=!0,this.class?.length&&(e[this.class]=!0),e}}},h=s(6262);const x=(0,h.A)(r,[["render",l],["__scopeId","data-v-544409fc"]]);var p=x}}]);
//# sourceMappingURL=1367.357a4e88.js.map