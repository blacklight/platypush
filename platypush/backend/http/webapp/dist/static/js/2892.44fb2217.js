"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[2892,6640],{2892:function(a,e,t){t.r(e),t.d(e,{default:function(){return p}});var n=t(6252);const l={class:"media-file-browser"};function i(a,e,t,i,o,r){const d=(0,n.up)("Loading"),s=(0,n.up)("Browser");return(0,n.wg)(),(0,n.iD)("div",l,[a.loading?((0,n.wg)(),(0,n.j4)(d,{key:0})):((0,n.wg)(),(0,n.j4)(s,{key:1,"is-media":!0,filter:a.filter,"has-back":!0,onBack:e[0]||(e[0]=e=>a.$emit("back")),onPathChange:e[1]||(e[1]=e=>a.$emit("path-change",e)),onPlay:e[2]||(e[2]=e=>a.$emit("play",e))},null,8,["filter"]))])}var o=t(941),r=t(6791),d=t(6640),s={mixins:[d["default"]],components:{Browser:o.Z,Loading:r.Z}},u=t(3744);const c=(0,u.Z)(s,[["render",i],["__scopeId","data-v-5f4a36da"]]);var p=c},6640:function(a,e,t){t.r(e),t.d(e,{default:function(){return o}});var n=t(8637),l={mixins:[n.Z],emits:["add-to-playlist","back","create-playlist","download","download-audio","path-change","play","remove-from-playlist","remove-playlist","rename-playlist"],props:{filter:{type:String,default:""},loading:{type:Boolean,default:!1},selectedPlaylist:{default:null},selectedChannel:{default:null}},data(){return{loading_:!1}},computed:{isLoading(){return this.loading||this.loading_}}};const i=l;var o=i}}]);
//# sourceMappingURL=2892.44fb2217.js.map