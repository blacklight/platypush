"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[8409],{8409:function(e,t,i){i.d(t,{Z:function(){return Wt}});var s=i(6252),l=i(9963),o=i(3577);const a=e=>((0,s.dD)("data-v-0c7b0e28"),e=e(),(0,s.Cn)(),e),n={class:"browser"},r={class:"nav",ref:"nav"},c={class:"path-container"},d={key:0,class:"path"},h=a((()=>(0,s._)("i",{class:"fa fa-home"},null,-1))),p=[h],u={key:0,class:"separator"},f=a((()=>(0,s._)("i",{class:"fa fa-chevron-right"},null,-1))),m=[f],v=["onClick"],y={class:"token"},w={key:0,class:"separator"},g=a((()=>(0,s._)("i",{class:"fa fa-chevron-right"},null,-1))),k=[g],_={class:"btn-container"},b={key:2,class:"items",ref:"items"},C=a((()=>(0,s._)("div",{class:"col-10 left side"},[(0,s._)("i",{class:"icon fa fa-folder"}),(0,s._)("span",{class:"name"},"..")],-1))),F=[C],D=a((()=>(0,s._)("div",{class:"col-10 left side"},[(0,s._)("i",{class:"icon fa fa-hand-point-right"}),(0,s._)("span",{class:"name"},"<Select This Directory>")],-1))),I=[D],T=["onClick"],x={class:"col-10"},$={class:"name"},U={key:0,class:"col-2 actions"},S={class:"modal-body"},R={key:3,class:"upload-file-container"},q={key:4,class:"info-modal-container"},W={class:"modal-body"},B=a((()=>(0,s._)("br",null,null,-1))),M=a((()=>(0,s._)("br",null,null,-1))),Z=a((()=>(0,s._)("br",null,null,-1))),H=a((()=>(0,s._)("br",null,null,-1))),z=a((()=>(0,s._)("br",null,null,-1))),E=a((()=>(0,s._)("br",null,null,-1))),O=a((()=>(0,s._)("br",null,null,-1))),j=a((()=>(0,s._)("br",null,null,-1))),A={class:"copy-modal-container"},L={class:"modal-body"};function N(e,t,i,a,h,f){const g=(0,s.up)("Loading"),C=(0,s.up)("DropdownItem"),D=(0,s.up)("Dropdown"),N=(0,s.up)("Home"),P=(0,s.up)("BrowserOptions"),K=(0,s.up)("Modal"),Y=(0,s.up)("FileUploader"),V=(0,s.up)("FileInfo"),G=(0,s.up)("ConfirmDialog"),J=(0,s.up)("FileEditor"),Q=(0,s.up)("TextPrompt"),X=(0,s.up)("Browser",!0);return(0,s.wg)(),(0,s.iD)("div",n,[h.loading?((0,s.wg)(),(0,s.j4)(g,{key:0})):(0,s.kq)("",!0),(0,s._)("div",r,[(0,s._)("div",c,[f.hasHomepage?((0,s.wg)(),(0,s.iD)("span",d,[(0,s._)("span",{class:"token",onClick:t[0]||(t[0]=(0,l.iM)((e=>h.path=null),["stop"]))},p),f.pathTokens.length?((0,s.wg)(),(0,s.iD)("span",u,m)):(0,s.kq)("",!0)])):(0,s.kq)("",!0),((0,s.wg)(!0),(0,s.iD)(s.HY,null,(0,s.Ko)(f.pathTokens,((e,t)=>((0,s.wg)(),(0,s.iD)("span",{class:"path",key:t,onClick:(0,l.iM)((e=>h.path=f.pathTokens.slice(0,t+1).join("/").slice(1)),["stop"])},[(0,s._)("span",y,(0,o.zw)(e),1),(t>0||f.pathTokens.length>1)&&t<f.pathTokens.length-1?((0,s.wg)(),(0,s.iD)("span",w,k)):(0,s.kq)("",!0)],8,v)))),128))]),(0,s._)("div",_,[(0,s.Wm)(D,{style:{"min-width":"11em"},onClick:t[5]||(t[5]=(0,l.iM)((()=>{}),["prevent"]))},{default:(0,s.w5)((()=>[(0,s.Wm)(C,{"icon-class":"fa fa-plus",text:"New Folder",onInput:t[1]||(t[1]=e=>h.showCreateDirectory=!0)}),(0,s.Wm)(C,{"icon-class":"fa fa-file",text:"Create File",onInput:t[2]||(t[2]=e=>h.showCreateFile=!0)}),(0,s.Wm)(C,{"icon-class":"fa fa-upload",text:"Upload",onInput:t[3]||(t[3]=e=>h.showUpload=!0)}),(0,s.Wm)(C,{"icon-class":"fa fa-sync",text:"Refresh",onInput:f.refresh},null,8,["onInput"]),(0,s.Wm)(C,{"icon-class":"fa fa-cog",text:"Options",onInput:t[4]||(t[4]=e=>h.showOptions=!0)})])),_:1})])],512),!h.path&&f.hasHomepage?((0,s.wg)(),(0,s.j4)(N,{key:1,items:i.homepage,filter:i.filter,"has-back":i.hasBack,onBack:f.onBack,onInput:f.onItemSelect},null,8,["items","filter","has-back","onBack","onInput"])):((0,s.wg)(),(0,s.iD)("div",b,[h.path?.length&&"/"!==h.path||i.hasBack?((0,s.wg)(),(0,s.iD)("div",{key:0,class:"row item",onClick:t[6]||(t[6]=(0,l.iM)(((...e)=>f.onBack&&f.onBack(...e)),["stop"]))},F)):(0,s.kq)("",!0),i.hasSelectCurrentDirectory?((0,s.wg)(),(0,s.iD)("div",{key:1,class:"row item",ref:"selectCurrent",onClick:t[7]||(t[7]=(0,l.iM)(((...e)=>f.onSelectCurrentDirectory&&f.onSelectCurrentDirectory(...e)),["stop"]))},I,512)):(0,s.kq)("",!0),((0,s.wg)(!0),(0,s.iD)(s.HY,null,(0,s.Ko)(f.filteredFiles,((e,i)=>((0,s.wg)(),(0,s.iD)("div",{class:"row item",key:i,onClick:(0,l.iM)((t=>f.onItemSelect(e)),["stop"])},[(0,s._)("div",x,[(0,s._)("i",{class:(0,o.C_)(["icon fa",f.fileIcons[e.path]])},null,2),(0,s._)("span",$,(0,o.zw)(e.name),1)]),Object.keys(f.fileActions[e.path]||{})?.length?((0,s.wg)(),(0,s.iD)("div",U,[(0,s.Wm)(D,{style:{"min-width":"11em"},onClick:t[8]||(t[8]=(0,l.iM)((()=>{}),["prevent"]))},{default:(0,s.w5)((()=>[((0,s.wg)(!0),(0,s.iD)(s.HY,null,(0,s.Ko)(f.fileActions[e.path],((t,i)=>((0,s.wg)(),(0,s.j4)(C,{key:i,"icon-class":t.iconClass,text:t.text,onInput:i=>t.onClick(e)},null,8,["icon-class","text","onInput"])))),128))])),_:2},1024)])):(0,s.kq)("",!0)],8,T)))),128))],512)),(0,s.Wm)(K,{title:"Options",visible:h.showOptions,onClose:t[9]||(t[9]=e=>h.showOptions=!1)},{default:(0,s.w5)((()=>[(0,s._)("div",S,[(0,s.Wm)(P,{value:h.opts,onInput:f.onOptsChange},null,8,["value","onInput"])])])),_:1},8,["visible"]),h.showUpload?((0,s.wg)(),(0,s.iD)("div",R,[(0,s.Wm)(Y,{path:h.path,visible:h.showUpload,ref:"uploader",onComplete:f.onUploadCompleted,onClose:t[10]||(t[10]=e=>h.showUpload=!1)},null,8,["path","visible","onComplete"])])):(0,s.kq)("",!0),null!=h.showInfoFile?((0,s.wg)(),(0,s.iD)("div",q,[(0,s.Wm)(K,{title:"File Info",visible:null!=h.showInfoFile,onClose:t[11]||(t[11]=e=>h.showInfoFile=null)},{default:(0,s.w5)((()=>[(0,s._)("div",W,[(0,s.Wm)(V,{file:h.showInfoFile,loading:h.loading},null,8,["file","loading"])])])),_:1},8,["visible"])])):(0,s.kq)("",!0),(0,s.Wm)(G,{visible:h.editWarnings.length>0,onClose:f.clearEditFile,onInput:t[12]||(t[12]=e=>f.editFile(h.editedFile,{force:!0}))},{default:(0,s.w5)((()=>[(0,s.Uk)(" The following warnings were raised: "),(0,s._)("ul",null,[((0,s.wg)(!0),(0,s.iD)(s.HY,null,(0,s.Ko)(h.editWarnings,((e,t)=>((0,s.wg)(),(0,s.iD)("li",{key:t},(0,o.zw)(e),1)))),128))]),(0,s.Uk)(" Are you sure you that you want to edit the file? ")])),_:1},8,["visible","onClose"]),(0,s.Wm)(G,{visible:null!=h.fileToRemove,onClose:t[13]||(t[13]=e=>h.fileToRemove=null),onInput:t[14]||(t[14]=e=>f.deleteFile(h.fileToRemove))},{default:(0,s.w5)((()=>[(0,s.Uk)(" Are you sure you that you want to delete this file?"),B,M,(0,s._)("b",null,(0,o.zw)(h.fileToRemove),1)])),_:1},8,["visible"]),(0,s.Wm)(G,{visible:null!=h.directoryToRemove,onClose:t[15]||(t[15]=e=>h.directoryToRemove=null),onInput:t[16]||(t[16]=e=>f.deleteDirectory(h.directoryToRemove))},{default:(0,s.w5)((()=>[(0,s.Uk)(" Are you sure you that you want to delete this directory?"),Z,H,(0,s._)("b",null,(0,o.zw)(h.directoryToRemove),1)])),_:1},8,["visible"]),(0,s.Wm)(G,{visible:null!=h.directoryToRemove&&h.directoryNotEmpty,onClose:t[17]||(t[17]=e=>{h.directoryToRemove=null,h.directoryNotEmpty=!1}),onInput:t[18]||(t[18]=e=>f.deleteDirectory(h.directoryToRemove,{recursive:!0}))},{default:(0,s.w5)((()=>[(0,s.Uk)(" This directory is not empty. Are you sure you that you want to delete it?"),z,E,(0,s._)("b",null,(0,o.zw)(h.directoryToRemove),1)])),_:1},8,["visible"]),h.editedFile&&!h.editWarnings?.length?((0,s.wg)(),(0,s.j4)(J,{key:5,file:h.editedFile,"is-new":h.isNewFileEdit,visible:null!=h.editedFile,uppercase:!1,onClose:f.clearEditFile,onSave:f.refresh},null,8,["file","is-new","visible","onClose","onSave"])):(0,s.kq)("",!0),(0,s.Wm)(Q,{visible:h.showCreateDirectory,onInput:t[19]||(t[19]=e=>f.createDirectory(e)),onClose:t[20]||(t[20]=e=>h.showCreateDirectory=!1)},{default:(0,s.w5)((()=>[(0,s.Uk)(" Enter the name of the new directory: ")])),_:1},8,["visible"]),(0,s.Wm)(Q,{visible:h.showCreateFile,onInput:f.editNewFile,onClose:t[21]||(t[21]=e=>h.showCreateFile=!1)},{default:(0,s.w5)((()=>[(0,s.Uk)(" Enter the name of the new file: ")])),_:1},8,["visible","onInput"]),(0,s.Wm)(Q,{visible:null!=h.fileToRename,value:f.displayedFileToRename,onInput:f.renameFile,onClose:t[22]||(t[22]=e=>h.fileToRename=null)},{default:(0,s.w5)((()=>[(0,s.Uk)(" Enter a new name for this file:"),O,j,(0,s._)("b",null,(0,o.zw)(h.fileToRename),1)])),_:1},8,["visible","value","onInput"]),(0,s._)("div",A,[f.showCopyModal?((0,s.wg)(),(0,s.j4)(K,{key:0,title:(null!=h.copyFile?"Copy":"Move")+" File",visible:f.showCopyModal,onClose:t[24]||(t[24]=e=>f.showCopyModal=!1)},{default:(0,s.w5)((()=>[(0,s._)("div",L,[(0,s.Wm)(X,{path:h.path,"has-back":!0,"has-select-current-directory":!0,"show-directories":!0,"show-files":!1,onBack:t[23]||(t[23]=e=>{h.copyFile=null,h.moveFile=null}),onInput:f.copyOrMove},null,8,["path","onInput"])])])),_:1},8,["title","visible"])):(0,s.kq)("",!0)])])}i(560);const P={class:"browser-options"},K={key:1,class:"options-body"},Y={class:"row item"},V=["checked","value"],G={class:"row item sort-container"},J=["value"],Q=["selected"],X=["selected"],ee=["selected"],te=["selected"],ie=["checked"],se=["checked"];function le(e,t,i,l,o,a){const n=(0,s.up)("Loading");return(0,s.wg)(),(0,s.iD)("div",P,[i.loading?((0,s.wg)(),(0,s.j4)(n,{key:0})):((0,s.wg)(),(0,s.iD)("div",K,[(0,s._)("div",Y,[(0,s._)("label",null,[(0,s._)("input",{type:"checkbox",checked:i.value.showHidden,value:i.value.showHidden,onInput:t[0]||(t[0]=t=>e.$emit("input",{...i.value,showHidden:t.target.checked}))},null,40,V),(0,s.Uk)(" Show hidden files ")])]),(0,s._)("div",G,[(0,s._)("span",null,[(0,s._)("label",null,[(0,s.Uk)(" Sort by "),(0,s._)("span",null,[(0,s._)("select",{value:i.value.sortBy,onInput:t[1]||(t[1]=t=>e.$emit("input",{...i.value,sortBy:t.target.value}))},[(0,s._)("option",{value:"name",selected:"name"===i.value.sortBy},"Name",8,Q),(0,s._)("option",{value:"size",selected:"size"===i.value.sortBy},"Size",8,X),(0,s._)("option",{value:"created",selected:"created"===i.value.sortBy},"Creation Date",8,ee),(0,s._)("option",{value:"last_modified",selected:"last_modified"===i.value.sortBy},"Last Modified",8,te)],40,J)])])]),(0,s._)("span",null,[(0,s._)("label",null,[(0,s._)("input",{type:"radio",checked:!i.value.reverseSort,onInput:t[2]||(t[2]=t=>e.$emit("input",{...i.value,reverseSort:!1}))},null,40,ie),(0,s.Uk)(" Ascending ")]),(0,s._)("label",null,[(0,s._)("input",{type:"radio",checked:i.value.reverseSort,onInput:t[3]||(t[3]=t=>e.$emit("input",{...i.value,reverseSort:!0}))},null,40,se),(0,s.Uk)(" Descending ")])])])]))])}var oe=i(6791),ae=i(8637),ne={emits:["input"],mixins:[ae.Z],components:{Loading:oe.Z},props:{loading:{type:Boolean,default:!1},value:{type:Object,required:!0}}},re=i(3744);const ce=(0,re.Z)(ne,[["render",le],["__scopeId","data-v-c4abebfe"]]);var de=ce,he=i(3513),pe=i(1370),ue=i(7597),fe=i(8756);const me=e=>((0,s.dD)("data-v-417b1bc7"),e=e(),(0,s.Cn)(),e),ve={class:"file-info"},ye={key:1,class:"file-info-container"},we={class:"row item"},ge=me((()=>(0,s._)("div",{class:"label"},"Path",-1))),ke={class:"value"},_e={key:0,class:"row item"},be=me((()=>(0,s._)("div",{class:"label"},"Size",-1))),Ce={class:"value"},Fe={key:1,class:"row item"},De=me((()=>(0,s._)("div",{class:"label"},"Creation Date",-1))),Ie={class:"value"},Te={key:2,class:"row item"},xe=me((()=>(0,s._)("div",{class:"label"},"Last Modified",-1))),$e={class:"value"},Ue={key:3,class:"row item"},Se=me((()=>(0,s._)("div",{class:"label"},"MIME type",-1))),Re={class:"value"},qe={key:4,class:"row item"},We=me((()=>(0,s._)("div",{class:"label"},"Permissions",-1))),Be={class:"value"},Me={key:5,class:"row item"},Ze=me((()=>(0,s._)("div",{class:"label"},"Owner ID",-1))),He={class:"value"},ze={key:6,class:"row item"},Ee=me((()=>(0,s._)("div",{class:"label"},"Group ID",-1))),Oe={class:"value"};function je(e,t,i,l,a,n){const r=(0,s.up)("Loading");return(0,s.wg)(),(0,s.iD)("div",ve,[a.loading?((0,s.wg)(),(0,s.j4)(r,{key:0})):a.info?((0,s.wg)(),(0,s.iD)("div",ye,[(0,s._)("div",we,[ge,(0,s._)("div",ke,(0,o.zw)(a.info.path),1)]),null!=a.info.size?((0,s.wg)(),(0,s.iD)("div",_e,[be,(0,s._)("div",Ce,(0,o.zw)(e.convertSize(a.info.size)),1)])):(0,s.kq)("",!0),null!=a.info.created?((0,s.wg)(),(0,s.iD)("div",Fe,[De,(0,s._)("div",Ie,(0,o.zw)(e.formatDate(a.info.created,!0)),1)])):(0,s.kq)("",!0),null!=a.info.last_modified?((0,s.wg)(),(0,s.iD)("div",Te,[xe,(0,s._)("div",$e,(0,o.zw)(e.formatDate(a.info.last_modified,!0)),1)])):(0,s.kq)("",!0),null!=a.info.mime_type?((0,s.wg)(),(0,s.iD)("div",Ue,[Se,(0,s._)("div",Re,(0,o.zw)(a.info.mime_type),1)])):(0,s.kq)("",!0),null!=a.info.permissions?((0,s.wg)(),(0,s.iD)("div",qe,[We,(0,s._)("div",Be,(0,o.zw)(a.info.permissions),1)])):(0,s.kq)("",!0),null!=a.info.owner?((0,s.wg)(),(0,s.iD)("div",Me,[Ze,(0,s._)("div",He,(0,o.zw)(a.info.owner),1)])):(0,s.kq)("",!0),null!=a.info.group?((0,s.wg)(),(0,s.iD)("div",ze,[Ee,(0,s._)("div",Oe,(0,o.zw)(a.info.group),1)])):(0,s.kq)("",!0)])):(0,s.kq)("",!0)])}var Ae=i(1065),Le={components:{Loading:oe.Z},mixins:[ae.Z,Ae.Z],props:{file:{type:String}},data(){return{info:{},loading:!1}},methods:{async refresh(){this.loading=!0;try{this.info=(await this.request("file.info",{files:[this.file]}))[this.file]}finally{this.loading=!1}}},watch:{file(){this.refresh()}},mounted(){this.refresh()}};const Ne=(0,re.Z)(Le,[["render",je],["__scopeId","data-v-417b1bc7"]]);var Pe=Ne;const Ke={class:"upload-file-modal-container"},Ye={class:"modal-body"};function Ve(e,t,i,l,o,a){const n=(0,s.up)("FileUploader"),r=(0,s.up)("Modal");return(0,s.wg)(),(0,s.iD)("div",Ke,[(0,s.Wm)(r,{title:"Upload File(s)",visible:e.visible,onClose:t[3]||(t[3]=t=>e.$emit("close"))},{default:(0,s.w5)((()=>[(0,s._)("div",Ye,[(0,s.Wm)(n,{path:e.path,onComplete:t[0]||(t[0]=t=>e.$emit("complete")),onStart:t[1]||(t[1]=t=>e.$emit("start")),onError:t[2]||(t[2]=t=>e.$emit("error"))},null,8,["path"])])])),_:1},8,["visible"])])}const Ge=e=>((0,s.dD)("data-v-67b7ea3b"),e=e(),(0,s.Cn)(),e),Je={class:"upload-file-container"},Qe={class:"row file-input"},Xe=["disabled"],et={class:"row btn-container"},tt=["disabled"],it=Ge((()=>(0,s._)("i",{class:"fa fa-upload"},null,-1))),st={class:"existing-files-container"},lt={key:1,class:"progress-container"},ot={class:"filename"},at={class:"progress-bar-container"},nt=["value"];function rt(e,t,i,a,n,r){const c=(0,s.up)("Loading"),d=(0,s.up)("ConfirmDialog");return(0,s.wg)(),(0,s.iD)("div",Je,[n.uploading?((0,s.wg)(),(0,s.j4)(c,{key:0})):(0,s.kq)("",!0),(0,s._)("form",{ref:"uploadForm",class:"upload-form",onSubmit:t[1]||(t[1]=(0,l.iM)((e=>r.uploadFiles()),["prevent"]))},[(0,s._)("div",Qe,[(0,s._)("input",{type:"file",ref:"files",multiple:"",disabled:n.uploading,onInput:t[0]||(t[0]=(...e)=>r.onFilesInput&&r.onFilesInput(...e))},null,40,Xe)]),(0,s._)("div",et,[(0,s._)("button",{type:"submit",disabled:n.uploading||!n.hasFiles},[it,(0,s.Uk)("  Upload ")],8,tt)])],544),(0,s._)("div",st,[((0,s.wg)(!0),(0,s.iD)(s.HY,null,(0,s.Ko)(n.existingFiles,(e=>((0,s.wg)(),(0,s.j4)(d,{key:e.name,visible:!0,onClose:t=>delete n.existingFiles[e.name],onInput:t=>r.uploadFiles([e],{force:!0})},{default:(0,s.w5)((()=>[(0,s.Uk)(" The file "),(0,s._)("b",null,(0,o.zw)(e.name),1),(0,s.Uk)(" already exists. Do you want to overwrite it? ")])),_:2},1032,["onClose","onInput"])))),128))]),Object.keys(n.progress||{}).length?((0,s.wg)(),(0,s.iD)("div",lt,[((0,s.wg)(!0),(0,s.iD)(s.HY,null,(0,s.Ko)(n.progress,((e,t)=>((0,s.wg)(),(0,s.iD)("div",{class:"row progress",key:t},[(0,s._)("span",ot,(0,o.zw)(t),1),(0,s._)("span",at,[(0,s._)("progress",{class:"progress-bar",value:e,max:"100"},null,8,nt)])])))),128))])):(0,s.kq)("",!0)])}var ct=i(7066),dt={emits:["complete","error","start"],mixins:[ae.Z],components:{ConfirmDialog:he.Z,Loading:oe.Z},props:{path:{type:String,required:!0}},data(){return{existingFiles:{},hasFiles:!1,progress:{},uploading:!1}},computed:{formFiles(){return this.$refs.files?.files?Array.from(this.$refs.files.files):[]}},methods:{async uploadFile(e,t){const{force:i}=t||{};i&&delete this.existingFiles[e.name];try{const t=i?"put":"post",s=await ct.Z[t](`/file?path=${this.path}/${e.name}`,e,{onUploadProgress:t=>{this.progress[e.name]=Math.round(100*t.loaded/t.total)},headers:{"Content-Type":e.type}});return this.notify({title:"File uploaded",text:`${e.name} uploaded to ${this.path}`,image:{icon:"check"}}),{file:e,status:s.status}}catch(s){const t={file:e,status:s.response?.status,error:s.response?.data?.error};return 409!==t.status&&this.onUploadError(s),t}},async uploadFiles(e,t){const{force:i}=t||{};if(e=e||this.formFiles,e.forEach((e=>{delete this.existingFiles[e.name]})),!e?.length)return void this.notify({title:"No files selected",text:"Please select files to upload",warning:!0,image:{icon:"upload"}});this.onUploadStarted(e);const s=[];try{const t=await Promise.all(e.map((e=>this.uploadFile(e,{force:i}))));s.push(...t.filter((e=>e?.error))),s.length||this.onUploadCompleted()}finally{this.uploading=!1}const l=s.filter((e=>409===e?.status&&e?.error));this.existingFiles={...this.existingFiles,...l.reduce(((e,t)=>(e[t.file.name]=t.file,e)),{})}},onFilesInput(e){this.hasFiles=Array.from(e.target.files).length>0},onUploadStarted(e){this.uploading=!0,this.$emit("start"),this.notify({title:"Upload started",text:`Uploading ${e.length} file(s) to ${this.path}`,image:{icon:"upload"}})},onUploadCompleted(){this.uploading=!1,this.$emit("complete")},onUploadError(e){const t=e.response?.data?.error;t&&(e.message=`${e.message}: ${t}`),this.$emit("error",e),this.notify({title:"Upload error",text:e.message,error:!0,image:{icon:"upload"}})}}};const ht=(0,re.Z)(dt,[["render",rt],["__scopeId","data-v-67b7ea3b"]]);var pt=ht,ut=i(2918),ft={mixins:[pt,ut.Z],components:{FileUploader:pt,Modal:ut.Z}};const mt=(0,re.Z)(ft,[["render",Ve],["__scopeId","data-v-f6e584b8"]]);var vt=mt;const yt=e=>((0,s.dD)("data-v-e2c178b2"),e=e(),(0,s.Cn)(),e),wt={class:"browser-home"},gt={class:"items",ref:"items"},kt=yt((()=>(0,s._)("div",{class:"icon-container"},[(0,s._)("i",{class:"icon fa fa-chevron-left"})],-1))),_t=yt((()=>(0,s._)("span",{class:"name"},"Back",-1))),bt=[kt,_t],Ct=["onClick"],Ft={class:"icon-container"},Dt=["src"],It={class:"name"};function Tt(e,t,i,l,a,n){return(0,s.wg)(),(0,s.iD)("div",wt,[(0,s._)("div",gt,[i.hasBack?((0,s.wg)(),(0,s.iD)("div",{key:0,class:"row item",onClick:t[0]||(t[0]=t=>e.$emit("back"))},bt)):(0,s.kq)("",!0),((0,s.wg)(!0),(0,s.iD)(s.HY,null,(0,s.Ko)(n.filteredItems,((t,i)=>((0,s.wg)(),(0,s.iD)("div",{class:"row item",key:i,onClick:i=>e.$emit("input",t)},[(0,s._)("div",Ft,[t.icon?.url?.length?((0,s.wg)(),(0,s.iD)("img",{key:0,class:"icon",src:t.icon.url},null,8,Dt)):((0,s.wg)(),(0,s.iD)("i",{key:1,class:(0,o.C_)(["icon",t.icon?.["class"]||"fas fa-folder"])},null,2))]),(0,s._)("span",It,(0,o.zw)(i),1)],8,Ct)))),128))],512)])}var xt={mixins:[ae.Z],emits:["back","input"],props:{hasBack:{type:Boolean,default:!1},filter:{type:String,default:""},items:{type:Object,required:!0},includeHome:{type:Boolean,default:!0},includeRoot:{type:Boolean,default:!0}},data(){return{userHome:null}},computed:{allItems(){return Object.entries({...this.includeRoot?{Root:{name:"Root",path:"/",icon:{class:"fas fa-hard-drive"}}}:{},...this.includeHome&&this.userHome?{Home:{name:"Home",path:this.userHome,icon:{class:"fas fa-home"}}}:{},...this.items}).reduce(((e,[t,i])=>(i.type?.length||(i.type="directory"),e[t]={name:t,...i},e)),{})},filteredItems(){return Object.fromEntries(Object.entries(this.allItems).filter((e=>e[0].toLowerCase().includes(this.filter.toLowerCase()))))}},methods:{async getUserHome(){return this.userHome||(this.userHome=await this.request("file.get_user_home")),this.userHome}},mounted(){this.getUserHome()}};const $t=(0,re.Z)(xt,[["render",Tt],["__scopeId","data-v-e2c178b2"]]);var Ut=$t,St=i(671),Rt={emits:["back","input","path-change","play"],mixins:[ae.Z,Ae.Z],components:{BrowserOptions:de,ConfirmDialog:he.Z,DropdownItem:ue.Z,Dropdown:pe.Z,FileEditor:fe.Z,FileInfo:Pe,FileUploader:vt,Home:Ut,Loading:oe.Z,Modal:ut.Z,TextPrompt:St.Z},props:{hasBack:{type:Boolean,default:!1},hasSelectCurrentDirectory:{type:Boolean,default:!1},initialPath:{type:String},isMedia:{type:Boolean},filter:{type:String,default:""},filterTypes:{type:Array,default:()=>[]},homepage:{type:Object},showDirectories:{type:Boolean,default:!0},showFiles:{type:Boolean,default:!0}},data(){return{copyFile:null,directoryNotEmpty:!1,directoryToRemove:null,editedFile:null,editWarnings:[],files:[],fileToRemove:null,fileToRename:null,info:{},isNewFileEdit:!1,loading:!1,mimeTypes:{},moveFile:null,opts:{showHidden:!1,sortBy:"name",reverseSort:!1},path:this.initialPath,showCreateDirectory:!1,showCreateFile:!1,showInfoFile:null,showOptions:!1,showUpload:!1,uploading:!1}},computed:{displayedFileToRename(){return this.fileToRename?.slice(this.path.length+1)||""},editedFileName(){return this.editedFile?.split("/").pop()||"Untitled"},filteredTypesMap(){return this.filterTypes.reduce(((e,t)=>(e[t]=!0,t.split("/").forEach((t=>{e[t]=!0})),e)),{})},filteredFiles(){return this.files.filter((e=>{if("directory"===e.type&&!this.showDirectories)return!1;if("directory"!==e.type&&!this.showFiles)return!1;if((e?.name||"").toLowerCase().indexOf(this.filter.toLowerCase())<0)return!1;if(!this.opts.showHidden&&e.name.startsWith("."))return!1;if(this.filterTypes.length){const t=this.mimeTypes[e.path]||"",i=[t,...t.split("/")];if(!i.some((e=>this.fileredTypesMap[e])))return!1}return!0}))},fileActions(){return this.files.reduce(((e,t)=>{const i=this.mimeTypes[t.path]||"";return e[t.path]={},this.isMedia&&(i.startsWith("audio/")||i.startsWith("video/"))&&(e[t.path]={play:{iconClass:"fa fa-play",text:"Play",onClick:e=>this.$emit("play",{type:"file",url:`file://${e.path}`})}}),"directory"!==t.type?(e[t.path].view={iconClass:"fa fa-eye",text:"View",onClick:e=>this.viewFile(e.path)},e[t.path].download={iconClass:"fa fa-download",text:"Download",onClick:e=>this.downloadFile(e.path)},e[t.path].edit={iconClass:"fa fa-edit",text:"Edit",onClick:e=>this.editFile(e.path)},e[t.path].copy={iconClass:"fa fa-copy",text:"Copy",onClick:e=>this.copyFile=e.path},e[t.path].move={iconClass:"fa fa-arrows-alt",text:"Move",onClick:e=>this.moveFile=e.path},e[t.path].rename={iconClass:"fa fa-pen",text:"Rename",onClick:e=>this.fileToRename=e.path},e[t.path].info={iconClass:"fa fa-info",text:"Info",onClick:e=>this.showInfoFile=e.path},e[t.path].delete={iconClass:"delete fa fa-trash",text:"Delete",onClick:e=>this.fileToRemove=e.path}):e[t.path].delete={iconClass:"delete fa fa-trash",text:"Delete",onClick:e=>this.directoryToRemove=e.path},e}),{})},fileIcons(){return this.files.reduce(((e,t)=>{if("directory"===t.type)e[t.path]="fa-folder";else{const i=this.mimeTypes[t.path]||"";switch(!0){case i.startsWith("audio/"):e[t.path]="fa-file-audio";break;case i.startsWith("video/"):e[t.path]="fa-file-video";break;case i.startsWith("image/"):e[t.path]="fa-file-image";break;case i.startsWith("text/"):e[t.path]="fa-file-alt";break;default:e[t.path]="fa-file";break}}return e}),{})},hasHomepage(){return Object.keys(this.homepage||{}).length},pathTokens(){return this.path?this.path?.length?["/",...this.path.split(/(?<!\\)\//).slice(1)].filter((e=>e.length)):["/"]:[]},showCopyModal(){return null!=this.copyFile||null!=this.moveFile}},methods:{initOpts(){const e=this.getUrlArgs();null!=e.showHidden&&(this.opts.showHidden=!!e.showHidden),null!=e.sortBy&&(this.opts.sortBy=e.sortBy),null!=e.reverseSort&&(this.opts.reverseSort=!!e.reverseSort),null!=e.file&&(this.editedFile=e.file)},async refresh(){this.loading=!0,this.$nextTick((()=>{this.$refs.nav&&(this.$refs.nav.scrollLeft=99999),this.$refs.items&&(this.$refs.items.scrollTop=0)}));try{this.files=await this.request("file.list",{path:this.path,sort:this.opts.sortBy,reverse:this.opts.reverseSort}),this.$emit("path-change",this.path),this.setUrlArgs({path:decodeURIComponent(this.path)})}finally{this.loading=!1}await this.refreshMimeTypes()},async refreshMimeTypes(){this.mimeTypes=await this.request("file.get_mime_types",{files:this.files.filter((e=>"directory"!==e.type)).map((e=>e.path))})},viewFile(e){window.open(`/file?path=${encodeURIComponent(e)}`,"_blank")},async editNewFile(e){return await this.editFile(`${this.path}/${e}`,{newFile:!0})},async editFile(e,t){const i=!!t?.force,s=this.isNewFileEdit=!!t?.newFile;if(i)this.editWarnings=[];else if(!s){const[t,i]=await Promise.all([this.request("file.info",{files:[e]}),this.request("file.is_binary",{file:e})]),s=t?.[e]?.size||0;if(i&&this.editWarnings.push("File is binary"),(t[e]?.size||0)>1048576&&this.editWarnings.push(`File is too large (${this.convertSize(s)})`),this.editWarnings.length)return void(this.editedFile=e)}this.editedFile=e},async deleteFile(){if(this.fileToRemove){this.loading=!0;try{await this.request("file.unlink",{file:this.fileToRemove})}finally{this.loading=!1,this.fileToRemove=null}this.refresh()}},async deleteDirectory(e,t){if(e=e||this.directoryToRemove,!e)return;const i=!!t?.recursive;let s=!1;this.loading=!0;try{await this.request("file.rmdir",{directory:e,recursive:i})}catch(l){"string"===typeof l&&l.search(/^\[?Errno 39\]?/i)>=0&&(s=!0)}finally{this.loading=!1,this.directoryNotEmpty=s,s||(this.directoryToRemove=null)}s?this.directoryToRemove=e:this.refresh()},async createDirectory(e){if(e){this.loading=!0;try{await this.request("file.mkdir",{directory:`${this.path}/${e}`})}finally{this.loading=!1}this.refresh()}},async copyOrMove(e){let t=null,i=null;if(this.copyFile)t="copy",i=this.copyFile;else{if(!this.moveFile)return;t="move",i=this.moveFile}this.loading=!0;try{await this.request(`file.${t}`,{source:i,target:e}),this.notify({text:`File ${t} completed successfully`,title:"Success",image:{icon:"check"}})}finally{this.loading=!1,this.copyFile=null,this.moveFile=null}this.refresh()},async renameFile(e){if(this.fileToRename&&e?.trim()?.length){this.loading=!0;try{await this.request("file.rename",{file:this.fileToRename,name:`${this.path}/${e}`})}finally{this.loading=!1,this.fileToRename=null}this.refresh()}},clearEditFile(){this.editedFile=null,this.editWarnings=[]},downloadFile(e){window.open(`/file?path=${encodeURIComponent(e)}&download=true`,"_blank")},onOptsChange(e){this.opts=e},onBack(){this.path?.length&&"/"!==this.path?this.path=[...this.pathTokens].slice(0,-1).join("/").slice(1):this.$emit("back")},onItemSelect(e){"directory"===e.type?this.path=e.path:this.$emit("input",e.path)},onSelectCurrentDirectory(){this.$emit("input",this.path)},onUploadCompleted(){this.refresh()}},watch:{initialPath(){this.path=this.initialPath},opts:{deep:!0,handler(){this.setUrlArgs(this.opts),this.refresh()}},path(e,t){t!==e&&this.refresh()},showUpload(e){const t=this.$refs.uploader;e?(t?.open(),this.$nextTick((()=>{t?.focus()}))):t?.close()}},mounted(){const e=this.getUrlArgs();e.path&&(this.path=e.path),this.initOpts(),this.refresh()}};const qt=(0,re.Z)(Rt,[["render",N],["__scopeId","data-v-0c7b0e28"]]);var Wt=qt},1065:function(e,t,i){i.d(t,{Z:function(){return a}});i(560);var s=i(8637),l={name:"Utils",mixins:[s.Z],computed:{audioExtensions(){return new Set(["3gp","aa","aac","aax","act","aiff","amr","ape","au","awb","dct","dss","dvf","flac","gsm","iklax","ivs","m4a","m4b","m4p","mmf","mp3","mpc","msv","nmf","nsf","ogg,","opus","ra,","raw","sln","tta","vox","wav","wma","wv","webm","8svx"])},videoExtensions(){return new Set(["webm","mkv","flv","flv","vob","ogv","ogg","drc","gif","gifv","mng","avi","mts","m2ts","mov","qt","wmv","yuv","rm","rmvb","asf","amv","mp4","m4p","m4v","mpg","mp2","mpeg","mpe","mpv","mpg","mpeg","m2v","m4v","svi","3gp","3g2","mxf","roq","nsv","flv","f4v","f4p","f4a","f4b"])},mediaExtensions(){return new Set([...this.videoExtensions,...this.audioExtensions])}},methods:{convertTime(e){e=parseFloat(e);const t={};t.h=""+parseInt(e/3600),t.m=""+parseInt(e/60-60*t.h),t.s=""+parseInt(e-(3600*t.h+60*t.m));for(const s of["m","s"])parseInt(t[s])<10&&(t[s]="0"+t[s]);const i=[];return parseInt(t.h)&&i.push(t.h),i.push(t.m,t.s),i.join(":")},async startStreaming(e,t,i=!1){let s=e,l=null;e instanceof Object?(s=e.url,l=e.subtitles):e={url:s};const o=await this.request(`${t}.start_streaming`,{media:s,subtitles:l,download:i});return{...e,...o}},async stopStreaming(e,t){await this.request(`${t}.stop_streaming`,{media_id:e})}}};const o=l;var a=o},671:function(e,t,i){i.d(t,{Z:function(){return v}});var s=i(6252),l=i(9963),o=i(3577);const a=e=>((0,s.dD)("data-v-77ea2884"),e=e(),(0,s.Cn)(),e),n={class:"dialog-content"},r={class:"buttons"},c=a((()=>(0,s._)("i",{class:"fas fa-check"},null,-1))),d=a((()=>(0,s._)("i",{class:"fas fa-xmark"},null,-1)));function h(e,t,i,a,h,p){const u=(0,s.up)("Modal");return(0,s.wg)(),(0,s.j4)(u,{ref:"modal",title:i.title},{default:(0,s.w5)((()=>[(0,s._)("form",{onSubmit:t[5]||(t[5]=(0,l.iM)(((...e)=>p.onConfirm&&p.onConfirm(...e)),["prevent"]))},[(0,s._)("div",n,[(0,s.WI)(e.$slots,"default",{},void 0,!0),(0,s.wy)((0,s._)("input",{type:"text",ref:"input","onUpdate:modelValue":t[0]||(t[0]=e=>h.value_=e)},null,512),[[l.nr,h.value_]])]),(0,s._)("div",r,[(0,s._)("button",{type:"submit",class:"ok-btn",onClick:t[1]||(t[1]=(...e)=>p.onConfirm&&p.onConfirm(...e)),onTouch:t[2]||(t[2]=(...e)=>p.onConfirm&&p.onConfirm(...e))},[c,(0,s.Uk)("   "+(0,o.zw)(i.confirmText),1)],32),(0,s._)("button",{type:"button",class:"cancel-btn",onClick:t[3]||(t[3]=(...e)=>p.close&&p.close(...e)),onTouch:t[4]||(t[4]=(...e)=>p.close&&p.close(...e))},[d,(0,s.Uk)("   "+(0,o.zw)(i.cancelText),1)],32)])],32)])),_:3},8,["title"])}var p=i(2918),u={emits:["input"],components:{Modal:p.Z},props:{title:{type:String},confirmText:{type:String,default:"OK"},cancelText:{type:String,default:"Cancel"},visible:{type:Boolean,default:!1},value:{type:String,default:""}},data(){return{value_:"",visible_:!1}},methods:{onConfirm(){this.value_?.trim()?.length&&this.$emit("input",this.value_),this.close()},open(){this.visible_||(this.value_=this.value,this.$refs.modal.show(),this.visible_=!0,this.focus())},close(){this.visible_&&(this.value_="",this.$refs.modal.hide(),this.visible_=!1)},show(){this.open()},hide(){this.close()},focus(){this.$nextTick((()=>{this.$refs.input.focus()}))}},watch:{visible(e){e?this.open():this.close()}},mounted(){this.visible_=this.visible,this.value_=this.value||""}},f=i(3744);const m=(0,f.Z)(u,[["render",h],["__scopeId","data-v-77ea2884"]]);var v=m}}]);
//# sourceMappingURL=8409.fc27b0c8.js.map