"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[1330],{3222:function(e,t,o){o.d(t,{Z:function(){return r}});var n=o(6252),a=o(3577);const d={class:"no-items-container"};function l(e,t,o,l,s,i){return(0,n.wg)(),(0,n.iD)("div",d,[(0,n._)("div",{class:(0,a.C_)(["no-items fade-in",{shadow:o.withShadow}])},[(0,n.WI)(e.$slots,"default",{},void 0,!0)],2)])}var s={name:"NoItems",props:{withShadow:{type:Boolean,default:!0}}},i=o(3744);const u=(0,i.Z)(s,[["render",l],["__scopeId","data-v-4856c4d7"]]);var r=u},1330:function(e,t,o){o.r(t),o.d(t,{default:function(){return f}});var n=o(6252);const a={class:"media-youtube-feed"};function d(e,t,o,d,l,s){const i=(0,n.up)("Loading"),u=(0,n.up)("NoItems"),r=(0,n.up)("Results");return(0,n.wg)(),(0,n.iD)("div",a,[s.isLoading?((0,n.wg)(),(0,n.j4)(i,{key:0})):l.feed?.length?((0,n.wg)(),(0,n.j4)(r,{key:2,results:l.feed,filter:o.filter,sources:{youtube:!0},"selected-result":l.selectedResult,onAddToPlaylist:t[0]||(t[0]=t=>e.$emit("add-to-playlist",t)),onDownload:t[1]||(t[1]=t=>e.$emit("download",t)),onDownloadAudio:t[2]||(t[2]=t=>e.$emit("download-audio",t)),onOpenChannel:t[3]||(t[3]=t=>e.$emit("open-channel",t)),onSelect:t[4]||(t[4]=e=>l.selectedResult=e),onPlay:t[5]||(t[5]=t=>e.$emit("play",t)),onPlayCache:t[6]||(t[6]=t=>e.$emit("play-cache",t))},null,8,["results","filter","selected-result"])):((0,n.wg)(),(0,n.j4)(u,{key:1,"with-shadow":!1},{default:(0,n.w5)((()=>[(0,n.Uk)(" No videos found. ")])),_:1}))])}var l=o(3222),s=o(6791),i=o(2893),u=o(8637),r={mixins:[u.Z],emits:["add-to-playlist","download","download-audio","open-channel","play","play-cache"],components:{Loading:s.Z,NoItems:l.Z,Results:i.Z},props:{filter:{type:String,default:null},loading:{type:Boolean,default:!1}},data(){return{feed:[],loading_:!1,selectedResult:null}},computed:{isLoading(){return this.loading_||this.loading}},methods:{async loadFeed(){this.loading_=!0;try{this.feed=(await this.request("youtube.get_feed")).map((e=>({...e,type:"youtube"})))}finally{this.loading_=!1}}},mounted(){this.loadFeed()}},c=o(3744);const p=(0,c.Z)(r,[["render",d],["__scopeId","data-v-1353fda8"]]);var f=p}}]);
//# sourceMappingURL=1330.e58a96ea.js.map