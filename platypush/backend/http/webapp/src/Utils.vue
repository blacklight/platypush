<script>
import Api from "@/utils/Api";
import Clipboard from "@/utils/Clipboard";
import Cookies from "@/utils/Cookies";
import DateTime from "@/utils/DateTime";
import Events from "@/utils/Events";
import Extensions from "@/utils/Extensions";
import Notification from "@/utils/Notification";
import Screen from "@/utils/Screen";
import Text from "@/utils/Text";
import Types from "@/utils/Types";

export default {
  name: "Utils",
  mixins: [
    Api,
    Clipboard,
    Cookies,
    DateTime,
    Events,
    Notification,
    Extensions,
    Screen,
    Text,
    Types,
  ],
}
</script>
