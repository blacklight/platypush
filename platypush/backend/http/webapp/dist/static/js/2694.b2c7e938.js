"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[2694,1652],{3222:function(t,l,e){e.d(l,{Z:function(){return r}});var i=e(6252),a=e(3577);const s={class:"no-items-container"};function d(t,l,e,d,n,o){return(0,i.wg)(),(0,i.iD)("div",s,[(0,i._)("div",{class:(0,a.C_)(["no-items fade-in",{shadow:e.withShadow}])},[(0,i.WI)(t.$slots,"default",{},void 0,!0)],2)])}var n={name:"NoItems",props:{withShadow:{type:Boolean,default:!0}}},o=e(3744);const y=(0,o.Z)(n,[["render",d],["__scopeId","data-v-4856c4d7"]]);var r=y},1652:function(t,l,e){e.r(l),e.d(l,{default:function(){return N}});var i=e(6252),a=e(3577);const s={class:"media-youtube-playlist"},d={key:1,class:"playlist-container"},n={class:"header"},o={class:"banner"},y=["src"],r={class:"row info-container"},u={class:"info"},c={class:"row"},p=["href"],m={key:1,class:"title"},h={class:"n-items"},f={key:0,class:"row"},w={class:"description"},P={key:1,class:"row"},g={class:"channel"},v=["href"];function _(t,l,e,_,k,b){const C=(0,i.up)("Loading"),D=(0,i.up)("NoItems"),I=(0,i.up)("Results");return(0,i.wg)(),(0,i.iD)("div",s,[k.loading?((0,i.wg)(),(0,i.j4)(C,{key:0})):((0,i.wg)(),(0,i.iD)("div",d,[(0,i._)("div",n,[(0,i._)("div",o,[e.metadata?.image?.length?((0,i.wg)(),(0,i.iD)("img",{key:0,src:e.metadata?.image},null,8,y)):(0,i.kq)("",!0)]),(0,i._)("div",r,[(0,i._)("div",u,[(0,i._)("div",c,[e.metadata?.url?((0,i.wg)(),(0,i.iD)("a",{key:0,class:"title",href:e.metadata?.url,target:"_blank",rel:"noopener noreferrer"},(0,a.zw)(b.name),9,p)):((0,i.wg)(),(0,i.iD)("span",m,(0,a.zw)(b.name),1)),(0,i._)("div",h,(0,a.zw)(b.nItems)+" videos",1)]),e.metadata?.description?((0,i.wg)(),(0,i.iD)("div",f,[(0,i._)("div",w,(0,a.zw)(e.metadata?.description),1)])):(0,i.kq)("",!0),e.metadata?.channel_url?((0,i.wg)(),(0,i.iD)("div",P,[(0,i._)("div",g,[(0,i.Uk)(" Uploaded by "),(0,i._)("a",{href:e.metadata.channel_url,target:"_blank",rel:"noopener noreferrer"},(0,a.zw)(e.metadata?.channel),9,v)])])):(0,i.kq)("",!0)])])]),b.nItems?((0,i.wg)(),(0,i.j4)(I,{key:1,results:k.items,sources:{youtube:!0},filter:e.filter,playlist:e.id,"selected-result":k.selectedResult,onAddToPlaylist:l[0]||(l[0]=l=>t.$emit("add-to-playlist",l)),onDownload:l[1]||(l[1]=l=>t.$emit("download",l)),onDownloadAudio:l[2]||(l[2]=l=>t.$emit("download-audio",l)),onOpenChannel:l[3]||(l[3]=l=>t.$emit("open-channel",l)),onPlay:l[4]||(l[4]=l=>t.$emit("play",l)),onPlayWithOpts:l[5]||(l[5]=l=>t.$emit("play-with-opts",l)),onRemoveFromPlaylist:l[6]||(l[6]=l=>t.$emit("remove-from-playlist",l)),onSelect:l[7]||(l[7]=t=>k.selectedResult=t)},null,8,["results","filter","playlist","selected-result"])):((0,i.wg)(),(0,i.j4)(D,{key:0,"with-shadow":!1},{default:(0,i.w5)((()=>[(0,i.Uk)(" No videos found. ")])),_:1}))]))])}var k=e(3222),b=e(6791),C=e(1602),D=e(8637),I={mixins:[D.Z],emits:["add-to-playlist","download","download-audio","open-channel","play","play-with-opts","remove-from-playlist"],components:{Loading:b.Z,NoItems:k.Z,Results:C.Z},props:{id:{type:String,required:!0},filter:{type:String,default:null},metadata:{type:Object,default:null}},data(){return{items:[],loading:!1,selectedResult:null}},computed:{name(){return this.metadata?.title||this.metadata?.name},nItems(){return this.metadata?.videos||this.items?.length||0}},methods:{async loadItems(){this.loading=!0;try{this.items=(await this.request("youtube.get_playlist",{id:this.id})).map((t=>({...t,type:"youtube"})))}finally{this.loading=!1}}},mounted(){this.setUrlArgs({playlist:this.id}),this.loadItems()},unmounted(){this.setUrlArgs({playlist:null})}},$=e(3744);const Z=(0,$.Z)(I,[["render",_],["__scopeId","data-v-7f3997be"]]);var N=Z},2694:function(t,l,e){e.r(l),e.d(l,{default:function(){return S}});var i=e(6252),a=e(3577),s=e(9963);const d=t=>((0,i.dD)("data-v-643b9f62"),t=t(),(0,i.Cn)(),t),n={class:"media-youtube-playlists"},o={key:0,class:"playlists-index"},y={key:2,class:"body grid"},r=["onClick"],u={class:"title"},c={class:"actions"},p=["onClick"],m=d((()=>(0,i._)("i",{class:"fa fa-trash"},null,-1))),h=[m],f=["onClick"],w=d((()=>(0,i._)("i",{class:"fa fa-pencil"},null,-1))),P=[w],g={key:1,class:"playlist-body"},v={class:"row"},_={class:"row"},k={class:"row buttons"},b=d((()=>(0,i._)("div",{class:"btn-container col-6"},[(0,i._)("button",{type:"submit"},[(0,i._)("i",{class:"fa fa-check"}),(0,i.Uk)(" Save ")])],-1))),C={class:"btn-container col-6"},D=d((()=>(0,i._)("i",{class:"fa fa-times"},null,-1)));function I(t,l,e,d,m,w){const I=(0,i.up)("Loading"),$=(0,i.up)("NoItems"),Z=(0,i.up)("MediaImage"),N=(0,i.up)("Playlist"),U=(0,i.up)("TextPrompt"),O=(0,i.up)("ConfirmDialog"),q=(0,i.up)("Modal"),A=(0,i.up)("FloatingButton");return(0,i.wg)(),(0,i.iD)("div",n,[e.selectedPlaylist?.id?((0,i.wg)(),(0,i.iD)("div",g,[(0,i.Wm)(N,{id:e.selectedPlaylist.id,filter:e.filter,metadata:w.playlistsById[e.selectedPlaylist.id]||e.selectedPlaylist,onAddToPlaylist:l[0]||(l[0]=l=>t.$emit("add-to-playlist",l)),onDownload:l[1]||(l[1]=l=>t.$emit("download",l)),onDownloadAudio:l[2]||(l[2]=l=>t.$emit("download-audio",l)),onOpenChannel:l[3]||(l[3]=l=>t.$emit("open-channel",l)),onRemoveFromPlaylist:l[4]||(l[4]=l=>t.$emit("remove-from-playlist",{item:l,playlist_id:e.selectedPlaylist.id})),onPlay:l[5]||(l[5]=l=>t.$emit("play",l)),onPlayWithOpts:l[6]||(l[6]=l=>t.$emit("play-with-opts",l))},null,8,["id","filter","metadata"])])):((0,i.wg)(),(0,i.iD)("div",o,[w.isLoading?((0,i.wg)(),(0,i.j4)(I,{key:0})):m.playlists?.length?((0,i.wg)(),(0,i.iD)("div",y,[((0,i.wg)(!0),(0,i.iD)(i.HY,null,(0,i.Ko)(w.playlistsById,((l,e)=>((0,i.wg)(),(0,i.iD)("div",{class:"playlist item",key:e,onClick:e=>t.$emit("select",l)},[(0,i.Wm)(Z,{item:l,"has-play":!1},null,8,["item"]),(0,i._)("div",u,(0,a.zw)(l.name),1),(0,i._)("div",c,[(0,i._)("button",{title:"Remove",onClick:(0,s.iM)((t=>m.deletedPlaylist=l.id),["stop"])},h,8,p),(0,i._)("button",{title:"Edit",onClick:(0,s.iM)((t=>m.editedPlaylist=l.id),["stop"])},P,8,f)])],8,r)))),128))])):((0,i.wg)(),(0,i.j4)($,{key:1,"with-shadow":!1},{default:(0,i.w5)((()=>[(0,i.Uk)(" No playlists found. ")])),_:1}))])),(0,i.Wm)(U,{visible:m.showCreatePlaylist,onInput:l[7]||(l[7]=t=>w.createPlaylist(t)),onClose:l[8]||(l[8]=t=>m.showCreatePlaylist=!1)},{default:(0,i.w5)((()=>[(0,i.Uk)(" Playlist name ")])),_:1},8,["visible"]),(0,i.Wm)(O,{ref:"removePlaylist",title:"Remove Playlist",visible:null!=m.deletedPlaylist,onClose:l[9]||(l[9]=t=>m.deletedPlaylist=null),onInput:w.removePlaylist},{default:(0,i.w5)((()=>[(0,i.Uk)(" Are you sure you want to remove this playlist? ")])),_:1},8,["visible","onInput"]),(0,i.Wm)(q,{ref:"editPlaylist",title:"Edit Playlist",visible:null!=m.editedPlaylist,onClose:w.clearEditPlaylist,onOpen:w.onEditPlaylistOpen},{default:(0,i.w5)((()=>[(0,i._)("form",{class:"edit-playlist-form",onSubmit:l[13]||(l[13]=(0,s.iM)(((...t)=>w.editPlaylist&&w.editPlaylist(...t)),["prevent"]))},[(0,i._)("div",v,[(0,i.wy)((0,i._)("input",{ref:"editPlaylistName",placeholder:"Playlist name","onUpdate:modelValue":l[10]||(l[10]=t=>m.editedPlaylistName=t)},null,512),[[s.nr,m.editedPlaylistName]])]),(0,i._)("div",_,[(0,i.wy)((0,i._)("input",{placeholder:"Playlist description","onUpdate:modelValue":l[11]||(l[11]=t=>m.editedPlaylistDescription=t)},null,512),[[s.nr,m.editedPlaylistDescription]])]),(0,i._)("div",k,[b,(0,i._)("div",C,[(0,i._)("button",{onClick:l[12]||(l[12]=(...t)=>w.clearEditPlaylist&&w.clearEditPlaylist(...t))},[D,(0,i.Uk)(" Cancel ")])])])],32)])),_:1},8,["visible","onClose","onOpen"]),(0,i.Wm)(A,{"icon-class":"fa fa-plus",title:"Create Playlist",onClick:l[14]||(l[14]=t=>m.showCreatePlaylist=!0)})])}var $=e(3513),Z=e(8807),N=e(5300),U=e(3848),O=e(3222),q=e(6791),A=e(1652),B=e(671),E=e(8637),R={mixins:[E.Z],emits:["add-to-playlist","create-playlist","download","download-audio","open-channel","play","play-with-opts","remove-from-playlist","remove-playlist","rename-playlist","select"],components:{ConfirmDialog:$.Z,FloatingButton:Z.Z,Loading:q.Z,MediaImage:N.Z,Modal:U.Z,NoItems:O.Z,Playlist:A["default"],TextPrompt:B.Z},props:{selectedPlaylist:{type:Object,default:null},filter:{type:String,default:null},loading:{type:Boolean,default:!1}},data(){return{deletedPlaylist:null,editedPlaylist:null,editedPlaylistName:"",editedPlaylistDescription:"",playlists:[],loading_:!1,showCreatePlaylist:!1}},computed:{playlistsById(){return this.playlists.filter((t=>!this.filter||t.name.toLowerCase().includes(this.filter.toLowerCase()))).reduce(((t,l)=>(t[l.id]=l,t)),{})},isLoading(){return this.loading_||this.loading}},methods:{async loadPlaylists(){this.loading_=!0;try{this.playlists=await this.request("youtube.get_playlists")}finally{this.loading_=!1}},async createPlaylist(t){this.loading_=!0;try{await this.request("youtube.create_playlist",{name:t}),this.showCreatePlaylist=!1,this.loadPlaylists()}finally{this.loading_=!1}},async removePlaylist(){if(this.deletedPlaylist){this.loading_=!0;try{await this.request("youtube.delete_playlist",{id:this.deletedPlaylist}),this.deletedPlaylist=null,this.loadPlaylists()}finally{this.loading_=!1}}},async editPlaylist(){if(this.editedPlaylist){this.loading_=!0;try{await this.request("youtube.rename_playlist",{id:this.editedPlaylist,name:this.editedPlaylistName,description:this.editedPlaylistDescription}),this.clearEditPlaylist(),this.loadPlaylists()}finally{this.loading_=!1}}},clearEditPlaylist(){this.editedPlaylist=null,this.editedPlaylistName="",this.editedPlaylistDescription="",this.$refs.editPlaylist.hide()},onEditPlaylistOpen(){const t=this.playlistsById[this.editedPlaylist];this.editedPlaylistName=t.name,this.editedPlaylistDescription=t.description,this.$nextTick((()=>this.$refs.editPlaylistName.focus()))}},async mounted(){await this.loadPlaylists();const t=this.getUrlArgs();if(t.playlist){const l=this.playlistsById[t.playlist];l?this.$emit("select",l):this.$emit("select",{id:t.playlist})}},unmouted(){this.setUrlArgs({section:null})}},W=e(3744);const L=(0,W.Z)(R,[["render",I],["__scopeId","data-v-643b9f62"]]);var S=L}}]);
//# sourceMappingURL=2694.b2c7e938.js.map