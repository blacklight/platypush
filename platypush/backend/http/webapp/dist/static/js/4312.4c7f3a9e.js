"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[4312],{4312:function(l,e,a){a.r(e),a.d(e,{default:function(){return E}});var t=a(641),s=a(33),i=a(3751);const n=l=>((0,t.Qi)("data-v-31c67fb5"),l=l(),(0,t.jt)(),l),o={class:"entity variable-container"},d={class:"icon"},u={class:"label"},c=["textContent"],r=["textContent"],v={class:"row"},p={class:"row"},h={class:"col-9"},k=["disabled"],b={class:"col-3 pull-right"},f=["disabled"],m=n((()=>(0,t.Lk)("i",{class:"fas fa-trash"},null,-1))),g=[m],y=["disabled"],L=n((()=>(0,t.Lk)("i",{class:"fas fa-check"},null,-1))),C=[L];function V(l,e,a,n,m,L){const V=(0,t.g2)("EntityIcon");return(0,t.uX)(),(0,t.CE)("div",o,[(0,t.Lk)("div",{class:(0,s.C4)(["head",{collapsed:l.collapsed}])},[(0,t.Lk)("div",d,[(0,t.bF)(V,{entity:l.value,loading:l.loading,error:l.error},null,8,["entity","loading","error"])]),(0,t.Lk)("div",u,[(0,t.Lk)("div",{class:"name",textContent:(0,s.v_)(l.value.name)},null,8,c)]),(0,t.Lk)("div",{class:"value-and-toggler",onClick:e[1]||(e[1]=(0,i.D$)((e=>l.collapsed=!l.collapsed),["stop"]))},[(0,t.Lk)("div",{class:"value",textContent:(0,s.v_)(l.value.value)},null,8,r),(0,t.Lk)("div",{class:"collapse-toggler",onClick:e[0]||(e[0]=(0,i.D$)((e=>l.collapsed=!l.collapsed),["stop"]))},[(0,t.Lk)("i",{class:(0,s.C4)(["fas",{"fa-chevron-down":l.collapsed,"fa-chevron-up":!l.collapsed}])},null,2)])])],2),l.collapsed?(0,t.Q3)("",!0):((0,t.uX)(),(0,t.CE)("div",{key:0,class:"body",onClick:e[5]||(e[5]=(0,i.D$)(((...e)=>l.prevent&&l.prevent(...e)),["stop"]))},[(0,t.Lk)("div",v,[(0,t.Lk)("form",{onSubmit:e[4]||(e[4]=(0,i.D$)(((...l)=>L.setValue&&L.setValue(...l)),["prevent"]))},[(0,t.Lk)("div",p,[(0,t.Lk)("div",h,[(0,t.bo)((0,t.Lk)("input",{type:"text","onUpdate:modelValue":e[2]||(e[2]=e=>l.value_=e),placeholder:"Variable value",disabled:l.loading,ref:"text"},null,8,k),[[i.Jo,l.value_]])]),(0,t.Lk)("div",b,[(0,t.Lk)("button",{type:"button",title:"Clear",onClick:e[3]||(e[3]=(0,i.D$)(((...l)=>L.clearValue&&L.clearValue(...l)),["stop"])),disabled:l.loading},g,8,f),(0,t.Lk)("button",{type:"submit",title:"Edit",disabled:l.loading},C,8,y)])])],32)])]))])}var $=a(4897),_=a(1029),w={name:"Variable",components:{EntityIcon:_["default"]},mixins:[$["default"]],emits:["loading"],data:function(){return{collapsed:!0,value_:null}},computed:{isCollapsed(){return this.collapsed}},methods:{async clearValue(){this.$emit("loading",!0);try{await this.request("variable.unset",{name:this.value.name})}finally{this.$emit("loading",!1)}},async setValue(){const l=this.value_;if(!l?.length)return await this.clearValue();this.$emit("loading",!0);try{const e={};e[this.value.name]=l,await this.request("variable.set",e)}finally{this.$emit("loading",!1)}}},mounted(){this.value_=this.value.value,this.$watch((()=>this.value.value),(l=>{this.value_=l}))}},x=a(6262);const D=(0,x.A)(w,[["render",V],["__scopeId","data-v-31c67fb5"]]);var E=D}}]);
//# sourceMappingURL=4312.4c7f3a9e.js.map