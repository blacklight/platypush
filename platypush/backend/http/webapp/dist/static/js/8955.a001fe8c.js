"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[8955],{8955:function(e,n,t){t.r(n),t.d(n,{default:function(){return N}});var s=t(6252),i=t(3577);const l={class:"media-youtube-channel"},a={key:1,class:"channel"},r={class:"header"},c={class:"banner"},o=["src"],d={class:"row info-container"},u={class:"info"},h={class:"row"},b={class:"title-container"},g=["href"],p={class:"image"},y=["src"],m=["href"],w={class:"actions"},_=["title"],f={key:0,class:"subscribers"},k={key:0,class:"description"};function v(e,n,t,v,x,S){const q=(0,s.up)("Loading"),C=(0,s.up)("Results");return(0,s.wg)(),(0,s.iD)("div",l,[S.isLoading?((0,s.wg)(),(0,s.j4)(q,{key:0})):x.channel?((0,s.wg)(),(0,s.iD)("div",a,[(0,s._)("div",r,[(0,s._)("div",c,[x.channel?.banner?.length?((0,s.wg)(),(0,s.iD)("img",{key:0,src:x.channel.banner},null,8,o)):(0,s.kq)("",!0)]),(0,s._)("div",d,[(0,s._)("div",u,[(0,s._)("div",h,[(0,s._)("div",b,[x.channel?.image?.length?((0,s.wg)(),(0,s.iD)("a",{key:0,href:x.channel.url,target:"_blank",rel:"noopener noreferrer"},[(0,s._)("div",p,[(0,s._)("img",{src:x.channel.image},null,8,y)])],8,g)):(0,s.kq)("",!0),(0,s._)("a",{class:"title",href:x.channel.url,target:"_blank",rel:"noopener noreferrer"},(0,i.zw)(x.channel?.name),9,m)]),(0,s._)("div",w,[(0,s._)("button",{title:x.subscribed?"Unsubscribe":"Subscribe",onClick:n[0]||(n[0]=(...e)=>S.toggleSubscription&&S.toggleSubscription(...e))},(0,i.zw)(x.subscribed?"Unsubscribe":"Subscribe"),9,_),null!=x.channel.subscribers&&(x.channel.subscribers||0)>=0?((0,s.wg)(),(0,s.iD)("div",f,(0,i.zw)(e.formatNumber(x.channel.subscribers))+" subscribers ",1)):(0,s.kq)("",!0)])]),x.channel?.description?((0,s.wg)(),(0,s.iD)("div",k,(0,i.zw)(x.channel.description),1)):(0,s.kq)("",!0)])])]),(0,s.Wm)(C,{results:x.channel.items,filter:t.filter,"result-index-step":null,"selected-result":x.selectedResult,ref:"results",onAddToPlaylist:n[1]||(n[1]=n=>e.$emit("add-to-playlist",n)),onDownload:n[2]||(n[2]=n=>e.$emit("download",n)),onDownloadAudio:n[3]||(n[3]=n=>e.$emit("download-audio",n)),onOpenChannel:n[4]||(n[4]=n=>e.$emit("open-channel",n)),onPlay:n[5]||(n[5]=n=>e.$emit("play",n)),onPlayWithOpts:n[6]||(n[6]=n=>e.$emit("play-with-opts",n)),onScrollEnd:S.loadNextPage,onSelect:n[7]||(n[7]=e=>x.selectedResult=e)},null,8,["results","filter","selected-result","onScrollEnd"])])):(0,s.kq)("",!0)])}var x=t(6791),S=t(1602),q=t(8637),C={mixins:[q.Z],emits:["add-to-playlist","download","download-audio","open-channel","play","play-with-opts"],components:{Loading:x.Z,Results:S.Z},props:{id:{type:String,required:!0},filter:{type:String,default:null},loading:{type:Boolean,default:!1}},data(){return{channel:null,loading_:!1,loadingNextPage:!1,selectedResult:null,subscribed:!1}},computed:{isLoading(){return this.loading||this.loading_},itemsByUrl(){return this.channel?.items.reduce(((e,n)=>(e[n.url]=n,e)),{})}},methods:{async loadChannel(){this.loading_=!0;try{await this.updateChannel(!0),this.subscribed=await this.request("youtube.is_subscribed",{channel_id:this.id})}finally{this.loading_=!1}},async updateChannel(e){const n=await this.request("youtube.get_channel",{id:this.id,next_page_token:this.channel?.next_page_token}),t=this.itemsByUrl||{};let s=n.items.filter((e=>!t[e.url])).map((e=>({type:"youtube",...e})));e||(s=this.channel.items.concat(s)),this.channel=n,this.channel.items=s},async loadNextPage(){if(this.channel?.next_page_token&&!this.loadingNextPage){this.loadingNextPage=!0;try{await this.timeout(500),await this.updateChannel()}finally{this.loadingNextPage=!1}}},async toggleSubscription(){const e=this.subscribed?"unsubscribe":"subscribe";await this.request(`youtube.${e}`,{channel_id:this.id}),this.subscribed=!this.subscribed}},async mounted(){this.setUrlArgs({channel:this.id}),await this.loadChannel()},unmounted(){this.setUrlArgs({channel:null})}},P=t(3744);const D=(0,P.Z)(C,[["render",v],["__scopeId","data-v-7dc6ffd8"]]);var N=D}}]);
//# sourceMappingURL=8955.a001fe8c.js.map