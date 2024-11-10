"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[560],{8082:function(t,s,a){a.d(s,{A:function(){return y}});var e=a(641);function i(t,s,a,i,l,r){const n=(0,e.g2)("Loading"),o=(0,e.g2)("MusicPlugin");return(0,e.uX)(),(0,e.CE)(e.FK,null,[l.loading?((0,e.uX)(),(0,e.Wv)(n,{key:0})):(0,e.Q3)("",!0),(0,e.bF)(o,{"plugin-name":a.pluginName,config:a.config,"edited-playlist-tracks":l.editedPlaylistTracks,"edited-playlist":l.editedPlaylist,images:l.images,"library-results":l.libraryResults,loading:l.loading,path:l.path,playlists:l.playlists,"search-results":l.searchResults,status:r.status,track:r.track,"track-info":l.trackInfo,tracks:l.tracks,onAddToPlaylist:r.addToPlaylist,onAddToTracklistFromEditedPlaylist:r.addToTracklistFromEditedPlaylist,onAddToTracklist:r.addToTracklist,onCd:r.cd,onClear:r.clear,onConsume:r.consume,onInfo:s[0]||(s[0]=t=>l.trackInfo=t),onLoadPlaylist:r.loadPlaylist,onNewPlayingTrack:s[1]||(s[1]=t=>r.refreshStatus(!0,!0,t)),onNext:r.next,onPause:r.pause,onPlayPlaylist:r.playPlaylist,onPlay:r.play,onPlaylistAdd:r.playlistAdd,onPlaylistEdit:r.playlistEditChanged,onPlaylistTrackMove:r.playlistTrackMove,onPlaylistUpdate:s[2]||(s[2]=t=>r.refresh(!0)),onPrevious:r.previous,onRandom:r.random,onRemoveFromPlaylist:r.removeFromPlaylist,onRemoveFromTracklist:r.removeFromTracklist,onRemovePlaylist:r.removePlaylist,onRepeat:r.repeat,onSearchClear:s[3]||(s[3]=t=>l.searchResults=[]),onSearch:r.search,onSeek:r.seek,onSetVolume:r.setVolume,onStatusUpdate:s[4]||(s[4]=t=>r.refreshStatus(!0,!0,t)),onStop:r.stop,onSwapTracks:r.swapTracks,onTracklistMove:r.moveTracklistTracks,onTracklistSave:r.saveToPlaylist},null,8,["plugin-name","config","edited-playlist-tracks","edited-playlist","images","library-results","loading","path","playlists","search-results","status","track","track-info","tracks","onAddToPlaylist","onAddToTracklistFromEditedPlaylist","onAddToTracklist","onCd","onClear","onConsume","onLoadPlaylist","onNext","onPause","onPlayPlaylist","onPlay","onPlaylistAdd","onPlaylistEdit","onPlaylistTrackMove","onPrevious","onRandom","onRemoveFromPlaylist","onRemoveFromTracklist","onRemovePlaylist","onRepeat","onSearch","onSeek","onSetVolume","onStop","onSwapTracks","onTracklistMove","onTracklistSave"])],64)}a(4114);var l=a(4834),r=a(2002),n=a(9828),o=a(6658),h=a(2537),u={components:{Loading:n.A,MusicPlugin:l["default"]},mixins:[o.A,r.A],props:{config:{type:Object,default:()=>{}},pluginName:{type:String,required:!0},fetchStatusOnUpdate:{type:Boolean,default:!0}},data(){return{loading:!1,tracks:[],playlists:[],status_:{},images:{},editedPlaylist:null,editedPlaylistTracks:[],trackInfo:null,searchResults:[],libraryResults:[],path:[]}},computed:{status(){const t={...this.status_};return t.elapsed||isNaN(parseFloat(t.time))||(t.elapsed=t.time),t},track(){let t=null;return null!=this.status?.playingPos?t=this.status.playingPos:null!=this.status?.track?.pos&&(t=this.status.track.pos),null==t?null:this.tracks[t]}},methods:{async refreshTracks(t){t||(this.loading=!0);try{this.tracks=await this.request(`${this.pluginName}.get_tracks`)}finally{this.loading=!1}},setStatusFromEvent(t){t&&t.status&&(this.status_=this.parseStatus(t.status))},async refreshStatus(t,s,a){if(s&&!this.fetchStatusOnUpdate)this.setStatusFromEvent(a);else{t||(this.loading=!0);try{this.status_=this.parseStatus(await this.request(`${this.pluginName}.status`))}finally{this.loading=!1}}this.refreshCurrentImage()},async refreshCurrentImage(){const t=this.track?.uri||this.track?.file;t&&!(t in this.images)&&await this.refreshImages([this.track])},async refreshImages(t){Object.entries(await this.request(`${this.pluginName}.get_images`,{resources:[...new Set(t.map((t=>t.uri||t.file)).filter((t=>t&&!(t in this.images))))]})).forEach((([t,s])=>{this.images[t]=s}))},async refreshPlaylists(t){t||(this.loading=!0);try{this.playlists=(await this.request(`${this.pluginName}.get_playlists`)).map((t=>({...t,lastModified:t.last_modified}))).sort(((t,s)=>t.name.localeCompare(s.name)))}finally{this.loading=!1}},async refresh(t){t||(this.loading=!0);try{await Promise.all([this.refreshTracks(t),this.refreshStatus(t),this.refreshPlaylists(t)])}finally{this.loading=!1}},async play(t){null!=t?.pos?await this.request(`${this.pluginName}.play_pos`,{pos:t.pos}):t?.file?await this.request(`${this.pluginName}.play`,{resource:t.file}):await this.request(`${this.pluginName}.play`),await this.refreshStatus(!0)},async pause(){await this.request(`${this.pluginName}.pause`),await this.refreshStatus(!0)},async stop(){await this.request(`${this.pluginName}.stop`),await this.refreshStatus(!0)},async previous(){await this.request(`${this.pluginName}.previous`),await this.refreshStatus(!0)},async next(){await this.request(`${this.pluginName}.next`),await this.refreshStatus(!0)},async clear(){await this.request(`${this.pluginName}.clear`),await Promise.all([this.refreshStatus(!0),this.refreshTracks(!0)])},async setVolume(t){t!==this.status.volume&&(await this.request(`${this.pluginName}.set_volume`,{volume:t}),await this.refreshStatus(!0))},async seek(t){await this.request(`${this.pluginName}.seek`,{position:t}),await this.refreshStatus(!0)},async repeat(t){await this.request(`${this.pluginName}.repeat`,{value:!!parseInt(+t)}),await this.refreshStatus(!0)},async random(t){await this.request(`${this.pluginName}.random`,{value:!!parseInt(+t)}),await this.refreshStatus(!0)},async consume(t){await this.request(`${this.pluginName}.consume`,{value:!!parseInt(+t)}),await this.refreshStatus(!0)},async addToTracklist(t){t.file&&(t=t.file),await this.request(`${this.pluginName}.add`,{resource:t}),await this.refresh(!0)},async addToTracklistFromEditedPlaylist(t){const s=t?.tracks?.map((t=>this.editedPlaylistTracks[t]))?.filter((t=>t?.file))?.map((t=>t.file));s?.length&&(await Promise.all(s.map((t=>this.request(`${this.pluginName}.add`,{resource:t})))),await this.refresh(!0),t.play&&await this.request(`${this.pluginName}.play_pos`,{pos:this.tracks.length-s.length}))},async removeFromPlaylist(t){await this.request(`${this.pluginName}.remove_from_playlist`,{resources:t,playlist:this.playlists[this.editedPlaylist].name}),await this.playlistEditChanged(this.editedPlaylist)},async removeFromTracklist(t){await this.request(`${this.pluginName}.delete`,{positions:t.sort()}),await this.refresh(!0)},async swapTracks(t){await this.request(`${this.pluginName}.move`,{from_pos:t[0],to_pos:t[1]}),await this.refresh(!0)},async playPlaylist(t){await this._loadPlaylist(t,!0)},async loadPlaylist(t){await this._loadPlaylist(t,!1)},async _loadPlaylist(t,s){const a=this.playlists[t];await this.request(`${this.pluginName}.load`,{playlist:a.uri||a.name,play:s}),await this.refresh(!0)},async removePlaylist(t){const s=this.playlists[t];confirm(`Are you REALLY sure that you want to remove the playlist ${s.name}?`)&&(await this.request(`${this.pluginName}.delete_playlist`,{playlist:s.name}),await this.refreshPlaylists(!0))},async saveToPlaylist(t){await this.request(`${this.pluginName}.save`,{name:t}),await this.refreshPlaylists(!0)},splitMoveTracksIntoChunks(t){let s=[],a=t.to;const e=(t?.from||[]).map((t=>parseInt(t))).sort(((t,s)=>t-s)).reduce(((t,a,e)=>(0===e||s.length>0&&a===s[s.length-1]+1?s.push(a):(t.push(s),s=[a]),t)),[]);return s.length>0&&e.push(s),e.map((t=>{const s=t[0],e=t[t.length-1]===t[0]?t[0]:t[t.length-1]+1;let i={start:s,end:e,position:a};return a+=t.length,i}))},async moveTracklistTracks(t){for(const s of this.splitMoveTracksIntoChunks(t))await this.request(`${this.pluginName}.move`,s);this.fetchStatusOnUpdate||await this.refreshTracks(!0)},async playlistAdd(t){await this.request(`${this.pluginName}.add_to_playlist`,{resources:[t],playlist:this.playlists[this.editedPlaylist].name}),await this.playlistEditChanged(this.editedPlaylist)},async playlistEditChanged(t){if(this.editedPlaylist=t,null!=t){this.loading=!0;try{this.editedPlaylistTracks=await this.request(`${this.pluginName}.get_playlist`,{playlist:this.playlists[t].name})}finally{this.loading=!1}}},async addToPlaylist(t){await Promise.all(t.playlists.map((async s=>{await this.request(`${this.pluginName}.add_to_playlist`,{resources:[t.track.file],playlist:this.playlists[s].name}),await this.playlistEditChanged(s)})))},async playlistTrackMove(t){const s=this.playlists[t.playlist];if(s){for(const a of this.splitMoveTracksIntoChunks(t))await this.request(`${this.pluginName}.playlist_move`,{playlist:s.uri||s.name,start:a.start,end:a.end,position:a.position});await this.playlistEditChanged(t.playlist)}},async search(t){this.loading=!0;try{this.searchResults=await this.request(`${this.pluginName}.search`,{filter:t})}finally{this.loading=!1}},async cd(t){this.loading=!0;let s=t;Array.isArray(t)&&(s=0===t.length?null:t[t.length-1]);try{this.libraryResults=(await this.request(`${this.pluginName}.browse`,{uri:s})).filter((t=>!t.playlist)),this.path=t}finally{this.loading=!1}}},mounted(){h.j.on("connected",this.refresh),this.refresh(),this.cd(this.path)}},p=a(6262);const c=(0,p.A)(u,[["render",i]]);var y=c},560:function(t,s,a){a.r(s),a.d(s,{default:function(){return h}});var e=a(641);function i(t,s,a,i,l,r){const n=(0,e.g2)("MusicPlugin");return(0,e.uX)(),(0,e.Wv)(n,{"plugin-name":"music.mpd"})}var l=a(8082),r={components:{MusicPlugin:l.A}},n=a(6262);const o=(0,n.A)(r,[["render",i]]);var h=o},6658:function(t,s,a){a.d(s,{A:function(){return l}});var e={methods:{parseStatus(t){return Object.entries(t).reduce(((t,[s,a])=>{switch(s){case"bitrate":case"volume":t[s]=parseInt(a);break;case"consume":case"random":case"repeat":case"single":t[s]=!!parseInt(+a);break;case"playing_pos":case"song":t.playingPos=parseInt(a);break;case"time":a.split?(a=a.split(":"),1===a.length?t.elapsed=parseInt(a[0]):(t.elapsed=parseInt(a[0]),t.duration=parseInt(a[1]))):t.elapsed=a;break;case"track":null!=a?.time&&(t.duration=a.time),null!=a?.playlistPos&&(t.playingPos=a.pos);break;case"duration":t.duration=parseInt(a);break;case"elapsed":break;default:t[s]=a;break}return t}),{})}}};const i=e;var l=i}}]);
//# sourceMappingURL=560.2c038c1c.js.map