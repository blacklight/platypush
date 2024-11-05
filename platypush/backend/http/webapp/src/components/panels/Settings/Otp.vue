<template>
  <div class="otp-config-container">
    <Loading v-if="initializing" />

    <div class="otp-config" v-else>
      <div class="title">
        <h3>Two-Factor Authentication {{ otpEnabled ? 'Enabled' : 'Disabled'}}</h3>
        <ToggleSwitch :value="toggleOn"
                      :disabled="refreshing"
                      @input="currentOtpConfig?.otp_secret?.length ? startOtpDisable() : startOtpSetup()" />
      </div>

      <p class="description">
        Two-factor authentication adds an extra layer of security to your
        account. When enabled, you will need to enter a code from your
        authenticator app in addition to your password.
      </p>

      <div class="current-otp-config" v-if="currentOtpConfig?.otp_secret?.length">
        <div class="header">
          <h4>2FA Configuration</h4>
          <button class="btn btn-primary"
                  :disabled="refreshing"
                  @click="$refs.confirmModal.open"
                  v-if="hasChanges && temporaryOtpEnabled">
            <i class="fas fa-save"></i>&nbsp;Save
          </button>
        </div>

        <div class="description">
          <p>Scan the QR code with your authenticator app to add this account.</p>
          <p>Alternatively, you can add either the secret or the provisioning
          URL to your password manager or authenticator app.</p>
        </div>

        <div class="section qrcode-container" v-if="currentOtpConfig.qrcode">
          <img class="qrcode" :src="`data:image/png;base64,${currentOtpConfig.qrcode}`" alt="QR Code" />
        </div>

        <div class="section secret-container" v-if="currentOtpConfig.otp_secret">
          <h4>Secret</h4>
          <input type="text"
                 :value="currentOtpConfig.otp_secret"
                 readonly
                 @focus="copyToClipboard($event.target.value)" />
        </div>

        <div class="section uri-container" v-if="currentOtpConfig.otp_uri">
          <h4>Provisioning URL</h4>
          <input type="text"
                :value="currentOtpConfig.otp_uri"
                readonly
                @focus="copyToClipboard($event.target.value)" />
        </div>

        <div class="section backup-codes" v-if="otpEnabled">
          <div class="header">
            <h4>Backup Codes</h4>
            <button class="btn btn-primary"
                    :disabled="refreshing"
                    @click="$refs.confirmRefreshCodes.open">
              <i class="fas fa-sync"></i>&nbsp;Regenerate
            </button>
          </div>

          <div class="description" v-if="backupCodes?.length">
            <p>
              Backup Codes are one-time use codes that can be used to access
              your account in case you lose access to your authenticator app.
            </p>
            <p>Make sure to store them in a safe place.</p>
            <p><b>
              Take note of these codes NOW! You will not be able to see them again!
            </b></p>
          </div>

          <textarea :value="backupCodes.join('\n')"
                    readonly
                    @focus="copyToClipboard($event.target.value)"
                    v-if="backupCodes?.length" />
        </div>
      </div>
    </div>

    <ConfirmDialog ref="confirmRefreshCodes" @input="refreshCodes" v-if="!refreshing">
      Are you sure you want to regenerate the backup codes?
    </ConfirmDialog>

    <Modal title="Confirm 2FA Setup" ref="confirmModal" @open="onConfirmModalOpen">
      <div class="confirm-modal">
        <div class="dialog" v-if="temporaryOtpEnabled">
          <p>Are you sure you want to enable Two-Factor Authentication?</p>
          <p>Make sure to save the secret and backup codes in a safe place.</p>
          <p>
            In order to enable Two-Factor Authentication, you will need to enter
            your password and a code from your authenticator app.
          </p>
        </div>

        <div class="dialog" v-else>
          <p>Are you sure you want to disable Two-Factor Authentication?</p>
          <p>
            You will no longer need to enter a code from your authenticator app.
            You will still need to enter your password to log in, but your
            account may be less secure.
          </p>

          <p>
            In order to disable Two-Factor Authentication, you will need to enter
            your password.
          </p>
        </div>

        <form :disabled="refreshing" @submit.prevent="otpEnabled ? disableOtp() : enableOtp()">
          <input type="password"
                 placeholder="Password"
                 required
                 :disabled="refreshing"
                 ref="password" />

          <input type="text"
                 placeholder="Authenticator Code"
                 required
                 :disabled="refreshing"
                 ref="code"
                 v-if="temporaryOtpEnabled" />

          <div class="buttons">
            <button class="btn btn-primary"
                    :disabled="refreshing"
                    type="submit">
              <i class="fas fa-check"></i>&nbsp;Confirm
              <Loading v-if="refreshing" />
            </button>

            <button class="btn btn-default"
                    @click="$refs.confirmModal.close">
              <i class="fas fa-times"></i>&nbsp;Cancel
            </button>
          </div>
        </form>
      </div>
    </Modal>
  </div>
</template>

<script>
import ConfirmDialog from "@/components/elements/ConfirmDialog";
import Loading from "@/components/Loading";
import Modal from "@/components/Modal";
import ToggleSwitch from "@/components/elements/ToggleSwitch";
import Utils from '@/Utils'
import axios from 'axios'

