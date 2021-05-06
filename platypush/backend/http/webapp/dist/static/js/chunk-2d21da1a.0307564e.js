(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-2d21da1a"],{d1b9:function(e,t,r){"use strict";r.r(t);r("38cf"),r("ac1f"),r("841c");var n=r("7a23");function a(e,t,r,a,s,i){var u=Object(n["z"])("Loading"),c=Object(n["z"])("MusicPlugin");return Object(n["r"])(),Object(n["e"])(n["a"],null,[s.loading?(Object(n["r"])(),Object(n["e"])(u,{key:0})):Object(n["f"])("",!0),Object(n["h"])(c,{"plugin-name":"music.mpd",loading:s.loading,config:r.config,tracks:s.tracks,status:s.status,playlists:s.playlists,"edited-playlist":s.editedPlaylist,"edited-playlist-tracks":s.editedPlaylistTracks,"track-info":s.trackInfo,"search-results":s.searchResults,"library-results":s.libraryResults,path:s.path,onPlay:i.play,onPause:i.pause,onStop:i.stop,onPrevious:i.previous,onNext:i.next,onClear:i.clear,onSetVolume:i.setVolume,onSeek:i.seek,onConsume:i.consume,onRandom:i.random,onRepeat:i.repeat,onStatusUpdate:t[1]||(t[1]=function(e){return i.refreshStatus(!0)}),onPlaylistUpdate:t[2]||(t[2]=function(e){return i.refresh(!0)}),onNewPlayingTrack:t[3]||(t[3]=function(e){return i.refreshStatus(!0)}),onRemoveFromTracklist:i.removeFromTracklist,onAddToTracklist:i.addToTracklist,onSwapTracks:i.swapTracks,onLoadPlaylist:i.loadPlaylist,onPlayPlaylist:i.playPlaylist,onRemovePlaylist:i.removePlaylist,onTracklistMove:i.moveTracklistTracks,onTracklistSave:i.saveToPlaylist,onPlaylistEdit:i.playlistEditChanged,onAddToTracklistFromEditedPlaylist:i.addToTracklistFromEditedPlaylist,onRemoveFromPlaylist:i.removeFromPlaylist,onInfo:t[4]||(t[4]=function(e){return s.trackInfo=e}),onPlaylistAdd:i.playlistAdd,onAddToPlaylist:i.addToPlaylist,onPlaylistTrackMove:i.playlistTrackMove,onSearch:i.search,onSearchClear:t[5]||(t[5]=function(e){return s.searchResults=[]}),onCd:i.cd},null,8,["loading","config","tracks","status","playlists","edited-playlist","edited-playlist-tracks","track-info","search-results","library-results","path","onPlay","onPause","onStop","onPrevious","onNext","onClear","onSetVolume","onSeek","onConsume","onRandom","onRepeat","onRemoveFromTracklist","onAddToTracklist","onSwapTracks","onLoadPlaylist","onPlayPlaylist","onRemovePlaylist","onTracklistMove","onTracklistSave","onPlaylistEdit","onAddToTracklistFromEditedPlaylist","onRemoveFromPlaylist","onPlaylistAdd","onAddToPlaylist","onPlaylistTrackMove","onSearch","onCd"])],64)}var s=r("3835"),i=r("1da1"),u=(r("4fad"),r("d81d"),r("1276"),r("d3b7"),r("ddb0"),r("b0c0"),r("3ca3"),r("4de4"),r("96cf"),r("0d41")),c=r("3e54"),o=r("3a5e"),l={name:"MusicMpd",components:{Loading:o["a"],MusicPlugin:u["default"]},mixins:[c["a"]],props:{config:{type:Object,default:function(){}}},data:function(){return{loading:!1,tracks:[],playlists:[],status:{},editedPlaylist:null,editedPlaylistTracks:[],trackInfo:null,searchResults:[],libraryResults:[],path:"/"}},methods:{refreshTracks:function(e){var t=this;return Object(i["a"])(regeneratorRuntime.mark((function r(){return regeneratorRuntime.wrap((function(r){while(1)switch(r.prev=r.next){case 0:return e||(t.loading=!0),r.prev=1,r.next=4,t.request("music.mpd.playlistinfo");case 4:t.tracks=r.sent;case 5:return r.prev=5,t.loading=!1,r.finish(5);case 8:case"end":return r.stop()}}),r,null,[[1,,5,8]])})))()},refreshStatus:function(e){var t=this;return Object(i["a"])(regeneratorRuntime.mark((function r(){return regeneratorRuntime.wrap((function(r){while(1)switch(r.prev=r.next){case 0:return e||(t.loading=!0),r.prev=1,r.t0=Object,r.next=5,t.request("music.mpd.status");case 5:r.t1=r.sent,t.status=r.t0.entries.call(r.t0,r.t1).reduce((function(e,t){var r=Object(s["a"])(t,2),n=r[0],a=r[1];switch(n){case"bitrate":case"volume":e[n]=parseInt(a);break;case"consume":case"random":case"repeat":case"single":e[n]=!!parseInt(a);break;case"song":e["playingPos"]=parseInt(a);break;case"time":var i=a.split(":").map((function(e){return parseInt(e)})),u=Object(s["a"])(i,2);e["elapsed"]=u[0],e["duration"]=u[1];break;case"elapsed":break;default:e[n]=a;break}return e}),{});case 7:return r.prev=7,t.loading=!1,r.finish(7);case 10:case"end":return r.stop()}}),r,null,[[1,,7,10]])})))()},refreshPlaylists:function(e){var t=this;return Object(i["a"])(regeneratorRuntime.mark((function r(){return regeneratorRuntime.wrap((function(r){while(1)switch(r.prev=r.next){case 0:return e||(t.loading=!0),r.prev=1,r.next=4,t.request("music.mpd.listplaylists");case 4:t.playlists=r.sent.map((function(e){return{name:e.playlist,lastModified:e["last-modified"]}})).sort((function(e,t){return e.name.localeCompare(t.name)}));case 5:return r.prev=5,t.loading=!1,r.finish(5);case 8:case"end":return r.stop()}}),r,null,[[1,,5,8]])})))()},refresh:function(e){var t=this;return Object(i["a"])(regeneratorRuntime.mark((function r(){return regeneratorRuntime.wrap((function(r){while(1)switch(r.prev=r.next){case 0:return e||(t.loading=!0),r.prev=1,r.next=4,Promise.all([t.refreshTracks(e),t.refreshStatus(e),t.refreshPlaylists(e)]);case 4:return r.prev=4,t.loading=!1,r.finish(4);case 7:case"end":return r.stop()}}),r,null,[[1,,4,7]])})))()},play:function(e){var t=this;return Object(i["a"])(regeneratorRuntime.mark((function r(){return regeneratorRuntime.wrap((function(r){while(1)switch(r.prev=r.next){case 0:if(null==(null===e||void 0===e?void 0:e.pos)){r.next=5;break}return r.next=3,t.request("music.mpd.play_pos",{pos:e.pos});case 3:r.next=12;break;case 5:if(null===e||void 0===e||!e.file){r.next=10;break}return r.next=8,t.request("music.mpd.play",{resource:e.file});case 8:r.next=12;break;case 10:return r.next=12,t.request("music.mpd.play");case 12:return r.next=14,t.refreshStatus(!0);case 14:case"end":return r.stop()}}),r)})))()},pause:function(){var e=this;return Object(i["a"])(regeneratorRuntime.mark((function t(){return regeneratorRuntime.wrap((function(t){while(1)switch(t.prev=t.next){case 0:return t.next=2,e.request("music.mpd.pause");case 2:return t.next=4,e.refreshStatus(!0);case 4:case"end":return t.stop()}}),t)})))()},stop:function(){var e=this;return Object(i["a"])(regeneratorRuntime.mark((function t(){return regeneratorRuntime.wrap((function(t){while(1)switch(t.prev=t.next){case 0:return t.next=2,e.request("music.mpd.stop");case 2:return t.next=4,e.refreshStatus(!0);case 4:case"end":return t.stop()}}),t)})))()},previous:function(){var e=this;return Object(i["a"])(regeneratorRuntime.mark((function t(){return regeneratorRuntime.wrap((function(t){while(1)switch(t.prev=t.next){case 0:return t.next=2,e.request("music.mpd.previous");case 2:return t.next=4,e.refreshStatus(!0);case 4:case"end":return t.stop()}}),t)})))()},next:function(){var e=this;return Object(i["a"])(regeneratorRuntime.mark((function t(){return regeneratorRuntime.wrap((function(t){while(1)switch(t.prev=t.next){case 0:return t.next=2,e.request("music.mpd.next");case 2:return t.next=4,e.refreshStatus(!0);case 4:case"end":return t.stop()}}),t)})))()},clear:function(){var e=this;return Object(i["a"])(regeneratorRuntime.mark((function t(){return regeneratorRuntime.wrap((function(t){while(1)switch(t.prev=t.next){case 0:return t.next=2,e.request("music.mpd.clear");case 2:return t.next=4,Promise.all([e.refreshStatus(!0),e.refreshTracks(!0)]);case 4:case"end":return t.stop()}}),t)})))()},setVolume:function(e){var t=this;return Object(i["a"])(regeneratorRuntime.mark((function r(){return regeneratorRuntime.wrap((function(r){while(1)switch(r.prev=r.next){case 0:if(e!==t.status.volume){r.next=2;break}return r.abrupt("return");case 2:return r.next=4,t.request("music.mpd.set_volume",{volume:e});case 4:return r.next=6,t.refreshStatus(!0);case 6:case"end":return r.stop()}}),r)})))()},seek:function(e){var t=this;return Object(i["a"])(regeneratorRuntime.mark((function r(){return regeneratorRuntime.wrap((function(r){while(1)switch(r.prev=r.next){case 0:return r.next=2,t.request("music.mpd.seek",{position:e});case 2:return r.next=4,t.refreshStatus(!0);case 4:case"end":return r.stop()}}),r)})))()},repeat:function(e){var t=this;return Object(i["a"])(regeneratorRuntime.mark((function r(){return regeneratorRuntime.wrap((function(r){while(1)switch(r.prev=r.next){case 0:return r.next=2,t.request("music.mpd.repeat",{value:parseInt(+e)});case 2:return r.next=4,t.refreshStatus(!0);case 4:case"end":return r.stop()}}),r)})))()},random:function(e){var t=this;return Object(i["a"])(regeneratorRuntime.mark((function r(){return regeneratorRuntime.wrap((function(r){while(1)switch(r.prev=r.next){case 0:return r.next=2,t.request("music.mpd.random",{value:parseInt(+e)});case 2:return r.next=4,t.refreshStatus(!0);case 4:case"end":return r.stop()}}),r)})))()},consume:function(e){var t=this;return Object(i["a"])(regeneratorRuntime.mark((function r(){return regeneratorRuntime.wrap((function(r){while(1)switch(r.prev=r.next){case 0:return r.next=2,t.request("music.mpd.consume",{value:parseInt(+e)});case 2:return r.next=4,t.refreshStatus(!0);case 4:case"end":return r.stop()}}),r)})))()},addToTracklist:function(e){var t=this;return Object(i["a"])(regeneratorRuntime.mark((function r(){return regeneratorRuntime.wrap((function(r){while(1)switch(r.prev=r.next){case 0:return e.file&&(e=e.file),r.next=3,t.request("music.mpd.add",{resource:e});case 3:return r.next=5,t.refresh(!0);case 5:case"end":return r.stop()}}),r)})))()},addToTracklistFromEditedPlaylist:function(e){var t=this;return Object(i["a"])(regeneratorRuntime.mark((function r(){var n;return regeneratorRuntime.wrap((function(r){while(1)switch(r.prev=r.next){case 0:if(n=t.editedPlaylistTracks[e.pos],n){r.next=3;break}return r.abrupt("return");case 3:return r.next=5,t.request("music.mpd.add",{resource:n.file});case 5:return r.next=7,t.refresh(!0);case 7:if(!e.play){r.next=10;break}return r.next=10,t.request("music.mpd.play_pos",{pos:t.tracks.length-1});case 10:case"end":return r.stop()}}),r)})))()},removeFromPlaylist:function(e){var t=this;return Object(i["a"])(regeneratorRuntime.mark((function r(){return regeneratorRuntime.wrap((function(r){while(1)switch(r.prev=r.next){case 0:return r.next=2,t.request("music.mpd.playlistdelete",{pos:e,name:t.playlists[t.editedPlaylist].name});case 2:return r.next=4,t.playlistEditChanged(t.editedPlaylist);case 4:case"end":return r.stop()}}),r)})))()},removeFromTracklist:function(e){var t=this;return Object(i["a"])(regeneratorRuntime.mark((function r(){return regeneratorRuntime.wrap((function(r){while(1)switch(r.prev=r.next){case 0:return r.next=2,t.request("music.mpd.delete",{positions:e.sort()});case 2:return r.next=4,t.refresh(!0);case 4:case"end":return r.stop()}}),r)})))()},swapTracks:function(e){var t=this;return Object(i["a"])(regeneratorRuntime.mark((function r(){return regeneratorRuntime.wrap((function(r){while(1)switch(r.prev=r.next){case 0:return r.next=2,t.request("music.mpd.move",{from_pos:e[0],to_pos:e[1]});case 2:return r.next=4,t.refresh(!0);case 4:case"end":return r.stop()}}),r)})))()},playPlaylist:function(e){var t=this;return Object(i["a"])(regeneratorRuntime.mark((function r(){return regeneratorRuntime.wrap((function(r){while(1)switch(r.prev=r.next){case 0:return r.next=2,t._loadPlaylist(e,!0);case 2:case"end":return r.stop()}}),r)})))()},loadPlaylist:function(e){var t=this;return Object(i["a"])(regeneratorRuntime.mark((function r(){return regeneratorRuntime.wrap((function(r){while(1)switch(r.prev=r.next){case 0:return r.next=2,t._loadPlaylist(e,!1);case 2:case"end":return r.stop()}}),r)})))()},_loadPlaylist:function(e,t){var r=this;return Object(i["a"])(regeneratorRuntime.mark((function n(){var a;return regeneratorRuntime.wrap((function(n){while(1)switch(n.prev=n.next){case 0:return a=r.playlists[e],n.next=3,r.request("music.mpd.load",{playlist:a.name,play:t});case 3:return n.next=5,r.refresh(!0);case 5:case"end":return n.stop()}}),n)})))()},removePlaylist:function(e){var t=this;return Object(i["a"])(regeneratorRuntime.mark((function r(){var n;return regeneratorRuntime.wrap((function(r){while(1)switch(r.prev=r.next){case 0:if(n=t.playlists[e],confirm("Are you REALLY sure that you want to remove the playlist ".concat(n.name,"?"))){r.next=3;break}return r.abrupt("return");case 3:return r.next=5,t.request("music.mpd.rm",{playlist:n.name});case 5:return r.next=7,t.refreshPlaylists(!0);case 7:case"end":return r.stop()}}),r)})))()},saveToPlaylist:function(e){var t=this;return Object(i["a"])(regeneratorRuntime.mark((function r(){return regeneratorRuntime.wrap((function(r){while(1)switch(r.prev=r.next){case 0:return r.next=2,t.request("music.mpd.save",{name:e});case 2:return r.next=4,t.refreshPlaylists(!0);case 4:case"end":return r.stop()}}),r)})))()},moveTracklistTracks:function(e){var t=this;return Object(i["a"])(regeneratorRuntime.mark((function r(){return regeneratorRuntime.wrap((function(r){while(1)switch(r.prev=r.next){case 0:return r.next=2,t.request("music.mpd.move",{from_pos:e.from,to_pos:e.to});case 2:return r.next=4,t.refreshTracks(!0);case 4:case"end":return r.stop()}}),r)})))()},playlistAdd:function(e){var t=this;return Object(i["a"])(regeneratorRuntime.mark((function r(){return regeneratorRuntime.wrap((function(r){while(1)switch(r.prev=r.next){case 0:return r.next=2,t.request("music.mpd.playlistadd",{uri:e,name:t.playlists[t.editedPlaylist].name});case 2:return r.next=4,t.playlistEditChanged(t.editedPlaylist);case 4:case"end":return r.stop()}}),r)})))()},playlistEditChanged:function(e){var t=this;return Object(i["a"])(regeneratorRuntime.mark((function r(){return regeneratorRuntime.wrap((function(r){while(1)switch(r.prev=r.next){case 0:if(t.editedPlaylist=e,null!=e){r.next=3;break}return r.abrupt("return");case 3:return t.loading=!0,r.prev=4,r.next=7,t.request("music.mpd.listplaylistinfo",{name:t.playlists[e].name});case 7:t.editedPlaylistTracks=r.sent;case 8:return r.prev=8,t.loading=!1,r.finish(8);case 11:case"end":return r.stop()}}),r,null,[[4,,8,11]])})))()},addToPlaylist:function(e){var t=this;return Object(i["a"])(regeneratorRuntime.mark((function r(){return regeneratorRuntime.wrap((function(r){while(1)switch(r.prev=r.next){case 0:return r.next=2,Promise.all(e.playlists.map(function(){var r=Object(i["a"])(regeneratorRuntime.mark((function r(n){return regeneratorRuntime.wrap((function(r){while(1)switch(r.prev=r.next){case 0:return r.next=2,t.request("music.mpd.playlistadd",{uri:e.track.file,name:t.playlists[n].name});case 2:return r.next=4,t.playlistEditChanged(n);case 4:case"end":return r.stop()}}),r)})));return function(e){return r.apply(this,arguments)}}()));case 2:case"end":return r.stop()}}),r)})))()},playlistTrackMove:function(e){var t=this;return Object(i["a"])(regeneratorRuntime.mark((function r(){return regeneratorRuntime.wrap((function(r){while(1)switch(r.prev=r.next){case 0:return r.next=2,t.request("music.mpd.playlistmove",{name:t.playlists[e.playlist].name,from_pos:e.from,to_pos:e.to});case 2:return r.next=4,t.playlistEditChanged(e.playlist);case 4:case"end":return r.stop()}}),r)})))()},search:function(e){var t=this;return Object(i["a"])(regeneratorRuntime.mark((function r(){return regeneratorRuntime.wrap((function(r){while(1)switch(r.prev=r.next){case 0:return t.loading=!0,r.prev=1,r.next=4,t.request("music.mpd.search",{filter:e});case 4:t.searchResults=r.sent;case 5:return r.prev=5,t.loading=!1,r.finish(5);case 8:case"end":return r.stop()}}),r,null,[[1,,5,8]])})))()},cd:function(e){var t=this;return Object(i["a"])(regeneratorRuntime.mark((function r(){return regeneratorRuntime.wrap((function(r){while(1)switch(r.prev=r.next){case 0:return t.loading=!0,r.prev=1,r.next=4,t.request("music.mpd.lsinfo",{uri:e});case 4:t.libraryResults=r.sent.filter((function(e){return!e.playlist})),t.path=e;case 6:return r.prev=6,t.loading=!1,r.finish(6);case 9:case"end":return r.stop()}}),r,null,[[1,,6,9]])})))()}},mounted:function(){this.refresh(),this.cd(this.path)}};l.render=a;t["default"]=l}}]);
//# sourceMappingURL=chunk-2d21da1a.0307564e.js.map