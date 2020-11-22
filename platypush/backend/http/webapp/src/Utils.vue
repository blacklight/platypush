<script>
import Api from "@/utils/Api";
import DateTime from "@/utils/DateTime";
import Events from "@/utils/Events";
import Notification from "@/utils/Notification";
import Types from "@/utils/Types";

export default {
  name: "Utils",
  mixins: [Api, Notification, Events, DateTime, Types],
}
</script>
