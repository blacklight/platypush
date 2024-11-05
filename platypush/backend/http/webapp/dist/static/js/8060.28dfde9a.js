"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[8060,1918],{6561:function(t,l,e){e.d(l,{A:function(){return r}});var i=e(641),a=e(33);const s={class:"no-items-container"};function d(t,l,e,d,o,n){return(0,i.uX)(),(0,i.CE)("div",s,[(0,i.Lk)("div",{class:(0,a.C4)(["no-items fade-in",{shadow:e.withShadow}])},[(0,i.RG)(t.$slots,"default",{},void 0,!0)],2)])}var o={name:"NoItems",props:{withShadow:{type:Boolean,default:!0}}},n=e(6262);const y=(0,n.A)(o,[["render",d],["__scopeId","data-v-4856c4d7"]]);var r=y},1918:function(t,l,e){e.r(l),e.d(l,{default:function(){return E}});var i=e(641),a=e(33);const s={class:"media-youtube-playlist"},d={key:1,class:"playlist-container"},o={class:"header"},n={class:"banner"},y=["src"],r={class:"row info-container"},u={class:"info"},c={class:"row"},p=["href"],m={key:1,class:"title"},h={class:"n-items"},f={key:0,class:"row"},P={class:"description"},v={key:1,class:"row"},k={class:"channel"},g=["href"];function w(t,l,e,w,b,C){const _=(0,i.g2)("Loading"),L=(0,i.g2)("NoItems"),A=(0,i.g2)("Results");return(0,i.uX)(),(0,i.CE)("div",s,[b.loading?((0,i.uX)(),(0,i.Wv)(_,{key:0})):((0,i.uX)(),(0,i.CE)("div",d,[(0,i.Lk)("div",o,[(0,i.Lk)("div",n,[e.metadata?.image?.length?((0,i.uX)(),(0,i.CE)("img",{key:0,src:e.metadata?.image},null,8,y)):(0,i.Q3)("",!0)]),(0,i.Lk)("div",r,[(0,i.Lk)("div",u,[(0,i.Lk)("div",c,[e.metadata?.url?((0,i.uX)(),(0,i.CE)("a",{key:0,class:"title",href:e.metadata?.url,target:"_blank",rel:"noopener noreferrer"},(0,a.v_)(C.name),9,p)):((0,i.uX)(),(0,i.CE)("span",m,(0,a.v_)(C.name),1)),(0,i.Lk)("div",h,(0,a.v_)(C.nItems)+" videos",1)]),e.metadata?.description?((0,i.uX)(),(0,i.CE)("div",f,[(0,i.Lk)("div",P,(0,a.v_)(e.metadata?.description),1)])):(0,i.Q3)("",!0),e.metadata?.channel_url?((0,i.uX)(),(0,i.CE)("div",v,[(0,i.Lk)("div",k,[(0,i.eW)(" Uploaded by "),(0,i.Lk)("a",{href:e.metadata.channel_url,target:"_blank",rel:"noopener noreferrer"},(0,a.v_)(e.metadata?.channel),9,g)])])):(0,i.Q3)("",!0)])])]),C.nItems?((0,i.uX)(),(0,i.Wv)(A,{key:1,results:b.items,sources:{youtube:!0},filter:e.filter,playlist:e.id,"selected-result":b.selectedResult,onAddToPlaylist:l[0]||(l[0]=l=>t.$emit("add-to-playlist",l)),onDownload:l[1]||(l[1]=l=>t.$emit("download",l)),onDownloadAudio:l[2]||(l[2]=l=>t.$emit("download-audio",l)),onOpenChannel:l[3]||(l[3]=l=>t.$emit("open-channel",l)),onPlay:l[4]||(l[4]=l=>t.$emit("play",l)),onPlayWithOpts:l[5]||(l[5]=l=>t.$emit("play-with-opts",l)),onRemoveFromPlaylist:l[6]||(l[6]=l=>t.$emit("remove-from-playlist",l)),onSelect:l[7]||(l[7]=t=>b.selectedResult=t),onView:l[8]||(l[8]=l=>t.$emit("view",l))},null,8,["results","filter","playlist","selected-result"])):((0,i.uX)(),(0,i.Wv)(L,{key:0,"with-shadow":!1},{default:(0,i.k6)((()=>[(0,i.eW)(" No videos found. ")])),_:1}))]))])}var b=e(6561),C=e(9828),_=e(1101),L=e(2002),A={mixins:[L.A],emits:["add-to-playlist","download","download-audio","open-channel","play","play-with-opts","remove-from-playlist","view"],components:{Loading:C.A,NoItems:b.A,Results:_.A},props:{id:{type:String,required:!0},filter:{type:String,default:null},metadata:{type:Object,default:null}},data(){return{items:[],loading:!1,selectedResult:null}},computed:{name(){return this.metadata?.title||this.metadata?.name},nItems(){return this.metadata?.videos||this.items?.length||0}},methods:{async loadItems(){this.loading=!0;try{this.items=(await this.request("youtube.get_playlist",{id:this.id})).map((t=>({...t,type:"youtube"})))}finally{this.loading=!1}}},mounted(){this.setUrlArgs({playlist:this.id}),this.loadItems()},unmounted(){this.setUrlArgs({playlist:null})}},$=e(6262);const I=(0,$.A)(A,[["render",w],["__scopeId","data-v-7dfc81fd"]]);var E=I},8060:function(t,l,e){e.r(l),e.d(l,{default:function(){return U}});var i=e(641),a=e(33),s=e(3751);const d=t=>((0,i.Qi)("data-v-643b9f62"),t=t(),(0,i.jt)(),t),o={class:"media-youtube-playlists"},n={key:0,class:"playlists-index"},y={key:2,class:"body grid"},r=["onClick"],u={class:"title"},c={class:"actions"},p=["onClick"],m=d((()=>(0,i.Lk)("i",{class:"fa fa-trash"},null,-1))),h=[m],f=["onClick"],P=d((()=>(0,i.Lk)("i",{class:"fa fa-pencil"},null,-1))),v=[P],k={key:1,class:"playlist-body"},g={class:"row"},w={class:"row"},b={class:"row buttons"},C=d((()=>(0,i.Lk)("div",{class:"btn-container col-6"},[(0,i.Lk)("button",{type:"submit"},[(0,i.Lk)("i",{class:"fa fa-check"}),(0,i.eW)(" Save ")])],-1))),_={class:"btn-container col-6"},L=d((()=>(0,i.Lk)("i",{class:"fa fa-times"},null,-1)));function A(t,l,e,d,m,P){const A=(0,i.g2)("Loading"),$=(0,i.g2)("NoItems"),I=(0,i.g2)("MediaImage"),E=(0,i.g2)("Playlist"),X=(0,i.g2)("TextPrompt"),D=(0,i.g2)("ConfirmDialog"),N=(0,i.g2)("Modal"),W=(0,i.g2)("FloatingButton");return(0,i.uX)(),(0,i.CE)("div",o,[e.selectedPlaylist?.id?((0,i.uX)(),(0,i.CE)("div",k,[(0,i.bF)(E,{id:e.selectedPlaylist.id,filter:e.filter,metadata:P.playlistsById[e.selectedPlaylist.id]||e.selectedPlaylist,onAddToPlaylist:l[0]||(l[0]=l=>t.$emit("add-to-playlist",l)),onDownload:l[1]||(l[1]=l=>t.$emit("download",l)),onDownloadAudio:l[2]||(l[2]=l=>t.$emit("download-audio",l)),onOpenChannel:l[3]||(l[3]=l=>t.$emit("open-channel",l)),onRemoveFromPlaylist:l[4]||(l[4]=l=>t.$emit("remove-from-playlist",{item:l,playlist_id:e.selectedPlaylist.id})),onPlay:l[5]||(l[5]=l=>t.$emit("play",l)),onPlayWithOpts:l[6]||(l[6]=l=>t.$emit("play-with-opts",l))},null,8,["id","filter","metadata"])])):((0,i.uX)(),(0,i.CE)("div",n,[P.isLoading?((0,i.uX)(),(0,i.Wv)(A,{key:0})):m.playlists?.length?((0,i.uX)(),(0,i.CE)("div",y,[((0,i.uX)(!0),(0,i.CE)(i.FK,null,(0,i.pI)(P.playlistsById,((l,e)=>((0,i.uX)(),(0,i.CE)("div",{class:"playlist item",key:e,onClick:e=>t.$emit("select",l)},[(0,i.bF)(I,{item:l,"has-play":!1},null,8,["item"]),(0,i.Lk)("div",u,(0,a.v_)(l.name),1),(0,i.Lk)("div",c,[(0,i.Lk)("button",{title:"Remove",onClick:(0,s.D$)((t=>m.deletedPlaylist=l.id),["stop"])},h,8,p),(0,i.Lk)("button",{title:"Edit",onClick:(0,s.D$)((t=>m.editedPlaylist=l.id),["stop"])},v,8,f)])],8,r)))),128))])):((0,i.uX)(),(0,i.Wv)($,{key:1,"with-shadow":!1},{default:(0,i.k6)((()=>[(0,i.eW)(" No playlists found. ")])),_:1}))])),(0,i.bF)(X,{visible:m.showCreatePlaylist,onInput:l[7]||(l[7]=t=>P.createPlaylist(t)),onClose:l[8]||(l[8]=t=>m.showCreatePlaylist=!1)},{default:(0,i.k6)((()=>[(0,i.eW)(" Playlist name ")])),_:1},8,["visible"]),(0,i.bF)(D,{ref:"removePlaylist",title:"Remove Playlist",visible:null!=m.deletedPlaylist,onClose:l[9]||(l[9]=t=>m.deletedPlaylist=null),onInput:P.removePlaylist},{default:(0,i.k6)((()=>[(0,i.eW)(" Are you sure you want to remove this playlist? ")])),_:1},8,["visible","onInput"]),(0,i.bF)(N,{ref:"editPlaylist",title:"Edit Playlist",visible:null!=m.editedPlaylist,onClose:P.clearEditPlaylist,onOpen:P.onEditPlaylistOpen},{default:(0,i.k6)((()=>[(0,i.Lk)("form",{class:"edit-playlist-form",onSubmit:l[13]||(l[13]=(0,s.D$)(((...t)=>P.editPlaylist&&P.editPlaylist(...t)),["prevent"]))},[(0,i.Lk)("div",g,[(0,i.bo)((0,i.Lk)("input",{ref:"editPlaylistName",placeholder:"Playlist name","onUpdate:modelValue":l[10]||(l[10]=t=>m.editedPlaylistName=t)},null,512),[[s.Jo,m.editedPlaylistName]])]),(0,i.Lk)("div",w,[(0,i.bo)((0,i.Lk)("input",{placeholder:"Playlist description","onUpdate:modelValue":l[11]||(l[11]=t=>m.editedPlaylistDescription=t)},null,512),[[s.Jo,m.editedPlaylistDescription]])]),(0,i.Lk)("div",b,[C,(0,i.Lk)("div",_,[(0,i.Lk)("button",{onClick:l[12]||(l[12]=(...t)=>P.clearEditPlaylist&&P.clearEditPlaylist(...t))},[L,(0,i.eW)(" Cancel ")])])])],32)])),_:1},8,["visible","onClose","onOpen"]),(0,i.bF)(W,{"icon-class":"fa fa-plus",title:"Create Playlist",onClick:l[14]||(l[14]=t=>m.showCreatePlaylist=!0)})])}var $=e(3538),I=e(7998),E=e(12),X=e(9513),D=e(6561),N=e(9828),W=e(1918),F=e(710),O=e(2002),R={mixins:[O.A],emits:["add-to-playlist","create-playlist","download","download-audio","open-channel","play","play-with-opts","remove-from-playlist","remove-playlist","rename-playlist","select"],components:{ConfirmDialog:$.A,FloatingButton:I.A,Loading:N.A,MediaImage:E.A,Modal:X.A,NoItems:D.A,Playlist:W["default"],TextPrompt:F.A},props:{selectedPlaylist:{type:Object,default:null},filter:{type:String,default:null},loading:{type:Boolean,default:!1}},data(){return{deletedPlaylist:null,editedPlaylist:null,editedPlaylistName:"",editedPlaylistDescription:"",playlists:[],loading_:!1,showCreatePlaylist:!1}},computed:{playlistsById(){return this.playlists.filter((t=>!this.filter||t.name.toLowerCase().includes(this.filter.toLowerCase()))).reduce(((t,l)=>(t[l.id]=l,t)),{})},isLoading(){return this.loading_||this.loading}},methods:{async loadPlaylists(){this.loading_=!0;try{this.playlists=await this.request("youtube.get_playlists")}finally{this.loading_=!1}},async createPlaylist(t){this.loading_=!0;try{await this.request("youtube.create_playlist",{name:t}),this.showCreatePlaylist=!1,this.loadPlaylists()}finally{this.loading_=!1}},async removePlaylist(){if(this.deletedPlaylist){this.loading_=!0;try{await this.request("youtube.delete_playlist",{id:this.deletedPlaylist}),this.deletedPlaylist=null,this.loadPlaylists()}finally{this.loading_=!1}}},async editPlaylist(){if(this.editedPlaylist){this.loading_=!0;try{await this.request("youtube.rename_playlist",{id:this.editedPlaylist,name:this.editedPlaylistName,description:this.editedPlaylistDescription}),this.clearEditPlaylist(),this.loadPlaylists()}finally{this.loading_=!1}}},clearEditPlaylist(){this.editedPlaylist=null,this.editedPlaylistName="",this.editedPlaylistDescription="",this.$refs.editPlaylist.hide()},onEditPlaylistOpen(){const t=this.playlistsById[this.editedPlaylist];this.editedPlaylistName=t.name,this.editedPlaylistDescription=t.description,this.$nextTick((()=>this.$refs.editPlaylistName.focus()))}},async mounted(){await this.loadPlaylists();const t=this.getUrlArgs();if(t.playlist){const l=this.playlistsById[t.playlist];l?this.$emit("select",l):this.$emit("select",{id:t.playlist})}},unmouted(){this.setUrlArgs({section:null})}},B=e(6262);const S=(0,B.A)(R,[["render",A],["__scopeId","data-v-643b9f62"]]);var U=S}}]);
//# sourceMappingURL=8060.28dfde9a.js.map