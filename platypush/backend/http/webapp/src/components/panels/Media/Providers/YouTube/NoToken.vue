<template>
  <div class="no-token">
    <div class="title">
      No <code>auth_token</code> found in the YouTube configuration.
    </div>

    <div class="description">
      This integration requires an <code>auth_token</code> to be set in the
      <code>youtube</code> section of the configuration file in order to
      access your playlists and subscriptions.<br/><br/>

      Piped auth tokens are currently supported. You can retrieve one through
      the following procedure:

      <ol>
        <li>Login to your configured Piped instance.</li>
        <li>Copy the RSS/Atom feed URL on the <i>Feed</i> tab.</li>
        <li>Copy the <code>auth_token</code> query parameter from the URL.</li>
        <li>
          Enter it in the <code>auth_token</code> field in the
          <code>youtube</code> section of the configuration file.
        </li>
      </ol>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.no-token {
  padding: 0.5em;

  .title {
    font-size: 1.5em;
    font-weight: bold;
    margin-bottom: 1em;
  }
}
</style>
