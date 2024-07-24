"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[685,4535],{8925:function(e,t,r){r.r(t),r.d(t,{default:function(){return q}});var s=r(6252),i=r(3577);const a=e=>((0,s.dD)("data-v-f5e7f974"),e=e(),(0,s.Cn)(),e),n={key:1,class:"login-container"},o=a((()=>(0,s._)("div",{class:"header"},[(0,s._)("span",{class:"logo"},[(0,s._)("img",{src:"/logo.svg",alt:"logo"})]),(0,s._)("span",{class:"text"},"Platypush")],-1))),l={class:"row"},u=["disabled"],d={class:"row"},c=["disabled"],h={key:0,class:"row"},p=["disabled"],g={class:"row buttons"},m=["disabled"],w=a((()=>(0,s._)("div",{class:"row pull-right"},[(0,s._)("label",{class:"checkbox"},[(0,s._)("input",{type:"checkbox",name:"remember"}),(0,s.Uk)("  Keep me logged in on this device   ")])],-1))),f={key:1,class:"auth-error"};function y(e,t,r,a,y,_){const b=(0,s.up)("Loading");return y.initialized?((0,s.wg)(),(0,s.iD)("div",n,[y.isAuthenticated?(0,s.kq)("",!0):((0,s.wg)(),(0,s.iD)("form",{key:0,class:"login",method:"POST",onSubmit:t[0]||(t[0]=(...e)=>_.submitForm&&_.submitForm(...e))},[o,(0,s._)("div",l,[(0,s._)("label",null,[(0,s._)("input",{type:"text",name:"username",disabled:y.authenticating,placeholder:"Username",ref:"username"},null,8,u)])]),(0,s._)("div",d,[(0,s._)("label",null,[(0,s._)("input",{type:"password",name:"password",disabled:y.authenticating,placeholder:"Password"},null,8,c)])]),r.register?((0,s.wg)(),(0,s.iD)("div",h,[(0,s._)("label",null,[(0,s._)("input",{type:"password",name:"confirm_password",disabled:y.authenticating,placeholder:"Confirm password"},null,8,p)])])):(0,s.kq)("",!0),(0,s._)("div",g,[(0,s._)("button",{type:"submit",class:(0,i.C_)(["btn btn-primary",{loading:y.authenticating}]),disabled:y.authenticating},[y.authenticating?((0,s.wg)(),(0,s.j4)(b,{key:0})):(0,s.kq)("",!0),(0,s.Uk)(" "+(0,i.zw)(r.register?"Register":"Login"),1)],10,m)]),w,y.authError?((0,s.wg)(),(0,s.iD)("div",f,(0,i.zw)(y.authError),1)):(0,s.kq)("",!0)],32))])):((0,s.wg)(),(0,s.j4)(b,{key:0}))}var _=r(6791),b=r(8637),k=r(7066),v={name:"Login",mixins:[b.Z],components:{Loading:_.Z},props:{register:{type:Boolean,required:!1,default:!1}},computed:{redirect(){return this.$route.query.redirect?.length?this.$route.query.redirect:"/"}},data(){return{authError:null,authenticating:!1,isAuthenticated:!1,initialized:!1}},methods:{async submitForm(e){e.preventDefault();const t=e.target,r=new FormData(t),s="/auth?type="+(this.register?"register":"login");if(this.register&&r.get("password")!==r.get("confirm_password"))this.authError="Passwords don't match";else{this.authError=null;try{const e=await k.Z.post(s,r),t=e?.data?.session_token;if(t){const r=e.expires_at?Date.parse(e.expires_at):null;this.isAuthenticated=!0,this.setCookie("session_token",t,{expires:r}),window.location.href=e.redirect||this.redirect}else this.authError="Invalid credentials"}catch(e){this.authError=e.response.data.message||e.response.data.error,401===e.response?.status?this.authError=this.authError||"Invalid credentials":(this.authError=this.authError||"An error occurred while processing the request",e.response?console.error(e.response.status,e.response.data):console.error(e))}}},async checkAuth(){try{const e=await k.Z.get("/auth");e.data.session_token&&(this.isAuthenticated=!0,window.location.href=e.redirect||this.redirect)}catch(e){this.isAuthenticated=!1}finally{this.initialized=!0}}},async created(){await this.checkAuth()},async mounted(){this.$nextTick((()=>{this.$refs.username?.focus()}))}},E=r(3744);const x=(0,E.Z)(v,[["render",y],["__scopeId","data-v-f5e7f974"]]);var q=x},9780:function(e,t,r){r.r(t),r.d(t,{default:function(){return u}});var s=r(6252);function i(e,t,r,i,a,n){const o=(0,s.up)("Login");return(0,s.wg)(),(0,s.j4)(o,{register:!0})}var a=r(8925),n={name:"Register",mixins:[a["default"]],components:{Login:a["default"]},props:{register:{type:Boolean,required:!1,default:!0}}},o=r(3744);const l=(0,o.Z)(n,[["render",i]]);var u=l}}]);
//# sourceMappingURL=register.5ed802b7.js.map