"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[215],{4642:function(e,t,n){n.d(t,{Z:function(){return y}});var o=n(6252),s=n(9963),a=n(3577);const l={class:"dropdown-container"},i=["title"],r=["textContent"];function d(e,t,n,d,c,u){const p=(0,o.up)("DropdownBody");return(0,o.wg)(),(0,o.iD)("div",l,[(0,o._)("button",{title:n.title,ref:"button",onClick:t[0]||(t[0]=(0,s.iM)((e=>u.toggle(e)),["stop"]))},[n.iconClass?((0,o.wg)(),(0,o.iD)("i",{key:0,class:(0,a.C_)(["icon",n.iconClass])},null,2)):(0,o.kq)("",!0),n.text?((0,o.wg)(),(0,o.iD)("span",{key:1,class:"text",textContent:(0,a.zw)(n.text)},null,8,r)):(0,o.kq)("",!0)],8,i),(0,o._)("div",{class:(0,a.C_)(["body-container",{hidden:!c.visible}]),ref:"dropdownContainer"},[(0,o.Wm)(p,{id:n.id,keepOpenOnItemClick:n.keepOpenOnItemClick,style:(0,a.j5)(n.style),ref:"dropdown",onClick:u.onClick},{default:(0,o.w5)((()=>[(0,o.WI)(e.$slots,"default",{},void 0,!0)])),_:3},8,["id","keepOpenOnItemClick","style","onClick"])],2)])}var c=n(3218),u=n(5250),p={components:{DropdownBody:c.Z},emits:["click"],props:{id:{type:String},iconClass:{default:"fa fa-ellipsis-h"},text:{type:String},title:{type:String},keepOpenOnItemClick:{type:Boolean,default:!1},style:{type:Object,default:()=>({})}},data(){return{visible:!1}},computed:{button(){const e=this.$refs.button?.$el;return e?e.querySelector("button"):this.$refs.button},buttonStyle(){return this.button?getComputedStyle(this.button):{}},buttonWidth(){return parseFloat(this.buttonStyle.width||0)},buttonHeight(){return parseFloat(this.buttonStyle.height||0)}},methods:{documentClickHndl(e){if(!this.visible)return;let t=e.target;while(t){if(t.classList.contains("dropdown"))return;t=t.parentElement}this.close()},getDropdownWidth(){const e=this.$refs.dropdown?.$el;return e?parseFloat(getComputedStyle(e).width):0},getDropdownHeight(){const e=this.$refs.dropdown?.$el;return e?parseFloat(getComputedStyle(e).height):0},onClick(e){return this.keepOpenOnItemClick||this.close(),"A"===e.target.tagName?(e.preventDefault(),!1):e.defaultPrevented?(e.stopPropagation(),!1):void 0},close(){this.visible=!1,document.removeEventListener("click",this.documentClickHndl),u.$.emit("dropdown-close")},open(){document.addEventListener("click",this.documentClickHndl);const e=this.$refs.dropdown?.$el;e.parentElement||this.$el.appendChild(e),this.visible=!0,this.$nextTick(this.adjustDropdownPos)},adjustDropdownPos(){const e=this.button.getBoundingClientRect(),t={left:e.left+window.scrollX,top:e.top+window.scrollY},n={left:t.left,top:t.top+this.buttonHeight},o=this.getDropdownWidth(),s=this.getDropdownHeight();if(n.left+o>(window.innerWidth+window.scrollX)/2&&(n.left-=o-this.buttonWidth),n.top+s>(window.innerHeight+window.scrollY)/2){let e=n.top-(s+this.buttonHeight-10);e<0&&(e=0),n.top=e}const a=this.$refs.dropdown.$el;a.classList.add("fade-in"),a.style.top=`${n.top}px`,a.style.left=`${n.left}px`,u.$.emit("dropdown-open",this.$refs.dropdown)},toggle(e){e?.stopPropagation(),this.$emit("click",e),this.visible?this.close():this.open()},onKeyUp(e){e.stopPropagation(),"Escape"===e.key&&this.close()}},mounted(){document.body.addEventListener("keyup",this.onKeyUp)},unmounted(){document.body.removeEventListener("keyup",this.onKeyUp)}},h=n(3744);const k=(0,h.Z)(p,[["render",d],["__scopeId","data-v-3f1ad726"]]);var y=k},3218:function(e,t,n){n.d(t,{Z:function(){return c}});var o=n(6252),s=n(3577);const a=["id"];function l(e,t,n,l,i,r){return(0,o.wg)(),(0,o.iD)("div",{class:"dropdown",id:n.id,style:(0,s.j5)(n.style),onClick:t[0]||(t[0]=t=>e.$emit("click",t))},[(0,o.WI)(e.$slots,"default",{},void 0,!0)],12,a)}var i={emits:["click"],props:{id:{type:String},keepOpenOnItemClick:{type:Boolean,default:!1},style:{type:Object,default:()=>({})}}},r=n(3744);const d=(0,r.Z)(i,[["render",l],["__scopeId","data-v-24c5aa28"]]);var c=d},7597:function(e,t,n){n.d(t,{Z:function(){return k}});var o=n(6252),s=n(3577);const a=["title"],l={key:0,class:"col-2 icon"},i=["textContent"];function r(e,t,n,r,d,c){const u=(0,o.up)("Icon");return(0,o.wg)(),(0,o.iD)("div",{class:(0,s.C_)(["row item",{...c.itemClass_,disabled:n.disabled}]),title:n.hoverText,onClick:t[0]||(t[0]=(...e)=>c.clicked&&c.clicked(...e))},[n.iconClass?.length||n.iconUrl?.length?((0,o.wg)(),(0,o.iD)("div",l,[(0,o.Wm)(u,{class:(0,s.C_)(n.iconClass),url:n.iconUrl},null,8,["class","url"])])):(0,o.kq)("",!0),(0,o._)("div",{class:(0,s.C_)(["text",{"col-10":null!=n.iconClass}]),textContent:(0,s.zw)(n.text)},null,10,i)],10,a)}var d=n(657),c=n(5250),u={components:{Icon:d.Z},emits:["click","input"],props:{iconClass:{type:String},iconUrl:{type:String},text:{type:String},hoverText:{type:String,default:null},disabled:{type:Boolean,default:!1},itemClass:{}},computed:{itemClass_(){return"string"===typeof this.itemClass?{[this.itemClass]:!0}:this.itemClass}},methods:{clicked(e){if(this.$parent.keepOpenOnItemClick||c.$.emit("dropdown-close"),this.disabled)return e.stopPropagation(),e.preventDefault(),!1;this.$emit("input",e)}}},p=n(3744);const h=(0,p.Z)(u,[["render",r],["__scopeId","data-v-2babe09c"]]);var k=h},657:function(e,t,n){n.d(t,{Z:function(){return u}});var o=n(6252),s=n(3577);const a={class:"icon-container"},l=["src","alt"];function i(e,t,n,i,r,d){return(0,o.wg)(),(0,o.iD)("div",a,[n.url?.length?((0,o.wg)(),(0,o.iD)("img",{key:0,class:"icon",src:n.url,alt:n.alt},null,8,l)):d.className?.length?((0,o.wg)(),(0,o.iD)("i",{key:1,class:(0,s.C_)(["icon",d.className]),style:(0,s.j5)({color:n.color})},null,6)):(0,o.kq)("",!0)])}var r={props:{class:{type:String},url:{type:String},color:{type:String,default:""},alt:{type:String,default:""}},computed:{className(){return this.class}}},d=n(3744);const c=(0,d.Z)(r,[["render",i],["__scopeId","data-v-706a3bd1"]]);var u=c},3222:function(e,t,n){n.d(t,{Z:function(){return c}});var o=n(6252),s=n(3577);const a={class:"no-items-container"};function l(e,t,n,l,i,r){return(0,o.wg)(),(0,o.iD)("div",a,[(0,o._)("div",{class:(0,s.C_)(["no-items fade-in",{shadow:n.withShadow}])},[(0,o.WI)(e.$slots,"default",{},void 0,!0)],2)])}var i={name:"NoItems",props:{withShadow:{type:Boolean,default:!0}}},r=n(3744);const d=(0,r.Z)(i,[["render",l],["__scopeId","data-v-4856c4d7"]]);var c=d},8735:function(e,t,n){n.d(t,{Z:function(){return u}});var o=n(6252),s=n(3577);const a={key:0,class:"icon"};function l(e,t,n,l,i,r){const d=(0,o.up)("Icon");return(0,o.wg)(),(0,o.iD)("div",{class:(0,s.C_)(["tab",n.selected?"selected":""]),onClick:t[0]||(t[0]=t=>e.$emit("input"))},[n.iconClass?.length||n.iconUrl?.length?((0,o.wg)(),(0,o.iD)("span",a,[(0,o.Wm)(d,{class:(0,s.C_)(n.iconClass),url:n.iconUrl},null,8,["class","url"])])):(0,o.kq)("",!0),(0,o.Uk)("   "),(0,o.WI)(e.$slots,"default",{},void 0,!0)],2)}var i=n(657),r={name:"Tab",components:{Icon:i.Z},emits:["input"],props:{selected:{type:Boolean,default:!1},iconClass:{type:String},iconUrl:{type:String}}},d=n(3744);const c=(0,d.Z)(r,[["render",l],["__scopeId","data-v-f3217d34"]]);var u=c},3176:function(e,t,n){n.d(t,{Z:function(){return d}});var o=n(6252);const s={class:"tabs"};function a(e,t,n,a,l,i){return(0,o.wg)(),(0,o.iD)("div",s,[(0,o.WI)(e.$slots,"default",{},void 0,!0)])}var l={name:"Tabs"},i=n(3744);const r=(0,i.Z)(l,[["render",a],["__scopeId","data-v-f4300bb0"]]);var d=r},215:function(e,t,n){n.r(t),n.d(t,{default:function(){return Me}});var o=n(6252);const s={class:"tokens-container"},a={key:1,class:"main"},l={class:"header"},i={class:"tabs-container"},r={class:"body"};function d(e,t,n,d,c,u){const p=(0,o.up)("Loading"),h=(0,o.up)("Tab"),k=(0,o.up)("Tabs"),y=(0,o.up)("JwtToken"),g=(0,o.up)("ApiToken");return(0,o.wg)(),(0,o.iD)("div",s,[c.loading?((0,o.wg)(),(0,o.j4)(p,{key:0})):((0,o.wg)(),(0,o.iD)("div",a,[(0,o._)("div",l,[(0,o._)("div",i,[(0,o.Wm)(k,null,{default:(0,o.w5)((()=>[(0,o.Wm)(h,{selected:"api"===c.tokenType,onInput:t[0]||(t[0]=e=>c.tokenType="api")},{default:(0,o.w5)((()=>[(0,o.Uk)(" API Tokens ")])),_:1},8,["selected"]),(0,o.Wm)(h,{selected:"jwt"===c.tokenType,onInput:t[1]||(t[1]=e=>c.tokenType="jwt")},{default:(0,o.w5)((()=>[(0,o.Uk)(" JWT Tokens ")])),_:1},8,["selected"])])),_:1})])]),(0,o._)("div",r,["jwt"===c.tokenType?((0,o.wg)(),(0,o.j4)(y,{key:0,"current-user":n.currentUser},null,8,["current-user"])):((0,o.wg)(),(0,o.j4)(g,{key:1,"current-user":n.currentUser},null,8,["current-user"]))])]))])}var c=n(3577),u=n(9963);const p={class:"token-container"},h={class:"token-container"},k=(0,o._)("label",null,[(0,o.Uk)(" This is your generated token. Treat it carefully and do not share it with untrusted parties."),(0,o._)("br"),(0,o.Uk)(" Also, make sure to save it - it WILL NOT be displayed again. ")],-1),y=["textContent"],g={class:"form-container"},m=(0,o._)("p",null,"Confirm your credentials in order to generate a new API token.",-1),f=(0,o._)("span",null,"Confirm password",-1),w={type:"password",name:"password",ref:"password",placeholder:"Password"},_=(0,o._)("label",null,[(0,o._)("span",null,[(0,o.Uk)(" A friendly name used to identify this token - such as "),(0,o._)("code",null,"My App"),(0,o.Uk)(" or "),(0,o._)("code",null,"My Site"),(0,o.Uk)(". ")]),(0,o._)("span",null,[(0,o._)("input",{type:"text",name:"name",placeholder:"Token name"})])],-1),v=(0,o._)("label",null,[(0,o._)("span",null,"Token validity in days"),(0,o._)("span",null,[(0,o._)("input",{type:"text",name:"validityDays",placeholder:"Validity in days"})])],-1),b=(0,o._)("span",{class:"note"},[(0,o.Uk)(" Decimal values are also supported - e.g. "),(0,o._)("i",null,"0.5"),(0,o.Uk)(" means half a day (12 hours). An empty or zero value means that the token has no expiry date. ")],-1),T=(0,o._)("label",null,[(0,o._)("input",{type:"submit",class:"btn btn-primary",value:"Generate API Token"})],-1),C={class:"body"},D={class:"buttons"},I=(0,o._)("p",null,[(0,o._)("b",null,"API tokens"),(0,o.Uk)(" are randomly generated tokens that are stored encrypted on the server, and can be used to authenticate with the Platypush API. ")],-1),x=(0,o._)("a",{href:"/#settings?page=tokens&type=jwt"},"JWT tokens",-1),U=(0,o._)("ul",null,[(0,o._)("li",null,"They can be revoked at any time by the user who generated them, while JWT tokens can only be revoked by changing the user's password."),(0,o._)("li",null,"Their payload is random and not generated from the user's password, so even if an attacker gains access to the server's encryption keys, they cannot impersonate the user."),(0,o._)("li",null,"They can be generated with a friendly name that can be used to identify the token.")],-1);function $(e,t,n,s,a,l){const i=(0,o.up)("Loading"),r=(0,o.up)("Modal"),d=(0,o.up)("TokensList"),$=(0,o.up)("Description");return(0,o.wg)(),(0,o.iD)("div",p,[a.loading?((0,o.wg)(),(0,o.j4)(i,{key:0})):(0,o.kq)("",!0),(0,o.Wm)(r,{ref:"tokenModal"},{default:(0,o.w5)((()=>[(0,o._)("div",h,[k,(0,o._)("textarea",{class:"token",textContent:(0,c.zw)(a.token),onFocus:t[0]||(t[0]=t=>e.copyToClipboard(t.target.value))},null,40,y)])])),_:1},512),(0,o.Wm)(r,{title:"Generate an API token",ref:"tokenParamsModal",onOpen:t[2]||(t[2]=t=>e.$nextTick((()=>e.$refs.password.focus()))),onClose:t[3]||(t[3]=t=>e.$refs.generateTokenForm.reset())},{default:(0,o.w5)((()=>[(0,o._)("div",g,[m,(0,o._)("form",{onSubmit:t[1]||(t[1]=(0,u.iM)(((...e)=>l.generateToken&&l.generateToken(...e)),["prevent"])),ref:"generateTokenForm"},[(0,o._)("label",null,[f,(0,o._)("span",null,[(0,o._)("input",w,null,512)])]),_,v,b,T],544)])])),_:1},512),(0,o.Wm)(r,{title:"API Tokens",ref:"tokensModal",onClose:t[4]||(t[4]=e=>a.showTokens=!1)},{default:(0,o.w5)((()=>[a.showTokens?((0,o.wg)(),(0,o.j4)(d,{key:0})):(0,o.kq)("",!0)])),_:1},512),(0,o._)("div",C,[(0,o._)("div",D,[(0,o._)("label",null,[(0,o._)("button",{class:"btn btn-primary",onClick:t[5]||(t[5]=t=>e.$refs.tokenParamsModal.show())}," Generate API Token ")]),(0,o._)("label",null,[(0,o._)("button",{class:"btn btn-default",onClick:t[6]||(t[6]=e=>a.showTokens=!0)}," Manage Tokens ")])]),I,(0,o._)("p",null,[(0,o.Uk)(" When compared to the "),x,(0,o.Uk)(", API tokens have the following advantages: "),U,(0,o.Wm)($)])])])}var W=n(7066);const Z=(0,o._)("code",null,"/execute",-1),S=(0,o._)("br",null,null,-1),A=(0,o._)("br",null,null,-1),P=(0,o.uE)("<ul><li> Specify it on the <code>Authorization: Bearer &lt;token&gt;</code> header (replace <code>&lt;token&gt;</code> with your token). </li><li> Specify it on the <code>X-Token &lt;token&gt;</code> header (replace <code>&lt;token&gt;</code> with your token). </li><li> Specify it as a URL parameter: <code>http://site:8008/execute?token=...</code>. </li><li> Specify it on the body of your JSON request: <code>{&quot;type&quot;:&quot;request&quot;, &quot;action&quot;, &quot;...&quot;, &quot;token&quot;:&quot;...&quot;}</code>. </li></ul>",1);function q(e,t){return(0,o.wg)(),(0,o.iD)("p",null,[(0,o.Uk)(" You can use your token to authenticate calls to the "),Z,(0,o.Uk)(" endpoint or the Websocket routes."),S,A,(0,o.Uk)(" You can include the token in your requests in any of the following ways: "),P])}var O=n(3744);const j={},L=(0,O.Z)(j,[["render",q]]);var M=L,J=n(6791),F=n(8637),N=n(2918);const H={class:"tokens-list-container"},z=(0,o._)("p",null,"Are you sure you want to delete this token?",-1),B=(0,o._)("b",null," Any application that uses this token will no longer be able to authenticate with the Platypush API. This action cannot be undone. ",-1),E=(0,o._)("p",null,"No tokens have been generated yet.",-1),G={key:2,class:"main"},Y={class:"tokens-list"},K={class:"info"},X={class:"name"},R={class:"created-at"},V={class:"expires-at"},Q={class:"actions"};function ee(e,t,n,s,a,l){const i=(0,o.up)("ConfirmDialog"),r=(0,o.up)("Loading"),d=(0,o.up)("NoItems"),u=(0,o.up)("DropdownItem"),p=(0,o.up)("Dropdown");return(0,o.wg)(),(0,o.iD)("div",H,[(0,o.Wm)(i,{ref:"tokenDeleteConfirm",onInput:l.deleteToken,onClose:t[0]||(t[0]=e=>a.tokenToDelete=null)},{default:(0,o.w5)((()=>[z,B])),_:1},8,["onInput"]),a.loading?((0,o.wg)(),(0,o.j4)(r,{key:0})):l.tokens?.length?((0,o.wg)(),(0,o.iD)("div",G,[(0,o._)("div",Y,[((0,o.wg)(!0),(0,o.iD)(o.HY,null,(0,o.Ko)(l.tokens,(e=>((0,o.wg)(),(0,o.iD)("div",{class:"token",key:e.id},[(0,o._)("div",K,[(0,o._)("div",X,[(0,o._)("b",null,(0,c.zw)(e.name),1)]),(0,o._)("div",R,[(0,o.Uk)(" Created at: "),(0,o._)("b",null,(0,c.zw)(e.created_at),1)]),(0,o._)("div",V,[(0,o.Uk)(" Expires at: "),(0,o._)("b",null,(0,c.zw)(e.expires_at),1)])]),(0,o._)("div",Q,[(0,o.Wm)(p,{title:"Actions","icon-class":"fa fa-ellipsis-h"},{default:(0,o.w5)((()=>[(0,o.Wm)(u,{text:"Delete","icon-class":"fa fa-trash",onInput:t=>a.tokenToDelete=e},null,8,["onInput"])])),_:2},1024)])])))),128))])])):((0,o.wg)(),(0,o.j4)(d,{key:1,"with-shadow":!1},{default:(0,o.w5)((()=>[E])),_:1}))])}var te=n(3513),ne=n(4642),oe=n(7597),se=n(3222),ae={name:"Token",mixins:[F.Z],components:{ConfirmDialog:te.Z,Dropdown:ne.Z,DropdownItem:oe.Z,Loading:J.Z,NoItems:se.Z},data(){return{loading:!1,tokens_:[],tokenToDelete:null}},computed:{tokens(){return this.tokens_.map((e=>({...e,created_at:e.created_at?this.formatDateTime(e.created_at,!1,!1):"N/A",expires_at:e.expires_at?this.formatDateTime(e.expires_at,!1,!1):"never"})))}},methods:{async refresh(){this.loading=!0;try{this.tokens_=(await W.Z.get("/tokens")).data?.tokens}catch(e){console.error(e.toString()),this.notify({text:e.response?.data?.message||e.response?.data?.error||e.toString(),error:!0})}finally{this.loading=!1}},async deleteToken(){if(this.tokenToDelete){this.loading=!0;try{await W.Z.delete("/tokens",{data:{token_id:this.tokenToDelete.id}}),await this.refresh()}catch(e){console.error(e.toString()),this.notify({text:e.response?.data?.message||e.response?.data?.error||e.toString(),error:!0})}finally{this.loading=!1}}}},watch:{$route(){this.refresh()},tokenToDelete(e){e?this.$refs.tokenDeleteConfirm.open():this.$refs.tokenDeleteConfirm.close()}},mounted(){this.refresh()}};const le=(0,O.Z)(ae,[["render",ee]]);var ie=le,re={name:"Token",mixins:[F.Z],components:{Description:M,Loading:J.Z,Modal:N.Z,TokensList:ie},props:{currentUser:{type:Object,required:!0}},data(){return{loading:!1,showTokens:!1,token:null}},methods:{async generateToken(e){const t=this.currentUser.username,n=e.target.password.value,o=e.target.name.value;let s=e.target.validityDays?.length?parseInt(e.target.validityDays.value):0;s||(s=null),this.loading=!0;try{this.token=(await W.Z.post("/auth?type=token",{username:t,password:n,name:o,expiry_days:s})).data.token,this.token?.length&&this.$refs.tokenModal.show()}catch(a){console.error(a.toString()),this.notify({text:a.toString(),error:!0})}finally{this.loading=!1}}},watch:{showTokens(e){e?this.$refs.tokensModal.show():this.$refs.tokensModal.close()}}};const de=(0,O.Z)(re,[["render",$]]);var ce=de;const ue={class:"token-container"},pe={class:"token-container"},he=(0,o._)("label",null,[(0,o.Uk)(" This is your generated token. Treat it carefully and do not share it with untrusted parties."),(0,o._)("br"),(0,o.Uk)(" Also, make sure to save it - it WILL NOT be displayed again. ")],-1),ke=["textContent"],ye={class:"form-container"},ge=(0,o._)("p",null,"Confirm your credentials in order to generate a new JWT token.",-1),me=(0,o._)("span",null,"Confirm password",-1),fe={type:"password",name:"password",ref:"password",placeholder:"Password"},we=(0,o._)("label",null,[(0,o._)("span",null,"Token validity in days"),(0,o._)("span",null,[(0,o._)("input",{type:"text",name:"validityDays",placeholder:"Validity in days"})])],-1),_e=(0,o._)("span",{class:"note"},[(0,o.Uk)(" Decimal values are also supported - e.g. "),(0,o._)("i",null,"0.5"),(0,o.Uk)(" means half a day (12 hours). An empty or zero value means that the token has no expiry date. ")],-1),ve=(0,o._)("label",null,[(0,o._)("input",{type:"submit",class:"btn btn-primary",value:"Generate JWT Token"})],-1),be={class:"body"},Te={class:"generate-btn-container"},Ce=(0,o._)("p",null,[(0,o._)("b",null,"JWT tokens"),(0,o.Uk)(" are bearer-only, and they contain encrypted authentication information. ")],-1),De=(0,o._)("p",null," They can be used as permanent or time-based tokens to authenticate with the Platypush API. ",-1),Ie=(0,o._)("a",{href:"/#settings?page=tokens&type=api"},"API tokens",-1),xe=(0,o._)("ul",null,[(0,o._)("li",null,"They are not stored on the server, so compromising the server does not necessarily compromise the tokens too.")],-1),Ue=(0,o._)("ul",null,[(0,o._)("li",null,"They are not revocable - once generated, they can be used indefinitely until they expire."),(0,o._)("li",null,"The only way to revoke a JWT token is to change the user's password. However, if a user changes their password, all the JWT tokens generated with the old password will be invalidated."),(0,o._)("li",null,"Their payload is the encrypted representation of the user's credentials, but without any OTP information, so an attacker gains access to the user's credentials and the server's encryption keys they can impersonate the user indefinitely bypassing 2FA.")],-1),$e=(0,o._)("br",null,null,-1),We=(0,o._)("br",null,null,-1);function Ze(e,t,n,s,a,l){const i=(0,o.up)("Loading"),r=(0,o.up)("Modal"),d=(0,o.up)("Description");return(0,o.wg)(),(0,o.iD)("div",ue,[a.loading?((0,o.wg)(),(0,o.j4)(i,{key:0})):(0,o.kq)("",!0),(0,o.Wm)(r,{ref:"tokenModal"},{default:(0,o.w5)((()=>[(0,o._)("div",pe,[he,(0,o._)("textarea",{class:"token",textContent:(0,c.zw)(a.token),onFocus:t[0]||(t[0]=t=>e.copyToClipboard(t.target.value))},null,40,ke)])])),_:1},512),(0,o.Wm)(r,{title:"Generate a JWT token",ref:"tokenParamsModal",onOpen:t[2]||(t[2]=t=>e.$nextTick((()=>e.$refs.password.focus()))),onClose:t[3]||(t[3]=t=>e.$refs.generateTokenForm.reset())},{default:(0,o.w5)((()=>[(0,o._)("div",ye,[ge,(0,o._)("form",{onSubmit:t[1]||(t[1]=(0,u.iM)(((...e)=>l.generateToken&&l.generateToken(...e)),["prevent"])),ref:"generateTokenForm"},[(0,o._)("label",null,[me,(0,o._)("span",null,[(0,o._)("input",fe,null,512)])]),we,_e,ve],544)])])),_:1},512),(0,o._)("div",be,[(0,o._)("label",Te,[(0,o._)("button",{class:"btn btn-primary",onClick:t[4]||(t[4]=t=>e.$refs.tokenParamsModal.show())}," Generate JWT Token ")]),Ce,De,(0,o._)("p",null,[(0,o.Uk)(" When compared to the standard "),Ie,(0,o.Uk)(", JWT tokens have the following pros: "),xe,(0,o.Uk)(" And the following cons: "),Ue,(0,o.Uk)(" For these reasons, it is recommended to use generic API tokens over JWT tokens for most use cases."),$e,We,(0,o.Wm)(d)])])])}var Se={name:"Token",components:{Description:M,Loading:J.Z,Modal:N.Z},mixins:[F.Z],props:{currentUser:{type:Object,required:!0}},data(){return{loading:!1,token:null}},methods:{async generateToken(e){const t=this.currentUser.username,n=e.target.password.value;let o=e.target.validityDays?.length?parseInt(e.target.validityDays.value):0;o||(o=null),this.loading=!0;try{this.token=(await W.Z.post("/auth?type=jwt",{username:t,password:n,expiry_days:o})).data.token,this.token?.length&&this.$refs.tokenModal.show()}catch(s){console.error(s.toString()),this.notify({text:s.toString(),error:!0})}finally{this.loading=!1}}}};const Ae=(0,O.Z)(Se,[["render",Ze]]);var Pe=Ae,qe=n(8735),Oe=n(3176),je={mixins:[F.Z],components:{ApiToken:ce,JwtToken:Pe,Loading:J.Z,Tab:qe.Z,Tabs:Oe.Z},props:{currentUser:{type:Object,required:!0}},data(){return{loading:!1,token:null,tokenType:null}},methods:{refresh(){const e=this.getUrlArgs();this.$nextTick((()=>{this.tokenType=e.type?.length?e.type:"api"}))}},watch:{tokenType(e){this.setUrlArgs({type:e})},$route(){this.refresh()}},mounted(){this.refresh()},unmounted(){this.setUrlArgs({type:null})}};const Le=(0,O.Z)(je,[["render",d],["__scopeId","data-v-8b92029c"]]);var Me=Le}}]);
//# sourceMappingURL=215.57c634fb.js.map