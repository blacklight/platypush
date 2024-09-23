"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[293],{3825:function(e,t,s){s.d(t,{Z:function(){return u}});var n=s(6252),a=s(3577);const o=["disabled","title"];function i(e,t,s,i,r,l){const d=(0,n.up)("Icon");return(0,n.wg)(),(0,n.iD)("div",{class:(0,a.C_)(["floating-btn",l.classes])},[(0,n._)("button",{type:"button",class:(0,a.C_)(["btn btn-primary",s.glow?"with-glow":""]),disabled:s.disabled,title:s.title,onClick:t[0]||(t[0]=t=>e.$emit("click",t))},[(0,n.Wm)(d,{class:(0,a.C_)(s.iconClass),url:s.iconUrl},null,8,["class","url"])],10,o)],2)}var r=s(657),l={components:{Icon:r.Z},emits:["click"],props:{disabled:{type:Boolean,default:!1},iconClass:{type:String},iconUrl:{type:String},class:{type:String},title:{type:String},left:{type:Boolean,default:!1},right:{type:Boolean,default:!0},top:{type:Boolean,default:!1},bottom:{type:Boolean,default:!0},glow:{type:Boolean,default:!1}},computed:{classes(){const e={};return this.left?e.left=!0:e.right=!0,this.top?e.top=!0:e.bottom=!0,this.class?.length&&(e[this.class]=!0),e}}},d=s(3744);const c=(0,d.Z)(l,[["render",i],["__scopeId","data-v-544409fc"]]);var u=c},2717:function(e,t,s){s.d(t,{Z:function(){return h}});var n=s(6252);const a=e=>((0,n.dD)("data-v-2edff8b7"),e=e(),(0,n.Cn)(),e),o={class:"restart-btn-container"},i=a((()=>(0,n._)("i",{class:"fas fa-redo-alt"},null,-1)));function r(e,t,s,a,r,l){const d=(0,n.up)("ConfirmDialog");return(0,n.wg)(),(0,n.iD)("div",o,[(0,n.Wm)(d,{ref:"modal",onInput:l.restart},{default:(0,n.w5)((()=>[(0,n.Uk)(" Are you sure that you want to restart the application? ")])),_:1},8,["onInput"]),(0,n._)("button",{class:"btn btn-default restart-btn",onClick:t[0]||(t[0]=(...e)=>l.showDialog&&l.showDialog(...e)),onTouch:t[1]||(t[1]=(...e)=>l.showDialog&&l.showDialog(...e))},[i,(0,n.Uk)("   Restart Application ")],32)])}var l=s(3513),d=s(8637),c={name:"RestartButton",components:{ConfirmDialog:l.Z},mixins:[d.Z],methods:{showDialog(){this.$refs.modal.show()},async restart(){await this.request("application.restart")}}},u=s(3744);const p=(0,u.Z)(c,[["render",r],["__scopeId","data-v-2edff8b7"]]);var h=p},7514:function(e,t,s){s.d(t,{Z:function(){return f}});var n=s(6252),a=s(3577),o=s(9963);const i=e=>((0,n.dD)("data-v-eff375b6"),e=e(),(0,n.Cn)(),e),r=["checked","id"],l=i((()=>(0,n._)("div",{class:"switch"},[(0,n._)("div",{class:"dot"})],-1))),d={class:"label"};function c(e,t,s,i,c,u){return(0,n.wg)(),(0,n.iD)("div",{class:(0,a.C_)(["power-switch",{disabled:s.disabled}]),onClick:t[0]||(t[0]=(0,o.iM)(((...e)=>u.onInput&&u.onInput(...e)),["stop"]))},[(0,n._)("input",{type:"checkbox",checked:s.value,id:s.id},null,8,r),(0,n._)("label",null,[l,(0,n._)("span",d,[(0,n.WI)(e.$slots,"default",{},void 0,!0)])])],2)}var u={name:"ToggleSwitch",emits:["input"],props:{id:{type:String},value:{type:Boolean,default:!1},disabled:{type:Boolean,default:!1}},methods:{onInput(e){if(this.disabled)return!1;this.$emit("input",e)}}},p=s(3744);const h=(0,p.Z)(u,[["render",c],["__scopeId","data-v-eff375b6"]]);var f=h},293:function(e,t,s){s.r(t),s.d(t,{default:function(){return tt}});var n=s(6252);const a={class:"settings-container"};function o(e,t,s,o,i,r){const l=(0,n.up)("Application"),d=(0,n.up)("Users"),c=(0,n.up)("Tokens");return(0,n.wg)(),(0,n.iD)("div",a,[(0,n._)("main",null,["application"===s.selectedPanel?((0,n.wg)(),(0,n.j4)(l,{key:0})):(0,n.kq)("",!0),"users"===s.selectedPanel&&i.currentUser?((0,n.wg)(),(0,n.j4)(d,{key:1,"session-token":i.sessionToken,"current-user":i.currentUser},null,8,["session-token","current-user"])):"tokens"===s.selectedPanel&&i.currentUser?((0,n.wg)(),(0,n.j4)(c,{key:2,"current-user":i.currentUser},null,8,["current-user"])):(0,n.kq)("",!0)])])}const i={class:"app-container"},r={class:"btn-container"},l={class:"btn-container"};function d(e,t,s,a,o,d){const c=(0,n.up)("RestartButton"),u=(0,n.up)("StopButton");return(0,n.wg)(),(0,n.iD)("div",i,[(0,n._)("div",r,[(0,n.Wm)(c)]),(0,n._)("div",l,[(0,n.Wm)(u)])])}var c=s(2717);const u=e=>((0,n.dD)("data-v-1eab04fa"),e=e(),(0,n.Cn)(),e),p={class:"stop-btn-container"},h=u((()=>(0,n._)("br",null,null,-1))),f=u((()=>(0,n._)("br",null,null,-1))),g=u((()=>(0,n._)("span",{class:"text-danger"}," This will stop the application and you will not be able to restart it through the Web interface! ",-1))),m=u((()=>(0,n._)("i",{class:"fas fa-stop"},null,-1)));function w(e,t,s,a,o,i){const r=(0,n.up)("ConfirmDialog");return(0,n.wg)(),(0,n.iD)("div",p,[(0,n.Wm)(r,{ref:"modal",onInput:i.stop},{default:(0,n.w5)((()=>[(0,n.Uk)(" Are you sure that you want to stop the application? "),h,f,g])),_:1},8,["onInput"]),(0,n._)("button",{class:"btn btn-default stop-btn",onClick:t[0]||(t[0]=(...e)=>i.showDialog&&i.showDialog(...e)),onTouch:t[1]||(t[1]=(...e)=>i.showDialog&&i.showDialog(...e))},[m,(0,n.Uk)("   Stop Application ")],32)])}var b=s(3513),y=s(8637),_={name:"StopButton",components:{ConfirmDialog:b.Z},mixins:[y.Z],methods:{showDialog(){this.$refs.modal.show()},async stop(){await this.request("application.stop")}}},C=s(3744);const k=(0,C.Z)(_,[["render",w],["__scopeId","data-v-1eab04fa"]]);var v=k,O={name:"Application",components:{RestartButton:c.Z,StopButton:v}};const U=(0,C.Z)(O,[["render",d],["__scopeId","data-v-40365cea"]]);var D=U,T=s(215),P=s(3577);const A=["disabled"],x=["disabled"],$=["disabled"],q=["disabled"],M=["value"],Z=["disabled"],R=["disabled"],I=["disabled"],S=["disabled"],F={class:"body"},E={class:"users-list"},W=["onClick"],B=["textContent"],j={class:"actions pull-right col-4"};function Q(e,t,s,a,o,i){const r=(0,n.up)("Loading"),l=(0,n.up)("Modal"),d=(0,n.up)("Otp"),c=(0,n.up)("DropdownItem"),u=(0,n.up)("Dropdown"),p=(0,n.up)("FloatingButton"),h=(0,n.up)("ConfirmDialog");return(0,n.wg)(),(0,n.iD)(n.HY,null,[o.loading?((0,n.wg)(),(0,n.j4)(r,{key:0})):(0,n.kq)("",!0),(0,n.Wm)(l,{ref:"addUserModal",title:"Add User"},{default:(0,n.w5)((()=>[(0,n._)("form",{action:"#",method:"POST",ref:"addUserForm",onSubmit:t[0]||(t[0]=(...e)=>i.createUser&&i.createUser(...e))},[(0,n._)("label",null,[(0,n._)("input",{type:"text",name:"username",placeholder:"Username",disabled:o.commandRunning},null,8,A)]),(0,n._)("label",null,[(0,n._)("input",{type:"password",name:"password",placeholder:"Password",disabled:o.commandRunning},null,8,x)]),(0,n._)("label",null,[(0,n._)("input",{type:"password",name:"confirm_password",placeholder:"Confirm password",disabled:o.commandRunning},null,8,$)]),(0,n._)("label",null,[(0,n._)("input",{type:"submit",class:"btn btn-primary",value:"Create User",disabled:o.commandRunning},null,8,q)])],544)])),_:1},512),(0,n.Wm)(l,{ref:"changePasswordModal",title:"Change Password"},{default:(0,n.w5)((()=>[(0,n._)("form",{action:"#",method:"POST",ref:"changePasswordForm",onSubmit:t[1]||(t[1]=(...e)=>i.changePassword&&i.changePassword(...e))},[(0,n._)("label",null,[(0,n._)("input",{type:"text",name:"username",placeholder:"Username",value:o.selectedUser,disabled:"disabled"},null,8,M)]),(0,n._)("label",null,[(0,n._)("input",{type:"password",name:"password",placeholder:"Current password",disabled:o.commandRunning},null,8,Z)]),(0,n._)("label",null,[(0,n._)("input",{type:"password",name:"new_password",placeholder:"New password",disabled:o.commandRunning},null,8,R)]),(0,n._)("label",null,[(0,n._)("input",{type:"password",name:"confirm_new_password",placeholder:"Confirm new password",disabled:o.commandRunning},null,8,I)]),(0,n._)("label",null,[(0,n._)("input",{type:"submit",class:"btn btn-primary",value:"Change Password",disabled:o.commandRunning},null,8,S)])],544)])),_:1},512),(0,n.Wm)(l,{title:"Two-factor Authentication",visible:o.showOtpModal,onClose:t[2]||(t[2]=e=>o.showOtpModal=!1)},{default:(0,n.w5)((()=>[o.showOtpModal?((0,n.wg)(),(0,n.j4)(d,{key:0})):(0,n.kq)("",!0)])),_:1},8,["visible"]),(0,n._)("div",F,[(0,n._)("ul",E,[((0,n.wg)(!0),(0,n.iD)(n.HY,null,(0,n.Ko)(o.users,(s=>((0,n.wg)(),(0,n.iD)("li",{key:s.user_id,class:"item user",onClick:e=>o.selectedUser=s.username},[(0,n._)("div",{class:"name col-8",textContent:(0,P.zw)(s.username)},null,8,B),(0,n._)("div",j,[(0,n.Wm)(u,{title:"User Actions","icon-class":"fa fa-ellipsis"},{default:(0,n.w5)((()=>[(0,n.Wm)(c,{text:"Change Password",disabled:o.commandRunning,"icon-class":"fa fa-key",onInput:e=>i.showChangePasswordModal(s)},null,8,["disabled","onInput"]),(0,n.Wm)(c,{text:"Set Up 2FA",disabled:o.commandRunning||!i.supports2fa,"icon-class":"fa fa-lock",title:i.mfaTitle,onInput:t[3]||(t[3]=e=>o.showOtpModal=!0)},null,8,["disabled","title"]),(0,n.Wm)(c,{text:"Delete User",disabled:o.commandRunning,"icon-class":"fa fa-trash","item-class":"text-danger",onInput:t=>{o.selectedUser=s.username,e.$refs.deleteUserDialog.show()}},null,8,["disabled","onInput"])])),_:2},1024)])],8,W)))),128))]),(0,n.Wm)(p,{"icon-class":"fa fa-plus",text:"Add User",onClick:i.showAddUserModal},null,8,["onClick"]),(0,n.Wm)(h,{ref:"deleteUserDialog",onInput:t[4]||(t[4]=e=>i.deleteUser(o.selectedUser))},{default:(0,n.w5)((()=>[(0,n.Uk)(" Are you sure that you want to remove the user "+(0,P.zw)(o.selectedUser)+"? ",1)])),_:1},512)])],64)}s(560);var z=s(4660),L=s(2918),Y=s(6791),N=s(9963);const H=e=>((0,n.dD)("data-v-24d32b46"),e=e(),(0,n.Cn)(),e),K={class:"otp-config-container"},G={key:1,class:"otp-config"},J={class:"title"},V=H((()=>(0,n._)("p",{class:"description"}," Two-factor authentication adds an extra layer of security to your account. When enabled, you will need to enter a code from your authenticator app in addition to your password. ",-1))),X={key:0,class:"current-otp-config"},ee={class:"header"},te=H((()=>(0,n._)("h4",null,"2FA Configuration",-1))),se=["disabled"],ne=H((()=>(0,n._)("i",{class:"fas fa-save"},null,-1))),ae=H((()=>(0,n._)("div",{class:"description"},[(0,n._)("p",null,"Scan the QR code with your authenticator app to add this account."),(0,n._)("p",null,"Alternatively, you can add either the secret or the provisioning URL to your password manager or authenticator app.")],-1))),oe={key:0,class:"section qrcode-container"},ie=["src"],re={key:1,class:"section secret-container"},le=H((()=>(0,n._)("h4",null,"Secret",-1))),de=["value"],ce={key:2,class:"section uri-container"},ue=H((()=>(0,n._)("h4",null,"Provisioning URL",-1))),pe=["value"],he={key:3,class:"section backup-codes"},fe={class:"header"},ge=H((()=>(0,n._)("h4",null,"Backup Codes",-1))),me=["disabled"],we=H((()=>(0,n._)("i",{class:"fas fa-sync"},null,-1))),be={key:0,class:"description"},ye=H((()=>(0,n._)("p",null," Backup Codes are one-time use codes that can be used to access your account in case you lose access to your authenticator app. ",-1))),_e=H((()=>(0,n._)("p",null,"Make sure to store them in a safe place.",-1))),Ce=H((()=>(0,n._)("p",null,[(0,n._)("b",null," Take note of these codes NOW! You will not be able to see them again! ")],-1))),ke=[ye,_e,Ce],ve=["value"],Oe={class:"confirm-modal"},Ue={key:0,class:"dialog"},De=H((()=>(0,n._)("p",null,"Are you sure you want to enable Two-Factor Authentication?",-1))),Te=H((()=>(0,n._)("p",null,"Make sure to save the secret and backup codes in a safe place.",-1))),Pe=H((()=>(0,n._)("p",null," In order to enable Two-Factor Authentication, you will need to enter your password and a code from your authenticator app. ",-1))),Ae=[De,Te,Pe],xe={key:1,class:"dialog"},$e=H((()=>(0,n._)("p",null,"Are you sure you want to disable Two-Factor Authentication?",-1))),qe=H((()=>(0,n._)("p",null," You will no longer need to enter a code from your authenticator app. You will still need to enter your password to log in, but your account may be less secure. ",-1))),Me=H((()=>(0,n._)("p",null," In order to disable Two-Factor Authentication, you will need to enter your password. ",-1))),Ze=[$e,qe,Me],Re=["disabled"],Ie=["disabled"],Se=["disabled"],Fe={class:"buttons"},Ee=["disabled"],We=H((()=>(0,n._)("i",{class:"fas fa-check"},null,-1))),Be=H((()=>(0,n._)("i",{class:"fas fa-times"},null,-1)));function je(e,t,s,a,o,i){const r=(0,n.up)("Loading"),l=(0,n.up)("ToggleSwitch"),d=(0,n.up)("ConfirmDialog"),c=(0,n.up)("Modal");return(0,n.wg)(),(0,n.iD)("div",K,[o.initializing?((0,n.wg)(),(0,n.j4)(r,{key:0})):((0,n.wg)(),(0,n.iD)("div",G,[(0,n._)("div",J,[(0,n._)("h3",null,"Two-Factor Authentication "+(0,P.zw)(i.otpEnabled?"Enabled":"Disabled"),1),(0,n.Wm)(l,{value:i.toggleOn,disabled:o.refreshing,onInput:t[0]||(t[0]=e=>i.currentOtpConfig?.otp_secret?.length?i.startOtpDisable():i.startOtpSetup())},null,8,["value","disabled"])]),V,i.currentOtpConfig?.otp_secret?.length?((0,n.wg)(),(0,n.iD)("div",X,[(0,n._)("div",ee,[te,i.hasChanges&&i.temporaryOtpEnabled?((0,n.wg)(),(0,n.iD)("button",{key:0,class:"btn btn-primary",disabled:o.refreshing,onClick:t[1]||(t[1]=(...t)=>e.$refs.confirmModal.open&&e.$refs.confirmModal.open(...t))},[ne,(0,n.Uk)(" Save ")],8,se)):(0,n.kq)("",!0)]),ae,i.currentOtpConfig.qrcode?((0,n.wg)(),(0,n.iD)("div",oe,[(0,n._)("img",{class:"qrcode",src:`data:image/png;base64,${i.currentOtpConfig.qrcode}`,alt:"QR Code"},null,8,ie)])):(0,n.kq)("",!0),i.currentOtpConfig.otp_secret?((0,n.wg)(),(0,n.iD)("div",re,[le,(0,n._)("input",{type:"text",value:i.currentOtpConfig.otp_secret,readonly:"",onFocus:t[2]||(t[2]=t=>e.copyToClipboard(t.target.value))},null,40,de)])):(0,n.kq)("",!0),i.currentOtpConfig.otp_uri?((0,n.wg)(),(0,n.iD)("div",ce,[ue,(0,n._)("input",{type:"text",value:i.currentOtpConfig.otp_uri,readonly:"",onFocus:t[3]||(t[3]=t=>e.copyToClipboard(t.target.value))},null,40,pe)])):(0,n.kq)("",!0),i.otpEnabled?((0,n.wg)(),(0,n.iD)("div",he,[(0,n._)("div",fe,[ge,(0,n._)("button",{class:"btn btn-primary",disabled:o.refreshing,onClick:t[4]||(t[4]=(...t)=>e.$refs.confirmRefreshCodes.open&&e.$refs.confirmRefreshCodes.open(...t))},[we,(0,n.Uk)(" Regenerate ")],8,me)]),o.backupCodes?.length?((0,n.wg)(),(0,n.iD)("div",be,ke)):(0,n.kq)("",!0),o.backupCodes?.length?((0,n.wg)(),(0,n.iD)("textarea",{key:1,value:o.backupCodes.join("\n"),readonly:"",onFocus:t[5]||(t[5]=t=>e.copyToClipboard(t.target.value))},null,40,ve)):(0,n.kq)("",!0)])):(0,n.kq)("",!0)])):(0,n.kq)("",!0)])),o.refreshing?(0,n.kq)("",!0):((0,n.wg)(),(0,n.j4)(d,{key:2,ref:"confirmRefreshCodes",onInput:i.refreshCodes},{default:(0,n.w5)((()=>[(0,n.Uk)(" Are you sure you want to regenerate the backup codes? ")])),_:1},8,["onInput"])),(0,n.Wm)(c,{title:"Confirm 2FA Setup",ref:"confirmModal",onOpen:i.onConfirmModalOpen},{default:(0,n.w5)((()=>[(0,n._)("div",Oe,[i.temporaryOtpEnabled?((0,n.wg)(),(0,n.iD)("div",Ue,Ae)):((0,n.wg)(),(0,n.iD)("div",xe,Ze)),(0,n._)("form",{disabled:o.refreshing,onSubmit:t[7]||(t[7]=(0,N.iM)((e=>i.otpEnabled?i.disableOtp():i.enableOtp()),["prevent"]))},[(0,n._)("input",{type:"password",placeholder:"Password",required:"",disabled:o.refreshing,ref:"password"},null,8,Ie),i.temporaryOtpEnabled?((0,n.wg)(),(0,n.iD)("input",{key:0,type:"text",placeholder:"Authenticator Code",required:"",disabled:o.refreshing,ref:"code"},null,8,Se)):(0,n.kq)("",!0),(0,n._)("div",Fe,[(0,n._)("button",{class:"btn btn-primary",disabled:o.refreshing,type:"submit"},[We,(0,n.Uk)(" Confirm "),o.refreshing?((0,n.wg)(),(0,n.j4)(r,{key:0})):(0,n.kq)("",!0)],8,Ee),(0,n._)("button",{class:"btn btn-default",onClick:t[6]||(t[6]=(...t)=>e.$refs.confirmModal.close&&e.$refs.confirmModal.close(...t))},[Be,(0,n.Uk)(" Cancel ")])])],40,Re)])])),_:1},8,["onOpen"])])}var Qe=s(7514),ze=s(7066),Le={mixins:[y.Z],components:{ConfirmDialog:b.Z,Loading:Y.Z,Modal:L.Z,ToggleSwitch:Qe.Z},data(){return{backupCodes:[],initializing:!1,otpConfig:null,refreshing:!1,temporaryOtpConfig:null}},computed:{currentOtpConfig(){return this.otpEnabled?this.otpConfig:this.temporaryOtpConfig},hasChanges(){return!this.otpEnabled&&null!=this.temporaryOtpConfig||this.otpEnabled&&(null==this.temporaryOtpConfig||this.temporaryOtpConfig?.otp_secret!=this.otpConfig?.otp_secret)},otpEnabled(){return!!this?.otpConfig?.otp_secret?.length},temporaryOtpDisabled(){return this.hasChanges&&null==this.temporaryOtpConfig?.otp_secret},temporaryOtpEnabled(){return this.hasChanges&&null!=this.temporaryOtpConfig?.otp_secret},toggleOn(){return this.otpEnabled||this.temporaryOtpEnabled}},methods:{getErrorMessage(e){return e.response?.data?.message||e.response?.data?.error||e.message||e.response?.statusText||e.toString()},onError(e){console.error(e),e=this.getErrorMessage(e),this.notify({error:!0,title:"Error while setting up Two-Factor Authentication",text:e,image:{iconClass:"fas fa-exclamation-triangle"}})},async getOtpConfig(){this.initializing=!0;try{this.otpConfig=(await ze.Z.get("/otp/config")).data,this.temporaryOtpConfig=this.otpConfig}catch(e){this.onError(e)}finally{this.initializing=!1}},async startOtpSetup(){this.refreshing=!0;try{this.temporaryOtpConfig=(await ze.Z.post("/otp/config",{dry_run:!0})).data}finally{this.refreshing=!1}},async enableOtp(){this.refreshing=!0;try{const e=await ze.Z.post("/otp/config",{otp_secret:this.temporaryOtpConfig.otp_secret,password:this.$refs.password.value,code:this.$refs.code.value});this.backupCodes=e.data?.backup_codes||[],await this.getOtpConfig(),this.$refs.confirmModal.close(),this.notify({title:"Two-Factor Authentication enabled",text:"Two-Factor Authentication has been enabled for your account",image:{iconClass:"fas fa-shield-alt"}})}catch(e){this.onError(e)}finally{this.refreshing=!1}},async startOtpDisable(){this.temporaryOtpConfig=null,this.$refs.confirmModal.open()},async disableOtp(){this.refreshing=!0;try{await ze.Z.delete("/otp/config",{headers:{"Content-Type":"application/json"},data:{password:this.$refs.password.value}}),await this.getOtpConfig(),this.$refs.confirmModal.close(),this.notify({title:"Two-Factor Authentication disabled",text:"Two-Factor Authentication has been disabled for your account",image:{iconClass:"fas fa-shield-alt"}})}catch(e){this.onError(e)}finally{this.refreshing=!1}},async refreshCodes(){this.refreshing=!0;try{const e=await ze.Z.post("/otp/refresh-codes");this.backupCodes=e.data?.backup_codes||[],this.notify({title:"Backup codes regenerated",text:"Take note of these codes NOW! You will not be able to see them again!",image:{iconClass:"fas fa-shield-alt"}})}catch(e){this.onError(e)}finally{this.refreshing=!1}},onConfirmModalOpen(){this.$nextTick((()=>{this.$refs.password.value="",this.$refs.code&&(this.$refs.code.value=""),this.$refs.password.focus()}))}},async mounted(){await this.getOtpConfig()}};const Ye=(0,C.Z)(Le,[["render",je],["__scopeId","data-v-24d32b46"]]);var Ne=Ye,He=s(7597),Ke=s(3825),Ge={name:"Users",components:{ConfirmDialog:b.Z,Dropdown:z.Z,DropdownItem:He.Z,FloatingButton:Ke.Z,Loading:Y.Z,Modal:L.Z,Otp:Ne},mixins:[y.Z],props:{sessionToken:{type:String,required:!0},currentUser:{type:Object,required:!0}},data(){return{users:[],commandRunning:!1,loading:!1,selectedUser:null,hasOtpPlugin:!1,hasQrcodePlugin:!1,showOtpModal:!1}},computed:{supports2fa(){return this.hasOtpPlugin&&this.hasQrcodePlugin},mfaTitle(){if(this.supports2fa)return"";const e=[];return this.hasOtpPlugin||e.push("otp"),this.hasQrcodePlugin||e.push("qrcode"),"The following plugin(s) are missing: "+e.join(", ")}},methods:{async testOtp(){this.commandRunning=!0,this.hasOtpPlugin=!1,this.hasQrcodePlugin=!1;try{this.hasOtpPlugin=!0;const e=await this.request("otp.generate_secret",{},1e4,!1);if("string"===typeof e&&e.length){const e=await this.request("qrcode.generate",{content:"test"},1e4,!1);e?.data?.length&&(this.hasQrcodePlugin=!0)}}catch(e){this.hasOtpPlugin||console.info("otp plugin not found. Enable/configure it to use 2FA"),this.hasQrcodePlugin||console.info("qrcode plugin not found. Enable/configure it to use 2FA")}finally{this.commandRunning=!1}},async refresh(){this.loading=!0;try{this.users=await this.request("user.get_users")}finally{this.loading=!1}},async createUser(e){e.preventDefault();const t=[...this.$refs.addUserForm.querySelectorAll("input[name]")].reduce(((e,t)=>(e[t.name]=t.value,e)),{});if(t.password===t.confirm_password){this.commandRunning=!0;try{await this.request("user.create_user",{username:t.username,password:t.password,session_token:this.sessionToken})}finally{this.commandRunning=!1}this.notify({text:"User "+t.username+" created",image:{iconClass:"fas fa-check"}}),this.$refs.addUserModal.close(),await this.refresh()}else this.notify({title:"Unable to create user",text:"Please check that the passwords match",error:!0,image:{iconClass:"fas fa-times"}})},async changePassword(e){e.preventDefault();const t=[...this.$refs.changePasswordForm.querySelectorAll("input[name]")].reduce(((e,t)=>(e[t.name]=t.value,e)),{});if(t.new_password!==t.confirm_new_password)return void this.notify({title:"Unable to update password",text:"Please check that the passwords match",error:!0,image:{iconClass:"fas fa-times"}});this.commandRunning=!0;let s=!1;try{s=await this.request("user.update_password",{username:t.username,old_password:t.password,new_password:t.new_password})}finally{this.commandRunning=!1}s?(this.$refs.changePasswordModal.close(),this.notify({text:"Password successfully updated",image:{iconClass:"fas fa-check"}})):this.notify({title:"Unable to update password",text:"The current password is incorrect",error:!0,image:{iconClass:"fas fa-times"}})},async deleteUser(e){this.commandRunning=!0;try{await this.request("user.delete_user",{username:e,session_token:this.sessionToken})}finally{this.commandRunning=!1}this.notify({text:`User ${e} removed`,image:{iconClass:"fas fa-check"}}),this.selectedUser=null,await this.refresh()},showAddUserModal(){this.$refs.addUserModal.show(),this.$nextTick((()=>{this.$refs.addUserForm.reset(),this.$refs.addUserForm.username.focus()}))},showChangePasswordModal(e){this.$refs.changePasswordModal.show(),this.$nextTick((()=>{this.$refs.changePasswordForm.password.focus(),this.selectedUser=e.username}))}},async mounted(){await this.refresh(),await this.testOtp(),this.supports2fa||this.notify({title:"Two-factor Authentication not available",text:this.mfaTitle,error:!0,image:{iconClass:"fas fa-exclamation-triangle"}})}};const Je=(0,C.Z)(Ge,[["render",Q],["__scopeId","data-v-dbc28730"]]);var Ve=Je,Xe={name:"Settings",components:{Application:D,Users:Ve,Tokens:T["default"]},mixins:[y.Z],emits:["change-page"],props:{selectedPanel:{type:String}},data(){return{currentUser:null,sessionToken:null}},methods:{async refresh(){this.sessionToken=this.getCookies()["session_token"],this.currentUser=await this.request("user.get_user_by_session",{session_token:this.sessionToken})},updatePage(){const e=this.getUrlArgs();let t=null;t=e.page?.length?e.page:this.selectedPanel?.length?this.selectedPanel:"users",this.$emit("change-page",t)}},watch:{selectedPanel(e){this.setUrlArgs({page:e})},$route(){this.updatePage()}},async mounted(){this.updatePage(),await this.refresh()}};const et=(0,C.Z)(Xe,[["render",o],["__scopeId","data-v-7c14160a"]]);var tt=et}}]);
//# sourceMappingURL=293.09de0f61.js.map