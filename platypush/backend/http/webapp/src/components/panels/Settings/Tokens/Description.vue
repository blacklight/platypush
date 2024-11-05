<template>
  <p>
    You can use your token to authenticate calls to the <code>/execute</code> endpoint or the Websocket routes.<br/><br/>

    You can include the token in your requests in any of the following ways:

    <ul>
      <li>
        Specify it on the <code>Authorization: Bearer &lt;token&gt;</code>
        header (replace <code>&lt;token&gt;</code> with your token).
      </li>
      <li>
        Specify it on the <code>X-Token &lt;token&gt;</code> header (replace
        <code>&lt;token&gt;</code> with your token).
      </li>
      <li>
        Specify it as a URL parameter: <code>http://site:8008/execute?token=...</code>.
      </li>
      <li>
        Specify it on the body of your JSON request:
        <code>{"type":"request", "action", "...", "token":"..."}</code>.
      </li>
    </ul>
  </p>
</template>
