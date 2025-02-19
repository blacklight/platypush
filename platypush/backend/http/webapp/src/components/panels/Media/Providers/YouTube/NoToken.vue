<template>
  <div class="no-token">
    <div class="title">
      No <code>auth_token</code> found in the YouTube configuration.
    </div>

    <div class="description">
      This integration requires an <code>auth_token</code> to be set in the
      <code>youtube</code> section of the configuration file in order to
      access your playlists and subscriptions.<br/><br/>

      The following backends are supported:

      <h2>Piped</h2>

      You can retrieve an auth token from your favourite Piped instance
      (default: <a href="https://pipedapi.kavin.rocks" target="_blank">https://pipedapi.kavin.rocks</a>)
      through the following procedure:

      <ol>
        <li>Login to your configured Piped instance.</li>
        <li>Copy the RSS/Atom feed URL on the <i>Feed</i> tab.</li>
        <li>Copy the <code>auth_token</code> query parameter from the URL.</li>
      </ol>

      <h2>Invidious</h2>

      You can retrieve an auth token from your favourite Invidious instance
      (default: <a href="https://yewtu.be" target="_blank">https://yewtu.be</a>)
      through the following procedure:

      <ol>
        <li>Login to your configured Invidious instance.</li>
        <li>Open the URL <code>https://&lt;instance_url&gt;/authorize_token?scopes=:*</code>
          in your browser. Replace <code>&lt;instance_url&gt;</code> with the URL of your
          Invidious instance, and <code>:*</code> with the scopes you want to assign to
          the token (although an all-access token is recommended for full
          functionality).</li>
        <li>Copy the generated token.</li>
      </ol>

      <h2>Example Configuration</h2>

      <pre class="snippet" v-html="highlightedYAML"></pre>
    </div>
  </div>
</template>

<script>
import hljs from "highlight.js"

const configSnippet = `
youtube:
  backends:
    piped:
      # NOTE: This is the URL of the Piped instance API, not the web interface.
      instance_url: "https://pipedapi.kavin.rocks"
      auth_token: "s3cr3t"

    invidious:
      instance_url: "https://yewtu.be"
      auth_token: '{"session":"v1:s3cr3t","scopes":[":*"],"signature":"signed"}'
`

export default {
  computed: {
    highlightedYAML() {
      return hljs.highlight(
        configSnippet,
        {language: 'yaml'}
      ).value
    },
  },
}
</script>


<style lang="scss" scoped>
.no-token {
  padding: 0.5em;

  .title {
    font-size: 1.5em;
    font-weight: bold;
    margin-bottom: 1em;
  }

  .snippet {
    background-color: #f4f4f4;
    border-radius: 0.5em;
    padding: 0.5em;
    margin: 1em;
  }
}
</style>
