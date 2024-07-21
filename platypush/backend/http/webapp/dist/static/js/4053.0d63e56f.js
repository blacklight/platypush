"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[4053],{4053:function(s,t,e){e.r(t),e.d(t,{default:function(){return y}});var i=e(6252);function a(s,t,e,a,l,r){const c=(0,i.up)("Loading"),o=(0,i.up)("MusicPlugin");return(0,i.wg)(),(0,i.iD)(i.HY,null,[l.loading?((0,i.wg)(),(0,i.j4)(c,{key:0})):(0,i.kq)("",!0),(0,i.Wm)(o,{"plugin-name":"music.spotify",loading:l.loading,config:e.config,tracks:l.tracks,status:l.status,playlists:l.playlists,"edited-playlist":l.editedPlaylist,"edited-playlist-tracks":l.editedPlaylistTracks,"track-info":l.trackInfo,"search-results":l.searchResults,"library-results":l.libraryResults,path:l.path,devices:l.devices,"selected-device":l.selectedDevice,"active-device":l.activeDevice,onPlay:r.play,onPause:r.pause,onStop:r.stop,onPrevious:r.previous,onNext:r.next,onClear:r.clear,onSetVolume:r.setVolume,onSeek:r.seek,onConsume:r.consume,onRandom:r.random,onRepeat:r.repeat,onStatusUpdate:t[0]||(t[0]=s=>r.refreshStatus(!0)),onNewPlayingTrack:t[1]||(t[1]=s=>r.refreshStatus(!0)),onRemoveFromTracklist:r.removeFromTracklist,onAddToTracklist:r.addToTracklist,onSwapTracks:r.swapTracks,onLoadPlaylist:r.loadPlaylist,onPlayPlaylist:r.playPlaylist,onRemovePlaylist:r.removePlaylist,onTracklistMove:r.moveTracklistTracks,onTracklistSave:r.saveToPlaylist,onPlaylistEdit:r.playlistEditChanged,onRefreshStatus:r.refreshStatus,onAddToTracklistFromEditedPlaylist:r.addToTracklistFromEditedPlaylist,onRemoveFromPlaylist:r.removeFromPlaylist,onInfo:t[2]||(t[2]=s=>l.trackInfo=s),onPlaylistAdd:r.playlistAdd,onAddToPlaylist:r.addToPlaylist,onPlaylistTrackMove:r.playlistTrackMove,onSearch:r.search,onSearchClear:t[3]||(t[3]=s=>l.searchResults=[]),onCd:r.cd,onPlaylistUpdate:t[4]||(t[4]=s=>r.refresh(!0)),onSelectDevice:r.selectDevice},null,8,["loading","config","tracks","status","playlists","edited-playlist","edited-playlist-tracks","track-info","search-results","library-results","path","devices","selected-device","active-device","onPlay","onPause","onStop","onPrevious","onNext","onClear","onSetVolume","onSeek","onConsume","onRandom","onRepeat","onRemoveFromTracklist","onAddToTracklist","onSwapTracks","onLoadPlaylist","onPlayPlaylist","onRemovePlaylist","onTracklistMove","onTracklistSave","onPlaylistEdit","onRefreshStatus","onAddToTracklistFromEditedPlaylist","onRemoveFromPlaylist","onPlaylistAdd","onAddToPlaylist","onPlaylistTrackMove","onSearch","onCd","onSelectDevice"])],64)}var l=e(4015),r=e(8637),c=e(6791),o={name:"MusicSpotify",components:{Loading:c.Z,MusicPlugin:l["default"]},mixins:[r.Z],props:{config:{type:Object,default:()=>{}}},data(){return{loading:!1,devices:{},selectedDevice:null,activeDevice:null,tracks:[],playlists:[],status:{},editedPlaylist:null,editedPlaylistTracks:[],trackInfo:null,searchResults:[],libraryResults:[],path:"/"}},methods:{async refreshTracks(s){s||(this.loading=!0);try{this.tracks=(await this.request("music.spotify.history")).map((s=>(s.time=s.duration,s)))}finally{this.loading=!1}},async refreshStatus(s){s||(this.loading=!0),this.devices=(await this.request("music.spotify.get_devices")).reduce(((s,t)=>(s[t.id]=t,s)),{});const t=Object.values(this.devices).filter((s=>s.is_active));this.activeDevice=t.length?t[0].id:null,!this.selectedDevice&&Object.values(this.devices).length&&(this.selectedDevice=this.activeDevice||[...Object.values(this.devices)][0].id);try{const s=await this.request("music.spotify.status");this.status={...s,duration:s.time}}finally{this.loading=!1}this.status.track&&(this.tracks?.[0]?.id!==this.status.track.id&&(this.tracks=[{...this.status.track,time:this.status.duration},...this.tracks]),this.status.playingPos=0)},async refreshPlaylists(s){s||(this.loading=!0);try{this.playlists=(await this.request("music.spotify.get_playlists")).sort(((s,t)=>s.name.localeCompare(t.name)))}finally{this.loading=!1}},async refresh(s){s||(this.loading=!0);try{await Promise.all([this.refreshTracks(s),this.refreshStatus(s),this.refreshPlaylists(s)])}finally{this.loading=!1}},async play(s){null!=s?.pos&&(s.uri=this.tracks[s.pos].uri),s?.uri?await this.request("music.spotify.play",{resource:s.uri,device:this.selectedDevice}):await this.request("music.spotify.play",{device:this.selectedDevice}),await this.refreshStatus(!0)},async pause(){await this.request("music.spotify.pause",{device:this.selectedDevice}),await this.refreshStatus(!0)},async stop(){await this.request("music.spotify.stop",{device:this.selectedDevice}),await this.refreshStatus(!0)},async previous(){await this.request("music.spotify.previous",{device:this.selectedDevice}),await this.refreshStatus(!0)},async next(){await this.request("music.spotify.next",{device:this.selectedDevice}),await this.refreshStatus(!0)},async clear(){},async setVolume(s){s!==this.status.volume&&(await this.request("music.spotify.set_volume",{device:this.selectedDevice,volume:s}),await this.refreshStatus(!0))},async seek(s){await this.request("music.spotify.seek",{device:this.selectedDevice,position:s}),await this.refreshStatus(!0)},async repeat(){await this.request("music.spotify.repeat",{device:this.selectedDevice,value:!this.status?.repeat}),await this.refreshStatus(!0)},async random(){await this.request("music.spotify.random",{device:this.selectedDevice,value:!this.status?.random}),await this.refreshStatus(!0)},async consume(){},async addToTracklist(s){s.file&&(s=s.file),await this.request("music.spotify.add",{device:this.selectedDevice,resource:s}),await this.refresh(!0)},async addToTracklistFromEditedPlaylist(s){const t=s?.tracks?.map((s=>this.editedPlaylistTracks[s]))?.filter((s=>s?.file))?.map((s=>s.file));t?.length&&(s.play&&1===t.length?await this.request("music.spotify.play",{device:this.selectedDevice,resource:t[0]}):await Promise.all(t.map((s=>this.request("music.spotify.add",{device:this.selectedDevice,resource:s})))),await this.refresh(!0))},async removeFromPlaylist(s){const t=s.map((s=>this.playlists[this.editedPlaylist].tracks[s].uri));await this.request("music.spotify.remove_from_playlist",{resources:t,playlist:this.playlists[this.editedPlaylist].name}),await this.playlistEditChanged(this.editedPlaylist)},async removeFromTracklist(){},async swapTracks(){},async playPlaylist(s){await this._loadPlaylist(s,!0)},async loadPlaylist(s){await this._loadPlaylist(s,!1)},async _loadPlaylist(s){const t=this.playlists[s];await this.request("music.spotify.play",{resource:t.uri,device:this.selectedDevice}),await this.refresh(!0)},async removePlaylist(){this.notify({text:"Playlist removal is not supported"})},async saveToPlaylist(){},async moveTracklistTracks(){},async playlistAdd(s){await this.request("music.spotify.add_to_playlist",{resources:[s],playlist:this.playlists[this.editedPlaylist].uri}),await this.playlistEditChanged(this.editedPlaylist)},async playlistEditChanged(s){if(this.editedPlaylist=s,null!=s){this.loading=!0;try{const t=await this.request("music.spotify.get_playlist",{playlist:this.playlists[s].uri});this.editedPlaylistTracks=t.tracks.map((s=>(s.time=s.duration,s)))}finally{this.loading=!1}}},async addToPlaylist(s){await Promise.all(s.playlists.map((async t=>{await this.request("music.spotify.add_to_playlist",{resources:[s.track.uri],playlist:this.playlists[t].uri}),await this.playlistEditChanged(t)})))},async playlistTrackMove(s){await this.request("music.spotify.playlist_move",{playlist:this.playlists[s.playlist].uri,from_pos:s.from-1,to_pos:s.to-1}),await this.playlistEditChanged(s.playlist)},async search(s){this.loading=!0;try{this.searchResults=(await this.request("music.spotify.search",s)).map((s=>(s.time=s.duration,s)))}finally{this.loading=!1}},async cd(){},async selectDevice(s){this.selectedDevice!==s&&(await this.request("music.spotify.start_or_transfer_playback",{device:s}),this.selectedDevice=s,this.refreshStatus(!0))}},mounted(){this.refresh()}},n=e(3744);const d=(0,n.Z)(o,[["render",a]]);var y=d}}]);
//# sourceMappingURL=4053.0d63e56f.js.map