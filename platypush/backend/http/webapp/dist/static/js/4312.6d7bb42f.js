"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[4312],{4312:function(l,e,a){a.r(e),a.d(e,{default:function(){return $}});var t=a(641),s=a(33),i=a(3751);const n={class:"entity variable-container"},o={class:"icon"},u={class:"label"},d=["textContent"],c=["textContent"],r={class:"row"},v={class:"row"},p={class:"col-9"},h=["disabled"],k={class:"col-3 pull-right"},b=["disabled"],f=["disabled"];function m(l,e,a,m,g,y){const L=(0,t.g2)("EntityIcon");return(0,t.uX)(),(0,t.CE)("div",n,[(0,t.Lk)("div",{class:(0,s.C4)(["head",{collapsed:l.collapsed}])},[(0,t.Lk)("div",o,[(0,t.bF)(L,{entity:l.value,loading:l.loading,error:l.error},null,8,["entity","loading","error"])]),(0,t.Lk)("div",u,[(0,t.Lk)("div",{class:"name",textContent:(0,s.v_)(l.value.name)},null,8,d)]),(0,t.Lk)("div",{class:"value-and-toggler",onClick:e[1]||(e[1]=(0,i.D$)((e=>l.collapsed=!l.collapsed),["stop"]))},[(0,t.Lk)("div",{class:"value",textContent:(0,s.v_)(l.value.value)},null,8,c),(0,t.Lk)("div",{class:"collapse-toggler",onClick:e[0]||(e[0]=(0,i.D$)((e=>l.collapsed=!l.collapsed),["stop"]))},[(0,t.Lk)("i",{class:(0,s.C4)(["fas",{"fa-chevron-down":l.collapsed,"fa-chevron-up":!l.collapsed}])},null,2)])])],2),l.collapsed?(0,t.Q3)("",!0):((0,t.uX)(),(0,t.CE)("div",{key:0,class:"body",onClick:e[5]||(e[5]=(0,i.D$)(((...e)=>l.prevent&&l.prevent(...e)),["stop"]))},[(0,t.Lk)("div",r,[(0,t.Lk)("form",{onSubmit:e[4]||(e[4]=(0,i.D$)(((...l)=>y.setValue&&y.setValue(...l)),["prevent"]))},[(0,t.Lk)("div",v,[(0,t.Lk)("div",p,[(0,t.bo)((0,t.Lk)("input",{type:"text","onUpdate:modelValue":e[2]||(e[2]=e=>l.value_=e),placeholder:"Variable value",disabled:l.loading,ref:"text"},null,8,h),[[i.Jo,l.value_]])]),(0,t.Lk)("div",k,[(0,t.Lk)("button",{type:"button",title:"Clear",onClick:e[3]||(e[3]=(0,i.D$)(((...l)=>y.clearValue&&y.clearValue(...l)),["stop"])),disabled:l.loading},e[6]||(e[6]=[(0,t.Lk)("i",{class:"fas fa-trash"},null,-1)]),8,b),(0,t.Lk)("button",{type:"submit",title:"Edit",disabled:l.loading},e[7]||(e[7]=[(0,t.Lk)("i",{class:"fas fa-check"},null,-1)]),8,f)])])],32)])]))])}var g=a(4897),y=a(1029),L={name:"Variable",components:{EntityIcon:y["default"]},mixins:[g["default"]],emits:["loading"],data:function(){return{collapsed:!0,value_:null}},computed:{isCollapsed(){return this.collapsed}},methods:{async clearValue(){this.$emit("loading",!0);try{await this.request("variable.unset",{name:this.value.name})}finally{this.$emit("loading",!1)}},async setValue(){const l=this.value_;if(!l?.length)return await this.clearValue();this.$emit("loading",!0);try{const e={};e[this.value.name]=l,await this.request("variable.set",e)}finally{this.$emit("loading",!1)}}},mounted(){this.value_=this.value.value,this.$watch((()=>this.value.value),(l=>{this.value_=l}))}},C=a(6262);const V=(0,C.A)(L,[["render",m],["__scopeId","data-v-31c67fb5"]]);var $=V}}]);
//# sourceMappingURL=4312.6d7bb42f.js.map