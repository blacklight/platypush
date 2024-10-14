"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[2015,2200,6640,2991,8955,9091],{6640:function(e,t,l){l.r(t),l.d(t,{default:function(){return a}});var i=l(8637),n={mixins:[i.Z],emits:["add-to-playlist","back","create-playlist","download","download-audio","path-change","play","remove-from-playlist","remove-playlist","rename-playlist"],props:{filter:{type:String,default:""},loading:{type:Boolean,default:!1},mediaPlugin:{type:String},selectedPlaylist:{default:null},selectedChannel:{default:null}},data(){return{loading_:!1}},computed:{isLoading(){return this.loading||this.loading_}}};const s=n;var a=s},2991:function(e,t,l){l.r(t),l.d(t,{default:function(){return _}});var i=l(6252),n=l(3577);const s=e=>((0,i.dD)("data-v-1e886630"),e=e(),(0,i.Cn)(),e),a={class:"nav"},o={class:"path"},d=s((()=>(0,i._)("i",{class:"fas fa-home"},null,-1))),c=[d],r=s((()=>(0,i._)("span",{class:"separator"},[(0,i._)("i",{class:"fas fa-chevron-right"})],-1))),u=["title","onClick"],h={key:1},p={key:0,class:"separator"},y=s((()=>(0,i._)("i",{class:"fas fa-chevron-right"},null,-1))),g=[y];function f(e,t,l,s,d,y){return(0,i.wg)(),(0,i.iD)("div",a,[(0,i._)("span",o,[(0,i._)("span",{class:"back token",title:"Back",onClick:t[0]||(t[0]=t=>e.$emit("back"))},c),r]),((0,i.wg)(!0),(0,i.iD)(i.HY,null,(0,i.Ko)(l.path,((t,s)=>((0,i.wg)(),(0,i.iD)("span",{class:"path",key:s},[(0,i._)("span",{class:"token",title:t.title,onClick:e=>y.onClick(t)},[(e.icon=t.icon?.["class"])?((0,i.wg)(),(0,i.iD)("i",{key:0,class:(0,n.C_)(["icon",e.icon])},null,2)):(0,i.kq)("",!0),t.title?((0,i.wg)(),(0,i.iD)("span",h,(0,n.zw)(t.title),1)):(0,i.kq)("",!0)],8,u),(s>0||l.path.length>1)&&s<l.path.length-1?((0,i.wg)(),(0,i.iD)("span",p,g)):(0,i.kq)("",!0)])))),128))])}var m={emits:["back","select"],props:{path:{type:Array,default:()=>[]}},methods:{onClick(e){e.click&&(e.click(),this.$emit("select",e))}}},w=l(3744);const b=(0,w.Z)(m,[["render",f],["__scopeId","data-v-1e886630"]]);var _=b},2015:function(e,t,l){l.r(t),l.d(t,{default:function(){return b}});var i=l(6252);const n={class:"media-youtube-browser"},s={key:1,class:"browser"},a={key:1,class:"body"};function o(e,t,l,o,d,c){const r=(0,i.up)("Loading"),u=(0,i.up)("MediaNav"),h=(0,i.up)("NoToken"),p=(0,i.up)("Feed"),y=(0,i.up)("Playlists"),g=(0,i.up)("Subscriptions"),f=(0,i.up)("Index");return(0,i.wg)(),(0,i.iD)("div",n,[e.loading_?((0,i.wg)(),(0,i.j4)(r,{key:0})):((0,i.wg)(),(0,i.iD)("div",s,[(0,i.Wm)(u,{path:c.computedPath,onBack:t[0]||(t[0]=t=>e.$emit("back"))},null,8,["path"]),c.authToken?((0,i.wg)(),(0,i.iD)("div",a,["feed"===d.selectedView?((0,i.wg)(),(0,i.j4)(p,{key:0,filter:e.filter,loading:e.isLoading,onAddToPlaylist:t[1]||(t[1]=t=>e.$emit("add-to-playlist",t)),onDownload:t[2]||(t[2]=t=>e.$emit("download",t)),onDownloadAudio:t[3]||(t[3]=t=>e.$emit("download-audio",t)),onOpenChannel:c.selectChannelFromItem,onPlay:t[4]||(t[4]=t=>e.$emit("play",t)),onPlayWithOpts:t[5]||(t[5]=t=>e.$emit("play-with-opts",t))},null,8,["filter","loading","onOpenChannel"])):"playlists"===d.selectedView?((0,i.wg)(),(0,i.j4)(y,{key:1,filter:e.filter,loading:e.isLoading,"selected-playlist":d.selectedPlaylist_,onAddToPlaylist:t[6]||(t[6]=t=>e.$emit("add-to-playlist",t)),onDownload:t[7]||(t[7]=t=>e.$emit("download",t)),onDownloadAudio:t[8]||(t[8]=t=>e.$emit("download-audio",t)),onOpenChannel:c.selectChannelFromItem,onPlay:t[9]||(t[9]=t=>e.$emit("play",t)),onPlayWithOpts:t[10]||(t[10]=t=>e.$emit("play-with-opts",t)),onRemoveFromPlaylist:c.removeFromPlaylist,onSelect:c.onPlaylistSelected},null,8,["filter","loading","selected-playlist","onOpenChannel","onRemoveFromPlaylist","onSelect"])):"subscriptions"===d.selectedView?((0,i.wg)(),(0,i.j4)(g,{key:2,filter:e.filter,loading:e.isLoading,"selected-channel":d.selectedChannel_,onAddToPlaylist:t[11]||(t[11]=t=>e.$emit("add-to-playlist",t)),onDownload:t[12]||(t[12]=t=>e.$emit("download",t)),onDownloadAudio:t[13]||(t[13]=t=>e.$emit("download-audio",t)),onPlay:t[14]||(t[14]=t=>e.$emit("play",t)),onPlayWithOpts:t[15]||(t[15]=t=>e.$emit("play-with-opts",t)),onSelect:c.onChannelSelected},null,8,["filter","loading","selected-channel","onSelect"])):((0,i.wg)(),(0,i.j4)(f,{key:3,onSelect:c.selectView},null,8,["onSelect"]))])):((0,i.wg)(),(0,i.j4)(h,{key:0}))]))])}l(560);var d=l(6791),c=l(2991),r=l(6640),u=l(1042),h=l(2200),p=l(9091),y=l(2694),g=l(8903),f={mixins:[r["default"]],components:{Feed:u["default"],Index:h["default"],Loading:d.Z,MediaNav:c["default"],NoToken:p["default"],Playlists:y["default"],Subscriptions:g["default"]},emits:["add-to-playlist","back","download","download-audio","play","play-with-opts"],data(){return{youtubeConfig:null,selectedView:null,selectedPlaylist_:null,selectedChannel_:null,path:[]}},computed:{authToken(){return this.youtubeConfig?.auth_token},computedPath(){return[{title:"YouTube",click:()=>this.selectView(null),icon:{class:"fab fa-youtube"}},...this.path]}},methods:{async loadYoutubeConfig(){this.loading_=!0;try{this.youtubeConfig=(await this.request("config.get_plugins")).youtube}finally{this.loading_=!1}},async removeFromPlaylist(e){const t=e.playlist_id,l=e.item.url;this.loading_=!0;try{await this.request("youtube.remove_from_playlist",{playlist_id:t,video_id:l})}finally{this.loading_=!1}},async createPlaylist(e){this.loading_=!0;try{await this.request("youtube.create_playlist",{name:e})}finally{this.loading_=!1}},selectView(e){this.selectedView=e,"playlists"===e?this.selectedPlaylist_=null:"subscriptions"===e&&(this.selectedChannel_=null),this.path=e?.length?[{title:e.slice(0,1).toUpperCase()+e.slice(1),click:()=>this.selectView(e)}]:[]},onPlaylistSelected(e){this.selectedPlaylist_=e,e&&(this.selectedView="playlists",this.path.push({title:e.name}))},onChannelSelected(e){this.selectedChannel_=e,e&&(this.selectedView="subscriptions",this.path.push({title:e.name}))},initView(){const e=this.getUrlArgs();e.section&&(this.selectedView=e.section),this.selectedView&&this.selectView(this.selectedView)},async selectChannelFromItem(e){if(!e.channel_url)return;const t=await this.request("youtube.get_channel",{id:e.channel_url.split("/").pop()});t&&this.onChannelSelected(t)}},watch:{selectedPlaylist(){this.onPlaylistSelected(this.selectedPlaylist)},selectedPlaylist_(e){null==e&&this.setUrlArgs({playlist:null})},selectedChannel(){this.onChannelSelected(this.selectedChannel)},selectedChannel_(e){null==e&&this.setUrlArgs({channel:null})},selectedView(){this.setUrlArgs({section:this.selectedView})}},mounted(){this.loadYoutubeConfig(),this.initView(),this.onPlaylistSelected(this.selectedPlaylist),this.onChannelSelected(this.selectedChannel)},unmounted(){this.setUrlArgs({section:null})}},m=l(3744);const w=(0,m.Z)(f,[["render",o],["__scopeId","data-v-14d15ad4"]]);var b=w},8955:function(e,t,l){l.r(t),l.d(t,{default:function(){return L}});var i=l(6252),n=l(3577);const s={class:"media-youtube-channel"},a={key:1,class:"channel"},o={class:"header"},d={class:"banner"},c=["src"],r={class:"row info-container"},u={class:"info"},h={class:"row"},p={class:"title-container"},y=["href"],g={class:"image"},f=["src"],m=["href"],w={class:"actions"},b=["title"],_={key:0,class:"subscribers"},v={key:0,class:"description"};function k(e,t,l,k,C,P){const $=(0,i.up)("Loading"),D=(0,i.up)("Results");return(0,i.wg)(),(0,i.iD)("div",s,[P.isLoading?((0,i.wg)(),(0,i.j4)($,{key:0})):C.channel?((0,i.wg)(),(0,i.iD)("div",a,[(0,i._)("div",o,[(0,i._)("div",d,[C.channel?.banner?.length?((0,i.wg)(),(0,i.iD)("img",{key:0,src:C.channel.banner},null,8,c)):(0,i.kq)("",!0)]),(0,i._)("div",r,[(0,i._)("div",u,[(0,i._)("div",h,[(0,i._)("div",p,[C.channel?.image?.length?((0,i.wg)(),(0,i.iD)("a",{key:0,href:C.channel.url,target:"_blank",rel:"noopener noreferrer"},[(0,i._)("div",g,[(0,i._)("img",{src:C.channel.image},null,8,f)])],8,y)):(0,i.kq)("",!0),(0,i._)("a",{class:"title",href:C.channel.url,target:"_blank",rel:"noopener noreferrer"},(0,n.zw)(C.channel?.name),9,m)]),(0,i._)("div",w,[(0,i._)("button",{title:C.subscribed?"Unsubscribe":"Subscribe",onClick:t[0]||(t[0]=(...e)=>P.toggleSubscription&&P.toggleSubscription(...e))},(0,n.zw)(C.subscribed?"Unsubscribe":"Subscribe"),9,b),null!=C.channel.subscribers&&(C.channel.subscribers||0)>=0?((0,i.wg)(),(0,i.iD)("div",_,(0,n.zw)(e.formatNumber(C.channel.subscribers))+" subscribers ",1)):(0,i.kq)("",!0)])]),C.channel?.description?((0,i.wg)(),(0,i.iD)("div",v,(0,n.zw)(C.channel.description),1)):(0,i.kq)("",!0)])])]),(0,i.Wm)(D,{results:C.channel.items,filter:l.filter,"result-index-step":null,"selected-result":C.selectedResult,ref:"results",onAddToPlaylist:t[1]||(t[1]=t=>e.$emit("add-to-playlist",t)),onDownload:t[2]||(t[2]=t=>e.$emit("download",t)),onDownloadAudio:t[3]||(t[3]=t=>e.$emit("download-audio",t)),onOpenChannel:t[4]||(t[4]=t=>e.$emit("open-channel",t)),onPlay:t[5]||(t[5]=t=>e.$emit("play",t)),onPlayWithOpts:t[6]||(t[6]=t=>e.$emit("play-with-opts",t)),onScrollEnd:P.loadNextPage,onSelect:t[7]||(t[7]=e=>C.selectedResult=e)},null,8,["results","filter","selected-result","onScrollEnd"])])):(0,i.kq)("",!0)])}var C=l(6791),P=l(1602),$=l(8637),D={mixins:[$.Z],emits:["add-to-playlist","download","download-audio","open-channel","play","play-with-opts"],components:{Loading:C.Z,Results:P.Z},props:{id:{type:String,required:!0},filter:{type:String,default:null},loading:{type:Boolean,default:!1}},data(){return{channel:null,loading_:!1,loadingNextPage:!1,selectedResult:null,subscribed:!1}},computed:{isLoading(){return this.loading||this.loading_},itemsByUrl(){return this.channel?.items.reduce(((e,t)=>(e[t.url]=t,e)),{})}},methods:{async loadChannel(){this.loading_=!0;try{await this.updateChannel(!0),this.subscribed=await this.request("youtube.is_subscribed",{channel_id:this.id})}finally{this.loading_=!1}},async updateChannel(e){const t=await this.request("youtube.get_channel",{id:this.id,next_page_token:this.channel?.next_page_token}),l=this.itemsByUrl||{};let i=t.items.filter((e=>!l[e.url])).map((e=>({type:"youtube",...e})));e||(i=this.channel.items.concat(i)),this.channel=t,this.channel.items=i},async loadNextPage(){if(this.channel?.next_page_token&&!this.loadingNextPage){this.loadingNextPage=!0;try{await this.timeout(500),await this.updateChannel()}finally{this.loadingNextPage=!1}}},async toggleSubscription(){const e=this.subscribed?"unsubscribe":"subscribe";await this.request(`youtube.${e}`,{channel_id:this.id}),this.subscribed=!this.subscribed}},async mounted(){this.setUrlArgs({channel:this.id}),await this.loadChannel()},unmounted(){this.setUrlArgs({channel:null})}},S=l(3744);const A=(0,S.Z)(D,[["render",k],["__scopeId","data-v-7dc6ffd8"]]);var L=A},1042:function(e,t,l){l.r(t),l.d(t,{default:function(){return p}});var i=l(6252);const n={class:"media-youtube-feed"};function s(e,t,l,s,a,o){const d=(0,i.up)("Loading"),c=(0,i.up)("NoItems"),r=(0,i.up)("Results");return(0,i.wg)(),(0,i.iD)("div",n,[o.isLoading?((0,i.wg)(),(0,i.j4)(d,{key:0})):a.feed?.length?((0,i.wg)(),(0,i.j4)(r,{key:2,results:a.feed,filter:l.filter,sources:{youtube:!0},"selected-result":a.selectedResult,onAddToPlaylist:t[0]||(t[0]=t=>e.$emit("add-to-playlist",t)),onDownload:t[1]||(t[1]=t=>e.$emit("download",t)),onDownloadAudio:t[2]||(t[2]=t=>e.$emit("download-audio",t)),onOpenChannel:t[3]||(t[3]=t=>e.$emit("open-channel",t)),onSelect:t[4]||(t[4]=e=>a.selectedResult=e),onPlay:t[5]||(t[5]=t=>e.$emit("play",t)),onPlayWithOpts:t[6]||(t[6]=t=>e.$emit("play-with-opts",t))},null,8,["results","filter","selected-result"])):((0,i.wg)(),(0,i.j4)(c,{key:1,"with-shadow":!1},{default:(0,i.w5)((()=>[(0,i.Uk)(" No videos found. ")])),_:1}))])}var a=l(3222),o=l(6791),d=l(1602),c=l(8637),r={mixins:[c.Z],emits:["add-to-playlist","download","download-audio","open-channel","play","play-with-opts"],components:{Loading:o.Z,NoItems:a.Z,Results:d.Z},props:{filter:{type:String,default:null},loading:{type:Boolean,default:!1}},data(){return{feed:[],loading_:!1,selectedResult:null}},computed:{isLoading(){return this.loading_||this.loading}},methods:{async loadFeed(){this.loading_=!0;try{this.feed=(await this.request("youtube.get_feed")).map((e=>({...e,type:"youtube"})))}finally{this.loading_=!1}}},mounted(){this.loadFeed()}},u=l(3744);const h=(0,u.Z)(r,[["render",s],["__scopeId","data-v-0a5cd0e6"]]);var p=h},2200:function(e,t,l){l.r(t),l.d(t,{default:function(){return w}});var i=l(6252);const n={class:"youtube-views-browser grid"},s=(0,i._)("div",{class:"icon"},[(0,i._)("i",{class:"fas fa-rss"})],-1),a=(0,i._)("div",{class:"name"},"Feed",-1),o=[s,a],d=(0,i._)("div",{class:"icon"},[(0,i._)("i",{class:"fas fa-list"})],-1),c=(0,i._)("div",{class:"name"},"Playlists",-1),r=[d,c],u=(0,i._)("div",{class:"icon"},[(0,i._)("i",{class:"fas fa-user"})],-1),h=(0,i._)("div",{class:"name"},"Subscriptions",-1),p=[u,h];function y(e,t,l,s,a,d){return(0,i.wg)(),(0,i.iD)("div",n,[(0,i._)("div",{class:"item",onClick:t[0]||(t[0]=t=>e.$emit("select","feed"))},o),(0,i._)("div",{class:"item",onClick:t[1]||(t[1]=t=>e.$emit("select","playlists"))},r),(0,i._)("div",{class:"item",onClick:t[2]||(t[2]=t=>e.$emit("select","subscriptions"))},p)])}var g={emits:["select"]},f=l(3744);const m=(0,f.Z)(g,[["render",y]]);var w=m},9091:function(e,t,l){l.r(t),l.d(t,{default:function(){return u}});var i=l(6252);const n={class:"no-token"},s=(0,i.uE)('<div class="title" data-v-42457341> No <code data-v-42457341>auth_token</code> found in the YouTube configuration. </div><div class="description" data-v-42457341> This integration requires an <code data-v-42457341>auth_token</code> to be set in the <code data-v-42457341>youtube</code> section of the configuration file in order to access your playlists and subscriptions.<br data-v-42457341><br data-v-42457341> Piped auth tokens are currently supported. You can retrieve one through the following procedure: <ol data-v-42457341><li data-v-42457341>Login to your configured Piped instance.</li><li data-v-42457341>Copy the RSS/Atom feed URL on the <i data-v-42457341>Feed</i> tab.</li><li data-v-42457341>Copy the <code data-v-42457341>auth_token</code> query parameter from the URL.</li><li data-v-42457341> Enter it in the <code data-v-42457341>auth_token</code> field in the <code data-v-42457341>youtube</code> section of the configuration file. </li></ol></div>',2),a=[s];function o(e,t){return(0,i.wg)(),(0,i.iD)("div",n,a)}var d=l(3744);const c={},r=(0,d.Z)(c,[["render",o],["__scopeId","data-v-42457341"]]);var u=r},8903:function(e,t,l){l.r(t),l.d(t,{default:function(){return v}});var i=l(6252),n=l(3577);const s={class:"media-youtube-subscriptions"},a={key:0,class:"subscriptions-index"},o={key:2,class:"body grid"},d=["onClick"],c={class:"image"},r=["src","alt"],u={class:"title"},h={key:1,class:"subscription-body"};function p(e,t,l,p,y,g){const f=(0,i.up)("Loading"),m=(0,i.up)("NoItems"),w=(0,i.up)("Channel");return(0,i.wg)(),(0,i.iD)("div",s,[l.selectedChannel?.id?((0,i.wg)(),(0,i.iD)("div",h,[(0,i.Wm)(w,{id:l.selectedChannel.id,filter:l.filter,onAddToPlaylist:t[0]||(t[0]=t=>e.$emit("add-to-playlist",t)),onDownload:t[1]||(t[1]=t=>e.$emit("download",t)),onDownloadAudio:t[2]||(t[2]=t=>e.$emit("download-audio",t)),onPlay:t[3]||(t[3]=t=>e.$emit("play",t)),onPlayWithOpts:t[4]||(t[4]=t=>e.$emit("play-with-opts",t))},null,8,["id","filter"])])):((0,i.wg)(),(0,i.iD)("div",a,[y.loading?((0,i.wg)(),(0,i.j4)(f,{key:0})):y.channels?.length?((0,i.wg)(),(0,i.iD)("div",o,[((0,i.wg)(!0),(0,i.iD)(i.HY,null,(0,i.Ko)(g.channelsById,((t,l)=>((0,i.wg)(),(0,i.iD)("div",{class:"channel item",key:l,onClick:l=>e.$emit("select",t)},[(0,i._)("div",c,[(0,i._)("img",{src:t.image,alt:t.name},null,8,r)]),(0,i._)("div",u,(0,n.zw)(t.name),1)],8,d)))),128))])):((0,i.wg)(),(0,i.j4)(m,{key:1,"with-shadow":!1},{default:(0,i.w5)((()=>[(0,i.Uk)(" No channels found. ")])),_:1}))]))])}var y=l(8955),g=l(3222),f=l(6791),m=l(8637),w={mixins:[m.Z],emits:["add-to-playlist","download","download-audio","play","play-with-opts","select"],components:{Channel:y["default"],Loading:f.Z,NoItems:g.Z},props:{selectedChannel:{type:Object,default:null},filter:{type:String,default:null}},data(){return{channels:[],loading:!1}},computed:{channelsById(){return this.channels.filter((e=>!this.filter||e.name.toLowerCase().includes(this.filter.toLowerCase()))).reduce(((e,t)=>(e[t.id]=t,e)),{})}},methods:{async loadSubscriptions(){this.loading=!0;try{this.channels=await this.request("youtube.get_subscriptions")}finally{this.loading=!1}},initView(){const e=this.getUrlArgs();e.channel&&this.$emit("select",{id:e.channel})}},async mounted(){await this.loadSubscriptions(),this.initView()}},b=l(3744);const _=(0,b.Z)(w,[["render",p],["__scopeId","data-v-293192dc"]]);var v=_}}]);
//# sourceMappingURL=2015.8fb37a01.js.map