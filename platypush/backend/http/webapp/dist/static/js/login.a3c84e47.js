"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[6966],{5071:function(e,t,s){s.r(t),s.d(t,{default:function(){return C}});var r=s(641),a=s(33);const i=e=>((0,r.Qi)("data-v-1b764fc6"),e=e(),(0,r.jt)(),e),n={key:1,class:"login-container"},o=i((()=>(0,r.Lk)("div",{class:"header"},[(0,r.Lk)("span",{class:"logo"},[(0,r.Lk)("img",{src:"/logo.svg",alt:"logo"})]),(0,r.Lk)("span",{class:"text"},"Platypush")],-1))),l={class:"row"},d=["type","disabled"],u={class:"row"},c=["type","disabled"],h={key:0,class:"row"},p=["disabled"],k={key:1,class:"row"},g=["disabled"],m={class:"row buttons"},b=["disabled"],f=i((()=>(0,r.Lk)("div",{class:"row pull-right"},[(0,r.Lk)("label",{class:"checkbox"},[(0,r.Lk)("input",{type:"checkbox",name:"remember"}),(0,r.eW)("  Keep me logged in on this device   ")])],-1))),y={key:2,class:"auth-error"};function w(e,t,s,i,w,v){const L=(0,r.g2)("Loading");return w.initialized?((0,r.uX)(),(0,r.CE)("div",n,[w.isAuthenticated?(0,r.Q3)("",!0):((0,r.uX)(),(0,r.CE)("form",{key:0,class:"login",method:"POST",onSubmit:t[0]||(t[0]=(...e)=>v.submitForm&&v.submitForm(...e))},[o,(0,r.Lk)("div",l,[(0,r.Lk)("label",null,[(0,r.Lk)("input",{type:w.requires2fa?"hidden":"text",name:"username",disabled:w.authenticating,placeholder:"Username",ref:"username"},null,8,d)])]),(0,r.Lk)("div",u,[(0,r.Lk)("label",null,[(0,r.Lk)("input",{type:w.requires2fa?"hidden":"password",name:"password",disabled:w.authenticating,placeholder:"Password"},null,8,c)])]),w.requires2fa?((0,r.uX)(),(0,r.CE)("div",h,[(0,r.Lk)("label",null,[(0,r.Lk)("input",{type:"text",name:"code",disabled:w.authenticating,placeholder:"2FA code",ref:"code"},null,8,p)])])):(0,r.Q3)("",!0),s.register?((0,r.uX)(),(0,r.CE)("div",k,[(0,r.Lk)("label",null,[(0,r.Lk)("input",{type:"password",name:"confirm_password",disabled:w.authenticating,placeholder:"Confirm password"},null,8,g)])])):(0,r.Q3)("",!0),(0,r.Lk)("div",m,[(0,r.Lk)("button",{type:"submit",class:(0,a.C4)(["btn btn-primary",{loading:w.authenticating}]),disabled:w.authenticating},[w.authenticating?((0,r.uX)(),(0,r.Wv)(L,{key:0})):(0,r.Q3)("",!0),(0,r.eW)(" "+(0,a.v_)(s.register?"Register":"Login"),1)],10,b)]),f,w.authError?((0,r.uX)(),(0,r.CE)("div",y,(0,a.v_)(w.authError),1)):(0,r.Q3)("",!0)],32))])):((0,r.uX)(),(0,r.Wv)(L,{key:0}))}var v=s(9828),L=s(2002),E=s(4335),A={name:"Login",mixins:[L.A],components:{Loading:v.A},props:{register:{type:Boolean,required:!1,default:!1}},computed:{redirect(){return this.$route.query.redirect?.length?this.$route.query.redirect:"/"}},data(){return{authError:null,authenticating:!1,isAuthenticated:!1,initialized:!1,requires2fa:!1}},methods:{async submitForm(e){e.preventDefault();const t=e.target,s=new FormData(t),r="/auth?type="+(this.register?"register":"login");if(this.register&&s.get("password")!==s.get("confirm_password"))this.authError="Passwords don't match";else{this.authError=null;try{const e=await E.A.post(r,s),t=e?.data?.session_token;if(t){const s=e.expires_at?Date.parse(e.expires_at):null;this.isAuthenticated=!0,this.setCookie("session_token",t,{expires:s}),window.location.href=e.redirect||this.redirect}else this.authError="Invalid credentials"}catch(e){"MISSING_OTP_CODE"===e.response?.data?.error?(this.requires2fa=!0,this.$nextTick((()=>{this.$refs.code?.focus()}))):(this.authError=e.response.data.message||e.response.data.error,401===e.response?.status?this.authError=this.authError||"Invalid credentials":(this.authError=this.authError||"An error occurred while processing the request",e.response?console.error(e.response.status,e.response.data):console.error(e)))}}},async checkAuth(){try{const e=await E.A.get("/auth");e.data.session_token&&(this.isAuthenticated=!0,window.location.href=e.redirect||this.redirect)}catch(e){this.isAuthenticated=!1}finally{this.initialized=!0}}},async created(){await this.checkAuth()},async mounted(){this.$nextTick((()=>{this.$refs.username?.focus()}))}},_=s(6262);const x=(0,_.A)(A,[["render",w],["__scopeId","data-v-1b764fc6"]]);var C=x}}]);
//# sourceMappingURL=login.a3c84e47.js.map