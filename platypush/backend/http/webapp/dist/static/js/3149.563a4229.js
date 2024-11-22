"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[3149],{8692:function(t,e,i){i.d(e,{A:function(){return c}});var s=i(641),l=i(33);const n=["innerHTML"];function a(t,e,i,a,o,r){return(0,s.uX)(),(0,s.CE)("div",{class:(0,l.C4)(["dragged",{hidden:!r.draggingVisible}]),style:(0,l.Tr)({top:`${o.top}px`,left:`${o.left}px`})},[r.draggingVisible?((0,s.uX)(),(0,s.CE)("div",{key:0,class:"content",innerHTML:i.element?.outerHTML||"..."},null,8,n)):(0,s.Q3)("",!0)],6)}var o={emits:["contextmenu","drag","dragend","drop"],props:{disabled:{type:Boolean,default:!1},element:{type:Object},touchDragStartThreshold:{type:Number,default:500},touchDragMoveCancelDistance:{type:Number,default:10},value:{type:[Object,String,Number,Boolean,Array],default:()=>({})}},data(){return{dragging:!1,draggingHTML:null,eventsHandlers:{contextmenu:this.onContextMenu,drag:this.onDrag,dragend:this.onDragEnd,dragstart:this.onDragStart,drop:this.onDragEnd,touchcancel:this.onDragEnd,touchend:this.onTouchEnd,touchmove:this.onTouchMove,touchstart:this.onTouchStart},initialCursorOffset:null,left:0,top:0,touchDragStartTimer:null,touchScrollDirection:[0,0],touchScrollSpeed:10,touchScrollTimer:null,touchStart:null,touchOverElement:null}},computed:{draggingVisible(){return this.dragging&&this.touchStart},shouldScroll(){return this.touchScrollDirection[0]||this.touchScrollDirection[1]}},methods:{onContextMenu(t){!this.disabled&&this.touchStart?(t.preventDefault(),t.stopPropagation(),this.onDragStart(t)):this.$emit("contextmenu",t)},onDragStart(t){this.disabled||(this.dragging=!0,this.draggingHTML=this.$slots.default?.()?.el?.outerHTML,t.value=this.value,t.dataTransfer&&(t.dataTransfer.dropEffect="move",t.dataTransfer.effectAllowed="move",t.dataTransfer.setData("application/json",JSON.stringify(this.value))),this.cancelTouchDragStart(),this.$emit("drag",t))},onDragEnd(t){this.disabled||(this.reset(),this.$emit("dragend",t))},onTouchStart(t){if(this.disabled)return;const e=t.touches?.[0];e&&(this.touchStart=[e.clientX,e.clientY],this.cancelTouchDragStart(),this.touchDragStartTimer=setTimeout((()=>{this.onDragStart(t)}),this.touchDragStartThreshold))},onTouchMove(t){if(this.disabled)return;const e=t.touches?.[0];if(!e||!this.touchStart)return;if(this.touchDragStartTimer){const i=Math.hypot(e.clientX-this.touchStart[0],e.clientY-this.touchStart[1]);if(i>this.touchDragMoveCancelDistance)return void this.reset();this.onDragStart(t)}t.preventDefault();const{clientX:i,clientY:s}=e;this.left=i,this.top=s,this.left=i-this.touchStart[0],this.top=s-this.touchStart[1],this.touchScroll(t);let l=document.elementsFromPoint(i,s).filter((t=>t.dataset?.droppable&&!t.classList.contains("dragged")))?.[0];l?(this.dispatchEvent("dragenter",l),this.touchOverElement=l):this.touchOverElement=null},touchScroll(t){if(this.disabled)return;const e=this.getScrollableParent();if(!e)return;const i=t.touches?.[0];if(!i)return;const{clientX:s,clientY:l}=i,n=e.getBoundingClientRect(),a=[(s-n.left)/n.width,(l-n.top)/n.height],o=[0,0];a[0]<0?o[0]=-1:a[0]>1&&(o[0]=1),a[1]<0?o[1]=-1:a[1]>1&&(o[1]=1),this.handleTouchScroll(o,e)},onTouchEnd(t){if(this.disabled)return;const e=this.touchOverElement;e&&this.dispatchEvent("drop",e),this.onDragEnd(t)},handleTouchScroll(t,e){this.touchScrollDirection=t,t[0]||t[1]?this.touchScrollTimer||(this.touchScrollTimer=setInterval((()=>{if(!e)return;const[i,s]=t;e.scrollBy(i*this.touchScrollSpeed,s*this.touchScrollSpeed)}),1e3/60)):this.cancelScroll()},getScrollableParent(){let t=this.element?.parentElement;while(t){if(t.scrollHeight>t.clientHeight||t.scrollWidth>t.clientWidth){const e=window.getComputedStyle(t);if(["scroll","auto"].includes(e.overflowY)||["scroll","auto"].includes(e.overflowX))return t}t=t.parentElement}return null},dispatchEvent(t,e){e.dispatchEvent(new DragEvent(t,{target:{...e,value:this.value}}))},cancelScroll(){this.touchScrollDirection=[0,0],this.touchScrollTimer&&(clearInterval(this.touchScrollTimer),this.touchScrollTimer=null)},cancelTouchDragStart(){this.touchDragStartTimer&&(clearTimeout(this.touchDragStartTimer),this.touchDragStartTimer=null)},reset(){this.cancelTouchDragStart(),this.cancelScroll(),this.dragging=!1,this.touchStart=null,this.touchOverElement=null,this.left=0,this.top=0,this.initialCursorOffset=null},installHandlers(){console.debug("Installing drag handlers on",this.element),this.element?.setAttribute("draggable",!0),Object.entries(this.eventsHandlers).forEach((([t,e])=>{this.element?.addEventListener(t,e)}))},uninstallHandlers(){console.debug("Uninstalling drag handlers from",this.element),this.element?.setAttribute("draggable",!1),Object.entries(this.eventsHandlers).forEach((([t,e])=>{this.element?.removeEventListener(t,e)}))}},watch:{dragging(){this.dragging?(this.element?.classList.add("dragged"),this.$nextTick((()=>{this.touchStart&&(this.initialCursorOffset=[this.element?.offsetLeft-this.touchStart[0],this.element?.offsetTop-this.touchStart[1]])}))):this.element?.classList.remove("dragged")},disabled(t){t?(this.reset(),this.uninstallHandlers()):this.installHandlers()},element(){this.uninstallHandlers(),this.installHandlers()},touchOverElement(t,e){t!==e&&(e&&this.dispatchEvent("dragleave",e),t&&this.dispatchEvent("dragenter",t))}},mounted(){this.installHandlers()},unmounted(){this.uninstallHandlers()}},r=i(6262);const d=(0,r.A)(o,[["render",a],["__scopeId","data-v-dd2759da"]]);var c=d},3118:function(t,e,i){i.d(e,{A:function(){return d}});var s=i(641);const l={class:"droppable"};function n(t,e,i,n,a,o){return(0,s.uX)(),(0,s.CE)("div",l)}var a={emits:["dragenter","dragleave","dragover","drop"],props:{element:{type:Object},active:{type:Boolean,default:!1},disabled:{type:Boolean,default:!1}},data(){return{eventsHandlers:{dragenter:this.onDragEnter,dragleave:this.onDragLeave,dragover:this.onDragOver,drop:this.onDrop},selected:!1}},methods:{onDragEnter(t){this.disabled||this.selected||(this.selected=!0,this.$emit("dragenter",t))},onDragLeave(t){if(this.disabled||!this.selected)return;const e=this.element.getBoundingClientRect();t.clientX>=e.left&&t.clientX<=e.right&&t.clientY>=e.top&&t.clientY<=e.bottom||(this.selected=!1,this.$emit("dragleave",t))},onDragOver(t){this.disabled||(t.preventDefault(),this.selected=!0,this.$emit("dragover",t))},onDrop(t){this.disabled||(this.selected=!1,this.$emit("drop",t))},installHandlers(){const t=this.element;t&&(console.debug("Installing drop handlers on",this.element),t.dataset&&(t.dataset.droppable=!0),t.addEventListener&&Object.entries(this.eventsHandlers).forEach((([e,i])=>{t.addEventListener(e,i)})))},uninstallHandlers(){const t=this.element;t&&(console.debug("Uninstalling drop handlers from",this.element),t.dataset?.droppable&&delete t.dataset.droppable,t.removeEventListener&&Object.entries(this.eventsHandlers).forEach((([e,i])=>{t.removeEventListener(e,i)})))}},watch:{active(){this.active?this.element?.classList.add("active"):this.element?.classList.remove("active")},disabled:{handler(){this.disabled?this.element?.classList.add("disabled"):this.element?.classList.remove("disabled")}},element:{handler(){this.uninstallHandlers(),this.installHandlers()}},selected:{handler(t,e){t&&!e?this.element?.classList.add("selected"):!t&&e&&this.element?.classList.remove("selected")}}},mounted(){this.$nextTick((()=>{this.installHandlers()}))},unmounted(){this.uninstallHandlers()}},o=i(6262);const r=(0,o.A)(a,[["render",n]]);var d=r},7711:function(t,e,i){i.d(e,{A:function(){return Ht}});var s=i(641),l=i(33);const n={class:"media-info"},a={class:"row header"},o={class:"item-container"},r={key:1,class:"row direct-url"},d={class:"right side"},c=["href"],u={key:2,class:"row duration"},m=["textContent"],h={key:3,class:"row duration"},p=["textContent"],v={key:4,class:"row direct-url"},g={class:"right side"},f=["href"],y={key:5,class:"row"},k=["textContent"],C={key:6,class:"row"},w=["textContent"],L={key:7,class:"row"},b=["textContent"],I={key:8,class:"row"},x=["textContent"],_={key:9,class:"row"},E=["textContent"],D={key:10,class:"row"},S=["textContent"],X={key:11,class:"row"},$=["textContent"],Q={key:12,class:"row"},T=["textContent"],A={key:13,class:"row"},O=["textContent"],R={key:14,class:"row"},M=["textContent"],V={key:15,class:"row"},H=["textContent"],P={key:16,class:"row"},j=["textContent"],U={key:17,class:"row"},B={class:"right side"},W={key:18,class:"row"},N={class:"right side"},F={key:19,class:"row"},Y={class:"right side"},z={key:20,class:"row"},q={class:"right side"},J={key:21,class:"row"},K={class:"right side"},G={key:22,class:"row"},Z=["textContent"],tt={key:23,class:"row"},et=["textContent"],it={key:24,class:"row"},st={class:"right side"},lt=["href","textContent"],nt={key:25,class:"row"},at=["textContent"],ot={key:26,class:"row"},rt=["textContent"],dt={key:27,class:"row"},ct=["textContent"],ut={key:28,class:"row"},mt=["textContent"],ht={key:29,class:"row"},pt={class:"right side url"},vt=["href","textContent"],gt={key:30,class:"row"},ft=["textContent"],yt={key:31,class:"row"},kt=["textContent"],Ct={key:32,class:"row"},wt=["textContent"],Lt={key:33,class:"row"},bt=["textContent"],It={key:34,class:"row"},xt=["textContent"],_t={key:35,class:"row"},Et=["textContent"],Dt={key:36,class:"row"},St=["textContent"];function Xt(t,e,i,Xt,$t,Qt){const Tt=(0,s.g2)("Loading"),At=(0,s.g2)("Item");return(0,s.uX)(),(0,s.CE)("div",n,[$t.loading?((0,s.uX)(),(0,s.Wv)(Tt,{key:0})):(0,s.Q3)("",!0),(0,s.Lk)("div",a,[(0,s.Lk)("div",o,[(0,s.bF)(At,{item:i.item,onAddToPlaylist:e[0]||(e[0]=e=>t.$emit("add-to-playlist",i.item)),onOpenChannel:e[1]||(e[1]=e=>t.$emit("open-channel",i.item)),onPlay:e[2]||(e[2]=e=>t.$emit("play",i.item)),onPlayWithOpts:e[3]||(e[3]=e=>t.$emit("play-with-opts",e)),onDownload:e[4]||(e[4]=e=>t.$emit("download",i.item)),onDownloadAudio:e[5]||(e[5]=e=>t.$emit("download-audio",i.item))},null,8,["item"])])]),Qt.mainUrl?((0,s.uX)(),(0,s.CE)("div",r,[e[10]||(e[10]=(0,s.Lk)("div",{class:"left side"},"Direct URL",-1)),(0,s.Lk)("div",d,[(0,s.Lk)("a",{href:Qt.mainUrl,title:"Direct URL",target:"_blank"},e[8]||(e[8]=[(0,s.Lk)("i",{class:"fas fa-external-link-alt"},null,-1)]),8,c),(0,s.Lk)("button",{onClick:e[6]||(e[6]=e=>t.copyToClipboard(Qt.mainUrl)),title:"Copy URL to clipboard"},e[9]||(e[9]=[(0,s.Lk)("i",{class:"fas fa-clipboard"},null,-1)]))])])):(0,s.Q3)("",!0),Qt.computedItem?.duration?((0,s.uX)(),(0,s.CE)("div",u,[e[11]||(e[11]=(0,s.Lk)("div",{class:"left side"},"Duration",-1)),(0,s.Lk)("div",{class:"right side",textContent:(0,l.v_)(t.formatDuration(Qt.computedItem.duration,!0))},null,8,m)])):(0,s.Q3)("",!0),null!=Qt.computedItem?.n_items?((0,s.uX)(),(0,s.CE)("div",h,[e[12]||(e[12]=(0,s.Lk)("div",{class:"left side"},"Items",-1)),(0,s.Lk)("div",{class:"right side",textContent:(0,l.v_)(Qt.computedItem.n_items)},null,8,p)])):(0,s.Q3)("",!0),Qt.computedItem?.imdb_url?((0,s.uX)(),(0,s.CE)("div",v,[e[15]||(e[15]=(0,s.Lk)("div",{class:"left side"},"ImDB URL",-1)),(0,s.Lk)("div",g,[(0,s.Lk)("a",{href:Qt.computedItem.imdb_url,title:"ImDB URL",target:"_blank"},e[13]||(e[13]=[(0,s.Lk)("i",{class:"fas fa-external-link-alt"},null,-1)]),8,f),(0,s.Lk)("button",{onClick:e[7]||(e[7]=e=>t.copyToClipboard(Qt.computedItem.imdb_url)),title:"Copy URL to clipboard"},e[14]||(e[14]=[(0,s.Lk)("i",{class:"fas fa-clipboard"},null,-1)]))])])):(0,s.Q3)("",!0),Qt.computedItem?.artist?.name?((0,s.uX)(),(0,s.CE)("div",y,[e[16]||(e[16]=(0,s.Lk)("div",{class:"left side"},"Artist",-1)),(0,s.Lk)("div",{class:"right side",textContent:(0,l.v_)(Qt.computedItem.artist.name)},null,8,k)])):(0,s.Q3)("",!0),Qt.computedItem?.album?.name?((0,s.uX)(),(0,s.CE)("div",C,[e[17]||(e[17]=(0,s.Lk)("div",{class:"left side"},"Album",-1)),(0,s.Lk)("div",{class:"right side",textContent:(0,l.v_)(Qt.computedItem.album.name)},null,8,w)])):(0,s.Q3)("",!0),Qt.computedItem?.series?((0,s.uX)(),(0,s.CE)("div",L,[e[18]||(e[18]=(0,s.Lk)("div",{class:"left side"},"TV Series",-1)),(0,s.Lk)("div",{class:"right side",textContent:(0,l.v_)(Qt.computedItem.series)},null,8,b)])):(0,s.Q3)("",!0),Qt.computedItem?.season?((0,s.uX)(),(0,s.CE)("div",I,[e[19]||(e[19]=(0,s.Lk)("div",{class:"left side"},"Season",-1)),(0,s.Lk)("div",{class:"right side",textContent:(0,l.v_)(Qt.computedItem.season)},null,8,x)])):(0,s.Q3)("",!0),Qt.computedItem?.episode?((0,s.uX)(),(0,s.CE)("div",_,[e[20]||(e[20]=(0,s.Lk)("div",{class:"left side"},"Episode",-1)),(0,s.Lk)("div",{class:"right side",textContent:(0,l.v_)(Qt.computedItem.episode)},null,8,E)])):(0,s.Q3)("",!0),Qt.computedItem?.num_seasons?((0,s.uX)(),(0,s.CE)("div",D,[e[21]||(e[21]=(0,s.Lk)("div",{class:"left side"},"Number of seasons",-1)),(0,s.Lk)("div",{class:"right side",textContent:(0,l.v_)(Qt.computedItem.num_seasons)},null,8,S)])):(0,s.Q3)("",!0),Qt.computedItem?.description?((0,s.uX)(),(0,s.CE)("div",X,[e[22]||(e[22]=(0,s.Lk)("div",{class:"left side"},"Description",-1)),(0,s.Lk)("div",{class:"right side",textContent:(0,l.v_)(Qt.computedItem.description)},null,8,$)])):(0,s.Q3)("",!0),Qt.computedItem?.summary?((0,s.uX)(),(0,s.CE)("div",Q,[e[23]||(e[23]=(0,s.Lk)("div",{class:"left side"},"Summary",-1)),(0,s.Lk)("div",{class:"right side",textContent:(0,l.v_)(Qt.computedItem.summary)},null,8,T)])):(0,s.Q3)("",!0),Qt.computedItem?.overview?((0,s.uX)(),(0,s.CE)("div",A,[e[24]||(e[24]=(0,s.Lk)("div",{class:"left side"},"Overview",-1)),(0,s.Lk)("div",{class:"right side",textContent:(0,l.v_)(Qt.computedItem.overview)},null,8,O)])):(0,s.Q3)("",!0),Qt.computedItem?.country?((0,s.uX)(),(0,s.CE)("div",R,[e[25]||(e[25]=(0,s.Lk)("div",{class:"left side"},"Country",-1)),(0,s.Lk)("div",{class:"right side",textContent:(0,l.v_)(Qt.computedItem.country)},null,8,M)])):(0,s.Q3)("",!0),Qt.computedItem?.network?((0,s.uX)(),(0,s.CE)("div",V,[e[26]||(e[26]=(0,s.Lk)("div",{class:"left side"},"Network",-1)),(0,s.Lk)("div",{class:"right side",textContent:(0,l.v_)(Qt.computedItem.network)},null,8,H)])):(0,s.Q3)("",!0),Qt.computedItem?.status?((0,s.uX)(),(0,s.CE)("div",P,[e[27]||(e[27]=(0,s.Lk)("div",{class:"left side"},"Status",-1)),(0,s.Lk)("div",{class:"right side",textContent:(0,l.v_)(Qt.computedItem.status)},null,8,j)])):(0,s.Q3)("",!0),Qt.computedItem?.width&&Qt.computedItem?.height?((0,s.uX)(),(0,s.CE)("div",U,[e[28]||(e[28]=(0,s.Lk)("div",{class:"left side"},"Resolution",-1)),(0,s.Lk)("div",B,(0,l.v_)(Qt.computedItem.width)+"x"+(0,l.v_)(Qt.computedItem.height),1)])):(0,s.Q3)("",!0),null!=Qt.computedItem?.view_count?((0,s.uX)(),(0,s.CE)("div",W,[e[29]||(e[29]=(0,s.Lk)("div",{class:"left side"},"Views",-1)),(0,s.Lk)("div",N,(0,l.v_)(t.formatNumber(Qt.computedItem.view_count)),1)])):(0,s.Q3)("",!0),Qt.computedItem?.rating?((0,s.uX)(),(0,s.CE)("div",F,[e[30]||(e[30]=(0,s.Lk)("div",{class:"left side"},"Rating",-1)),(0,s.Lk)("div",Y,(0,l.v_)(Math.round(Qt.computedItem.rating))+"%",1)])):(0,s.Q3)("",!0),Qt.computedItem?.critic_rating?((0,s.uX)(),(0,s.CE)("div",z,[e[31]||(e[31]=(0,s.Lk)("div",{class:"left side"},"Critic Rating",-1)),(0,s.Lk)("div",q,(0,l.v_)(Math.round(Qt.computedItem.critic_rating))+"%",1)])):(0,s.Q3)("",!0),Qt.computedItem?.community_rating?((0,s.uX)(),(0,s.CE)("div",J,[e[32]||(e[32]=(0,s.Lk)("div",{class:"left side"},"Community Rating",-1)),(0,s.Lk)("div",K,(0,l.v_)(Math.round(Qt.computedItem.community_rating))+"%",1)])):(0,s.Q3)("",!0),Qt.computedItem?.votes?((0,s.uX)(),(0,s.CE)("div",G,[e[33]||(e[33]=(0,s.Lk)("div",{class:"left side"},"Votes",-1)),(0,s.Lk)("div",{class:"right side",textContent:(0,l.v_)(Qt.computedItem.votes)},null,8,Z)])):(0,s.Q3)("",!0),Qt.computedItem?.genres?.length?((0,s.uX)(),(0,s.CE)("div",tt,[e[34]||(e[34]=(0,s.Lk)("div",{class:"left side"},"Genres",-1)),(0,s.Lk)("div",{class:"right side",textContent:(0,l.v_)(Qt.computedItem.genres.join(", "))},null,8,et)])):(0,s.Q3)("",!0),Qt.channel?((0,s.uX)(),(0,s.CE)("div",it,[e[35]||(e[35]=(0,s.Lk)("div",{class:"left side"},"Channel",-1)),(0,s.Lk)("div",st,[(0,s.Lk)("a",{href:Qt.channel.url,target:"_blank",textContent:(0,l.v_)(Qt.channel.title||Qt.channel.url)},null,8,lt)])])):(0,s.Q3)("",!0),Qt.computedItem?.year?((0,s.uX)(),(0,s.CE)("div",nt,[e[36]||(e[36]=(0,s.Lk)("div",{class:"left side"},"Year",-1)),(0,s.Lk)("div",{class:"right side",textContent:(0,l.v_)(Qt.computedItem.year)},null,8,at)])):(0,s.Q3)("",!0),Qt.publishedDate?((0,s.uX)(),(0,s.CE)("div",ot,[e[37]||(e[37]=(0,s.Lk)("div",{class:"left side"},"Published at",-1)),(0,s.Lk)("div",{class:"right side",textContent:(0,l.v_)(Qt.publishedDate)},null,8,rt)])):(0,s.Q3)("",!0),Qt.computedItem?.file?((0,s.uX)(),(0,s.CE)("div",dt,[e[38]||(e[38]=(0,s.Lk)("div",{class:"left side"},"File",-1)),(0,s.Lk)("div",{class:"right side",textContent:(0,l.v_)(Qt.computedItem.file)},null,8,ct)])):(0,s.Q3)("",!0),null!=Qt.computedItem?.track_number?((0,s.uX)(),(0,s.CE)("div",ut,[e[39]||(e[39]=(0,s.Lk)("div",{class:"left side"},"Track",-1)),(0,s.Lk)("div",{class:"right side",textContent:(0,l.v_)(Qt.computedItem.track_number)},null,8,mt)])):(0,s.Q3)("",!0),Qt.computedItem?.trailer?((0,s.uX)(),(0,s.CE)("div",ht,[e[40]||(e[40]=(0,s.Lk)("div",{class:"left side"},"Trailer",-1)),(0,s.Lk)("div",pt,[(0,s.Lk)("a",{href:Qt.computedItem.trailer,target:"_blank",textContent:(0,l.v_)(Qt.computedItem.trailer)},null,8,vt)])])):(0,s.Q3)("",!0),Qt.computedItem?.size?((0,s.uX)(),(0,s.CE)("div",gt,[e[41]||(e[41]=(0,s.Lk)("div",{class:"left side"},"Size",-1)),(0,s.Lk)("div",{class:"right side",textContent:(0,l.v_)(t.convertSize(Qt.computedItem.size))},null,8,ft)])):(0,s.Q3)("",!0),Qt.computedItem?.quality?((0,s.uX)(),(0,s.CE)("div",yt,[e[42]||(e[42]=(0,s.Lk)("div",{class:"left side"},"Quality",-1)),(0,s.Lk)("div",{class:"right side",textContent:(0,l.v_)(Qt.computedItem.quality)},null,8,kt)])):(0,s.Q3)("",!0),Qt.computedItem?.seeds?((0,s.uX)(),(0,s.CE)("div",Ct,[e[43]||(e[43]=(0,s.Lk)("div",{class:"left side"},"Seeds",-1)),(0,s.Lk)("div",{class:"right side",textContent:(0,l.v_)(Qt.computedItem.seeds)},null,8,wt)])):(0,s.Q3)("",!0),Qt.computedItem?.peers?((0,s.uX)(),(0,s.CE)("div",Lt,[e[44]||(e[44]=(0,s.Lk)("div",{class:"left side"},"Peers",-1)),(0,s.Lk)("div",{class:"right side",textContent:(0,l.v_)(Qt.computedItem.peers)},null,8,bt)])):(0,s.Q3)("",!0),Qt.computedItem?.tags?.length?((0,s.uX)(),(0,s.CE)("div",It,[e[45]||(e[45]=(0,s.Lk)("div",{class:"left side"},"Tags",-1)),(0,s.Lk)("div",{class:"right side",textContent:(0,l.v_)(Qt.computedItem.tags.join(", "))},null,8,xt)])):(0,s.Q3)("",!0),Qt.computedItem?.language?((0,s.uX)(),(0,s.CE)("div",_t,[e[46]||(e[46]=(0,s.Lk)("div",{class:"left side"},"Language",-1)),(0,s.Lk)("div",{class:"right side",textContent:(0,l.v_)(Qt.computedItem.language)},null,8,Et)])):(0,s.Q3)("",!0),Qt.computedItem?.audio_channels?((0,s.uX)(),(0,s.CE)("div",Dt,[e[47]||(e[47]=(0,s.Lk)("div",{class:"left side"},"Audio Channels",-1)),(0,s.Lk)("div",{class:"right side",textContent:(0,l.v_)(Qt.computedItem.audio_channels)},null,8,St)])):(0,s.Q3)("",!0)])}var $t=i(9115),Qt=i(6382),Tt=i(9828),At=i(226),Ot=i(2002),Rt={name:"Info",components:{Item:Qt.A,Loading:Tt.A},mixins:[Ot.A,At.A],emits:["add-to-playlist","download","download-audio","open-channel","play","play-with-opts"],props:{item:{type:Object,default:()=>{}},pluginName:{type:String}},data(){return{typeIcons:$t,loading:!1,loadingUrl:!1,youtubeUrl:null,metadata:null}},computed:{channel(){let t=null;return this.item?.channelId?t={url:`https://www.youtube.com/channel/${this.item.channelId}`}:this.item?.channel_url&&(t={url:this.item.channel_url}),t?(this.item?.channelTitle?t.title=this.item.channelTitle:this.item?.channel&&(t.title=this.item.channel),t):null},computedItem(){return{...this.item||{},...this.metadata||{}}},publishedDate(){return this.item?.publishedAt?this.formatDate(this.item.publishedAt,!0):this.item?.created_at?this.formatDate(this.item.created_at,!0):this.item?.timestamp?this.formatDate(this.item.timestamp,!0):null},directUrl(){if("file"===this.item?.type&&this.item?.url){const t=this.item.url.replace(/^file:\/\//,"");return window.location.origin+"/file?path="+encodeURIComponent(t)}return null},mainUrl(){const t=this.directUrl;return t||this.item?.url}},methods:{async updateMetadata(){this.loading=!0;try{"jellyfin"===this.item?.type&&this.item?.id&&(this.metadata=await this.request("media.jellyfin.info",{item_id:this.item.id}))}finally{this.loading=!1}}},watch:{item:{handler(){this.updateMetadata()},deep:!0}},mounted(){this.updateMetadata()}},Mt=i(6262);const Vt=(0,Mt.A)(Rt,[["render",Xt],["__scopeId","data-v-3f7da956"]]);var Ht=Vt},6382:function(t,e,i){i.d(e,{A:function(){return H}});var s=i(641),l=i(33),n=i(3751);const a={key:0,class:"thumbnail"},o={class:"body"},r={class:"row title"},d={key:0,class:"track-number"},c={key:1,class:"track-number"},u={class:"artist-and-title"},m={key:0,class:"artist"},h={class:"title"},p={key:0,class:"duration"},v=["textContent"],g={class:"actions"},f={key:0,class:"row subtitle"},y=["src"],k=["textContent"],C={key:1,class:"row creation-date"},w=["textContent"],L={key:3,class:"row ratings"},b={key:0,class:"rating",title:"Critic rating"},I=["textContent"],x={key:1,class:"rating",title:"Community rating"},_=["textContent"],E={key:1,class:"photo-container"},D=["src"];function S(t,e,i,S,X,$){const Q=(0,s.g2)("MediaImage"),T=(0,s.g2)("DropdownItem"),A=(0,s.g2)("Dropdown"),O=(0,s.g2)("Modal");return i.hidden?(0,s.Q3)("",!0):((0,s.uX)(),(0,s.CE)("div",{key:0,ref:"item",class:(0,l.C4)(["item media-item",{selected:i.selected,list:i.listView}]),onContextmenu:e[5]||(e[5]=(0,n.D$)(((...t)=>$.onContextClick&&$.onContextClick(...t)),["right"]))},[i.listView?(0,s.Q3)("",!0):((0,s.uX)(),(0,s.CE)("div",a,[(0,s.bF)(Q,{item:i.item,onPlay:e[0]||(e[0]=e=>t.$emit("play")),onSelect:$.onMediaSelect},null,8,["item","onSelect"])])),(0,s.Lk)("div",o,[(0,s.Lk)("div",r,[(0,s.Lk)("div",{class:(0,l.C4)(["left side",{"col-11":!i.listView,"col-10":i.listView}]),onClick:e[1]||(e[1]=(0,n.D$)((e=>t.$emit("select")),["stop"]))},[$.playlistView?((0,s.uX)(),(0,s.CE)("span",d,(0,l.v_)(i.index+1),1)):i.listView&&i.item.track_number?((0,s.uX)(),(0,s.CE)("span",c,(0,l.v_)(i.item.track_number),1)):(0,s.Q3)("",!0),(0,s.Lk)("div",u,[$.playlistView&&i.item.artist?((0,s.uX)(),(0,s.CE)("span",m,(0,l.v_)(i.item.artist.name??i.item.artist),1)):(0,s.Q3)("",!0),(0,s.Lk)("span",h,(0,l.v_)(i.item.title||i.item.name),1)])],2),(0,s.Lk)("div",{class:(0,l.C4)(["right side",{"col-1":!i.listView,"col-2":i.listView}])},[i.item.duration&&i.listView?((0,s.uX)(),(0,s.CE)("span",p,[(0,s.Lk)("span",{textContent:(0,l.v_)(t.formatDuration(i.item.duration,!0))},null,8,v)])):(0,s.Q3)("",!0),(0,s.Lk)("span",g,[(0,s.bF)(A,{title:"Actions","icon-class":"fa fa-ellipsis-h",ref:"dropdown"},{default:(0,s.k6)((()=>[((0,s.uX)(!0),(0,s.CE)(s.FK,null,(0,s.pI)($.actions,(t=>((0,s.uX)(),(0,s.Wv)(T,{key:t.text,"icon-class":t.iconClass,text:t.text,onInput:t.action},null,8,["icon-class","text","onInput"])))),128))])),_:1},512)])],2)]),i.item.channel?((0,s.uX)(),(0,s.CE)("div",f,[(0,s.Lk)("a",{class:"channel",href:"#",target:"_blank",onClick:e[2]||(e[2]=(0,n.D$)((e=>t.$emit("open-channel")),["prevent"]))},[i.item.channel_image?((0,s.uX)(),(0,s.CE)("img",{key:0,src:i.item.channel_image,class:"channel-image"},null,8,y)):(0,s.Q3)("",!0),(0,s.Lk)("span",{class:"channel-name",textContent:(0,l.v_)(i.item.channel)},null,8,k)])])):(0,s.Q3)("",!0),i.item.created_at&&i.showDate?((0,s.uX)(),(0,s.CE)("div",C,(0,l.v_)(t.formatDateTime(i.item.created_at,!0)),1)):i.item.year&&i.showDate?((0,s.uX)(),(0,s.CE)("div",{key:2,class:"row creation-date",textContent:(0,l.v_)(i.item.year)},null,8,w)):(0,s.Q3)("",!0),null!=i.item.critic_rating||null!=i.item.community_rating?((0,s.uX)(),(0,s.CE)("div",L,[null!=i.item.critic_rating?((0,s.uX)(),(0,s.CE)("span",b,[e[6]||(e[6]=(0,s.Lk)("i",{class:"fa fa-star"},null,-1)),e[7]||(e[7]=(0,s.eW)("  ")),(0,s.Lk)("span",{textContent:(0,l.v_)(Math.round(i.item.critic_rating))},null,8,I),e[8]||(e[8]=(0,s.eW)("% "))])):(0,s.Q3)("",!0),null!=i.item.community_rating?((0,s.uX)(),(0,s.CE)("span",x,[e[9]||(e[9]=(0,s.Lk)("i",{class:"fa fa-users"},null,-1)),e[10]||(e[10]=(0,s.eW)("  ")),(0,s.Lk)("span",{textContent:(0,l.v_)(Math.round(i.item.community_rating))},null,8,_),e[11]||(e[11]=(0,s.eW)("% "))])):(0,s.Q3)("",!0)])):(0,s.Q3)("",!0)]),"photo"===i.item.item_type&&X.showPhoto?((0,s.uX)(),(0,s.CE)("div",E,[(0,s.bF)(O,{title:i.item.title||i.item.name,visible:!0,onClose:e[4]||(e[4]=t=>X.showPhoto=!1)},{default:(0,s.k6)((()=>[(0,s.Lk)("img",{src:i.item.url,ref:"image",onLoad:e[3]||(e[3]=(...t)=>$.onImgLoad&&$.onImgLoad(...t))},null,40,D)])),_:1},8,["title"])])):(0,s.Q3)("",!0)],34))}i(4114);var X=i(9265),$=i(9612),Q=i(9115),T=i(12),A=i(9513),O=i(2002),R={mixins:[O.A],components:{Dropdown:X.A,DropdownItem:$.A,MediaImage:T.A,Modal:A.A},emits:["add-to-playlist","download","download-audio","open-channel","play","play-with-opts","remove-from-playlist","select","view"],props:{item:{type:Object,required:!0},hidden:{type:Boolean,default:!1},index:{type:Number},listView:{type:Boolean,default:!1},playlist:{type:[Object,String]},selected:{type:Boolean,default:!1},showDate:{type:Boolean,default:!0}},computed:{actions(){const t=[];return["book","photo","torrent"].includes(this.item.item_type)||t.push({iconClass:"fa fa-play",text:"Play",action:()=>this.$emit("play")}),"youtube"===this.item.type&&t.push({iconClass:"fa fa-play",text:"Play (With Cache)",action:()=>this.$emit("play-with-opts",{item:this.item,opts:{cache:!0}})}),"photo"===this.item.item_type&&t.push({iconClass:"fa fa-eye",text:"View",action:()=>this.showPhoto=!0}),["file","jellyfin","youtube"].includes(this.item.type)&&t.push({iconClass:"fa fa-window-maximize",text:"View in Browser",action:()=>this.$emit("view")}),["torrent","youtube","jellyfin"].includes(this.item.type)&&"channel"!==this.item.item_type&&"playlist"!==this.item.item_type&&t.push({iconClass:"fa fa-download",text:"Download",action:()=>this.$emit("download")}),"youtube"===this.item.type&&"channel"!==this.item.item_type&&"playlist"!==this.item.item_type&&t.push({iconClass:"fa fa-volume-high",text:"Download Audio",action:()=>this.$emit("download-audio")}),["jellyfin","youtube"].includes(this.item.type)&&t.push({iconClass:"fa fa-list",text:"Add to Playlist",action:()=>this.$emit("add-to-playlist")}),["jellyfin","youtube"].includes(this.item.type)&&this.playlist&&t.push({iconClass:"fa fa-trash",text:"Remove from Playlist",action:()=>this.$emit("remove-from-playlist")}),t.push({iconClass:"fa fa-info-circle",text:"Info",action:()=>this.$emit("select")}),t},playlistView(){return this.playlist&&this.listView}},methods:{onContextClick(t){"photo"!==this.item?.item_type&&(t.preventDefault(),this.$refs.dropdown.toggle())},onImgLoad(){const t=this.$refs.image.naturalWidth,e=this.$refs.image.naturalHeight;t>e?this.$refs.image.classList.add("horizontal"):this.$refs.image.classList.add("vertical")},onMediaSelect(){"photo"===this.item?.item_type?this.showPhoto=!0:this.$emit("select")}},data(){return{showPhoto:!1,typeIcons:Q}}},M=i(6262);const V=(0,M.A)(R,[["render",S],["__scopeId","data-v-f028cbc6"]]);var H=V},12:function(t,e,i){i.d(e,{A:function(){return L}});var s=i(641),l=i(33),n=i(3751);const a={key:2,class:"icon type-icon"},o=["href"],r=["title"],d=["src","alt"],c={key:4,class:"image"},u={class:"inner"},m={key:5,class:"icon imdb-link"},h=["href"],p=["textContent"],v={key:7,class:"bottom-overlay videos"};function g(t,e,i,g,f,y){return(0,s.uX)(),(0,s.CE)("div",{class:(0,l.C4)(["image-container",y.containerClasses])},[i.hasPlay||["book","photo"].includes(i.item?.item_type)?((0,s.uX)(),(0,s.CE)("div",{key:0,class:"play-overlay",onClick:e[0]||(e[0]=(0,n.D$)(((...t)=>y.onItemClick&&y.onItemClick(...t)),["stop"]))},[(0,s.Lk)("i",{class:(0,l.C4)(y.overlayIconClass)},null,2)])):(0,s.Q3)("",!0),i.item?.image||i.item?.preview_url?((0,s.uX)(),(0,s.CE)("div",{key:1,class:"backdrop",style:(0,l.Tr)({backgroundImage:`url(${i.item.image||i.item.preview_url})`})},null,4)):(0,s.Q3)("",!0),f.typeIcons[i.item?.type]?((0,s.uX)(),(0,s.CE)("span",a,[i.item.url?((0,s.uX)(),(0,s.CE)("a",{key:0,href:i.item.url,target:"_blank"},[(0,s.Lk)("i",{class:(0,l.C4)(f.typeIcons[i.item.type]),title:i.item.type},"   ",10,r)],8,o)):(0,s.Q3)("",!0)])):(0,s.Q3)("",!0),y.imgUrl?((0,s.uX)(),(0,s.CE)("img",{key:3,class:"image",src:y.imgUrl,alt:i.item.title},null,8,d)):((0,s.uX)(),(0,s.CE)("div",c,[(0,s.Lk)("div",u,[(0,s.Lk)("i",{class:(0,l.C4)(y.iconClass)},null,2)])])),i.item?.imdb_id?((0,s.uX)(),(0,s.CE)("span",m,[(0,s.Lk)("a",{href:`https://www.imdb.com/title/${i.item.imdb_id}`,target:"_blank"},e[1]||(e[1]=[(0,s.Lk)("i",{class:"fab fa-imdb"},null,-1)]),8,h)])):(0,s.Q3)("",!0),null!=i.item?.duration?((0,s.uX)(),(0,s.CE)("span",{key:6,class:"bottom-overlay duration",textContent:(0,l.v_)(t.convertTime(i.item.duration))},null,8,p)):null!=i.item?.videos?((0,s.uX)(),(0,s.CE)("span",v,(0,l.v_)(i.item.videos)+" items ",1)):(0,s.Q3)("",!0)],2)}var f=i(9115),y=i(226),k={mixins:[f,y.A],emits:["play","select"],props:{item:{type:Object,default:()=>{}},hasPlay:{type:Boolean,default:!0}},data(){return{typeIcons:f}},computed:{clickEvent(){switch(this.item?.item_type){case"book":case"channel":case"playlist":case"folder":case"photo":return"select";default:return"play"}},containerClasses(){return{"with-image":!!this.item?.image,photo:"photo"===this.item?.item_type,book:"book"===this.item?.item_type}},iconClass(){switch(this.item?.item_type){case"book":return"fas fa-book";case"channel":return"fas fa-user";case"playlist":return"fas fa-list";case"folder":return"fas fa-folder";default:return"fas fa-play"}},imgUrl(){if("photo"===this.item?.item_type)return this.item?.preview_url||this.item?.url;let t=this.item?.image;return t||(t=this.item?.images?.[0]?.url),t},overlayIconClass(){return"channel"===this.item?.item_type||"playlist"===this.item?.item_type||"folder"===this.item?.item_type?"fas fa-folder-open":"photo"===this.item?.item_type?"fas fa-eye":"book"===this.item?.item_type?"fas fa-book-open":"fas fa-play"}},methods:{onItemClick(){this.$emit(this.clickEvent,this.item)}}},C=i(6262);const w=(0,C.A)(k,[["render",g],["__scopeId","data-v-1bfd997f"]]);var L=w},3149:function(t,e,i){i.d(e,{A:function(){return v}});var s=i(641),l=i(33);function n(t,e,i,n,a,o){const r=(0,s.g2)("Loading"),d=(0,s.g2)("Item"),c=(0,s.g2)("Draggable"),u=(0,s.g2)("Droppable"),m=(0,s.g2)("Info"),h=(0,s.g2)("Modal");return(0,s.uX)(),(0,s.CE)("div",{class:(0,l.C4)(["media-results",{list:i.listView}])},[i.loading?((0,s.uX)(),(0,s.Wv)(r,{key:0})):(0,s.Q3)("",!0),i.results?.length?((0,s.uX)(),(0,s.CE)("div",{key:1,class:"grid",ref:"grid",onScroll:e[3]||(e[3]=(...t)=>o.onScroll&&o.onScroll(...t))},[((0,s.uX)(!0),(0,s.CE)(s.FK,null,(0,s.pI)(o.visibleResults,((n,r)=>((0,s.uX)(),(0,s.CE)("div",{class:"item-container",key:r,ref_for:!0,ref:"item"},[o.playlistView&&null!=a.draggedIndex&&r>a.draggedIndex?((0,s.uX)(),(0,s.CE)("div",{key:0,class:(0,l.C4)(["droppable-container",{dragover:a.dragOverIndex===r}]),ref_for:!0,ref:"droppable-"+r},null,2)):(0,s.Q3)("",!0),(0,s.bF)(d,{item:n,index:r,"list-view":i.listView,playlist:i.playlist,selected:i.selectedResult===r,"show-date":i.showDate,onAddToPlaylist:e=>t.$emit("add-to-playlist",n),onOpenChannel:e=>t.$emit("open-channel",n),onRemoveFromPlaylist:e=>t.$emit("remove-from-playlist",n),onSelect:e=>t.$emit("select",r),onPlay:e=>t.$emit("play",n),onPlayWithOpts:e[0]||(e[0]=e=>t.$emit("play-with-opts",e)),onView:e=>t.$emit("view",n),onDownload:e=>t.$emit("download",n),onDownloadAudio:e=>t.$emit("download-audio",n),onVnodeMounted:t=>a.itemsRef[r]=t.el,onVnodeUnmounted:t=>delete a.itemsRef[r]},null,8,["item","index","list-view","playlist","selected","show-date","onAddToPlaylist","onOpenChannel","onRemoveFromPlaylist","onSelect","onPlay","onView","onDownload","onDownloadAudio","onVnodeMounted","onVnodeUnmounted"]),o.playlistView?((0,s.uX)(),(0,s.Wv)(c,{key:1,element:a.itemsRef[r],onDrag:t=>a.draggedIndex=r},null,8,["element","onDrag"])):(0,s.Q3)("",!0),(0,s.bF)(u,{element:a.itemsRef[r],onDragenter:t=>a.dragOverIndex=r,onDragleave:e[1]||(e[1]=t=>a.dragOverIndex=null),onDragover:t=>a.dragOverIndex=r,onDrop:t=>o.onMove(r)},null,8,["element","onDragenter","onDragover","onDrop"]),o.playlistView&&null!=a.draggedIndex&&r<a.draggedIndex?((0,s.uX)(),(0,s.CE)("div",{key:2,class:(0,l.C4)(["droppable-container",{dragover:a.dragOverIndex===r}]),ref_for:!0,ref:"droppable-"+r},null,2)):(0,s.Q3)("",!0),o.playlistView&&null!=a.draggedIndex&&r!==a.draggedIndex?((0,s.uX)(),(0,s.Wv)(u,{key:3,element:t.$refs["droppable-"+r]?.[0],onDragenter:t=>a.dragOverIndex=r,onDragleave:e[2]||(e[2]=t=>a.dragOverIndex=null),onDragover:t=>a.dragOverIndex=r,onDrop:t=>o.onMove(r)},null,8,["element","onDragenter","onDragover","onDrop"])):(0,s.Q3)("",!0)])))),128))],544)):(0,s.Q3)("",!0),(0,s.bF)(h,{ref:"infoModal",title:"Media info",onClose:e[10]||(e[10]=e=>t.$emit("select",null))},{default:(0,s.k6)((()=>[null!=i.selectedResult?((0,s.uX)(),(0,s.Wv)(m,{key:0,item:i.results[i.selectedResult],pluginName:i.pluginName,onAddToPlaylist:e[4]||(e[4]=e=>t.$emit("add-to-playlist",i.results[i.selectedResult])),onDownload:e[5]||(e[5]=e=>t.$emit("download",i.results[i.selectedResult])),onDownloadAudio:e[6]||(e[6]=e=>t.$emit("download-audio",i.results[i.selectedResult])),onOpenChannel:e[7]||(e[7]=e=>t.$emit("open-channel",i.results[i.selectedResult])),onPlay:e[8]||(e[8]=e=>t.$emit("play",i.results[i.selectedResult])),onPlayWithOpts:e[9]||(e[9]=e=>t.$emit("play-with-opts",{...e,item:i.results[i.selectedResult]}))},null,8,["item","pluginName"])):(0,s.Q3)("",!0)])),_:1},512)],2)}var a=i(8692),o=i(3118),r=i(7711),d=i(6382),c=i(9828),u=i(9513),m={components:{Draggable:a.A,Droppable:o.A,Info:r.A,Item:d.A,Loading:c.A,Modal:u.A},emits:["add-to-playlist","download","download-audio","move","open-channel","play","play-with-opts","remove-from-playlist","scroll-end","select","view"],props:{filter:{type:String,default:null},listView:{type:Boolean,default:!1},loading:{type:Boolean,default:!1},playlist:{default:null},pluginName:{type:String},results:{type:Array,default:()=>[]},resultIndexStep:{type:Number,default:25},selectedResult:{type:Number},showDate:{type:Boolean,default:!0},sources:{type:Object,default:()=>{}}},data(){return{draggedIndex:null,dragOverIndex:null,itemsRef:{},maxResultIndex:this.resultIndexStep}},computed:{playlistView(){return null!=this.playlist&&this.listView},visibleResults(){let t=this.results.filter((t=>!this.filter?.length||(t.title||t.name).toLowerCase().includes(this.filter.toLowerCase())));return null!=this.maxResultIndex&&(t=t.slice(0,this.maxResultIndex)),t}},methods:{onMove(t){if(null==this.draggedIndex)return;const e=this.results[this.draggedIndex];this.$emit("move",{from:this.draggedIndex,to:t,item:e}),this.draggedIndex=null},onScroll(t){const e=t.target;if(!e)return;const i=e.scrollHeight-e.scrollTop<=e.clientHeight+150;i&&(this.$emit("scroll-end"),null!=this.resultIndexStep&&(this.maxResultIndex+=this.resultIndexStep))}},watch:{selectedResult(t){"playlist"!==t?.item_type&&"channel"!==t?.item_type?null==this.selectedResult?this.$refs.infoModal?.close():this.$refs.infoModal?.show():this.$emit("select",null)}}},h=i(6262);const p=(0,h.A)(m,[["render",n],["__scopeId","data-v-2e38f16e"]]);var v=p},9115:function(t){t.exports=JSON.parse('{"file":"fa fa-hdd","torrent":"fa fa-magnet","youtube":"fab fa-youtube","plex":"fa fa-plex","jellyfin":"fa fa-jellyfin"}')}}]);
//# sourceMappingURL=3149.563a4229.js.map