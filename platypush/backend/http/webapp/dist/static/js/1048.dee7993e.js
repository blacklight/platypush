"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[1048],{6561:function(e,t,o){o.d(t,{A:function(){return r}});var n=o(641),d=o(33);const a={class:"no-items-container"};function s(e,t,o,s,l,i){return(0,n.uX)(),(0,n.CE)("div",a,[(0,n.Lk)("div",{class:(0,d.C4)(["no-items fade-in",{shadow:o.withShadow}])},[(0,n.RG)(e.$slots,"default",{},void 0,!0)],2)])}var l={name:"NoItems",props:{withShadow:{type:Boolean,default:!0}}},i=o(6262);const u=(0,i.A)(l,[["render",s],["__scopeId","data-v-4856c4d7"]]);var r=u},1048:function(e,t,o){o.r(t),o.d(t,{default:function(){return h}});var n=o(641);const d={class:"media-youtube-feed"};function a(e,t,o,a,s,l){const i=(0,n.g2)("Loading"),u=(0,n.g2)("NoItems"),r=(0,n.g2)("Results");return(0,n.uX)(),(0,n.CE)("div",d,[l.isLoading?((0,n.uX)(),(0,n.Wv)(i,{key:0})):s.feed?.length?((0,n.uX)(),(0,n.Wv)(r,{key:2,results:s.feed,filter:o.filter,sources:{youtube:!0},"selected-result":s.selectedResult,onAddToPlaylist:t[0]||(t[0]=t=>e.$emit("add-to-playlist",t)),onDownload:t[1]||(t[1]=t=>e.$emit("download",t)),onDownloadAudio:t[2]||(t[2]=t=>e.$emit("download-audio",t)),onOpenChannel:t[3]||(t[3]=t=>e.$emit("open-channel",t)),onSelect:t[4]||(t[4]=e=>s.selectedResult=e),onPlay:t[5]||(t[5]=t=>e.$emit("play",t)),onPlayWithOpts:t[6]||(t[6]=t=>e.$emit("play-with-opts",t)),onScrollEnd:l.loadFeed,onView:t[7]||(t[7]=t=>e.$emit("view",t))},null,8,["results","filter","selected-result","onScrollEnd"])):((0,n.uX)(),(0,n.Wv)(u,{key:1,"with-shadow":!1},{default:(0,n.k6)((()=>t[8]||(t[8]=[(0,n.eW)(" No videos found. ")]))),_:1}))])}o(4114);var s=o(6561),l=o(9828),i=o(3149),u=o(2002),r={mixins:[u.A],emits:["add-to-playlist","download","download-audio","open-channel","play","play-with-opts","view"],components:{Loading:l.A,NoItems:s.A,Results:i.A},props:{filter:{type:String,default:null},loading:{type:Boolean,default:!1}},data(){return{feed:[],firstLoad:!0,loading_:!1,page:1,selectedResult:null}},computed:{isLoading(){return(this.loading_||this.loading)&&this.firstLoad}},methods:{async loadFeed(){this.loading_=!0;try{this.feed.push(...(await this.request("youtube.get_feed",{page:this.page})).map((e=>({...e,type:"youtube"})))),this.firstLoad=!1,this.feed.length&&this.page++}finally{this.loading_=!1}}},mounted(){this.loadFeed()}},p=o(6262);const c=(0,p.A)(r,[["render",a],["__scopeId","data-v-45233b96"]]);var h=c}}]);
//# sourceMappingURL=1048.dee7993e.js.map