export default {
  mixins: [Utils],
  components: {
    ConfirmDialog,
    Loading,
    Modal,
    ToggleSwitch,
  },

  data() {
    return {
      backupCodes: [],
      initializing: false,
      otpConfig: null,
      refreshing: false,
      temporaryOtpConfig: null,
    }
  },

  computed: {
    currentOtpConfig() {
      return this.otpEnabled ? this.otpConfig : this.temporaryOtpConfig
    },

    hasChanges() {
      return (
        (!this.otpEnabled && this.temporaryOtpConfig != null) ||
        (this.otpEnabled && (this.temporaryOtpConfig == null || this.temporaryOtpConfig?.otp_secret != this.otpConfig?.otp_secret))
      )
    },

    otpEnabled() {
      return !!this?.otpConfig?.otp_secret?.length
    },

    temporaryOtpDisabled() {
      return this.hasChanges && this.temporaryOtpConfig?.otp_secret == null
    },

    temporaryOtpEnabled() {
      return this.hasChanges && this.temporaryOtpConfig?.otp_secret != null
    },

    toggleOn() {
      return this.otpEnabled || this.temporaryOtpEnabled
    },
  },

  methods: {
    getErrorMessage(error) {
      return (
        error.response?.data?.message ||
        error.response?.data?.error ||
        error.message ||
        error.response?.statusText ||
        error.toString()
      )
    },

    onError(error) {
      console.error(error)
      error = this.getErrorMessage(error)
      this.notify({
        error: true,
        title: "Error while setting up Two-Factor Authentication",
        text: error,
        image: {
          iconClass: "fas fa-exclamation-triangle",
        },
      })
    },

    async getOtpConfig() {
      this.initializing = true

      try {
        this.otpConfig = (await axios.get("/otp/config")).data
        this.temporaryOtpConfig = this.otpConfig
      } catch (error) {
        this.onError(error)
      } finally {
        this.initializing = false
      }
    },

    async startOtpSetup() {
      this.refreshing = true

      try {
        this.temporaryOtpConfig = (await axios.post("/otp/config", { dry_run: true })).data
      } finally {
        this.refreshing = false
      }
    },

    async enableOtp() {
      this.refreshing = true

      try {
        const response = await axios.post(
          "/otp/config",
          {
            otp_secret: this.temporaryOtpConfig.otp_secret,
            password: this.$refs.password.value,
            code: this.$refs.code.value,
          }
        )

        this.backupCodes = response.data?.backup_codes || []
        await this.getOtpConfig()

        this.$refs.confirmModal.close()
        this.notify({
          title: "Two-Factor Authentication enabled",
          text: "Two-Factor Authentication has been enabled for your account",
          image: {
            iconClass: "fas fa-shield-alt",
          },
        })
      } catch (error) {
        this.onError(error)
      } finally {
        this.refreshing = false
      }
    },

    async startOtpDisable() {
      this.temporaryOtpConfig = null
      this.$refs.confirmModal.open()
    },

    async disableOtp() {
      this.refreshing = true

      try {
        await axios.delete("/otp/config", {
          headers: {
            "Content-Type": "application/json",
          },
          data: {
            password: this.$refs.password.value
          }
        })

        await this.getOtpConfig()

        this.$refs.confirmModal.close()
        this.notify({
          title: "Two-Factor Authentication disabled",
          text: "Two-Factor Authentication has been disabled for your account",
          image: {
            iconClass: "fas fa-shield-alt",
          },
        })
      } catch (error) {
        this.onError(error)
      } finally {
        this.refreshing = false
      }
    },

    async refreshCodes() {
      this.refreshing = true

      try {
        const response = await axios.post("/otp/refresh-codes")
        this.backupCodes = response.data?.backup_codes || []
        this.notify({
          title: "Backup codes regenerated",
          text: "Take note of these codes NOW! You will not be able to see them again!",
          image: {
            iconClass: "fas fa-shield-alt",
          },
        })
      } catch (error) {
        this.onError(error)
      } finally {
        this.refreshing = false
      }
    },

    onConfirmModalOpen() {
      this.$nextTick(() => {
        this.$refs.password.value = ""
        if (this.$refs.code)
          this.$refs.code.value = ""

        this.$refs.password.focus()
      })
    },
  },

  async mounted() {
    await this.getOtpConfig()
  },
}
</script>

<style lang="scss" scoped>
.otp-config-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  position: relative;

  .description {
    font-size: 0.9em;
  }

  .otp-config {
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;

    .title {
      width: 100%;
      display: flex;
      align-items: center;

      h3 {
        flex-grow: 1;
      }
    }

    .section {
      input[type="text"] {
        width: 100%;
        max-width: 30em;
        padding: 0.5em;
        margin: 0.5em 0;
        border: 1px solid #ccc;
      }
    }

    .qrcode-container {
      width: 100%;
      display: flex;
      justify-content: center;
    }

    .qrcode {
      width: 200px;
    }

    .backup-codes {
      textarea {
        width: 100%;
        height: 16em;
        padding: .5em;
        border: $default-border-2;
        border-radius: 1em;
        box-shadow: $border-shadow-bottom-right;
        outline: none;
      }
    }
  }

  .current-otp-config {
    width: 100%;

    .header {
      width: 100%;
      display: flex;
      flex-direction: row;
      align-items: center;

      h4 {
        flex-grow: 1;
      }
    }
  }

  :deep(.modal) {
    .confirm-modal {
      width: 100%;
      max-width: 40em;

      .dialog {
        width: 100%;
      }

      form {
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;

        input[type="password"],
        input[type="text"],
        .buttons {
          width: 100%;
          max-width: 20em;
        }

        .buttons {
          display: flex;
          justify-content: center;

          button {
            margin: 0 0.5em;

            &[type="submit"] {
              position: relative;
            }
          }
        }
      }
    }
  }
}
</style>
