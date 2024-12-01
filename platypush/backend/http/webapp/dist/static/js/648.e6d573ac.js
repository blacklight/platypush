"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[648],{648:function(e,t,i){i.d(t,{A:function(){return et}});var s=i(641),l=i(3751),o=i(33);const a={class:"browser"},n={class:"nav",ref:"nav"},r={class:"path-container"},c={key:0,class:"path"},d={key:0,class:"separator"},u=["onClick"],h={class:"token"},p={key:0,class:"separator"},f={class:"btn-container"},m={key:2,class:"items",ref:"items"},v=["onClick"],y={class:"col-10"},k={class:"name"},g={key:0,class:"col-2 actions"},b={class:"modal-body"},w={key:3,class:"upload-file-container"},C={key:4,class:"info-modal-container"},F={class:"modal-body"},L={class:"copy-modal-container"},I={class:"modal-body"};function _(e,t,i,_,T,E){const x=(0,s.g2)("Loading"),$=(0,s.g2)("DropdownItem"),X=(0,s.g2)("Dropdown"),A=(0,s.g2)("Home"),S=(0,s.g2)("BrowserOptions"),D=(0,s.g2)("Modal"),R=(0,s.g2)("FileUploader"),W=(0,s.g2)("FileInfo"),B=(0,s.g2)("ConfirmDialog"),U=(0,s.g2)("FileEditor"),O=(0,s.g2)("TextPrompt"),H=(0,s.g2)("Browser",!0);return(0,s.uX)(),(0,s.CE)("div",a,[T.loading?((0,s.uX)(),(0,s.Wv)(x,{key:0})):(0,s.Q3)("",!0),(0,s.Lk)("div",n,[(0,s.Lk)("div",r,[E.hasHomepage?((0,s.uX)(),(0,s.CE)("span",c,[(0,s.Lk)("span",{class:"token",onClick:t[0]||(t[0]=(0,l.D$)((e=>T.path=null),["stop"]))},t[25]||(t[25]=[(0,s.Lk)("i",{class:"fa fa-home"},null,-1)])),E.pathTokens.length?((0,s.uX)(),(0,s.CE)("span",d,t[26]||(t[26]=[(0,s.Lk)("i",{class:"fa fa-chevron-right"},null,-1)]))):(0,s.Q3)("",!0)])):(0,s.Q3)("",!0),((0,s.uX)(!0),(0,s.CE)(s.FK,null,(0,s.pI)(E.pathTokens,((e,i)=>((0,s.uX)(),(0,s.CE)("span",{class:"path",key:i,onClick:(0,l.D$)((e=>T.path=E.pathTokens.slice(0,i+1).join("/").slice(1)),["stop"])},[(0,s.Lk)("span",h,(0,o.v_)(e),1),(i>0||E.pathTokens.length>1)&&i<E.pathTokens.length-1?((0,s.uX)(),(0,s.CE)("span",p,t[27]||(t[27]=[(0,s.Lk)("i",{class:"fa fa-chevron-right"},null,-1)]))):(0,s.Q3)("",!0)],8,u)))),128))]),(0,s.Lk)("div",f,[(0,s.bF)(X,{style:{"min-width":"11em"},onClick:t[5]||(t[5]=(0,l.D$)((()=>{}),["prevent"]))},{default:(0,s.k6)((()=>[(0,s.bF)($,{"icon-class":"fa fa-plus",text:"New Folder",onInput:t[1]||(t[1]=e=>T.showCreateDirectory=!0)}),(0,s.bF)($,{"icon-class":"fa fa-file",text:"Create File",onInput:t[2]||(t[2]=e=>T.showCreateFile=!0)}),(0,s.bF)($,{"icon-class":"fa fa-upload",text:"Upload",onInput:t[3]||(t[3]=e=>T.showUpload=!0)}),(0,s.bF)($,{"icon-class":"fa fa-sync",text:"Refresh",onInput:E.refresh},null,8,["onInput"]),(0,s.bF)($,{"icon-class":"fa fa-cog",text:"Options",onInput:t[4]||(t[4]=e=>T.showOptions=!0)})])),_:1})])],512),!T.path&&E.hasHomepage?((0,s.uX)(),(0,s.Wv)(A,{key:1,items:i.homepage,filter:i.filter,"has-back":i.hasBack,onBack:E.onBack,onInput:E.onItemSelect},null,8,["items","filter","has-back","onBack","onInput"])):((0,s.uX)(),(0,s.CE)("div",m,[T.path?.length&&"/"!==T.path||i.hasBack?((0,s.uX)(),(0,s.CE)("div",{key:0,class:"row item",onClick:t[6]||(t[6]=(0,l.D$)(((...e)=>E.onBack&&E.onBack(...e)),["stop"]))},t[28]||(t[28]=[(0,s.Lk)("div",{class:"col-10 left side"},[(0,s.Lk)("i",{class:"icon fa fa-folder"}),(0,s.Lk)("span",{class:"name"},"..")],-1)]))):(0,s.Q3)("",!0),i.hasSelectCurrentDirectory?((0,s.uX)(),(0,s.CE)("div",{key:1,class:"row item",ref:"selectCurrent",onClick:t[7]||(t[7]=(0,l.D$)(((...e)=>E.onSelectCurrentDirectory&&E.onSelectCurrentDirectory(...e)),["stop"]))},t[29]||(t[29]=[(0,s.Lk)("div",{class:"col-10 left side"},[(0,s.Lk)("i",{class:"icon fa fa-hand-point-right"}),(0,s.Lk)("span",{class:"name"},"<Select This Directory>")],-1)]),512)):(0,s.Q3)("",!0),((0,s.uX)(!0),(0,s.CE)(s.FK,null,(0,s.pI)(E.filteredFiles,((e,i)=>((0,s.uX)(),(0,s.CE)("div",{class:"row item",key:i,onClick:(0,l.D$)((t=>E.onItemSelect(e)),["stop"])},[(0,s.Lk)("div",y,[(0,s.Lk)("i",{class:(0,o.C4)(["icon fa",E.fileIcons[e.path]])},null,2),(0,s.Lk)("span",k,(0,o.v_)(e.name),1)]),Object.keys(E.fileActions[e.path]||{})?.length?((0,s.uX)(),(0,s.CE)("div",g,[(0,s.bF)(X,{style:{"min-width":"11em"},onClick:t[8]||(t[8]=(0,l.D$)((()=>{}),["prevent"]))},{default:(0,s.k6)((()=>[((0,s.uX)(!0),(0,s.CE)(s.FK,null,(0,s.pI)(E.fileActions[e.path],((t,i)=>((0,s.uX)(),(0,s.Wv)($,{key:i,"icon-class":t.iconClass,text:t.text,onInput:i=>t.onClick(e)},null,8,["icon-class","text","onInput"])))),128))])),_:2},1024)])):(0,s.Q3)("",!0)],8,v)))),128))],512)),(0,s.bF)(D,{title:"Options",visible:T.showOptions,onClose:t[9]||(t[9]=e=>T.showOptions=!1)},{default:(0,s.k6)((()=>[(0,s.Lk)("div",b,[(0,s.bF)(S,{value:T.opts,onInput:E.onOptsChange},null,8,["value","onInput"])])])),_:1},8,["visible"]),T.showUpload?((0,s.uX)(),(0,s.CE)("div",w,[(0,s.bF)(R,{path:T.path,visible:T.showUpload,ref:"uploader",onComplete:E.onUploadCompleted,onClose:t[10]||(t[10]=e=>T.showUpload=!1)},null,8,["path","visible","onComplete"])])):(0,s.Q3)("",!0),null!=T.showInfoFile?((0,s.uX)(),(0,s.CE)("div",C,[(0,s.bF)(D,{title:"File Info",visible:null!=T.showInfoFile,onClose:t[11]||(t[11]=e=>T.showInfoFile=null)},{default:(0,s.k6)((()=>[(0,s.Lk)("div",F,[(0,s.bF)(W,{file:T.showInfoFile,loading:T.loading},null,8,["file","loading"])])])),_:1},8,["visible"])])):(0,s.Q3)("",!0),(0,s.bF)(B,{visible:T.editWarnings.length>0,onClose:E.clearEditFile,onInput:t[12]||(t[12]=e=>E.editFile(T.editedFile,{force:!0}))},{default:(0,s.k6)((()=>[t[30]||(t[30]=(0,s.eW)(" The following warnings were raised: ")),(0,s.Lk)("ul",null,[((0,s.uX)(!0),(0,s.CE)(s.FK,null,(0,s.pI)(T.editWarnings,((e,t)=>((0,s.uX)(),(0,s.CE)("li",{key:t},(0,o.v_)(e),1)))),128))]),t[31]||(t[31]=(0,s.eW)(" Are you sure you that you want to edit the file? "))])),_:1},8,["visible","onClose"]),(0,s.bF)(B,{visible:null!=T.fileToRemove,onClose:t[13]||(t[13]=e=>T.fileToRemove=null),onInput:t[14]||(t[14]=e=>E.deleteFile(T.fileToRemove))},{default:(0,s.k6)((()=>[t[32]||(t[32]=(0,s.eW)(" Are you sure you that you want to delete this file?")),t[33]||(t[33]=(0,s.Lk)("br",null,null,-1)),t[34]||(t[34]=(0,s.Lk)("br",null,null,-1)),(0,s.Lk)("b",null,(0,o.v_)(T.fileToRemove),1)])),_:1},8,["visible"]),(0,s.bF)(B,{visible:null!=T.directoryToRemove,onClose:t[15]||(t[15]=e=>T.directoryToRemove=null),onInput:t[16]||(t[16]=e=>E.deleteDirectory(T.directoryToRemove))},{default:(0,s.k6)((()=>[t[35]||(t[35]=(0,s.eW)(" Are you sure you that you want to delete this directory?")),t[36]||(t[36]=(0,s.Lk)("br",null,null,-1)),t[37]||(t[37]=(0,s.Lk)("br",null,null,-1)),(0,s.Lk)("b",null,(0,o.v_)(T.directoryToRemove),1)])),_:1},8,["visible"]),(0,s.bF)(B,{visible:null!=T.directoryToRemove&&T.directoryNotEmpty,onClose:t[17]||(t[17]=e=>{T.directoryToRemove=null,T.directoryNotEmpty=!1}),onInput:t[18]||(t[18]=e=>E.deleteDirectory(T.directoryToRemove,{recursive:!0}))},{default:(0,s.k6)((()=>[t[38]||(t[38]=(0,s.eW)(" This directory is not empty. Are you sure you that you want to delete it?")),t[39]||(t[39]=(0,s.Lk)("br",null,null,-1)),t[40]||(t[40]=(0,s.Lk)("br",null,null,-1)),(0,s.Lk)("b",null,(0,o.v_)(T.directoryToRemove),1)])),_:1},8,["visible"]),T.editedFile&&!T.editWarnings?.length?((0,s.uX)(),(0,s.Wv)(U,{key:5,file:T.editedFile,"is-new":T.isNewFileEdit,visible:null!=T.editedFile,uppercase:!1,onClose:E.clearEditFile,onSave:E.refresh},null,8,["file","is-new","visible","onClose","onSave"])):(0,s.Q3)("",!0),(0,s.bF)(O,{visible:T.showCreateDirectory,onInput:t[19]||(t[19]=e=>E.createDirectory(e)),onClose:t[20]||(t[20]=e=>T.showCreateDirectory=!1)},{default:(0,s.k6)((()=>t[41]||(t[41]=[(0,s.eW)(" Enter the name of the new directory: ")]))),_:1},8,["visible"]),(0,s.bF)(O,{visible:T.showCreateFile,onInput:E.editNewFile,onClose:t[21]||(t[21]=e=>T.showCreateFile=!1)},{default:(0,s.k6)((()=>t[42]||(t[42]=[(0,s.eW)(" Enter the name of the new file: ")]))),_:1},8,["visible","onInput"]),(0,s.bF)(O,{visible:null!=T.fileToRename,value:E.displayedFileToRename,onInput:E.renameFile,onClose:t[22]||(t[22]=e=>T.fileToRename=null)},{default:(0,s.k6)((()=>[t[43]||(t[43]=(0,s.eW)(" Enter a new name for this file:")),t[44]||(t[44]=(0,s.Lk)("br",null,null,-1)),t[45]||(t[45]=(0,s.Lk)("br",null,null,-1)),(0,s.Lk)("b",null,(0,o.v_)(T.fileToRename),1)])),_:1},8,["visible","value","onInput"]),(0,s.Lk)("div",L,[E.showCopyModal?((0,s.uX)(),(0,s.Wv)(D,{key:0,title:(null!=T.copyFile?"Copy":"Move")+" File",visible:E.showCopyModal,onClose:t[24]||(t[24]=e=>E.showCopyModal=!1)},{default:(0,s.k6)((()=>[(0,s.Lk)("div",I,[(0,s.bF)(H,{path:T.path,"has-back":!0,"has-select-current-directory":!0,"show-directories":!0,"show-files":!1,onBack:t[23]||(t[23]=e=>{T.copyFile=null,T.moveFile=null}),onInput:E.copyOrMove},null,8,["path","onInput"])])])),_:1},8,["title","visible"])):(0,s.Q3)("",!0)])])}i(4114);const T={class:"browser-options"},E={key:1,class:"options-body"},x={class:"row item"},$=["checked","value"],X={class:"row item sort-container"},A=["value"],S=["selected"],D=["selected"],R=["selected"],W=["selected"],B=["checked"],U=["checked"];function O(e,t,i,l,o,a){const n=(0,s.g2)("Loading");return(0,s.uX)(),(0,s.CE)("div",T,[i.loading?((0,s.uX)(),(0,s.Wv)(n,{key:0})):((0,s.uX)(),(0,s.CE)("div",E,[(0,s.Lk)("div",x,[(0,s.Lk)("label",null,[(0,s.Lk)("input",{type:"checkbox",checked:i.value.showHidden,value:i.value.showHidden,onInput:t[0]||(t[0]=t=>e.$emit("input",{...i.value,showHidden:t.target.checked}))},null,40,$),t[4]||(t[4]=(0,s.eW)(" Show hidden files "))])]),(0,s.Lk)("div",X,[(0,s.Lk)("span",null,[(0,s.Lk)("label",null,[t[5]||(t[5]=(0,s.eW)(" Sort by ")),(0,s.Lk)("span",null,[(0,s.Lk)("select",{value:i.value.sortBy,onInput:t[1]||(t[1]=t=>e.$emit("input",{...i.value,sortBy:t.target.value}))},[(0,s.Lk)("option",{value:"name",selected:"name"===i.value.sortBy},"Name",8,S),(0,s.Lk)("option",{value:"size",selected:"size"===i.value.sortBy},"Size",8,D),(0,s.Lk)("option",{value:"created",selected:"created"===i.value.sortBy},"Creation Date",8,R),(0,s.Lk)("option",{value:"last_modified",selected:"last_modified"===i.value.sortBy},"Last Modified",8,W)],40,A)])])]),(0,s.Lk)("span",null,[(0,s.Lk)("label",null,[(0,s.Lk)("input",{type:"radio",checked:!i.value.reverseSort,onInput:t[2]||(t[2]=t=>e.$emit("input",{...i.value,reverseSort:!1}))},null,40,B),t[6]||(t[6]=(0,s.eW)(" Ascending "))]),(0,s.Lk)("label",null,[(0,s.Lk)("input",{type:"radio",checked:i.value.reverseSort,onInput:t[3]||(t[3]=t=>e.$emit("input",{...i.value,reverseSort:!0}))},null,40,U),t[7]||(t[7]=(0,s.eW)(" Descending "))])])])]))])}var H=i(9828),M=i(2002),Q={emits:["input"],mixins:[M.A],components:{Loading:H.A},props:{loading:{type:Boolean,default:!1},value:{type:Object,required:!0}}},q=i(6262);const j=(0,q.A)(Q,[["render",O],["__scopeId","data-v-c4abebfe"]]);var N=j,P=i(3538),z=i(9265),K=i(9612),G=i(1367);const V={class:"file-info"},J={key:1,class:"file-info-container"},Y={class:"row item"},Z={class:"value"},ee={key:0,class:"row item"},te={class:"value"},ie={key:1,class:"row item"},se={class:"value"},le={key:2,class:"row item"},oe={class:"value"},ae={key:3,class:"row item"},ne={class:"value"},re={key:4,class:"row item"},ce={class:"value"},de={key:5,class:"row item"},ue={class:"value"},he={key:6,class:"row item"},pe={class:"value"};function fe(e,t,i,l,a,n){const r=(0,s.g2)("Loading");return(0,s.uX)(),(0,s.CE)("div",V,[a.loading?((0,s.uX)(),(0,s.Wv)(r,{key:0})):a.info?((0,s.uX)(),(0,s.CE)("div",J,[(0,s.Lk)("div",Y,[t[0]||(t[0]=(0,s.Lk)("div",{class:"label"},"Path",-1)),(0,s.Lk)("div",Z,(0,o.v_)(a.info.path),1)]),null!=a.info.size?((0,s.uX)(),(0,s.CE)("div",ee,[t[1]||(t[1]=(0,s.Lk)("div",{class:"label"},"Size",-1)),(0,s.Lk)("div",te,(0,o.v_)(e.convertSize(a.info.size)),1)])):(0,s.Q3)("",!0),null!=a.info.created?((0,s.uX)(),(0,s.CE)("div",ie,[t[2]||(t[2]=(0,s.Lk)("div",{class:"label"},"Creation Date",-1)),(0,s.Lk)("div",se,(0,o.v_)(e.formatDate(a.info.created,!0)),1)])):(0,s.Q3)("",!0),null!=a.info.last_modified?((0,s.uX)(),(0,s.CE)("div",le,[t[3]||(t[3]=(0,s.Lk)("div",{class:"label"},"Last Modified",-1)),(0,s.Lk)("div",oe,(0,o.v_)(e.formatDate(a.info.last_modified,!0)),1)])):(0,s.Q3)("",!0),null!=a.info.mime_type?((0,s.uX)(),(0,s.CE)("div",ae,[t[4]||(t[4]=(0,s.Lk)("div",{class:"label"},"MIME type",-1)),(0,s.Lk)("div",ne,(0,o.v_)(a.info.mime_type),1)])):(0,s.Q3)("",!0),null!=a.info.permissions?((0,s.uX)(),(0,s.CE)("div",re,[t[5]||(t[5]=(0,s.Lk)("div",{class:"label"},"Permissions",-1)),(0,s.Lk)("div",ce,(0,o.v_)(a.info.permissions),1)])):(0,s.Q3)("",!0),null!=a.info.owner?((0,s.uX)(),(0,s.CE)("div",de,[t[6]||(t[6]=(0,s.Lk)("div",{class:"label"},"Owner ID",-1)),(0,s.Lk)("div",ue,(0,o.v_)(a.info.owner),1)])):(0,s.Q3)("",!0),null!=a.info.group?((0,s.uX)(),(0,s.CE)("div",he,[t[7]||(t[7]=(0,s.Lk)("div",{class:"label"},"Group ID",-1)),(0,s.Lk)("div",pe,(0,o.v_)(a.info.group),1)])):(0,s.Q3)("",!0)])):(0,s.Q3)("",!0)])}var me=i(226),ve={components:{Loading:H.A},mixins:[M.A,me.A],props:{file:{type:String}},data(){return{info:{},loading:!1}},methods:{async refresh(){this.loading=!0;try{this.info=(await this.request("file.info",{files:[this.file]}))[this.file]}finally{this.loading=!1}}},watch:{file(){this.refresh()}},mounted(){this.refresh()}};const ye=(0,q.A)(ve,[["render",fe],["__scopeId","data-v-417b1bc7"]]);var ke=ye;const ge={class:"upload-file-modal-container"},be={class:"modal-body"};function we(e,t,i,l,o,a){const n=(0,s.g2)("FileUploader"),r=(0,s.g2)("Modal");return(0,s.uX)(),(0,s.CE)("div",ge,[(0,s.bF)(r,{title:"Upload File(s)",visible:e.visible,onClose:t[3]||(t[3]=t=>e.$emit("close"))},{default:(0,s.k6)((()=>[(0,s.Lk)("div",be,[(0,s.bF)(n,{path:e.path,onComplete:t[0]||(t[0]=t=>e.$emit("complete")),onStart:t[1]||(t[1]=t=>e.$emit("start")),onError:t[2]||(t[2]=t=>e.$emit("error"))},null,8,["path"])])])),_:1},8,["visible"])])}const Ce={class:"upload-file-container"},Fe={class:"row file-input"},Le=["disabled"],Ie={class:"row btn-container"},_e=["disabled"],Te={class:"existing-files-container"},Ee={key:1,class:"progress-container"},xe={class:"filename"},$e={class:"progress-bar-container"},Xe=["value"];function Ae(e,t,i,a,n,r){const c=(0,s.g2)("Loading"),d=(0,s.g2)("ConfirmDialog");return(0,s.uX)(),(0,s.CE)("div",Ce,[n.uploading?((0,s.uX)(),(0,s.Wv)(c,{key:0})):(0,s.Q3)("",!0),(0,s.Lk)("form",{ref:"uploadForm",class:"upload-form",onSubmit:t[1]||(t[1]=(0,l.D$)((e=>r.uploadFiles()),["prevent"]))},[(0,s.Lk)("div",Fe,[(0,s.Lk)("input",{type:"file",ref:"files",multiple:"",disabled:n.uploading,onInput:t[0]||(t[0]=(...e)=>r.onFilesInput&&r.onFilesInput(...e))},null,40,Le)]),(0,s.Lk)("div",Ie,[(0,s.Lk)("button",{type:"submit",disabled:n.uploading||!n.hasFiles},t[2]||(t[2]=[(0,s.Lk)("i",{class:"fa fa-upload"},null,-1),(0,s.eW)("  Upload ")]),8,_e)])],544),(0,s.Lk)("div",Te,[((0,s.uX)(!0),(0,s.CE)(s.FK,null,(0,s.pI)(n.existingFiles,(e=>((0,s.uX)(),(0,s.Wv)(d,{key:e.name,visible:!0,onClose:t=>delete n.existingFiles[e.name],onInput:t=>r.uploadFiles([e],{force:!0})},{default:(0,s.k6)((()=>[t[3]||(t[3]=(0,s.eW)(" The file ")),(0,s.Lk)("b",null,(0,o.v_)(e.name),1),t[4]||(t[4]=(0,s.eW)(" already exists. Do you want to overwrite it? "))])),_:2},1032,["onClose","onInput"])))),128))]),Object.keys(n.progress||{}).length?((0,s.uX)(),(0,s.CE)("div",Ee,[((0,s.uX)(!0),(0,s.CE)(s.FK,null,(0,s.pI)(n.progress,((e,t)=>((0,s.uX)(),(0,s.CE)("div",{class:"row progress",key:t},[(0,s.Lk)("span",xe,(0,o.v_)(t),1),(0,s.Lk)("span",$e,[(0,s.Lk)("progress",{class:"progress-bar",value:e,max:"100"},null,8,Xe)])])))),128))])):(0,s.Q3)("",!0)])}var Se=i(4335),De={emits:["complete","error","start"],mixins:[M.A],components:{ConfirmDialog:P.A,Loading:H.A},props:{path:{type:String,required:!0}},data(){return{existingFiles:{},hasFiles:!1,progress:{},uploading:!1}},computed:{formFiles(){return this.$refs.files?.files?Array.from(this.$refs.files.files):[]}},methods:{async uploadFile(e,t){const{force:i}=t||{};i&&delete this.existingFiles[e.name];try{const t=i?"put":"post",s=await Se.A[t](`/file?path=${this.path}/${e.name}`,e,{onUploadProgress:t=>{this.progress[e.name]=Math.round(100*t.loaded/t.total)},headers:{"Content-Type":e.type}});return this.notify({title:"File uploaded",text:`${e.name} uploaded to ${this.path}`,image:{icon:"check"}}),{file:e,status:s.status}}catch(s){const t={file:e,status:s.response?.status,error:s.response?.data?.error};return 409!==t.status&&this.onUploadError(s),t}},async uploadFiles(e,t){const{force:i}=t||{};if(e=e||this.formFiles,e.forEach((e=>{delete this.existingFiles[e.name]})),!e?.length)return void this.notify({title:"No files selected",text:"Please select files to upload",warning:!0,image:{icon:"upload"}});this.onUploadStarted(e);const s=[];try{const t=await Promise.all(e.map((e=>this.uploadFile(e,{force:i}))));s.push(...t.filter((e=>e?.error))),s.length||this.onUploadCompleted()}finally{this.uploading=!1}const l=s.filter((e=>409===e?.status&&e?.error));this.existingFiles={...this.existingFiles,...l.reduce(((e,t)=>(e[t.file.name]=t.file,e)),{})}},onFilesInput(e){this.hasFiles=Array.from(e.target.files).length>0},onUploadStarted(e){this.uploading=!0,this.$emit("start"),this.notify({title:"Upload started",text:`Uploading ${e.length} file(s) to ${this.path}`,image:{icon:"upload"}})},onUploadCompleted(){this.uploading=!1,this.$emit("complete")},onUploadError(e){const t=e.response?.data?.error;t&&(e.message=`${e.message}: ${t}`),this.$emit("error",e),this.notify({title:"Upload error",text:e.message,error:!0,image:{icon:"upload"}})}}};const Re=(0,q.A)(De,[["render",Ae],["__scopeId","data-v-67b7ea3b"]]);var We=Re,Be=i(9513),Ue={mixins:[We,Be.A],components:{FileUploader:We,Modal:Be.A}};const Oe=(0,q.A)(Ue,[["render",we],["__scopeId","data-v-f6e584b8"]]);var He=Oe;const Me={class:"browser-home"},Qe={class:"items",ref:"items"},qe=["onClick"],je={class:"icon-container"},Ne=["src"],Pe={class:"name"};function ze(e,t,i,l,a,n){return(0,s.uX)(),(0,s.CE)("div",Me,[(0,s.Lk)("div",Qe,[i.hasBack?((0,s.uX)(),(0,s.CE)("div",{key:0,class:"row item",onClick:t[0]||(t[0]=t=>e.$emit("back"))},t[1]||(t[1]=[(0,s.Lk)("div",{class:"icon-container"},[(0,s.Lk)("i",{class:"icon fa fa-chevron-left"})],-1),(0,s.Lk)("span",{class:"name"},"Back",-1)]))):(0,s.Q3)("",!0),((0,s.uX)(!0),(0,s.CE)(s.FK,null,(0,s.pI)(n.filteredItems,((t,i)=>((0,s.uX)(),(0,s.CE)("div",{class:"row item",key:i,onClick:i=>e.$emit("input",t)},[(0,s.Lk)("div",je,[t.icon?.url?.length?((0,s.uX)(),(0,s.CE)("img",{key:0,class:"icon",src:t.icon.url},null,8,Ne)):((0,s.uX)(),(0,s.CE)("i",{key:1,class:(0,o.C4)(["icon",t.icon?.["class"]||"fas fa-folder"])},null,2))]),(0,s.Lk)("span",Pe,(0,o.v_)(i),1)],8,qe)))),128))],512)])}var Ke={mixins:[M.A],emits:["back","input"],props:{hasBack:{type:Boolean,default:!1},filter:{type:String,default:""},items:{type:Object,required:!0},includeHome:{type:Boolean,default:!0},includeRoot:{type:Boolean,default:!0}},data(){return{userHome:null}},computed:{allItems(){return Object.entries({...this.includeRoot?{Root:{name:"Root",path:"/",icon:{class:"fas fa-hard-drive"}}}:{},...this.includeHome&&this.userHome?{Home:{name:"Home",path:this.userHome,icon:{class:"fas fa-home"}}}:{},...this.items}).reduce(((e,[t,i])=>(i.type?.length||(i.type="directory"),e[t]={name:t,...i},e)),{})},filteredItems(){return Object.fromEntries(Object.entries(this.allItems).filter((e=>e[0].toLowerCase().includes(this.filter.toLowerCase()))))}},methods:{async getUserHome(){return this.userHome||(this.userHome=await this.request("file.get_user_home")),this.userHome}},mounted(){this.getUserHome()}};const Ge=(0,q.A)(Ke,[["render",ze],["__scopeId","data-v-e2c178b2"]]);var Ve=Ge,Je=i(710),Ye={emits:["back","input","path-change","play"],mixins:[M.A,me.A],components:{BrowserOptions:N,ConfirmDialog:P.A,DropdownItem:K.A,Dropdown:z.A,FileEditor:G.A,FileInfo:ke,FileUploader:He,Home:Ve,Loading:H.A,Modal:Be.A,TextPrompt:Je.A},props:{hasBack:{type:Boolean,default:!1},hasSelectCurrentDirectory:{type:Boolean,default:!1},initialPath:{type:String},isMedia:{type:Boolean},filter:{type:String,default:""},filterTypes:{type:Array,default:()=>[]},homepage:{type:Object},showDirectories:{type:Boolean,default:!0},showFiles:{type:Boolean,default:!0}},data(){return{copyFile:null,directoryNotEmpty:!1,directoryToRemove:null,editedFile:null,editWarnings:[],files:[],fileToRemove:null,fileToRename:null,info:{},isNewFileEdit:!1,loading:!1,mimeTypes:{},moveFile:null,opts:{showHidden:!1,sortBy:"name",reverseSort:!1},path:this.initialPath,showCreateDirectory:!1,showCreateFile:!1,showInfoFile:null,showOptions:!1,showUpload:!1,uploading:!1}},computed:{displayedFileToRename(){return this.fileToRename?.slice(this.path.length+1)||""},editedFileName(){return this.editedFile?.split("/").pop()||"Untitled"},filteredTypesMap(){return this.filterTypes.reduce(((e,t)=>(e[t]=!0,t.split("/").forEach((t=>{e[t]=!0})),e)),{})},filteredFiles(){return this.files.filter((e=>{if("directory"===e.type&&!this.showDirectories)return!1;if("directory"!==e.type&&!this.showFiles)return!1;if((e?.name||"").toLowerCase().indexOf(this.filter.toLowerCase())<0)return!1;if(!this.opts.showHidden&&e.name.startsWith("."))return!1;if(this.filterTypes.length){const t=this.mimeTypes[e.path]||"",i=[t,...t.split("/")];if(!i.some((e=>this.fileredTypesMap[e])))return!1}return!0}))},fileActions(){return this.files.reduce(((e,t)=>{const i=this.mimeTypes[t.path]||"";return e[t.path]={},this.isMedia&&(i.startsWith("audio/")||i.startsWith("video/"))&&(e[t.path]={play:{iconClass:"fa fa-play",text:"Play",onClick:e=>this.$emit("play",{type:"file",url:`file://${e.path}`})}}),"directory"!==t.type?(e[t.path].view={iconClass:"fa fa-eye",text:"View",onClick:e=>this.viewFile(e.path)},e[t.path].download={iconClass:"fa fa-download",text:"Download",onClick:e=>this.downloadFile(e.path)},e[t.path].edit={iconClass:"fa fa-edit",text:"Edit",onClick:e=>this.editFile(e.path)},e[t.path].copy={iconClass:"fa fa-copy",text:"Copy",onClick:e=>this.copyFile=e.path},e[t.path].move={iconClass:"fa fa-arrows-alt",text:"Move",onClick:e=>this.moveFile=e.path},e[t.path].rename={iconClass:"fa fa-pen",text:"Rename",onClick:e=>this.fileToRename=e.path},e[t.path].info={iconClass:"fa fa-info",text:"Info",onClick:e=>this.showInfoFile=e.path},e[t.path].delete={iconClass:"delete fa fa-trash",text:"Delete",onClick:e=>this.fileToRemove=e.path}):e[t.path].delete={iconClass:"delete fa fa-trash",text:"Delete",onClick:e=>this.directoryToRemove=e.path},e}),{})},fileIcons(){return this.files.reduce(((e,t)=>{if("directory"===t.type)e[t.path]="fa-folder";else{const i=this.mimeTypes[t.path]||"";switch(!0){case i.startsWith("audio/"):e[t.path]="fa-file-audio";break;case i.startsWith("video/"):e[t.path]="fa-file-video";break;case i.startsWith("image/"):e[t.path]="fa-file-image";break;case i.startsWith("text/"):e[t.path]="fa-file-alt";break;default:e[t.path]="fa-file";break}}return e}),{})},hasHomepage(){return Object.keys(this.homepage||{}).length},pathTokens(){return this.path?this.path?.length?["/",...this.path.split(/(?<!\\)\//).slice(1)].filter((e=>e.length)):["/"]:[]},showCopyModal(){return null!=this.copyFile||null!=this.moveFile}},methods:{initOpts(){const e=this.getUrlArgs();null!=e.showHidden&&(this.opts.showHidden=!!e.showHidden),null!=e.sortBy&&(this.opts.sortBy=e.sortBy),null!=e.reverseSort&&(this.opts.reverseSort=!!e.reverseSort),null!=e.file&&(this.editedFile=e.file)},async refresh(){this.loading=!0,this.$nextTick((()=>{this.$refs.nav&&(this.$refs.nav.scrollLeft=99999),this.$refs.items&&(this.$refs.items.scrollTop=0)}));try{this.files=await this.request("file.list",{path:this.path,sort:this.opts.sortBy,reverse:this.opts.reverseSort}),this.$emit("path-change",this.path),this.setUrlArgs({path:decodeURIComponent(this.path)})}finally{this.loading=!1}await this.refreshMimeTypes()},async refreshMimeTypes(){this.mimeTypes=await this.request("file.get_mime_types",{files:this.files.filter((e=>"directory"!==e.type)).map((e=>e.path))})},viewFile(e){window.open(`/file?path=${encodeURIComponent(e)}`,"_blank")},async editNewFile(e){return await this.editFile(`${this.path}/${e}`,{newFile:!0})},async editFile(e,t){const i=!!t?.force,s=this.isNewFileEdit=!!t?.newFile;if(i)this.editWarnings=[];else if(!s){const[t,i]=await Promise.all([this.request("file.info",{files:[e]}),this.request("file.is_binary",{file:e})]),s=t?.[e]?.size||0;if(i&&this.editWarnings.push("File is binary"),(t[e]?.size||0)>1048576&&this.editWarnings.push(`File is too large (${this.convertSize(s)})`),this.editWarnings.length)return void(this.editedFile=e)}this.editedFile=e},async deleteFile(){if(this.fileToRemove){this.loading=!0;try{await this.request("file.unlink",{file:this.fileToRemove})}finally{this.loading=!1,this.fileToRemove=null}this.refresh()}},async deleteDirectory(e,t){if(e=e||this.directoryToRemove,!e)return;const i=!!t?.recursive;let s=!1;this.loading=!0;try{await this.request("file.rmdir",{directory:e,recursive:i})}catch(l){"string"===typeof l&&l.search(/^\[?Errno 39\]?/i)>=0&&(s=!0)}finally{this.loading=!1,this.directoryNotEmpty=s,s||(this.directoryToRemove=null)}s?this.directoryToRemove=e:this.refresh()},async createDirectory(e){if(e){this.loading=!0;try{await this.request("file.mkdir",{directory:`${this.path}/${e}`})}finally{this.loading=!1}this.refresh()}},async copyOrMove(e){let t=null,i=null;if(this.copyFile)t="copy",i=this.copyFile;else{if(!this.moveFile)return;t="move",i=this.moveFile}this.loading=!0;try{await this.request(`file.${t}`,{source:i,target:e}),this.notify({text:`File ${t} completed successfully`,title:"Success",image:{icon:"check"}})}finally{this.loading=!1,this.copyFile=null,this.moveFile=null}this.refresh()},async renameFile(e){if(this.fileToRename&&e?.trim()?.length){this.loading=!0;try{await this.request("file.rename",{file:this.fileToRename,name:`${this.path}/${e}`})}finally{this.loading=!1,this.fileToRename=null}this.refresh()}},clearEditFile(){this.editedFile=null,this.editWarnings=[]},downloadFile(e){window.open(`/file?path=${encodeURIComponent(e)}&download=true`,"_blank")},onOptsChange(e){this.opts=e},onBack(){this.path?.length&&"/"!==this.path?this.path=[...this.pathTokens].slice(0,-1).join("/").slice(1):this.$emit("back")},onItemSelect(e){"directory"===e.type?this.path=e.path:this.$emit("input",e.path)},onSelectCurrentDirectory(){this.$emit("input",this.path)},onUploadCompleted(){this.refresh()}},watch:{initialPath(){this.path=this.initialPath},opts:{deep:!0,handler(){this.setUrlArgs(this.opts),this.refresh()}},path(e,t){t!==e&&this.refresh()},showUpload(e){const t=this.$refs.uploader;e?(t?.open(),this.$nextTick((()=>{t?.focus()}))):t?.close()}},mounted(){const e=this.getUrlArgs();e.path&&(this.path=e.path),this.initOpts(),this.refresh()}};const Ze=(0,q.A)(Ye,[["render",_],["__scopeId","data-v-0c7b0e28"]]);var et=Ze},226:function(e,t,i){i.d(t,{A:function(){return a}});i(4114);var s=i(2002),l={name:"Utils",mixins:[s.A],computed:{audioExtensions(){return new Set(["3gp","aa","aac","aax","act","aiff","amr","ape","au","awb","dct","dss","dvf","flac","gsm","iklax","ivs","m4a","m4b","m4p","mmf","mp3","mpc","msv","nmf","nsf","ogg,","opus","ra,","raw","sln","tta","vox","wav","wma","wv","webm","8svx"])},videoExtensions(){return new Set(["webm","mkv","flv","flv","vob","ogv","ogg","drc","gif","gifv","mng","avi","mts","m2ts","mov","qt","wmv","yuv","rm","rmvb","asf","amv","mp4","m4p","m4v","mpg","mp2","mpeg","mpe","mpv","mpg","mpeg","m2v","m4v","svi","3gp","3g2","mxf","roq","nsv","flv","f4v","f4p","f4a","f4b"])},mediaExtensions(){return new Set([...this.videoExtensions,...this.audioExtensions])}},methods:{convertTime(e){e=parseFloat(e);const t={};t.h=""+parseInt(e/3600),t.m=""+parseInt(e/60-60*t.h),t.s=""+parseInt(e-(3600*t.h+60*t.m));for(const s of["m","s"])parseInt(t[s])<10&&(t[s]="0"+t[s]);const i=[];return parseInt(t.h)&&i.push(t.h),i.push(t.m,t.s),i.join(":")},async startStreaming(e,t,i=!1){let s=e,l=null;e instanceof Object?(s=e.url,l=e.subtitles):e={url:s};const o=await this.request(`${t}.start_streaming`,{media:s,subtitles:l,download:i});return{...e,...o}},async stopStreaming(e,t){await this.request(`${t}.stop_streaming`,{media_id:e})}}};const o=l;var a=o},710:function(e,t,i){i.d(t,{A:function(){return p}});var s=i(641),l=i(3751),o=i(33);const a={class:"dialog-content"},n={class:"buttons"};function r(e,t,i,r,c,d){const u=(0,s.g2)("Modal");return(0,s.uX)(),(0,s.Wv)(u,{ref:"modal",title:i.title},{default:(0,s.k6)((()=>[(0,s.Lk)("form",{onSubmit:t[5]||(t[5]=(0,l.D$)(((...e)=>d.onConfirm&&d.onConfirm(...e)),["prevent"]))},[(0,s.Lk)("div",a,[(0,s.RG)(e.$slots,"default",{},void 0,!0),(0,s.bo)((0,s.Lk)("input",{type:"text",ref:"input","onUpdate:modelValue":t[0]||(t[0]=e=>c.value_=e)},null,512),[[l.Jo,c.value_]])]),(0,s.Lk)("div",n,[(0,s.Lk)("button",{type:"submit",class:"ok-btn",onClick:t[1]||(t[1]=(...e)=>d.onConfirm&&d.onConfirm(...e)),onTouch:t[2]||(t[2]=(...e)=>d.onConfirm&&d.onConfirm(...e))},[t[6]||(t[6]=(0,s.Lk)("i",{class:"fas fa-check"},null,-1)),(0,s.eW)("   "+(0,o.v_)(i.confirmText),1)],32),(0,s.Lk)("button",{type:"button",class:"cancel-btn",onClick:t[3]||(t[3]=(...e)=>d.close&&d.close(...e)),onTouch:t[4]||(t[4]=(...e)=>d.close&&d.close(...e))},[t[7]||(t[7]=(0,s.Lk)("i",{class:"fas fa-xmark"},null,-1)),(0,s.eW)("   "+(0,o.v_)(i.cancelText),1)],32)])],32)])),_:3},8,["title"])}var c=i(9513),d={emits:["input"],components:{Modal:c.A},props:{title:{type:String},confirmText:{type:String,default:"OK"},cancelText:{type:String,default:"Cancel"},visible:{type:Boolean,default:!1},value:{type:String,default:""}},data(){return{value_:"",visible_:!1}},methods:{onConfirm(){this.value_?.trim()?.length&&this.$emit("input",this.value_),this.close()},open(){this.visible_||(this.value_=this.value,this.$refs.modal.show(),this.visible_=!0,this.focus())},close(){this.visible_&&(this.value_="",this.$refs.modal.hide(),this.visible_=!1)},show(){this.open()},hide(){this.close()},focus(){this.$nextTick((()=>{this.$refs.input.focus()}))}},watch:{visible(e){e?this.open():this.close()}},mounted(){this.visible_=this.visible,this.value_=this.value||""}},u=i(6262);const h=(0,u.A)(d,[["render",r],["__scopeId","data-v-77ea2884"]]);var p=h}}]);
//# sourceMappingURL=648.e6d573ac.js.map