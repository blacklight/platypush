"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[3780],{3780:function(e,l,a){a.r(l),a.d(l,{default:function(){return M}});var s=a(641),t=a(33),n=a(3751);const i={class:"entity alarm-container"},o={class:"icon col-1"},d={class:"label col-5"},u=["textContent"],c={key:0,class:"value"},r={key:1,class:"value"},v={key:2,class:"value"},k={key:3,class:"value next-run"},m=["textContent"],h=["textContent"],b={class:"child enable"},f=["for"],p={class:"value col-6"},g={key:0,class:"child buttons"},L={key:0,class:"label col-6"},C={class:"value"},y={class:"value"},E={key:2,class:"child edit"},w={class:"value col-1 collapse-toggler"},$={class:"alarm-running-modal"},x={class:"title"},D={class:"buttons"},I={class:"label"},R={class:"label"};function S(e,l,a,S,z,_){const A=(0,s.g2)("EntityIcon"),X=(0,s.g2)("ToggleSwitch"),W=(0,s.g2)("AlarmEditor"),N=(0,s.g2)("Modal"),Q=(0,s.g2)("ConfirmDialog");return(0,s.uX)(),(0,s.CE)("div",i,[(0,s.Lk)("div",{class:(0,t.C4)(["head",{collapsed:e.collapsed}])},[(0,s.Lk)("div",o,[(0,s.bF)(A,{entity:e.value,loading:e.loading,error:e.error},null,8,["entity","loading","error"])]),(0,s.Lk)("div",d,[(0,s.Lk)("div",{class:"name",textContent:(0,t.v_)(e.value.name)},null,8,u)]),(0,s.Lk)("div",{class:"value-and-toggler col-8",onClick:l[1]||(l[1]=(0,n.D$)((l=>e.collapsed=!e.collapsed),["stop"]))},[e.value.enabled?_.isRunning?((0,s.uX)(),(0,s.CE)("div",r,"Running")):_.isSnoozed?((0,s.uX)(),(0,s.CE)("div",v,"Snoozed")):_.nextRun?((0,s.uX)(),(0,s.CE)("div",k,[(0,s.Lk)("div",{class:"date",textContent:(0,t.v_)(_.nextRun.toDateString())},null,8,m),(0,s.Lk)("div",{class:"time",textContent:(0,t.v_)(_.nextRun.toLocaleTimeString())},null,8,h)])):(0,s.Q3)("",!0):((0,s.uX)(),(0,s.CE)("div",c,"Disabled")),(0,s.Lk)("div",{class:"collapse-toggler",onClick:l[0]||(l[0]=(0,n.D$)((l=>e.collapsed=!e.collapsed),["stop"]))},[(0,s.Lk)("i",{class:(0,t.C4)(["fas",{"fa-chevron-down":e.collapsed,"fa-chevron-up":!e.collapsed}])},null,2)])])],2),e.collapsed?(0,s.Q3)("",!0):((0,s.uX)(),(0,s.CE)("div",{key:0,class:"body children",onClick:l[6]||(l[6]=(0,n.D$)(((...e)=>_.prevent&&_.prevent(...e)),["stop"]))},[(0,s.Lk)("div",b,[(0,s.Lk)("label",{for:_.enableInputId,class:"label"},[l[9]||(l[9]=(0,s.Lk)("div",{class:"name col-6"},"Enabled",-1)),(0,s.Lk)("div",p,[(0,s.bF)(X,{id:_.enableInputId,value:e.value.enabled,onInput:_.setEnabled},null,8,["id","value","onInput"])])],8,f)]),_.isRunning||_.isSnoozed?((0,s.uX)(),(0,s.CE)("div",g,[_.isRunning?((0,s.uX)(),(0,s.CE)("label",L,[(0,s.Lk)("div",C,[(0,s.Lk)("button",{class:"btn btn-default",onClick:l[2]||(l[2]=(...e)=>_.snooze&&_.snooze(...e))},l[10]||(l[10]=[(0,s.Lk)("i",{class:"fas fa-pause"},null,-1),(0,s.eW)("   Snooze ")]))])])):(0,s.Q3)("",!0),(0,s.Lk)("label",{class:(0,t.C4)(["label",{"col-6":_.isRunning,"col-12":!_.isRunning}])},[(0,s.Lk)("div",y,[(0,s.Lk)("button",{class:"btn btn-default",onClick:l[3]||(l[3]=(...e)=>_.dismiss&&_.dismiss(...e))},l[11]||(l[11]=[(0,s.Lk)("i",{class:"fas fa-times"},null,-1),(0,s.eW)("   Dismiss ")]))])],2)])):(0,s.Q3)("",!0),_.hasEdit?((0,s.uX)(),(0,s.CE)("div",{key:1,class:"child remove",onClick:l[4]||(l[4]=(...l)=>e.$refs.removeDialog.show&&e.$refs.removeDialog.show(...l))},l[12]||(l[12]=[(0,s.Lk)("label",{class:"label"},[(0,s.Lk)("div",{class:"value"},[(0,s.Lk)("i",{class:"fas fa-trash"}),(0,s.eW)("   Remove ")])],-1)]))):(0,s.Q3)("",!0),_.hasEdit?((0,s.uX)(),(0,s.CE)("div",E,[(0,s.Lk)("div",{class:(0,t.C4)(["head",{collapsed:e.editCollapsed}]),onClick:l[5]||(l[5]=(0,n.D$)((l=>e.editCollapsed=!e.editCollapsed),["stop"]))},[l[13]||(l[13]=(0,s.Lk)("div",{class:"label name col-11"},[(0,s.Lk)("i",{class:"fas fa-pen-to-square"}),(0,s.eW)("  Edit ")],-1)),(0,s.Lk)("div",w,[(0,s.Lk)("i",{class:(0,t.C4)(["fas",{"fa-chevron-down":e.editCollapsed,"fa-chevron-up":!e.editCollapsed}])},null,2)])],2),e.editCollapsed?(0,s.Q3)("",!0):((0,s.uX)(),(0,s.Wv)(W,{key:0,value:e.value},null,8,["value"]))])):(0,s.Q3)("",!0)])),(0,s.bF)(N,{title:"Alarm Running",ref:"runningModal",visible:_.isRunning},{default:(0,s.k6)((()=>[(0,s.Lk)("div",$,[l[17]||(l[17]=(0,s.Lk)("div",{class:"icon blink"},[(0,s.Lk)("i",{class:"fas fa-stopwatch"})],-1)),(0,s.Lk)("div",x,[(0,s.Lk)("h3",null,[(0,s.Lk)("b",null,(0,t.v_)(e.value.name),1),l[14]||(l[14]=(0,s.eW)(" is running"))])]),(0,s.Lk)("div",D,[(0,s.Lk)("label",I,[(0,s.Lk)("button",{class:"btn btn-default",onClick:l[7]||(l[7]=(...e)=>_.snooze&&_.snooze(...e))},l[15]||(l[15]=[(0,s.Lk)("i",{class:"fas fa-pause"},null,-1),(0,s.eW)("   Snooze ")]))]),(0,s.Lk)("label",R,[(0,s.Lk)("button",{class:"btn btn-default",onClick:l[8]||(l[8]=(...e)=>_.dismiss&&_.dismiss(...e))},l[16]||(l[16]=[(0,s.Lk)("i",{class:"fas fa-times"},null,-1),(0,s.eW)("   Dismiss ")]))])])])])),_:1},8,["visible"]),(0,s.bF)(Q,{ref:"removeDialog",onInput:_.remove},{default:(0,s.k6)((()=>[l[18]||(l[18]=(0,s.eW)(" Are you sure you want to remove alarm ")),(0,s.Lk)("b",null,(0,t.v_)(e.value.name),1),l[19]||(l[19]=(0,s.eW)("? "))])),_:1},8,["onInput"])])}var z=a(7594),_=a(3538),A=a(4897),X=a(1029),W=a(9513),N=a(11),Q={mixins:[A["default"]],emits:["loading"],components:{AlarmEditor:z["default"],ConfirmDialog:_.A,EntityIcon:X["default"],Modal:W.A,ToggleSwitch:N.A},data:function(){return{collapsed:!0,editCollapsed:!0}},computed:{hasEdit(){return!this.value.static},isCollapsed(){return this.collapsed},isRunning(){return"RUNNING"===this.value.state},isSnoozed(){return"SNOOZED"===this.value.state},nextRun(){return this.value.next_run&&this.value.enabled?new Date(1e3*this.value.next_run):null},enableInputId(){return`alarm-input-${this.value.name}`}},methods:{async setEnabled(){this.$emit("loading",!0);try{await this.request("alarm.set_enabled",{name:this.value.external_id,enabled:!this.value.enabled}),await this.refresh()}finally{this.$emit("loading",!1)}},async snooze(){this.$emit("loading",!0);try{await this.request("alarm.snooze"),await this.refresh()}finally{this.$emit("loading",!1)}},async dismiss(){this.$emit("loading",!0);try{await this.request("alarm.dismiss"),await this.refresh()}finally{this.$emit("loading",!1)}},async refresh(){this.$emit("loading",!0);try{await this.request("alarm.status")}finally{this.$emit("loading",!1)}},async remove(){this.$emit("loading",!0);try{await this.request("alarm.delete",{name:this.value.name})}finally{this.$emit("loading",!1)}},prevent(e){e.stopPropagation()}},mounted(){this.$watch((()=>this.value),((e,l)=>{if(e?.state!==l?.state){const l={image:{icon:"stopwatch"}};switch(e?.state){case"RUNNING":l.text=`Alarm ${e.name} is running`;break;case"SNOOZED":l.text=`Alarm ${e.name} has been snoozed`;break;case"DISMISSED":l.text=`Alarm ${e.name} has been dismissed`;break}l.text&&this.notify(l)}}))}},q=a(6262);const F=(0,q.A)(Q,[["render",S],["__scopeId","data-v-03ac0f14"]]);var M=F}}]);
//# sourceMappingURL=3780.0c7c8fa3.js.map