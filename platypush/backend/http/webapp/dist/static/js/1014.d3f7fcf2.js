"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[1014],{1014:function(e,n,t){t.r(n),t.d(n,{default:function(){return E}});var s=t(641),i=t(33);const l={class:"media-youtube-channel"},a={key:1,class:"channel"},r={class:"header"},c={class:"banner"},o=["src"],u={class:"row info-container"},d={class:"info"},h={class:"row"},b={class:"title-container"},g=["href"],p={class:"image"},y=["src"],m=["href"],f={class:"actions"},k=["title"],v={key:0,class:"subscribers"},w={key:0,class:"description"};function _(e,n,t,_,C,L){const x=(0,s.g2)("Loading"),S=(0,s.g2)("Results");return(0,s.uX)(),(0,s.CE)("div",l,[L.isLoading?((0,s.uX)(),(0,s.Wv)(x,{key:0})):C.channel?((0,s.uX)(),(0,s.CE)("div",a,[(0,s.Lk)("div",r,[(0,s.Lk)("div",c,[C.channel?.banner?.length?((0,s.uX)(),(0,s.CE)("img",{key:0,src:C.channel.banner},null,8,o)):(0,s.Q3)("",!0)]),(0,s.Lk)("div",u,[(0,s.Lk)("div",d,[(0,s.Lk)("div",h,[(0,s.Lk)("div",b,[C.channel?.image?.length?((0,s.uX)(),(0,s.CE)("a",{key:0,href:C.channel.url,target:"_blank",rel:"noopener noreferrer"},[(0,s.Lk)("div",p,[(0,s.Lk)("img",{src:C.channel.image},null,8,y)])],8,g)):(0,s.Q3)("",!0),(0,s.Lk)("a",{class:"title",href:C.channel.url,target:"_blank",rel:"noopener noreferrer"},(0,i.v_)(C.channel?.name),9,m)]),(0,s.Lk)("div",f,[(0,s.Lk)("button",{title:C.subscribed?"Unsubscribe":"Subscribe",onClick:n[0]||(n[0]=(...e)=>L.toggleSubscription&&L.toggleSubscription(...e))},(0,i.v_)(C.subscribed?"Unsubscribe":"Subscribe"),9,k),null!=C.channel.subscribers&&(C.channel.subscribers||0)>=0?((0,s.uX)(),(0,s.CE)("div",v,(0,i.v_)(e.formatNumber(C.channel.subscribers))+" subscribers ",1)):(0,s.Q3)("",!0)])]),C.channel?.description?((0,s.uX)(),(0,s.CE)("div",w,(0,i.v_)(C.channel.description),1)):(0,s.Q3)("",!0)])])]),(0,s.bF)(S,{results:C.channel.items,filter:t.filter,"result-index-step":null,"selected-result":C.selectedResult,ref:"results",onAddToPlaylist:n[1]||(n[1]=n=>e.$emit("add-to-playlist",n)),onDownload:n[2]||(n[2]=n=>e.$emit("download",n)),onDownloadAudio:n[3]||(n[3]=n=>e.$emit("download-audio",n)),onOpenChannel:n[4]||(n[4]=n=>e.$emit("open-channel",n)),onPlay:n[5]||(n[5]=n=>e.$emit("play",n)),onPlayWithOpts:n[6]||(n[6]=n=>e.$emit("play-with-opts",n)),onScrollEnd:L.loadNextPage,onSelect:n[7]||(n[7]=e=>C.selectedResult=e),onView:n[8]||(n[8]=n=>e.$emit("view",n))},null,8,["results","filter","selected-result","onScrollEnd"])])):(0,s.Q3)("",!0)])}var C=t(9828),L=t(3149),x=t(2002),S={mixins:[x.A],emits:["add-to-playlist","download","download-audio","open-channel","play","play-with-opts","view"],components:{Loading:C.A,Results:L.A},props:{id:{type:String,required:!0},filter:{type:String,default:null},loading:{type:Boolean,default:!1}},data(){return{channel:null,loading_:!1,loadingNextPage:!1,selectedResult:null,subscribed:!1}},computed:{isLoading(){return this.loading||this.loading_},itemsByUrl(){return this.channel?.items.reduce(((e,n)=>(e[n.url]=n,e)),{})}},methods:{async loadChannel(){this.loading_=!0;try{await this.updateChannel(!0),this.subscribed=await this.request("youtube.is_subscribed",{channel_id:this.id})}finally{this.loading_=!1}},async updateChannel(e){const n=await this.request("youtube.get_channel",{id:this.id,next_page_token:this.channel?.next_page_token}),t=this.itemsByUrl||{};let s=n.items.filter((e=>!t[e.url])).map((e=>({type:"youtube",...e})));e||(s=this.channel.items.concat(s)),this.channel=n,this.channel.items=s},async loadNextPage(){if(this.channel?.next_page_token&&!this.loadingNextPage){this.loadingNextPage=!0;try{await this.timeout(500),await this.updateChannel()}finally{this.loadingNextPage=!1}}},async toggleSubscription(){const e=this.subscribed?"unsubscribe":"subscribe";await this.request(`youtube.${e}`,{channel_id:this.id}),this.subscribed=!this.subscribed}},async mounted(){this.setUrlArgs({channel:this.id}),await this.loadChannel()},unmounted(){this.setUrlArgs({channel:null})}},P=t(6262);const A=(0,P.A)(S,[["render",_],["__scopeId","data-v-448cf852"]]);var E=A}}]);
//# sourceMappingURL=1014.d3f7fcf2.js.map