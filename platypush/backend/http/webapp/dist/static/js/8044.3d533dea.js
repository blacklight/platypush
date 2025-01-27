"use strict";(self["webpackChunkplatypush"]=self["webpackChunkplatypush"]||[]).push([[8044],{8044:function(e,t,a){a.r(t),a.d(t,{default:function(){return p}});var n=a(641);const o={class:"no-token"},i={class:"description"},d=["innerHTML"];function c(e,t,a,c,s,r){return(0,n.uX)(),(0,n.CE)("div",o,[t[1]||(t[1]=(0,n.Lk)("div",{class:"title"},[(0,n.eW)(" No "),(0,n.Lk)("code",null,"auth_token"),(0,n.eW)(" found in the YouTube configuration. ")],-1)),(0,n.Lk)("div",i,[t[0]||(t[0]=(0,n.Fv)(' This integration requires an <code data-v-c4645d8e>auth_token</code> to be set in the <code data-v-c4645d8e>youtube</code> section of the configuration file in order to access your playlists and subscriptions.<br data-v-c4645d8e><br data-v-c4645d8e> The following backends are supported: <h2 data-v-c4645d8e>Piped</h2> You can retrieve an auth token from your favourite Piped instance (default: <a href="https://pipedapi.kavin.rocks" target="_blank" data-v-c4645d8e>https://pipedapi.kavin.rocks</a>) through the following procedure: <ol data-v-c4645d8e><li data-v-c4645d8e>Login to your configured Piped instance.</li><li data-v-c4645d8e>Copy the RSS/Atom feed URL on the <i data-v-c4645d8e>Feed</i> tab.</li><li data-v-c4645d8e>Copy the <code data-v-c4645d8e>auth_token</code> query parameter from the URL.</li></ol><h2 data-v-c4645d8e>Invidious</h2> You can retrieve an auth token from your favourite Invidious instance (default: <a href="https://yewtu.be" target="_blank" data-v-c4645d8e>https://yewtu.be</a>) through the following procedure: <ol data-v-c4645d8e><li data-v-c4645d8e>Login to your configured Invidious instance.</li><li data-v-c4645d8e>Open the URL <code data-v-c4645d8e>https://&lt;instance_url&gt;/authorize_token?scopes=:*</code> in your browser. Replace <code data-v-c4645d8e>&lt;instance_url&gt;</code> with the URL of your Invidious instance, and <code data-v-c4645d8e>:*</code> with the scopes you want to assign to the token (although an all-access token is recommended for full functionality).</li><li data-v-c4645d8e>Copy the generated token.</li></ol><h2 data-v-c4645d8e>Example Configuration</h2>',19)),(0,n.Lk)("pre",{class:"snippet",innerHTML:r.highlightedYAML},null,8,d)])])}var s=a(9878);const r='\nyoutube:\n  backends:\n    piped:\n      # NOTE: This is the URL of the Piped instance API, not the web interface.\n      instance_url: "https://pipedapi.kavin.rocks"\n      auth_token: "s3cr3t"\n\n    invidious:\n      instance_url: "https://yewtu.be"\n      auth_token: \'{"session":"v1:s3cr3t","scopes":[":*"],"signature":"signed"}\'\n';var u={computed:{highlightedYAML(){return s.A.highlight(r,{language:"yaml"}).value}}},h=a(6262);const l=(0,h.A)(u,[["render",c],["__scopeId","data-v-c4645d8e"]]);var p=l}}]);
//# sourceMappingURL=8044.3d533dea.js.map